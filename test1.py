import chardet
fobj=open('C:\\Users\\Administrator\\Desktop\\111.txt','r')
data=fobj.read()
print chardet.detect(data)['encoding']