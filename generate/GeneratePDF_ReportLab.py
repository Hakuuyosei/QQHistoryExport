from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PIL import Image

import sqlite3
import re
import os
import configparser
import json



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

    def procTipMessage(self, data, startY, startC):
        if startY - style["tipTextHeight"] < style["chatBoxTextMaxY"]:
            return startY, False
        pdfDraw.drawTipText(data, startY, startC)
        return startY - style["tipTextHeight"], True

    def procImgMessage(self, data, startY, startC):
        1

    def procChatBoxMessage(self, dataList, startY, startC):
        isFinish = False
        curY = startY
        isFinish, textHeight, textWidth, drawData, remaindData \
            = self.processMessageList(dataList, startY - self.style["chatBoxPadding"], startC)

        # 绘制聊天框
        chatBoxHeight = textHeight + 2 * self.style["chatBoxPadding"]
        chatBoxWidth = textWidth + 2 * self.style["chatBoxPadding"]
        chatBoxY = startY - chatBoxHeight
        print("chatboxsize", chatBoxHeight, chatBoxWidth)
        pdfDraw.drawChatBox(chatBoxY, startC, chatBoxWidth, chatBoxHeight)
        curY = chatBoxY
        # 绘制内容
        for item in drawData:
            # py语法糖，将item[1]的所有项作为参数给函数items[0]
            item[0](*item[1])
            print("item", item[1])

        return curY, isFinish, remaindData

    def processMessageList(self, dataList, startY, startC):
        drawData = []
        # 初始化绘制区域
        curX = self.style["chatBoxTextStartX"]
        bufStartX = curX
        curY = startY - self.style["textHeight"]
        textWidth = 0
        textHeight = 0

        # 遍历列表中的每一个元素
        for item in dataList:
            # 处理 "m" 类型的元素
            if item["t"] == "m":
                # 暂存一行中的文本
                buffer = ""
                # 遍历字符串中的每一个字符
                for character in item["c"]["m"]:
                    # 判断字符是否为表情符号
                    if fontQuery.isEmoji(character):
                        # 如果是表情符号，则绘制符号，并更新当前坐标

                        if buffer != "":
                            drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                            buffer = ""

                        drawData.append([pdfDraw.drawEmoji, [character, curX, curY, startC]])
                        curX += self.emojiWidth
                        bufStartX = curX + self.emojiWidth

                    if character == "\n":
                        drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                        # 更新当前坐标到下一行开头，并清空暂存字符串
                        textWidth = curX - self.style["chatBoxTextStartX"]
                        curX = self.style["chatBoxTextStartX"]
                        bufStartX = curX
                        curY -= self.style["textHeight"] + self.style["lineSpacing"]
                        textHeight += self.style["textHeight"] + self.style["lineSpacing"]
                        buffer = ""

                    else:
                        # 如果不是表情符号，先查询其宽度
                        charWidth = fontQuery.queryCharWidth(character)
                        # 判断是否需要换行
                        if curX + charWidth > self.style["chatBoxTextMaxX"]:
                            # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则先将暂存字符串绘制出来
                            drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                            # 更新当前坐标到下一行开头，并清空暂存字符串
                            curX = self.style["chatBoxTextStartX"]
                            bufStartX = curX
                            curY -= self.style["textHeight"] + self.style["lineSpacing"]
                            textHeight += self.style["textHeight"] + self.style["lineSpacing"]
                            buffer = ""
                            textWidth = self.style["chatBoxTextMaxWidth"]
                        # 将当前字符加入缓冲区中
                        buffer += character
                        curX += charWidth
                # 处理剩余的暂存字符串
                if buffer:
                    drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                    if curX - self.style["chatBoxTextStartX"] > textWidth:
                        textWidth = curX - self.style["chatBoxTextStartX"]
                    # curX += self.style["chatBoxTextStartX"]
                    # curY -= self.style["textHeight"] + self.style["lineSpacing"]

                    # 更新当前坐标到下一行开头，不加行间距
                    bufStartX = curX
                    print(bufStartX)

            # 处理 qqemoji 类型的元素
            elif item["t"] == "qqemoji":
                # 绘制qq表情符号并更新坐标
                drawData.append([pdfDraw.drawQQEmoji, [item["c"]["path"], curX, curY]])
                curX += self.style["qqemojiWidth"]

            # 处理 "img" 类型的元素
            elif item["t"] == "img":
                # 绘制图片并更新坐标
                drawData.append([pdfDraw.DrawQQimg, [item["c"]["imgPath"], curX, curY]])
                # 图片后要加两个换行
                curX = self.style["chatBoxTextStartX"]

            # 其他类型的元素忽略

            # 检查是否超出绘制区域，如果是，则返回剩余的元素
            # if curY >= maxY:
            #    return False, curY, drawData, dataList[dataList.index(item):]

        # 处理完所有元素，返回空列表

        # 留出最后一行的位置
        textHeight += self.style["textHeight"] + self.style["lineSpacing"]
        return True, textHeight, textWidth, drawData, []


