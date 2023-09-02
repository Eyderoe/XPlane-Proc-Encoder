import appr_func as af

# 程序读取，校验
temp = open('APPR.txt', 'r', encoding='utf-8')
procedure = []
for iLine in temp:
    if af.not_empty(iLine):
        procedure.append(af.clean_tail(iLine))
temp.close()
info = procedure[0].split(',')
af.info_check(info, procedure[1])
# 程序分割
header = procedure[:2]
content = procedure[2:]
procedure.clear()
location = af.locate(content)
# ---写入iaf
outputFile = open(header[0].split(',')[1] + ".appr", 'w')
IAF = ['A', 'B', 'C', 'D', 'E']
for i in IAF:
    if i in location:
        for j in range(location[i][1] + 1):  # 加1是因为要写入fap点
            txt = af.iaf_encoder(content[location[i][0]:location[i][0] + location[i][1]], content[location['W'][0]], j,
                                 header[0])
            outputFile.write(txt + '\n')
# ---写入fap
if 'W' in location:
    for i in range(location['W'][1]):
        # af.fap_encoder和上面af.iaf_encoder一样的
        start = location['W'][0]
        length = location['W'][1]
        txt = af.fap_encoder(content[start:start + length], i, header[0])
        outputFile.write(txt + '\n')
# ---写入fap
content, location = af.holding_pattern(content, location)
if 'Q' in location:
    for i in range(location['Q'][1]):
        start = location['Q'][0]
        length = location['Q'][1]
        txt = af.ga_encoder(content[start:start + length], i, header[0])
        outputFile.write(txt + '\n')
outputFile.close()
