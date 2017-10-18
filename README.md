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
### 二，如何使用线程本地数据？
##### 实际案例：
我们实现了一个web视频监控服务器，服务器端采用摄像头数据，客户端使用浏览器通过http请求接收数据。服务器使用推送的方式（multipart/x-mixed-replace）一直使用一个tcp连接客户端传递数据，这种方式将持续占用一个线程
导致单线程服务器无法处理多客户端请求。</br>
改写程序，在每个线程中处理一个客户端请求，支持多客户端访问。<br>
##### 解决方案：
threading.local函数可以创建线程本地数据空间，其下属性对每个线程独立存在。
```
import os, cv2, time, struct, threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import TCPServer, ThreadingTCPServer
from threading import Thread, RLock
from select import select

class JpegStreamer(Thread):
    def __init__(self, camera):
        Thread.__init__(self)
        self.cap = cv2.VideoCapture(camera)
        self.lock = RLock()
        self.pipes = {}

    def register(self):
        pr, pw = os.pipe()
        self.lock.acquire()
        self.pipes[pr] = pw
        self.lock.release()
        return pr

    def unregister(self, pr):
        self.lock.acquire()
        self.pipes.pop(pr)
        self.lock.release()
        pr.close()
        pw.close()

    def capture(self):
        cap = self.cap
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                #ret, data = cv2.imencode('.jpg', frame)
                ret, data = cv2.imencode('.jpg', frame, (cv2.IMWRITE_JPEG_QUALITY, 40))
                yield data.tostring()

    def send(self, frame):
        n = struct.pack('l', len(frame))
        self.lock.acquire()
        if len(self.pipes):
            _, pipes, _ = select([], self.pipes.itervalues(), [], 1)
            for pipe in pipes:
                os.write(pipe, n)
                os.write(pipe, frame)
        self.lock.release()

    def run(self):
        for frame in self.capture():
            self.send(frame)

class JpegRetriever(object):
    def __init__(self, streamer):
        self.streamer = streamer
        self.local = threading.local()

    def retrieve(self):
        while True:
            ns = os.read(self.local.pipe, 8)
            n = struct.unpack('l', ns)[0]
            data = os.read(self.local.pipe, n)
            yield data

    def __enter__(self):
        if hasattr(self.local, 'pipe'):
            raise RuntimeError()

        self.local.pipe = streamer.register()
        return self.retrieve()

    def __exit__(self, *args):
        self.streamer.unregister(self.local.pipe)
        del self.local.pipe
        return True

class Handler(BaseHTTPRequestHandler):
    retriever = None
    @staticmethod
    def setJpegRetriever(retriever):
        Handler.retriever = retriever

    def do_GET(self):
        if self.retriever is None:
            raise RuntimeError('no retriver')

        if self.path != '/':
            return

        self.send_response(200) 
        self.send_header("Content-type", 'multipart/x-mixed-replace;boundary=abcde')
        self.end_headers()

        with self.retriever as frames:
            for frame in frames:
                self.send_frame(frame)

    def send_frame(self, frame):
        self.wfile.write('--abcde\r\n')
        self.wfile.write('Content-Type: image/jpeg\r\n')
        self.wfile.write('Content-Length: %d\r\n\r\n' % len(frame))
        self.wfile.write(frame)

if __name__ == '__main__':
    streamer = JpegStreamer(0)
    streamer.start()

    retriever = JpegRetriever(streamer)
    Handler.setJpegRetriever(retriever)

    print 'Start server...'
    httpd = ThreadingTCPServer(('', 9000), Handler)
    httpd.serve_forever()
```
### 三，如何使用线程池？
##### 实际案例：
我们之前实现了一个多线程web视频监控服务器，我们需要对请求连接数做限制，以防止恶意用户发起大量连接而导致服务器创建大量线程，最终因资源耗尽而瘫痪。</br>
可以使用线程池，替代原来的每次请求创建线程。
##### 解决方案：
使用标准库中concurrent.futures下的ThreadPoolExcutor，对象的submit和map方法可以用来启动线程池中线程执行任务。
### 四，如何使用多进程？
##### 实际案例：
由于python中全局解释器锁(GIL)的存在，在任意时刻只允许一个线程在解释器中运行。因此python的多线程不适合处理CPU密集型的任务。
要想处理CPU密集型的任务，可以使用多进程模型。
##### 解决方案：
使用标准库中multiprocessing.Process,它可以启动子进程执行任务操作接口，进程间通信，进程间同步等都与Threading.Thread类似。
