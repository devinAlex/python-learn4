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

#coding:utf-8
from xml.etree.ElementTree import parse
f = open('C:\\Users\\Administrator\\Desktop\\demo.xml')
et = parse(f)
root = et.getroot()
list = []
for child in root:
	for detail in child.iter('constant'):
		result = {}
		result['name'] = detail.find('name').text
		result['age'] = detail.find('age').text
		result['school'] = detail.find('school').text
		list.append(result)
print list
===========================================
#coding:utf-8
import xlrd
book = xlrd.open_workbook('C:\\Users\\Administrator\\Desktop\\demo.xlsx')
table = book.sheet_by_index(0)
nrows = table.nrows
#ncols = table.ncols
list = []
for rownum in range(1,nrows):
	row = table.row_values(rownum)
	if row:
		result = {}
		result['name'] = row[0]
		result['age'] = row[1]
		result['school'] = row[2]
		list.append(result)
print list
