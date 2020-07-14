import pandas as pd
import numpy as np
import sys, os
if not os.path.dirname(__file__) in sys.path:
    sys.path.append(os.path.dirname(__file__))
from Session import Session


class Rat:
    def __init__(self,masterfolder):
        
        self.id = masterfolder.split('/')[-1]
        self.pawpref = None
        
        #mapped directly to data in sessions object, key are session dates as "YYYYMMDD"
        #data = unmodified
        #modifiedData has been scaled and
        self.sessions = {}
        score_path = masterfolder + '/' + self.id + '_scores.csv'
        self.labels = pd.read_csv(score_path)
        self.labels = self.labels.drop('Unnamed: 0', axis='columns')
        
        #Can probably move this to a separate function to make this more concise
        for folder in os.listdir(masterfolder):
            fullpath = masterfolder + '/' + folder
            if os.path.isdir(fullpath) and fullpath.endswith('a'):
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
                
                try:
                    sessionLabels = self.labels[date_form].tolist()
                    #If this second block is outside try statement, will try to make
                    #session object without a a sessionLabels variable
                    self.sessions[date] = Session(self, fullpath, date, sessionLabels)
                except KeyError:
                    #This should only happen if there is a folder/session that exists that is unscored
                    #Update this to save any session dates (and corresponding RatID) to keep track of unscored sessions
                    print('KeyError in Rat')
                    print(fullpath)
                    print(date_form)
        return
                
    def trainingSet(self,prob):
        #Keep this until trainingClass is completely functional
        #At the moment this is not being used at all
        
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
                    if self.pawpref == 'l':
                        self.sessions[date].trials[trialNum].data.drop(['leftmcp1p','leftmcp2p','leftmcp3p','leftmcp4p',
                                                 'leftpip1p','leftpip2p','leftpip3p','leftpip4p',
                                                 'leftdigit1p','leftdigit2p','leftdigit3p','leftdigit4p',
                                                 'leftpawdorsump','nosep','pelletp','rightpawdorsump'],
                                                axis='columns')
                    elif self.pawpref == 'r':
                        self.sessions[date].trials[trialNum].data.drop(['rightmcp1p','rightmcp2p','rightmcp3p','rightmcp4p',
                                                 'rightpip1p','rightpip2p','rightpip3p','rightpip4p',
                                                 'rightdigit1p','rightdigit2p','rightdigit3p','rightdigit4p',
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
        #Currently unused, consider using this to plot an "average" trajectory if would be helpful
        
        #Returns all kinematics data for a trial with a given label
        label = int(givenlabel)
        labelledTrials = {}
        for date in self.sessions:
            session = self.sessions[date].trials
            for trialNum in session:
                trialObj = self.sessions[date].trials[trialNum]
                #try:
                if int(trialObj.label) == givenlabel:
                    labelledTrials[trialNum] = trialObj
                #except ValueError:
                    #continue
        return labelledTrials