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
### 二，如何解析简单的xml文档？
使用标准库中的xml.etree.ElementTree,其中的parse函数可以解析xml文档。
### 三，如何构建xml文档？
使用标准库中的xml.etree.ElementTree,构建ElementTree,使用write方法写入文件。
```
from xml.etree.ElementTree import Element, ElementTree
from xml.etree.ElementTree import tostring
e = Element('Data')
e.set('name', 'abc')
e.text = '123'
e2 = Element('Row')
e3 = Element('Open')
e3.text = '8.80'
e2.append(e3)
e.text = None
e.append(e2)
et = ElementTree(e)
et.write('C:\\Users\\Administrator\\Desktop\\demo.xml')
print tostring(e)
```
```
from xml.etree.ElementTree import Element, ElementTree
import csv
def pretty(e, level=0):
	if len(e) > 0:
		e.text = '\n' + '\t' * (level + 1)
		for child in e:
			pretty(child, level + 1)
		child.tail = child.tail[:-1]
	e.tail = '\n' + '\t' * level
	
def csvToXml(fname):
	with open(fname, 'rb') as f:
		reader = csv.reader(f)
		headers = reader.next()
		
		root = Element('Data')
		for row in reader:
			eRow = Element('Row')
			root.append(eRow)
			for tag, text in zip(headers, row):
				e = Element(tag)
				e.text = text
				eRow.append(e)
	pretty(root)
	return ElementTree(root)
et = csvToXml('C:\\Users\\Administrator\\Desktop\\pingan2.csv')
et.write('C:\\Users\\Administrator\\Desktop\\pingan.xml')
```
### 四，如何读写excel?
使用第三方库xlrd和xlwt，这两个库分别用于excel读和写。
```
#import xlrd
#book = xlrd.open_workbook('C:\\Users\\Administrator\\Desktop\\111.xlsx')
#sheet = book.sheet_by_index(0) #get 0 sheet
#print sheet.nrows
#print sheet.ncols
import xlwt
wbook = xlwt.Workbook()
wsheet = wbook.add_sheet('mytest')
wbook.save('C:\\Users\\Administrator\\Desktop\\aaa.xlsx')
```
```
#coding:utf8
import xlrd, xlwt
rbook = xlrd.open_workbook('C:\\Users\\Administrator\\Desktop\\111.xlsx')
rsheet = rbook.sheet_by_index(0)

nc = rsheet.ncols
rsheet.put_cell(0, nc, xlrd.XL_CELL_TEXT, u'总分', None)

for row in xrange(1, rsheet.nrows):
	t = sum(rsheet.row_values(row, 1))
	rsheet.put_cell(row, nc, xlrd.XL_CELL_NUMBER, t, None)

wbook = xlwt.Workbook()
wsheet = wbook.add_sheet(rsheet.name)
style = xlwt.easyxf('align:vertical center, horizontal center')

for r in xrange(rsheet.nrows):
	for c in xrange(rsheet.ncols):
		wsheet.write(r, c, rsheet.cell_value(r, c), style)

wbook.save('C:\\Users\\Administrator\\Desktop\\output.xls')

```
### 五，线程操作
```
def handle(sid):
	print 'Download...(%d)' % sid
	url = 'http://table.finance.yahoo.com/table.scv?s=%s.sz'
	url %= str(sid).rjust(6,'0')
	rf = download(url)
	if rf is None: return
	
	print 'Covert to XML....(%d)' % sid
	fname = str(sid).rjust(6, '0') + '.xml'
	with open(fname, 'wb') as wf:
		csvToXml(rf, wf)
from threading import Thread
#第一种方法
t = Thread(target=handle, args=(1,0))
t.start()
#第二种方法，使用类
class MyThread(Thread):
	def __init__(self, sid):
		Thread.__init__(self)
		self.sid = sid
	
	def run(self):
		handle(self.sid)

t = MyThread(1)
t.start()

t.join()#阻塞 方法 等待线程执行完，才执行主线程
print 'main thread'
#==================================================
class MyThread(Thread):
	def __init__(self, sid):
		Thread.__init__(self)
		self.sid = sid
	
	def run(self):
		handle(self.sid)
threads =[]
for i in xrange(1, 11):
	t = MyThread(i)
	threads.append(t)
	t.start()
for t in threads:
	t.join()
```
由于全局解释器锁GIL（global interpreter lock）的存在，多线程进行CPU密集型操作并不能提高执行效率。</br>
```
import csv
from xml.etree.ElementTree import Element, ElementTree
import requests
from StringIO import StringIO
from threading import Thread
from Queue import Queue

class DownloadThread(Thread):
	def __init__(self, sid, queue):
		Thread.__init__(self)
		self.sid = sid
		self.url = 'http://table.finance.yahoo.com/table.scv?s=%s.sz'
		self.url %= str(sid).rjust(6,'0')
		self.queue = queue
	
	def download(self, url):
		response = requests.get(url, timeout=3)
		if response.ok:
			return StringIO(response.content)
	
	def run(self):
		#1.
		print 'Download', self.sid
		data = self.download(self.url)
		#2. (sid, data)
		self.queue.put((self.sid, data))
		
class CovertThread(Thread):
	def __init__(self, queue):
		Thread.__init__(self)
		self.queue = queue

	def csvToXml(self, scsv, fxml):
		reader = csv.reader(scsv)
		headers = reader.next()
		headers = map(lambda h:h.replace(' ',''), headers)
	
		root = Element('Data')
		for row in reader:
			eRow = Element('Row')
			root.append(eRow)
			for tag, text in zip(headers, row):
				e = Element(tag)
				e.text = text
				eRow.append(e)
	
		pretty(root)
		et = Element(root)
		et.write(fxml)
	def run(self):
		while True:
			sid, data = self.queue.get()
			print 'Covert', sid
			if sid == -1:
				break
			if data:
				fname = str(sid).rjust(6, '0') + '.xml'
				with open(fname, 'wb') as wf:
				self.csvToXml(data, wf)
def pretty(e, level=0):
	if len(e) > 0:
		e.text = '\n' + '\t' * (level + 1)
		for child in e:
			pretty(child, level + 1)
		child.tail = child.tail[:-1]
	e.tail = '\n' + '\t' * level

q = Queue()
dThreads = [DownloadThread(i, q) for i in xrange(1, 11)]
cThread = CovertThread(q)
for t in dThreads:
	t.start()
cThread.start()

for t in dThreads:
	t.join()

q.put((-1, None))
```
