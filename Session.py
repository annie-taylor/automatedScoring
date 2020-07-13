import pandas as pd
import numpy as np
import os
from Trial import Trial

TEST = 'hi'

class Session():
    def __init__(self, ratIn, folder, date_in, labl_arr):
        self.rat = ratIn # Rat obj. which contains session
        self.trials = {} # Dict. storing all trial obj. for this session
        self.date = date_in #Date of the session YYYYMMDD
        
        #Currently unused
        self.laser_info = labl_arr[0]
        
        for subfolder in os.listdir(folder):
            subfolder = folder + '/' + subfolder
            
            #if 'dir' in subfolder:
            #    for csv in os.listdir(subfolder):
            #        if csv.endswith('.csv'):
            #            csv = subfolder + '/' + csv
            #            trialNum = int(csv.split('_')[-7])
            #            import math
            #            if not math.isnan(float(labl_arr[trialNum])):
            #                self.trials[trialNum] = Trial(self, csv, trialNum, labl_arr[trialNum])
                            
            #Try not using direct view
            
            if 'left' in subfolder:
                self.rat.pawpref = 'l'
                for csv in os.listdir(subfolder):
                    if csv.endswith('.csv'):
                        csv = subfolder + '/' + csv
                        trialNum = int(csv.split('_')[-7])
                        import math
                        if not math.isnan(float(labl_arr[trialNum])):
                            self.trials[trialNum] = Trial(self, csv, trialNum, labl_arr[trialNum])
                            
            if 'right' in subfolder:
                self.rat.pawpref = 'r'
                for csv in os.listdir(subfolder):
                    if csv.endswith('.csv'):
                        csv = subfolder + '/' + csv
                        trialNum = int(csv.split('_')[-7])
                        import math
                        if not math.isnan(float(labl_arr[trialNum])):
                            self.trials[trialNum] = Trial(self, csv, trialNum, labl_arr[trialNum])
            
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
