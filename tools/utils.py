import pymysql
import math
import json
from osgeo import gdal
from config import hour_max_range, day_max_range,grid_algorithm,rgb_color
from copy import deepcopy
import struct
from range60 import colors
from range60 import aqi, cieq, pm10, pm25, hour_co, hour_no2, hour_o3, hour_so2, day_co, day_no2, day_o3, day_so2
import os


def connect_db():
    conn = pymysql.connect(
        host='47.99.183.154',
        user='mj',
        passwd='kloe.dfjTe',
        db='meijing-data-db',
        port=31002,
    )
    print('连接成功！')
    cursor = conn.cursor()
    return conn, cursor

def int2str(start_time):
    start_time = str(start_time)
    start_time = '{year}-{month}-{day} {hour}:00:00'.format(year=start_time[:4], month=start_time[4:6],
                                                            day=start_time[6:8], hour=start_time[8:])
    return start_time


def select_data_to_geojson(factor_name='aqi', start_time=None):
    '''

    :param factor_name: 默认aqi，目前只限6因子
    :param start_time: 必填需要插值的预测数据时间 2020-02-07 18:00:00
    :return: geojson标准形式
    '''
    conn, cursor = connect_db()
    sql = "select city,longitude,latitude,"+ factor_name +" from air_zq_city_forecast_data where forecast_time=\'{}\'".format(start_time)
    cursor.execute(sql)


    forecast_all_data = cursor.fetchall()

    stations = {
        "type": "FeatureCollection",
        "features": []
    }
    for one in forecast_all_data:
        one_dict = {
            "type": "Feature",
            "geometry": {
                "coordinates": None,
                "type": "Point"
            },
            "properties": {
                "id": None,
                "name": None,
                "type": None,
                "area": None,
                "cityCode": None,
                "stationCode": None,
                "aqi": None,
                "pm25": None,
                "pm10": None,
                "so2": None,
                "no2": None,
                'co': None,
                "o3": None,
                "cieq": None
            }
        }

        one_dict['geometry']['coordinates'] = lnglat_2_webmercator(float(one[2]), float(one[1]))
        one_dict['properties']['area'] = one[0]

        if factor_name == 'co':
            # co是float
            one_dict['properties']['{}'.format(factor_name)] = float(one[3])
        else:
            # 其他数据为int
            one_dict['properties']['{}'.format(factor_name)] = int(one[3])

        stations['features'].append(one_dict)

    cursor.close()
    conn.close()
    return stations

def lnglat_2_webmercator(lng, lat):
    '''
        经纬度转网络墨卡托投影坐标
        lng--- 经度
        lat--- 纬度
        参数：[114.32894, 30.585748]
        返回值：[12727039.383734727, 3579066.6894065146]
    '''
    earthRad = 6378137.0
    x = lng * math.pi / 180 * earthRad
    a = lat * math.pi / 180
    y = earthRad / 2 * math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
    return [x, y]

def write_content(file_path, content, file_type = 'txt', mode = 'w'):
    '''
        文本内容写入
        file_path--- 写入文件路径
        content--- 写入内容
        file_type--- 文件格式, 默认为txt, 其他包括json
        mode--- 文件打开模式
    '''

    with open(file_path, mode) as f:
        if file_type == 'txt':
            f.writelines(content)
        elif file_type == 'json':
            json.dump(content, f)
        f.flush()
        f.close()


