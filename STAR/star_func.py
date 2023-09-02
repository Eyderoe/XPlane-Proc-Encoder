import os


def master_caution(string):
    print("MasterCaution: ", end='')
    print(string)
    exit()


def multi_runway(head: str) -> list:
    """
    返回字符串列表
    :param head: 整个头部
    :return: 编码过后的字符串
    """
    # 算了不想搞花活 重新编码跑道 02L,02R -> 02B 不这样写应该也能识别？
    head = head.split(',')[4]
    if ' ' not in head:
        return [head]
    else:
        return head.split(' ')


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
    if information[0] != 'L':
        master_caution("not Arrival Procedure.")
    if not os.path.exists(path):
        master_caution("navData path not exist.")
    airport = information[1]
    area = information[2]
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
    # STAR专门部分，可以同时服务多条跑道
    if ' ' in information[4]:
        information[4] = information[4].split(' ')
    else:
        information[4] = [information[4]]
    for i in information[4]:
        if i not in runways:
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
    :param x: RF弧半径
    :param front: 整数部分位数
    :param back: 小数部分位数
    :return: 字符串
    """
    if x == "-" or x == "-1":
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


def trans_encoder(trans: list, base: str, timer: int, header: str) -> str:
    """
    接受程序并返回相应字符串，程序由主程序写入
    :param trans: trans段
    :param base: base段第一个点
    :param timer: 计数器，航点为第几段
    :param header: 头部
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = trans[timer] if timer != len(trans) else base  # 当前程序
    now = now.split(',')
    # 1.程序类型+编号
    key_word[0] = "STAR:" + digit_process(str(timer + 1), 2, 1)
    # 2.程序类型 4表示RNAV STAR Enroute Transition
    key_word[1] = '4'
    # 3.程序名
    proc_name = base.split(',')[1]
    lens = len(proc_name) + len(header[3])
    proc_name = proc_name[:-(lens - 6)] if lens > 6 else proc_name
    proc_name += header[3]
    key_word[2] = proc_name
    # 4.IAF点 Transition Identifier
    key_word[4] = now[1] # 这两个反了 就直接这样换了
    # 5.航路点 Fix Identifie
    key_word[3] = trans[0].split(',')[1]
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer != len(trans):
        key_word[8] = "E   "
    else:
        key_word[8] = "EE  "  # Essential Waypoint,End of Terminal Procedure Route Type
    if 'Y' in now and key_word[8][1] == ' ':
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
    key_word[35] = ' '  # PBN RNP or RNAV Visual Procedure, SBAS-based vertical navigation NOT Authorized
    key_word[36] = ' '  # GNSS Required
    key_word[37] = " ;"  # Procedure with Straight in Minimums
    return ','.join(key_word)


def base_encoder(base: list, timer: int, header: str, runway: str) -> str:
    """
    跟上面iaf_encoder一样的，偷懒
    :param base: fap点
    :param timer: 计数器，航点为第几段
    :param header: 头部
    :param runway: 跑道
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = base[timer]
    now = now.split(',')
    # 1.程序类型+编号
    key_word[0] = "STAR:" + digit_process(str(timer + 1), 2, 1)
    # 2.程序类型 5表示RNAV STAR or STAR Common Route
    key_word[1] = '5'
    # 3.程序名
    proc_name = base[0].split(',')[1]
    lens = len(proc_name) + len(header[3])
    proc_name = proc_name[:-(lens - 6)] if lens > 6 else proc_name
    proc_name += header[3]
    key_word[2]=proc_name
    # 4.不需要
    key_word[3] = "RW" + runway
    # 5.航路点 Fix Identifie
    key_word[4] = now[1]
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer != len(base) - 1:
        key_word[8] = "E   "
    else:
        key_word[8] = "EE  "  # Essential Waypoint,End of Terminal Procedure Route Type
    if 'Y' in now and key_word[8][1] == ' ':
        key_word[8] = key_word[8][0] + 'Y' + key_word[8][2:]
    if 'H'in now:
        key_word[8]=key_word[:-1]+'H'
    # 10.转向 RF航段
    is_rf = 'R' in now or 'L' in now
    if timer==0:
        is_rf=False
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
    if 'H' in now:
        loc = now.index('H')
        key_word[20] = digit_process(now[loc + 1], 3, 1)  # 出航航向，默认磁航
        if 'T' in now[loc + 2]:
            key_word[21] = 'T' + digit_process(now[loc + 2][1:], 3, 0)  # 长度为时间
        else:
            key_word[21] = digit_process(now[loc + 2], 3, 1)  # 长度为距离
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
    key_word[35] = ' '  # PBN RNP or RNAV Visual Procedure, SBAS-based vertical navigation NOT Authorized
    key_word[36] = ' '  # GNSS Required
    key_word[37] = " ;"  # Procedure with Straight in Minimums
    return ','.join(key_word)
