"""
This script is to setup the ground plane and cave settings.
When it's completely functional, it will have the ability to display a ground plane, 
Allow functions to change basic configurations such as color, size, mode etc,
and also setup the cave frustrum and boundaries.

At this moment we define only one wall of the cave. Additional logic is required to 
define an entire CAVE (front, back, left, right, top and bottom walls). But this is 
as simple as just defining the additional wall boundries and adding them to the cave viwe.

Author:
Rahul N Gopinathan(@rnn4511)
"""
import viz
import vizcave
import viztracker
import Connector
import vizact
import vizshape
from Foot import Foot

"""
TODO: try threading for population of the buffer!!
"""

class Environment():
	
	"""
	Initializes the Environment. Requires .cave file that contains the four corners of the powerwall.
	Also accepts the debug flag for future use.
	"""
	def __init__(self, caveWallFileName = None, debug = True):
						
		#Default bottom wall boundaries as marked out on the lab floor. 
		self.defaultTopLeftXYZ = [-2.26977050781, 0.0, 1.05118676758]
		self.defaultTopRightXYZ = [0.988239257812, 0.0, 0.967888549805]
		self.defaultBottomLeftXYZ = [-2.25686572266, 0.0, -0.73389465332]
		self.defaultBottomRightXYZ = [0.874583740234, 0.0, -0.748521972656]
		
		#The powerwall, see vizard docs for info on powerwall
		self.powerwall = None
		self.cave = None
		self.caveView = None
		
		#Mocap objects#
		self.mocap = None
		self.head_tracker = None

		#Virtual Objects#
		self.crate = None
		self.shutterGlass = None
		
		#Foot Class objects#
		self.leftFoot = None
		self.rightFoot = None
		
		#Visual nodes for the foot#
		self.leftFootViz = None
		self.rightFootViz = None

		#Debug flag. In the future, you can distinguish between debug mode or otherwise using this flag.#
		self.debug = debug
		self.researchMode = True
		
		#Temporary collision flags for each leg#
		self.flag_leftFootCollision = False
		self.flag_rightFootCollision = False
		
		#File object and record flag#
		self.file = None
		self.recording = None
		
		#List to hold corner points when updating dynamically during a running simulation#
		self.genericCornerCoordinates = []	
		self.groundCornerCoordinates = []
		
		#Initial empty placeholders to write the corner marker pos to.#
		self.genericCornerCoordinates.append([])
		self.genericCornerCoordinates.append([])
		self.genericCornerCoordinates.append([])
		self.genericCornerCoordinates.append([])
		self.groundCornerCoordinates.append([])
		self.groundCornerCoordinates.append([])
		self.groundCornerCoordinates.append([])
		self.groundCornerCoordinates.append([])
		
		#Filename to read in persisted corner values from#
		self.caveWallFileName = caveWallFileName
		
		### Define the cave powerwall boundries in the world###
		if(None == caveWallFileName):
			self.powerwall = vizcave.Wall(  upperLeft=self.defaultTopLeftXYZ,
								upperRight=self.defaultTopRightXYZ,
								lowerLeft=self.defaultBottomLeftXYZ,
								lowerRight=self.defaultBottomRightXYZ,
								name='Bottom' )
		
		# :) #
		self.__setupVizParams__()
		self.__setupWorld__()
		self.__setupTracking__()
		self.__setupPhysics__()
		self.__setupKeyListeners__()		
		
		
		
	"""
	Setup vizard initial parameters
	"""
	def __setupVizParams__(self):
		
		#Just playing here#
		#viz.setMultiSample(8)
		#viz.fov(120)
		
		#Check monitor refresh rate and set stereo mode accordingly#
		monitor_RefreshRate = viz.getOption('viz.monitor.refresh_rate', type=int)
		#if(119 <= monitor_RefreshRate):
			#Turn on the physics engine
		viz.phys.enable() 
		viz.window.setFullscreenMonitor(2)
		viz.setMultiSample(8)
		viz.go(viz.FULLSCREEN | viz.QUAD_BUFFER)
		print "here"
