import time, csv, os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import stock_module as m

slist = m.get_setting()
cnt = len(slist)

currentDateTime = datetime.datetime.today()
month = currentDateTime.month
year = currentDateTime.year
fileDate = m.get_month_of_lastyear(year, month)

for i in range(cnt):
    stockId, buyPrice, salePrice = slist[i]
    for date in fileDate:
        filePath = 'stock-price/' + stockId + '-' + date + '.csv'
        if not os.path.isfile(filePath):
            outputFile = open(filePath, 'w' , newline='', encoding='big5')
            outputWriter = csv.writer(outputFile)
            historyPriceList = m.get_history_price(str(date[0:3]),str(date[3:]), stockId)
            print(historyPriceList[1])
            time.sleep(3)
            outputFile.close()
