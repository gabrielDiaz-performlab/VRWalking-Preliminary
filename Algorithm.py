import numpy as np
from sympy import *
import matplotlib as plt


#takes the whole data set and splits up the data into the seperate trials    
def splitTrials(eventframe,time, bXpos, bYpos, bZpos, hXpos, hYpos, hZpos ):
#bXpos is the ball's x position
#bYpos is the ball's y position
#bZpos is the ball's z position
#hXpos is the hand's x position
#hYpos is the hand's y position
#hZpos is the hand's z position
    
    triallist = []
#finds all the frames in which an start event occurs
#when the event is a 1, the ball shows up
    for i, j in enumerate(eventframe):
        if j == 1:
            triallist.append(i)
    k = 0
    attempttimelist = []
    attemptbXlist = []
    attemptbYlist = []
    attemptbZlist = []
    attempthXlist = []
    attempthYlist = []
    attempthZlist = []
    attemptEventlist = []
    attemptTXYZElist = []
    totalattemptlist = []
    #sorts the data into the different trials
    while k < len(triallist)-1:
        #creates the fist index where the trial begins
        starttrialindex = triallist[k]
        #creates the index where the trial ends
        finnishtrialindex = triallist[k+1]
        #creates a list of times that stays within bounds of the current trial
        attempttimelist.append(time[starttrialindex:finnishtrialindex])
        #creates a list of the ball's X position that stays within bounds of the current trial
        attemptbXlist.append(bXpos[starttrialindex:finnishtrialindex])
        #creates a list of ball's Y position that stays within bounds of the current trial
        attemptbYlist.append(bYpos[starttrialindex:finnishtrialindex])
        #creates a list of ball's Z position that stays within bounds of the current trial
        attemptbZlist.append(bZpos[starttrialindex:finnishtrialindex])
        #creates a list of hand's X position that stays within bounds of the current trial
        attempthXlist.append(hXpos[starttrialindex:finnishtrialindex])
        #creates a list of hand's Y position that stays within bounds of the current trial
        attempthYlist.append(hYpos[starttrialindex:finnishtrialindex])
        #creates a list of hand's Z position that stays within bounds of the current trial
        attempthZlist.append(hZpos[starttrialindex:finnishtrialindex])
        #creates a list of eventframes that stays within bounds of the current trial
        attemptEventlist.append(eventframe[starttrialindex:finnishtrialindex])
        #creates a list of all the lists that were created
        #organizes all the data from one trial into one space
        attemptTXYZElist.append(attempttimelist)
        attemptTXYZElist.append(attemptbXlist)
        attemptTXYZElist.append(attemptbYlist)
        attemptTXYZElist.append(attemptbZlist)
        attemptTXYZElist.append(attempthXlist)
        attemptTXYZElist.append(attempthYlist)
        attemptTXYZElist.append(attempthZlist)
        attemptTXYZElist.append(attemptEventlist)
        #adds all the trials into one list
        totalattemptlist.append(attemptTXYZElist)
        attempttimelist = []
        attemptbXlist = []
        attemptbYlist = []
        attemptbZlist = []
        attempthXlist = []
        attempthYlist = []
        attempthZlist = []
        attemptEventlist = []
        attemptTXYZElist = []
        k+=1
    return totalattemptlist



#given teh XYZ position of the hand, it finds the velocity and shortens the time that is shown on the graph
def findVelocitiesandShorten(trialnum, TrialSplitList):
    #splits up the data from the trial
    trial = TrialSplitList[trialnum]
    trialindex = TrialSplitList.index(trial)
    timelist = trial[0]
    time = timelist[0]
    Xposlist = trial[4]
    Xpos = Xposlist[0]
    Yposlist = trial[5]
    Ypos = Yposlist[0]
    Zposlist = trial[6]
    Zpos = Zposlist[0]
    eventFramelist = trial[7]
    eventFrame = eventFramelist[0]  
    
    #finds when the ball bounces
    bounceFrame_tr = eventFrame.index(3.0)
    bounceTime_tr = time[bounceFrame_tr]
     
     #uses the shortenTime method to reduce the size of the lists
    [Xpos, Ypos, ZPos, times]= shortenTime(bounceTime_tr, time, Xpos, Ypos, Zpos)
    
    def findvel(x0,x1,y0,y1,z0,z1):
        #finds the total distance the ball traveled between the 2 frames
        distance=sqrt(((x1-x0)**2)+((y1-y0)**2)+((z1-z0)**2))
        #divides the total distance by the time between frames
        velocity = distance*60 #/(t1-t0)
        return velocity
    
    i = 0
    velocities = []
    #creates a list of all the velocities in the one trial
    while(i<(len(times)-1)):
        veloc = findvel(Xpos[i],Xpos[i+1],Ypos[i],Ypos[i+1],Zpos[i],Zpos[i+1])
        velocities.append(veloc)
        i+=1
    velocityarray = np.array(velocities)
    times = times.tolist()
    #deletes the last value in the times list so that velocities and times are the same size
    del times[len(times)-1]
    
    #finds the time values in milliseconds after adjusting them to the bounce
    for t in times:
        t_index= times.index(t)
        r = t-bounceTime_tr
        r*=1000
        times[t_index] = r

    del times[0]
    del velocities[0]
    
    #reduce the noise in the graph
    velocities = smoothListGaussian(velocities)
    timesANDvelocities = [times, velocities]
    return timesANDvelocities