def grid_option(factor_name='aqi', time_interval = 'd', start_time = None):
    '''
        构造插值选项
        factor--- 插值因子名称
        time_interval--- 时间尺度, 取值 y/m
        start_time--- 累计插值数据开始时间, 格式为 yyyymmdd / yyyymmddHH
        current_task_name--- 累计数据插值当前时间, 格式为 yyyymmdd / yyyymmddHH
    '''


    max_val = get_factor_max_val(factor_name, time_interval)
    return gdal.GridOptions(options = [],
                            format = 'GTiff',
                            outputType = gdal.GDT_Float32,
                            width = 1091,
                            height = 800,
                            creationOptions = None,
                            outputSRS = 'EPSG:3857',
                            noData = None,
                            algorithm = grid_algorithm,
                            layers = None,
                            SQLStatement = None,
                            where = '{factorName} >= 0 and {factorName} <= {maxVal}'.format(factorName = factor_name, maxVal = max_val),
                            spatFilter = None,
                            zfield = factor_name,
                            z_increase = None,
                            z_multiply = None,
                            callback = None,
                            callback_data = None
                            )
def get_factor_max_val(factor_name = 'aqi', time_interval = 'd'):
    '''
        获取因子允许最大值
        factor_name--- 因子名称
        time_interval--- 时间尺度, y/m
    '''
    max_range = day_max_range
    if time_interval == 'd':
            max_range = hour_max_range

    return max_range[factor_name]

def hex2rgb(hex_str):
    '''
        16进制颜色转换为 RGB
        hex_str--- 16进制颜色字符串
    '''

    int_tuple = struct.unpack('BBB', bytes.fromhex(hex_str))
    return tuple([val for val in int_tuple])

def get_color(factor_name, val, time_interval):
    '''
        根据因子值获取对应的颜色
        factor_name--- 因子名称
        val--- 因子值
        time_interval--- 时间尺度, y/d
    '''

    factor_ranges = aqi
    if factor_name == 'aqi':
        factor_ranges = aqi
    elif factor_name == 'cieq':
        factor_ranges = cieq
    elif factor_name == 'pm25':
        factor_ranges = pm25
    elif factor_name == 'pm10':
        factor_ranges = pm10
    elif factor_name == 'co':
        factor_ranges = day_co if time_interval == 'y' else hour_co
    elif factor_name == 'no2':
        factor_ranges = day_no2 if time_interval == 'y' else hour_no2
    elif factor_name == 'o3':
        factor_ranges = day_o3 if time_interval == 'y' else hour_o3
    elif factor_name == 'so2':
        factor_ranges = day_so2 if time_interval == 'y' else hour_so2

    for factor_range in factor_ranges:
        if val >= factor_range[0] and val <= factor_range[1]:
            index = factor_ranges.index(factor_range)
            if rgb_color:
                return colors[index]
            else:
                return hex2rgb(colors[index][1:])

def export_png(template_img, factor_name='aqi', factor_data=None, time_interval = 'd', start_time = None, img_name=None):
    '''
        执行导出png的操作
        template_img--- 模板png影像数据
        factor_name--- 插值因子名称
        factor_data--- 插值因子tif数据(二维数组)
        time_interval--- 时间尺度, 取值 y/m
        start_time--- 累计插值数据开始时间

    '''


    # 深拷贝一份模板图像
    img = deepcopy(template_img)
    width = img.size[0]
    height = img.size[1]

    # 遍历所有长度的点(宽度)
    for i in range(0, width):
        # 遍历所有宽度的点(高度)
        for j in range(0, height):
            data = (img.getpixel((i, j)))
            # 对透明度不为0的区域进行处理
            if  data[0] != 0 and data[1] != 0:
                # factor_value = factor_data[j, i]
                # 用PIL - Image getpixel方式获取像元值
                factor_value = factor_data.getpixel((i, j))
                factor_color = get_color(factor_name, factor_value, time_interval)
                if factor_color is not None:
                    # 给图片赋予颜色
                    img.putpixel((i, j), (factor_color[0], factor_color[1], factor_color[2], 255))
                else:
                    # tif中NoData部分设置为透明
                    img.putpixel((i, j), (255, 255, 255, 0))
            else:
                # 背景设置为透明
                img.putpixel((i, j), (255, 255, 255, 0))

    # 把图片强制转成RGBA(背景透明的关键)
    img = img.convert("RGBA")

    img.save('./Image_data//{}.png'.format(img_name))