import  os

path = os.getcwd()
files = os.listdir(path)
pickles = []
for file in files:
    if file.endswith('.p'):
        pickles.append(file)

for pickle in pickles:
    picklepath = path + pickle
    os.remove(pickle)

