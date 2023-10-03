import fixTransformFunc as fTF

# 程序只针对国区进行优化
filePath = "t1.txt"
airport = "ZUMY"
fixList, locList = fTF.rough_process(filePath)
locList = fTF.location_process(locList)
fTF.encoding(airport,filePath,fixList,locList)
