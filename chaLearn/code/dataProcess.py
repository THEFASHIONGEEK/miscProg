import numpy as np
from skvideo.io import VideoCapture
import cv2
import skimage
import random
from pydub import AudioSegment
import subprocess
import arff
import os, sys
import cPickle as pickle

def equalizeImgList(imgList, row = 100, col = 100):
	'''
	Given a frameList, normalize (resize) all the frames to a common size
	'''
	# OPTIMIZATION POSSIBLE

	newFrameList = []

	for i in range(imgList.shape[0]):
		try:
			newImg = cv2.resize(imgList[i], (row, col))
		except:
			print 'Resizing error found for image with dimensions', imgList[i].shape
			continue

		newImg = np.array(newImg, dtype = np.uint8)
		newFrameList.append(newImg)

	newFrameList = np.array(newFrameList)
	return newFrameList

def getTruthVal(fileName):
	'''
	Take the fileName (CSV File) of the truth file
	Returns a dictionary which contains mapping between fileName and 5 attitude scores
	'''

	trueMap = {}
	trueVal = np.genfromtxt(fileName, delimiter=',', dtype=None)
	# Assuming we get a csv file

	for i in range(1,trueVal.shape[0]):
		# The first one is not a valid entry
		tmpList = list(trueVal[i][1:])
		tmpList = [float(x) for x in tmpList]
		tmpKey = trueVal[i][0].strip('.mp4')
		trueMap[tmpKey] = np.array(tmpList)

	return trueMap

def readFromFileAudioFetA(fileName):
	filePath = 'tmpData/audioFetA/'
	fileName = filePath+fileName+'.p'
	if (not os.path.isfile(fileName)):
		return []
	fetList = pickle.load(open(fileName, 'rb'))
	tmpList = []
	for i in range(len(fetList)):
		audioFet = np.array(fetList[i]['data'][0][1:-1])
		# The first and last values are unnecessary
		tmpList.append(audioFet)
	# tmpList = np.array(tmpList)
	# print tmpList.shape
	return tmpList

def readFromFileFetA(fileName, skipLength = 2, augment = False):
	filePath = 'tmpData/visualFetA/'
	fileName = filePath+fileName+'.npy'
	if (not os.path.isfile(fileName)):
		return []
	newImgList = np.load(fileName)
	tmpList = []
	row, col = 50, 50
	startInd = random.randint(0, skipLength-1)
	for i in range(startInd, newImgList.shape[0], skipLength):
		newImg = cv2.resize(newImgList[i], (row, col))
		if augment:
			if (random.randint(1,2) > 1):
				newImg = np.fliplr(newImg)
		tmpList.append(newImg)
	tmpList = np.array(tmpList)
	return tmpList

def readFromFileFetB(fileName, skipLength = 2):
	filePath = 'tmpData/visualFetB/'
	fileName = filePath+fileName+'.npy'
	if (not os.path.isfile(fileName)):
		return []
	fetList = np.load(fileName)
	tmpList = []
	startInd = random.randint(0, skipLength-1)
	for i in range(startInd, fetList.shape[0], skipLength):
		tmpList.append(fetList[i])
	tmpList = np.array(tmpList)
	tmpList.astype(np.float32)
	return tmpList

def readFromFileFetC(fileName, skipLength = 2, augment = False):
	filePath = 'tmpData/visualFetC/'
	fileName = filePath+fileName+'.npy'
	if (not os.path.isfile(fileName)):
		return []
	newImgList = np.load(fileName)
	tmpList = []
	row, col = 50, 50
	startInd = random.randint(0, skipLength-1)
	for i in range(startInd, newImgList.shape[0], skipLength):
		ind1 = random.randint(0, 8)
		ind2 = random.randint(0, 8)
		l = 100 - (ind1 + ind2)
		newImg = newImgList[i][ind1:ind1 + l, ind2:ind2 + l]
		newImg = cv2.resize(newImg, (row, col))
		if augment:
			if (random.randint(1,2) > 1):
				newImg = np.fliplr(newImg)
		tmpList.append(newImg)
	tmpList = np.array(tmpList)
	return tmpList

