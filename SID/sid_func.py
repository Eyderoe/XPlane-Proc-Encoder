import os


def master_caution(string):
    """
    简单的丢出一个主警戒并结束程序
    :param string:警戒内容
    """
    print("MasterCaution: ", end='')
    print(string)
    exit()


def not_empty(string: str) -> bool:
    """
    检查字符串不为空
    :param string: 字符串
    :return: 是/否
    """
    for i in string:
        if i != ' ' and i != '\n':
            return True
    return False


def clean_tail(string: str) -> str:
    """
    去掉字符串末尾空字符
    :param string: 字符串
    :return: 字符串
    """
    while string[-1] == ' ' or string[-1] == '\n':
        string = string[:-1]
    return string


def info_check(information: list, path: str):
    """
    检查信息[程序类型，区域，机场]是否正确
    :param information: 基本信息列表
    :param path: 导航数据路径
    """
    if path[-1] == '\\':
        path = path[:-1]
    if information[0] != 'S':
        master_caution("not Departure Procedure.")
    if not os.path.exists(path):
        master_caution("navData path not exist.")
    airport = information[1]
    area = information[2]
    runway = information[4]
    # 检查机场区域是否正确
    earth_fix = open(path + "\\earth_fix.dat", 'r')
    timer = 0
    for i_line in earth_fix:
        if timer < 2:
            timer += 1
            continue
        if not not_empty(i_line):
            continue
        i_line = i_line.split(' ')
        while '' in i_line:
            i_line.remove('')
        if i_line[3] == airport:
            i_line[4] = clean_tail(i_line[4])
            if i_line[4] == area:
                break
            else:
                master_caution("area disagree. might be " + i_line[4])
    earth_fix.close()
    # 检查跑道是否正确
    airport_data = open(path + "\\GNS430\\navdata\\Airports.txt", 'r')
    bottom = False
    runways = []
    for i_line in airport_data:
        if airport in i_line:
            bottom = True
            continue
        if bottom:
            if not_empty(i_line):
                runways.append(i_line.split(',')[1])
            else:
                break
    airport_data.close()
    if runway not in runways:
        if not runways == []:
            master_caution("runway disagree. might be " + (lambda x: ','.join(x))(runways))


def locate(listy: list) -> dict:
    """
    返回键-阶段 键值-各个阶段[起始,长度(不包含VIP)]
    :param listy: 程序列表
    :return: 字典：
    """
    location = {}
    for i in range(len(listy)):
        mark = listy[i][0]
        if mark in location:
            location[mark][1] += 1
        else:
            location[mark] = [i, 1]
    return location


def digit_process(x: str, front: int, back: int) -> str:
    """
    返回对应字符串
    :param x: 数字,int这些其实也可以传入
    :param front: 整数部分位数
    :param back: 小数部分位数
    :return: 字符串
    """
    if x == "-":
        return " " * (front + back)
    if "FL" in x:  # 高度限制可以用高度层
        return "FL" + digit_process(x[2:], 3, 0)
    x = str(float(x))
    for i in range(front - len(x[:x.index('.')])):
        x = '0' + x
    for i in range(back - len(x[x.index('.') + 1:])):
        x += '0'
    x = x[:x.index('.')] + x[x.index('.') + 1:]
    if len(x) > (front + back):
        x = x[:-(len(x) - (front + back))]
    return x


