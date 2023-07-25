"""
通过PIL计算字体的宽高比，存入数据库中，方便绘制PDF时排版
"""
import sqlite3

import os
from PIL import ImageFont

# 要处理的文件路径
file_path = '../../resources/fonts/simhei.ttf'


# 获取文件名称、拓展名和路径
file_name, file_ext = os.path.splitext(os.path.basename(file_path))
dir_path = os.path.dirname(file_path)


# 组合保存文件名称
output_file_name = f"{file_name}_aspect_ratio.db"

# 构建输出路径
output_path = os.path.join(dir_path, output_file_name)

# 如果文件已经存在，则删除原文件
if os.path.exists(output_path):
    os.remove(output_path)


# 连接数据库
conn = sqlite3.connect(output_path)
c = conn.cursor()

# 创建数据表
c.execute('''CREATE TABLE IF NOT EXISTS font_metrics
             (unicode INT PRIMARY KEY, aspect_ratio REAL)''')

# 加载字体
font = ImageFont.truetype('../../resources/fonts/simhei.ttf', size=16)



# 查询每个 Unicode 字符的宽高比并插入到数据库中
for code_point in range(0x10FFFF):
    char = chr(code_point)
    width, height = font.getsize(char)
    aspect_ratio = width / height
    c.execute(f"INSERT INTO font_metrics (unicode, aspect_ratio) VALUES ({code_point}, {aspect_ratio})")

# 提交更改并关闭连接
conn.commit()
conn.close()
