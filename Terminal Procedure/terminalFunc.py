import os.path
import pandas as pd

"""
备忘：
注意TA和TL都是以英尺形式给出，digit_process可能要额外加入一个参数
APPR中的IF点问题编码F √
所有复制都没有考虑限制的问题艹(去看好像又不会重复显示了,先mark一下)
4和26还有点问题
Cpp见证虔诚的信徒,Python诞生虚伪的屎山。
"""


def printf(string: str, exiting: bool):
    """
    输出警告和过程
    """
    if exiting:
        print("<警告!!!> " + string)
        input()
        exit()
    else:
        print("<进程> " + string)


class Info:
    # 仅结构体，仅存放需要二次处理的数据
    # 由于结构混乱，有些东西来不及printf就在这里报错了。应该？
    def __init__(self):
        self.runway = [].copy()
        self.alfa = [].copy()
        self.typist = None
        self.haveTrans = False
        self.procName = None
        self.area = None
        self.transAltitude = None
        self.rfFull = None

    def set(self, header: list, content: list):
        if header[0].count(',') != 6:
            printf("head argument disagree", True)
        self.runway = header[0].split(',')[4]
        self.procName = header[0].split(',')[3]
        if ' ' in self.runway:
            self.runway = self.runway.split(' ').copy()
        else:
            self.runway = [self.runway].copy()
        for i in content:
            ii = i.split(',')[0]
            if ii not in self.alfa:
                self.alfa.append(ii)
        try:
            self.alfa.remove('M')
        except ValueError:
            printf("missing M", True)
        if len(self.alfa) != 0:
            self.haveTrans = True
        self.typist = header[0].split(',')[0]
        self.area = header[0].split(',')[2]
        if self.typist == 'A' and len(self.procName) != 1:
            printf("procedure name error", True)
        if self.typist in ['L', 'S'] and len(self.procName) != 2:
            printf("procedure name error", True)
        self.transAltitude = header[0].split(',')[5]
        self.rfFull = bool(int(header[0].split(',')[6]))


namelist = []
isFirst = 0
refer = Info()


def est_name(xlsx):
    """
    生成列表，xlsx文件中所有工作薄名称的列表
    """
    db = pd.read_excel(xlsx, sheet_name=None)
    temp = list(db.keys())
    global namelist
    for i in temp:
        if ("appr" in i) or ("sid" in i) or ("star" in i):
            namelist.append(i)
    del db
    return namelist


def get_name():
    """
    按sid star appr的顺序获取工作薄名称
    """
    if len(namelist) == 0:
        return -1
    type_list = ['sid', 'star', "appr"]
    type_now = 3
    type_loc = -1
    for i in range(len(namelist)):
        for j in range(3):
            if (type_list[j] in namelist[i]) and j < type_now:
                type_loc = i
    temp = namelist[type_loc]
    namelist.pop(type_loc)
    return temp


def empty_process(mode: int, string: str):
    """
    1: 清除尾部空白
    2: 清除所有空白
    3: 返回是否空白
    """
    if mode == 1:
        while string[-1] == ' ' or string[-1] == '\n':
            string = string[:-1]
        return string
    elif mode == 2:
        string = list(string)
        string = [i for i in string if (i != ' ') and (i != '\n')]
        return ''.join(string)
    else:
        for i in string:
            if (i != ' ') and (i != '\n'):
                return False
        else:
            return True


def trans_table(table: pd.DataFrame, path: str):
    """
    创建某工作薄临时文件.temp 和 表格总体文件.dat。
    并把某工作薄写入.temp
    """
    table.fillna("null", inplace=True)
    path_all = path[:path.index('.')] + ".add"
    path_temp = path[:path.index('.')] + ".temp"
    global isFirst
    if isFirst == 0:
        txt_all = open(path_all, 'w')
        txt_all.close()
        isFirst += 1
    txt_temp = open(path_temp, 'w')
    for i in range(table.shape[0]):
        trans_list = table.iloc[i, :].tolist()
        trans_list = [i for i in trans_list if i != "null"]
        if len(trans_list) == 0:
            continue
        txt_temp.write(','.join(trans_list) + '\n')
    txt_temp.close()


def read_txt(file):
    """
    返回头部和程序部分
    """
    txt = open(file[:file.index('.')] + ".temp", 'r')
    head = [].copy()
    proc = [].copy()
    timer = 0
    for i in txt:
        timer += 1
        i = empty_process(1, i)
        if timer <= 2:
            head.append(i)
        else:
            proc.append(i)
    return head.copy(), proc.copy()


