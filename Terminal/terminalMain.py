import pandas as pd

import terminalFunc as func

# 1. 将xlsx文件转换为文本
# 2. 对程序进行校验
# 3. 对文件进行处理(添加序号，整理trans, ...)
# 4. 编码

# 将xlsx文件转换为文本
xlsxPath = "zuck.xlsx"
nameList = func.est_name(xlsxPath)
while True:
    iName = func.get_name()
    if iName == -1:
        break
    print(iName)
    df = pd.read_excel(xlsxPath, sheet_name=iName)
