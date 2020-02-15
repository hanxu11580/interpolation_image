

rgb_color = False
# 插值算法
grid_algorithm = 'invdist:power=2:smoothing=0:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=0.0'

# 小时数据各因子最大值
hour_max_range = {
    'aqi': 500,
    'pm25': 500,
    'pm10': 600,
    'no2': 3840,
    'o3': 1200,
    'co': 150,
    'so2': 800,
    'cieq': 12
}

# 日数据各因子最大值
day_max_range = {
    'aqi': 500,
    'pm25': 500,
    'pm10': 600,
    'no2': 940,
    'o3': 800,
    'co': 60,
    'so2': 2620,
    'cieq': 12
}