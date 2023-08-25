# XPlane Procedure Encoder
方便Toliss在XP11中使用自定义的RNP-AR程序\
传统程序打点就好了。\
不完全遵循ARINC-424.18+规范，只在xp11的toliss下进行过测试。
## XP规范下的ARINC424.xlsx
显然/易得：解释了每个字段含义，具体参照ARINC-424标准。
## procConverter.py
将xp中的CIFP程序按字段切片存入csv表格中。\
读取：InRroc.dat 输出：OutProc.csv
## waypointTrans
两种航路点转换：naip和little navmap
## APPR
进近程序及说明
## SID
离场程序及说明
## STAR
进场程序及说明