class PdfDraw:
    def __init__(self, fontPath, style):
        self.style = style

        pdfmetrics.registerFont(TTFont(self.style["fontName"], fontPath))
        # pdfmetrics.registerFont(TTFont('ColorEmoji', 'fonts/ColorEmoji.ttf'))
        self.pdf_canvas = canvas.Canvas("chatData.pdf", pagesize=self.style["pageSize"])
        self.drawPageFooter(1)

    def save(self):
        self.pdf_canvas.save()

    # pdf文档翻页
    def showPage(self):
        self.pdf_canvas.showPage()

    # pdf绘制页脚
    def drawPageFooter(self, pageNum):
        text = self.style["pageFooterText"].replace("$page", str(pageNum))
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["pageFooterTextHeight"])
        self.pdf_canvas.drawString(self.style["leftMargin"], self.style["bottomMargin"], text)

    # pdf翻页
    def nextPage(self, pageNum):
        self.showPage()
        self.drawPageFooter(pageNum)

    def drawText(self, text, x, y, c):
        x = style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["textHeight"])
        self.pdf_canvas.drawString(x, y, text)

    def drawTipText(self, text, y, c):
        self.pdf_canvas.setFillColor(self.style["tipTextColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["tipTextHeight"])
        x = style["pageWidth"] * c + style["contentCenter"]
        y = y - self.style["tipTextHeight"]
        self.pdf_canvas.drawCentredString(x, y, text)

    def drawQQEmoji(self, path, x, y, c):
        x = style["pageWidth"] * c + x
        print("emoji", x, y)

        self.pdf_canvas.drawImage(path, x, y,
                                  width=self.style["qqemojiWidth"], height=self.style["qqemojiWidth"],
                                  mask='auto')

    def drawImg(self, path, x, y, c):
        x = style["pageWidth"] * c + x
        print("Img", x, y)
        # 获取文件名
        filename = os.path.basename(path)

        self.pdf_canvas.drawImage(path, x, y,
                                  width=self.style["qqemojiWidth"], height=self.style["qqemojiWidth"],
                                  mask='auto')

    def drawEmoji(self, x, y, c):
        1
        # pdf_canvas.setFont('Noto-COLRv1', 12 * mm)
        # pdf_canvas.drawString(7.25 * mm, 10 * mm, "🥺")

    def drawChatBox(self, y, c, width, Hight):
        x = style["pageWidth"] * c + self.style["contentStartX"]
        self.pdf_canvas.setFillColor(self.style["chatBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, Hight, style["chatBoxradius"],
                                  fill=1, stroke=0)


class Generate:
    def __init__(self, outputFolderPath, style):
        self.outputFolderPath = outputFolderPath
        self.style = style
        self.pageNum = 1
        self.curY = self.style["contentStartY"]
        self.curC = 0

    def nextPage(self):
        if self.curC + 1 < style["numColumn"]:
            self.curC = self.curC + 1
        else:
            self.pageNum += 1
            pdfDraw.nextPage(self.pageNum)
        self.curY = self.style["contentStartY"]

    def main(self):
        with open(f"{self.outputFolderPath}/chatData.txt", "r") as f:
            i = 1
            for line in f:
                i += 1
                obj = json.loads(line)
                if obj["t"] == "msg":
                    isFinish = False
                    remaindData = obj["c"]
                    while not isFinish:
                        self.curY, isFinish, remaindData = dataprocessor.procChatBoxMessage(remaindData, self.curY,
                                                                                            self.curC)
                        if not isFinish:
                            self.nextPage()

                elif obj["t"] == "revoke":
                    isFinish = False
                    data = obj["c"]["text"]
                    self.curY, isFinish = dataprocessor.procTipMessage(data, self.curY, self.curC)
                    if not isFinish:
                        self.nextPage()
                        self.curY, isFinish = dataprocessor.procTipMessage(data, self.curY, self.curC)

                if i == 10:
                    break
                self.curY -= style["MassageSpacing"]
                if self.curY <= style["chatBoxTextMaxY"]:
                    self.nextPage()




def my_optionxform(optionstr: str) -> str:
    return optionstr
def read_ini_file(file_path: str) -> dict:
    parser = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes=';', comment_prefixes=';')
    parser.optionxform = my_optionxform
    parser.read(file_path, encoding="utf-8")

    data = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            # 尝试将值转换为 int 类型
            if key[0:3] == "num":
                value = int(value)
                data[key] = value
            elif key == "pageSize":
                if value == 'A4': value = A4
                if value == 'A5': value = A5
            else:
                try:
                    value = float(value) * mm
                except ValueError:
                    pass

            data[key] = value

    return data
def procStyle(file_path):
    style = read_ini_file(file_path)
    # Page
    style["pageHeight"] = style["pageSize"][1]  # 纸张高度
    style["pageWidth"] = style["pageSize"][0] / style["numColumn"]  # 纸张宽度

    # 聊天内容
    style["contentStartX"] = style["leftMargin"] + \
                             style["avatarSize"] + 2 * style["avatarMargin"]  # 聊天内容开始X坐标
    style["contentStartY"] = style["pageHeight"] - style["topMargin"]  # 聊天内容开始Y坐标

    style["contentMaxX"] = style["pageWidth"] - style["rightMargin"]  # 聊天内容最大X坐标
    style["contentMaxY"] = style["bottomMargin"] - style["pageFooterTextHeight"]  # 聊天内容最大Y坐标
    style["contentMaxWidth"] = style["pageWidth"] - style["rightMargin"] - style["leftMargin"]
    style["contentCenter"] = style["contentMaxWidth"] / 2 + style["rightMargin"]

    # 聊天框
    style["chatBoxTextStartX"] = style["contentStartX"] + style["chatBoxPadding"]
    style["chatBoxTextMaxX"] = style["contentMaxX"] - style["chatBoxPadding"]
    style["chatBoxTextMaxY"] = style["contentMaxY"] - style["chatBoxPadding"]
    style["chatBoxTextMaxWidth"] = style["chatBoxTextMaxX"] - style["chatBoxTextStartX"]

style = procStyle('GeneratePDF_ReportLab_config.ini')

fontName = "simhei"
fontDirName = "../lib/fonts/"
fontPath = fontDirName + fontName + ".ttf"
fontInfoPath = fontDirName + fontName + "_aspect_ratio.db"

fontQuery = FontQuery(fontInfoPath, style)
pdfDraw = PdfDraw(fontPath, style)
dataprocessor = DataProcessor(style)
generate = Generate("../output", style)
generate.main()
pdfDraw.save()
