import viz
import threading
import vizact
import sys

class MATRIX:
	
	def __init__(self, name):
		
		self.WEAPON_OF_MASS_DESTRUCTION = threading.Lock()
		self.name = name
		self.flag = False
		self.yo = False
		self.first = None
		
	def tester1(self, name):
		
		self.yo = self.WEAPON_OF_MASS_DESTRUCTION.acquire()
		if None is self.first:
			print "\nNEO: HAHA, THERE IS NO SPOON. I Got here first.\n"
		else:
			print "\nNEO: Awww, :( I'm sooo late. Sorry People of ZION\n"
		
	def tester2(self,name):
		
		print "*****Looking around*****"
		viz.waitTime(3)
		if None is self.first:
			self.first = "smith"
		print "\nAgent SMITH: I WILL KILL YOU ALLLLLL!!!\n"
		viz.waitTime(2)
		if(False == self.yo):
			self.flag = True
			viz.waitTime(2)
			viz.quit()
		else:
			viz.waitTime(2)
			print "Agent SMITH: Wait waaa!!"
			viz.waitTime(2)
			print "*****NEO beats up Agent SMITH and destroys him*****"
			viz.waitTime(2)
			print "Agent SMITH: Damn you NEOOOOO!!\nAgent SMITH: NOW Fall Agent SMITH"
			
		
	def die(self):
		if(True is self.flag):
			viz.waitTime(2)
			print "People of ZION: WE ARE DYIIIIIIIIIIING. :( "
			viz.waitTime(2)
			print "People of ZION: WE ALL FALL DOWN. :( :("
	
		
	def intro(self):
		print "\nAgent SMITH:      Agent SMITH is here!!"
		

viz.go()
object1 = MATRIX("1")
vizact.ontimer2(3,0,object1.tester2, "Agent SMITH thread")
vizact.ontimer2(2,0,object1.tester1, "NEO thread")
vizact.ontimer2(1,0,object1.intro)
viz.callback(viz.EXIT_EVENT, object1.die)