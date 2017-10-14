### 一，如何读写csv数据？
##### 实际案例：
http://table.finance.yahoo.com/table.csv?s=000001.sz我们可以通过雅虎网站获取中国股市（深市）数据集，它以csv数据格式存储.请将平安银行这支股票，在2016年终成交量超过50000000的记录存储到另一个csv文件中。
##### 解决方案：
使用标准库中的csv模块，可以使用其中reader和writer完成csv文件读写。
```
from urllib import urlretrieve
import csv
#urlretrieve('http://quotes.money.163.com/service/chddata.html?code=0000001&start=19901219&end=20150911&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER', 'C:\\Users\\Administrator\\Desktop\\pingan.csv')
with open('C:\\Users\\Administrator\\Desktop\\pingan.csv', 'rb') as rf:
	reader = csv.reader(rf)
	with open('C:\\Users\\Administrator\\Desktop\\pingan2.csv', 'wb') as wf:
		writer = csv.writer(wf)
		headers = reader.next()
		writer.writerow(headers)
		for row in reader:
			if row[0] < '2015-01-01':
				break
			if int(row[10]) >= 600000000:
				writer.writerow(row)
print 'end'
```
