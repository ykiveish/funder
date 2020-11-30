#!/usr/bin/python
import os
import urllib2
import json
import signal
import time
import datetime
from datetime import date

gExit = False

def Load(filename):
	if os.path.isfile(filename) is True:
		file = open(filename, "r")
		data = file.read()
		file.close()
		return data
	return ""
	
def Save(filename, data):
	file = open(filename, "w")
	file.write(data)
	file.close()

def Append(filename, data):
		file = open(filename, "a")
		file.write(data)
		file.close()

def SaveJSON(filename, data):
	db_file = open(filename, "w")
	json.dump(data, db_file, indent=2)
	db_file.close()

def GetRequest (url, with_dealy):
	try:
		hdr = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			'Accept-Encoding': 'none',
			'Accept-Language': 'en-US,en;q=0.8',
			'Connection': 'keep-alive'
		}
		req = urllib2.Request(url, headers=hdr)
		page  = urllib2.urlopen(req, timeout=5)
		if page  != None:
			if with_dealy != 0:
				time.sleep(with_dealy)
			data = page .read()
		else:
			return "failed (timeout)"
	except Exception as e:
		print(e)
		return "failed"

	return data

def signal_handler(signal, frame):
	global gExit
	gExit = True

def main():
	global gExit
	signal.signal(signal.SIGINT, signal_handler)

	companies = [
		{
			"stock": "tesla"
		},
		{
			"stock": "apple" 
		},
		{
			"stock": "microsoft" 
		},
		{
			"stock": "amazon" 
		},
		{
			"stock": "intel" 
		},
		{
			"stock": "wix" 
		},
		{
			"stock": "facebook" 
		},
		{
			"stock": "rada" 
		},
		{
			"stock": "ge" 
		},
		{
			"stock": "ge" 
		},
		{
			"stock": "nikola" 
		},
		{
			"stock": "kndi" 
		},
		{
			"stock": "spaq" 
		},
		{
			"stock": "kcac" 
		},
		{
			"stock": "jfrog" 
		},
		{
			"stock": "fly" 
		},
		{
			"stock": "CL=F" 
		},
		{
			"stock": "QCOM" 
		},
	]

	timestamp = 0
	interval = 5 * 60
	while (True):
		try:
			currTime = datetime.datetime.now().time()
			if (currTime > datetime.time(16,25) and currTime < datetime.time(23,5)):
				if (time.time() - timestamp > interval):
					today = datetime.datetime.today()
					dateNow = today.strftime("%a %b %d %Y %H:%M:%S")
					print("Sampling ... ({0})".format(str(dateNow)))
					for company in companies:
						if gExit is True:
							return
						url = "https://www.google.com/search?q={0}+stock".format(company["stock"])
						print(url)
						data = GetRequest(url, 0)
						ancore = 'IsqQVc NprOob XcVN5d">'
						index = data.index(ancore)
						subindex = data[index+len(ancore):].index('</')
						stockPrice = data[index+len(ancore):index+len(ancore)+subindex]
						dataToSave = "{0},{1},{2},{3}\n".format(str(time.time()),str(dateNow),str(today.strftime("%H:%M:%S")),str(stockPrice.replace(",","")))
						filePath = os.path.join("monitor","{0}.csv".format(company["stock"]))
						Append(filePath, dataToSave)
					timestamp = time.time()
				else:
					time.sleep(1)
					if gExit is True:
						return
			else:
				time.sleep(1)
				if (time.time() - timestamp > 30):
					print("Stock market closed ({0})".format(str(currTime)))
					timestamp = time.time()
				if gExit is True:
					return
		except Exception as e:
			print(e)
			if gExit is True:
				return

if __name__ == "__main__":
	main()
