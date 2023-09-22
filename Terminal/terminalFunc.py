import pandas as pd

namelist = []


def est_name(xlsx):
    db = pd.read_excel(xlsx, sheet_name=None)
    temp = list(db.keys())
    for i in temp:
        if ("appr" in i) or ("sid" in i) or ("star" in i):
            namelist.append(i)
    return namelist


def get_name():
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
