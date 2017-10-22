```
#coding:utf8

#[题目1]斐波那契数据（Fibonacci Sequence），又称黄金分割数列，
#		指的是这样一个数列：1，1，2，3，5，8，13，21，......
# 		这个数列从第三项开始，每一项都等于前两项之和，求数列第n项
def memo(func):
	cache = {}
	def wrap(*args):
		if args not in cache:
			cache[args] = func(*args)
		return cache[args]
	return wrap
@memo
def fibonacci(n):
	if n <= 1:
		return 1
	return fibonacci(n-1) + fibonacci(n-2)
#fibonacci = memo(fibonacci)
#print fibonacci(50)
#[题目2]一个共有10个台阶的楼梯，从下面走到上面，一次只能迈1-3个台阶
#		并且不能后退，走完这个楼梯共有多少种方法
@memo
def climb(n, steps):
	count = 0
	if n == 0:
		count = 1
	elif n > 0:
		for step in steps:
			count += climb(n - step, steps)
	return count

print climb(10,(1,2,3))
```
### 一，如何为被装饰的函数保存元数据？
##### 实际案例：
在函数对象中保存着一些函数的元数据，例如：</br>
f.__name__ : 函数的名字</br>
f.__doc__ :函数文档字符串</br>
f.__module__: 函数所属模块名</br>
f.__dict__:属性字典</br>
f.__defaults__:默认参数元组</br>
我们在使用装饰器后，再使用上面这些属性访问时，看到的是内部包裹函数的元数据，原来函数的元数据变丢失了，应该如何解决?
##### 解决方案：
使用标准库functools中的装饰器wraps装饰内部包裹函数，可以制定将原函数的某些属性，更新到包裹函数上面。
```
from functools import update_wrapper, wraps, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES
def mydecorator(func):
	@wraps(func)
	def wrapper(*args, **kargs):
		'''wrapper function'''
		print 'In wrapper'
		func(*args, **kargs)
	#update_wrapper(wrapper, func, ('__name__', '__doc__'), ('__dict__',))
	#update_wrapper(wrapper, func)
	return wrapper
@mydecorator
def example():
	'''example function'''
	print 'In example'

print example.__name__
print example.__doc__
#print WRAPPER_ASSIGNMENTS
#print WRAPPER_UPDATES
```
### 二，如何定义带参数的装饰器？
##### 实际案例：
实现一个装饰器，它用来检查被装饰函数的参数类型，装饰器可以通过参数指明函数参数的类型，调用时如果检测出类型不匹配则抛出异常。
```
@typeassert(str, int, int)
def(a, b, c)
.....
@typeassert(y=list)
def g(x,y):
......
```
##### 解决方案：
提取函数签名：inspect.signature()</br>
带参数的装饰器，也就是根据参数定制化一个装饰器。可以看成生产装饰器的工厂。每次调用typeassert,返回一个特定的装饰器，然后用它去修饰其他函数。
```
from inspect import signature

def typeassert(*ty_args, **ty_kargs):
    def decorator(func):
        # func -> a,b 
        # d = {'a': int, 'b': str}
        sig = signature(func)
        btypes = sig.bind_partial(*ty_args, **ty_kargs).arguments
        def wrapper(*args, **kargs):
            # arg in d, instance(arg, d[arg])
            for name, obj in sig.bind(*args, **kargs).arguments.items():
                if name in btypes:
                    if not isinstance(obj, btypes[name]):
                        raise TypeError('"%s" must be "%s"' % (name, btypes[name]))
            return func(*args, **kargs)
        return wrapper
    return decorator

@typeassert(int, str, list)
def f(a, b, c):
    print(a, b, c)

f(1, 'abc', [1,2,3])
f(1, 2, [1,2,3])
```
### 三，如何实现属性可修改的函数装饰器？
##### 实际案例：
为分析程序内哪些函数执行时间开销较大，我们定义一个带timeout参数的函数装饰器。装饰功能如下：</br>
1，统计被装饰函数单次调用运行时间。</br>
2，时间大于参数timeout的，将此次函数调用记录到log日志中。<br>
3，运行时刻修改timeout的值。</br>
##### 解决方案：
为包裹函数增添一个函数，用来修改闭包中使用的自由变量。在python3中：使用nonlocal访问嵌套作用域中的变量引用.
```
from functools import wraps
import time
import logging

def warn(timeout):
	timeout = [timeout]
	def decorator(func):
		def wrapper(*args, **kargs):
			start = time.time()
			res = func(*args, **kargs)
			used = time.time() - start
			if used > timeout[0]:
				msg = '"%s": %s > %s' % (func.__name__, used, timeout[0])
				logging.warn(msg)
			return res
		def setTimeout(k):
			#nonlocal timeout
			timeout[0] = k
		wrapper.setTimeout = setTimeout 
		return wrapper
	
	return decorator
from  random import randint
@warn(1.5)
def test():
	print('In Test')
	while randint(0, 1):
		time.sleep(0.5)

for _ in range(30):
	test()
	
test.setTimeout(1)
for _ in range(30):
	test()
```
### 四，如何在类中定义装饰器？
##### 实际案例：
实现一个能将函数调用信息记录到日志的装饰器：</br>
1，把每次函数的调用时间，执行时间，调用次数写入日志。</br>
2，可以对被装饰函数分组，调用信息记录到不同日志。</br>
3，动态修改参数，比如日志格式。</br>
4，动态打开关闭日志输出功能。</br>
##### 解决方案：
为了让装饰器在使用上更加灵活，可以把类的实例方法作为装饰器，此时在包裹函数中就可以持有实例对象，便于修改属性和拓展功能。
```
import logging
from time import localtime,time, strftime, sleep

class CallingInfo(object):
	def __init__(self, name):
		log = logging.getLogger(name)
		log.setLevel(logging.INFO)
		fh = logging.FileHandler(name + '.log')
		log.addHandler(fh)
		log.info('Start'.center(50, '-'))
		self.log = log
		self.formatter = '%(func)s -> [%(time)s - %(used)s - %(ncalls)s]'
	
	def info(self, func):
		def wrapper(*args, **kargs):
			wrapper.ncalls += 1
			lt = localtime()
			start = time()
			res = func(*args, **kargs)
			used = time() - start
			info = {}
			info['func'] = func.__name__
			info['time'] = strftime('%x %X', lt)
			info['used'] = used
			info['ncalls'] = wrapper.ncalls
			msg = self.formatter % info
			self.log.info(msg)
			return res
		wrapper.ncalls = 0
		return wrapper
	def setFormatter(self, formatter):
		self.formatter = formatter
		
	def turnOn(self):
		self.log.setLevel(logging.INFO)
		
	def turnOff(self):
		self.log.setLevel(logging.WARN)
cinfo1 = CallingInfo('C:\\Users\\Administrator\\Desktop\\mylog1')
cinfo2 = CallingInfo('C:\\Users\\Administrator\\Desktop\\mylog2')		

cinfo1.setFormatter('%(func)s -> [%(time)s - %(ncalls)s]')
cinfo2.turnOff()

@cinfo1.info
def f():
	print 'in f'
@cinfo1.info
def g():
	print 'in g'
@cinfo2.info
def h():
	print 'in h'
	
from random import choice
for _ in xrange(50):
	choice([f, g, h])()
	sleep(choice([0.5, 1, 1.5]))
```


