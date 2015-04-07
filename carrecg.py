# -*- coding: utf-8 -*-
import ctypes
from ctypes import *
import os
import re
import json

from PIL import Image


class CarRecgEngine:

    def __init__(self):
        """创建车型识别引擎"""
        self.dll = ctypes.cdll.LoadLibrary('CarRecogniseEngine.dll')
        self.engineID = self.dll.InitialEngine()
        self.file = 'cropimg'

    def __del__(self):
        self.dll.UnInitialEngine(self.engineID)

    def imgrecg(self, path, coordinates=None):
        """识别车辆信息"""
        try:
            recg_path = None
            if coordinates is not None:
                path = self.crop_img(path, coordinates)
                recg_path = path

            p_str_url = create_string_buffer(path)
            sz_result = create_string_buffer('\0' * 1024)

            ret = self.dll.doRecg(self.engineID, byref(p_str_url),
                                  byref(sz_result), 1024)

            return json.loads(sz_result.value, 'gbk')
        except Exception:
            return None
        finally:
            try:
                if recg_path is not None:
                    os.remove(recg_path)
            except Exception:
                pass

    def uninit(self):
        self.dll.UnInitialEngine(self.engineID)

    def rematch(self, j):
        """转化标准Json格式"""
        j = re.sub(r"{\s*(\w)", r'{"\1', j)
        j = re.sub(r",\s*(\w)", r',"\1', j)
        j = re.sub(r"(\D):", r'\1":', j)
        j = j.replace("'", "\"")

        return json.loads(j, 'gbk')

    def crop_img(self, path, coordinates):
        """图片截取"""
        im = Image.open(path)

        box = (coordinates[0], coordinates[1], coordinates[2], coordinates[3])
        region = im.crop(box)

        filename = os.path.basename(path)

        crop_path = os.path.join(self.file, filename)
        region.save(crop_path)

        return crop_path


if __name__ == '__main__':
    cr = CarRecgEngine()
    area1 = (0,357,1316,2046)
    area2 = (221,409,1194,1351)
    a=cr.imgrecg('img/000.jpg',None)
    #a = '{"head":{"code":1,"count":0,"msg":"识别功"},"body":"[{"ywcl":1,"ywhp":1,"hpzl":"02","hphm":"粤LXA293","cllx":"K33","csys":"J","ppdm":"012","clpp":"比亚迪F3","kxd": 69,"jcsj":"2014-10-28 23":51":17"}]"}'
    #b = '{"head":{"code":1,"count":0,"msg":"识别成功"},"body":"123"}'
    #print a[]
    #b = cr.imgrecg(a)
    print a
    #print b['body']
    #cr.uninit()
    del cr
