# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 22:08:39 2019

@author: tazz4
"""
import requests
from bs4 import BeautifulSoup

def get_web_page(url,stock_id):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebkit/537.36(KHTML, like Gecko) ''Chrome/66.0.3359.181 Safari/537.36'}
    resp = requests.get(url + stock_id, headers = headers)
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

def get_stock_info(dom):
    soup = BeautifulSoup(dom, 'html5lib')
    stock = dict()
    sections = soup.find_all('g-card-section')
    
    stock['name'] = sections[1].div.text
    spans = sections[1].find_all('div', recursive = False)[1].find_all('span', recursive = False)
    """recursive = False--->表示只搜索下一層，不要再往更深層搜索 """
    stock['current_price'] = spans[0].text
    stock['current_change'] = spans[1].text
    
    for table in sections[3].find_all('table')[1]:
        for tr in table.find_all('tr')[2:4]:
            key = tr.find_all('td')[0].text.lower().strip()
            value = tr.find_all('td')[1].text.strip()
            stock[key] = value
            
    return stock

file = open(r'C:\Users\tazz4\OneDrive\桌面\Program\Python\stock_id.txt')
for line in file:
    line1 = line.split(',')[0]
    price = line.split(',')[1].split('\n')[0]
    stock_num = 'TPE' + line1
    G_FINANCE_URL = 'https://www.google.com/search?q='
    page = get_web_page(G_FINANCE_URL, stock_num)
    if page:
        stock = get_stock_info(page)
        """print (stock['current_price'].split(' TWD')[0])"""
        for k, v in stock.items():
            print (k,v)
        if price > stock['current_price'].split(' TWD')[0]:
            print (stock['current_price'].split(' TWD')[0] + r' 低於希望買進價格' + price + r' 買進買進!!!!' + '\n')
        else:
            print ('\n')