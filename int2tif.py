"""
Created on Thu Sep 28 14:47:13 2023
@author: Administrator
"""

# -*- coding: utf-8 -*-
import numpy as np
from osgeo import gdal
import os
from osgeo import osr


# 依据BSQ存储规则，按照存储完单波段整幅图像后再存储下一波段的存储方法进行提取并存入数组。
def read_as_bsq(dataarr, bands, rows, col):
    imgarr = np.zeros((bands, rows, col))
    for b in range(bands):  # 取出每个波段
        start = b * rows * col
        end = start + rows * col
        arrtem = dataarr[start:end]
        for r in range(rows):  # 一维数组按行取出，存入对应三维数组。
            start2 = r * col
            end2 = start2 + col
            imgarr[b, r, :] = arrtem[start2:end2]
    return imgarr


def test_writetotif(dir):
    # 读取二进制数据并转换成int16类型的数组
    # dir = r"J:\G\workk\2023\zy\LGC\MODIS\MOD09GA_A2004107.sur_refl.int"
    f = open(dir, 'rb')
    fint = np.fromfile(f, dtype=np.int16)

    # 数据提取
    bands, rows, col = 6, 2040, 1720
    # imgarr = read_as_bil(fint, bands, rows, col)
    imgarr = read_as_bsq(fint, bands, rows, col)
    # imgarr = read_as_bip(fint, bands, rows, col)
    # 将提取的数组存储为tif格式图像.
    # 注意这里未设置地理坐标和仿射变换信息，所以不能用ENVI等软件打开。
    savedir = dir.split(".")[0] + "_sur_refl.tif"
    # savedir = r"E:\datasets\stfdatasets\Coleambally_Irrigation_Area\CIA\MODIS\2001_281_08oct\MOD09GA_A2001281.sur_refl.tif"
    datatype = gdal.GDT_UInt16
    bands, high, width = imgarr.shape
    driver = gdal.GetDriverByName("GTiff")
    datas = driver.Create(savedir, col, rows, bands, datatype)

    # 设置地理坐标和仿射变换信息
    image_geotrans = [378000, 25, 0, 6170000, 0, 25]
    image_projection = "AMG55"
    datas.SetGeoTransform(image_geotrans)

    # datas.SetProjection(agd66)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(20255)
    datas.SetProjection(outRasterSRS.ExportToWkt())
    for i in range(bands):
        datas.GetRasterBand(i + 1).WriteArray(imgarr[i])
    del datas


if __name__ == "__main__":
    in_dir = r'./'  # input dir

    file_list = os.listdir(in_dir)
    for file in file_list:
        if file.endswith('.int'):
            test_writetotif(in_dir + "\\" + file)
    print("save succfully")