res = {}
with open('C:\\Users\\Administrator\\Desktop\\111.txt') as f:
	for char in f.read().replace(' ',''):
		res[char] = res.get(char, 0)+1
for c, num in sorted(res.items(), key = lambda x: x[1],reverse=True)[:3]:
	print '%s count is %d' %(c, num)

import os
#修改文件
os.rename("111.txt","wancheng.txt")
#删除文件
os.remove("111.txt")
#获取当前python所在路径
os.getcwd()
#获取指定目录中的文件和文件夹
os.listdir(".")