#given teh XYZ position of the hand, it finds the velocity and shortens the time that is shown on the graph
def findVelocitiesnoShorten(trialnum, TrialSplitList):
    #splits up the data from the trial
    trial = TrialSplitList[trialnum]
    trialindex = TrialSplitList.index(trial)
    timelist = trial[0]
    time = timelist[0]
    Xposlist = trial[4]
    Xpos = Xposlist[0]
    Yposlist = trial[5]
    Ypos = Yposlist[0]
    Zposlist = trial[6]
    Zpos = Zposlist[0]
    eventFramelist = trial[7]
    eventFrame = eventFramelist[0]  
    
    #finds when the ball bounces
    bounceFrame_tr = eventFrame.index(3.0)
    bounceTime_tr = time[bounceFrame_tr]
    
    #renames the timelist
    times = time
    
    def findvel(x0,x1,y0,y1,z0,z1):
        #finds the total distance the ball traveled between the 2 frames
        distance=sqrt(((x1-x0)**2)+((y1-y0)**2)+((z1-z0)**2))
        #divides the total distance by the time between frames
        velocity = distance*60 #/(t1-t0)
        return velocity
    
    i = 0
    velocities = []
    #creates a list of all the velocities in the one trial
    while(i<(len(times)-1)):
        veloc = findvel(Xpos[i],Xpos[i+1],Ypos[i],Ypos[i+1],Zpos[i],Zpos[i+1])
        velocities.append(veloc)
        i+=1
    velocityarray = np.array(velocities)
    #times = times.tolist()
    #deletes the last value in the times list so that velocities and times are the same size
    del times[len(times)-1]
    
    #finds the time values in milliseconds after adjusting them to the bounce
    for t in times:
        t_index= times.index(t)
        r = t-bounceTime_tr
        r*=1000
        times[t_index] = r

    del times[0]
    del velocities[0]
    
    
    #reduce the noise in the graph
    velocities = smoothListGaussian(velocities)
    timesANDvelocities = [times, velocities]
    return timesANDvelocities
    
#shortens the Time witch is shown in the graph 
def shortenTime(bounceTime_tr,Times,Xs, Ys, Zs):
    #finds endpoints of new time
    startcutval = bounceTime_tr-.8
    endcutval = bounceTime_tr+.4
    cuttimes = [] #= Times
    XsTrue = []
    YsTrue = []
    ZsTrue = []
    
    #makes new arrays of times and positions within the new time range 
    for i in Times:
        if startcutval<i<endcutval:
            iindex = Times.index(i)
            cuttimes.append(i)
            XsTrue.append(Xs[iindex])
            YsTrue.append(Ys[iindex])
            ZsTrue.append(Zs[iindex])
             
    XArray = np.array([XsTrue])
    YArray = np.array([YsTrue])
    ZArray = np.array([ZsTrue])
    cutTimeArray = np.array([cuttimes])
    
    #creates a new array that holds all of the smaller Arrays
    ShorTimeMatrix = np.vstack((XArray,YArray))
    ShorTimeMatrix = np.vstack((ShorTimeMatrix, ZArray))
    ShorTimeMatrix = np.vstack((ShorTimeMatrix, cutTimeArray))
    return ShorTimeMatrix
    

#finds the derivative(acceleration) of two lists (time and velocity)    
def getderiv(xvalues, yvalues):
    t=0
    h=0
    j=0
    diffx=[]
    diffy=[]
    deriv=[]
    #finds the difference in adjacent x (time) values
    while(j<(len(xvalues)-1)):
        diffx.append(xvalues[j+1]-xvalues[j])
        j+=1
    #finds the differnce in adjacent y(velocity) values
    while(h<(len(yvalues)-1)):
        diffy.append(yvalues[h+1]-yvalues[h])
        h+=1
    #divides the differences and creates a list
    while(t<=(len(diffx)-1)):
        deriv.append(diffy[t]/diffx[t])
        t+=1
    return deriv
#reduces noise in the graph- the greater the degree the more noise is reduced
def smoothListGaussian(list,strippedXs=False,degree=5):
    
     list = [list[0]]*(degree-1) + list + [list[-1]]*degree  

     window=degree*2-1  

     weight=np.array([1.0]*window)  

     weightGauss=[]  

     for i in range(window):  

         i=i-degree+1  

         frac=i/float(window)  

         gauss=1/(np.exp((4*(frac))**2))  

         weightGauss.append(gauss)  

     weight=np.array(weightGauss)*weight  

     smoothed=[0.0]*(len(list)-window)  

     for i in range(len(smoothed)):  

         smoothed[i]=(sum(np.array(list[i:i+window])*weight)/sum(weight))  

     return smoothed
     
         

    
        
                    
                        
                
                
            


          
              