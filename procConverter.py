import pandas as pd

inputFile = open("InProc.dat", 'r')
outputFile = pd.DataFrame()
timer = 0
for i in inputFile:
    i = i[:-1]
    i = i.split(',')
    outputFile[timer] = pd.Series(i)
    timer += 1
outputFile.to_csv("OutProc.csv", index=False, header=False)