def info_check(multi_info: str, path: str):
    """
    检查信息[区域，机场]是否正确
    """
    # 以前的代码 不想看了 应该没有错的
    multi_info = multi_info.split(',')
    airport = multi_info[1]
    area = multi_info[2]
    # 检查机场区域是否正确
    earth_fix = open(os.path.join(path, "earth_fix.dat"), 'r')
    timer = 0
    for i_line in earth_fix:
        if timer < 2:
            timer += 1
            continue
        if empty_process(3, i_line):
            continue
        i_line = i_line.split(' ')
        if i_line[3] == airport:
            i_line[4] = empty_process(1, i_line[4])
            if i_line[4] == area:
                break
            else:
                printf("area disagree. might be " + i_line[4], True)
    earth_fix.close()
    # 检查跑道是否正确
    airport_data = open(os.path.join(path, "GNS430/navdata/Airports.txt"), 'r')
    bottom = False
    runways = []  # 所有跑道
    for i_line in airport_data:
        if airport in i_line:
            bottom = True
            continue
        if bottom:
            if not empty_process(3, i_line):
                runways.append(i_line.split(',')[1])
            else:
                break
    airport_data.close()
    runway = refer.runway  # 程序跑道
    for i in runway:
        if i not in runways:
            printf("runway disagree. might be " + (lambda x: ','.join(x))(runways), True)


def locate(listy: list) -> dict:
    """
    返回: (键-阶段 键值-各个阶段)
    :param listy: 程序列表
    :return: 字典
    """
    location = {}
    for i in range(len(listy)):
        mark = listy[i][0]
        if mark in location:
            location[mark][1] += 1
        else:
            location[mark] = [i, 1]
    return location


