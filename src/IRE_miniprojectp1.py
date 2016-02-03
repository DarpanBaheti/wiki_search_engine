#IRE_wiki_search_engine

import xml.sax
import re
from Stemmer import Stemmer
#from stemming.porter2 import stem
from collections import defaultdict
from heapq import *
from os import listdir
from os.path import isfile, join
import os

###	Stemmin
stem=Stemmer('english')
####	Stopwords List
textfile = open("src/stopwords.txt","r")
stopwords = textfile.readlines()
stopwords = [l.strip('\n\r') for l in stopwords]
textfile.close()

###	Regular expression
reg_exp =  re.compile(r'[^A-Za-z]+')

####	Index dictionary
###     global_cnt#d_id1=cnt1|d_id2=cnt2
dict_title = defaultdict(str)
dict_infobox = defaultdict(str)
dict_references = defaultdict(str)
dict_external = defaultdict(str)
dict_category = defaultdict(str)
dict_body = defaultdict(str)

cnt_page = 0
cnt_file = 0


#### Class structure...because SAX parser is used.
class ABContentHandler(xml.sax.ContentHandler):
	def __init__(self):
		xml.sax.ContentHandler.__init__(self)

    		self.doc_id = ""
    		self.title = ""
    		self.text = ""
    		self.infobox = ""
		self.body = ""
		self.references = ""
    		self.external = ""
    		self.category = ""

    		self.content =  "" 
    		self.current = ""
    		self.parent = ""
    		self.elements = []

	#### Stack Implementation which considers different starting and closing Tags.	
	#### Tag Hierarchy
	#### Self denotes the Current Page

	#### fucntion-Tag_Starts
  	def startElement(self, name, attrs):
    		self.elements.append(name)
    		if self.current:
        		self.parent = self.current
    		self.current = name
    		#if name=="page":
        		#print "=== PAGE STARTS ==="
 
	#### function-Tag_Ends
  	def endElement(self, name):
		global cnt_page

      		content = self.content

      		if name=="page":
			self.doc_id = ""
                        self.title = ""
                        self.text = ""
                        self.infobox = ""
			self.body = ""
			self.references = ""
                        self.external = ""
			self.category = ""
                       
                        self.content =  ""
                        self.current = ""
                        self.parent = ""

			cnt_page = cnt_page + 1;

          		#print "=== PAGE ENDS ==="
          		pass
      		if name=="id":
          		if self.parent == "page":
              			self.doc_id = self.content
				self.doc_id = self.doc_id.replace('\n', '')
              			#print "ID : " + self.doc_id      
				self.content=""
      		if name=="title":
          		self.title = self.content
			self.title = self.title.replace('\n','')
			self.content=""
         		#print "TITLE : " + self.title
		if name=="text":
			self.text = self.content
			#### Parsing Function
			self.parse_textfunc()
			self.content=""
			
		#### Takes Care of parent...stack implementation
      		self.elements.pop()
      		if self.elements:
          		self.current = self.parent
          		if len(self.elements) ==1:
              			self.parent=""
          		else:
              			self.parent= self.elements[-1]
      		else:
        		self.current=""
 
  	def characters(self, content):
      		uni = content.encode("utf-8").strip()
      		if uni:
          		self.content = self.content + "\n" + uni


	#### Parsing Fucntion 
	def parse_textfunc(self):
		global stopwords
		global reg_exp
		global dict_title 
		global dict_infobox
		global dict_references 
		global dict_external 
		global dict_category 
		global dict_body 
		global cnt_page 
		global cnt_file
	
		endflag_infobox = 0
		#### 1 - Write, 0 - Inactive 
		references_flag = 0
		external_flag = 0
		body_flag = 0

		#print self.text
		self.text = self.text.lower()
		for line in self.text.split('\n'):
			#print line

			####	Infobox
			if line == "}}" and endflag_infobox == 0:
				endflag_infobox = 1
				#self.infobox = self.infobox + line
				body_flag = 1
				continue
			if endflag_infobox == 0:
				body_flag = 0
				self.infobox = self.infobox + line + "\n"
				continue

			####	References
			if line == "==references==":
				references_flag = 1
				body_flag = 0
				continue
			if line == "==external links==" or line.startswith("[[category") == True or (line.startswith("==") == True and line.startswith("===") == False):
				references_flag = 0
				body_flag = 1
			if references_flag == 1:
				self.references = self.references + line + "\n"
				continue

			####	External Links
			if line == "==external links==":
				external_flag = 1
				body_flag = 0
				continue
			if line.startswith("[[category") == True:
				external_flag = 0
				body_flag = 1
			if external_flag == 1:
				self.external = self.external + line + "\n"
				continue

			####	Category
			if line.startswith("[[category") == True:
				body_flag = 0
				self.category = self.category + line + "\n"	

			####	Body
			if body_flag == 1 and endflag_infobox == 1 and references_flag == 0 and external_flag == 0:
				self.body = self.body + line + "\n"
				

		#print self.body
		#print "-----------------------"		
		
		cnt_d=defaultdict(int)

		for i in reg_exp.split(self.title):
			if len(i) > 0:
				x = i.strip()
				if x not in stopwords:
					y = stem.stemWord(x)
					#y = stem(x)
					if y in cnt_d:	
						cnt_d[x]+=1
					else:
						cnt_d[x]=1
		for i in cnt_d.keys():
			if i in dict_title:
				temp_t = dict_title[i].split("#")
				gnct = int(temp_t[0]) + 1
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_title[i] = str(gnct) + "#" + temp_t[1] + "|" + temp_s
			else:
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_title[i] = str(1) + '#' + temp_s
		cnt_d.clear()	

	
		for i in reg_exp.split(self.infobox):
			if len(i) > 0:
				x = i.strip()
				if x not in stopwords:
					y = stem.stemWord(x)
					#y = stem(x)
					if y in cnt_d:	
						cnt_d[x]+=1
					else:
						cnt_d[x]=1
		for i in cnt_d.keys():
			if i in dict_infobox:
				temp_t = dict_infobox[i].split("#")
				gnct = int(temp_t[0]) + 1
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_infobox[i] = str(gnct) + "#" + temp_t[1] + "|" + temp_s
			else:
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_infobox[i] = str(1) + '#' + temp_s
		cnt_d.clear()


		for i in reg_exp.split(self.references):
			if len(i) > 0:
				x = i.strip()
				if x not in stopwords:
					y = stem.stemWord(x)
					#y = stem(x)
					if y in cnt_d:	
						cnt_d[x]+=1
					else:
						cnt_d[x]=1
		for i in cnt_d.keys():
			if i in dict_references:
				temp_t = dict_references[i].split("#")
				gnct = int(temp_t[0]) + 1
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_references[i] = str(gnct) + "#" + temp_t[1] + "|" + temp_s
			else:
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_references[i] = str(1) + '#' + temp_s
		cnt_d.clear()


		for i in reg_exp.split(self.external):
			if len(i) > 0:
				x = i.strip()
				if x not in stopwords:
					y = stem.stemWord(x)
					#y = stem(x)
					if y in cnt_d:	
						cnt_d[x]+=1
					else:
						cnt_d[x]=1
		for i in cnt_d.keys():
			if i in dict_external:
				temp_t = dict_external[i].split("#")
				gnct = int(temp_t[0]) + 1
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_external[i] = str(gnct) + "#" + temp_t[1] + "|" + temp_s
			else:
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_external[i] = str(1) + '#' + temp_s
		cnt_d.clear()
		

		for i in reg_exp.split(self.category):
			if len(i) > 0:
				x = i.strip()
				if x not in stopwords:
					y = stem.stemWord(x)
					#y = stem(x)
					if y in cnt_d:	
						cnt_d[x]+=1
					else:
						cnt_d[x]=1
		for i in cnt_d.keys():
			if i in dict_category:
				temp_t = dict_category[i].split("#")
				gnct = int(temp_t[0]) + 1
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_category[i] = str(gnct) + "#" + temp_t[1] + "|" + temp_s
			else:
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_category[i] = str(1) + '#' + temp_s
		cnt_d.clear()


		for i in reg_exp.split(self.body):
			if len(i) > 0:
				x = i.strip()
				if x not in stopwords:
					y = stem.stemWord(x)
					#y = stem(x)
					if y in cnt_d:	
						cnt_d[x]+=1
					else:
						cnt_d[x]=1
		for i in cnt_d.keys():
			if i in dict_body:
				temp_t = dict_body[i].split("#")
				gnct = int(temp_t[0]) + 1
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_body[i] = str(gnct) + "#" + temp_t[1] + "|" + temp_s
			else:
				temp_s = str(self.doc_id) + '=' + str(cnt_d[i])
				dict_body[i] = str(1) + '#' + temp_s
		cnt_d.clear()

		#print cnt_page

		if cnt_page == 1000:
			cnt_file = cnt_file + 1
		
			keys = []

			keys = dict_title.keys()
			keys.sort()
			filename = "./Index/title/" + "title" + str(cnt_file) + ".txt"
			f = open(filename,'w')
			for i in keys:
				line = i + ":" + dict_title[i] + "\n"
				f.write(line)
			f.close()

			del keys[:]
			keys = dict_infobox.keys()
			keys.sort()
			filename = "./Index/infobox/" + "infobox" + str(cnt_file) + ".txt"
			f = open(filename,'w')
			for i in keys:
				line = i + ":" + dict_infobox[i] + "\n"
				f.write(line)
			f.close()
			
			del keys[:]
			keys = dict_references.keys()
			keys.sort()
			filename = "./Index/references/" + "references" + str(cnt_file) + ".txt"
			f = open(filename,'w')
			for i in keys:
				line = i + ":" + dict_references[i] + "\n"
				f.write(line)
			f.close()

			del keys[:]
			keys = dict_external.keys()
			keys.sort()
			filename = "./Index/external/" + "external" + str(cnt_file) + ".txt"
			f = open(filename,'w')
			for i in keys:
				line = i + ":" + dict_external[i] + "\n"
				f.write(line)
			f.close()

			del keys[:]
			keys = dict_category.keys()
			keys.sort()
			filename = "./Index/category/" + "category" + str(cnt_file) + ".txt"
			f = open(filename,'w')
			for i in keys:
				line = i + ":" + dict_category[i] + "\n"
				f.write(line)
			f.close()

			del keys[:]
			keys = dict_body.keys()
			keys.sort()
			filename = "./Index/body/" + "body" + str(cnt_file) + ".txt"
			f = open(filename,'w')
			for i in keys:
				line = i + ":" + dict_body[i] + "\n"
				f.write(line)
			f.close()

			dict_title.clear()
			dict_infobox.clear()
			dict_references.clear()
			dict_external.clear()
			dict_category.clear()
			dict_body.clear()
			cnt_page = 0
		
