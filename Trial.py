import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import os


class Trial():
    def __init__(self, sessionIn, filename, tnum, label_in):
        self.session = sessionIn
        self.filename = filename
        self.trialNum = tnum
        self.label = label_in
        try:
            self.data = pd.read_csv(filename,header=1,dtype=float,skiprows=[2])
        except FileNotFoundError:
            #Some naming conventions for files are different and trial number is in wrong place
            #Save file name to create a case statement to handle different naming conventions
            print('FileNotFoundError in Trial')
            print(filename)
        self.data = self.data.drop('bodyparts',axis='columns')

        #Didn't have to do this, could have just used [] for indexing, didn't know this at
        #the time so renamed everything instead
        self.data = self.data.rename(columns = {
            'leftmcp1':'leftmcp1x','leftmcp1.1':'leftmcp1y','leftmcp1.2':'leftmcp1p',
            'leftmcp2':'leftmcp2x','leftmcp2.1':'leftmcp2y','leftmcp2.2':'leftmcp2p',
            'leftmcp3':'leftmcp3x','leftmcp3.1':'leftmcp3y','leftmcp3.2':'leftmcp3p',
            'leftmcp4':'leftmcp4x','leftmcp4.1':'leftmcp4y','leftmcp4.2':'leftmcp4p',
                                                
            'leftpip1':'leftpip1x','leftpip1.1':'leftpip1y','leftpip1.2':'leftpip1p',
            'leftpip2':'leftpip2x','leftpip2.1':'leftpip2y','leftpip2.2':'leftpip2p',
            'leftpip3':'leftpip3x','leftpip3.1':'leftpip3y','leftpip3.2':'leftpip3p',
            'leftpip4':'leftpip4x','leftpip4.1':'leftpip4y','leftpip4.2':'leftpip4p',
                                                
            'leftdigit1':'leftdigit1x','leftdigit1.1':'leftdigit1y','leftdigit1.2':'leftdigit1p',
            'leftdigit2':'leftdigit2x','leftdigit2.1':'leftdigit2y','leftdigit2.2':'leftdigit2p',
            'leftdigit3':'leftdigit3x','leftdigit3.1':'leftdigit3y','leftdigit3.2':'leftdigit3p',
            'leftdigit4':'leftdigit4x','leftdigit4.1':'leftdigit4y','leftdigit4.2':'leftdigit4p',
                                                
            'leftpawdorsum':'leftpawdorsumx','leftpawdorsum.1':'leftpawdorsumy','leftpawdorsum.2':'leftpawdorsump',
            'nose':'nosex','nose.1':'nosey','nose.2':'nosep',
            'pellet':'pelletx','pellet.1':'pellety','pellet.2':'pelletp',
            
            'rightmcp1':'rightmcp1x','rightmcp1.1':'rightmcp1y','rightmcp1.2':'rightmcp1p',
            'rightmcp2':'rightmcp2x','rightmcp2.1':'rightmcp2y','rightmcp2.2':'rightmcp2p',
            'rightmcp3':'rightmcp3x','rightmcp3.1':'rightmcp3y','rightmcp3.2':'rightmcp3p',
            'rightmcp4':'rightmcp4x','rightmcp4.1':'rightmcp4y','rightmcp4.2':'rightmcp4p',
                                                
            'rightpip1':'rightpip1x','rightpip1.1':'rightpip1y','rightpip1.2':'rightpip1p',
            'rightpip2':'rightpip2x','rightpip2.1':'rightpip2y','rightpip2.2':'rightpip2p',
            'rightpip3':'rightpip3x','rightpip3.1':'rightpip3y','rightpip3.2':'rightpip3p',
            'rightpip4':'rightpip4x','rightpip4.1':'rightpip4y','rightpip4.2':'rightpip4p',
                                                
            'rightdigit1':'rightdigit1x','rightdigit1.1':'rightdigit1y','rightdigit1.2':'rightdigit1p',
            'rightdigit2':'rightdigit2x','rightdigit2.1':'rightdigit2y','rightdigit2.2':'rightdigit2p',
            'rightdigit3':'rightdigit3x','rightdigit3.1':'rightdigit3y','rightdigit3.2':'rightdigit3p',
            'rightdigit4':'rightdigit4x','rightdigit4.1':'rightdigit4y','rightdigit4.2':'rightdigit4p',
            
            
            'rightpawdorsum':'rightpawdorsumx','rightpawdorsum.1':'rightpawdorsumy','rightpawdorsum.2':'rightpawdorsump',
            'rightpaw':'rightpawdorsumx','rightpaw.1':'rightpawdorsumy','rightpaw.2':'rightpawdorsump'
            })
        self.modifiedData = self.data.copy() # Will be used to save data after origin shift
        # Both standardScale and smoothProb() change modifiedData alone
        self.pelletOrigin()
        self.smoothProb()
        self.standardScale()

    def standardScale(self):
        #First transforms dataset to consider initial pellet location as origin
        #Then, scales dataset to have variance = 1 and mean = 0
        
        #Consider doing this iteratively
        #Apply this to trial with multiple labels
        scaler = StandardScaler()
        #self.pelletOrigin()
        cols = self.modifiedData.columns
        self.modifiedData[cols] = scaler.fit_transform(self.modifiedData[cols])
        return
    
    def pelletOrigin(self):
        #Calls "getPelletLoc" to find average initial pellet location
        #Scales all coordinates in trial by initial pellet location
        #Also updates the "pawpref" attribute for the rat if not yet determined
        [pelletX, pelletY] = self.getPelletLoc()
        
        try:
            #Shift X
            #If left pawed
            self.modifiedData.leftmcp1x = self.data.leftmcp1x - pelletX
            self.modifiedData.leftmcp2x = self.data.leftmcp2x - pelletX
            self.modifiedData.leftmcp3x = self.data.leftmcp3x - pelletX
            self.modifiedData.leftmcp4x = self.data.leftmcp4x - pelletX

            self.modifiedData.leftpip1x = self.data.leftpip1x - pelletX
            self.modifiedData.leftpip2x = self.data.leftpip2x - pelletX
            self.modifiedData.leftpip3x = self.data.leftpip3x - pelletX
            self.modifiedData.leftpip4x = self.data.leftpip4x - pelletX

            self.modifiedData.leftdigit1x = self.data.leftdigit1x - pelletX
            self.modifiedData.leftdigit2x = self.data.leftdigit2x - pelletX
            self.modifiedData.leftdigit3x = self.data.leftdigit3x - pelletX
            self.modifiedData.leftdigit4x = self.data.leftdigit4x - pelletX

            #Always
            self.modifiedData.leftpawdorsumx = self.data.leftpawdorsumx - pelletX
            self.modifiedData.nosex = self.data.nosex - pelletX
            self.modifiedData.pelletx = self.data.pelletx - pelletX
            self.modifiedData.rightpawdorsumx = self.data.rightpawdorsumx - pelletX

            #Shift Y
            #If left pawed
            self.modifiedData.leftmcp1y = self.data.leftmcp1y - pelletY
            self.modifiedData.leftmcp2y = self.data.leftmcp2y - pelletY
            self.modifiedData.leftmcp3y = self.data.leftmcp3y - pelletY
            self.modifiedData.leftmcp4y = self.data.leftmcp4y - pelletY

            self.modifiedData.leftpip1y = self.data.leftpip1y - pelletY
            self.modifiedData.leftpip2y = self.data.leftpip2y - pelletY
            self.modifiedData.leftpip3y = self.data.leftpip3y - pelletY
            self.modifiedData.leftpip4y = self.data.leftpip4y - pelletY

            self.modifiedData.leftdigit1y = self.data.leftdigit1y - pelletY
            self.modifiedData.leftdigit2y = self.data.leftdigit2y - pelletY
            self.modifiedData.leftdigit3y = self.data.leftdigit3y - pelletY
            self.modifiedData.leftdigit4y = self.data.leftdigit4y - pelletY
            
            #Update paw preference
            self.session.rat.pawpref = 'l'
    
            #always
            self.modifiedData.leftpawdorsumy = self.data.leftpawdorsumy - pelletY
            self.modifiedData.nosey = self.data.nosey - pelletY
            self.modifiedData.pellety = self.data.pellety - pelletY
            self.modifiedData.rightpawdorsumy = self.data.rightpawdorsumy - pelletY
            
        except AttributeError:
            #Shift X
            #If right pawed
            self.modifiedData.rightmcp1x = self.data.rightmcp1x - pelletX
            self.modifiedData.rightmcp2x = self.data.rightmcp2x - pelletX
            self.modifiedData.rightmcp3x = self.data.rightmcp3x - pelletX
            self.modifiedData.rightmcp4x = self.data.rightmcp4x - pelletX

            self.modifiedData.rightpip1x = self.data.rightpip1x - pelletX
            self.modifiedData.rightpip2x = self.data.rightpip2x - pelletX
            self.modifiedData.rightpip3x = self.data.rightpip3x - pelletX
            self.modifiedData.rightpip4x = self.data.rightpip4x - pelletX

            self.modifiedData.rightdigit1x = self.data.rightdigit1x - pelletX
            self.modifiedData.rightdigit2x = self.data.rightdigit2x - pelletX
            self.modifiedData.rightdigit3x = self.data.rightdigit3x - pelletX
            self.modifiedData.rightdigit4x = self.data.rightdigit4x - pelletX

            #Shift Y
            #Always
            self.modifiedData.leftpawdorsumx = self.data.leftpawdorsumx - pelletX
            self.modifiedData.nosex = self.data.nosex - pelletX
            self.modifiedData.pelletx = self.data.pelletx - pelletX
            self.modifiedData.rightpawdorsumx = self.data.rightpawdorsumx - pelletX
            
            #If right pawed
            self.modifiedData.rightmcp1y = self.data.rightmcp1y - pelletY
            self.modifiedData.rightmcp2y = self.data.rightmcp2y - pelletY
            self.modifiedData.rightmcp3y = self.data.rightmcp3y - pelletY
            self.modifiedData.rightmcp4y = self.data.rightmcp4y - pelletY

            self.modifiedData.rightpip1y = self.data.rightpip1y - pelletY
            self.modifiedData.rightpip2y = self.data.rightpip2y - pelletY
            self.modifiedData.rightpip3y = self.data.rightpip3y - pelletY
            self.modifiedData.rightpip4y = self.data.rightpip4y - pelletY

            self.modifiedData.rightdigit1y = self.data.rightdigit1y - pelletY
            self.modifiedData.rightdigit2y = self.data.rightdigit2y - pelletY
            self.modifiedData.rightdigit3y = self.data.rightdigit3y - pelletY
            self.modifiedData.rightdigit4y = self.data.rightdigit4y - pelletY
            
            #Update paw preference
            self.session.rat.pawpref = 'r'
            
            #Always
            self.modifiedData.leftpawdorsumy = self.data.leftpawdorsumy - pelletY
            self.modifiedData.nosey = self.data.nosey - pelletY
            self.modifiedData.pellety = self.data.pellety - pelletY
            self.modifiedData.rightpawdorsumy = self.data.rightpawdorsumy - pelletY
        
        return
    
    def getPelletLoc(self):
    # Averages first 10 coordinates of pellet with likelihood of 1 to get initial location
    # Also ensures that the pellet location is not changing (e.g. if pedestal is still rising)
        
        isChanging = True
        pelletLoc = 0
        firstTenX = []
        runningSumX = 0
        firstTenY = []
        runningSumY = 0
        testtrial = int(self.trialNum)
        l = len(self.data.pelletp)
        for i in range(l):
            x = self.data.pelletx[i+1]
            y = self.data.pellety[i+1]
            p = self.data.pelletp[i+1]
            x2 = self.data.pelletx[i+2]
            y2 = self.data.pellety[i+2]
            if ((x2 - x)<5) or ((y2-y)<5):
                #Make sure the pellet is not still moving at the beginning of the trial
                isChanging = False
            if not isChanging:
                if len(firstTenX) > 9:
                    break
                if not (p == 'likelihood'):
                    if (float(i)  > .99):
                        if not (x == 'x'):
                            firstTenX.append(x)
                            runningSumX = runningSumX + float(x)
                        if not (y == 'y'):
                            firstTenY.append(y)
                            runningSumY = runningSumY + float(y)
        pelletLoc = [runningSumX/10, runningSumY/10]
        return pelletLoc
    
    def shuffleFrames(self):
    #Currently unused
    # Returns df with all rows in random order
    # It doesn't actually do this, it shuffles data w.r.t. axis, which is columns
    # So this function is useless, but it would be good to have something that ACTUALLY shuffles rows
        return self.modifiedData.sample(frac = 1,axis = 1)
    
    def smoothProb(self):
    # Looks through trial data for low probability values, reassigns all low prob points
    # With a point extrapolated between the most recent high p point and the next closest high p
        columnNames = self.modifiedData.columns
        missed = []
        numMissed = 0
        first = False
        for i in columnNames:
            if i.endswith('p'):
                bodypart = i[:-1]
                x = bodypart + 'x'
                y = bodypart + 'y'
                for j in self.modifiedData.index:
                    if self.modifiedData[i].values[j] < .98:
                            missed.append(j)
                            #Check to see if low likelihood point was first point
                            if (numMissed == 0) and (j == 0):
                                first = True
                                leftmost = j
                            elif numMissed == 0:
                                leftmost = j - 1
                            numMissed = len(missed)
                    #If probability is greater than 0.98
                    else:
                        #Save newest high likelihood point index
                        rightmost = j
                        #If last datapoint was lowlikelihood, extrapolate and fill in
                        if numMissed > 0:
                            #If low likelihood point included, draw straight line between left/right
                            if first:
                                leftmost = rightmost
                                first = False
                            missed, numMissed = self.extrapolate(missed,numMissed,x,y,leftmost,rightmost)
                        #Save most recent high likelihood point
                        leftmost = j
                #If probability on last datapoint was less than 0.98
                if numMissed > 0:
                    if self.modifiedData[i].values[j] > .98:
                        rightmost = j
                    else:
                        rightmost = leftmost
                    missed, numMissed = self.extrapolate(missed,numMissed,x,y,leftmost,rightmost)
        self.dropProb()
        return
    
    def extrapolate(self,missed,numMissed,x,y,leftmost,rightmost):
        #Draws a line between most recent high likelihood points,
        #overwrites low likelihood points with data from line
        l = int(numMissed/2)
        r = numMissed
        linex = np.linspace(self.modifiedData[x].values[leftmost],
                            self.modifiedData[x].values[rightmost],numMissed)
        liney = np.linspace(self.modifiedData[y].values[leftmost],
                            self.modifiedData[y].values[rightmost],numMissed)
        for k in range(r):
            current = int(missed[k])
            self.modifiedData[x].values[current] = linex[k]
            self.modifiedData[y].values[current] = liney[k]
        missed = []
        numMissed = 0
        return missed,numMissed

    def dropProb(self):
        #Now that probability has been incorporated, drop probability values
        if self.session.rat.pawpref == 'l':
            self.modifiedData = self.modifiedData.drop(['leftmcp1p','leftmcp2p','leftmcp3p','leftmcp4p',
                                'leftpip1p','leftpip2p','leftpip3p','leftpip4p',
                                'leftdigit1p','leftdigit2p','leftdigit3p','leftdigit4p',
                                'leftpawdorsump','nosep','pelletp','rightpawdorsump'],
                                axis='columns')
            
        elif self.session.rat.pawpref == 'r':
            self.modifiedData = self.modifiedData.drop(['rightmcp1p','rightmcp2p','rightmcp3p','rightmcp4p',
                                'rightpip1p','rightpip2p','rightpip3p','rightpip4p',
                                'rightdigit1p','rightdigit2p','rightdigit3p','rightdigit4p',
                                'leftpawdorsump','nosep','pelletp','rightpawdorsump'],
                                axis='columns')
        return
    
    def plotTrajectories(self,bodyPart,showProb):
    #Not used in pipeline, but helpful to confirm changes to data actually make sense
    #Makes 3D plot of a particular bodypart, colorbar scales with likelihood if showProb is true
        x = bodyPart + 'x'
        y = bodyPart + 'y'
        pName = bodyPart + 'p'
        if showProb:
            p = self.data[pName].values
            fig = go.Figure(data=[go.Scatter3d(x=self.modifiedData.index.values, y=self.modifiedData[y].values,
                    z=self.modifiedData[x].values,mode='markers',
                    marker=dict(size=3,
                    color=p,                # set color to an array/list of desired values
                    colorscale = 'RdBu',    # choose a colorscale
                    opacity=0.8,showscale = True))],
                    layout=go.Layout(
                    title=go.layout.Title(text=bodyPart)
                ))
            fig.show()
        else:
            fig = go.Figure(data=[go.Scatter3d(x=self.modifiedData.index.values, y=self.modifiedData[y].values,
                    z=self.modifiedData[x].values,mode='markers',
                    marker=dict(size=3))],
                    layout=go.Layout(
                    title=go.layout.Title(text=bodyPart)
                ))
            fig.show()
        return
