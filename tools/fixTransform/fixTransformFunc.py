def rough_process(txt: str):
    def not_empty(a):
        for i in a:
            if i != '\n' and i != ' ':
                return True
        else:
            return False

    def clean_head_tail(a: str):
        while a[0] == ' ' or a[0] == '\n':
            a = a[1:]
        while a[-1] == ' ' or a[-1] == '\n':
            a = a[:-1]
        return a

    _txt = open(txt, 'r', encoding="utf-8")
    fix_list = []
    location_list = []
    cat = 1  # 0整齐 1杂乱
    txt = _txt.read()
    for i in txt:
        if '°' in i:
            cat = 0
            break
    _txt.close()
    if cat == 0:
        txt = txt.split('\n')
        txt = [i for i in txt if not_empty(i)]
        for i in range(len(txt)):
            if i < len(txt) / 2:
                fix_list.append(clean_head_tail(txt[i]))
            else:
                location_list.append(clean_head_tail(txt[i]))
    else:
        txt = txt.replace('\n', ' ').split(' ')
        txt = [i for i in txt if i != '']
        for i in range(len(txt)):
            if i % 2 == 0:
                fix_list.append(txt[i])
            else:
                location_list.append(txt[i])
    return fix_list, location_list


def location_process(loc_list: list):
    def cut(string: str, sep: list) -> list:
        baka = ['']
        timer = 0
        for iChar in string:
            if iChar in sep:
                baka.append('')
                timer += 1
            else:
                baka[timer] += iChar
        baka = [float(i) for i in baka if i != '']
        return baka.copy()

    back = []
    timer = -1
    for i in loc_list:
        if '°' in i:  # N29°18'45.1"E092°19'45.4" 度分秒
            mode = 0
        elif '.' in i:  # N3226.0E10456.0 度分？
            mode = 1
        else:  # N312047E1044856 度分秒？
            mode = 2
        if mode == 0:  # 感觉有点像脱了裤子放屁 算了
            i = cut(i, ['N', 'E', '°', '\'', '\"'])
            for j in range(6):
                k = j % 3
                if k == 0:
                    back.append(0)
                    timer += 1
                back[timer] += i[j] / pow(60, k)
        elif mode == 1:
            i = cut(i, ['N', 'E'])
            i = list(map(str, i))
            i = [[float(j[:-4]), float(j[-4:])] for j in i]
            for j in i:  # j:[32.0, 26.0]
                add = 0
                for k in range(2):  # j[k]:32.0
                    add += j[k] / (60 ** k)
                back.append(add)  # 怎么感觉上面的写法好奇怪
        else:
            i = cut(i, ['N', 'E'])
            i = [str(int(j)) for j in i]
            i = [[float(j[:-4]), float(j[-4:-2]), float(j[-2:])] for j in i]
            print(i)
            for j in i:  # j:[31.0, 30.0, 6.0]
                add = 0
                for k in range(3):  # j[k]:32.0 艹复制下来忘改成3了
                    add += j[k] / (60 ** k) 
                back.append(add)  # 怎么感觉上面的写法好奇怪
    back = [str(round(i, 9)) for i in back]
    return back


def encoding(port: str, path: str, fix: list, loc: list):
    for i in range(len(loc)):  # 本来写的列表推导式 后面发现前面好像不行
        j = str(loc[i])
        j = j + (9 - len(j[j.index('.') + 1:])) * '0'
        fn = (3 if i % 2 == 0 else 4)
        j = (fn - len(j[:j.index('.')])) * ' ' + j
        loc[i] = j
    fix = [(5 - len(i)) * ' ' + i for i in fix]
    with open(path[:-3] + "fix", 'w') as f:
        for i in range(len(fix)):
            f.write(loc[2 * i + 0] + ' ')
            f.write(loc[2 * i + 1] + "  ")
            f.write(fix[i] + ' ')
            f.write(port.upper() + ' ')
            f.write(port[:2].upper() + ' ')
            f.write("4608073" + '\n')
