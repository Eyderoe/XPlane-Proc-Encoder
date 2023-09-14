import os


def master_caution(string):
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
    if information[0] != 'A':
        master_caution("not Approach Procedure.")
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


def iaf_encoder(iaf: list, fap: str, timer: int, header: str) -> str:
    """
    接受程序并返回相应字符串，程序由主程序写入
    :param iaf: iaf-fap点
    :param fap: fap点
    :param timer: 计数器，航点为第几段
    :param header: 头部
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = iaf[timer] if timer != len(iaf) else fap  # 当前程序
    now = now.split(',')
    # 1.程序类型+编号
    key_word[0] = "APPCH:" + digit_process(str(timer + 1), 2, 1)
    # 2.程序类型 A表示Approach Transition
    key_word[1] = 'A'
    # 3.程序名 程序R03-U显示为RNV03-U
    key_word[2] = "R" + header[4] + "-" + header[3]
    # 4.IAF点 Transition Identifier
    key_word[3] = iaf[0].split(',')[1]
    # 5.航路点 Fix Identifie
    key_word[4] = now[1]
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer == 0:
        key_word[8] = "E  B"  # Essential Waypoint,Intermediate Approach Fix
    elif timer == len(iaf):
        key_word[8] = "EE F"  # Essential Waypoint,End of Terminal Procedure Route Type,Final End Point Fix
    else:
        key_word[8] = "E   "  # Essential Waypoint
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
    key_word[35] = 'B'  # PBN RNP or RNAV Visual Procedure, SBAS-based vertical navigation NOT Authorized
    key_word[36] = 'P'  # GNSS Required
    key_word[37] = "S;"  # Procedure with Straight in Minimums
    return ','.join(key_word)


def fap_encoder(fap: list, timer: int, header: str) -> str:
    """
    跟上面iaf_encoder一样的，偷懒
    :param fap: fap点
    :param timer: 计数器，航点为第几段
    :param header: 头部
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = fap[timer]
    now = now.split(',')
    # 1.程序类型+编号
    step = 10 // (len(fap) - 1)
    if timer != len(fap) - 1:
        key_word[0] = "APPCH:" + digit_process(str(2 + step * 0.1 * timer), 2, 1)
    else:
        key_word[0] = "APPCH:030"
    # 2.程序类型 R表示Area Navigation (RNAV) Approach
    key_word[1] = 'R'
    # 3.程序名 程序R03-U显示为RNV03-U
    key_word[2] = "R" + header[4] + "-" + header[3]
    # 4.不需要
    # 5.航路点 Fix Identifie
    key_word[4] = "RW" + now[1] if timer == len(fap) - 1 else now[1]
    if timer == len(fap) - 1 and now[1] != header[4]:
        master_caution("runway disagree.")
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer == len(fap) - 1:
        key_word[8] = "GY M"  # Runway as Waypoint,Fly-Over Waypoint,Published Missed Approach Point Fix
    else:
        key_word[8] = "E   "  # Essential Waypoint
    if 'Y' in now and key_word[8][1] == ' ':
        key_word[8] = key_word[8][0] + 'Y' + key_word[8][2:]
    # 10.转向 RF航段
    is_rf = 'R' in now or 'L' in now
    if timer == 0:
        is_rf = False  # FAP点的rf航段编码应该在上面
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
    loc = fap[0].split(',').index('G')  # FAP点一定会标注下滑道
    key_word[28] = "    "
    if timer != 0:
        key_word[28] = '-' + digit_process(fap[0].split(',')[loc + 1], 1, 2)
    key_word[29] = "   "
    # 35.Multiple Code or TAA Sector Identifier
    # 36.37.38.
    key_word[35] = 'B'  # PBN RNP or RNAV Visual Procedure, SBAS-based vertical navigation NOT Authorized
    key_word[36] = 'P'  # GNSS Required
    key_word[37] = "S;"  # Procedure with Straight in Minimums
    return ','.join(key_word)


