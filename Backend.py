from flask import Flask, render_template
import pandas as pd
import requests
import bs4
import json
import numpy
import matplotlib
import matplotlib.pyplot as plt
from fake_headers import Headers
import threading
import os
from wordcloud import WordCloud,STOPWORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
matplotlib.use('agg')
def Search(x,p):
    Data=[]
    t1=threading.Thread(target=flipkartSearch,args=(x,p,Data,))
    t2=threading.Thread(target=amazonSearch,args=(x,p,Data,))
    t3=threading.Thread(target=poorvika,args=(x,p,Data,))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    with open("Data.json","w+") as f:
        json.dump(Data,f)

def amazonSearch(x,p,Data): 
    url = "https://www.amazon.in/s?k={0}&page={1}"
    # url="https://www.amazon.in/s"
    url=url.format(x,p)
    page = requests.get(url, headers=Headers(os='win',browser='chrome',headers=True).generate())
    html = page.content
    page_soup = bs4.BeautifulSoup(html,"html.parser")
    # Single grid
    if(page_soup.find('div',class_='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 AdHolder sg-col s-widget-spacing-small sg-col-12-of-16')):
        amazon=page_soup.findAll('div', attrs={'data-component-type': 's-search-result'})
        # print(amazon)
        for div in amazon:
            d={}
            # b=div.find('span', attrs={'class':'a-size-base-plus a-color-base'})
            p=div.find('span', attrs={'class':'a-price-whole'})
            rating=div.find('span', attrs={'class':'a-icon-alt'})
                        # specification = containers.find('div', {'class':'_1rcHFq'})
            i=div.find('img',class_='s-image')
            n=div.find('span',attrs={'class':'a-size-medium a-color-base a-text-normal'})
            if(n==None):
                b='Nill'
            else:
                b=(n.text).split(' ')
            l=div.find('a',class_='a-link-normal s-no-outline')
            if(n!=None and p!=None and b!=None and i!=None and l!=None):
                d['Name']=n.text
                d['Price']="₹"+p.text
                d['Brand']=b[0]
                d['Image']=i.get('src')
                # ratings.append(rating.text)
                d['ProductLink']='https://amazon.in/'+l.get('href')
                if(rating==None):
                    d["Rating"]="NaN"
                else:
                    nr=(rating.text).split(" ")
                    d["Rating"]=nr[0]
                d['FA']="Amazon"
                d['ID']=div['data-asin']
                Data.append(d)
    else:
        amazon=page_soup.findAll('div', attrs={'data-component-type': 's-search-result'})
        for div in amazon:
            d={}
            # b=div.find('span', attrs={'class':'a-size-base-plus a-color-base'})
            p=div.find('span', attrs={'class':'a-price-whole'})
            rating=div.find('span', attrs={'class':'a-icon-alt'})
                            # specification = containers.find('div', {'class':'_1rcHFq'})
            i=div.find('img',class_='s-image')
            n=div.find('span',attrs={'class':'a-size-base-plus a-color-base a-text-normal'})
            l=div.find('a',class_='a-link-normal s-no-outline')
            if(n==None):
                b='Nill'
            else:
                b=(n.text).split(' ')
            if(n!=None and p!=None and b!=None and i!=None and l!=None):
                d['Name']=n.text
                d['Price']="₹"+p.text
                d['Brand']=b[0]
                d['Image']=i.get('src')
                # ratings.append(rating.text)
                d['ProductLink']='https://amazon.in/'+l.get('href')
                if(rating==None):
                    d["Rating"]="NaN"
                else:
                    nr=(rating.text).split(" ")
                    d["Rating"]=nr[0]
                d['FA']="Amazon"
                d['ID']=div['data-asin']
                Data.append(d)

