import pandas as pd
import math

table = pd.read_excel("APPR.xlsx", header=None)
output = open("APPR.txt", 'w')
for i in range(table.shape[0]):
    transList = table.iloc[i, :].tolist()
    transList = [x for x in transList if not isinstance(x, float) or not math.isnan(x)]
    noNumpy = []
    for j in transList:
        noNumpy.append(str(j))
    output.write(','.join(noNumpy) + '\n')
output.close()