def readData(fileNames, trueVal = None, feature = 'A'):
	X = []
	Y = []
	# CAN BE OPTIMIZED
	for i in xrange(len(fileNames)):
		fileName = fileNames[i]
		if (feature == 'A'):
			imgList = readFromFileFetA(fileName, 6, augment = False)
		elif (feature == 'B'):
			imgList = readFromFileFetB(fileName, 2)			
		elif (feature == 'C'):
			imgList = readFromFileFetC(fileName, 5, augment = True)
		elif (feature == 'AudioA'):
			imgList = readFromFileAudioFetA(fileName)
		if (len(imgList) == 0):
			continue
		X.extend(imgList)
		if (trueVal is not None):
			Y.extend([trueVal[fileName]]*len(imgList))
			print '\r', (i*(1.0))/len(fileNames), 'part reading completed',
			sys.stdout.flush()
	X = np.array(X, dtype = np.float16)
	Y = np.array(Y, dtype = np.float16)
	print X.shape, Y.shape
	return X, Y

def getAudioFeatureAList(fileName, segLen = 4, overlap = 3):
	'''
	Get IS10 features from an audio file (In WAV format)
	Assumes already present in the opensmile directory
	Returns a list of dictionaries containing the features for the segments
	'''
	fetList = []
	song = AudioSegment.from_wav(fileName)
	segLen = segLen*1000
	overlap = overlap*1000
	# Things done in ms
	totLen = len(song)
	for i in range(0, totLen - segLen, segLen - overlap):
		tmpSong = song[i:i+segLen]
		tmpSong.export("tmpAudioFeatureA.wav", format="wav")
		p = subprocess.Popen('./SMILExtract -l 1 -C config/IS10_paraling.conf -I tmpAudioFeatureA.wav -O tmpFeature.arff', shell=True, stdout=subprocess.PIPE)
		p.wait()
		data = arff.load(open('tmpFeature.arff', 'rb'))
		fetList.append(data)
		# Removing the file for the next one
		p = subprocess.Popen('rm tmpFeature.arff', shell=True, stdout=subprocess.PIPE)
		p.wait()

	return fetList

def randomCrops(frame, numCrops = 8, row = 224, col = 224):
	X = []
	rows = frame.shape[0]
	cols = frame.shape[1]

	if (rows*cols == 0):
		return np.array([])

	if ((rows < row) or (cols < col)):
		return np.array([])

	meanVal = np.array([103.939, 116.779, 123.68])   # BGR
	for i in range(numCrops):
		x = random.randint(0, rows - row)
		y = random.randint(0, cols - col)
		img = frame[x:(x+row), y:(y+col), :].astype(np.float32)
		img = img[::-1]  # switch to BGR, since VGG requires BGR images
		img -= meanVal
		X.append(img)

	X = np.array(X)
	return X

def GetBGFeatures(frameList, model, numCrops = 8):
	fetList = []
	row, col = 224, 224

	# print len(frameList)
	for i in xrange(len(frameList)):
		frame = frameList[i]
		X = randomCrops(frame, numCrops, row = row, col = col)
		X = X.reshape(X.shape[0], 3, row, col)

		embed = model.predict(X)
		# Don't do max pool right now. Store all the embeddings to perform augmentation later.
		# finX = np.max(embed, axis = 0)
		fetList.append(embed)

	fetList = np.array(fetList)
	# print fetList.shape
	return fetList

def evaluateTraits(p, gt):
	if (len(p) == len(gt)):
		for i in range(len(p)):
			if (len(p[i]) != 5) or (len(gt[i]) != 5):
				print "Inputs must be a list of 5 values within the range [0,1]. Traits could not be evaluated."
				return
			for j in range(len(p[i])):
				if p[i][j] < 0 or p[i][j] > 1 or gt[i][j] < 0 or gt[i][j] > 1:
					print "Inputs must be values in the range [0,1]. Traits could not be evaluated."
					return
	
	errors = np.abs(p-gt)
	meanAccs = 1-np.mean(errors, axis=0)
	
	print "\nAverage accuracy of "+str(np.mean(meanAccs))+": "
	
	# These scores are reported.
	print "Accuracy predicting Extraversion: "+str(meanAccs[0])
	print "Accuracy predicting Agreeableness: "+str(meanAccs[1])
	print "Accuracy predicting Conscientiousness: "+str(meanAccs[2])
	print "Accuracy predicting Neuroticism: "+str(meanAccs[3])
	print "Accuracy predicting Openness to Experience: "+str(meanAccs[4])
	print "\n"
		
	return meanAccs