def flipkartSearch(x,p,Data):
    url = "https://www.flipkart.com/search?q={0}&page={1}"
    url = url.format(x,p)
    page = requests.get(url, headers=Headers(os='win',browser='chrome',headers=True).generate())
    html = page.content
    page_soup = bs4.BeautifulSoup(html, "html.parser")
    # print(page_soup)

    # Single grid
    if(page_soup.find('div',class_='tUxRFH')):
        flipkart=page_soup.findAll('div',class_='cPHDOP col-12-12')
        # print(len(flipkart))
        for div in flipkart:
            d={}
            n=div.find('div', attrs={'class':'KzDlHZ'})
            # print(n,end="\n")
            p=div.find('div', attrs={'class':'Nx9bqj _4b5DiR'})
            # print(p,end="\n")
            l=div.find('a',class_='CGtC98')
            # print(l,end="\n")
            i=div.find('img',class_='DByuf4')
            # print(i,end="\n")
            if(n!=None):
                b=(n.text).split(' ')
            rating=div.find('div',class_='XQDdHH')
            if(n!=None):
                d["Name"]=n.text
                d["Price"]=p.text
                d["Brand"]=b[0]
                d["Image"]=i.get('src')
                d["ProductLink"]="https://www.flipkart.com"+l.get('href')
                if(rating==None):
                    d["Rating"]="NaN"
                else:
                    d["Rating"]=rating.text
                d["FA"]="Flipkart"
                id=div.find('div')
                d["ID"]=id.find('div')['data-id']
                Data.append(d)

    #4 grid
    else:
        flipkart=page_soup.findAll('div',class_='cPHDOP col-12-12')
        for div in flipkart:
            d={}
            n=div.find('a', attrs={'class':'WKTcLC'})
            if(n==None):
                n=div.find('a', attrs={'class':'wjcEIp'})
            # print(n,end="\n")
            p=div.find('div', attrs={'class':'Nx9bqj'})
            l=div.find('a',class_='rPDeLR')
            if(l==None):
                l=div.find('a',class_='VJA3rP')
            # print(l,end="\n")
            i=div.find('img',class_='_53J4C-')
            if(i==None):
                i=div.find('img',class_='DByuf4')
            # print(i,end="\n")
            b=div.find('div',attrs={'class':'sy19yP'})
            if(b==None and n!=None):
                t=n.text.split(" ")
                b=t[0]
            # print(b,end="\n")
            r=div.find('div',class_='XQDdHH')
            # print(n,l,i,b,r,sep=" ")
            if(n!=None):
                d["Name"]=n.text
                d["Price"]=p.text
                if(b==None):
                    d["Brand"]="Nan"
                else:
                    d["Brand"]=b
                d["Image"]=i.get('src')
                d["ProductLink"]="https://www.flipkart.com"+l.get('href')
                if(r==None):
                    d["Rating"]="NaN"
                else:
                    d["Rating"]=r.text
                d["FA"]="Flipkart"
                id=div.find('div')
                d["ID"]=id.find('div')['data-id']
                Data.append(d)  


def poorvika(x,p,Data):
    url="https://poorvika.com/s?q={0}&page={1}"
    url=url.format(x,p)
    page=requests.get(url)
    page_soup = bs4.BeautifulSoup(page.content,"html.parser")
    # print(page_soup)
    for div in page_soup.findAll('div',class_='product-cardlist_card__IeCc4 product-cardlist_card--border__C3__Q no-select'):
        d={}
        n=div.find('div',class_='product-cardlist_product-tool-tip__lPD6f')
        l=div.find('a')
        i=div.find('img')
        p=div.find('span',class_='whitespace-nowrap')
        b=(n.text).split(' ')
        if(i!=None and n!=None and l!=None and p!=None):
                d["Name"]=n.text
                d["Price"]=p.text
                d["Brand"]=b[0]
                d["Image"]=i.get('src')
                d["ProductLink"]="https://www.poorvika.com"+l.get('href')
                d["Rating"]="NaN"
                d["FA"]="Poorvika"
                Data.append(d)
        

def Analyse():
    f=open("Data.json","r+")
    df=pd.read_json(f)
    folder="static/Page"
    for files in os.listdir(folder):
        fp=os.path.join(folder,files)
        if(os.path.exists(fp)):
            os.remove(fp)
    plt.clf()
    plt.figure(figsize=(12,8))
    plt.title("Market share")
    df["Brand"].value_counts().plot.pie(autopct="%.1f%%",startangle=90)
    plt.savefig("static/Page/Plot.png")
    plt.clf()
    plt.figure(figsize=(12,8))
    plt.title('Rating')
    df.groupby("Brand")["Rating"].sum().plot.bar()
    plt.savefig("static/Page/Rate.png")
    plt.clf()

