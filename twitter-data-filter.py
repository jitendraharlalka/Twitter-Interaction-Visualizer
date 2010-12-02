import urllib
import simplejson
import re
from xml.dom import minidom

class Graph:
	def __init__(self):
		self.term='%23ff'
		self.rpp=100
		self.url="http://search.twitter.com/search.json"
		self.userProfile="http://api.twitter.com/1/users/show.xml"
		self.data=[]		
		self.fetchFirstPage()

	def fetchFirstPage(self):
		urlHandle=urllib.urlopen(self.url+"?q="+self.term+"&rpp="+str(self.rpp))
		jsonData=simplejson.load(urlHandle)
		tempData=jsonData["results"]
		self.data+=tempData
		print jsonData["next_page"]
		print len(self.data)
		try:
			if(len(tempData)==self.rpp):
				print "page"		
				self.fetchSubsequentPages(jsonData["next_page"])
		except KeyError:
			print "Hit error"
		self.dataBuild()
		
	def fetchSubsequentPages(self,next_page):
		urlHandle=urllib.urlopen(self.url+next_page+"&rpp="+str(self.rpp))
		jsonData=simplejson.load(urlHandle)
		tempData=jsonData["results"]
		self.data+=tempData
		print len(self.data)
		print jsonData["next_page"]
		try:
			if(len(tempData)==self.rpp):
				print "page"
				"""self.fetchSubsequentPages(jsonData["next_page"])"""
		except KeyError:
			print "Hit error"

	def dataBuild(self):
		pattern1=re.compile(r" @[A-Za-z0-9_]+")
		pattern2=re.compile(r"^@[A-Za-z0-9_]+")
		allCombinations=[]
		allUsers=set()
		for datum in self.data:
			tweet=datum['text']
			mentions=re.findall(pattern1,tweet)
			a=re.search(pattern2,tweet)
			if(a):
				mentions.append(a.group(0))
				mentions.append(datum['from_user'])
				noUnicode=[handle.encode('ascii','ignore') for handle in mentions]
				trimmed=[handle.strip() for handle in noUnicode]
				user=[]
				for handle in trimmed:
					if(handle[0]=="@"):
						user.append(handle[1:].lower())
						allUsers.add(handle[1:].lower())
					else:
						user.append(handle.lower())
						allUsers.add(handle.lower())
				allCombinations.append(user)
		print allCombinations
		print allUsers
		networkData={"nodes":[],"links":[]}
		for iuser in allUsers:
			networkData["nodes"].append({'nodeName':iuser, 'group':1})
		for msg in allCombinations:
			source=msg[len(msg)-1]
			sourceIndex=networkData["nodes"].index({'nodeName':source, 'group':1})
			for target in msg[:-1]:
				targetIndex=networkData["nodes"].index({'nodeName':target, 'group':1})
				networkData["links"].append({'source':sourceIndex, 'target':targetIndex, 'value':1})
		print
		print networkData

		datafile=open('jsonData.js','w')
		datafile.write("var tweeples=")
		simplejson.dump(networkData,datafile)
		datafile.write(";")
		datafile.flush()
		datafile.close()

if __name__=="__main__":
	Graph()
