from tkinter import Tk
from tkinter import filedialog
import time
from Rat import Rat
from Session import Session
from Trial import Trial
import trainingClass as tc

class wrapperBullshit():
    def __init__(self):
        time1 = time.time()
        Tk().withdraw()
        dirselect = filedialog.Directory()
        self.dirs = []
        self.rats = {}
        self.training = 0
        while True:
            d = dirselect.show(initialdir = "/Volumes/SharedX/Neuro-Leventhal/data/Skilled Reaching/DLC output",title = "Select rat folder")
            if not d: break
            self.dirs.append(d)
        time2 = time.time()
        print("Time to save pathnames: %f" % (time2-time1))
         
    def addRat(self):
        ## Create object with dataset
        time1 = time.time()
        for i in range(len(self.dirs)):
            Rat1 = Rat(self.dirs[i])
            self.rats[Rat1.id] = Rat1
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
        time2 = time.time()
        print("Time to initialize trainingClass: %f" % (time2-time1))
        return
    
def main():
    wrap = wrapperBullshit()
    wrap.addRat()
    wrap.addTrainClass()
    #Try training classifier with pca = 7 dim, knn = 3 neighbors
    time1 = time.time()
    wrap.training.trainClassifier(7,3,.33)
    time2 = time.time()
    print("Time to initialize train classifier: %f" % (time2-time1))
    
if __name__ == '__main__':
    main()
