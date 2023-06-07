from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Frame, Paragraph, Flowable

import re

def isEmoji(s):
    """
    判断字符串是否为Emoji表情
    """
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags=re.UNICODE)
    return emoji_pattern.search(s) is not None


def procText(rowWidth, colWidth, emojiWidth, qqemojiWidth, lst):
    curRow = 0
    curY = 0
    buffer = ''
    for item in lst:
        if item[0] == 'm':
            text = item[1]
            for character in text:
                if isEmoji(character):
                    pdfDraw.DrawEmoji(character)
                    curRow += qqemojiWidth
                else:
                    charWidth = queryCharWidth(character)
                    if curRow + charWidth > rowWidth:
                        pdfDraw.DrawText(buffer)
                        curRow = 0
                        curY += colWidth
                        buffer = ''
                    buffer += character
                    curRow += charWidth
        elif item[0] == 'qqemoji':
            path = item[2]
            pdfDraw.DrawQQEmoji(path, qqemojiWidth)
        elif item[0] == 'img':
            path = item[2]
            pdfDraw.DrawQQimg(path)
            curY += colWidth
            curRow = 0
    pdfDraw.DrawText(buffer)


# 定义样式
styles = getSampleStyleSheet()
styleNormal = styles['Normal']

# 创建页面大小和画布对象
PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]
pdf_canvas = canvas.Canvas("example.pdf", pagesize=letter)

# 定义段落内容
text = "He"

# 设置段落样式
para = Paragraph(text, styleNormal)

# 创建圆角矩形对象
radius = 0.25 * inch
r = RoundedRectangle(1, 1, radius, fill_color=colors.blue)

# 计算圆角矩形的大小
width, height = para.wrap(1000, 1000)
r.width = width + 2 * radius
r.height = height + 2 * radius

# 将段落添加到圆角矩形内部
para.wrapOn(pdf_canvas, r.width - 2 * radius, r.height - 2 * radius)
para.drawOn(pdf_canvas, radius, radius)

# 将圆角矩形添加到画布上
r.drawOn(pdf_canvas, 2 * inch, 6.5 * inch)

# 保存PDF文件
pdf_canvas.save()
