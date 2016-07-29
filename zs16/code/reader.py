import csv
import cPickle as pickle
import numpy as np
import random, sys

def getInt(val):
	try:
		a = int(val)
	except ValueError:
		return "IGNORE"
	return a

def formatField(val):
	if ('Hospital ' in val):
		val = val.strip('Hospital ')
	elif ('Region ' in val):
		val = val.strip('Region ')
	elif ('District ' in val):
		val = val.strip('District ')
	elif ('Instrument ' in val):
		val = val.strip('Instrument ')
	return getInt(val)

def getDataXY():
	dataList = []
	with open('../resources/Dataset/HospitalRevenue.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = []
			for i in range(17):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)
			if (len(fetList) < 16):
				continue
			fetList = np.array(fetList)
			dataList.append(fetList)
	csvfile.close()
	dataList = np.array(dataList)

	print dataList.shape

	X = dataList[:,0:4]
	Y = dataList[:,-1:]

	print X.shape
	print Y.shape

	return X, Y

if __name__ == "__main__":
	getDataXY()
