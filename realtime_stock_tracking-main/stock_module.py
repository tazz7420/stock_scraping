import twstock, requests
from bs4 import BeautifulSoup

def get_setting():
    res = []
    try:
        with open('stock.txt') as f:
            slist = f.readlines()
            print('讀入:', slist)
            for lst in slist:
                s = lst.split(',')
                res.append([s[0].strip(), float(s[1]), float(s[2])])
    except:
        print('讀取錯誤')
    return res

def get_price(stockid):
    rt = twstock.realtime.get(stockid)
    if rt['success']:
        return (rt['info']['name'], float(rt['realtime']['latest_trade_price']))
    else:
        return (False, False)

def get_best(stockid):
    stock = twstock.Stock(stockid)
    bp = twstock.BestFourPoint(stock).best_four_point()
    if(bp):
        return ('買進' if bp[0] else '賣出', bp[1])
    else:
        return (False, False)

def send_by_line(v1, v2, v3):
    try:
        with open('LineToken.txt') as f:
            token = f.readline()
    except:
        print('Line Token讀取錯誤')
    headers = {
        'Authorization': 'Bearer ' + str(token), 
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    payload = {'message': '\n' + str(v1) + '股價:' + str(v2) + '\n' + '建議操作:' + str(v3)}
    r = requests.post('https://notify-api.line.me/api/notify', headers = headers, params = payload)
    return r.status_code

def google_finance(stockid):
    G_FINANCE_URL = 'https://www.google.com/search?q='
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebkit/537.36(KHTML, like Gecko) ''Chrome/66.0.3359.181 Safari/537.36'}
    resp = requests.get(G_FINANCE_URL + stockid, headers=headers)
    html = resp.content
    soup = BeautifulSoup(html, 'html5lib')
    stock = dict()
    spans = soup.find_all('span')
    stock['name'] = spans[18].text
    stock['current_price'] = spans[21].text
    return (stock['name'], float(stock['current_price']))

def get_history_price(year, month, stockid):
    STOCK_WEARM_URL = 'https://stock.wearn.com/cdata.asp?'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebkit/537.36(KHTML, like Gecko) ''Chrome/66.0.3359.181 Safari/537.36'}
    resp = requests.get(STOCK_WEARM_URL + 'year=' + str(year) + '&month=' + str(month) + '&kind=' + stockid, headers=headers)
    html = resp.content
    soup = BeautifulSoup(html, 'html5lib')
    sections = soup.find_all('tr')
    return (sections[2:-1])

def get_month_of_lastyear(currentYear, currentMonth):
    dates = []
    for i in range(12):
        month = currentMonth-i
        year = currentYear - 1911
        if month <= 0:
            outputMonth = 12 + month
            outputYear = year - 1
            if outputMonth < 10:
                outputMonth1 = '0' + str(outputMonth)
            else:
                outputMonth1 = str(outputMonth)
            dates.append(str(outputYear) + outputMonth1)
        else:
            outputMonth = month
            outputYear = year
            if outputMonth < 10:
                outputMonth1 = '0' + str(outputMonth)
            else:
                outputMonth1 = str(outputMonth)
            dates.append(str(outputYear) + outputMonth1)
    return(dates)
