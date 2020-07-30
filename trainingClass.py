import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier as kNN
from sklearn.preprocessing import StandardScaler
import pickle
import easygui as gui

class trainingClass:
    #This is meant to combine trial data across multiple rats as well as
    #saving the parameters for PCA transforms and kNN classifiers
    #*args should be Rat class
    def __init__(self,ratList):
        # Add an option to load a trained classifier into a new trainingClass?
    
        # PCA model should be updated each time, currently not doing this...?
        self.PCAmodel = 0
        self.kNNmodel = 0
        self.ratModifiedData = {} #Dict. mapping ratIds to array containing all kinematic data for that rat
        self.ratLabels = {} #Dict. mapping ratIds to array containing all labels for that rat (not sep. by date/trial)
        
        #Populates data and modifiedData from rats used as input
        #modifiedData has been shifted to pellet origin, scaled, and
        #probabilities have been accounted for
        reshaped_mod = []
        reshaped_lab = []
        for rat in ratList:
            sess = rat.sessions
            for date,session in sess.items():
                tri = sess[date].trials
                for num, trial in tri.items():
                    modDat = tri[num].modifiedData.values
                    lab = tri[num].label
                    #Reshaped is a temporary variable that is supposed to combine all 1290 rows from
                    #each trial into a 1D feature array, it is then added to the list of all trials
                    #and reset
                    reshaped = []
                    first = True
                    for row in modDat:
                        if first:
                            reshaped = row
                            first = False
                        else:
                            reshaped = np.concatenate((reshaped, row))
                    reshaped_mod.append(reshaped)
                    reshaped_lab.append(lab)
            self.ratModifiedData[rat.id] = reshaped_mod
            self.ratLabels[rat.id] = reshaped_lab

    def splitData(self,test_frac):
        #Divides data from trainingClass into training and test sets
        #where test_frac is the % of data saved for test sets
        allData = []
        trialData_reshaped = []
        allLabels = []
        first = True
        
        for ratId,rat in self.ratModifiedData.items():
            if first:
                allData = rat
                first = False
                allLabels = self.ratLabels[ratId]
            else:
                allData = np.concatenate((allData,rat))
                allLabels = np.concatenate((allLabels,self.ratLabels[ratId]))
        
        trainData, testData, trainLabel, testLabel = train_test_split(allData, allLabels, test_size=test_frac)
        
        return trainData, testData, trainLabel, testLabel

    def testAll(self):
        #Same process as 'splitData' but does not split dataset into training and test sets
        allData = []
        trialData_reshaped = []
        allLabels = []
        first = True
        
        for ratId,rat in self.ratModifiedData.items():
            if first:
                allData = rat
                first = False
                allLabels = self.ratLabels[ratId]
            else:
                allData = np.concatenate((allData,rat))
                allLabels = np.concatenate((allLabels,self.ratLabels[ratId]))
                
        return allData, allLabels

    def trainClassifier(self,n_components,n_neighbors,test_frac):
        #Implements pipeline to fit Scaler, PCA transform and kNN classifier,
        #saves parameters for both as attributes of trainingClass
        #prints training and test score for the classifier
        pipe = Pipeline([('scaler',StandardScaler()),('ipca', IncrementalPCA(n_components = n_components)),
                        ('knn', BaggingClassifier(base_estimator=kNN(n_neighbors = n_neighbors,weights = 'distance'),n_estimators=5))],verbose=True )
                        
        trainData, testData, trainLabel, testLabel = self.splitData(test_frac)
        
        pipe.fit(trainData,trainLabel)
        
        self.scaler = pipe.named_steps['scaler']
        self.PCAmodel = pipe.named_steps['ipca']
        self.kNNmodel = pipe.named_steps['knn']
        self.pipeline = pipe
        
        prefix = self.nameClassifier()
        if (prefix == ''):
            picklename = 'UnnamedClassifier.p'
        else:
            picklename = prefix + '.p'
        pickle.dump(self,open(picklename,'wb'))
        
        train_score = pipe.score(trainData,trainLabel)
        test_score = pipe.score(testData,testLabel)
        print('Training score is: %f' % train_score)
        print('Testing score is: %f' % test_score)
        
        return
        
    def nameClassifier(self):
        msg = 'Type filename for this classifier: '
        reply = input(msg)
        if reply == '':
            doubleCheck = input('If you do not enter a prefix, file will be saved as "Classifier.p" - continue? (y/n): ')
            if doubleCheck == 'y':
                reply = ''
                pass
            else:
                reply = input(msg)
    
        return reply
    
    
    def checkMistake(self,mis):
        all = len(mis)
        if not (all == 0):
            count1 = 0
            count2 = 0
            count3 = 0
            count4 = 0
            count7 = 0
            count_other = 0
            for i in mis:
                if i == '1':
                    count1 += 1
                elif i == '2':
                    count2 += 1
                elif i == '3':
                    count3 += 1
                elif i == '4':
                    count4 += 1
                elif i == '7':
                    count7 += 1
                else:
                    count_other += 1
            all = len(mis)
            fracs = [count1/all, count2/all, count3/all, count4/all, count7/all, count_other/all]
        else: fracs = [0,0,0,0,0,0]
        return fracs
        
    
    def useClassifier(self):
        #Score a dataset
        testData, testLabel = self.testAll()
        pipe = self.pipeline
        predictions = pipe.predict(testData)
        
        perfect = len(predictions)
        assert perfect == len(testLabel)
        score = 0
        mistakes = []
        
        for i in range(perfect):
            if predictions[i] == testLabel[i]:
                score += 1
            else:
                mistakes.append([predictions[i], testLabel[i]])
                
        mis_1 = []
        mis_2 = []
        mis_3 = []
        mis_4 = []
        mis_7 = []
        mis_other = []
        for a,b in mistakes:
            if a == '1':
                mis_1.append(b)
            elif a == '2':
                mis_2.append(b)
            elif a == '3':
                mis_3.append(b)
            elif a == '4':
                mis_4.append(b)
            elif a == '7':
                mis_4.append(b)
            else:
                mis_other.append(b)
        
        if len(mis_1) > 0:
            frac1, frac2, frac3, frac4, frac7, frac_o = self.checkMistake(mis_1)
            print('1s were mislabelled as:\n 2: %2f percent of the time\n 3: %2f of the time\n 4: %2f percent of the time\n 7: %2f percent of the time\n Other: %2f percent of the time\n' % (frac2,frac3,frac4,frac7,frac_o))
        else:
            print('1s were not mislabelled.')
        
        if len(mis_2) > 0:
            frac1, frac2, frac3, frac4, frac7, frac_o = self.checkMistake(mis_2)
            print('2s were mislabelled as:\n 1: %2f percent of the time\n 3: %2f percent of the time\n 4: %2f percent of the time\n 7: %2f percent of the time\n Other: %2f percent of the time\n' % (frac1*100,frac3*100,frac4*100,frac7*100,frac_o*100))
        else:
            print('2s were not mislabelled.')
        
        if len(mis_3) > 0:
            frac1, frac2, frac3, frac4, frac7, frac_o = self.checkMistake(mis_3)
            print('3s were mislabelled as:\n 1: %2f percent of the time\n 2: %2f percent of the time\n 4: %2f percent of the time\n 7: %2f percent of the time\n Other: %2f percent of the time\n' % (frac1*100,frac2*100,frac4*100,frac7*100,frac_o*100))
        else:
            print('3s were not mislabelled.')
        
        if len(mis_4) > 0:
            frac1, frac2, frac3, frac4, frac7, frac_o = self.checkMistake(mis_4)
            print('4s were mislabelled as:\n 1: %2f percent of the time\n 2: %2f percent of the time\n 3: %2f percent of the time\n 7: %2f percent of the time\n Other: %2f percent of the time\n' % (frac1*100,frac2*100,frac3*100,frac7*100,frac_o*100))
        else:
            print('4s were not mislabelled.')
        
        if len(mis_7) > 0:
            frac1, frac2, frac3, frac4, frac7, frac_o = self.checkMistake(mis_7)
            print('7s were mislabelled as:\n 1: %2f percent of the time\n 2: %2f percent of the time\n 3: %2f percent of the time\n 4: %2f percent of the time\n Other: %2f percent of the time\n' % (frac1*100,frac2*100,frac3*100,frac4*100,frac_o*100))
        else:
            print('7s were not mislabelled.')
        
        print('Total score was: %f' % (score/perfect))
        return
