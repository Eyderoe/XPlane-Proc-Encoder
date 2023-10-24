import fixTransformFunc as fTF

# 程序只针对国区进行优化
filePath = "test.txt"
airport = "zumy"
fixList, locList = fTF.rough_process(filePath, 3)
locList = fTF.location_process(locList)
fTF.encoding(airport, filePath, fixList, locList)
