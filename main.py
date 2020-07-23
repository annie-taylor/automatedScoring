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
        #Might not really need all three options, two might be enough
        options = ['Existing rat data','Existing rat and training class data','Upload new data']
        choice = gui.choicebox(msg='Reload earlier classes?',title='Reload Dialogue',choices=options)
        if choice == options[0]:
            self.rats = pickle.load(open('rats.p','rb'))
            self.addTrainClass()
        elif choice == options[1]:
            self.rats = pickle.load(open('rats.p','rb'))
            self.training = pickle.load(open('trainingClass.p','rb'))
        elif choice == options[2]:
            self.getDirs()
            self.addRat()
            self.addTrainClass()
            
    def addRat(self):
        ## Create object with dataset
        time1 = time.time()
        try:
            #If rats database already exists, will add rats
            loadrats = pickle.load(open('rats.p','rb'))
            ids = loadrats.keys()
            for i in range(len(self.dirs)):
                Rat1 = Rat(self.dirs[i])
                currentid = Rat1.id
                self.rats[Rat1.id] = Rat1
                if currentid not in ids:
                    loadrats[currentid] = Rat1
                    self.saveKeyErrors(Rat1)
            pickle.dump(loadrats,open('rats.p','wb'))
            print(self.keyerrors)
            self.exportKeyErrors()
        except EOFError:
            #If rats db does not exist, will create it
            for i in range(len(self.dirs)):
                Rat1 = Rat(self.dirs[i])
                currentid = Rat1.id
                self.rats[Rat1.id] = Rat1
                self.saveKeyErrors(Rat1)
            pickle.dump(self.rats,open('rats.p','wb'))
            print(self.keyerrors)
            self.exportKeyErrors()
            
        time2 = time.time()
        elapsed = time2-time1
        minutes = int(elapsed/60)
        seconds = elapsed - (minutes*60)
        print("Total time for preprocessing: %d minutes %f seconds" % (minutes,seconds))
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
        import importlib
        importlib.reload(tc)
        #Test trainingSet methods
        time1 = time.time()
        ratList = self.rats.values()
        self.training = tc.trainingClass(ratList)
        pickle.dump(self.training,open('trainingClass.p','wb'))
        time2 = time.time()
        print("Time to initialize trainingClass: %f" % (time2-time1))
        return
        
    def reload(self):
        options = ['RatClasses','Rat & Training Classes','None']
        choice = gui.choicebox(msg='Reload earlier classes?',title='Reload Dialogue',choices=options)
        if choice == options[0]:
            self.rats = pickle.load(open('rats.p','rb'))
        elif choice == options[1]:
            self.rats = pickle.load(open('rats.p','rb'))
            self.training = pickle.load(open('trainingClass.p','rb'))
        elif choice == options[2]:
            self.addRat()
            self.addTrainClass()
    
    def getDirs(self):
        time1 = time.time()
        dirselect = filedialog.Directory()
        while True:
            # Can modify this to req. people type in directories instead?
            # Like in BSOID?
            d = dirselect.show(initialdir = "/Volumes/SharedX/Neuro-Leventhal/data/Skilled Reaching/DLC output",title = "Select rat folder")
            if not d: break
            self.dirs.append(d)
        Tk().withdraw()
        time2 = time.time()
        print("Time to save pathnames: %f" % (time2-time1))

def askParams():
    msg = "Enter parameter values:"
    title = "K-NN Classifier Parameters"
    fieldNames = ["PCA: # of dimensions","K-NN: # of neighbors","Fraction held out for test set"]
    fieldValues = []
    input = gui.multenterbox(msg,title, fieldNames)
    
    #Reloads dialog box if fields are empty
    while 1:
        if input is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if input[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break #No fields are empty
        input = gui.multenterbox(errmsg, title, fieldNames, input)
    #Cast first two values to int, third to float
    for i in range(len(input)):
        if (i == 0) or (i == 1):
            fieldValues.append(int(input[i]))
        else:
            fieldValues.append(float(input[i]))
    print("Reply was: %s" % str(fieldValues))
    return fieldValues
 
def initialAsk():
    msg = "Do you want to load an old classifier or train a new classifier?"
    title = "Start"
    fieldNames = ["Old","New"]
    response = ""
    response = gui.buttonbox(msg,title, fieldNames)
    return response

def askTrainClassifier(wrap):
    time1 = time.time()
    response = askParams()
    wrap.training.trainClassifier(response[0],response[1],response[2])
    time2 = time.time()
    print("Time to initialize train classifier: %f" % (time2-time1))

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
    if response == "Old":
        filename = selectClassifier()
        print(filename)
    elif response == "New":
        wrap = wrapper()
        #Try training classifier with pca = 7 dim, knn = 3 neighbors
        askTrainClassifier(wrap)
        

if __name__ == '__main__':
    main()
