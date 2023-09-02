import star_func as yf

# 程序读取，校验
temp = open('STAR.txt', 'r', encoding='utf-8')
procedure = []
for iLine in temp:
    if yf.not_empty(iLine):
        procedure.append(yf.clean_tail(iLine))
temp.close()
info = procedure[0].split(',')
yf.info_check(info, procedure[1])
# 程序分割
header = procedure[:2]
content = procedure[2:]
procedure.clear()
location = yf.locate(content)
outputFile = open(header[0].split(',')[1] + ".star", 'w')
# ---写入trans
trans = ['A', 'B', 'C', 'D', 'E']
for i in trans:
    if i in location:
        start = location[i][0]
        length = location[i][1]
        for j in range(length + 1):
            txt = yf.trans_encoder(content[start:start + length], content[location['F'][0]], j, header[0])
            outputFile.write(txt + '\n')
# ---写入base
runway = yf.multi_runway(header[0])
for iRW in runway:
    for i in range(location['F'][1]):
        start = location['F'][0]
        length = location['F'][1]
        txt = yf.base_encoder(content[start:start + length], i, header[0], iRW)
        outputFile.write(txt + '\n')

outputFile.close()
