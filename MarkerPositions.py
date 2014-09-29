"""
This script will query a single marker, the Marker 'E', for it's position.

Keys and their corresponding marker positions:
1 - Top left
2 - Top right
3 - Bottom left
4 - Bottom right
5 - Print in WEnvironment.py1 format
6 - Refresh (Delete) recorded positions
"""

import viz
import vizshape
from mocapInterface import mocapInterface

viz.setMultiSample(8)
viz.fov(60)
viz.go()

import vizact
from mocapInterface import mocapInterface

phaseSpaceIP = '192.168.1.230'
owlParamMarkerCount = 25

# Dir where textures and rb files are located
phaseSpaceFilePath = 'MocapResources/'

# Rb files in phaseSpaceFilePath
rigidFileNames_ridx = []
	
# Shapes defined in rigidbody._createVizNode()
# Look there to see what shapes are accepted, or add more shapes
rigidBodyShapes_ridx = ['sphere']
	
# Sizes must correspond to parameters for the vizshape in rigidBodyShapes_ridx 
rigidBodySizes_ridx = [[.1]]
	
# Is the rigid body visible on startup?
rigidBodyToggleVisibility_ridx = [1]

#Phasespace mode. This is the profile number the server uses to load resources for our project
phaseSpaceMode = 1

# Start up the motion capture server
mocap = mocapInterface(phaseSpaceIP,phaseSpaceFilePath,owlParamMarkerCount,
rigidFileNames_ridx,rigidBodyShapes_ridx,rigidBodySizes_ridx,
rigidBodyToggleVisibility_ridx, 1)

strsEnv = []
strs3D = []

strsEnv.append([])
strsEnv.append([])
strsEnv.append([])
strsEnv.append([])
strs3D.append([])
strs3D.append([])
strs3D.append([])
strs3D.append([])

def refreshList():
	global strs3D
	global strsEnv
	strsEnv = []
	strs3D = []
	
	print "cleared : ", len(strsEnv), len(strs3D)

def markerPos(key):
	marker = mocap.getMarkerPosition(0,4)
	if key == 1:
		print "Top Left"
		strsEnv[0] = "self.defaultTopLeft = [" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "]"
		strs3D.append("upperLeft=(" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "),")
	elif key == 2:
		print "Top Right"
		strsEnv[1] = "self.defaultTopRight = [" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "]"
		strs3D.append("upperRight=(" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "),")
	elif key == 3:
		print "Bottom Left"
		strsEnv[2] = "self.defaultBottomLeft = [" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "]"
		strs3D.append("lowerLeft=(" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "),")
	elif key == 4:
		print "Bottom Right"
		strsEnv[3] = "self.defaultBottomRight = [" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "]"
		strs3D.append("lowerRight=(" + str(-marker[2]/1000) + ", 0.0, " + str(-marker[0]/1000) + "),")
	elif key == 5:
		print "For WEnv"
		print strsEnv[0]
		print strsEnv[1]
		print strsEnv[2]
		print strsEnv[3]
		
		print "\nFor 3D"
		print strs3D[0]
		print strs3D[1]
		print strs3D[2]
		print strs3D[3]
	
vizact.onkeydown('1', markerPos, 1)
vizact.onkeydown('2', markerPos, 2)
vizact.onkeydown('3', markerPos, 3)
vizact.onkeydown('4', markerPos, 4)
vizact.onkeydown('5', markerPos, 5)
vizact.onkeydown('6', refreshList)



