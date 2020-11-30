#!/usr/bin/python
import os
import urllib2
import json
import signal
import time

gExit = False

def Save (filename, data):
	file = open(filename, "w")
	file.write(data)
	file.close()

def SaveJSON(filename, data):
	db_file = open(filename, "w")
	json.dump(data, db_file, indent=2)
	db_file.close()

def GetRequest (url, with_dealy):
	try:
		req = urllib2.urlopen(url, timeout=1)
		if req != None:
			if with_dealy != 0:
				time.sleep(with_dealy)
			data = req.read()
		else:
			return "failed"
	except:
		return "failed"

	return data

def signal_handler(signal, frame):
	global gExit
	gExit = True

def main():
	global gExit
	signal.signal(signal.SIGINT, signal_handler)
	html = GetRequest("https://www.funder.co.il/fundList.aspx", 0)
	#Save("funder.html", html)
	rows = html.split("\n")
	for row in rows:
		if "fundlistData =" in row:
			index = row.index('=')
			jsonStr = row[index+1:-2]
			#Save("funder.txt",jsonStr)
			data = json.loads(jsonStr)
			#dataEncoded = json.JSONEncoder(ensure_ascii=False).encode(data)
			#SaveJSON("funder.json", data)
			length = len(data["x"])
			for idx, item in enumerate(data["x"]):
				if gExit is True:
					return
				print("Requesting {0}/{1} for FUND ID {2}".format(str(idx),str(length),item["fundNum"]))
				filePath = "{0}.html".format(os.path.join("funds","html",str(item["fundNum"])))
				if not os.path.exists(filePath):
					fundHtml = GetRequest("https://www.funder.co.il/fund/{0}".format(item["fundNum"]), 1)
					Save(filePath, fundHtml)

if __name__ == "__main__":
	main()
