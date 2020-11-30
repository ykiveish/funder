#!/usr/bin/python
import os
import urllib2
import json
import signal
import argparse
import time
import datetime
from datetime import date

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

def signal_handler(signal, frame):
	global gExit
	gExit = True

def BasicDataCalulation(data):
	sum = 0
	stock_value = 0
	min = data[0]
	max = data[0]
	prev_item = data[0]
	diff_minus = 0
	diff_plus = 0
	for item in data:
		sum += item
		if min > item:
			min = item
		if max < item:
			max = item
		
		diff = item - prev_item
		if diff < 0:
			diff_minus += 1
		else:
			diff_plus += 1
		
		stock_value += diff
		prev_item = item
	
	average = float(sum) / float(len(data))
	amp = max - min
	
	return average, max, min, amp, stock_value + data[0], stock_value, diff_plus, diff_minus

def Analize(file):
	csv_str = Load(file)
	csv = csv_str.split("\n")
	stock_price = []
	for row_str in csv:
		row = row_str.split(",")
		if len(row) > 2:
			stock_price.append(float(row[3]))
	
	return BasicDataCalulation(stock_price)

def SaveToFile(file, data):
	today = datetime.datetime.today()
	dateNow = today.strftime("%a %b %d %Y %H:%M:%S")
	dataToSave = "{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(str(dateNow),
																data[0],
																data[1],
																data[2],
																data[3],
																data[4],
																data[5],
																data[6],
																data[7])
	filePath = os.path.join("analize","{0}.csv".format(file))
	if os.path.exists(filePath) is False:
		Append(filePath, "{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format("time",
																"average",
																"max",
																"min",
																"amplitude",
																"stock value",
																"stock_change",
																"diff plus",
																"diff minus"))
	Append(filePath, dataToSave)

def Compare(file, data):
	filePath = os.path.join("analize","{0}.csv".format(file))
	if os.path.exists(filePath) is True:
		csv_str = Load(filePath)
		csv = csv_str.split("\n")
		row_str = csv[len(csv)-2]
		row = row_str.split(",")
		data = "{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(0,
															data[0],
															data[1],
															data[2],
															data[3],
															data[4],
															data[5],
															data[6],
															data[7]).split(",")
		for idx, item in enumerate(row[1:]):
			if item != data[idx+1]:
				return False
	else:
		return False
	
	return True

def main():
	signal.signal(signal.SIGINT, signal_handler)
	
	parser = argparse.ArgumentParser(description='Development')
	parser.add_argument('-v', '--version', action='store_true',
		help='Version of analizer tool')
	parser.add_argument('-f', '--file', action='store',
		dest='file', help='File to parse')
	
	analize_all = False
	args = parser.parse_args()	
	if args.file is not None:
		stock_file = os.path.join("monitor", str(args.file))
	else:
		analize_all = True
	
	try:
		if analize_all is True:
			path = "monitor"
			onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
			for file in onlyfiles:
				stock_file = os.path.join("monitor", file)
				data = Analize(stock_file)
				same = Compare(file.replace(".csv",""), data)
				print(same)
				if same is False:
					SaveToFile(file.replace(".csv",""), data)
		else:
			data = Analize(stock_file)
			same = Compare(str(args.file).replace(".csv",""), data)
			print(same)
			if same is False:
				SaveToFile(args.file.replace(".csv",""), data)
		
	except Exception as e:
		print(e)

if __name__ == "__main__":
	main()