def rest_write():
	global stopwords
	global reg_exp
	global dict_title 
	global dict_infobox
	global dict_references 
	global dict_external 
	global dict_category 
	global dict_body 
	global cnt_page 
	global cnt_file
	cnt_file = cnt_file + 1
		
	keys = []

	keys = dict_title.keys()
	keys.sort()
	filename = "./Index/title/" + "title" + str(cnt_file) + ".txt"
	f = open(filename,'w')
	for i in keys:
		line = i + ":" + dict_title[i] + "\n"
		f.write(line)
	f.close()

	del keys[:]
	keys = dict_infobox.keys()
	keys.sort()
	filename = "./Index/infobox/" + "infobox" + str(cnt_file) + ".txt"
	f = open(filename,'w')
	for i in keys:
		line = i + ":" + dict_infobox[i] + "\n"
		f.write(line)
	f.close()
			
	del keys[:]
	keys = dict_references.keys()
	keys.sort()
	filename = "./Index/references/" + "references" + str(cnt_file) + ".txt"
	f = open(filename,'w')
	for i in keys:
		line = i + ":" + dict_references[i] + "\n"
		f.write(line)
	f.close()

	del keys[:]
	keys = dict_external.keys()
	keys.sort()
	filename = "./Index/external/" + "external" + str(cnt_file) + ".txt"
	f = open(filename,'w')
	for i in keys:
		line = i + ":" + dict_external[i] + "\n"
		f.write(line)
	f.close()

	del keys[:]
	keys = dict_category.keys()
	keys.sort()
	filename = "./Index/category/" + "category" + str(cnt_file) + ".txt"
	f = open(filename,'w')
	for i in keys:
		line = i + ":" + dict_category[i] + "\n"
		f.write(line)
	f.close()

	del keys[:]
	keys = dict_body.keys()
	keys.sort()
	filename = "./Index/body/" + "body" + str(cnt_file) + ".txt"
	f = open(filename,'w')
	for i in keys:
		line = i + ":" + dict_body[i] + "\n"
		f.write(line)
	f.close()

	dict_title.clear()
	dict_infobox.clear()
	dict_references.clear()
	dict_external.clear()
	dict_category.clear()
	dict_body.clear()
	cnt_page = 0