def complex_process(head: str, proc: list):
    """
    1. 对乱序的大航段[trans,base,app,ga,...]进行重新排序
    2. 对程序进行修改[盘旋点,trans起点,...] 需要多复制一行
    3. 内部编码 N编号 C占位符 E跑道索引值 F进近初始点 _FI一段起始 _EN一段终止 _ME一段中间
    对程序有甚大的改变 分段print一下就会很显然
    """
    proc = proc.copy()  # 我也不清楚这里需不要要 运算量小 无所谓的 感觉应该要，就像cv::Mat
    # * 重新排序，sid把m放前面，appr star把m放后面
    location = locate(proc)  # 注意位置变动
    base_loc = location.get('M', -1)  # 注意位置变动
    if base_loc == -1:
        printf("undefined M", True)
    _type = head.split(',')[0]
    if _type == 'S':  # sid M前置
        if base_loc[0] != 0:
            start = base_loc[0]
            end = start + base_loc[1]
            proc = proc[start:end] + proc[:start] + proc[end:]
    elif _type == 'L' or _type == 'A':  # appr star M后置
        _temp = list(location.values())
        max_start = (max(location, key=lambda x: x[0]))[0]
        if base_loc[0] != max_start:
            start = base_loc[0]
            end = start + base_loc[1]
            proc.extend(proc[start:end])
            proc = [proc[i] for i in range(len(proc)) if i <= start - 1 or i >= end]  # 你脑子有病是吧，不切片用推导式
    else:
        printf(_type + " NotMatch:SID-S STAR-L APPR-A", True)
    location = locate(proc)
    # * 对程序进行修改
    # ** 复制阶段 越写越答辩 艹 星号代表第几级注释
    # *** 这里复制基础航段
    for i in refer.alfa:
        if _type == 'S':  # SID 把M最后一个加到A前面
            last_of_base = proc[location['M'][0] + location['M'][1] - 1]
            proc.insert(location[i][0], last_of_base)
            proc[location[i][0]] = i + proc[location[i][0]][1:]
        elif _type == 'L' or _type == 'A':  # STAR APPR 把M第一个加到A后面
            if _type == 'A':
                fap_point = proc[location['M'][0]].split(',')
                try:
                    fap_point[fap_point.index('G')] = 'C'
                except ValueError:
                    printf("glide slope missing at fap", True)
                first_of_base = ','.join(fap_point)
            else:
                first_of_base = proc[location['M'][0]]
            proc.insert(location[i][0] + location[i][1], first_of_base)
            proc[location[i][0] + location[i][1]] = i + proc[location[i][0] + location[i][1]][1:]
        else:
            printf("unknown type", True)
        location = locate(proc)
    del_location = [location[i][0] for i in refer.alfa] if _type == 'S' else [location['M'][0]]
    for i in del_location:  # 主要是因为SID涉及多个 所以才会写成这么一坨 包括上面那一行 这一坨是写啥的？？？
        _a = proc[i].split(',')
        _rf = ['L', 'R']
        for j in _rf:
            if j in _a:
                _a[_a.index(j)] = 'C'
        proc[i] = ','.join(_a)
    # *** 这里复制盘旋和star多跑道情况 只针对appr star的盘旋没有太大用
    if _type == 'A':
        _a = proc[-1].split(',')
        if 'H' in _a:
            proc.append(proc[-1])
            _a[_a.index('H')] = 'C'
            proc[-2] = ','.join(_a)
    if _type == 'L':
        for i in range(len(refer.runway) - 1):
            proc.extend(proc[location['M'][0]:location['M'][0] + location['M'][1]])
    location = locate(proc)
    # ** 编码阶段
    # *** 对star多跑道编码 E
    if _type == 'L':
        _c = location['M'][0]
        _d = len(refer.runway)
        _e = 0
        timer = 0
        for i in range(location['M'][1]):
            timer += 1
            proc[_c] += ',E,'
            proc[_c] += str(_e)
            _c += 1
            if timer % (location['M'][1] / _d) == 0:
                _e += 1
    # *** 对APP无IF点情况编码 F 突然想起还有下滑道标识G
    if _type == 'A':
        # F
        for i in refer.alfa:
            check = False
            for j in range(location[i][0], location[i][0] + location[i][1]):
                if 'F' in proc[j].split(','):
                    check = True
                    break
            if not check:
                proc[location[i][0]] += ",F"
        # G
        fap_point = proc[location['M'][0]].split(',')
        glide_slope = fap_point[fap_point.index('G'):fap_point.index('G') + 2]
        glide_slope = ',' + ','.join(glide_slope)
        runway_loc = -1
        for i in range(len(proc)):
            if 'V' in proc[i].split(','):
                runway_loc = i
        if runway_loc == -1:
            printf("mark V (runway) missing", True)
        for i in range(location['M'][0], runway_loc + 1):
            proc[i] += glide_slope
    # *** 编号 N
    if _type == 'S' or _type == 'L':  # 对于sid和star
        _a = location.keys()
        for iAlfa in _a:
            start = location[iAlfa][0]
            for i in range(location[iAlfa][1]):
                j = i  # 本来这一坨是写给star的，后面发现sid好像也能用。评论是-好好好好好
                j = j % (location['M'][1] // len(refer.runway))
                proc[start + i] += (',N,' + str(j + 1))
    else:
        # 解决trans段的问题
        _a = refer.alfa
        for iAlfa in _a:
            start = location[iAlfa][0]
            for i in range(location[iAlfa][1]):
                proc[start + i] += (',N,' + str(i + 1))
        # 解决基础段问题 此处不适合写复杂的代码
        glide_s_start = location['M'][0]
        glide_s_end = -1
        g_around_start = -1
        g_around_end = -1
        for i in range(len(proc)):
            if 'V' in proc[i].split(','):  # 写到这里 我只能说去他喵的性能
                glide_s_end = i
        if (glide_s_end - glide_s_start + 1) != location['M'][1]:  # 说明啊 说明存在ga航段
            g_around_start = glide_s_end + 1
            g_around_end = location['M'][0] + location['M'][1] - 1  # 这里开始写ga
        for i in range(g_around_start, g_around_end + 1):
            proc[i] += (',N,' + str(i + 4 - g_around_start))
        step = 10 // (glide_s_end - glide_s_start)  # 这里开始写下降
        for i in range(glide_s_start, glide_s_end):
            proc[i] += (',N,' + str(round((i - glide_s_start) * step * 0.1 + 2, 2)))
        proc[glide_s_end] += ",N,3"
    # 遭不住了 国庆休息几天再写 自言自语的现象越来越重了 嘿嘿 我的小米
    # *** 编码 _FI一段起始 _EN一段终止 _ME一段中间
    _temp = refer.alfa.copy()
    _temp.append('M')
    for iAlfa in _temp:
        _start = location[iAlfa][0]
        _end = location[iAlfa][0] + location[iAlfa][1]
        _alfa = location[iAlfa][1] if iAlfa != 'M' else location[iAlfa][1] / len(refer.runway)
        for i in range(_start, _end):
            j = (i - _start) % _alfa
            if j == 0:
                proc[i] += ",_FI"
            elif j == (_alfa - 1):
                proc[i] += ",_EN"
            else:
                proc[i] += ",_ME"
    return proc


def write2file(path, content):
    a = open(path[:-4] + "add", 'a')
    a.write(content + '\n')


def encode(content, timer):
    """
    最终编码，按处理过的字符串编码 有些东西可以放在information里面处理，不想传入文件头
    """

    # 但 但我还不能在这里倒下 やるんだな いまここで

    def digit_process(x: str, front: int, back: int) -> str:
        """
        返回对应字符串
        :param x: 字符串形式的数字
        :param front: 整数部分位数
        :param back: 小数部分位数
        :return: 字符串
        """
        if x == "-" or x == "-1":
            return " " * (front + back)
        if "FL" in x:  # 高度限制可以用高度层
            return "FL" + digit_process(x[2:], 3, 0)
        x = str(float(x))
        for o in range(front - len(x[:x.index('.')])):
            x = '0' + x
        for o in range(back - len(x[x.index('.') + 1:])):
            x += '0'
        x = x[:x.index('.')] + x[x.index('.') + 1:]
        if len(x) > (front + back):
            x = x[:-(len(x) - (front + back))]
        return x

    location = locate(content)
    now = content[timer].split(',')
    key_word = [' '] * 38
    # 1.程序类型+编号
    if refer.typist == 'A':  # APPR
        key_word[0] = "APPCH:" + digit_process(now[now.index('N') + 1], 2, 1)
    elif refer.typist == 'L':  # STAR
        key_word[0] = "STAR:" + digit_process(now[now.index('N') + 1], 2, 1)
    else:  # SID
        key_word[0] = "SID:" + digit_process(now[now.index('N') + 1], 2, 1)
    # 2.程序类型
    if refer.typist == 'A':  # APPR
        key_word[1] = 'A' if now[0] != 'M' else 'R'
    elif refer.typist == 'L':  # STAR
        key_word[1] = '4' if now[0] != 'M' else '5'
    else:  # SID
        key_word[1] = '5' if now[0] != 'M' else '6'
    # 3.程序名
    if refer.typist == 'A':  # APPR
        key_word[2] = 'R' + refer.runway[0] + '-' + refer.procName
    elif refer.typist == 'L':  # STAR
        _base_point = content[location['M'][0]].split(',')[1]
        _smaller = _base_point if len(_base_point) <= 4 else _base_point[:4]
        key_word[2] = _smaller + refer.procName
    else:  # SID
        _base_point = content[location['M'][0] + location['M'][1] - 1].split(',')[1]
        _smaller = _base_point if len(_base_point) <= 4 else _base_point[:4]
        key_word[2] = _smaller + refer.procName
    # 4.IAF点 Transition Identifier
    if refer.typist == 'A':  # APPR
        key_word[3] = ' ' if now[0] == 'M' else content[location[now[0]][0]].split(',')[1]
    elif refer.typist == 'L' and now[0] != 'M':  # STAR 过渡
        key_word[3] = content[location[now[0]][0]].split(',')[1]
    elif refer.typist == 'L' and now[0] == 'M':  # STAR 基础
        runway_num = int(now[now.index('E') + 1])
        key_word[3] = "RW" + refer.runway[runway_num]
    else:  # SID
        _nr = refer.runway[0]
        key_word[3] = "RW" + _nr if now[0] == 'M' else content[location['M'][0] + location['M'][1] - 1].split(',')[1]
    # 5.航路点 Fix Identifie
    key_word[4] = now[1] if 'V' not in now else "RW" + now[1]
    if refer.typist == 'S' and timer == 0:  # 打的第一个补丁
        key_word[4] = "RW" + now[1]
    # 6.7.8.ICAO Code
    key_word[5] = refer.area  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    # ** 第一位
    key_word[8] = "E   "
    # ** 第二位
    if 'Y' in now:  # *** 芝士飞跃
        key_word[8] = "EY" + key_word[8][2:]
    if "_EN" in now:  # *** 芝士某一段结尾 改写了下
        key_word[8] = "EE" + key_word[8][2:]
    # ** 第四位
    if 'F' in now:  # *** 进近if点
        key_word[8] = key_word[8][:-1] + 'B'
    _temp = location[now[0]]  # *** 进近fap点
    if refer.typist == 'A' and now[0] != 'M' and timer == _temp[0] + _temp[1] - 1:
        key_word[8] = key_word[8][:-1] + 'F'
    # ** 全局
    if 'V' in now:
        key_word[8] = "GY M"
    # 10.转向 RF航段
    if 'R' in now or 'U' in now:
        key_word[9] = 'R'
    elif 'L' in now or 'I' in now:
        key_word[9] = 'L'
    else:
        key_word[9] = ' '
    # 11.RNP值 遭不住了 再把上面那个函数改一改增加类型
    if "_FI" not in now:
        key_word[10] = "302"
    else:
        key_word[10] = "   "
    # 12.航段类型Path and Termination (2)
    if "_FI" in now:
        key_word[11] = "IF"
    else:
        key_word[11] = "TF"
    if 'R' in now or 'L' in now:
        key_word[11] = "RF"
    if refer.typist == 'A' and 'H' in now:
        key_word[11] = "HM"
    # 13.14.15.16.17.
    pass
    # 18.ARC Radius (6)
    if 'R' in now or 'L' in now:
        try:
            _loc = now.index('R') + 1
        except ValueError:
            _loc = now.index('L') + 1
        key_word[17] = digit_process(now[_loc], 3, 3)
    else:
        key_word[17] = digit_process('-', 3, 3)
    # 19.20.
    key_word[18] = key_word[19] = "    "
    # 21.Magnetic Course (4)
    if 'V' in now:
        course = now[now.index('V') + 1]
    elif 'H' in now:
        course = now[now.index('H') + 2]
    else:
        course = '-'
    key_word[20] = digit_process(course, 3, 1)
    # 22.Route Distance/Holding Distance or Time (4)
    if 'V' in now:
        key_word[21] = "0010"  # 参照VNKT写的 意思是锚定点后1NM？ 我猜的
    elif "H" in now:
        if 'T' not in now[now.index('H') + 3]:
            key_word[21] = digit_process(now[now.index('H') + 3], 3, 1)
        else:
            key_word[21] = "T" + digit_process(now[now.index('H') + 3][1:], 2, 1)
    # 23.24.25.高度限制
    h_limit = [["A+", '+'], ["A-", '-'], ["A@", ' '], ["A~", 'B']]
    for i in h_limit:
        if i[0] in now:
            key_word[22] = i[1]
            loc = now.index(i[0])
            key_word[23] = digit_process(now[loc + 1], 5, 0)
            if i[0] == "A~":
                key_word[24] = digit_process(now[loc + 2], 5, 0)
            else:
                key_word[24] = "     "
            break
        else:
            key_word[23] = key_word[24] = "     "
    # 26.Transition Altitude 过渡高度
    if "_FI" in now:
        if "FL" in refer.transAltitude:
            key_word[25] = digit_process(str(int(refer.transAltitude[2:]) * 100), 5, 0)
        else:
            key_word[25] = digit_process(refer.transAltitude, 5, 0)
    else:
        key_word[25] = digit_process('-', 5, 0)
    # 27.28.速度限制
    if 'S' in now:
        key_word[26] = '-'
        key_word[27] = now[now.index('S') + 1]
    else:
        key_word[27] = "   "
    # 29.30.下滑道和 Vertical Scale Factor(424-18中没有这个)
    if 'G' in now:
        key_word[28] = digit_process(now[now.index('G') + 1], 1, 2)
    else:
        key_word[28] = digit_process('-', 1, 2)
    key_word[29] = "   "
    # 31.32.33.34 RF段中心定位点
    if refer.rfFull and ('R' in now or 'L' in now):
        try:
            key_word[30] = now[now.index('L') + 2]
        except ValueError:
            key_word[30] = now[now.index('R') + 2]
        key_word[31] = refer.area
        key_word[32] = 'P'
        key_word[33] = 'C'
    if (not refer.rfFull) and ('R' in now or 'L' in now):
        key_word[30] = "KTC32"
        key_word[31] = "VN"
        key_word[32] = 'P'
        key_word[33] = 'C'
    # 35.Multiple Code or TAA Sector Identifier
    # 36.37.38.
    if refer.typist != 'A':
        key_word[35] = key_word[36] = ' '
        key_word[37] = " ;"
    else:
        key_word[35] = 'B'
        key_word[36] = 'P'
        key_word[37] = "S;"
    return ','.join(key_word)