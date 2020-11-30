#!/usr/bin/python
import os
import urllib2
import json
import signal
import time

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
	path = os.path.join("funds","html")
	onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

	companies = {}
	#jsonPath = os.path.join("funds","json")
	for idx, fund in enumerate(onlyfiles):
		print(idx,fund)
		html = Load(os.path.join("funds","html",fund))
		rows = html.split("\n")
		for row in rows:
			if "fundHoldingItemsData =" in row:
				index = row.index('=')
				jsonStr = row[index+1:-2]
				#Save(os.path.join(jsonPath,"{0}.txt".format(fund[:-5])),jsonStr)
				data = json.loads(jsonStr)
				#SaveJSON(os.path.join(jsonPath,"{0}.json".format(fund[:-5])), data)
				for item in data:
					for hold in item["holdingItemsList"]:
						if hold["aType"] == "2":
							if hold["aName"] in companies:
								companies[hold["aName"]]["count"] += 1
							else:
								companies[hold["aName"]] = { 
									"count": 1,
									"stock": hold["TICKER"]
								}
	
	csvText = ""
	Save("companies.csv",csvText)
	for key in companies:
		item = companies[key]
		try:
			csvText = "{0},{1},{2}\n".format(key.replace(",",""),item["stock"],item["count"])
			anchore = '<span class="html-attribute-name">jsname</span>="<span class="html-attribute-value">vWLAgc</span>" <span class="html-attribute-name">class</span>="<span class="html-attribute-value">IsqQVc NprOob XcVN5d</span>"&gt;</span>'
			anchore = '<span class="html-attribute-value">padding-left:0</span>"&gt;</span>Previous Close<span class="html-tag">&lt;/th&gt;</span><span class="html-tag">&lt;th&gt;</span>'
			Append("companies.csv",csvText.encode('utf-8'))
		except Exception as e:
			pass

if __name__ == "__main__":
	main()