def amazonReviewAnalyse(ASIN):
    url1="https://www.amazon.in/product-reviews/"+ASIN+"?pageNumber=1&filterByStar=positive"
    url2="https://www.amazon.in/product-reviews/"+ASIN+"?pageNumber=1&filterByStar=critical"
    postive=requests.get(url1, headers=Headers(os='win',browser='chrome',headers=True).generate())
    critical=requests.get(url2, headers=Headers(os='win',browser='chrome',headers=True).generate())
    page_soup1=bs4.BeautifulSoup(postive.content,"html.parser")
    page_soup2=bs4.BeautifulSoup(critical.content,"html.parser")
    # p1=page_soup1.findAll('div',attrs={'data-hook':'review'})
    # p2=page_soup2.findAll('div',attrs={'data-hook':'review'})
    Words=""
    Positive=[]
    Negative=[]
    for i in page_soup1.findAll('div',attrs={'data-hook':'review'}):
        review=i.find('a',attrs={'data-hook':'review-title'})
        if(review!=None):
            t=review.text.split("stars")
            Words+=t[1]+"\n"
            Positive.append(review.text)
    for i in page_soup2.findAll('div',attrs={'data-hook':'review'}):
        review=i.find('a',attrs={'data-hook':'review-title'})
        if(review!=None):
            t=review.text.split("stars")
            Words+=t[1]+"\n"
            Negative.append(review.text)
    # print(Words)
    if(Words=="" or len(Positive)==0 or len(Negative)==0):
        return [0,0,'Not enough review to analyse',0]
    
    Sentiment=sentiment_scores(Words)
    if Sentiment['compound'] >= 0.05 :
        Overall="Positive"

    elif Sentiment['compound'] <= - 0.05 :
        Overall="Negative"
    d=sentiment_scores(Words)
    plt.clf()
    sizes=[Sentiment['pos'],Sentiment['neg'],Sentiment['neu']]
    labels = ['Positive', 'Negative', 'Neutral']
    # only "explode" the 2nd slice (i.e. 'Hogs')
    explode = (0.1, 0, 0)  
    fig1, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    # Equal aspect ratio ensures that pie is drawn as a circle
    # ax1.axis('equal')  
    plt.tight_layout()
    fp="static/Product/Reviewplot.png"
    if(os.path.exists(fp)):
        os.remove(fp)
    plt.savefig("static/Product/Reviewplot.png")
    #Word Cloud
    w=WordCloud(width=800,height=400).generate(Words)
    fp="static/Product/WordCloud.png"
    if(os.path.exists(fp)):
        os.remove(fp)
    w.to_file("static/Product/WordCloud.png")
    Comments=[Positive[0],Negative[0],Overall,1]
    return Comments

def flipkartReviewAnalyse(FSN):
    url1="https://www.flipkart.com/product/product-reviews/itme=?pid="+FSN+"&sortOrder=POSITIVE_FIRST&page=1"
    url2="https://www.flipkart.com/product/product-reviews/itme=?pid="+FSN+"&sortOrder=NEGATIVE_FIRST&page=1"
    positive=requests.get(url1, headers=Headers(os='win',browser='chrome',headers=True).generate())
    critical=requests.get(url2, headers=Headers(os='win',browser='chrome',headers=True).generate())
    page_soup1=bs4.BeautifulSoup(positive.content,"html.parser")
    page_soup2=bs4.BeautifulSoup(critical.content,"html.parser")
    Words=""
    Positive=[]
    Negative=[]
    for i in page_soup1.findAll('div',class_="cPHDOP col-12-12"):
        if(i.find('div',class_='EKFha-')):
            if(i.find('div',class_='_11pzQk')):
                review=i.find('div',class_='_11pzQk')
            elif(i.find('p',class_='z9E0IG')):
                review=i.find('p',class_='z9E0IG')
            if(review!=None):
                Words+=review.text+"\n"
                Positive.append(review.text)
    for i in page_soup2.findAll('div',class_="cPHDOP col-12-12"):
        if(i.find('div',class_='EKFha-')):
            if(i.find('div',class_='_11pzQk')):
                review=i.find('div',class_='_11pzQk')
            elif(i.find('p',class_='z9E0IG')):
                review=i.find('p',class_='z9E0IG')
            if(review!=None):
                Words+=review.text+"\n"
                Negative.append(review.text)
    # print(Words)
    if(Words=="" or len(Positive)==0 or len(Negative)==0):
        return [0,0,'Not enough review to analyse',0]
    Sentiment=sentiment_scores(Words)
    if Sentiment['compound'] >= 0.05 :
        Overall="Positive"

    elif Sentiment['compound'] <= - 0.05 :
        Overall="Negative"
    plt.clf()
    sizes=[Sentiment['pos'],Sentiment['neg'],Sentiment['neu']]
    # Pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    explode = (0.1, 0, 0)  
    fig1, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')  
    plt.tight_layout()
    fp="static/Product/Reviewplot.png"
    if(os.path.exists(fp)):
        os.remove(fp)
    plt.savefig("static/Product/Reviewplot.png")
    #Word Cloud
    w=WordCloud(width=800,height=400).generate(Words)
    fp="static/Product/WordCloud.png"
    if(os.path.exists(fp)):
        os.remove(fp)
    w.to_file("static/Product/WordCloud.png")
    Comments=[Positive[0],Negative[0],Overall,1]
    return Comments

def sentiment_scores(sentence):
	sid_obj = SentimentIntensityAnalyzer()
	sentiment_dict = sid_obj.polarity_scores(sentence)
	return sentiment_dict
	
        