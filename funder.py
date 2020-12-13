#!/usr/bin/python
import os
#import urllib2
import json
import signal
import time
from urllib.request import urlopen

gExit = False

def Load(filename):
	if os.path.isfile(filename) is True:
		file = open(filename, "r")
		data = file.read()
		file.close()
		return data
	return ""

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
		req = urlopen(url, timeout=1)
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

def GetFunderJsonDB():
	html = GetRequest("https://www.funder.co.il/fundList.aspx", 0).decode()
	rows = html.split("\n")
	# Itterate HTML rows
	for row in rows:
		# Look for "fundlistData"
		if "fundlistData =" in row:
			# Find start of JSON format from string
			index = row.index('=')
			return row[index+1:-2]
	return None

def GetFundInfoFromJson(data):
	funds_info = []
	for idx, item in enumerate(data):
		funds_info.append({
			'id': item["fundNum"],
			'name': item["fundName"],
		})
	
	return funds_info

def ExportFundInfoToCSV(data):
	csv = ""
	for fund in data:
		csv += "{0},{1}\n".format(fund["id"],json.dumps(fund["name"], ensure_ascii=False))
	Save("funds_info.csv",csv)

def GetFundInfoFromDB(fund_id):
	try:
		data = GetRequest("https://www.funder.co.il/fund/{0}".format(fund_id), 1)
		if data is not None:
			html = data.decode()
			rows = html.split("\n")
			# Itterate HTML rows
			for row in rows:
				# Look for "fundHoldingItemsData"
				if "fundHoldingItemsData =" in row:
					# Find start of JSON format from string
					index = row.index('=')
					return row[index+1:-2]
	except:
		print("ERROR (GetFundInfoFromDB): Fund id {0}".format(fund_id))
	return None

def GetCompanies(data):
	companies = {}
	for holds in data:
		holding_list = holds["holdingItemsList"]
		for hold in holding_list:
			if hold["fType"] == "1001":
				if hold["aName"] in companies:
					companies[hold["aName"]]["count"] += 1
				else:
					companies[hold["aName"]] = { 
						"count": 1,
						"ticker": hold["TICKER"]
					}
	return companies

def ImportCompanies(funds_list):
	'''
	[
		{
			"title": "חוזים עתידיים – מניות",
			"holdingItemsList": [
				"aType": "2",
				"perc": "0.01",
				"aName": "AMERICAN AIRLINES GROUP INC.",
				"TICKER": "AAL",
				"fType": "1001",
				"title": "מניות חו'ל",
				"valShk": "4381.93",
				"amount": "100",
				"aghachRate": ""
			]
		},
		{
			"title": "ים מדינה חו'ל",
			"holdingItemsList": [
			]
		},
	]
	'''
	companies = {}
	funds_count = len(funds_list)
	for idx, fund in enumerate(funds_list):
		print("Importing companies from fund id {0} ({1}/{2})...({3:.4g}%)".format(fund["id"],idx,funds_count,(idx/funds_count*100)))
		json_fund_str  = GetFundInfoFromDB(fund["id"])
		try:
			if json_fund_str is not None:
				Save(os.path.join("output","{0}.json".format(fund["id"])), json_fund_str)
				json_fund_info = json.loads(json_fund_str)

				for holds in json_fund_info:
					holding_list = holds["holdingItemsList"]
					for hold in holding_list:
						if hold["fType"] == "1001":
							if hold["aName"] in companies:
								companies[hold["aName"]]["count"] += 1
								companies[hold["aName"]]["funds"].append({
									"name": fund["name"],
									"id": fund["id"]
								})
							else:
								funds = [{
									"name": fund["name"],
									"id": fund["id"]
								}]
								companies[hold["aName"]] = { 
									"count": 1,
									"ticker": hold["TICKER"],
									"funds": funds
							}
		except:
			print("ERROR (ImportCompanies): Fund id {0}".format(fund["id"]))
		time.sleep(0.5)
	return companies

def ExportCompaniesToCSV(companies):
	csv = ""
	for key in companies:
		company = companies[key]

		funds_id_list = ""
		funds_name_list = ""
		for fund in company["funds"]:
			funds_id_list += "{0} | ".format(fund["id"])
			funds_name_list += "{0} | ".format(fund["name"])
		csv += "{0},{1},{2},{3},{4}\n".format(json.dumps(key, ensure_ascii=False),json.dumps(company["ticker"], ensure_ascii=False),company["count"],json.dumps(funds_id_list, ensure_ascii=False),json.dumps(funds_name_list, ensure_ascii=False))
	Save("companies.csv",csv)

def main():
	global gExit
	signal.signal(signal.SIGINT, signal_handler)
	csv = ""

	json_db_str = GetFunderJsonDB()
	if json_db_str is not None:
		Save("funder.txt",json_db_str)
		# Load JSON
		data = json.loads(json_db_str)["x"]
		funds = GetFundInfoFromJson(data)
		ExportFundInfoToCSV(funds)

		companies = ImportCompanies(funds)
		ExportCompaniesToCSV(companies)

if __name__ == "__main__":
	main()

'''
#jsonStr = Load("funder.txt").decode('utf-8')
	#with open('funder.txt') as data_file:
	#	jsonData = json.loads(data_file.read(), encoding='utf-8')
	#	#data = json.loads(jsonData)
	#return

	
	#print(html)
	#return
	#Save("funder.html", html)
	
	
		
			
			#Save("funder.txt",jsonStr)
			#dataEncoded = json.JSONEncoder(ensure_ascii=False).encode(data)
			#SaveJSON("funder.json", data)
			length = len(data["x"])
			for idx, item in enumerate(data["x"]):
				if gExit is True:
					return
				
				csv += "{0}\n".format(json.dumps(item["fundName"], ensure_ascii=False))
				
				#print("Requesting {0}/{1} for FUND ID {2}".format(str(idx),str(length),item["fundNum"]))
				#filePath = "{0}.html".format(os.path.join("funds","html",str(item["fundNum"])))
				#if not os.path.exists(filePath):
				#	fundHtml = GetRequest("https://www.funder.co.il/fund/{0}".format(item["fundNum"]), 1)
				#	Save(filePath, fundHtml)
	Save("funds.csv",csv)


	for fund in funds[:5]:
			json_fund_str  = GetFundInfoFromDB(fund["id"])
			json_fund_info = json.loads(json_fund_str)

			#companies = None
			#holdings = {}
			#for holding in json_fund_info:
			#	holding_list = holding["holdingItemsList"]
			#Save(os.path.join("output","{0}.json".format(fund["id"])), json_fund_str)

			# companies = GetCompanies(json_fund_info)
			
			print(companies)
			ExportCompaniesToCSV(companies)
'''
