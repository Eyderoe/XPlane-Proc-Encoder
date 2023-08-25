def cut(coordinate):  # N29°17'45.1"E094°19'21.1" 复用的代码，可读性很弱。中国坐标均为正，不需要考虑符号
    coordinate = coordinate.split('"')[:-1]  # ["N29°17'45.1", "E094°19'21.1"]
    feedback = []
    timer = 0
    for each in coordinate:
        timer += 1
        each = each[1:]  # 29°17'45.1
        nums = [each.split('°')[0], each.split('°')[1].split("'")[0],
                each.split('°')[1].split("'")[1]]  # ['29', '17', '45.1']
        num = 0
        for j in range(3):
            num += float(nums[j]) / pow(60, j)
        num = str(round(num, 9))
        # 小数位补齐
        smallNum = len(num.split('.')[1])
        if smallNum < 9:
            num += "0" * (9 - smallNum)
        # 整数位补齐
        bigNum = len(num.split('.')[0])
        need = 3 if timer == 1 else 5
        if bigNum < need:
            num = (need - bigNum) * " " + num
        feedback.append(num)
    return feedback


originFile = open('waypoint.txt', 'r', encoding="utf-8")
waypoint = []
longitude = []
latitude = []
airport = "ZUNZ"
area = "ZU"
code = "4608073"
# 对于N29°18'41.4"E094°20'51.8"这种格式的新文件。航路点一行坐标一行
for iLine in originFile:
    print(iLine)
    if iLine[-1] == '\n':
        iLine = iLine[:-1]
    if "°" not in iLine:
        waypoint.append(iLine)
    else:
        temp = cut(iLine)
        longitude.append(temp[1])
        latitude.append(temp[0])
num = len(waypoint)
# 补齐航路点
for j in range(len(waypoint)):
    ned = len(waypoint[j])
    if ned < 5:
        waypoint[j] = (5 - ned) * " " + waypoint[j]
transFile = open("transPoint.txt", 'w')
for i in range(num):
    transFile.write(latitude[i])
    transFile.write(longitude[i])
    transFile.write("  " + waypoint[i])
    transFile.write(" " + airport)
    transFile.write(" " + area)
    transFile.write(" " + code + '\n')
