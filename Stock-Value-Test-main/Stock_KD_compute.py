# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 23:14:54 2019

@author: tazz4
"""
import requests,datetime,sqlite3,time


def str_to_num(s, c_type):
    if c_type not in ['float', 'int']:
        return s
    s = s.replace(',', '')
    try:
        if c_type == 'int':
            return int(s)
        else: #c_type == 'float':
            return float(s)
    except:
        return -1

def crawl_price(date):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebkit/537.36(KHTML, like Gecko) ''Chrome/66.0.3359.181 Safari/537.36'}
    datestr = date.strftime('%Y%m%d')
    resp = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=' + datestr + '&type=ALLBUT0999', headers = headers)
    data = resp.json()
    if 'data9' not in data:
        return None
    types = ['text', 'datetime', 'int', 'int', 'int', 'float', 'float', 'float', 'float', 'float', 'float', 'int', 'float', 'int', 'float']
    prices = []
    for item in data['data9']:
        if item[2] == '0':
            continue
        filtered = item[:1] + item[2:9] + item[10:]
        filtered = filtered[:1] + [date.strftime('%Y-%m-%d')] + filtered[1:]
        prices.append([str_to_num(s, types[i]) for i, s in enumerate(filtered)])
    return prices

"""for row in crawl_price(datetime.datetime(2019, 7, 25)):
    print(row)"""

def execute_db(fname, sql_cmd):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(sql_cmd)
    conn.commit()
    conn.close()

db_name = 'data.sqlite3'
'''cmd = 'CREATE TABLE daily_price (證券代號 TEXT, 日期 DATE, 成交股數 INTEGER, 成交筆數 INTEGER, 成交金額 INTEGER, 開盤價 REAL, 最高價 REAL, 最低價 REAL, 收盤價 REAL, 漲跌價差 REAL, 最後揭示買價 REAL, 最後揭示買量 INTEGER, 最後揭示賣價 REAL, 最後揭示賣量 INTEGER, 本益比 REAL)' 
execute_db(db_name, cmd)'''

def bulk_insert(fname, bulk_data):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute('BEGIN TRANSACTION')
    for d in bulk_data:
        values = ["'" + str(e) + "'" for e in d]
        cmd = 'INSERT OR REPLACE INTO daily_price VALUES({})'.format(','.join(values))
        c.execute(cmd)
    c.execute('COMMIT')
    conn.close()

def update_db(date_from, date_to):
    print('更新資料: {} 到 {}'.format(date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d')))
    current = date_from
    while current <= date_to:
        prices = crawl_price(current)
        if prices:
            bulk_insert(db_name, prices)
            print(current.strftime('%Y-%m-%d'), '...成功')
        else:
            print(current.strftime('%Y-%m-%d'), '...失敗(可能為假日)')
        current += datetime.timedelta(days=1)
        time.sleep(3)

def get_date_range_from_db(fname):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute('select * from daily_price order by 日期 ASC LIMIT 1;')
    date_from = datetime.datetime.strptime(list(c)[0][1], '%Y-%m-%d')
    c.execute('select * from daily_price order by 日期 DESC LIMIT 1;')
    date_to = datetime.datetime.strptime(list(c)[0][1], '%Y-%m-%d')
    return date_from, date_to

db_from, db_to = get_date_range_from_db(db_name)
print ('資料庫日期: {} 到 {}'.format(db_from.strftime('%Y-%m-%d'), db_to.strftime('%Y-%m-%d')))
date_from = db_to + datetime.timedelta(days=1)
date_to = datetime.datetime.today()
update_db(date_from, date_to)

def get_data(fname, stock_id, period):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    cmd = 'SELECT 日期, 收盤價 FROM daily_price WHERE 證券代號 = "{:s}" ORDER BY 日期 DESC LIMIT {:d};'.format(stock_id, period)
    c.execute(cmd)
    rows = c.fetchall()
    rows.reverse()
    conn.close()
    return rows

def calc_rsv(prices):
    window = prices[:8]
    highest = [0]*8
    lowest = [0]*8
    rsv_values = [0]*8
    k_values = [0]*7 + [50]
    d_values = [0]*7 + [50]
    for i, p in enumerate(prices[8:]):
        window.append(p)
        window = window[len(window)-9:]
        high = max(window)
        low = min(window)
        rsv = 100 * ((p - low) / (high - low))
        k = ((1/3)*rsv) +((2/3)*k_values[i-1])
        d = ((1/3)*k) +((2/3)*d_values[i-1])
        highest.append(high)
        lowest.append(low)
        rsv_values.append(rsv)
        k_values.append(k)
        d_values.append(d)
    return k_values, d_values

def get_buy_signal(k_values, d_values, dates):
    buy = [0]*8
    count = []
    for i in range(8, len(k_values)):
        if k_values[i-1] < d_values[i-1] and k_values[i] > d_values[i] and k_values[i] < 30:
            buy.append(1)
            count.append(dates[i])
        else:
            buy.append(0)
    return buy, count

        
file = open(r'C:\Users\tazz4\OneDrive\桌面\Program\Python\stock_test.txt')
for line in file:
    line = line.split('\n')[0]
    price_data = get_data(db_name, line, 1000)
    dates = [d[0] for d in price_data]
    prices = [d[1] for d in price_data]
    print('股票代號:' + line + ' 起始日期: {} (收盤價: {}), 結束日期: {} (收盤價: {}) ({} 天)'.format(dates[0], prices[0], dates[-1], prices[-1], len(dates)))
    k, d = calc_rsv(prices)
    buy, count = get_buy_signal(k, d, dates)
    print('期間有 {}次買進訊號'.format(sum(buy)))
    for q in count:
        print(q)
