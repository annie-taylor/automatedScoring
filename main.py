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

class wrapper():
    def __init__(self):
        self.dirs = []
        self.rats = {}
        self.training = 0
        options = ['RatClasses','Rat & Training Classes','None']
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
        for i in range(len(self.dirs)):
            Rat1 = Rat(self.dirs[i])
            self.rats[Rat1.id] = Rat1
        pickle.dump(self.rats,open('rats.p','wb'))
        time2 = time.time()
        print("Time to initialize rat: %f" % (time2-time1))
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
    
    def getDirs():
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
    fieldValues = []  # we start with blanks for the values
    input = gui.multenterbox(msg,title, fieldNames)
    
    # make sure that none of the fields was left blank
    while 1:
        if input is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if input[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break # no problems found
        input = gui.multenterbox(errmsg, title, fieldNames, input)
    #Cast first two values to int, third to float
    for i in range(len(input)):
        if (i == 0) or (i == 1):
            fieldValues.append(int(input[i]))
        else:
            fieldValues.append(float(input[i]))
    print("Reply was: %s" % str(fieldValues))
    return fieldValues

    
def main():
    wrap = wrapper()
    #Try training classifier with pca = 7 dim, knn = 3 neighbors
    time1 = time.time()
    response = askParams()
    wrap.training.trainClassifier(response[0],response[1],response[2])
    time2 = time.time()
    print("Time to initialize train classifier: %f" % (time2-time1))
    
if __name__ == '__main__':
    main()
