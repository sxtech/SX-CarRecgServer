# -*- coding: utf-8 -*-
import ctypes
from ctypes import *
import os
import re
import json

from PIL import Image
from app import app, logger


class CarRecgEngine:

    def __init__(self):
        """创建车型识别引擎"""
        self.dll = ctypes.cdll.LoadLibrary('CarRecogniseEngine.dll')
        self.engineID = self.dll.InitialEngine()

    def __del__(self):
        self.dll.UnInitialEngine(self.engineID)

    def imgrecg(self, path, coord=[]):
        """识别车辆信息"""
        try:
            recg_path = None
            if coord != []:
                path = self.crop_img(path, coord)
                recg_path = path

            p_str_url = create_string_buffer(path)
            sz_result = create_string_buffer('\0' * 1024)

            ret = self.dll.doRecg(self.engineID, byref(p_str_url),
                                  byref(sz_result), 1024)

            res = sz_result.value.decode(encoding='gbk', errors='ignore')

            return json.loads(res)
        except Exception as e:
            logger.error(e)
            return None
        finally:
            try:
                if recg_path is not None:
                    os.remove(recg_path)
            except Exception as e:
                logger.error(e)

    def rematch(self, j):
        """转化标准Json格式"""
        j = re.sub(r"{\s*(\w)", r'{"\1', j)
        j = re.sub(r",\s*(\w)", r',"\1', j)
        j = re.sub(r"(\D):", r'\1":', j)
        j = j.replace("'", "\"")

        return json.loads(j, 'gbk')

    def crop_img(self, path, coord):
        """图片截取"""
        im = Image.open(path)

        box = (coord[0], coord[1], coord[2], coord[3])
        region = im.crop(box)

        filename = os.path.basename(path)

        crop_path = os.path.join(app.config['CROP_PATH'], filename)
        region.save(crop_path)

        return crop_path
