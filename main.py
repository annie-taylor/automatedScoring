from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox
import time
from Rat import Rat
from Session import Session
from Trial import Trial
import trainingClass as tc
import easygui as gui
import pickle
import os
import pandas as pd

class wrapper():
    def __init__(self):
        self.dirs = []
        self.rats = {}
        self.training = 0
        self.keyerrors = pd.DataFrame()
        choice = input('Reload old data or upload new data? (old/new): ')
        choice = choice.lower()
        if choice == 'old':
            view = input('Do you want to load direct view, side view, or both (type direct/side/both): ')
            if view == 'both':
                self.rats = pickle.load(open('rats.p','rb'))
            #Loads all data, only saves data w/direct view
            elif view == 'direct':
                self.rats = pickle.load(open('rats.p','rb'))
                for ratId,rat in self.rats.items():
                    for sessionId,session in self.rats[ratId].sessions.items():
                        for trialNum,trial in self.rats[ratId].sessions[sessionId].trials.items():
                            data = self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData
                            columnNames = self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData.columns
                            drops = []
                            for i in columnNames:
                                if 'side' in i:
                                    drops.append(i)
                            self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData = self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData.drop(drops,axis='columns')
            #Loads all data, only saves data w/side view
            elif view == 'side':
                self.rats = pickle.load(open('rats.p','rb'))
                for ratId,rat in self.rats.items():
                    for sessionId,session in self.rats[ratId].sessions.items():
                        for trialNum,trial in self.rats[ratId].sessions[sessionId].trials.items():
                            data = self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData
                            columnNames = self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData.columns
                            drops = []
                            for i in columnNames:
                                if 'dir' in i:
                                    drops.append(i)
                            self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData = self.rats[ratId].sessions[sessionId].trials[trialNum].modifiedData.drop(drops,axis='columns')
            print('Building trainingClass object...')
            self.addTrainClass()
        elif choice == 'new':
            print('Opening window to select files...')
            self.getDirs()
            self.addRat()
            print('Building trainingClass object...')
            self.addTrainClass()
            
    def addRat(self):
        ## Create object with dataset
        time1 = time.time()
        try:
            #If rats database already exists, will add rats
            loadrats = pickle.load(open('rats.p','rb'))
            self.rats = loadrats
            ids = loadrats.keys()
            print(ids)
            for i in range(len(self.dirs)):
                currentDir = self.dirs[i]
                checkId = currentDir.split('/')
                checkId = checkId[-1]
                print(checkId)
                if checkId not in ids:
                    Rat1 = Rat(currentDir)
                    currentid = Rat1.id
                    self.rats[Rat1.id] = Rat1
                    loadrats[currentid] = Rat1
                    self.saveKeyErrors(Rat1)
                else:
                    self.rats = loadrats
            pickle.dump(loadrats,open('rats.p','wb'))
            self.exportKeyErrors()
        except FileNotFoundError:
            #If rats db does not exist, will create it
            for i in range(len(self.dirs)):
                Rat1 = Rat(self.dirs[i])
                currentid = Rat1.id
                self.rats[Rat1.id] = Rat1
                self.saveKeyErrors(Rat1)
            pickle.dump(self.rats,open('rats.p','wb'))
            self.exportKeyErrors()
        time2 = time.time()
        elapsed = time2-time1
        minutes = int(elapsed/60)
        seconds = elapsed - (minutes*60)
        print("Total time to load dataset: %d minutes %d seconds" % (minutes,seconds))
        return

    def saveKeyErrors(self,Rat):
        #This is not working properly
        id = Rat.id
        self.keyerrors.append({id:Rat.keyerrors},ignore_index=True)
        return
    
    def exportKeyErrors(self):
        #This is not working properly
        (self.keyerrors).to_csv("KeyErrors.csv")
        return
    
    def addTrainClass(self):
        #Test trainingSet methods
        time1 = time.time()
        ratList = self.rats.values()
        self.training = tc.trainingClass(ratList)
        pickle.dump(self.training,open('trainingClass.p','wb'))
        time2 = time.time()
        #print("Time to build trainingClass object: %f" % (time2-time1))
        return
        
    def reload(self):
        #options = ['RatClasses','Rat & Training Classes','None']
        #choice = gui.choicebox(msg='Reload earlier classes?',title='Reload Dialogue',choices=options)
        choice = input('Reload old data or upload new data? (old/new): ')
        choice = choice.lower()
        if choice == 'old':
            self.rats = pickle.load(open('rats.p','rb'))
        #elif choice == options[1]:
         #   self.rats = pickle.load(open('rats.p','rb'))
         #   self.training = pickle.load(open('trainingClass.p','rb'))
        elif choice == 'new':
            self.addRat()
            self.addTrainClass()
    
    def getDirs(self):
        time1 = time.time()
        #get rid of that little annoying tk window
        root = Tk()
        root.withdraw()
        #do the thing
        dirselect = filedialog.Directory()
        while True:
            # Can modify this to req. people type in directories instead?
            # Like in BSOID?
            d = dirselect.show(initialdir = "/Volumes/",title = "Select rat folder")
            if not d: break
            self.dirs.append(d)
        time2 = time.time()
        print("Time to save pathnames: %d seconds" % (time2-time1))

def askParams():
    
    pca = int(input("PCA: # of dimensions: "))
    knn = int(input("K-NN: # of neighbors: "))
    frac = float(input("Fraction held out for test set: "))
    
    values = [pca,knn,frac]
    return values
 
def initialAsk():
    msg = "Do you want to load an old classifier or train a new classifier? (old/new): "
    #title = "Start"
    #fieldNames = ["Old","New"]
    #response = ""
    #response = gui.buttonbox(msg,title, fieldNames)
    response = input(msg)
    return response

def askTrainClassifier(wrap):
    response = askParams()
    time1 = time.time()
    print("Training classifier...")
    wrap.training.trainClassifier(response[0],response[1],response[2])
    time2 = time.time()
    elapsed = time2-time1
    minutes = int(elapsed/60)
    seconds = elapsed - (minutes*60)
    print("Time to train classifier: %d minutes %d seconds" % (minutes,seconds))

def selectClassifier():
    path = os.getcwd()
    files = os.listdir(path)
    pickles = []
    for file in files:
        if file.endswith('Classifier.p'):
            pickles.append(file)
    
    msg = "Choose file to reload previously trained classifier"
    title = "Select classifier"
    response = ""
    response = gui.buttonbox(msg,title, pickles)
    return response
    
def main():
    response = initialAsk()
    response = response.lower()
    if response == "old":
        filename = selectClassifier()
    elif response == "new":
        wrap = wrapper()
        askTrainClassifier(wrap)
    
if __name__ == '__main__':
    main()
    
