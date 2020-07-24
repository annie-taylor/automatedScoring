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
        if self.session.rat.pawpref == 'r':
        #If right pawed, name rpd sidepd and lpd contrapd
            self.data = self.data.rename(columns={
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
                    'rightpawdorsum':'sidepawdorsumx','rightpawdorsum.1':'sidepawdorsumy','rightpawdorsum.2':'sidepawdorsump','rightpaw':'sidepawdorsumx','rightpaw.1':'sidepawdorsumy','rightpaw.2':'sidepawdorsump','leftpawdorsum':'sidecontrapawdorsumx','leftpawdorsum.1':'sidecontrapawdorsumy','leftpawdorsum.2':'sidecontrapawdorsump',
                           ##Same for both paw pref
                                    
                        'nose':'sidenosex','nose.1':'sidenosey','nose.2':'sidenosep',
                        'pellet':'sidepelletx','pellet.1':'sidepellety','pellet.2':'sidepelletp',
                                
                                         })
        elif self.session.rat.pawpref == 'l':
        #If left pawed, name rpd sidepd and lpd contrapd
            self.data = self.data.rename(columns={
            ## If left paw dominant, will rename form left to side
            
                'leftmcp1':'sidemcp1x','leftmcp1.1':'sidemcp1y','leftmcp1.2':'sidemcp1p',
                'leftmcp2':'sidemcp2x','leftmcp2.1':'sidemcp2y','leftmcp2.2':'sidemcp2p',
                'leftmcp3':'sidemcp3x','leftmcp3.1':'sidemcp3y','leftmcp3.2':'sidemcp3p',
                'leftmcp4':'sidemcp4x','leftmcp4.1':'sidemcp4y','leftmcp4.2':'sidemcp4p',
                                                    
                'leftpip1':'sidepip1x','leftpip1.1':'sidepip1y','leftpip1.2':'sidepip1p',
                'leftpip2':'sidepip2x','leftpip2.1':'sidepip2y','leftpip2.2':'sidepip2p',
                'leftpip3':'sidepip3x','leftpip3.1':'sidepip3y','leftpip3.2':'sidepip3p',
                'leftpip4':'sidepip4x','leftpip4.1':'sidepip4y','leftpip4.2':'sidepip4p',
                                                    
                'leftdigit1':'sidedigit1x','leftdigit1.1':'sidedigit1y','leftdigit1.2':'sidedigit1p',
                'leftdigit2':'sidedigit2x','leftdigit2.1':'sidedigit2y','leftdigit2.2':'sidedigit2p',
                'leftdigit3':'sidedigit3x','leftdigit3.1':'sidedigit3y','leftdigit3.2':'sidedigit3p',
                'leftdigit4':'sidedigit4x','leftdigit4.1':'sidedigit4y','leftdigit4.2':'sidedigit4p',
                
                'rightpawdorsum':'sidecontrapawdorsumx','rightpawdorsum.1':'sidecontrapawdorsumy','rightpawdorsum.2':'sidecontrapawdorsump',
                'rightpaw':'sidecontrapawdorsumx','rightpaw.1':'sidecontrapawdorsumy','rightpaw.2':'sidecontrapawdorsump',
                'leftpawdorsum':'sidepawdorsumx','leftpawdorsum.1':'sidepawdorsumy','leftpawdorsum.2':'sidepawdorsump',
           
            ##Same for both paw pref
                'nose':'sidenosex','nose.1':'sidenosey','nose.2':'sidenosep',
                'pellet':'sidepelletx','pellet.1':'sidepellety','pellet.2':'sidepelletp',
                                         })
        if self.session.rat.view == 'both':
            self.addDirectView()
            self.data = self.data.drop('bodyparts',axis='columns')
        elif self.session.rat.view == 'direct':
            self.addDirectView()
            self.data = self.data.drop('bodyparts',axis='columns')
            columnNames = self.data.columns
            drops = []
            #remove all side view data (in future, modify this to not import unused data, save time)
            for i in columnNames:
                if 'side' in i:
                    drops.append(i)
            self.data = self.data.drop(drops,axis='columns')
        #Continues normally if view is 'side'
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
        if self.session.rat.view == 'both':
            [sidepelletX, sidepelletY] = self.getPelletLoc('side')
            [dirpelletX, dirpelletY] = self.getPelletLoc('direct')
        elif self.session.rat.view == 'side':
            [sidepelletX, sidepelletY] = self.getPelletLoc('side')
        elif self.session.rat.view == 'direct':
            [dirpelletX, dirpelletY] = self.getPelletLoc('direct')
        
        if (self.session.rat.view == 'both') or (self.session.rat.view == 'side'):
            #Shift X
            #If left pawed
            self.modifiedData.sidemcp1x = self.data.sidemcp1x - sidepelletX
            self.modifiedData.sidemcp2x = self.data.sidemcp2x - sidepelletX
            self.modifiedData.sidemcp3x = self.data.sidemcp3x - sidepelletX
            self.modifiedData.sidemcp4x = self.data.sidemcp4x - sidepelletX

            self.modifiedData.sidepip1x = self.data.sidepip1x - sidepelletX
            self.modifiedData.sidepip2x = self.data.sidepip2x - sidepelletX
            self.modifiedData.sidepip3x = self.data.sidepip3x - sidepelletX
            self.modifiedData.sidepip4x = self.data.sidepip4x - sidepelletX

            self.modifiedData.sidedigit1x = self.data.sidedigit1x - sidepelletX
            self.modifiedData.sidedigit2x = self.data.sidedigit2x - sidepelletX
            self.modifiedData.sidedigit3x = self.data.sidedigit3x - sidepelletX
            self.modifiedData.sidedigit4x = self.data.sidedigit4x - sidepelletX

            #Always
            self.modifiedData.sidepawdorsumx = self.data.sidepawdorsumx - sidepelletX
            self.modifiedData.sidenosex = self.data.sidenosex - sidepelletX
            self.modifiedData.sidepelletx = self.data.sidepelletx - sidepelletX
            self.modifiedData.sidecontrapawdorsumx = self.data.sidecontrapawdorsumx - sidepelletX

            #Shift Y
            #If left pawed
            self.modifiedData.sidemcp1y = self.data.sidemcp1y - sidepelletY
            self.modifiedData.sidemcp2y = self.data.sidemcp2y - sidepelletY
            self.modifiedData.sidemcp3y = self.data.sidemcp3y - sidepelletY
            self.modifiedData.sidemcp4y = self.data.sidemcp4y - sidepelletY

            self.modifiedData.sidepip1y = self.data.sidepip1y - sidepelletY
            self.modifiedData.sidepip2y = self.data.sidepip2y - sidepelletY
            self.modifiedData.sidepip3y = self.data.sidepip3y - sidepelletY
            self.modifiedData.sidepip4y = self.data.sidepip4y - sidepelletY

            self.modifiedData.sidedigit1y = self.data.sidedigit1y - sidepelletY
            self.modifiedData.sidedigit2y = self.data.sidedigit2y - sidepelletY
            self.modifiedData.sidedigit3y = self.data.sidedigit3y - sidepelletY
            self.modifiedData.sidedigit4y = self.data.sidedigit4y - sidepelletY

            #always
            self.modifiedData.sidepawdorsumy = self.data.sidepawdorsumy - sidepelletY
            self.modifiedData.sidenosey = self.data.sidenosey - sidepelletY
            self.modifiedData.sidepellety = self.data.sidepellety - sidepelletY
            self.modifiedData.sidecontrapawdorsumy = self.data.sidecontrapawdorsumy - sidepelletY
        
       
        if (self.session.rat.view == 'both') or (self.session.rat.view == 'direct'):
            # Same as above but for direct view
            # Need to have a separate pelletOrigin function for direct and side views
            
            #Shift X
            #If left pawed
            self.modifiedData.dirmcp1x = self.data.dirmcp1x - dirpelletX
            self.modifiedData.dirmcp2x = self.data.dirmcp2x - dirpelletX
            self.modifiedData.dirmcp3x = self.data.dirmcp3x - dirpelletX
            self.modifiedData.dirmcp4x = self.data.dirmcp4x - dirpelletX
            
            self.modifiedData.dirpip1x = self.data.dirpip1x - dirpelletX
            self.modifiedData.dirpip2x = self.data.dirpip2x - dirpelletX
            self.modifiedData.dirpip3x = self.data.dirpip3x - dirpelletX
            self.modifiedData.dirpip4x = self.data.dirpip4x - dirpelletX

            self.modifiedData.dirdigit1x = self.data.dirdigit1x - dirpelletX
            self.modifiedData.dirdigit2x = self.data.dirdigit2x - dirpelletX
            self.modifiedData.dirdigit3x = self.data.dirdigit3x - dirpelletX
            self.modifiedData.dirdigit4x = self.data.dirdigit4x - dirpelletX

            #Always
            self.modifiedData.dirpawdorsumx = self.data.dirpawdorsumx - dirpelletX
            self.modifiedData.dirnosex = self.data.dirnosex - dirpelletX
            self.modifiedData.dirpelletx = self.data.dirpelletx - dirpelletX
            self.modifiedData.dircontrapawdorsumx = self.data.dircontrapawdorsumx - dirpelletX

            #Shift Y
            #If left pawed
            self.modifiedData.dirmcp1y = self.data.dirmcp1y - dirpelletY
            self.modifiedData.dirmcp2y = self.data.dirmcp2y - dirpelletY
            self.modifiedData.dirmcp3y = self.data.dirmcp3y - dirpelletY
            self.modifiedData.dirmcp4y = self.data.dirmcp4y - dirpelletY

            self.modifiedData.dirpip1y = self.data.dirpip1y - dirpelletY
            self.modifiedData.dirpip2y = self.data.dirpip2y - dirpelletY
            self.modifiedData.dirpip3y = self.data.dirpip3y - dirpelletY
            self.modifiedData.dirpip4y = self.data.dirpip4y - dirpelletY

            self.modifiedData.dirdigit1y = self.data.dirdigit1y - dirpelletY
            self.modifiedData.dirdigit2y = self.data.dirdigit2y - dirpelletY
            self.modifiedData.dirdigit3y = self.data.dirdigit3y - dirpelletY
            self.modifiedData.dirdigit4y = self.data.dirdigit4y - dirpelletY
            
            #always
            self.modifiedData.dirpawdorsumy = self.data.dirpawdorsumy - dirpelletY
            self.modifiedData.dirnosey = self.data.dirnosey - dirpelletY
            self.modifiedData.dirpellety = self.data.dirpellety - dirpelletY
            self.modifiedData.dircontrapawdorsumy = self.data.dircontrapawdorsumy - dirpelletY
                
        return
    
    def addDirectView(self):
    
        #Whatever the fuck shuffle is actually makes this impossible. Will have to use OS to read from files rather than copying existing strings.
        dirPaths = self.session.dirPaths
        myDirPath = dirPaths[self.trialNum]
        
        try:
            dirDf = pd.read_csv(myDirPath,header=1,dtype=float,skiprows=[2])
            dirDf.drop('bodyparts',axis='columns')
        except FileNotFoundError:
            #Some naming conventions for files are different and trial number is in wrong place
            #Save file name to create a case statement to handle different naming conventions
            print('FileNotFoundError in Trial')
            print(dirFilename)
         
        if self.session.rat.pawpref == 'r':
        #If right pawed, name rpd sidepd and lpd contrapd
            dirDf = dirDf.rename(columns = { ##If right paw dominant, will rename from right to side
                          
            'rightmcp1':'dirmcp1x','rightmcp1.1':'dirmcp1y','rightmcp1.2':'dirmcp1p',
            'rightmcp2':'dirmcp2x','rightmcp2.1':'dirmcp2y','rightmcp2.2':'dirmcp2p',
            'rightmcp3':'dirmcp3x','rightmcp3.1':'dirmcp3y','rightmcp3.2':'dirmcp3p',
            'rightmcp4':'dirmcp4x','rightmcp4.1':'dirmcp4y','rightmcp4.2':'dirmcp4p',
                                                               
            'rightpip1':'dirpip1x','rightpip1.1':'dirpip1y','rightpip1.2':'dirpip1p',
            'rightpip2':'dirpip2x','rightpip2.1':'dirpip2y','rightpip2.2':'dirpip2p',
            'rightpip3':'dirpip3x','rightpip3.1':'dirpip3y','rightpip3.2':'dirpip3p',
            'rightpip4':'dirpip4x','rightpip4.1':'dirpip4y','rightpip4.2':'dirpip4p',
                                                               
            'rightdigit1':'dirdigit1x','rightdigit1.1':'dirdigit1y','rightdigit1.2':'dirdigit1p',
            'rightdigit2':'dirdigit2x','rightdigit2.1':'dirdigit2y','rightdigit2.2':'dirdigit2p',
            'rightdigit3':'dirdigit3x','rightdigit3.1':'dirdigit3y','rightdigit3.2':'dirdigit3p',
            'rightdigit4':'dirdigit4x','rightdigit4.1':'dirdigit4y','rightdigit4.2':'dirdigit4p',
            
            'rightpawdorsum':'dirpawdorsumx','rightpawdorsum.1':'dirpawdorsumy', 'rightpawdorsum.2':'dirpawdorsump',
            'rightpaw':'dirpawdorsumx','rightpaw.1':'dirpawdorsumy','rightpaw.2':'dirpawdorsump',
            'leftpawdorsum':'dircontrapawdorsumx','leftpawdorsum.1':'dircontrapawdorsumy','leftpawdorsum.2':'dircontrapawdorsump',
    
            ##Same for both paw pref
                                         
            'nose':'dirnosex','nose.1':'dirnosey','nose.2':'dirnosep',
            'pellet':'dirpelletx','pellet.1':'dirpellety','pellet.2':'dirpelletp',})
            
        elif self.session.rat.pawpref == 'l':
        #If left pawed, name rpd sidepd and lpd contrapd
            dirDf = dirDf.rename(columns = {
            ## If left paw dominant, will rename form left to side
                   
            'leftmcp1':'dirmcp1x','leftmcp1.1':'dirmcp1y','leftmcp1.2':'dirmcp1p',
            'leftmcp2':'dirmcp2x','leftmcp2.1':'dirmcp2y','leftmcp2.2':'dirmcp2p',
            'leftmcp3':'dirmcp3x','leftmcp3.1':'dirmcp3y','leftmcp3.2':'dirmcp3p',
            'leftmcp4':'dirmcp4x','leftmcp4.1':'dirmcp4y','leftmcp4.2':'dirmcp4p',
                                                           
            'leftpip1':'dirpip1x','leftpip1.1':'dirpip1y','leftpip1.2':'dirpip1p',
            'leftpip2':'dirpip2x','leftpip2.1':'dirpip2y','leftpip2.2':'dirpip2p',
            'leftpip3':'dirpip3x','leftpip3.1':'dirpip3y','leftpip3.2':'dirpip3p',
            'leftpip4':'dirpip4x','leftpip4.1':'dirpip4y','leftpip4.2':'dirpip4p',
                                                           
            'leftdigit1':'dirdigit1x','leftdigit1.1':'dirdigit1y','leftdigit1.2':'dirdigit1p',
            'leftdigit2':'dirdigit2x','leftdigit2.1':'dirdigit2y','leftdigit2.2':'dirdigit2p',
            'leftdigit3':'dirdigit3x','leftdigit3.1':'dirdigit3y','leftdigit3.2':'dirdigit3p',
            'leftdigit4':'dirdigit4x','leftdigit4.1':'dirdigit4y','leftdigit4.2':'dirdigit4p',
                                                 
            'rightpawdorsum':'dircontrapawdorsumx','rightpawdorsum.1':'dircontrapawdorsumy','rightpawdorsum.2':'dircontrapawdorsump',
            'rightpaw':'dircontrapawdorsumx','rightpaw.1':'dircontrapawdorsumy','rightpaw.2':'dircontrapawdorsump',
            'leftpawdorsum':'dirpawdorsumx','leftpawdorsum.1':'dirpawdorsumy','leftpawdorsum.2':'dirpawdorsump',
            
            ##Same for both paw pref
                                         
            'nose':'dirnosex','nose.1':'dirnosey','nose.2':'dirnosep',
            'pellet':'dirpelletx','pellet.1':'dirpellety','pellet.2':'dirpelletp',})
            
        self.data = self.data.join(dirDf)
        return
    
    def getPelletLoc(self,view):
    # Averages first 10 coordinates of pellet with likelihood of 1 to get initial location
    # Also ensures that the pellet location is not changing (e.g. if pedestal is still rising)
        
        if view == 'side':
            isChanging = True
            pelletLoc = 0
            firstTenX = []
            runningSumX = 0
            firstTenY = []
            runningSumY = 0
            #For side view
            l = len(self.data.sidepelletp)
            for i in range(l):
                x = self.data.sidepelletx[i+1]
                y = self.data.sidepellety[i+1]
                p = self.data.sidepelletp[i+1]
                x2 = self.data.sidepelletx[i+2]
                y2 = self.data.sidepellety[i+2]
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
        
        if view == 'direct':
            isChanging = True
            pelletLoc = 0
            firstTenX = []
            runningSumX = 0
            firstTenY = []
            runningSumY = 0
            #For direct view
            l = len(self.data.dirpelletp)
            for i in range(l):
                x = self.data.dirpelletx[i+1]
                y = self.data.dirpellety[i+1]
                p = self.data.dirpelletp[i+1]
                x2 = self.data.dirpelletx[i+2]
                y2 = self.data.dirpellety[i+2]
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
        if self.session.rat.view == 'both':
            self.modifiedData = self.modifiedData.drop(['sidemcp1p','sidemcp2p','sidemcp3p','sidemcp4p',
            'sidepip1p','sidepip2p','sidepip3p','sidepip4p',
            'sidedigit1p','sidedigit2p','sidedigit3p','sidedigit4p',
            'sidepawdorsump','sidenosep','sidepelletp','sidecontrapawdorsump',
            'dirmcp1p','dirmcp2p','dirmcp3p','dirmcp4p',
            'dirpip1p','dirpip2p','dirpip3p','dirpip4p',
            'dirdigit1p','dirdigit2p','dirdigit3p','dirdigit4p',
            'dirpawdorsump','dirnosep','dirpelletp','dircontrapawdorsump'],
            axis='columns')
        elif self.session.rat.view == 'side':
            self.modifiedData = self.modifiedData.drop(['sidemcp1p','sidemcp2p','sidemcp3p','sidemcp4p',
            'sidepip1p','sidepip2p','sidepip3p','sidepip4p',
            'sidedigit1p','sidedigit2p','sidedigit3p','sidedigit4p',
            'sidepawdorsump','sidenosep','sidepelletp'],
            axis='columns')
        elif self.session.rat.view == 'direct':
            self.modifiedData = self.modifiedData.drop([
            'dirmcp1p','dirmcp2p','dirmcp3p','dirmcp4p',
            'dirpip1p','dirpip2p','dirpip3p','dirpip4p',
            'dirdigit1p','dirdigit2p','dirdigit3p','dirdigit4p',
            'dirpawdorsump','dirnosep','dirpelletp','dircontrapawdorsump'],
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
