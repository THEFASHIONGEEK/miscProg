import numpy as np
from skvideo.io import VideoCapture
import cv2
import skimage

def DetectFace(frame):
	'''
	Given a frame, detect and return the subimage containing the face
	'''
	return []

def DrawFace(frame):
	'''
	Given a frame, draw the box surrounding the detected faces
	Returns None
	'''

	cascPath = 'coreData/haarcascade_frontalface_default.xml'
	faceCascade = cv2.CascadeClassifier(cascPath)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Detect faces in the image
	faces = faceCascade.detectMultiScale(
		gray,
		scaleFactor=1.0,
		minNeighbors=3,
		minSize=(30, 30),
		flags = cv2.cv.CV_HAAR_SCALE_IMAGE
	)

	print "Found {0} faces!".format(len(faces))
	# Draw a rectangle around the faces
	for (x, y, w, h) in faces:
		cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

	cv2.imshow("Faces found", frame)
	cv2.waitKey(0)

	return None

def DetectFaceInList(frameList):
	'''
	Given a frame list, detect (track) the faces
	Returns list of subimages containing tracekd faces
	'''

	cascPath = 'coreData/haarcascade_frontalface_default.xml'
	faceCascade = cv2.CascadeClassifier(cascPath)

	for i in range(0, frameList.shape[0]):
		frame = frameList[i]
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = faceCascade.detectMultiScale(
			gray,
			scaleFactor=1.2,
			minNeighbors=5,
			minSize=(30, 30),
			flags = cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT
			# flags = cv2.cv.CV_HAAR_SCALE_IMAGE
		)
		for (x, y, w, h) in faces:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
		cv2.imshow('Detected Faces', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	return None