"""
The Foot module is the representation of an independent foot.
It constructs foot data for consumption.

Author:
Rahul N Gopinathan (@rnn4511)
"""

from collections import deque
import numpy as np
import threading
import copy
import viz

"""
The following data structure is for the foot buffer. 
It holds the frameTime, position and orientation of the foot at the time of capture.
FrameTime starts from 0 and is the time in seconds of the rendered frame since the beginning of the simulation.
"""
class SingleBufferEntry():
	
	def __init__(self, frameTime = -1, pos_XYZ = None, ori_XYZW = None):
		self.frameTime = frameTime
		self.footPos_XYZ = pos_XYZ
		self.footOri_XYZ = ori_XYZW

"""
The following data structure holds the required data for the user when polling for foot data.
"""
class InstantaneousFootProperties():
	
	def __init__(self, speed_MS = -1, velocity_MS_XYZ = np.array([-1,-1,-1]), 
					direction_Vector = np.array([-1,-1,-1]), startPos_foot = -1, 
					endPos_foot = -1, startTime_frame = -1, endTime_frame = -1):
		self.speed_MS = speed_MS
		self.velocity_MS_XYZ = velocity_MS_XYZ
		self.direction_Vector = direction_Vector
		
		#The startPos_foot corresponds to the average position of the first set of the buffer elements.
		#The endPos_foot corresponds to the average position of the second set of the buffer elements.
		#Used while filtering. See filterData method for usage.
		self.startPos_foot = startPos_foot
		self.endPos_foot = endPos_foot
		
		#Similar to startPos_foot and endPos_foot, start & end times are used while filtering data.
		#startTime_frame is the most recent frame in the first set of buffer elements. Assigned to the averaged positions.
		#endTime_frame is the most recent frame in the second set of buffer elements.
		self.startTime_frame = startTime_frame
		self.endTime_frame = endTime_frame

"""
The foot class.
"""
class Foot():

	"""
	Each foot instance is an independent foot. Hence when it is instantiated, it requires a 
	mocap interface to the foot rigid body (returnPointerToRigid object).
	
	The default buffer size is 10 and is private to each foot.
	"""
	def __init__(self, maxBufferLen = 10, mocapFootObj = None, name = ""):
		
		if(not mocapFootObj):
			print >> sys.stderr, "Initialize a foot using mocap first. No changes made."
			return
			
		self.footBuffer = deque(maxlen = maxBufferLen)
		self.mocapFoot = mocapFootObj		
		self.lock = threading.Lock()
		self.name = name

	"""
	This method will be usually called in a timer loop.
	When called, the foot will lock it's buffer first and insert the frame data.
	This includes the orientation and position data of the foot and the frameTime, 
	which is the number of seconds into the simulation.
	"""
	def populateNextBufferElement(self):
		footProperties = SingleBufferEntry(
							frameTime = viz.getFrameTime(),
							pos_XYZ = self.mocapFoot.vizNode.getPosition(),
							ori_XYZW = self.mocapFoot.vizNode.getQuat()
						)
						
		# write here to file for unfiltered data
		# Lock the buffer before writing to it, so other threads cannot read from it at the same time.
		self.lock.acquire()
		self.footBuffer.append(footProperties)
		self.lock.release()
		
	
	"""
	Returns an InstantaneousFoot object after average data calculation.
	**MODIFY THIS METHOD TO INCLUDE FILTERING**
	"""
	def getFiltered_InstantaneousFootInfo(self):
		
		#Split buffer into two parts
		set1Elements = self.footBuffer.maxlen / 2
		set2Elements = self.footBuffer.maxlen - set1Elements
		
		#Lock buffer and make a copy of it's contents.
		self.lock.acquire()
		bufferCopy = copy.deepcopy(self.footBuffer)
		self.lock.release()
		
		if len(bufferCopy) < (set1Elements + set2Elements):
			return None
		
		vectorSet1 = np.array([0,0,0])
		vectorSet2 = np.array([0,0,0])
		
		time1 = -1
		time2 = -1
		
		#Average positions of both buffer parts
		np.average
		for index in range(set1Elements):
			vectorSet1 = vectorSet1 + np.array(bufferCopy[index].footPos_XYZ)
			
		for index in range(set1Elements, bufferCopy.maxlen):
			vectorSet2 = vectorSet2 + np.array(bufferCopy[index].footPos_XYZ)
		
		#Average out the position information to get an average position for each buffer set.
		#It works because, each buffer set always contains consecutive frames.
		#Because of threading, there is no corruption of frame order in the buffer.
		vectorSet1 /= set1Elements
		vectorSet2 /= set2Elements
		
		#Assign the last frame's time as the time for each buffer set
		time1 = bufferCopy[set1Elements - 1].frameTime
		time2 = bufferCopy[self.footBuffer.maxlen - 1].frameTime
		
		#Distance and direction calculation
		distance_Calculated = np.linalg.norm(vectorSet1 - vectorSet2)
		direction_Calculated = vectorSet2 - vectorSet1
		
		#Speed calculation
		speed_MS = -1
		try:
			speed_MS = distance_Calculated / (time2 - time1)
		except ZeroDivisionError:
			print >> sys.stderr, "Warning: DivideByZero. Not calculating speed_MS."
			speed_MS = 0
		
		#velocity calculation
		velocityCalculated = (direction_Calculated / distance_Calculated) * speed_MS
		
		return InstantaneousFootProperties(
					speed_MS = speed_MS, 
					velocity_MS_XYZ = velocityCalculated, 
					direction_Vector = direction_Calculated, 
					startPos_foot = vectorSet1, 
					endPos_foot = vectorSet2, 
					startTime_frame = time1, 
					endTime_frame = time2
				)
		
if __name__ == '__main__':
	f = Foot()