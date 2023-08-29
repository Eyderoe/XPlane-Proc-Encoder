import sid_func as df

# 程序读取，校验
temp = open('SID.txt', 'r', encoding='utf-8')
procedure = []
for iLine in temp:
    if df.not_empty(iLine):
        procedure.append(df.clean_tail(iLine))
temp.close()
info = procedure[0].split(',')
df.info_check(info, procedure[1])
# 程序分割
header = procedure[:2]
content = procedure[2:]
procedure.clear()
location = df.locate(content)
outputFile = open(header[0].split(',')[1] + ".add", 'w')
# ---写入基准 (无trans)
procName = content[location['Q'][1] - 1].split(',')[1]
procName = procName[:4] if len(procName) > 4 else procName
procName += header[0].split(',')[3]
for i in range(location['Q'][1]):
    txt = df.base_encoder(content[i], i, header[0], procName, location['Q'][1])
    outputFile.write(txt + '\n')
# ---写入trans
# 代码复用 写的就很快 
trans = ['A', 'B', 'C', 'E', 'F']
for i in trans:
    if i in location:  # 现在啊 现在是北京时间3:20 很好 很有精神
        start = location[i][0]
        end_plusOne = location[i][1] + location[i][0]
        for j in range(location[i][1] + 1):
            txt = df.trans_encoder(content[start:end_plusOne], content[location['Q'][1] - 1], j, header[0])
            outputFile.write(txt + '\n')  # 写完3:50 推到github上面去，Delta还是Echo hmm
outputFile.close()
