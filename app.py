from distutils.log import debug
from flask import Flask, render_template, request, jsonify
import json
#import bill

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    return 'hello product'
    #return bill.products
    #number = bill.number
    #item = bill.products[-1]['item']
    #price = bill.products[-1]['price']
    #taken = bill.products[-1]['taken']
    #final_rate = bill.products[-1]['final_rate']

    #return render_template('products.html', number=number, item=item, price=price, taken=taken, final_rate=final_rate)

@app.route('/cart', methods = ['POST', 'GET'])
def cart():
    return render_template('products.html', product='anzil')

if __name__ == '__main__':
    app.run(debug=True)
  