def base_encoder(waypoint: str, timer: int, header: str, name: str, num: int) -> str:
    """
    接受程序并返回相应字符串，程序由主程序写入
    :param waypoint: 单个点，不明白为什么之前传的是整个大航段 ？ 这里的程序起始肯定是跑道 笑 跑道放在header里面的,艹 笨蛋
    :param timer: 计数器，航点为第几段
    :param header: 头部
    :param name: 程序名
    :param num: 整个段的长度，tmd终于知道为什么传的是整个大航段
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = waypoint.split(',')
    # 1.程序类型+编号
    key_word[0] = "SID:" + digit_process(str(timer + 1), 2, 1)
    # 2.程序类型 5表示RNAV SID or SID Common Route
    key_word[1] = '5'
    # 3.程序名
    key_word[2] = name
    # 4.IAF点 Transition Identifier
    key_word[3] = "RW" + header[4]
    # 5.航路点 Fix Identifie
    key_word[4] = now[1] if timer != 0 else "RW" + now[1]
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer == num - 1:
        key_word[8] = "EE  "  # Essential Waypoint,End of Terminal Procedure Route Type
    else:
        key_word[8] = "E   "  # Essential Waypoint,Intermediate Approach Fix
    if 'Y' in now and key_word[8][1] == ' ':  # 这一坨可能有用？
        key_word[8] = key_word[8][0] + 'Y' + key_word[8][2:]
    # 10.转向 RF航段
    is_rf = 'R' in now or 'L' in now
    if is_rf:
        loc = now.index('R') if 'R' in now else now.index('L')
        key_word[9] = now[loc]  # 转向
        key_word[11] = "RF"  # 航段类型
        key_word[17] = digit_process(now[loc + 1], 3, 3)  # rf弧半径。关键字段，Toliss对距离中心点不敏感
        if header[6] == '1':
            key_word[21] = digit_process(now[loc + 3], 3, 1)  # rf弧距离
            key_word[30] = now[loc + 2]  # rf弧中心点
        else:  # 缩写因为toliss好像是用半径进行计算的，这两个不重要
            key_word[21] = digit_process(str(1), 3, 1)
            key_word[30] = "KTC32"
        key_word[31] = header[2]  # 区域
        key_word[32] = 'P'  # Airport
        key_word[33] = 'C'  # Terminal Waypoints
    else:
        key_word[11] = "IF" if timer == 0 else "TF"
        key_word[17] = digit_process("-", 3, 3)
        key_word[21] = digit_process("-", 3, 1)
    # 11.RNP值
    key_word[10] = "302" if timer != 0 else "   "  # 默认0.3NM
    # 19.20.21.22.
    key_word[18] = key_word[19] = key_word[20] = "    "
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
    key_word[25] = digit_process(header[5], 5, 0) if timer == 0 else "     "
    # 27.28.速度限制
    if 'S' in now:
        key_word[26] = '-'
        key_word[27] = now[now.index('S') + 1]
    else:
        key_word[27] = "   "
    # 29.30.下滑道和 Vertical Scale Factor(424-18中没有这个)
    key_word[28] = "    "
    key_word[29] = "   "
    # 35.Multiple Code or TAA Sector Identifier
    # 36.37.38.
    key_word[35] = key_word[36] = ' '
    key_word[37] = " ;"
    return ','.join(key_word)


def trans_encoder(trans: list, base_last: str, timer: int, header: str) -> str:
    """
    接受程序并返回相应字符串，程序由主程序写入
    :param trans: trans段
    :param base_last: 基段最后一个点
    :param timer: 计数器，航点为第几段
    :param header: 头部
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = base_last if timer == 0 else trans[timer - 1]
    now = now.split(',')
    # 1.程序类型+编号
    key_word[0] = "SID:" + digit_process(str(timer + 1), 2, 1)
    # 2.程序类型 6表示RNAV SID Enroute Transition
    key_word[1] = '6'
    # 3.程序名
    final_point = trans[-1].split(',')[1]
    final_point = final_point if len(final_point) <= 4 else final_point[:4]
    key_word[2] = final_point + header[3]
    # 4.IAF点 Transition Identifier
    key_word[3] = trans[-1].split(',')[1]
    # 5.航路点 Fix Identifie
    key_word[4] = now[1]
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer == len(trans):
        key_word[8] = "EE  "  # Essential Waypoint,End of Terminal Procedure Route Type
    else:
        key_word[8] = "E   "  # Essential Waypoint,Intermediate Approach Fix
    if 'Y' in now and key_word[8][1] == ' ':  # 这一坨可能有用？
        key_word[8] = key_word[8][0] + 'Y' + key_word[8][2:]
    # 10.转向 RF航段
    is_rf = 'R' in now or 'L' in now
    if timer == 0:
        is_rf = False
    if is_rf:
        loc = now.index('R') if 'R' in now else now.index('L')
        key_word[9] = now[loc]  # 转向
        key_word[11] = "RF"  # 航段类型
        key_word[17] = digit_process(now[loc + 1], 3, 3)  # rf弧半径。关键字段，Toliss对距离中心点不敏感
        if header[6] == '1':
            key_word[21] = digit_process(now[loc + 3], 3, 1)  # rf弧距离
            key_word[30] = now[loc + 2]  # rf弧中心点
        else:
            key_word[21] = digit_process(str(1), 3, 1)
            key_word[30] = "KTC32"
        key_word[31] = header[2]  # 区域
        key_word[32] = 'P'  # Airport
        key_word[33] = 'C'  # Terminal Waypoints
    else:
        key_word[11] = "IF" if timer == 0 else "TF"
        key_word[17] = digit_process("-", 3, 3)
        key_word[21] = digit_process("-", 3, 1)
    # 11.RNP值
    key_word[10] = "302" if timer != 0 else "   "  # 默认0.3NM
    # 19.20.21.22.
    key_word[18] = key_word[19] = key_word[20] = "    "
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
    # 26.Transition Altitude?过渡高度层
    key_word[25] = digit_process(header[5], 5, 0) if timer == 0 else "     "
    # 27.28.速度限制
    if 'S' in now:
        key_word[26] = '-'
        key_word[27] = now[now.index('S') + 1]
    else:
        key_word[27] = "   "
    # 29.30.下滑道和 Vertical Scale Factor(424-18中没有这个)
    key_word[28] = "    "
    key_word[29] = "   "
    # 35.Multiple Code or TAA Sector Identifier
    # 36.37.38.
    key_word[35] = ' '
    key_word[36] = ' '
    key_word[37] = " ;"
    return ','.join(key_word)
