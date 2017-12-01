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
/////////////////////////////////////
import os
from ftplib import FTP, error_perm
class FTPUtils(object):
    def __init__(self, host):
        self.ftp = FTP()
        self.ftp.connect(host, 21)
        print '***Connected to host "%s"' % host

    #登录    
    def login(self, user, password):
        try:
            self.ftp.login(user, password)
        except error_perm:
            print 'ERROR: cannot login as %' % user
            self.ftp.quit()
            return
        print '***Logged in as %s' % user

    #移动到某个目录下
    def cwd(self, where):
        try:
            self.ftp.cwd(where)
        except error_perm:
            print 'ERRORL cannot CD to "%s"' % where
            self.ftp.quit()
            return
        print '*** Changed to "%s" folder' % where

    #下载文件
    def get(self, local):
        try:
            self.ftp.retrbinary('RETR %s' % local, open(local, 'wb').write)
            print "start"
        except error_perm:
            print 'ERROR: cannot read file "%s"' % local
            os.unlink(local)
        else:
            print '*** Downloaded "%s" to CWD' % local
            self.ftp.quit()
        print "end"
        return

    #列出当前目录
    def dir(self):
        self.ftp.dir()

    #下载当前目录所有文件
    def down_all(self, path):
        list = self.ftp.nlst()
        for l in list:
            self.ftp.retrbinary('RETR %s' % l, open(path + "/" + l, 'wb').write)
        return

    #关闭ftp连接
    def close(self):
        self.ftp.close()

#测试
if __name__ == "__main__":
    port = 22
    host = "xxx.cn"
    user = "xxx"
    password = "xxx"
    test = FTPUtils(host)
    test.login(user, password)
    test.cwd("application/logs")
    os.mkdir("logs")
    test.down_all("logs/")
    test.close()