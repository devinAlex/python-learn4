### 一，如何在线程间进行时间通知？
##### 实际案例：
我们通过雅虎网站获取了中国股市某支股票csv数据文件，我们现在下载了多支股票的csv数据，并将其转换为xml文件，额外需求：实现一个线程，将转换出的xml文件压缩打包，比如转换线程每生产出100个xml文件，就通知打包线程将它们打包成一个xxx.tgz文件，并删除xml文件。打包完成后，打包线程反过来通知转化线程，转换线程继续转换。
##### 解决方案：
线程间的事件通知，可以使用标准库中Threading.Event:</br>
1,等待事件一端调用wait，等待事件。</br>
2,通知事件一端调用set，通知事件。</br>
```
import csv
from xml.etree.ElementTree import Element, ElementTree
import requests
from StringIO import StringIO
from threading import Thread, Event
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
	def __init__(self, queue, cEvent, tEvent):
		Thread.__init__(self)
		self.queue = queue
		self.cEvent = cEvent
		self.tEvent = tEvent

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
		count = 0
		while True:
			sid, data = self.queue.get()
			print 'Covert', sid
			if sid == -1:
				self.cEvent.set()
				self..tEvent.wait()
				break
			if data:
				fname = str(sid).rjust(6, '0') + '.xml'
				with open(fname, 'wb') as wf:
					self.csvToXml(data, wf)
				count += 1
				if count == 5:
					self.cEvent.set()
					self.tEvent.wait()
					self.tEvent.clear()
					count = 0

import tarfile
import os
class TarThread(Thread):
	def __init__(self, cEvent, tEvent):
		Thread.__init__(self)
		self.count = 0
		self.cEvent = cEvent
		self.tEvent = tEvent
		self.setDaemon(True)
	
	def tarXML(self):
		self.count += 1
		tfname = '%d.tgz' % self.count
		tf = tarfile.open(tfname, 'w:gz')
		for fname in os.listdir('.'):
			if fname.endswith('.xml'):
				tf.add(fname)
				os.remove(fname)
		tf.close()
	
		if not tf.members:
			os.remove(tfname)
	def run(self):
		 while True:
			self.cEvent.wait()
			self.tarXML()
			self.cEvent.clear()
			
			self.tEvent.set()
def pretty(e, level=0):
	if len(e) > 0:
		e.text = '\n' + '\t' * (level + 1)
		for child in e:
			pretty(child, level + 1)
		child.tail = child.tail[:-1]
	e.tail = '\n' + '\t' * level
if __name__ == '__main__':
	q = Queue()
	dThreads = [DownloadThread(i, q) for i in xrange(1, 11)]
	
	cEvent = Event()
	tEvent = Event()
	
	cThread = CovertThread(q, cEvent, tEvent)
	tThread = TarThread(cEvent, tEvent)
	tThread.start()
	
	for t in dThreads:
		t.start()
	cThread.start()

	for t in dThreads:
		t.join()

	q.put((-1, None))
```