# XPlane Procedure Encoder
方便Toliss在XP11中使用自定义的RNP-AR程序\
传统程序打点就好了。\
不完全遵循ARINC-424.18+规范，只在xp11的toliss下测试过。
## XP规范下的ARINC424.xlsx
显然/易得：解释了每个字段含义，具体参照ARINC-424标准。
## procConverter.py
将xp中的CIFP程序按字段切片存入csv表格中。\
读取：InRroc.dat 输出：OutProc.csv
## naipWaypointTrans
方法：复制naip中航路点坐标文件内容至txt文件\
所得到的文件应该和sample类似。\
通过转换得到符合earth_fix.dat规范的文本。[注意机场代码和区域代码]
