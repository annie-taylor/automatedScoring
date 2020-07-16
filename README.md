# automatedScoring

**Readme is no longer up to date, does not reflect changes made on 7/15/20**

To run automatedScoring program in command line, follow the steps below (only need to perform step 1 when first downloading program):

1. git clone https://github.com/annie-taylor/automatedScoring
2. cd automatedScoring
3. python3 main.py

After (3) a python window will pop-up asking you if you want to reload class data and providing three options:
    (1) RatClasses
    (2) Rat and Training Classes
    (3) None

    If you select (1), the program will reload a file containing previously constructed 'rat' objects (this saves a lot of time if you have already run the program once, you will not have to wait to reupload rat data or preprocess every time). Then the program will create a trainingClass object from the available rats.

    If you select (2) the program will reload files containing the 'rat' objects and 'trainingClass' objects, rather than forcing you to create them.

    If you select (3), a python window will pop-up allowing you to select any number of folders for analysis. These should be organized as Rat folders from DLC output, otherwise it may not work. Continue selecting folders until you have selected as many as you want (must select one folder at a time), hit cancel once you are finished. The program will create rat objects based on the selected folders and perform preprocessing. Then the program will create a trainingClass object from the available rats.

The program will then ask for parameters for the PCA and kNN classifier. You must enter (1) the final number of dimensions needed for PCA (integer), (2) the number of nearest neighbors to use in the classifier (integer), and (3) the fraction of kinematics data to be saved for the test set (decimal/fraction).

**Note: Current runtime is ~5-10 minutes for a single rat including all steps.**
