###  一，如何使用生成器函数实现可迭代对象?
##### 实际案例:
实现一个可迭代对象的类，它能迭代给定范围内所有素数：
```
pn = PrimeNumbers(1,30)
for k in pn:
	print k,
输出结果：2 3 5 7 11 13 17 19 23 29
```
##### 解决方案：
将该类的__iter__方法实现生成器函数，每次yield返回一个素数。含有yield的语句的函数，即是生成器函数。
```
class PrimeNumbers:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        
    def isPrimeNum(self, k):
        if k < 2:
            return False
        
        for i in xrange(2, k):
            if k % i == 0:
                return False
            return True
    
    def __iter__(self):
        for k in xrange(self.start, self.end + 1):
            if self.isPrimeNum(k):
                yield k
for x in PrimeNumbers(2, 30):
    print x
```
### 二，如何进行反向迭代以及如何实现反向迭代？
##### 实际案例：
实现一个连续浮点数发生器FloatRange(和xrange类似)，根据给定范围(start,end)和步进值(step)产生一系列连续浮点数，如迭代FloatRange(3.0, 4.0,0.2)可产生序列：
 `正向：3.0->3.2->3.4->3.6->3.8->4.0
 反向：4.0->3.8->3.6->3.4->3.2->3.0 `  
 
 *反序列列表：l = [1,2,3,4]  l,reverse() l[::-1]*
```
class FloatRange:
	def __init__(self, start, end, step):
		self.start = start
		self.end = end
		self.step = step
	
	def __iter__(self):
		t = self.start
		while t <= self.end:
			yield t
			t += self.step
	
	def __reversed__(self):
		t = self.end
		while t >= self.start:
			yield t 
			t -= self.step

for x in reversed(FloatRange(1.0, 4.0, 0.5)):
	print x
```