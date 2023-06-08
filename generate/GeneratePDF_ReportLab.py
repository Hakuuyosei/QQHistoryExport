from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import sqlite3
import re







class FontQuery:
    def __init__(self, db_path, font_size):
        # 连接数据库
        print(db_path)
        self.conn = sqlite3.connect(db_path)
        self.font_size = font_size

    def queryCharWidth(self, char):
        # 查询宽高比
        c = self.conn.cursor()
        c.execute(f"SELECT aspect_ratio FROM font_metrics WHERE unicode={ord(char)}")
        result = c.fetchone()

        if result:
            aspect_ratio = result[0]
            # 计算宽度并返回结果
            width = round(aspect_ratio * self.font_size)
            return width

        return None

    def isEmoji(self, s):
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


class DataProcessor:
    def __init__(self, textHeight, lineSpacing, Width, Height, boxPadding, emojiWidth, qqemojiWidth):
        self.textHeight = textHeight
        self.lineSpacing = lineSpacing
        self.Width = Width
        self.Height = Height
        self.boxPadding = boxPadding
        self.emojiWidth = emojiWidth
        self.qqemojiWidth = qqemojiWidth

    def procChatBoxMessage(self, dataList, startX, startY):
        isFinish = False
        while(isFinish):
            isFinish, chatBoxHeight, drawData, remaindData = self.processMessageList(dataList, startX, startY)


    def processMessageList(self, dataList, startX, startY):
        drawData = []
        # 初始化绘制区域
        curX = self.boxPadding + startX
        bufStartX = curX
        curY = self.boxPadding + startY

        maxY = self.Height - startY

        # 遍历列表中的每一个元素
        for item in dataList:
            # 处理 "m" 类型的元素
            if item[0] == "m":
                # 暂存一行中的文本
                buffer = ""
                # 遍历字符串中的每一个字符
                for character in item[1]:
                    # 判断字符是否为表情符号
                    if fontQuery.isEmoji(character):
                        # 如果是表情符号，则绘制符号，并更新当前坐标

                        if buffer != "":
                            pdfDraw.drawText(buffer, bufStartX, curY)
                            buffer = ""

                        drawData.append([pdfDraw.drawEmoji, [character, curX, curY]])
                        curX += self.emojiWidth
                        bufStartX = curX + self.emojiWidth
                    else:
                        # 如果不是表情符号，先查询其宽度
                        charWidth = fontQuery.queryCharWidth(character)
                        # 判断是否需要换行
                        if curX + charWidth > startX + self.Width:
                            # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则先将暂存字符串绘制出来
                            drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY]])
                            # 更新当前坐标到下一行开头，并清空暂存字符串
                            curX = startX + self.boxPadding
                            bufStartX = curX
                            curY += self.textHeight + self.lineSpacing
                            buffer = ""
                        # 将当前字符加入缓冲区中
                        buffer += character
                # 处理剩余的暂存字符串
                if buffer:
                    drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY]])
                    # 更新当前坐标到下一行开头，不加行间距
                    curX = startX + self.boxPadding
                    bufStartX = curX
                    curY += self.textHeight

            # 处理 "qqemoji" 类型的元素
            elif item[0] == "qqemoji":
                # 绘制qq表情符号并更新坐标
                drawData.append([pdfDraw.DrawQQEmoji([item[2], self.qqemojiWidth, curX, curY)]])
                curX += self.qqemojiWidth

            # # 处理 "img" 类型的元素
            # elif item[0] == "img":
            #     # 绘制图片并更新坐标
            #     pdfDraw.DrawQQimg(item[2])
            #     # 图片后要加两个换行
            #     curX = startX + self.boxPadding
            #     curY += self.textHeight + self.lineSpacing
            #     curY += self.textHeight + self.lineSpacing

            # 其他类型的元素忽略

            # 检查是否超出绘制区域，如果是，则返回剩余的元素
            if curY >= maxY:
                return False, curY, drawData, dataList[dataList.index(item):]

        # 处理完所有元素，返回空列表
        return True curY, drawData, []

class PdfDraw():
    def __init__(self, fontPath, chatBoxradius, pageSize):
        self.chatBoxradius = chatBoxradius

        pdfmetrics.registerFont(TTFont('simhei', fontPath))
        #pdfmetrics.registerFont(TTFont('ColorEmoji', 'fonts/ColorEmoji.ttf'))
        self.pdf_canvas = canvas.Canvas("example.pdf", pagesize=pageSize, bottomup=0)
        self.PAGE_HEIGHT = A4[1]
        self.PAGE_WIDTH = A4[0]
        print(self.PAGE_WIDTH / mm)

    def save(self):
        self.pdf_canvas.save()

    def showPage(self):
        self.pdf_canvas.showPage()

    def drawText(self,text, x, y):
        self.pdf_canvas.setFont('simhei', 3 * mm)
        self.pdf_canvas.drawString(x * mm, y * mm, text)
        
    def drawQQEmoji(self, x, y):
        1
    def drawEmoji(self, x, y):
        1
        # pdf_canvas.setFont('Noto-COLRv1', 12 * mm)
        # pdf_canvas.drawString(7.25 * mm, 10 * mm, "🥺")
    def drawChatBox(self, x, y, width, Hight):
        self.pdf_canvas.roundRect(x, y, width, Hight, chatBoxradius)


textHeight = 100 * mm
lineSpacing = 1 * mm
Width = 40 * mm
Height = 40 * mm
boxPadding = 1 * mm
emojiWidth = 1 * mm
qqemojiWidth = 1 * mm
chatBoxradius = 1 * mm

topMargin = 3 * mm
leftMargin = 3 * mm
rightMargin = 3 * mm
bottomMargin = 3 * mm

pageSize = A4
pageHeight = pageSize[1]
pageWidth = pageSize[0]

fontName = "simhei"
fontDirName = "../lib/fonts/"
fontPath = fontDirName + fontName + ".ttf"
fontInfoPath = fontDirName + fontName + "_aspect_ratio.db"

fontQuery = FontQuery(fontInfoPath, textHeight)
pdfDraw = PdfDraw(fontPath, chatBoxradius, pageSize)
dataprocessor = DataProcessor(textHeight, lineSpacing,Width, Height, boxPadding, emojiWidth, qqemojiWidth)
dataprocessor.processMessageList([["m","12121"]],1 * mm, 1 * mm)
pdfDraw.drawChatBox(200*mm,200*mm,200*mm,200*mm)
pdfDraw.save()





