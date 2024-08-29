'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-08-25 23:33:49
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-08-26 23:34:47
Description: 
pip install pillow exifread ffmpeg-python pymediainfo
提取相片、影片等檔案的拍攝日期或建立日期，可以使用 Python 來遍歷檔案，並針對每種檔案類型讀取相關的時間資訊。
對於圖片（如 JPG、PNG、TIFF、HEIC 等），我們可以使用 PIL 和 exifread 庫來獲取 EXIF 元數據中的拍攝日期。
對於影片（如 MOV、MP4、AVI 等），可以使用 ffmpeg 或 mediainfo 來提取時間資訊。
如果找不到拍攝日期，則使用檔案的建立日期或修改日期。
brew install libheif pyhief

'''

import os
import piexif
import pyheif
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import re
import subprocess
import exifread


# 處理 HEIC 圖片格式的函數
# def get_heic_exif_date(image_path):
#     try:
#         heif_file = pyheif.read(image_path)
#         metadata = heif_file.metadata or []
#         for item in metadata:
#             if item['type'] == 'Exif':
#                 exif_data = piexif.load(item['data'])
#                 if piexif.ImageIFD.DateTimeOriginal in exif_data['Exif']:
#                     return exif_data['Exif'][piexif.ImageIFD.DateTimeOriginal].decode('utf-8')
#         return None
#     except Exception as e:
#         print(f"Error reading HEIC EXIF: {e}")
#         return None


def get_exif_date(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                print(tag_name)
                if tag_name == 'DateTimeOriginal':  # 拍攝日期
                    return value
        else:
            return None
    except Exception as e:
        print(f"Error reading EXIF: {e}")
        return None


def get_file_creation_date(file_path):
    try:
        if os.path.exists(file_path):
            file_stat = os.stat(file_path)
            creation_time = datetime.fromtimestamp(file_stat.st_ctime)
            return creation_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None
    except Exception as e:
        print(f"Error retrieving creation date: {e}")
        return None


def get_mov_mp4_metadata(file_path):
    try:
        cmd = f"ffmpeg -i {file_path} -f ffmetadata -"
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True)
        metadata = result.stdout
        date_match = re.search(
            r'creation_time\s*:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', metadata)
        if date_match:
            return date_match.group(1)
        return None
    except Exception as e:
        print(f"Error retrieving video metadata: {e}")
        return None


def get_heic_exif_date(image_path):
    try:
        heif_file = pyheif.read(image_path)
        metadata = heif_file.metadata or []
        for item in metadata:
            if item['type'] == 'Exif':
                exif_data = piexif.load(item['data'])
                date_taken = exif_data['Exif'].get(
                    piexif.ExifIFD.DateTimeOriginal)
                if date_taken:
                    return date_taken.decode('utf-8')
        return None
    except Exception as e:
        print(f"Error reading HEIC EXIF: {e}")
        return None
        
def get_media_date(file_path):
    file_ext = file_path.split('.')[-1].lower()
    if file_ext == 'heic':
        #heic_date = get_heic_exif_date(file_path)
        heic_date = get_exif_date(get_exif_date)
        
        if heic_date:
            return heic_date
        else:
            return get_file_creation_date(file_path)
    elif file_ext in ['jpg', 'jpeg']:
        exif_date = get_exif_date(file_path)
        if exif_date:
            return exif_date
        else:
            return get_file_creation_date(file_path)
    elif file_ext in ['mp4', 'mov']:
        media_date = get_mov_mp4_metadata(file_path)
        if media_date:
            return media_date
        else:
            return get_file_creation_date(file_path)
    elif file_ext == 'png':
        return get_file_creation_date(file_path)
    else:
        return "Unsupported file format."


def convert_heic_to_jpg(heic_path, output_path):
    heif_file = pyheif.read(heic_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(output_path, "JPEG")
    get_exif_date(os.path.join(output_path, "JPEG"))


def organize_photos_by_date(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file_name in files:            
            file_path = os.path.join(root, file_name)            
            ans = get_media_date(file_path)
            print(f"{file_name} Date: {ans}")

# 測試範例
# file_path = input("請輸入要整理的資料夾路徑: ")
# organize_photos_by_date(file_path.strip())


file_path = "/Users/gump/Desktop/test/00_number_1.mov"
print(get_mov_mp4_metadata(file_path))
