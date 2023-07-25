import os
import sqlite3
from PIL import Image



import os
import sqlite3

def merge_files(directory_path, db_path, output_file_path):
    if os.path.exists(db_path):
        if os.path.isfile(db_path):
            os.remove(db_path)
    # 获取文件夹中的所有文件路径
    file_paths = []
    for subdir, _, files in os.walk(directory_path):
        for file in files:
            file_paths.append(os.path.join(subdir, file))

    # 拼接所有文件内容到一个大文件中，并记录每个小文件的数据以还原
    with open(output_file_path, "wb") as output_file, \
         sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS files_info
                        (file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         file_name TEXT,
                         start_offset INTEGER,
                         end_offset INTEGER)''')
        offset = 0
        for file_path in file_paths:
            file_size = os.path.getsize(file_path)
            with open(file_path, "rb") as input_file:
                file_content = input_file.read()
                output_file.write(file_content)
            conn.execute('''INSERT INTO files_info (file_name, start_offset, end_offset)
                            VALUES (?, ?, ?)''',
                         (os.path.basename(file_path), offset, offset + file_size))
            offset += file_size
        conn.commit()

def restore_file(merged_file, db_path, file_name):
    # 从数据库中获取文件信息
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute('''SELECT start_offset, end_offset FROM files_info
                                 WHERE file_name = ?''', (file_name,))
        row = cursor.fetchone()
        if not row:
            print("文件不存在")
            return
        start_offset, end_offset = row

    # 从大文件中还原小文件
    with open(merged_file, "rb") as merged_file, \
         open(file_name, "wb") as output_file:
        merged_file.seek(start_offset)
        output_file.write(merged_file.read(end_offset - start_offset))



# 示例用法
fonts_Name = "AppleEmoji"
png_dir = 'E:\Projects/13QQhistoryback/fonts/AppleEmoji/160'
db_path = f'../../resources/fonts/{fonts_Name}/{fonts_Name}.db'
merged_file = f'../../resources/fonts/{fonts_Name}/{fonts_Name}'

# 调用 merge_files 函数将文件夹中的所有文件拼接成一个大文件，并记录文件信息到数据库中
merge_files(png_dir, db_path, merged_file)

# 调用 restore_file 函数还原指定文件名的小文件
restore_file(merged_file, db_path, 'emoji_u1f1e6_1f1ee.png')

#弃用
def merge_pngs(png_dir, db_path, big_png_path):
    """
    拼接图片并保存到数据库
    :param png_dir: 存放png图片的目录
    :param db_path: 数据库路径
    :param big_png_path: 大图保存路径
    :return: None
    """
    # 获取图片列表
    png_files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
    # 每行图片数量
    row_size = 100
    # 图片间隔
    padding = 10
    # 单个图片大小
    img_width, img_height = Image.open(os.path.join(png_dir, png_files[0])).size
    # 大图宽高
    big_img_width = (img_width + padding) * row_size + padding
    big_img_height = (img_height + padding) * ((len(png_files) - 1) // row_size + 1) + padding

    # 创建大图
    big_img = Image.new('RGBA', (big_img_width, big_img_height), (255, 255, 255, 0))
    # 记录坐标和原文件名
    coords_and_names = []

    for i in range(len(png_files)):
        # 计算在大图中的坐标
        x = (i % row_size) * (img_width + padding) + padding
        y = (i // row_size) * (img_height + padding) + padding
        # 打开并复制单个图片到大图
        img = Image.open(os.path.join(png_dir, png_files[i])).copy()
        big_img.paste(img, (x, y))
        # 记录坐标和原文件名
        coords_and_names.append((png_files[i], x, y))

    # 保存大图
    big_img.save(big_png_path)

    # 保存到数据库
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS png_coords (filename TEXT, x INT, y INT)')
    c.executemany('INSERT INTO png_coords VALUES (?, ?, ?)', coords_and_names)
    conn.commit()
    conn.close()

#弃用
def extract_png_from_db(db_path, big_png_path, filename):
    """
    从数据库中提取坐标并还原小图
    :param db_path: 数据库路径
    :param big_png_path: 大图路径
    :param filename: 文件名
    :return: None
    """
    # 从数据库中查询坐标
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT x, y FROM png_coords WHERE filename = ?', (filename,))
    result = c.fetchone()
    if not result:
        print(f'{filename} not found in database!')
        return
    x, y = result
    conn.close()

    # 打开大图并裁剪出对应的小图
    big_img = Image.open(big_png_path)
    img_width, img_height = 160, 160
    row_size = 100
    padding = 10
    idx = int((y - padding) // (img_height + padding)) * row_size + int((x - padding) // (img_width + padding))
    x_offset = ((idx % row_size) * (img_width + padding)) + padding
    y_offset = ((idx // row_size) * (img_height + padding)) + padding
    img = big_img.crop((x_offset, y_offset, x_offset + img_width, y_offset + img_height))

    # 保存小图
    img.save("E:/Projects/13QQhistoryback/fonts/1.png")

# merge_pngs(png_dir, db_path, big_png_path)

# extract_png_from_db(db_path, big_png_path, 'emoji_u1f1e6_1f1ee.png')