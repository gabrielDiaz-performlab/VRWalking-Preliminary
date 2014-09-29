import viz
import vizcave
import viztracker

#Create single power wall
'''
BottomWall = vizcave.Wall(  #upperLeft=(-2.97846777344, 0.0, 0.818440734863),
							#upperRight=(2.22551123047, 0.0, 0.983547119141),
							#lowerRight=(2.51278833008, 0.0, -2.00895361328),
							#lowerLeft=(-2.83207202148, 0.0, -2.30359692383),
							upperLeft=(-2.26977050781, 0.0, 1.05118676758),
							upperRight=(0.988239257812, 0.0, 0.967888549805),
							lowerLeft=(-2.25686572266, 0.0, -0.73389465332),
							lowerRight=(0.874583740234, 0.0, -0.748521972656),
							name='Bottom' )
'''

import vizshape
#Add a world axis with X,Y,Z labels
world_axes = vizshape.addAxes()
X = viz.addText3D('X',pos=[1.1,0,0],color=viz.RED,scale=[0.3,0.3,0.3],parent=world_axes)
Y = viz.addText3D('Y',pos=[0,1.1,0],color=viz.GREEN,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)
Z = viz.addText3D('Z',pos=[0,0,1.1],color=viz.BLUE,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)

#Initialize graphics window
viz.go(viz.FULLSCREEN | viz.QUAD_BUFFER)

viz.window.setFullscreenMonitor(1)

#Create cave object with power wall
cave = vizcave.Cave()
cave.load('caveWallDimensions.cave')
#cave.addWall(BottomWall)

phaseSpaceIP = '192.168.1.230'
owlParamMarkerCount = 25

# Dir where textures and rb files are located
phaseSpaceFilePath = 'MocapResources/'

# Rb files in phaseSpaceFilePath
rigidFileNames_ridx = ['ShutterGlass.rb']
	
# Shapes defined in rigidbody._createVizNode()
# Look there to see what shapes are accepted, or add more shapes
rigidBodyShapes_ridx = ['sphere']
	
# Sizes must correspond to parameters for the vizshape in rigidBodyShapes_ridx 
rigidBodySizes_ridx = [[.05]]
	
# Is the rigid body visible on startup?
rigidBodyToggleVisibility_ridx = [0]

#Phasespace mode. This is the profile number the server uses to load resources for our project
phaseSpaceMode = 4

from mocapInterface import mocapInterface
# Start up the motion capture server
mocap = mocapInterface(phaseSpaceIP,phaseSpaceFilePath,owlParamMarkerCount,
rigidFileNames_ridx,rigidBodyShapes_ridx,rigidBodySizes_ridx,
rigidBodyToggleVisibility_ridx, phaseSpaceMode)

#Get the hat rigid body
sGlass = mocap.returnPointerToRigid('ShutterGlass')


"""
Create tracker object that represents the users head position, specifically the center of the eyes.
The position provided by the head tracker must be in the same reference frame as the cave wall coordinates.
This will normally be a tracking sensor, but for this example we will simulate a head tracker
using the keyboard (WASD keys).
"""
head_tracker = viz.link(sGlass.vizNode,viz.NullLinkable,srcFlag=viz.ABS_PARENT)
#head_tracker.setMask(viz.LINK_POS)

"""
Pass the head tracker to the cave object so it can automatically update the
view frustums every frame based on the current head position relative to each wall.
"""
cave.setTracker(head_tracker)

"""
Create CaveView object for manipulating the virtual viewpoint.
cave_origin is a node that controls the position of the cave within the virtual world.
For example, if you wanted to simulate the cave user flying through an environment,
you would apply the transformation to the cave_origin node.
"""
cave_origin = vizcave.CaveView(head_tracker)

"""
The cave_origin node is a standard Vizard node that you can apply any position/rotation to.
In this example we will create a keyboard/mouse tracker (using arrow keys) and link it to
the cave_origin node, allowing us to  fly the cave user through the virtual environment.
"""

origin_tracker = viztracker.KeyboardMouse6DOF()
origin_link = viz.link(origin_tracker, cave_origin)
origin_link.setMask(viz.LINK_POS)
#Add gallery environment model
blah = viz.add('piazza.osgb')
blah.setScale([.15,.15,.15])
blah.setPosition([0,0,-5])

import vizact
vizact.onkeydown('h', mocap.resetRigid, 'ShutterGlass')
vizact.onkeydown('e', viz.MainWindow.setStereoSwap, False)
vizact.onkeydown('E', viz.MainWindow.setStereoSwap, True)