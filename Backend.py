from flask import Flask, render_template
import pandas as pd
import requests
import bs4
import json
import cloudscraper
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
    url=url.format(x,p)
    page = requests.get(url, headers=Headers(os='win',browser='chrome',headers=True).generate())
    html = page.content
    page_soup = bs4.BeautifulSoup(html,"html.parser")

    amazon = page_soup.findAll('div', attrs={'data-component-type': 's-search-result'})
    for div in amazon:
        d={}
        p_elem = div.find('span', attrs={'class':'a-price-whole'})
        rating = div.find('span', attrs={'class':'a-icon-alt'})
        i = div.find('img', class_='s-image')
        
        n_h2 = div.find('h2')
        n = n_h2.find('span') if n_h2 else None
        
        l = div.find('a', class_='a-link-normal s-no-outline') or div.find('a', class_='a-link-normal')
                
        if(n==None):
            b='Nill'
        else:
            b=(n.text).split(' ')
            
        if(n!=None and p_elem!=None and b!=None and i!=None and l!=None):
            d['Name']=n.text
            d['Price']="₹"+p_elem.text
            d['Brand']=b[0]
            d['Image']=i.get('src')
            
            href = l.get('href', '')
            if href.startswith('http'):
                d['ProductLink'] = href
            else:
                d['ProductLink']='https://amazon.in'+href
                
            if(rating==None):
                d["Rating"]="NaN"
            else:
                nr=(rating.text).split(" ")
                d["Rating"]=nr[0]
            d['FA']="Amazon"
            d['ID']=div.get('data-asin', '')
            Data.append(d)

def flipkartSearch(x,p,Data):
    url = f"https://www.flipkart.com/search?q={x}&page={p}"
    scraper = cloudscraper.create_scraper()
    page_soup = bs4.BeautifulSoup(scraper.get(url).text, "html.parser")

    seen_ids = set()
    for node in page_soup.find_all('div', attrs={'data-id': True}):
        item_id = node.get('data-id')
        if not item_id or item_id in seen_ids:
            continue
            
        curr = node
        while curr and curr.name != 'body':
            if curr.find('img') and any('/p/' in a['href'] or 'pid=' in a['href'] for a in curr.find_all('a', href=True)) and any('₹' in s for s in curr.strings):
                break
            curr = curr.parent

        if not curr or curr.name == 'body':
            continue
            
        link_node = next((a for a in curr.find_all('a', href=True) if '/p/' in a['href'] or 'pid=' in a['href']), None)
        img_node = curr.find('img')
        
        if not link_node or not img_node: 
            continue

        strings = [s.strip() for s in curr.strings if s.strip()]
        name = img_node.get('alt', '').strip() or next((s for s in strings if len(s) > 15), "Nill")
        price = next((s for s in strings if '₹' in s), None)
        rating = next((s for s in strings if len(s) <= 3 and s.replace('.', '', 1).isdigit() and '.' in s), "NaN")
        
        if not price: 
            continue

        Data.append({
            "Name": name,
            "Price": price,
            "Brand": name.split(' ')[0] if name != "Nill" else "NaN",
            "Image": img_node.get('src', ''),
            "ProductLink": "https://www.flipkart.com" + link_node['href'] if link_node['href'].startswith('/') else link_node['href'],
            "Rating": rating,
            "FA": "Flipkart",
            "ID": item_id
        })
        seen_ids.add(item_id)


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
	
        