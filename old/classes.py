import os
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go

class Rat:
    def __init__(self,masterfolder):
        self.sessions = {}
        self.id = masterfolder.split('/')[-1]
        
        score_path = masterfolder + '/' + self.id + '_scores.csv'
        self.labels = pd.read_csv(score_path)
        self.labels = self.labels.drop('Unnamed: 0', axis='columns')
        
        for folder in os.listdir(masterfolder):
            fullpath = masterfolder + '/' + folder
            if os.path.isdir(fullpath):
                date = str(folder[-9:-1])
                
                year = date[0:4]
                month = date[4:6]
                day = date[6:]
                date_form = ''
                if month[0] == '0':
                    date_form += month[-1] + '/'
                else:
                    date_form += month + '/'
                if day[0] == '0':
                    date_form += day[-1] + '/'
                else:
                    date_form += day + '/'
                date_form += year[-2:]
                
                sess_labls = self.labels[date_form].tolist()
                self.sessions[date] = Session(fullpath, date, sess_labls)
        
        
    def trainingSet(self,prob):
        #Generate training data and labels from a rat class
        #Outputs trainingData and trainingLabels as lists of dataframes
        #Will either keep (prob = 1) or omit (prob = 0) probabilities depending on value of 'prob'

        fitData = []
        fitLabels = []
        
        for date in self.sessions:
            session = self.sessions[date].trials
            
            if not prob:
                for trialNum in session:
                    self.sessions[date].trials[trialNum].smoothProb()
                    self.sessions[date].trials[trialNum].data.drop(['leftmcp1p','leftmcp2p','leftmcp3p','leftmcp4p',
                                             'leftpip1p','leftpip2p','leftpip3p','leftpip4p',
                                             'leftdigit1p','leftdigit2p','leftdigit3p','leftdigit4p',
                                             'leftpawdorsump','nosep','pelletp','rightpawdorsump'],
                                            axis='columns')
            else:
                for trialNum in session:
                    self.sessions[date].trials[trialNum].smoothProb()
                    
            decompFeatures, labels = self.sessions[date].dimReduction(3,1)
            
            for trial in decompFeatures:
                trialAr = np.concatenate((trial[:,0], trial[:,1], trial[:,2]))
                fitData.append(trialAr)
                
            for label in labels:
                fitLabels.append(label)
                
        trainData, testData, trainLabel, testLabel = train_test_split(fitData, fitLabels, test_size=0.33)
        return trainData, testData, trainLabel, testLabel
    
    def sortByLabel(self,givenlabel):
        #Returns all kinematics data for a trial with a given label
        label = int(givenlabel)
        labelledTrials = {}
        for date in self.sessions:
            session = self.sessions[date].trials
            for trialNum in session:
                trialObj = self.sessions[date].trials[trialNum]
                try:
                    if int(trialObj.label) == givenlabel:
                        labelledTrials[trialNum] = trialObj
                except ValueError:
                    continue
        return labelledTrials
    

class Session:
    def __init__(self, folder, date_in, labl_arr):
 
        self.trials = {}
        self.date = date_in
        self.laser_info = labl_arr[0]
        
        for subfolder in os.listdir(folder):
            subfolder = folder + '/' + subfolder
            
            if 'dir' in subfolder:
                for csv in os.listdir(subfolder):
                    if csv.endswith('.csv'):
                        csv = subfolder + '/' + csv
                        trialNum = int(csv.split('_')[-7])
                        import math
                        if not math.isnan(float(labl_arr[trialNum])):
                            self.trials[trialNum] = Trial(csv, trialNum, labl_arr[trialNum])
                        
    def dimReduction(self,n_components,n_trials):
        # n_components specifies what 
        # n_trials 
        
        #Need to test how many times to run incremental PCA
        decomp = IncrementalPCA(n_components=n_components)
        count = 0
        decompFeatures = []
        labels = []

        #Fit PCA to first ten trials in feature array
        for trialNum, trialObj in self.trials.items():
            trialData = trialObj.modifiedData
            decomp = decomp.partial_fit(trialData)
            count += 1
            if not (count < n_trials):
                break

        #Apply PCA to all trials in feature array
        for trialNum, trialObj in self.trials.items():
            trialData = trialObj.modifiedData
            decomp_trial = decomp.transform(trialData)
            decompFeatures.append(decomp_trial)
            labels.append(trialObj.label)
            
        return decompFeatures, labels
                        
