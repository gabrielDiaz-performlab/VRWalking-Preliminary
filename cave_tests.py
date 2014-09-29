"""
This script demonstrates how the vizcave module works in Vizard.

Use the WASD keys to move the avatar within the cave.
This simulates the head tracker assigned to vicave.setTracker()

Use the mouse + arrow keys to move the entire cave through the environment.
This simulates how the vizcave.CaveView object affects the final viewpoint.

Press the 1-4 keys to change which cave wall is represented by the right half
of the window.
"""
import viz
import vizact
import vizcam
import vizcave
import vizshape

viz.setMultiSample(8)
viz.go()

'''
import vizinfo
infoWindow = viz.addWindow(pos=(0,1), size=(1,1), clearMask=0, order=10)
infoWindow.visible(False,viz.WORLD)
vizinfo.InfoPanel(window=infoWindow)
'''

# Setup main window
viz.MainWindow.setSize([0.5,1])

# Setup cave window
caveView = viz.addView()

# Setup pivot navigation for main window
cam = vizcam.PivotNavigate(distance=10,center=(0,2,0))
cam.rotateUp(25)

# Create avatar to simulate person standing in cave
#avatar = viz.addAvatar('vcc_male2.cfg')
#avatar.state(1)


import vizact
from mocapInterface import mocapInterface

phaseSpaceIP = '192.168.1.230'
owlParamMarkerCount = 25

# Dir where textures and rb files are located
phaseSpaceFilePath = 'MocapResources/'

# Rb files in phaseSpaceFilePath
rigidFileNames_ridx = ['hat.rb']
	
# Shapes defined in rigidbody._createVizNode()
# Look there to see what shapes are accepted, or add more shapes
rigidBodyShapes_ridx = ['sphere']
	
# Sizes must correspond to parameters for the vizshape in rigidBodyShapes_ridx 
rigidBodySizes_ridx = [[.1]]
	
# Is the rigid body visible on startup?
rigidBodyToggleVisibility_ridx = [1]

#Phasespace mode. This is the profile number the server uses to load resources for our project
phaseSpaceMode = 2


# Start up the motion capture server
mocap = mocapInterface(phaseSpaceIP,phaseSpaceFilePath,owlParamMarkerCount,
rigidFileNames_ridx,rigidBodyShapes_ridx,rigidBodySizes_ridx,
rigidBodyToggleVisibility_ridx)


#Add a world axis with X,Y,Z labels
world_axes = vizshape.addAxes()
X = viz.addText3D('X',pos=[1.1,0,0],color=viz.RED,scale=[0.3,0.3,0.3],parent=world_axes)
Y = viz.addText3D('Y',pos=[0,1.1,0],color=viz.GREEN,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)
Z = viz.addText3D('Z',pos=[0,0,1.1],color=viz.BLUE,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)


#Get the hat rigid body
hatRigid = mocap.returnPointerToRigid('hat')



# Use keyboard to simulate avatar movement
#avatar_tracker = vizcam.addKeyboard6DOF(turnScale=2.0)
##viz.link(avatar_tracker,avatar)
#avatarLink = viz.link(hatRigid.vizNode,avatar)
#avatarLink.setMask(viz.LINK_POS)
#avatarLink.preTrans([0,0,7])

# Head tracker
#head_tracker = viz.link(avatar,viz.NullLinkable,srcFlag=viz.ABS_PARENT)
head_tracker = viz.link(hatRigid.vizNode,viz.NullLinkable,srcFlag=viz.ABS_PARENT)
head_tracker.preTrans([0,1.69,0.12])
#head_tracker.preTrans([0,0,-10])

# Create cave view
cave_origin = vizcave.CaveView(head_tracker,view=caveView)
cave_origin.renderOnlyToWindows([viz.MainWindow])

# Use keyboard mouse to simulate origin tracker
origin_tracker = vizcam.addFlyNavigate()
origin_tracker.setPosition([0,0.1,0])

#viz.link(origin_tracker, cave_origin)
origin_link = viz.link(origin_tracker, cave_origin)
origin_link.setMask(viz.LINK_POS)
#origin_link.preEuler([0,90,0])

