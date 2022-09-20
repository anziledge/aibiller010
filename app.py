from distutils.log import debug
from flask import Flask, render_template, request
import json
import pyqrcode
import time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    pros = []
    with open('storage/products.txt', 'r') as file:
        for line in file:
            pros.append(eval(line.strip()))
            
    return render_template('products.html', products=pros)

@app.route('/cart', methods = ['POST', 'GET'])
def cart():
    data = request.get_json()
    with open('storage/products.txt', 'a') as outfile:
        json.dump(data, outfile)
        outfile.write('\n')
    return 'hi'

@app.route('/payment')
def pay():
    #price = 10
    url = pyqrcode.create('www.instagram.com')
    url.svg("myqr", scale=10)
    
    return render_template('qr.html')



if __name__ == '__main__':
    app.run(debug=False)
  



