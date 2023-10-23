import os
import terminalFunc as func

# 1. 将xlsx文件转换为文本
# 2. 对程序进行校验
# 3. 对文件进行处理(添加序号，整理trans, ...)
# 4. 编码

# 读取并处理xlsx文件
xlsxPath = r"D:\Python项目\Terminal\存档\zhny.xlsx"
func.spawn_proc(xlsxPath)
while True:
    # 从.temp文件拿一个程序
    header, _content = func.get_proc(xlsxPath)
    if header == -1:
        break
    try:
        func.printf("{} / {}".format(func.clock - 1, func.procCount), False)
    except TypeError:  # 忘了 反正可能会报
        pass
    # 程序校验
    func.refer.set(header, _content)
    func.info_check(header[0], header[1])
    # 程序修改
    content = func.complex_process(header[0], _content)
    # 程序写入
    for i in range(len(content)):
        output = func.encode(content, i)
        func.write2file(xlsxPath, output)
    if False:
        func.write2file(xlsxPath, '')
os.remove(xlsxPath[:-4] + "temp")
