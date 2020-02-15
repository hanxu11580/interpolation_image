from tools.utils import select_data_to_geojson
from tools.utils import write_content
from tools.utils import grid_option
from tools.utils import int2str
from PIL import Image
from tools.utils import export_png
from osgeo import gdal
from flask import Flask
from flask_restful import Resource, Api
import os


app = Flask(__name__)
api = Api(app)


class InterpolationApi(Resource):
    def get(self, factor_name, start_time):
        start_time = int2str(start_time)
        stations = select_data_to_geojson(factor_name, start_time)
        if os.path.exists('./Image_data//{factor}//{time}.png'.format(factor=factor_name, time=start_time.replace(':', '_'))):
            return "This time factor interpolation picture already exists"

        json_file = './geojson_data//{factor}//{time}.json'.format(factor=factor_name, time=start_time.replace(':', '_'))
        tif_file = './tif_data//{factor}//{time}.tif'.format(factor=factor_name, time=start_time.replace(':', '_'))
        write_content(json_file, stations, 'json')
        print("写入geojson中...")

        dataset = gdal.OpenEx(json_file)
        grid_opt = grid_option(factor_name, 'd',)
        print("插值中...")
        gdal.Grid(tif_file, dataset, options=grid_opt)

        # 出图
        print("生成图片中...")
        img = Image.open('./state.png')
        tif = Image.open(tif_file)
        export_png(img, factor_name, tif, 'd', img_name='{factor}//{time}'.format(factor=factor_name, time=start_time.replace(':', '_')))
        print("出图成功!")
        return "The image is generated successfully. Please check the corresponding file"


api.add_resource(InterpolationApi, '/<string:factor_name>/<int:start_time>')


if __name__ == "__main__":

    app.run()