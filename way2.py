#pip install exifread

import os
import shutil
import exifread
from datetime import datetime

def get_photo_date_taken(filepath):
    with open(filepath, 'rb') as f:
        tags = exifread.process_file(f)
        date_taken = tags.get('EXIF DateTimeOriginal')
        if date_taken:
            return str(date_taken)
        else:
            # 如果沒有 EXIF 日期信息，返回文件的修改時間
            return datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y:%m:%d %H:%M:%S')

def create_date_folder(base_path, date_taken):
    date_obj = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
    folder_name = date_obj.strftime('%Y_%m_')
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def move_photo(file_path, dest_folder):
    file_name = os.path.basename(file_path)
    dest_path = os.path.join(dest_folder, file_name)

    # 如果文件名已存在，添加時間碼避免覆蓋
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(file_name)
        timestamp = datetime.now().strftime('%H%M%S')
        new_file_name = f"{base}_{timestamp}{ext}"
        dest_path = os.path.join(dest_folder, new_file_name)
    
    shutil.move(file_path, dest_path)

def delete_empty_folders(path):
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        if not dirnames and not filenames:
            os.rmdir(dirpath)

def organize_photos_by_date(root_folder):
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(subdir, file)

            # 取得照片的拍攝日期
            try:
                date_taken = get_photo_date_taken(file_path)
            except Exception as e:
                print(f"無法讀取 {file} 的日期資訊: {e}")
                continue
            
            # 創建或獲取對應日期的資料夾
            dest_folder = create_date_folder(root_folder, date_taken)

            # 移動照片到目標資料夾
            move_photo(file_path, dest_folder)
    
    # 刪除空的資料夾
    delete_empty_folders(root_folder)

# 使用範例
root_folder = '/path/to/your/photos'
organize_photos_by_date(root_folder)
