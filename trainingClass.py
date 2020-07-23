import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier as kNN
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
        #self.ratData = {}
        self.ratModifiedData = {} #Dict. mapping ratIds to array containing all kinematic data for that rat
        self.ratLabels = {} #Dict. mapping ratIds to array containing all labels for that rat (not sep. by date/trial)
        
        #Populates data and modifiedData from rats used as input
        #modifiedData has been shifted to pellet origin, scaled, and
        #probabilities have been accounted for
        reshaped_mod = []
        #reshaped_dat = []
        reshaped_lab = []
        for rat in ratList:
            sess = rat.sessions
            for date,session in sess.items():
                tri = sess[date].trials
                for num, trial in tri.items():
                    modDat = tri[num].modifiedData.values
                    #dat = tri[num].data.values
                    lab = tri[num].label
                    #Reshaped is a temporary variable that is supposed to combine all 1290 rows from
                    #each trial into a 1D feature array, it is then added to the list of all trials
                    #and reset
                    reshaped = []
                    first = True
                    for row in modDat:
                        #print(row)
                        #break
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
        #return

    def trainClassifier(self,n_components,n_neighbors,test_frac):
        #Implements pipeline to fit PCA transform and kNN classifier,
        #saves parameters for both as attributes of trainingClass
        #prints training and test score for the classifier
        pipe = Pipeline([('ipca', IncrementalPCA(n_components = n_components)),
                        ('knn', BaggingClassifier(base_estimator=kNN(n_neighbors = n_neighbors,weights = 'distance'),n_estimators=5))] )
        trainData, testData, trainLabel, testLabel = self.splitData(test_frac)
        pipe.fit(trainData,trainLabel)
        
        self.PCAmodel = pipe.named_steps['ipca']
        self.kNNmodel = pipe.named_steps['knn']
        
        #Save classifier as pck
        #pickle.dump(self.PCAmodel,open('PCAmodel.p','wb'))
        #pickle.dump(self.kNNmodel,open('kNNmodel.p','wb'))
        
        wholeModel = {'PCA':self.PCAmodel,'kNN':self.kNNmodel}
        
        prefix = self.nameClassifier()
        if (prefix == ''):
            picklename = 'Classifier.p'
            #print('no response')
        else:
            picklename = prefix+'Classifier.p'
        pickle.dump(wholeModel,open(picklename,'wb'))
        
        train_score = pipe.score(trainData,trainLabel)
        test_score = pipe.score(testData,testLabel)
        print('Training score is: %f' % train_score)
        print('Testing score is: %f' % test_score)
        
        return
        
    def nameClassifier(self):
        msg = 'Type filename for this classifier:'
        title = 'Name Classifier'
        fieldNames = ['Prefix']
        reply = gui.multenterbox(msg,title,fieldNames)[0]
        if reply == '':
            doubleCheck = gui.ccbox(msg='If you do not enter a prefix, file will be saved as "Classifier.p". Continue?',title='You did not enter a prefix')
            if doubleCheck:
                reply = ['']
                print('no response')
                pass
            else:
                reply = gui.multenterbox(msg,title,fieldNames)[0]
    
        return reply
    
    def useClassifier(self):
        #Score a dataset
        trainData, testData, trainLabel, testLabel = self.splitData(1)
        pipe = Pipeline([self.PCAmodel,self.kNNmodel])
        predictions = pipe.predict(testData)
        
        perfect = len(predictions)
        assert perfect == len(testLabel)
        score = 0
        mistakes = {}
        
        for i in perfect:
            if predictions[i] == testLabel[i]:
                score += 1
            else:
                mistakes[i] = [prediction, testLabel]
        
        print(score/perfect)
        
        return mistakes
