import os.path
from pandas import ExcelFile
from pandas import read_excel

"""
备忘：
注意TA和TL都是以英尺形式给出，digit_process可能要额外加入一个参数 √
APPR中的IF点问题编码F √
所有复制都没有考虑限制的问题艹(问题出在APPR STA) CTMD测试程序完美避开了bug √
4和26还有点问题 √
编码应该没问题看的是名称 重新把complex_process重构下应该就行了。sid移动后该删哪些也要写 √
sid过渡段标识也错了 √
上面两个弄完了要重新审一遍encode √
sid-star-appr也有问题 fuck √
CA(航向到高度) DF(直飞到航点) CF(航向到航点) √
RNP数值计算 √
重构pandas读取 有点问题又把第一行当表头读取了 √
CF(航向到航点)检查一下
有时间再把程序重新写写
进近最后不会显示锚定点 ??? 没有一点头猪
Cpp见证虔诚的信徒,Python诞生虚伪的屎山。 √
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


logPath = ""


def log_record(anything, enter=0):
    global logPath
    log = open(logPath, 'a+', encoding='utf-8')
    for i in range(enter):
        log.write('\n')
    log.write(str(anything))
    log.close()


class Info:
    # 仅结构体，仅存放需要二次处理的数据
    # 由于结构混乱，有些东西来不及printf就在这里报错了。应该？
    def __init__(self):
        self.rfFull = None
        self.transAltitude = None
        self.area = None
        self.typist = None
        self.haveTrans = None
        self.runway = None
        self.procName = None
        self.alfa = None

    def set(self, header: list, content: list):
        self.runway = [].copy()
        self.alfa = [].copy()
        if not os.path.isdir(header[1]):
            printf("不存在该路径{}".format(header[1]), True)
        if header[0].count(',') != 6:
            printf("程序头第一行错误", True)
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
            printf("缺失航段M", True)
        if len(self.alfa) != 0:
            self.haveTrans = True
        self.typist = header[0].split(',')[0]
        self.area = header[0].split(',')[2]
        # if self.typist == 'A' and len(self.procName) != 1: # 不判断了 现在
        #     printf("procedure name error", True)
        # if self.typist in ['L', 'S'] and len(self.procName) != 2:
        #     printf("procedure name error", True)
        self.transAltitude = header[0].split(',')[5]
        self.rfFull = bool(int(header[0].split(',')[6]))
        log_record("结构体检查通过",1)


namelist = []
clock = 1  # 读取目标，应读取第clock个程序(对应读取到第clock个_QED)
refer = Info()
procCount = 0
excelGlobal = None


def est_name(xlsx):
    """
    生成列表，xlsx文件中所有工作薄名称的列表
    """

    # est_name和get_name都重构了
    def rank(a):
        if "sid" in a.lower():
            return 1
        elif "star" in a.lower():
            return 2
        else:
            return 3

    global excelGlobal
    excelGlobal = ExcelFile(xlsx)
    db = read_excel(excelGlobal, sheet_name=None)
    temp = list(db.keys())
    log_record("所有工作表: " + str(temp) + "\n")
    global namelist
    for i in temp:
        if ("appr" in i.lower()) or ("sid" in i.lower()) or ("star" in i.lower()):
            namelist.append(i)
    namelist = sorted(namelist, key=rank)
    log_record("有效工作表: " + str(namelist))
    return namelist


def empty_process(mode: int, string: str):
    """
    1: 清除尾部空白
    2: 清除所有空白
    3: 返回是否空白
    4: 清除尾部和头部空白
    """
    if mode == 1:
        while string[-1] == ' ' or string[-1] == '\n':
            string = string[:-1]
        return string
    elif mode == 2:
        string = list(string)
        string = [i for i in string if (i != ' ') and (i != '\n')]
        return ''.join(string)
    elif mode == 3:
        for i in string:
            if (i != ' ') and (i != '\n'):
                return False
        else:
            return True
    elif mode == 4:
        while string[0] == ' ' or string[0] == '\n':
            string = string[1:]
        while string[-1] == ' ' or string[-1] == '\n':
            string = string[:-1]
        return string
    else:
        printf("illegal para.", True)


def trans_table(path: str, sheet_name: str):
    """
    并把某工作薄写入.temp
    """
    qed_check = False
    global excelGlobal
    table = read_excel(excelGlobal, sheet_name=sheet_name, header=None, dtype=str)
    table.fillna("null", inplace=True)
    temp_file = open(path[:-4] + "temp", 'a', encoding="utf-8")
    global procCount
    for i in range(table.shape[0]):
        trans_list = table.iloc[i, :].tolist()
        trans_list = [empty_process(4, i) for i in trans_list if i != "null"]
        if len(trans_list) == 0:
            continue
        temp_file.write(','.join(trans_list).upper() + '\n')  # 应该用不到大写吧 ？？？
        if "_QED" in ','.join(trans_list).upper():
            qed_check = True
            procCount += 1
    if not qed_check:
        printf("程序尾部缺失_QED", True)
    temp_file.close()


def spawn_proc(file_path):
    """
    创建文本化的xlsx文件.temp 和 所有程序存储文件.dat。
    建立工作表名称列表
    工作表写入临时文件
    """
    base_path, base_name = os.path.split(file_path)
    path_log = os.path.join(base_path, "log.md")
    path_all = file_path[:file_path.index('.')] + ".proc"
    path_temp = file_path[:file_path.index('.')] + ".temp"
    file_all = open(path_all, 'w', encoding="utf-8")
    file_all.close()
    path_all = open(path_temp, 'w', encoding="utf-8")
    path_all.close()
    global logPath
    logPath = path_log
    path_all = open(path_log, 'w', encoding="utf-8")
    path_all.close()

    sheet_list = est_name(file_path)

    for i in sheet_list:
        trans_table(file_path, i)
    log_record("\n读取到{}个程序".format(procCount))
    printf("加载程序数量: " + str(procCount), False)


def get_proc(vnv):
    temp_file = open(vnv[:-4] + "temp", 'r', encoding="utf-8")
    combine = []
    qed_time = 0  # 读取到qed的次数
    global clock
    for iLine in temp_file:
        if "_QED" in iLine:
            qed_time += 1
            if qed_time == clock:
                clock += 1
                break
            else:
                combine = []
                continue
        combine.append(empty_process(4, iLine))
    temp_file.close()
    if not combine:
        return -1, -1
    log_record("获取程序", 2)
    log_record("程序头部" + str(combine[:2]), 1)
    log_record("程序内容" + str(combine[2:]), 1)
    for i in combine[2:]:
        if os.path.isdir(i):
            printf("_QED存在缺失",True)
    return combine[:2].copy(), combine[2:].copy()


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
        try:
            if i_line[3] == airport:
                i_line[4] = empty_process(1, i_line[4])
                if i_line[4] == area:
                    break
                else:
                    printf("机场{}区域错误,可能是: ".format(airport) + i_line[4], True)
        except IndexError:
            pass  # 假如直接从little navmap里面导出就可能导致没有后面那几个
    earth_fix.close()
    # 检查跑道是否正确
    # * 有些环境下可能出现路径错误的情况 所以这样改
    path_list = ["GNS430", "navdata", "Airports.txt"]
    for i in path_list:
        path = os.path.join(path, i)
    if not os.path.exists(path):
        printf("路径{}不存在".format(path), True)
    airport_data = open(path, 'r')
    bottom = False
    runways = []  # 所有跑道
    for i_line in airport_data:
        if ',' + airport + ',' in i_line:
            bottom = True
            continue
        if bottom:
            if not empty_process(3, i_line):
                runways.append(i_line.split(',')[1])
            else:
                break
    if len(runways) == 0:
        print("<警戒!> 机场{}没有找到跑道".format(airport))
        return None
    airport_data.close()
    runway = refer.runway  # 程序跑道
    for i in runway:
        if i not in runways:
            printf("机场{}跑道错误,可能是: ".format(airport) + (lambda x: ','.join(x))(runways), True)


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


def complex_process(head: str, proc: list, del_rf=False):
    """
    1. 对乱序的大航段[trans,base,app,ga,...]进行重新排序
    2. 对程序进行修改[盘旋点,trans起点,...] 需要多复制一行
    3. 内部编码 N编号 C占位符 E跑道索引值 F进近初始点 _FI一段起始 _EN一段终止 _ME一段中间
    对程序有甚大的改变 分段print一下就会很显然
    """

    def del_words(string: str, words: list):  # 重写代码的乐趣 有病是吧？？？ 对于rf弧其实也可以写这样的一个函数
        """
        在string中删除words中的元素，并返回
        """
        string = string.split(',')
        for iWord in words:
            if iWord in string:
                string[string.index(iWord)] = 'C'
        return ','.join(string)

    proc = proc.copy()  # 我也不清楚这里需不要要 运算量小 无所谓的 感觉应该要，就像cv::Mat
    if del_rf:  # 禁用RF弧段
        for i in range(len(proc)):
            proc[i] = del_words(proc[i], ['R', 'L'])
    # * 重新排序，sid把m放前面，appr star把m放后面
    location = locate(proc)  # 注意位置变动
    base_loc = location.get('M', -1)  # 注意位置变动
    if base_loc == -1:
        printf("没有定义航段M", True)
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
        printf(_type + " 程序不符合:SID-S STAR-L APPR-A", True)
    location = locate(proc)
    # * 对程序进行修改
    # ** 复制阶段 越写越答辩 艹 星号代表第几级注释
    # *** 这里复制交叉点航段 艹 删了将近30行 心痛 动的地方哪些该删要删
    if _type == 'S':  # 离场 复制基础最后一个点到过渡第一个
        for iAlfa in refer.alfa:
            _temp = proc[location['M'][0] + location['M'][1] - 1].split(',')
            _temp[_temp.index("M")] = iAlfa
            proc.insert(location[iAlfa][0], ','.join(_temp))
            proc[location[iAlfa][0]] = del_words(proc[location[iAlfa][0]], ['S', 'R', 'L'])
            location = locate(proc)
    else:
        proc[location['M'][0]] = del_words(proc[location['M'][0]], ['L', 'R'])  # 速度限制不需要删？
        for iAlfa in refer.alfa:
            _loc = location[iAlfa][0] + location[iAlfa][1] - 1
            proc[_loc] = del_words(proc[_loc], ['G'])
    # *** 这里复制盘旋和star多跑道情况 只针对appr star的盘旋没有太大用
    if _type == 'A':
        if 'H' in proc[-1].split(','):
            proc.append(proc[-1])
            # print(proc)
            proc[-2] = del_words(proc[-2], ['H', 'S'])
            if "A+" in proc[-2].split(','):
                _temp = proc[-2].split(',')
                _temp[_temp.index("A+")] = "A@"
                proc[-2] = ','.join(_temp)
    if _type == 'L':
        for i in range(len(refer.runway) - 1):
            proc.extend(proc[location['M'][0]:location['M'][0] + location['M'][1]])
    location = locate(proc)
    # *** 离场的CA-DF CF
    if _type == 'S':
        for i in range(len(proc)):
            if "_CA" in proc[i].split(','):
                proc[i + 1] += ",_DF"
                proc[i + 1] = del_words(proc[i + 1], ['R', 'L'])
                proc[i] = del_words(proc[i], ['A+', 'A-', "A@", "A~"])
                j = proc[i].split(',')
                j.insert(j.index('_CA') + 2, "A+")
                proc[i] = ','.join(j)
            # if "CF" in proc[i]:  # 不对这个编码了
            #     proc[i] = del_words(proc[i], ["CF"])
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
        glide_slope = []
        try:
            glide_slope = fap_point[fap_point.index('G'):fap_point.index('G') + 2]
        except ValueError:
            printf("下滑道标识缺失-G", True)
        glide_slope = ',' + ','.join(glide_slope)
        runway_loc = -1
        for i in range(len(proc)):
            if 'V' in proc[i].split(','):
                runway_loc = i
        if runway_loc == -1:
            printf("跑道标识V丢失", True)
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
    if _type == 'A' and False:
        for i in proc:
            print(i)
    log_record("程序复杂处理" + str(proc), 1)
    return proc


def write2file(path, content):
    a = open(path[:-4] + "proc", 'a')
    a.write(content + '\n')


def encode(content, timer):
    """
    最终编码，按处理过的字符串编码 有些东西可以放在information里面处理，不想传入文件头
    """

    # 但 但我还不能在这里倒下 やるんだな いまここで
    def rnp_value(rnp: float):
        rnp = str(rnp)
        if '.' in rnp and len(rnp) == 3:  # 不想搞高级的算法，累
            return rnp[-1] + "02"
        if '.' not in rnp and len(rnp) == 1:
            return '0' + rnp + '0'
        else:
            printf("RNP值错误", True)

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
    log_record("当前航点: " + str(now), 1)
    key_word = [' '] * 38
    # 1.程序类型+编号
    if refer.typist == 'A':  # APPR
        try:
            key_word[0] = "APPCH:" + digit_process(now[now.index('N') + 1], 2, 1)
        except ValueError:
            printf(now, True)
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
        key_word[1] = '6' if now[0] != 'M' else '5'
    # 3.程序名
    if refer.typist == 'A':  # APPR
        if refer.procName == "-1":
            key_word[2] = 'R' + refer.runway[0]
        else:
            key_word[2] = 'R' + refer.runway[0] + '-' + refer.procName
    elif refer.typist == 'L':  # STAR
        _base_point = content[location['M'][0]].split(',')[1]
        _smaller = _base_point if len(_base_point) <= 4 else _base_point[:4]
        key_word[2] = _smaller + refer.procName if len(refer.procName) <= 2 else refer.procName
    else:  # SID
        _base_point = content[location['M'][0] + location['M'][1] - 1].split(',')[1]
        _smaller = _base_point if len(_base_point) <= 4 else _base_point[:4]
        key_word[2] = _smaller + refer.procName if len(refer.procName) <= 2 else refer.procName
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
        na = now[0]  # now alfa
        key_word[3] = "RW" + _nr if na == 'M' else content[location[na][0] + location[na][1] - 1].split(',')[1]
    # 5.航路点 Fix Identifie
    key_word[4] = now[1]
    if ('V' in now) and (now[1] in refer.runway):
        key_word[4] = "RW" + now[1]
    if ('V' in now) and (now[1] not in refer.runway) and (len(now[1]) <= 3):
        print("<警戒!> 考虑进近跑道错误")
    if refer.typist == 'S' and timer == 0:  # 打的第一个补丁
        key_word[4] = "RW" + now[1]
    # 6.7.8.ICAO Code
    key_word[5] = refer.area  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    if 'V' in now:
        key_word[7] = 'G'  # 3rd补丁
    # 9.类型Waypoint Description Code
    # ** 第一位
    key_word[8] = "E   "
    # ** 第二位
    if 'Y' in now:  # *** 芝士飞跃
        key_word[8] = "EY" + key_word[8][2:]
    if "_EN" in now:  # *** 芝士某一段结尾 改写了下
        key_word[8] = "EE" + key_word[8][2:]
    # ** 第三位
    if 'V' in content[timer - 1].split(',') and (timer > 1):  # *** 进近复飞点 没有后面那个好像不会报错？
        key_word[8] = key_word[8][0:2] + 'M' + key_word[8][-1]
    # ** 第四位
    if 'F' in now:  # *** 进近if点
        key_word[8] = key_word[8][:-1] + 'B'
    _temp = location[now[0]]  # *** 进近fap点
    if refer.typist == 'A' and now[0] != 'M' and False:  # 这是啥 不应该有的感觉 关掉了
        key_word[8] = key_word[8][:-1] + 'F'
    if 'H' in now:
        key_word[8] = key_word[8][:-1] + 'H'
    if refer.typist == 'A':
        if "_FI" in now:
            if 'M' not in now:
                if 'H' in now:
                    key_word[8] = key_word[8][:-1] + 'C'  # 应该不会出现这个？好久没管这一坨了
                else:
                    key_word[8] = key_word[8][:-1] + 'A'
            else:
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
    value = "302" if "_RNP" not in now else rnp_value(now[now.index("_RNP") + 1])
    if "_FI" not in now:
        key_word[10] = value
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
    if "_CA" in now:
        key_word[11] = "CA"
    if "_DF" in now:
        key_word[11] = "DF"
    if "_CF" in now:
        key_word[11] = "CF"
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
        try:
            digit_process(course, 3, 1)
        except ValueError:
            printf("检查-> 进近程序-跑道描述-V-航向", True)
    elif 'H' in now:
        course = now[now.index('H') + 2]
    else:
        course = '-'
    key_word[20] = digit_process(course, 3, 1)
    # 22.Route Distance/Holding Distance or Time (4)
    key_word[21] = "    "
    if 'V' in now:
        key_word[21] = "0010"  # 参照VNKT写的 意思是锚定点后1NM？ 我猜的
    elif 'H' in now:
        if 'T' not in now[now.index('H') + 3]:
            key_word[21] = digit_process(now[now.index('H') + 3], 3, 1)
        else:
            key_word[21] = "T" + digit_process(now[now.index('H') + 3][1:], 2, 1)
    if 'L' in now or 'R' in now:
        if refer.rfFull:
            try:
                key_word[21] = digit_process(now[now.index('R') + 3], 3, 1)
            except ValueError:
                key_word[21] = digit_process(now[now.index('L') + 3], 3, 1)
        else:
            key_word[21] = "0010"
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
    if 'G' in now and "_FI" not in now:
        key_word[28] = '-' + digit_process(now[now.index('G') + 1], 1, 2)
    else:
        key_word[28] = digit_process('-', 2, 2)
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

    # 下面全是补丁
    # 对CA航段 DF不需要处理
    if "_CA" in now:
        key_word[4:9] = [' ', ' ', ' ', ' ', "    "]
        key_word[20] = digit_process(now[now.index('_CA') + 1], 3, 1)
    if "_CF" in now:
        key_word[20] = digit_process(now[now.index('_CF') + 1], 3, 1)
    if "_CA" in now or "_CF" in now:
        if "_R" in now:
            key_word[9] = 'R'
        elif "_L" in now:
            key_word[9] = 'L'
        else:
            key_word[9] = ' '
    # 对锚定点不是跑道的进近程序
    if ('V' in now) and ("RW" not in key_word[4]):
        key_word[7] = 'C'
        key_word[8] = "EY M"
    log_record("当前航点编码"+'['+','.join(key_word)+']',1)
    return ','.join(key_word)  # 怎么是620 不是 520 艹
