'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-08-25 19:33:26
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-08-27 20:00:31
Description: 
見README.md
'''
from pillow_heif import register_heif_opener
from PIL import Image
from hachoir.parser import createParser #mov
from hachoir.metadata import extractMetadata #mov
import os
import piexif # jpg
import platform # other file AAE
import time  # other file AAE
import shutil # 分folder用
from datetime import datetime  # 分folder用

# OK! GET HEIC!!
def get_heic_photo_date(file_path):
    # Register the HEIF opener
    register_heif_opener()

    # Open the HEIC file
    image = Image.open(file_path)

    # Get EXIF data
    exif_data = image.getexif()

    # Extract photo date if available
    if exif_data:
        # print(exif_data)
        # 36867 is the tag for DateTimeOriginal
        # photo_date = exif_data.get(306)
        # formatted_date = photo_date.replace(":", "-", 2)
        return exif_data.get(306)

    return None

# OK MOV and MP4
def get_mov_creation_date(file_path):
    parser = createParser(file_path)
    if not parser:
        print("Unable to parse file.")
        return None

    metadata = extractMetadata(parser)
    if metadata:
        for item in metadata.exportPlaintext():
            if "creation date" in item.lower():
                # Extract the date from the string
                photo_date = item.split(": ", 1)[1]
                formatted_date = photo_date.replace("-", ":", 2)
               
                return formatted_date

    return None

# AAE PNG
def get_file_creation_date(file_path):
    if platform.system() == 'Windows':
        # For Windows, use os.path.getctime (creation time)
        creation_time = os.path.getctime(file_path)
    else:
        # For Unix-based systems (macOS, Linux), use os.stat().st_birthtime if available
        stat = os.stat(file_path)
        try:
            creation_time = stat.st_birthtime  # Creation date
        except AttributeError:
            # If birthtime is not available, fallback to modification time
            print("Birthtime not available, using modification time.")
            creation_time = stat.st_mtime  # Modification date
            return False

    # Convert timestamp to readable format
    print("file")
    print(creation_time)
    return time.strftime('%Y:%m:%d %H:%M:%S', time.localtime(creation_time))

    
# JPG
def get_jpg_photo_date(file_path):
    try:
        # Open the image
        img = Image.open(file_path)

        # Load EXIF data
        exif_data = img.info.get('exif')

        if exif_data:
            # Extract EXIF metadata using piexif
            exif_dict = piexif.load(exif_data)
            # Retrieve the original date from EXIF metadata
            photo_date = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal)

            if photo_date:         
                # formatted_date = photo_date.replace(":", "-", 2)
                return photo_date.decode('utf-8')


        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    

def get_media_date(file_path):
    file_ext = file_path.split('.')[-1].lower()
    if file_ext == 'heic':
        heic_date = get_heic_photo_date(file_path)

        if heic_date:
            return heic_date
        else:
            print("no date in heic")
            return False
           
        
    elif file_ext in ['jpg', 'jpeg']:
        exif_date = get_jpg_photo_date(file_path)
        if exif_date:
            return exif_date
        else:
            exif_date = get_file_creation_date(file_path)
            if exif_date:
                return exif_date
            else:
                print("no date in jpg 2 ways")
                return False #get_file_creation_date(file_path)
        
    elif file_ext in ['mp4', 'mov']:
        media_date = get_mov_creation_date(file_path)
        if media_date:
            return media_date
        else:
            print("no date in mov")
            return False #get_file_creation_date(file_path)
        
    elif file_ext in ['png', 'aae']:
        return get_file_creation_date(file_path)
    
    else:
        print("no date in file.")
        return False


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
                date_taken = get_media_date(file_path)
            except Exception as e:
                print(f"無法讀取 {file} 的日期資訊: {e}")
                continue

            print(f"date_taken:{date_taken}")
            if date_taken != False:
                try:
                    datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
                    # 創建或獲取對應日期的資料夾
                    dest_folder = create_date_folder(root_folder, date_taken)
                    # 移動照片到目標資料夾
                    move_photo(file_path, dest_folder)
                except Exception as e:
                    print(f"{file}日期格式錯誤=>{date_taken}")
                

    # 刪除空的資料夾
    delete_empty_folders(root_folder)


def main():
    """
    用于开发时调试的主函数
    """
    # 测试文件路径
    test_file_path = "/Users/gump/Desktop/test/IMG_3453.HEIC"
    
    # 测试获取媒体日期
    photo_date = get_media_date(test_file_path)
    if photo_date:
        print("Photo Date:", photo_date)
    else:
        print("No date found in EXIF metadata.")
    
    # 测试文件夹整理
    test_folder_path = "/Users/gump/Desktop/test"
    organize_photos_by_date(test_folder_path)

if __name__ == "__main__":
    main()