# Class for rendering frustum of cave
class CaveFrustum(viz.VizNode):

	def __init__(self,**kw):
		group = viz.addGroup(**kw)
		viz.VizNode.__init__(self,group.id)

		self._quad = vizshape.addQuad([1,1],parent=self)
		self._quad.color(viz.RED)
		self._quad.polyMode(viz.POLY_WIRE)

		viz.startLayer(viz.LINES)
		viz.vertexColor(viz.RED)
		for x in range(8):
			viz.vertex([0,0,0])
		self._lines = viz.endLayer(parent=self)
		self._lines.dynamic()

		self.zoffset(-2)
		self.lineWidth(2)
		self.disable(viz.LIGHTING)

		self._wall = None
		self._tracker = None

		vizact.onupdate(viz.PRIORITY_LAST_UPDATE,self.updateFrustum)

	def setWallAndTracker(self,wall,tracker):
		self._wall = wall
		self._tracker = tracker

		self._quad.setPosition(wall.getCenter())
		self._quad.setQuat(wall.getQuat())
		self._quad.setScale([wall.getWidth(),wall.getHeight(),1.0])
		self._lines.setVertex(1,wall.getUpperLeft())
		self._lines.setVertex(3,wall.getUpperRight())
		self._lines.setVertex(5,wall.getLowerLeft())
		self._lines.setVertex(7,wall.getLowerRight())

	def updateFrustum(self):
		if self._wall is not None:
			head_pos = self._tracker.getPosition()
			for x in range(0,8,2):
				self._lines.setVertex(x,head_pos)

# Define cave walls
WIDTH	= 6.0
HEIGHT	= 3.0
DEPTH	= 6.0

W2 = WIDTH / 2.0
D2 = DEPTH / 2.0

FrontWall = vizcave.Wall(   upperLeft=(-W2,HEIGHT,D2),
                            upperRight=(W2,HEIGHT,D2),
                            lowerLeft=(-W2,0.0,D2),
                            lowerRight=(W2,0.0,D2),
                            name='Front' )

LeftWall = vizcave.Wall(   upperLeft=(-W2,HEIGHT,-D2),
                            upperRight=(-W2,HEIGHT,D2),
                            lowerLeft=(-W2,0.0,-D2),
                            lowerRight=(-W2,0.0,D2),
                            name='Left' )

RightWall = vizcave.Wall(   upperLeft=(W2,HEIGHT,D2),
                            upperRight=(W2,HEIGHT,-D2),
                            lowerLeft=(W2,0.0,D2),
                            lowerRight=(W2,0.0,-D2),
                            name='Right' )

BottomWall = vizcave.Wall(  upperLeft=(-W2,0.0,D2),
                            upperRight=(W2,0.0,D2),
                            lowerLeft=(-W2,0.0,-D2),
                            lowerRight=(W2,0.0,-D2),
                            name='Bottom' )

walls = [FrontWall,LeftWall,RightWall,BottomWall]

wall_frustum = CaveFrustum(parent=cave_origin)

def setActiveWall(wall):
	wall_frustum.setWallAndTracker(wall,cave.getPositionTracker())
	cave.activeWall = wall
	for w in walls:
		w.window.visible(w is wall)

# Setup cave
cave = vizcave.Cave()
for index,wall in enumerate(walls):
	wall.window = viz.addWindow(pos=(0.5,1),size=(0.5,1),view=caveView)
	wall.window.visible(False)
	cave.addWall(wall,window=wall.window)
	vizact.onkeydown(str(index+1),setActiveWall,wall)

cave.setTracker(hatRigid.vizNode)

setActiveWall(FrontWall)

def addCaveWall(cave):
	"""Create visualization of cave walls"""

	walls = cave.getWalls()

	group = viz.addGroup()

	for w in walls:

		mat = viz.Matrix()
		mat.setQuat(w.getQuat())
		mat.setPosition(w.getCenter())

		wall_node = vizshape.addQuad([w.getWidth(),w.getHeight()],transform=mat,parent=group)
		wall_node.color(viz.GRAY)
		wall_node.alpha(0.3)

		wire_node = vizshape.addQuad([w.getWidth(),w.getHeight()],transform=mat,parent=group)
		wire_node.color(viz.BLACK)
		wire_node.polyMode(viz.POLY_WIRE)
		wire_node.zoffset()

	group.disable(viz.LIGHTING)

	return group

# Create walls of cave
cave_walls = addCaveWall(cave)
cave_walls.setParent(cave_origin)

# Attach avatar to cave origin
#avatar.setParent(cave_origin)

# Add environment
viz.add('piazza.osgb')

cube = vizshape.addCube(size=2)
cube.setPosition([0,1,3])
cube.setScale([0.5,0.5,0.5])

cubePosition = cube.getPosition()
bottomLeft = [cubePosition[0] - 1, cubePosition[2] - 1]
bottomRight = [cubePosition[0] + 1, cubePosition[2] - 1]
topLeft = [cubePosition[0] - 1, cubePosition[2] + 1]
topRight = [cubePosition[0] + 1, cubePosition[2] + 1]

def changeCube():
	
	hatPos = hatRigid.vizNode.getPosition()
	
	if(hatPos[0] >= bottomLeft[0] and hatPos[0] <= bottomRight[0]):
		if(hatPos[2] >= bottomLeft[1] and hatPos[2] <= topRight[1]):
			cube.color([0,1,0])
		else:
			cube.color([0,0,1])


import vizact
vizact.ontimer(0.15, changeCube)

	
