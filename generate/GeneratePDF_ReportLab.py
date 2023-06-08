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
    def __init__(self, db_path, style):
        self.style = style

        # 连接数据库
        self.conn = sqlite3.connect(db_path)
        self.font_size = self.style["textHeight"]

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
    def __init__(self, style):
        self.style = style

    def procChatBoxMessage(self, dataList, startY):
        isFinish = False
        while(not isFinish):
            textStartY = startY + self.style["chatBoxPadding"]
            isFinish, textHeight, textWidth, drawData, remaindData \
                = self.processMessageList(dataList, startY)

            # 绘制聊天框
            chatBoxHeight = textHeight + 2 * self.style["chatBoxPadding"]
            chatBoxWidth = textWidth + 2 * self.style["chatBoxPadding"]
            print(chatBoxHeight, chatBoxWidth)
            pdfDraw.drawChatBox(startY, chatBoxWidth, chatBoxHeight)
            # 绘制内容
            for items in drawData:
                # py语法糖，将items[1]的所有项作为参数给函数items[0]
                items[0](*items[1])
                print(items[1])





    def processMessageList(self, dataList, startY):
        drawData = []
        # 初始化绘制区域
        curX = self.style["chatBoxTextStartX"]
        bufStartX = curX
        curY = startY
        textWidth = 0
        textHeight = 0

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
                            drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY]])
                            buffer = ""

                        drawData.append([pdfDraw.drawEmoji, [character, curX, curY]])
                        curX += self.emojiWidth
                        bufStartX = curX + self.emojiWidth
                    else:
                        # 如果不是表情符号，先查询其宽度
                        charWidth = fontQuery.queryCharWidth(character)
                        # 判断是否需要换行
                        if curX + charWidth > self.style["chatBoxTextMaxX"]:
                            # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则先将暂存字符串绘制出来
                            drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY]])
                            # 更新当前坐标到下一行开头，并清空暂存字符串
                            curX = self.style["chatBoxTextStartX"]
                            bufStartX = curX
                            curY += self.style["textHeight"] + self.style["lineSpacing"]
                            textHeight += self.style["textHeight"] + self.style["lineSpacing"]
                            buffer = ""
                            textWidth = self.style["chatBoxTextMaxWidth"]
                        # 将当前字符加入缓冲区中
                        buffer += character
                        curX += charWidth
                # 处理剩余的暂存字符串
                if buffer:
                    drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY]])
                    if curX - self.style["chatBoxTextStartX"] > textWidth:
                        textWidth = curX - self.style["chatBoxTextStartX"]
                    curX = self.style["chatBoxTextStartX"]
                    # curY += self.style["textHeight"] + self.style["lineSpacing"]

                    # 更新当前坐标到下一行开头，不加行间距
                    bufStartX = curX
                    print(bufStartX)

            # 处理 "qqemoji" 类型的元素
            elif item[0] == "qqemoji":
                # 绘制qq表情符号并更新坐标
                drawData.append([pdfDraw.DrawQQEmoji,[item[2], self.qqemojiWidth, curX, curY]])
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
            #if curY >= maxY:
            #    return False, curY, drawData, dataList[dataList.index(item):]

        # 处理完所有元素，返回空列表

        # 留出最后一行的位置
        textHeight += self.style["textHeight"]
        return True, textHeight, textWidth, drawData, []

class PdfDraw():
    def __init__(self, fontPath, style):
        self.style = style

        pdfmetrics.registerFont(TTFont(style["fontName"], fontPath))
        #pdfmetrics.registerFont(TTFont('ColorEmoji', 'fonts/ColorEmoji.ttf'))
        self.pdf_canvas = canvas.Canvas("example.pdf", pagesize = style["pageSize"], bottomup=0)

    def save(self):
        self.pdf_canvas.save()

    def showPage(self):
        self.pdf_canvas.showPage()

    def drawText(self, text, x, y):
        print(text,x,y)
        textY = y + self.style["textHeight"]
        self.pdf_canvas.setFont('simhei', 6 * mm)
        self.pdf_canvas.drawString(x, textY, text)
        
    def drawQQEmoji(self, x, y):
        1
    def drawEmoji(self, x, y):
        1
        # pdf_canvas.setFont('Noto-COLRv1', 12 * mm)
        # pdf_canvas.drawString(7.25 * mm, 10 * mm, "🥺")
    def drawChatBox(self, y, width, Hight):
        print(self.style["contentStartX"])
        self.pdf_canvas.roundRect(self.style["contentStartX"], y, width, Hight, style["chatBoxradius"])


style = {
    # 文字
    "fontName": "simhei",# 字体名称
    "textHeight": 6 * mm,# 文本高度
    "lineSpacing": 1 * mm,# 行距
    "emojiWidth": 6 * mm,# emoji宽度
    "qqemojiWidth": 6 * mm,# qqemoji宽度 注意，请勿大于行距 + 文本高度

    # 聊天框
    "chatBoxPadding": 1 * mm,# 聊天框内边距
    "chatBoxradius": 1 * mm,# 聊天框圆角半径

    # 头像
    "avatarSize": 3 * mm,# 文本高度
    "avatarMargin": 1 * mm,# 文本高度

    # 页边距
    "topMargin": 3 * mm,
    "leftMargin": 3 * mm,
    "rightMargin": 3 * mm,
    "bottomMargin": 3 * mm,

    #页脚
    "pageFooterText": "生成日期：$date  第 $page 页",
    "pageFooterTextHeight": 3 * mm,

    # 纸张大小
    "pageSize": A4
}
# Page
style["pageHeight"] = style["pageSize"][1]# 纸张高度
style["pageWidth"] = style["pageSize"][0]# 纸张宽度

# 聊天内容
style["contentStartX"] = style["leftMargin"] + \
                         style["avatarSize"] + 2 * style["avatarMargin"]# 聊天内容开始X坐标
style["contentStartY"] = style["topMargin"]# 聊天内容开始X坐标

style["contentMaxX"] = style["pageWidth"] - style["rightMargin"]# 聊天内容最大X坐标
style["contentMaxY"] = style["pageHeight"] - style["topMargin"]\
                       - style["pageFooterTextHeight"]# 聊天内容最大Y坐标

# 聊天框
style["chatBoxTextStartX"] = style["contentStartX"] + style["chatBoxPadding"]
style["chatBoxTextMaxX"] = style["contentMaxX"] - style["chatBoxPadding"]
style["chatBoxTextMaxY"] = style["contentMaxY"] - style["chatBoxPadding"]
style["chatBoxTextMaxWidth"] = style["chatBoxTextMaxX"] - style["chatBoxTextStartX"]



fontName = "simhei"
fontDirName = "../lib/fonts/"
fontPath = fontDirName + fontName + ".ttf"
fontInfoPath = fontDirName + fontName + "_aspect_ratio.db"

fontQuery = FontQuery(fontInfoPath, style)
pdfDraw = PdfDraw(fontPath, style)
dataprocessor = DataProcessor(style)
dataprocessor.procChatBoxMessage([["m","你是谁？？你是谁？？你是谁？？你是谁？？？？？"]],4 * mm)
#pdfDraw.drawChatBox(200*mm,200*mm,200*mm,200*mm)
pdfDraw.save()





