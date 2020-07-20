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
        
        ## If left paw dominant, will rename form left to side
        
            'leftmcp1':'sidemcp1x','leftmcp1.1':'sidemcp1y','leftmcp1.2':'sidemcp1p',
            'leftmcp2':'sidemcp2x','leftmcp2.1':'sidemcp2y','leftmcp2.2':'sidemcp2p',
            'leftmcp3':'sidemcp3x','leftmcp3.1':'sidemcp3y','leftmcp3.2':'sidemcp3p',
            'leftmcp4':'sidemcp4x','leftmcp4.1':'sidemcp4y','sidemcp4.2':'sidemcp4p',
                                                
            'leftpip1':'sidepip1x','leftpip1.1':'sidepip1y','leftpip1.2':'sidepip1p',
            'leftpip2':'sidepip2x','leftpip2.1':'sidepip2y','leftpip2.2':'sidepip2p',
            'leftpip3':'sidepip3x','leftpip3.1':'sidepip3y','leftpip3.2':'sidepip3p',
            'leftpip4':'sidepip4x','leftpip4.1':'sidepip4y','leftpip4.2':'sidepip4p',
                                                
            'leftdigit1':'sidedigit1x','leftdigit1.1':'sidedigit1y','leftdigit1.2':'sidedigit1p',
            'leftdigit2':'sidedigit2x','leftdigit2.1':'sidedigit2y','leftdigit2.2':'sidedigit2p',
            'leftdigit3':'sidedigit3x','leftdigit3.1':'sidedigit3y','leftdigit3.2':'sidedigit3p',
            'leftdigit4':'sidedigit4x','leftdigit4.1':'sidedigit4y','leftdigit4.2':'sidedigit4p',
                                                
            
           ##If right paw dominant, will rename from right to side
           
            'rightmcp1':'sidemcp1x','rightmcp1.1':'sidemcp1y','rightmcp1.2':'sidemcp1p',
            'rightmcp2':'sidemcp2x','rightmcp2.1':'sidemcp2y','rightmcp2.2':'sidemcp2p',
            'rightmcp3':'sidemcp3x','rightmcp3.1':'sidemcp3y','rightmcp3.2':'sidemcp3p',
            'rightmcp4':'sidemcp4x','rightmcp4.1':'sidemcp4y','rightmcp4.2':'sidemcp4p',
                                                
            'rightpip1':'sidepip1x','rightpip1.1':'sidepip1y','rightpip1.2':'sidepip1p',
            'rightpip2':'sidepip2x','rightpip2.1':'sidepip2y','rightpip2.2':'sidepip2p',
            'rightpip3':'sidepip3x','rightpip3.1':'sidepip3y','rightpip3.2':'sidepip3p',
            'rightpip4':'sidepip4x','rightpip4.1':'sidepip4y','rightpip4.2':'sidepip4p',
                                                
            'rightdigit1':'sidedigit1x','rightdigit1.1':'sidedigit1y','rightdigit1.2':'sidedigit1p',
            'rightdigit2':'sidedigit2x','rightdigit2.1':'sidedigit2y','rightdigit2.2':'sidedigit2p',
            'rightdigit3':'sidedigit3x','rightdigit3.1':'sidedigit3y','rightdigit3.2':'sidedigit3p',
            'rightdigit4':'sidedigit4x','rightdigit4.1':'sidedigit4y','rightdigit4.2':'sidedigit4p',
            
            ##Same for both paw pref
            
            'nose':'sidenosex','nose.1':'sidenosey','nose.2':'sidenosep',
            'pellet':'sidepelletx','pellet.1':'sidepellety','pellet.2':'sidepelletp',
        
            })
            
        if self.session.rat.pawpref == 'r':
        #If right pawed, name rpd sidepd and lpd contrapd
            self.data = self.data.rename({'rightpawdorsum':'sidepawdorsumx','rightpawdorsum.1':'sidepawdorsumy','rightpawdorsum.2':'sidepawdorsump',
                'rightpaw':'rightpawdorsumx','sidepaw.1':'rightpawdorsumy','rightpaw.2':'sidepawdorsump',
                'leftpawdorsum':'contrapawdorsumx','leftpawdorsum.1':'contrapawdorsumy','leftpawdorsum.2':'contrapawdorsump',
                                         })
        elif self.session.rat.pawpref == 'l':
        #If left pawed, name rpd sidepd and lpd contrapd
            self.data = self.data.rename({
            'rightpawdorsum':'contrapawdorsumx','rightpawdorsum.1':'contrapawdorsumy','rightpawdorsum.2':'contrapawdorsump',
                'rightpaw':'contrapawdorsumx','rightpaw.1':'contrapawdorsumy','rightpaw.2':'contrapawdorsump',
                'leftpawdorsum':'sidepawdorsumx','leftpawdorsum.1':'sidepawdorsumy','leftpawdorsum.2':'sidepawdorsump',
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
            self.modifiedData.sidemcp1x = self.data.sidemcp1x - pelletX
            self.modifiedData.sidemcp2x = self.data.sidemcp2x - pelletX
            self.modifiedData.sidemcp3x = self.data.sidemcp3x - pelletX
            self.modifiedData.sidemcp4x = self.data.sidemcp4x - pelletX

            self.modifiedData.sidepip1x = self.data.sidepip1x - pelletX
            self.modifiedData.sidepip2x = self.data.sidepip2x - pelletX
            self.modifiedData.sidepip3x = self.data.sidepip3x - pelletX
            self.modifiedData.sidepip4x = self.data.sidepip4x - pelletX

            self.modifiedData.sidedigit1x = self.data.sidedigit1x - pelletX
            self.modifiedData.sidedigit2x = self.data.sidedigit2x - pelletX
            self.modifiedData.sidedigit3x = self.data.sidedigit3x - pelletX
            self.modifiedData.sidedigit4x = self.data.sidedigit4x - pelletX

            #Always
            self.modifiedData.sidepawdorsumx = self.data.sidepawdorsumx - pelletX
            self.modifiedData.nosex = self.data.nosex - pelletX
            self.modifiedData.pelletx = self.data.pelletx - pelletX
            self.modifiedData.rightpawdorsumx = self.data.rightpawdorsumx - pelletX

            #Shift Y
            #If left pawed
            self.modifiedData.sidemcp1y = self.data.sidemcp1y - pelletY
            self.modifiedData.sidemcp2y = self.data.sidemcp2y - pelletY
            self.modifiedData.sidemcp3y = self.data.sidemcp3y - pelletY
            self.modifiedData.sidemcp4y = self.data.sidemcp4y - pelletY

            self.modifiedData.sidepip1y = self.data.sidepip1y - pelletY
            self.modifiedData.sidepip2y = self.data.sidepip2y - pelletY
            self.modifiedData.sidepip3y = self.data.sidepip3y - pelletY
            self.modifiedData.sidepip4y = self.data.sidepip4y - pelletY

            self.modifiedData.sidedigit1y = self.data.sidedigit1y - pelletY
            self.modifiedData.sidedigit2y = self.data.sidedigit2y - pelletY
            self.modifiedData.sidedigit3y = self.data.sidedigit3y - pelletY
            self.modifiedData.sidedigit4y = self.data.sidedigit4y - pelletY
    
            #always
            self.modifiedData.sidepawdorsumy = self.data.sidepawdorsumy - pelletY
            self.modifiedData.nosey = self.data.nosey - pelletY
            self.modifiedData.pellety = self.data.pellety - pelletY
            self.modifiedData.contrapawdorsumy = self.data.contrapawdorsumy - pelletY
            
        except AttributeError:
            #This should no longer happen
            print('AttributeError in trial from %s' % self.session.rat.id)
        
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