def holding_pattern(fly_all: list, loc: dict) -> tuple:
    """
    把盘旋作为单独一行重新加入。写的时候脑子昏昏的，应该差不多对的。hmm.不对
    :param fly_all: 所有段
    :param loc: 阶段存储字典
    :return: 返回更新后的形参
    """
    hold_loc = -1
    for i in range(len(fly_all)):
        j = fly_all[i].split(',')
        if 'H' in j:
            hold_loc = i
            break
    if hold_loc == -1:
        return fly_all, loc
    has_hold = fly_all[hold_loc]
    raw = has_hold.split(',')
    raw = ','.join(raw[:raw.index('H')]) + ',' + ','.join(raw[raw.index('H') + 3:])
    raw = raw[:-1] if raw[-1] == ',' else raw
    fly_all.insert(hold_loc, raw)
    loc['Q'][1] += 1
    # 简单的删去了盘旋点的rf段，按目前的读取规则来说应该没错？这样下面应该就不用改了
    # if 'R' in fly_all[hold_loc + 1].split(',') or 'L' in fly_all[hold_loc + 1].split(','):
    #     temp = fly_all[hold_loc + 1].split(',')
    #     temp.remove('R') if 'R' in temp else temp.remove('L')
    #     fly_all[hold_loc + 1] = ','.join(temp)
    # 高度限制和速度限制好像也要删 这代码没注释看着好头痛
    # 算了 对这一段合并下 屎山
    delete_list = ['R', 'L']
    for i in delete_list:
        if i in fly_all[hold_loc + 1].split(','):
            temp = fly_all[hold_loc + 1].split(',')
            temp.remove(i)
            fly_all[hold_loc + 1] = ','.join(temp)
    delete_list = ["A+", "A-", "A@", 'A~', 'S']
    for i in delete_list:
        if i in fly_all[hold_loc].split(','):
            temp = fly_all[hold_loc].split(',')
            temp.remove(i)
            fly_all[hold_loc] = ','.join(temp)
    return fly_all, loc


def ga_encoder(ga: list, timer: int, header: str) -> str:
    """
    偷懒
    :param ga: goAround段
    :param timer: 计数器，航点为第几段
    :param header: 头部
    """
    key_word = [' '] * 38
    header = header.split(',')
    now = ga[timer]
    now = now.split(',')
    # 1.程序类型+编号
    key_word[0] = "APPCH:" + digit_process(str(timer + 4), 2, 1)
    # 2.程序类型 R表示Area Navigation (RNAV) Approach
    key_word[1] = 'R'
    # 3.程序名 程序R03-U显示为RNV03-U
    key_word[2] = "R" + header[4] + "-" + header[3]
    # 4.不需要
    # 5.航路点 Fix Identifie
    key_word[4] = now[1]
    # 6.7.8.ICAO Code
    key_word[5] = header[2]  # 区域
    key_word[6] = 'P'  # Toliss对此参数不敏感,P-Airport，默认先寻找终端点后寻找航路点？
    key_word[7] = 'C'  # Terminal Waypoints
    # 9.类型Waypoint Description Code
    if timer == len(ga) - 1:
        key_word[8] = "EE  "  # Essential Waypoint,End of Terminal Procedure Route Type
    else:
        key_word[8] = "E   "  # Essential Waypoint
    if 'Y' in now and key_word[8][1] == ' ':
        key_word[8] = key_word[8][0] + 'Y' + key_word[8][2:]
    if 'H' in now:
        key_word[8] = key_word[8][0:3] + 'H'  # Essential Waypoint,End of Terminal Procedure Route Type,Holding Fix
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
        key_word[11] = "TF"
        key_word[17] = digit_process("-", 3, 3)
        key_word[21] = digit_process("-", 3, 1)
    # 11.RNP值
    key_word[10] = "302"  # 默认0.3NM
    # 19.20.21.22.
    key_word[18] = key_word[19] = key_word[20] = "    "
    if 'H' in now:
        key_word[11] = "HM"
        loc = now.index('H')
        key_word[20] = digit_process(now[loc + 1], 3, 1)  # 出航航向，默认磁航
        if 'T' in now[loc + 2]:
            key_word[21] = 'T' + digit_process(str(float(now[loc + 2][1:]) * 10), 3, 0)  # 长度为时间
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
    key_word[25] = "     "
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
    key_word[35] = 'B'  # PBN RNP or RNAV Visual Procedure, SBAS-based vertical navigation NOT Authorized
    key_word[36] = 'P'  # GNSS Required
    key_word[37] = "S;"  # Procedure with Straight in Minimums
    return ','.join(key_word)
