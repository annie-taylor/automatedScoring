import pandas as pd
import numpy as np
import sys, os
if not os.path.dirname(__file__) in sys.path:
    sys.path.append(os.path.dirname(__file__))
from Session import Session
import csv


class Rat:
    def __init__(self,masterfolder,view):
        
        self.id = masterfolder.split('/')[-1]
        print("Currently preprocessing data from %s..." % self.id)
        self.pawpref = None
        self.view = view
        
        #mapped directly to data in sessions object, key are session dates as "YYYYMMDD"
        #data = unmodified
        #modifiedData has been scaled and
        self.sessions = {}
        score_path = masterfolder + '/' + self.id + '_scores.csv'
        self.labels = pd.read_csv(score_path)
        self.labels = self.labels.drop('Unnamed: 0', axis='columns')
        self.keyerrors = []
        
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
                    self.keyerrors.append(date)
                    #print('KeyError in Rat')
                    #print(fullpath)
                    #print(date_form)


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
