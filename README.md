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