#		else:
#			print '*****************NOT RENDERING IN 3D**********************'
#			viz.setMultiSample(8)
#			viz.window.setFullscreenMonitor(2)
#			viz.go(viz.FULLSCREEN)
			
			
			
	"""
	Setup world, objects and other visuals here
	"""
	def __setupWorld__(self):
		
		#Initialize cave and load the powerwall#
		self.cave = vizcave.Cave()		
		#This line of code opens the file if a filename is provided and loads the corner co-ordinates from it, else uses the default co-ordinates#
		self.cave.load(self.caveWallFileName) if None is not self.caveWallFileName else self.cave.addWall(self.powerwall)
		
		# TODO: Pair every obstacle with an invisible "hat" object to detect when the obstacle was avoided.
		# Create a seperate module that does this automatically for each object added.
		# Like from a config file.
		self.crate = viz.addChild( 'crate.osgb' )
		self.crate.setScale([.2,.2,.2])
		self.crate.setPosition([-.45, 0, -.10])
		
		self.cratePole = vizshape.addCylinder(height = .5, radius = 0.025)
		self.cratePole.setPosition( [-.45, .3, -.10] )
		self.cratePole.alpha(0.5)

		self.avatar = viz.addAvatar('duck.cfg')
		self.avatar.setScale(.2, .2, .2)
		self.avatar.setPosition([-1, .1, -.10])		
		
		#self.floor = viz.addChild('lab.osgb')
		self.floor = viz.addChild('piazza.osgb')
		#vizshape.addGrid()
		
		
		
	"""
	Setup tracking here
	"""
	def __setupTracking__(self):
		
		#get mocap interface
		self.mocap = Connector.getMocapInterface()

		#Get the shutter-glass rigid body
		self.shutterGlass = self.mocap.returnPointerToRigid(Connector.SHUTTERGLASSES)
		self.head_tracker = viz.link(self.shutterGlass.vizNode,viz.NullLinkable,srcFlag=viz.ABS_PARENT)
		self.cave.setTracker(self.head_tracker)

		# Create cave view
		cave_origin = vizcave.CaveView(self.head_tracker)
		
		#In case you want to override & translate the physical location of cave, uncommnet this
		
		'''
		origin_tracker = viztracker.KeyboardMouse6DOF()
		origin_link = viz.link(origin_tracker, cave_origin)
		origin_link.setMask(viz.LINK_POS)
		'''
		
		#Foot rigidBodies
		leftFootRigid = self.mocap.returnPointerToRigid(Connector.L_FOOT)
		rightFootRigid = self.mocap.returnPointerToRigid(Connector.R_FOOT)
		
		#Foot visuals, make them 100% transparent when not in debug mode
		self.leftFootViz = vizshape.addBox(size=(.2,.2,.2))
		self.rightFootViz = vizshape.addBox(size=(.2,.2,.2))
		
		if(self.debug):
			self.leftFootViz.alpha(0.025)
			self.rightFootViz.alpha(0.025)
		else:
			self.leftFootViz.alpha(0.0075)
			self.rightFootViz.alpha(0.0075)
		
		#Foot class objects
		self.leftFoot = Foot(mocapFootObj = leftFootRigid, name="Left")
		self.rightFoot = Foot(mocapFootObj = rightFootRigid, name="Right")
		
		#setup buffer updates
		vizact.onupdate(0, self.leftFoot.populateNextBufferElement)
		vizact.onupdate(0, self.rightFoot.populateNextBufferElement)
		vizact.onupdate(0, self.updateBooties)
		viz.callback(viz.COLLIDE_BEGIN_EVENT, self.collideDetected)
		
		
		
	"""
	Physics of the world here.
	
	***NEED TO ADD: FOOT tracking during obstacle avoidance logic***
	"""
	def __setupPhysics__(self):

		#Create ground plane and disable physics on it
		self.floorPhy = self.floor.collidePlane()
		self.floor.disable(viz.DYNAMICS)
		viz.gravity(0)
		
		#Duck
		self.avatar.collideMesh()
		self.avatar.enable(viz.COLLIDE_NOTIFY)
		self.avatar.disable(viz.DYNAMICS)
		
		#Crate
		self.cratePhysics = self.crate.collideBox(bounce = 0.05, density = 1)
		self.crate.enable(viz.COLLIDE_NOTIFY)
		self.crate.disable(viz.DYNAMICS)
		
		#CratePole
		self.cratePolePhy = self.cratePole.collideMesh()
		self.cratePole.enable(viz.COLLIDE_NOTIFY)
		self.cratePole.disable(viz.DYNAMICS)
		
		#Feet Physics
		self.leftFootPhysics = self.leftFootViz.collideBox(density = 2)
		self.leftFootViz.disable(viz.DYNAMICS)
		self.rightFootPhysics = self.rightFootViz.collideBox(density = 2)
		self.leftFootViz.disable(viz.DYNAMICS)
		
		
		
	"""
	Method to declare all key listeners
	"""
	def __setupKeyListeners__(self):
		
		""" 
		Look for tracker calibration key press. 
		Allows us to calibrate projections without needing the participant to move.
		"""
		vizact.onkeydown('x', self.trackerCalibrations, 'x')
		vizact.onkeydown('y', self.trackerCalibrations, 'y')
		vizact.onkeydown('z', self.trackerCalibrations, 'z')
		
		""" Rigid body resets and saves """
		vizact.onkeydown('s', self.mocap.resetRigid, 'ShutterGlass')
		vizact.onkeydown('S', self.mocap.saveRigid, 'ShutterGlass')	
		vizact.onkeydown('l', self.mocap.resetRigid, 'LeftFoot')
		vizact.onkeydown('L', self.mocap.saveRigid, 'LeftFoot')	
		vizact.onkeydown('r', self.mocap.resetRigid, 'RightFoot')
		vizact.onkeydown('R', self.mocap.saveRigid, 'RightFoot')	
		
		"""
		File IOs
		Press 'O' to open the file.
		Press 'C' to close the file after writing.
		Press 'M' to start or stop recording info. from current trial.
		"""
		vizact.onkeydown('o', self.openTextFile)
		vizact.onkeydown('c', self.closeTextFile)
		vizact.onkeydown('m', self.startStopWritingToFile)
		
		""" Swap eyes in case glasses sync incorrectly 
		This is where the magic happens when we see overlapped projection 
		of objects above a certain height. 
		
		Reset the glasses first and then use 'e' or SHIFT+'e' to correct projections.
		No more tweaking them manually :) .
		"""
		vizact.onkeydown('e', viz.MainWindow.setStereoSwap, False)
		vizact.onkeydown('E', viz.MainWindow.setStereoSwap, True)
		
		"""Enable/Disable physics"""
		vizact.onkeydown('1', self.enableGameMode)
		vizact.onkeydown('2', self.enableResearchMode)

		"""
		Reset Tracker Positions.
		4 - TopLeft
		5 - TopRight
		6 - BottomRight
		7 - BottomLeft
		
		8 - Save as non-ground-plane points
		9 - Save as ground-plane points
		"""
		vizact.onkeydown('4', self.markerPos, 4)
		vizact.onkeydown('5', self.markerPos, 5)
		vizact.onkeydown('6', self.markerPos, 6)
		vizact.onkeydown('7', self.markerPos, 7)
		vizact.onkeydown('8', self.markerPos, 8)
		vizact.onkeydown('9', self.markerPos, 9)
		
		""" Temps: Resets crate pos. in game mode """
		vizact.onkeydown('v', self.crate.setPosition, [0,5,0])
		
		
	
	"""
	Method to callback when a collision is detected in the world
	"""
	def collideDetected(self, event):
		
		if (event.obj2 is self.leftFootViz and event.obj1 is not self.avatar): 
			self.flag_leftFootCollision = True
		elif event.obj2 is self.rightFootViz and event.obj1 is not self.avatar:
			self.flag_rightFootCollision = True

		rightFootData = self.rightFoot.getFiltered_InstantaneousFootInfo()
		if event.obj1 is self.avatar:
			if rightFootData is not None and rightFootData.speed_MS <= .5:
				viz.playSound('quack.wav')
				self.avatar.execute(1)
			elif rightFootData is not None and rightFootData.speed_MS > .5:
				viz.playSound('pigeon_fly.wav')
				self.avatar.execute(2)
			return
				
		if event.obj1 is self.crate and (event.obj2 is self.leftFootViz or event.obj2 is self.rightFootViz):
			viz.playSound('crash.wav')
			self.crate.color(1,0,0)
			
		elif event.obj1 is self.cratePole and (event.obj2 is self.leftFootViz or event.obj2 is self.rightFootViz):
			print "Evade registered at: ", event.pos
			self.printLeftFootProperties() if event.obj2 is self.leftFootViz else self.printRightFootProperties()
			viz.playSound('BUZZER.wav')
			
			
			
	def openTextFile(self):
		
		if not self.file:
			self.file = open('dataRecordings.txt', 'w')
			print "file open"
		else:
			print >> sys.stderr, "Seems like the file object is already open."
			
			
			
	def closeTextFile(self):
		
		if not self.file:
			print >> sys.stderr, "Seems like the file object is not open."
		else:
			self.file.flush()
			self.file.close()
			self.file = None
			print "File close"
			
			
			
			
	def startStopWritingToFile(self):
		
		#If not already recording, setup a record event on every frame
		if not self.recording:
			self.flag_rightFootCollision = False
			self.flag_leftFootCollision = False
			self.recording = vizact.onupdate(0, self.writeToFile)
			print "Record start"
			
		#Else disable record event and set the record flag to none	
		else:
			self.recording.remove()
			self.recording = None


	#Writes raw data to file		
	def writeToFile(self):
		
		if not self.file:
			print >> sys.stderr, "No file open to write to"
		else:			
			leftBuffer = self.leftFoot.getFiltered_InstantaneousFootInfo()
			rightBuffer = self.rightFoot.getFiltered_InstantaneousFootInfo()
			leftMocapPos = self.leftFoot.mocapFoot.vizNode.getPosition()
			rightMocapPos = self.rightFoot.mocapFoot.vizNode.getPosition()
			
			#Fastest way to concatenate strings.
			#You dont want to spend time creating and concatenating strings
			oneLineOfData = []
			oneLineOfData.append('lFPos ') 
			oneLineOfData.append(str(leftMocapPos[0]))
			oneLineOfData.append(' ')
			oneLineOfData.append(str(leftMocapPos[1]))
			oneLineOfData.append(' ')
			oneLineOfData.append(str(leftMocapPos[2]))
			oneLineOfData.append(' rFPos ')
			oneLineOfData.append(str(rightMocapPos[0]))
			oneLineOfData.append(' ')
			oneLineOfData.append(str(rightMocapPos[1]))
			oneLineOfData.append(' ')
			oneLineOfData.append(str(rightMocapPos[2]))
			oneLineOfData.append(' leftSpeed ')
			oneLineOfData.append(str(leftBuffer.speed_MS))
			oneLineOfData.append(' rightSpeed ')
			oneLineOfData.append(str(rightBuffer.speed_MS))
			oneLineOfData.append(' leftCollision ')
			oneLineOfData.append(str(self.flag_leftFootCollision))
			oneLineOfData.append(' rightCollision ')
			oneLineOfData.append(str(self.flag_rightFootCollision)) 
			oneLineOfData.append(' frameTimeW ')
			oneLineOfData.append(str(viz.getFrameTime()))
			
			#If there was a collision in this frame, construct the string and set the collision flags to false again
			if self.flag_leftFootCollision or self.flag_rightFootCollision :
				self.flag_leftFootCollision = False
				self.flag_rightFootCollision = False
			
			#Join all the strings, this is where the string is created, so no time spent in concatenating :)
			finalString = ''.join(oneLineOfData)
			self.file.write(finalString)
			self.file.write('\n')
			
			
	
	""" Left foot RawData & Filtered Data """
	def printLeftFootProperties(self):
		leftBuffer = self.leftFoot.getFiltered_InstantaneousFootInfo()
		leftMocapPos = self.leftFoot.mocapFoot.vizNode.getPosition()
		leftMocapORI = self.leftFoot.mocapFoot.vizNode.getQuat()
		
		print "Foot: LEFT"
		print "***********FOOT BUFFER***********"
		print "Direction :", leftBuffer.direction_Vector
		print "StartPos  :", leftBuffer.startPos_foot
		print "EndPos    :", leftBuffer.endPos_foot
		print "Velocity  :", leftBuffer.velocity_MS_XYZ
		print "Speed     :", leftBuffer.speed_MS
		print "*********************************\n"
		
		print "**********FOOT MOCAP*************"
		print "Position     :", leftMocapPos
		print "Orientation  :", leftMocapORI
		print "Height       :", leftMocapPos[1]
		if leftMocapPos[1] >= self.crate.getScale()[1]:
			print "Foot State   : Foot UP"
		else:
			print "Foot State   : Foot DOWN"
		
		
		
	""" Right Foot RawData & Filtered Data """	
	def printRightFootProperties(self):
		rightBuffer = self.rightFoot.getFiltered_InstantaneousFootInfo()
		rightMocapPos = self.rightFoot.mocapFoot.vizNode.getPosition()
		rightMocapORI = self.rightFoot.mocapFoot.vizNode.getQuat()
		
		print "Foot: Right"
		print "***********FOOT BUFFER***********"
		print "Direction :", rightBuffer.direction_Vector
		print "StartPos  :", rightBuffer.startPos_foot
		print "EndPos    :", rightBuffer.endPos_foot
		print "Velocity  :", rightBuffer.velocity_MS_XYZ
		print "Speed     :", rightBuffer.speed_MS
		print "*********************************\n"
		
		print "**********FOOT MOCAP*************"
		print "Position     :", rightMocapPos
		print "Orientation  :", rightMocapORI
		print "Height       :", rightMocapPos[1]
		if rightMocapPos[1] >= self.crate.getScale()[1]:
			print "Foot State   : Foot UP"
		else:
			print "Foot State   : Foot DOWN"
			
		
			
	"""
	Control booties position update
	"""
	def updateBooties(self):
		
		leftPosXYZ = self.leftFoot.mocapFoot.vizNode.getPosition()
		rightPosXYZ = self.rightFoot.mocapFoot.vizNode.getPosition()
		
		#Height will always be close to 0 in game mode.
		if self.researchMode:
			leftPosXYZ[1] = .1
			rightPosXYZ[1] = .1
		else:
			leftPosXYZ[1] = .1
			rightPosXYZ[1] = .1
		
		self.leftFootViz.setPosition(leftPosXYZ)
		self.leftFootViz.setQuat(self.leftFoot.mocapFoot.vizNode.getQuat())
		self.rightFootViz.setPosition(rightPosXYZ)	
		self.rightFootViz.setQuat(self.rightFoot.mocapFoot.vizNode.getQuat())


	
	"""
	This method will allow us to tune position of participant while a simulation is running,
	without have the participant physcially move to adjust projection perfectly.
	"""
	def trackerCalibrations(self, key):
		
		#translate x and -x (x and CTRL + x)
		if('x' == str(key)):
			if(1 == viz.key.isDown(viz.KEY_CONTROL_L, immediate = True)):
				self.head_tracker.preTrans([-0.001,0,0])
			else:
				self.head_tracker.preTrans([0.001,0,0])

		#translate y and -y (y and CTRL + y)				
		if('y' == str(key)):
			if(1 == viz.key.isDown(viz.KEY_CONTROL_L, immediate = True)):
				self.head_tracker.preTrans([0,-0.001,0])
			else:
				self.head_tracker.preTrans([0,0.001,0])
		
		#translate z and -z (z and CTRL + z)
		if('z' == str(key)):
			if(1 == viz.key.isDown(viz.KEY_CONTROL_L, immediate = True)):
				self.head_tracker.preTrans([0,0,-0.001])
			else:
				self.head_tracker.preTrans([0,0,0.001])
		
		print "Setting head_tracker position" + str(self.head_tracker.getPosition())
		
		
		
	def enableGameMode(self):
		print "Lets go kick them boxes"
		viz.gravity(0)
		self.crate.enable(viz.DYNAMICS)
		self.leftFootViz.enable(viz.DYNAMICS)
		self.rightFootViz.enable(viz.DYNAMICS)
		
		
		
	def enableResearchMode(self):
		print "Research!!"
		self.crate.disable(viz.DYNAMICS)
		self.leftFootViz.disable(viz.DYNAMICS)
		self.rightFootViz.disable(viz.DYNAMICS)
		
		

	def markerPos(self, key):
		
		#Turns out this is marker 'E' on string 1 with the driver profile 'VCAVE (mode 4)'
		#This is the Corner Marker on the Glasses
		marker = self.mocap.getMarkerPosition(0,0)
		if key == 4:
			print "Recorded New Top Left"
			self.genericCornerCoordinates[0] = [-marker[2]/1000, marker[1]/1000, -marker[0]/1000]
			self.groundCornerCoordinates[0] = [-marker[2]/1000, 0, -marker[0]/1000]
		elif key == 5:
			print "Recorded New Top Right"
			self.genericCornerCoordinates[1] = [-marker[2]/1000, marker[1]/1000, -marker[0]/1000]
			self.groundCornerCoordinates[1] = [-marker[2]/1000, 0, -marker[0]/1000]
		elif key == 7:
			print "Recorded New Bottom Left"
			self.genericCornerCoordinates[2] = [-marker[2]/1000, marker[1]/1000, -marker[0]/1000]
			self.groundCornerCoordinates[2] = [-marker[2]/1000, 0, -marker[0]/1000]
		elif key == 6:
			print "Recorded New Bottom Right"
			self.genericCornerCoordinates[3] = [-marker[2]/1000, marker[1]/1000, -marker[0]/1000]
			self.groundCornerCoordinates[3] = [-marker[2]/1000, 0, -marker[0]/1000]
		elif key == 8:
			print "Resetting NON-GroundPlane Dimensions"
			
			self.defaultTopLeftXYZ = self.genericCornerCoordinates[0]
			self.defaultTopRightXYZ = self.genericCornerCoordinates[1]
			self.defaultBottomLeftXYZ = self.genericCornerCoordinates[2]
			self.defaultBottomRightXYZ = self.genericCornerCoordinates[3]
			
			self.cave.removeWall(self.powerwall)
			self.cave.clear()
			
			self.powerwall = vizcave.Wall(  upperLeft=self.defaultTopLeftXYZ,
									upperRight=self.defaultTopRightXYZ,
									lowerLeft=self.defaultBottomLeftXYZ,
									lowerRight=self.defaultBottomRightXYZ,
									name='Bottom' )
									
			print "Persisting new dimension values"
			self.cave.addWall(self.powerwall)
			self.cave.update()
			self.cave.save('caveWallDimensions.cave')
		elif key == 9:
			print "Resetting GroundPlane Dimensions"
			
			self.defaultTopLeftXYZ = self.groundCornerCoordinates[0]
			self.defaultTopRightXYZ = self.groundCornerCoordinates[1]
			self.defaultBottomLeftXYZ = self.groundCornerCoordinates[2]
			self.defaultBottomRightXYZ = self.groundCornerCoordinates[3]
			
			self.cave.removeWall(self.powerwall)
			self.cave.clear()
			
			self.powerwall = vizcave.Wall(  upperLeft=self.defaultTopLeftXYZ,
									upperRight=self.defaultTopRightXYZ,
									lowerLeft=self.defaultBottomLeftXYZ,
									lowerRight=self.defaultBottomRightXYZ,
									name='Bottom' )
									
			print "Persisting new dimension values"
			self.cave.addWall(self.powerwall)
			self.cave.update()
			self.cave.save('caveWallDimensions.cave')
			
		
if __name__ == "__main__":	
	env = Environment(caveWallFileName = 'caveWallDimensions.cave', debug = True)
	#env = Environment(debug = True)