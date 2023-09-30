import os
import random

path = "E:\steampower\steamapps\common\X-Plane 11\Custom Data\CIFP"
aim = "PI"
timeMax = 10  # 最多列举10个机场

isFirst = 0
airportList = os.listdir(path)
randonNum = random.randint(1, 1000)
if randonNum > 500:
    random.shuffle(airportList)
for i in airportList:
    if not i[:-4].isalpha():
        continue
    if isFirst == timeMax:
        break
    iPath = os.path.join(path, i)
    airport = open(iPath, "r")
    littleTimer = 0
    check = False
    for eachLine in airport:
        if littleTimer == 3:  # 一个机场最多列举3条
            break
        if ("," + aim + ",") in eachLine:
            print(i + "  " + eachLine, end='')
            check = True
            littleTimer += 1
    if check:
        isFirst += 1
        print()
    airport.close()
