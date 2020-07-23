import pandas as pd
import numpy as np
import os
from Trial import Trial
import math


class Session():
    def __init__(self, ratIn, folder, date_in, labl_arr):
        self.rat = ratIn # Rat obj. which contains session
        self.trials = {} # Dict. storing all trial obj. for this session
        self.date = date_in #Date of the session YYYYMMDD
        self.dirPaths = {}
        
        #Currently unused
        self.laser_info = labl_arr[0]
    
        subfolders = os.listdir(folder)
        for subfolder in subfolders:
            subfolder = folder + '/' + subfolder
            #Make list of direct view filenames
            if 'dir' in subfolder:
                for csv in os.listdir(subfolder):
                    if csv.endswith('.csv'):
                        csv = subfolder + '/' + csv
                        trialNum = int(csv.split('_')[-7])
                        if not math.isnan(float(labl_arr[trialNum])):
                            self.dirPaths[trialNum] = csv
        
        for subfolder in subfolders:
            subfolder = folder + '/' + subfolder
            
            #Check side views
            if 'right' in subfolder:
                #L paw pref rats have camera from right side (I think.. double check this)
                self.rat.pawpref = 'l'
                for csv in os.listdir(subfolder):
                    if csv.endswith('.csv'):
                        csv = subfolder + '/' + csv
                        try:
                            trialNum = int(csv.split('_')[-7])
                            if not math.isnan(float(labl_arr[trialNum])):
                                self.trials[trialNum] = Trial(self, csv, trialNum, labl_arr[trialNum])
                        except ValueError:
                            print('ValueError in Session')
                            print(self.rat.id)
                            print(self.date)
                            print(trialNum)
                        
                            
            if 'left' in subfolder:
                self.rat.pawpref = 'r'
                for csv in os.listdir(subfolder):
                    if csv.endswith('.csv'):
                        csv = subfolder + '/' + csv
                        try:
                            trialNum = int(csv.split('_')[-7])
                            if not math.isnan(float(labl_arr[trialNum])):
                                self.trials[trialNum] = Trial(self, csv, trialNum, labl_arr[trialNum])
                        except ValueError:
                            print('ValueError in Session')
                            print(self.rat.id)
                            print(self.date)
            
    def dimReduction(self,n_components,n_trials):
        #Currently unused, moved to super class
        
        # n_components specifies number of principle components for PCA output
        # n_trials
        # Can I apply the same transformation to differently sized arrays?
        # Have to ask this question for both the PCA and the classifier
        
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
