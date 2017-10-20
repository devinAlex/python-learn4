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