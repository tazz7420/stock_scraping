import time
import stock_module as m

slist = m.get_setting()
cnt = len(slist)

log1 = []
log2 = []

for i in range(cnt):
    log1.append('')
    log2.append('')

check_cnt = 20
while True:
    for i in range(cnt):
        try:
            stockId, buyPrice, salePrice = slist[i]
            name, realtimePrice = m.google_finance(stockId)
            print('StockName:', name, 'Price:', realtimePrice)
            if buyPrice != 0:
                if realtimePrice <= buyPrice:
                    if log1[i] != 'buy':
                        m.send_by_line(name, realtimePrice,
                                    '買進（股價低於' + str(buyPrice) + '）')
                        log1[i] = 'buy'
            if salePrice != 0:
                if realtimePrice >= salePrice:
                    if log1[i] != 'sale':
                        m.send_by_line(name, realtimePrice,
                                    '賣出（股價高於' + str(salePrice) + '）')
                        log1[i] = 'sale'
            time.sleep(3)
            act, why = m.get_best(stockId)
            if why:
                if log2[i] != why:
                    m.send_by_line(name, realtimePrice, act + '（' + why + '）')
                    log2[i] = why
            time.sleep(5)
        except:
            print('讀取資料逾時')
            time.sleep(2)
    print('-------------------')
    check_cnt -= 1
    if check_cnt == 0:
        break
    time.sleep(180)
