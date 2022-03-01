from PIL import Image, ImageEnhance, ExifTags, ImageFilter
from PIL.ExifTags import TAGS

from pillow_heif import register_heif_opener
import pillow_heif
register_heif_opener()

import numpy as np
from glob import glob
import random
from time import time
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_background_images(dir_path, drop_list = []):
    """Loads all the images from a given directory path"""
    # COLOR MODE: [background,foreground]
    mode = ["bw","col"] #["bw","col"]

    suffixes = ["png","PNG","jpg","JPG","jpeg","JPEG","HEIC","heic"]

    image_paths= []
    for suf in suffixes:
        # print(os.path.join(dir_path,"*"+ suf))
        for path in glob(os.path.join(dir_path,"*"+ suf)):
            image_paths.append(path)
            
    # Drop redundant/BAD image
    #["IMG_2277.JPG","IMG_2275.JPG","IMG_2276.JPG","IMG_2274.JPG","IMG_3522.jpg"]
    for file in drop_list:
        try:
            image_paths.remove(file)
            print("REMOVED:",file)
        except:
            pass
        
    return image_paths


def correct(tmp_img):
    try:
        for orientation in TAGS.keys() : 
            if ExifTags.TAGS[orientation]=='Orientation': break 
        exif=dict(tmp_img._getexif().items())

        if   exif[orientation] == 3 : 
            tmp_img=tmp_img.rotate(180, expand=True)
        elif exif[orientation] == 6 : 
            tmp_img=tmp_img.rotate(270, expand=True)
        elif exif[orientation] == 8 : 
            tmp_img=tmp_img.rotate(90, expand=True)
    except:
        pass
        
    return tmp_img


def init_main_image(main_img_path, min_img_dim=1000):
# load in the main image that the other photos will form
    main_img = Image.open(main_img_path)

    # correct the orientation
    main_img = correct(main_img)
    # print("Original Dimesions:", main_img.size)

    # Convert to RGB
    main_img = main_img.convert("RGB")

    #resize to the final dimensions
    og_dims = list(main_img.size)
    # print("Modified Dimesions:", main_img.size)
    scaling_factor = min_img_dim / min(og_dims)
    new_dims = [int(og_dims[0] * scaling_factor),
                int(og_dims[1] * scaling_factor)]
    main_img = main_img.resize(new_dims)

    # print("Final Dimesions:", main_img.size)

    return main_img


def crop_image(main_img, crop_pix=[0,0,0,0], crop_percent=[0,0,0,0]):
    """Crop based on pixels or percent of the image
       Param: crop_pix = [left,right,top,bottom]
       Param: crop_percent = [left,right,top,bottom]"""

    # crop to the given size
    crop_percent_left = crop_pix[0]
    crop_percent_right = crop_pix[0]
    crop_percent_top = crop_pix[0]
    crop_percent_bottom = crop_pix[0]

    crop_pixels_left = crop_percent[0]
    crop_pixels_right = crop_percent[0]
    crop_pixels_top = crop_percent[0]
    crop_pixels_bottom = crop_percent[0]

    #crop the image
    og_dims = list(main_img.size)
    main_img = main_img.crop((0 + crop_percent_left * main_img.size[0] + crop_pixels_left,
                            0+ crop_percent_top * main_img.size[1] + crop_pixels_top, 
                            main_img.size[0] - crop_percent_right * main_img.size[0] - crop_pixels_right, 
                            main_img.size[1] - crop_percent_bottom * main_img.size[1] - crop_pixels_bottom)) #left, up, right, bottom


    # rescale
    scaling_factor = min(og_dims) / min(main_img.size)
    new_dims = [int(main_img.size[0] * scaling_factor),
                int(main_img.size[1] * scaling_factor)]
    main_img = main_img.resize(new_dims)

    return main_img