def merge_files(current_dir):
	global stopwords
	global reg_exp
	global dict_title 
	global dict_infobox
	global dict_references 
	global dict_external 
	global dict_category 
	global dict_body 
	global cnt_page 
	global cnt_file
	allfiles = [ f for f in listdir("./Index/"+current_dir+"/") if isfile(join("./Index/"+current_dir+"/",f)) ]
	#print allfiles

	outf = open(current_dir + ".txt",'w')

	#fcnt = 0
	fcnt = cnt_file
	heap_offile = []

	for i in allfiles:
		if ".txt" in i:
			filename="./Index/"+current_dir+"/"+i
			#fcnt = fcnt + 1
			f = open(filename,'r')
			heap_offile.append((f.readline()[:-1],f))	 

	#print heap_offile
	heapify(heap_offile)
	#print heap_offile
	#print fcnt

	while(fcnt):
		temp_list = []
		top = heappop(heap_offile)
		temp_list.append(top[0])
	
		#print temp_list

		next_line = top[1].readline()[:-1]
		if next_line=='':
			fcnt-=1
		else:
			heappush(heap_offile,(next_line,top[1]))

		while(True):
			try:
				top = heappop(heap_offile)
			except IndexError:
				break
		
			top_word = top[0].split(':')[0]
			current_word = temp_list[-1].split(':')[0]
	
			if current_word != top_word:
				if top_word=='':
					fcnt-=1
				else:
					heappush(heap_offile,(top[0], top[1]))
				break
			else:
				temp_list.append(top[0])
				f1 = top[1]
				next_line2 = f1.readline()[:-1]
				if next_line2 == '':
					fcnt-=1
				else:
					heappush(heap_offile, (next_line2,top[1]))
	
		word=''
		temp_gcnt=0
		temp_s=''
		for i in temp_list:
			a = i.split(':')
			word = a[0]
			temp_gcnt = temp_gcnt + int(a[1].split('#')[0])
			temp_s+= a[1].split('#')[1]
		outf.write(word + ":" + str(temp_gcnt) + "#" + temp_s+'\n')

	outf.close()
	for i in heap_offile:
		i[1].close()

					
def main(sourceFileName):
  	source = open(sourceFileName)
	xml.sax.parse(source, ABContentHandler())

	rest_write()

	merge_files("title")
	merge_files("infobox")
	merge_files("references")
	merge_files("external")
	merge_files("category")
	merge_files("body")

if __name__ == "__main__":
	main("sample.xml")
