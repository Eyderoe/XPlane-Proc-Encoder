import os

import pandas as pd

import terminalFunc as func

# 1. 将xlsx文件转换为文本
# 2. 对程序进行校验
# 3. 对文件进行处理(添加序号，整理trans, ...)
# 4. 编码

# 读取并处理xlsx文件
xlsxPath = "D:\Python项目\Terminal\存档\zuls.xlsx"
nameList = func.est_name(xlsxPath)
while True:
    iName = func.get_name()
    if iName == -1:
        break
    func.printf(iName, False)
    df = pd.read_excel(xlsxPath, sheet_name=iName, header=None, dtype=str)
    # 表格转换文本
    func.trans_table(df, xlsxPath)
    header, _content = func.read_txt(xlsxPath)
    func.refer.set(header, _content)
    # 程序校验
    func.info_check(header[0], header[1])
    # 程序修改
    content = func.complex_process(header[0], _content)
    # 程序写入
    for i in range(len(content)):
        output = func.encode(content, i)
        func.write2file(xlsxPath, output)
    func.write2file(xlsxPath, '')
os.remove(xlsxPath[:-4] + "temp")
