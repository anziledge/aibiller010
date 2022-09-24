import cv2
import os
import time
from edge_impulse_linux.image import ImageImpulseRunner
import webbrowser

import RPi.GPIO as GPIO

import requests
import json
from hx711 import HX711

dir_path = os.path.dirname(os.path.realpath(__file__))
modelfile = os.path.join(dir_path, 'modelfile.eim')

def now():
    return round(time.time() * 1000)




referenceUnit = 1
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(389.5)
hx.reset()
hx.tare()


def find_weight():
    try:
        val = abs(int(hx.get_weight(5)))
    except (KeyboardInterrupt, SystemExit):
        print('some error occured')
    
    # val here is in grams
    return val


# this text file stores each products in dictionary format
# this text file gets deleted after the checkout button is clicked
# it will be created again in the next checkout
text_file = os.path.join('storage', 'products.txt')


def post(label,price,final_rate,quantity):
    product = {}
    product['label'] = label
    product['price'] = price
    product['quantity'] = quantity
    product['amount payable'] = final_rate

    requests.post('http://localhost:5000/cart', json=product)


def rate(label, quantity):
    if label == 'Pears soap' :
        price = 51
    elif label == 'Good knight' :
        price = 77
    else:
        price = 70
         
    final_rate = price * quantity
    
    if label == 'Lemon':
        final_rate_str = str(final_rate)
        if '.' in final_rate_str and '0' in final_rate_str[final_rate_str.index('.'):]:
            final_rate = float(final_rate_str[:final_rate_str.index('0')])
    
    post(label,price,final_rate,quantity)



while True:
    # there should be no products.txt at beginning
    # it is created only when a product is added
    if os.path.isfile(text_file):
        os.remove(text_file)
    
    
    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()

            videoCaptureDeviceId = 0
            
            camera = cv2.VideoCapture(videoCaptureDeviceId)
            camera.release()
            
            next_frame = 0  # limit to ~10 fps here
            flag = False
            # home page opens in the browser
            webbrowser.open('http://127.0.0.1:5000/')
            
            old_labels = []
            
            for res, img in runner.classifier(videoCaptureDeviceId):
                
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)
                
                if os.path.isfile(text_file):
                    pass
                else:
                    old_labels = []
                
                bounding_boxes = res['result']['bounding_boxes']
                
                if len(bounding_boxes) != 0 and bounding_boxes[0]["label"] not in old_labels:
                    if flag == False:
                        time.sleep(3)
                        flag = True
                        continue
                    
                    flag = False
                    
                    filtered_products = [thing for thing in bounding_boxes if thing['value'] > 0.85]
                    
                    if len(filtered_products) == 0:
                        continue
                    
                    label = filtered_products[0]['label']
                    
                    if label != 'Lemon' and label not in old_labels:
                        taken = len(filtered_products)
                        rate(label,taken)
                        old_labels.append(label)
                    elif label == 'Lemon' and label not in old_labels:
                        weight = find_weight()
                        if weight > 10:
                            weight = round(weight/1000, 2)
                            rate('Lemon', weight)
                            old_labels.append('Lemon')
                    
                next_frame = now() + 100
        finally:
            if (runner):
                runner.stop()