class Trial:
    def __init__(self, filename, tnum, label_in):
        self.trialNum = tnum
        self.label = label_in
        self.data = pd.read_csv(filename,header=1,dtype=float,skiprows=[2])   
        self.data = self.data.drop('bodyparts',axis='columns')

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
            'rightpawdorsum':'rightpawdorsumx','rightpawdorsum.1':'rightpawdorsumy','rightpawdorsum.2':'rightpawdorsump'
            })
        self.modifiedData = pd.DataFrame(self.data) # Will be used to save data after pellet
        self.standardScale()

    def standardScale(self):
        scaler = StandardScaler()
        self.pelletOrigin()
        scaler.fit(self.modifiedData.values)
        self.modifiedData = scaler.transform(self.modifiedData.values)
        return
    
    def pelletOrigin(self):
        [pelletX, pelletY] = self.getPelletLoc()
        
        #Shift X
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
        
        self.modifiedData.leftpawdorsumx = self.data.leftpawdorsumx - pelletX
        self.modifiedData.nosex = self.data.nosex - pelletX
        self.modifiedData.pelletx = self.data.pelletx - pelletX
        self.modifiedData.rightpawdorsumx = self.data.rightpawdorsumx - pelletX
        
        #Shift Y
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
        
        self.modifiedData.leftpawdorsumy = self.data.leftpawdorsumy - pelletY
        self.modifiedData.nosey = self.data.nosey - pelletY
        self.modifiedData.pellety = self.data.pellety - pelletY
        self.modifiedData.rightpawdorsumy = self.data.rightpawdorsumy - pelletY
        
        return
    
    def getPelletLoc(self):
        #Averages first 10 coordinates of pellet with likelihood of 1 to get initial location
        
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
        #Returns df with all rows in random order
        return self.data.sample(frac = 1)
    
    def smoothProb(self):
    # Looks through trial data for low probability values, reassigns all low prob points
    # With a point extrapolated between the most recent high p point and the next closest high p
        testtrial = self.data
        columnNames = testtrial.columns
        missed = []
        numMissed = 0
        for i in columnNames:
            if i.endswith('p'):
                bodypart = i[:-1]
                x = bodypart + 'x'
                y = bodypart + 'y'
                for j in testtrial.index:
                    if testtrial[i].values[j] < .98:
                            missed.append(j)
                            if numMissed == 0:
                                leftmost = j
                            numMissed = len(missed)
                    else:
                        rightmost = j
                        if numMissed > 0:
                            l = int(numMissed/2)
                            r = numMissed
                            linex = np.linspace(testtrial[x].values[leftmost],
                                                testtrial[x].values[rightmost],numMissed)
                            liney = np.linspace(testtrial[y].values[leftmost],
                                                testtrial[y].values[rightmost],numMissed)
                            for k in range(r):
                                current = int(missed[k])
                                testtrial[x].values[current] = linex[k]
                                testtrial[y].values[current] = liney[k]
                            missed = []
                            numMissed = 0
                        leftmost = j
                if (numMissed) > 0:
                    if numMissed > 0:
                            l = int(numMissed/2)
                            r = numMissed
                            linex = np.linspace(testtrial[x].values[leftmost],
                                                testtrial[x].values[rightmost],numMissed)
                            liney = np.linspace(testtrial[y].values[leftmost],
                                                testtrial[y].values[rightmost],numMissed)
                            for k in range(r):
                                current = int(missed[k])
                                testtrial[x].values[current] = linex[k]
                                testtrial[y].values[current] = liney[k]
        return
    
    def plotTrajectories(self,bodyPart,showProb):
        x = bodyPart + 'x'
        y = bodyPart + 'y'
        pName = bodyPart + 'p'
        if showProb:
            p = self.data[pName].values
            fig = go.Figure(data=[go.Scatter3d(x=self.data.index.values, y=self.data[y].values, 
                    z=self.data[x].values,mode='markers',
                    marker=dict(size=3,
                    color=p,                # set color to an array/list of desired values
                    colorscale = 'RdBu',                        # choose a colorscale
                    opacity=0.8,showscale = True))],
                    layout=go.Layout(
                    title=go.layout.Title(text=bodyPart)
                ))
            fig.show()
        else:
            fig = go.Figure(data=[go.Scatter3d(x=self.data.index.values, y=self.data[y].values, 
                    z=self.data[x].values,mode='markers',
                    marker=dict(size=3))],
                    layout=go.Layout(
                    title=go.layout.Title(text=bodyPart)
                ))
            fig.show()
        return 