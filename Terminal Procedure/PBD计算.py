from geopy import distance
from geopy.point import Point


# 谨记：3°下滑道坡度是5.24%
def trans(raw: str):
    raw = raw.split()
    raw.pop(3)
    raw.pop()
    for i in range(len(raw)):
        raw[i] = raw[i].replace('m', '\'')
        raw[i] = raw[i].replace('s', '\"')
    raw[0] = 'N' + raw[0] + '°'
    raw.insert(3, ' ')
    raw[4] = 'E' + raw[4] + '°'
    return ''.join(raw)


# 已知点的经纬度
latitude = 29.29776382
longitude = 90.89167786

# 将已知点的经纬度转换为Point对象
known_point = Point(latitude, longitude)

# 计算新点的经纬度
new_point = distance.distance(kilometers=10).destination(known_point, 269)
new_latitude = new_point.latitude
new_longitude = new_point.longitude

print(f"已知点经纬度：({latitude}, {longitude})")
print(f"新点经纬度：({new_latitude}, {new_longitude})")
print("新点经纬度：" + trans(new_point.format()))
