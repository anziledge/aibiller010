from distutils.log import debug
from flask import Flask, render_template, request
import json
import pyqrcode
import png
import time
import os
import webbrowser
app = Flask(__name__)

#pic_folder = os.path.join('static', 'images')
#app.config['UPLOAD_FOLDER'] = pic_folder
fileno = 190

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    pros = []
    with open('storage/products.txt', 'r') as file:
        for line in file:
            pros.append(eval(line.strip()))
    
    price_list = [product['amount payable'] for product in pros]
    length = len(price_list)
    total_price = round(sum(price_list), 2)
    
            
    return render_template('products.html', products=pros, number=length, total_price=total_price)

@app.route('/cart', methods = ['GET', 'POST'])
def cart():
    if request.method == 'POST':
        data = request.get_json()
        with open('storage/products.txt', 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')
        webbrowser.open('http://127.0.0.1:5000/products')
    return 'go to products instead of cart'

@app.route('/payment')
def pay():
    global fileno
    pros = []
    with open('storage/products.txt', 'r') as file:
        for line in file:
            pros.append(eval(line.strip()))
    price_list = [product['amount payable'] for product in pros]
    total_price = round(sum(price_list), 2)
    
    filename = str(fileno)
    fileno += 1
    price=str(total_price)
    s = 'upi://pay?pa=abdul2hadi2k2k@oksbi&pn=ABDUL%40HADI&am='+price+'&cu=INR&aid=uGICAgICTvd6KIQ'
    url = pyqrcode.create(s)
    url.png(f"static/images/{filename}.png", scale=8)
    file = os.path.join('static', 'images', f'{filename}.png')
    
    # deletes products.txt
    text_file = os.path.join('storage', 'products.txt')
    if os.path.isfile(text_file):
        os.remove(text_file)
    
    return render_template('qr.html', image=file)
    
    
if __name__ == '__main__':
    app.run(debug=False)


