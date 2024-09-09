import json
from flask import Flask, render_template, request,redirect,send_file
# import pandas as pd
from Backend import Search,Analyse,flipkartReviewAnalyse,amazonReviewAnalyse
# import bs4
from fake_headers import Headers
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the product name from the form
        if(request.form["product_name"]):
            product_name = request.form.get("product_name")
            fp="static/Page/Plot.png"
            if(os.path.exists(fp)):
                os.remove(fp)
        # Call the search function with the product name
            Search(product_name,1)

            with open("Data.json",'r+') as f:
                js=json.load(f)
            return render_template('index.html', data=js,page=1,s=product_name)
        # else:
        #     return render_template('index.html')
    else:
        # Render the initial HTML form
        return render_template('home.html')
    
@app.route('/<int:page>',methods=['GET','POST'])
def navigate(page):
    if request.method == 'POST':
        # Get the product name from the form
        if(request.form["Page"]):
            # product_name = request.form.get("product_name")
            # fp="static/Page/Plot.png"
            # if(os.path.exists(fp)):
            #     os.remove(fp)
            product_name=request.form.get('Page')
        # Call the search function with the product name
            Search(product_name,page)

            with open("Data.json",'r+') as f:
                js=json.load(f)
            p=page+1
            return render_template('index.html', data=js,page=p,s=product_name)
    else:
        # Render the initial HTML form
        return redirect("/")

@app.route("/analyse",methods=['POST','GET']) 
def page():
    if(request.method=='POST'):
        # fp="static/Page/Plot.png"
        # if(os.path.exists(fp)):
        #     os.remove(fp)
        Analyse()
        # with open("Data.json",'r+') as f:
        #     js=json.load(f)
        return render_template('Stats.html')
    else:
        return redirect("/")

@app.route("/aproductanalyse",methods=['GET','POST'])
def aproduct():
    if request.method=='POST':
        ASIN=request.form.get("ProductAnalyse")
        sentiment=amazonReviewAnalyse(ASIN)
        return render_template('Product.html',Data=sentiment)
    else:
        return redirect("/")
@app.route("/fproductanalyse",methods=['GET','POST'])
def fproduct():
    if request.method=='POST':
        FSN=request.form["ProductAnalyse"]
        sentiment=flipkartReviewAnalyse(FSN)
        return render_template('Product.html',Data=sentiment)
    else:
        return redirect("/")

@app.route("/download",methods=["GET","POST"])
def download():
    path="Data.json"
    return send_file(path,as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
