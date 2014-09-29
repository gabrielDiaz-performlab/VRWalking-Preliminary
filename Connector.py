"""
This module is responsible for connecting with the mocap interface.
The methods here will be solely responsible for the communication with mocap interface,
constructing a mocap interface object. The environment will use this object to query mocap
information.

Gabriel Diaz
Rahul N Gopinathan
"""

from mocapInterface import mocapInterface
import viz

"""
Defining global constants for rigid bodies etc. that are ment to be referenced in multiple places.
This save time in the future in case we decide to change their values.
"""
SHUTTERGLASSES = 'ShutterGlass.rb'
L_FOOT = 'LeftFoot.rb'
R_FOOT = 'RightFoot.rb'

"""
Constructs the mocap object and returns it to the calling method.
Eventually, the hard coded values will be read from config. files.
"""
def getMocapInterface():
	phaseSpaceIP = '192.168.1.230'
	owlParamMarkerCount = 15

	# Dir where textures and rb files are located
	phaseSpaceFilePath = 'MocapResources/'

	# Rb files in phaseSpaceFilePath
	rigidFileNames_ridx = [SHUTTERGLASSES, L_FOOT, R_FOOT]
		
	# Shapes defined in rigidbody._createVizNode()
	# Look there to see what shapes are accepted, or add more shapes
	rigidBodyShapes_ridx = ['sphere', 'cylinder', 'cylinder']
		
	# Sizes must correspond to parameters for the vizshape in rigidBodyShapes_ridx 
	rigidBodySizes_ridx = [[.05],[.03,.09], [.03,.09]]
		
	# Is the rigid body visible on startup?
	rigidBodyToggleVisibility_ridx = [0,0,0]

	#Phasespace mode. This is the profile number the server uses to load resources for our project
	phaseSpaceMode = 4

	# Start up the motion capture server
	return mocapInterface(phaseSpaceIP,phaseSpaceFilePath,owlParamMarkerCount,
	rigidFileNames_ridx,rigidBodyShapes_ridx,rigidBodySizes_ridx,
	rigidBodyToggleVisibility_ridx, phaseSpaceMode)

	
	
if __name__ == "__main__":
		
	viz.go()
	mocap = getMocapInterface()