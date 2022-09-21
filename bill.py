import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import asyncio
import webbrowser

import RPi.GPIO as GPIO

import requests
import json
from requests.structures import CaseInsensitiveDict
from hx711 import HX711


runner = None
show_camera = True

dir_path = os.path.dirname(os.path.realpath(__file__))
modelfile = os.path.join(dir_path, 'modelfile.eim')


def now():
    return round(time.time() * 1000)


product = None

referenceUnit = 1
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(389.5)
hx.reset()
hx.tare()

def find_weight():
    try:
        time.sleep(3)
        val = abs(int(hx.get_weight(5)))
    except (KeyboardInterrupt, SystemExit):
        print('some error occured')
    
    return val


text_file = os.path.join('storage', 'products.txt')


def post(label,price,final_rate,quantity):
    
    product = {}
    product['label'] = label
    product['price'] = price
    product['quantity'] = quantity
    product['amount payable'] = final_rate

    requests.post('http://localhost:5000/cart', json=product)
    #webbrowser.open(f'http://localhost:5000/cart/?item={label}&price={price}&taken={taken}&final_rate={final_rate}')
    #webbrowser.open('http://localhost:5000/cart')
    
    

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
    
    
    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            # print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            #labels = model_info['model_parameters']['labels']
            # print(labels)

            videoCaptureDeviceId = 0
            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]

            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %
                      (backendName, h, w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0  # limit to ~10 fps here
            
            webbrowser.open('http://127.0.0.1:5000/')
            
            
            for res, img in runner.classifier(videoCaptureDeviceId):
                
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)
                    # print('classification runner response', res)
                    
                if len(res["result"]["bounding_boxes"]) != 0:
                    
                    if os.path.isfile(text_file):
                        pass
                    else:
                        old_labels = []
                    
                    a = []
                    if res['result']['bounding_boxes'][0]['label'] != 'Lemon':
                        
                        for i in range(len(res['result']['bounding_boxes'])):
                            if res['result']['bounding_boxes'][i]['value'] > 0.9:
                                a.append(res['result']['bounding_boxes'][i]['label'])
                    
                        if len(a) > 0:
                            label = res['result']['bounding_boxes'][0]['label']
                            if len(set(a)) == 1 and len(a) == 1 and label not in old_labels:
                                taken = 1
                                rate(label,taken)
                                old_labels.append(label)
                            elif len(set(a)) == 1 and len(a) > 1 and label not in old_labels:
                                taken = len(a)
                                rate(label,taken)
                                old_labels.append(label)
                            
                    else:
                        if res['result']['bounding_boxes'][0]['value'] > 0.9 and 'Lemon' not in old_labels:
                            weight = find_weight()
                            rate('Lemon', round(weight/1000, 2))
                            old_labels.append('Lemon')
                            
                
                next_frame = now() + 100

        finally:
            if (runner):
                runner.stop()




