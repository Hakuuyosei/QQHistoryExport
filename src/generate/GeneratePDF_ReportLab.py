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
import datetime
import shutil

class DrawingQuery:
    def __init__(self, paths, style):
        self.paths = paths
        self.style = style

        # 连接数据库
        self.conn = sqlite3.connect(paths["fontInfoPath"])

    def queryCharWidth(self, char):
        # 查询宽高比
        c = self.conn.cursor()
        c.execute(f"SELECT aspect_ratio FROM font_metrics WHERE unicode={ord(char)}")
        result = c.fetchone()

        if result:
            aspect_ratio = result[0]
            # 计算宽度并返回结果
            width = round(aspect_ratio * self.style["textHeight"])
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

    def resize_image(self, img_width, img_height, max_width, max_height):
        # 比较宽高的大小，计算缩放比例
        ratio = min(max_width / img_width, max_height / img_height)
        # 根据比例计算新的宽高
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        return new_width, new_height


class DataProcessor:
    def __init__(self, paths, style):
        self.paths = paths
        self.style = style

    def procTipMessage(self, data, startY, startC):
        if startY - style["tipTextHeight"] < style["chatBoxTextMaxY"]:
            return startY, False
        pdfDraw.drawTipText(data, startY, startC)
        return startY - style["tipTextHeight"], True

    def procImgMessage(self, data, offsetX, startY, startC):
        path = data["imgPath"]
        name = data["name"]
        imgType = data["imgType"]

        if path == "":
            return True, startY
        with Image.open(self.paths["outputDirPath"] + path) as img:
            imgWidth, imgHeight = img.size
        # 如果是图片表情
        if imgType == "marketface":
            maxWidth = style["imgEmoMaxSize"]
            maxHeight = style["imgEmoMaxSize"]
        else:
            maxWidth = style["imgMaxWidth"]
            maxHeight = style["imgMaxHeight"]


        width, height = drawingQuery.resize_image(imgWidth, imgHeight, maxWidth, maxHeight)

        if startY - height - style["textHeight"] < style["contentMaxY"]:
            return startY, False
        print("image", width, height, imgType)
        pdfDraw.drawImg(path, name, width, height, offsetX, startY, startC)
        return startY - height - style["textHeight"], True

    def procChatBoxMessage(self, dataList, startY, startC):
        isFinish = False
        curY = startY
        isFinish, textHeight, textWidth, drawData, remaindData \
            = self.processMessageList(dataList, startY - self.style["chatBoxPadding"], startC)

        # 绘制聊天框
        if textHeight != 0:
            chatBoxHeight = textHeight + 2 * self.style["chatBoxPadding"]
            chatBoxWidth = textWidth + 2 * self.style["chatBoxPadding"]
            chatBoxY = startY - chatBoxHeight

            # print("chatboxsize", chatBoxHeight, chatBoxWidth)
            pdfDraw.drawChatBox(chatBoxY, startC, chatBoxWidth, chatBoxHeight)
            curY = chatBoxY
            # 绘制内容
            for item in drawData:
                # py语法糖，将item[1]的所有项作为参数给函数items[0]
                item[0](*item[1])
                # print("item", item[1])

        return curY, isFinish, remaindData

    def processMessageList(self, dataList, startY, startC):
        def lineBreak():
            nonlocal buffer, bufStartX, curX, curY, startC, textHeight, textWidth
            if buffer != "":
                # 绘制缓冲区字符
                drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                buffer = ""

            # 更新当前坐标到下一行开头，并清空暂存字符串
            if curX - self.style["chatBoxTextStartX"] > textWidth:
                textWidth = curX - self.style["chatBoxTextStartX"]
            curX = self.style["chatBoxTextStartX"]
            bufStartX = curX

            if curY - self.style["textHeight"] + self.style["lineSpacing"] < \
                    style["chatBoxTextMaxY"]:
                return False
            else:
                curY -= self.style["textHeight"] + self.style["lineSpacing"]
                textHeight += self.style["textHeight"] + self.style["lineSpacing"]
                return True

        buffer = ""
        drawData = []
        textWidth = 0
        textHeight = 0

        curX = self.style["chatBoxTextStartX"]
        curY = startY
        bufStartX = curX
        if not lineBreak():
            # 没有空间用来换行
            return False, 0, 0, drawData, dataList
        else:
            # 校正初次换行
            curY += self.style["lineSpacing"]
            textHeight = 0

        # 遍历列表中的每一个元素
        for itemNum in range(len(dataList)):
            item = dataList[itemNum]
            # 处理 "m" 类型的元素
            if item["t"] == "m":
                # 暂存一行中的文本
                buffer = ""
                # 遍历字符串中的每一个字符
                str = item["c"]["m"]
                for charNum in range(len(str)):
                    character = str[charNum]
                    # 判断字符是否为表情符号
                    if drawingQuery.isEmoji(character):
                        # 如果是表情符号，则绘制符号，并更新当前坐标

                        if buffer != "":
                            drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                            buffer = ""

                        drawData.append([pdfDraw.drawTextEmoji, [character, curX, curY, startC]])
                        curX += self.style["emojiWidth"]
                        bufStartX = curX + self.style["emojiWidth"]

                    if character == "\n":
                        if not lineBreak():
                            remaindData = []
                            if dataList[itemNum + 1:] != []:
                                remaindData.append(*dataList[itemNum + 1:])
                            return False, textHeight, textWidth, drawData, remaindData

                    else:
                        # 如果不是表情符号，先查询其宽度
                        charWidth = drawingQuery.queryCharWidth(character)
                        # 判断是否需要换行
                        if curX + charWidth > self.style["chatBoxTextMaxX"]:
                            # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则将暂存字符串绘制出来并换行
                            if not lineBreak():

                                remaindData = []
                                item["c"]["m"] = str[charNum:]
                                remaindData.append(item)
                                if dataList[itemNum + 1:] != []:
                                    remaindData.append(*dataList[itemNum + 1:])
                                return False, textHeight, textWidth, drawData, remaindData



                        # 将当前字符加入缓冲区中
                        buffer += character
                        curX += charWidth
                # 处理剩余的暂存字符串
                if buffer:
                    if curX - self.style["chatBoxTextStartX"] > textWidth:
                        textWidth = curX - self.style["chatBoxTextStartX"]

                    drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])


            # 处理 qqemoji 类型的元素
            elif item["t"] == "qqemoji":
                if curX + self.style["qqemojiWidth"] > self.style["chatBoxTextMaxX"]:
                    # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则先将暂存字符串绘制出来
                    if buffer != []:
                        drawData.append([pdfDraw.drawText, [buffer, bufStartX, curY, startC]])
                    # 更新当前坐标到下一行开头，并清空暂存字符串
                    curX = self.style["chatBoxTextStartX"]
                    bufStartX = curX


                    curY -= self.style["textHeight"] + self.style["lineSpacing"]
                    textHeight += self.style["textHeight"] + self.style["lineSpacing"]
                    buffer = ""
                    textWidth = self.style["chatBoxTextMaxWidth"]
                    # 待验证
                    if curY - self.style["textHeight"] + self.style["lineSpacing"] - self.style["textHeight"] < \
                            self.style["c"] - style["chatBoxTextMaxY"]:
                        remaindData = []
                        remaindData.append(*dataList[itemNum:])
                        return False, textHeight, textWidth, drawData, remaindData


                # 绘制qq表情符号并更新坐标
                drawData.append([pdfDraw.drawTextQQEmoji, [item["c"]["path"], curX, curY, startC]])
                curX += self.style["qqemojiWidth"]
                if curX - self.style["chatBoxTextStartX"] > textWidth:
                    textWidth = curX - self.style["chatBoxTextStartX"]

            # 处理 "img" 类型的元素
            elif item["t"] == "img":
                data = item["c"]
                path = data["imgPath"]
                name = data["name"]
                imgType = data["imgType"]

                # 如果是图片表情
                if imgType == "marketFace":
                    maxWidth = style["imgEmoMaxSize"]
                    maxHeight = style["imgEmoMaxSize"]
                else:
                    maxWidth = style["imgMaxWidth"] - 2 * self.style["chatBoxPadding"]
                    maxHeight = style["imgMaxHeight"] - 2 * self.style["chatBoxPadding"]

                width, height = drawingQuery.resize_image(data["imgWidth"], data["imgHeight"], maxWidth,
                                                          maxHeight)

                if curY - height - style["textHeight"] < style["contentMaxY"]:
                    remaindData = []
                    remaindData.append(*dataList[itemNum:])
                    return False, textHeight, textWidth, drawData, remaindData
                    drawData.append([pdfDraw.drawImg,
                                     [path, name, width, height, self.style["chatBoxPadding"], startY, startC]])


                # 绘制图片并更新坐标
                drawData.append([pdfDraw.DrawTextImg, [item["c"]["imgPath"], curX, curY]])
                textHeight += height + style["textHeight"]
                curY = height - style["textHeight"]
                curX = self.style["chatBoxTextStartX"]
                if width > textWidth:
                    textWidth = width

        # 留出最后一行的位置
        textHeight += self.style["textHeight"] + self.style["lineSpacing"]
        return True, textHeight, textWidth, drawData, []


class PdfDraw:
    def __init__(self, paths, style):
        self.paths = paths
        self.style = style

        pdfmetrics.registerFont(TTFont(self.style["fontName"], self.paths["fontPath"]))
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

    def drawTextQQEmoji(self, path, x, y, c):
        x = style["pageWidth"] * c + x
        print("emoji", x, y)
        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y,
                                  width=self.style["qqemojiWidth"], height=self.style["qqemojiWidth"],
                                  mask='auto')

    def drawImg(self, path, name, width, height, offsetX, y, c):
        x = style["pageWidth"] * c + self.style["contentStartX"] + offsetX
        print("Img", x, y, width, height)

        if path == "":
            return
        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y - height,
                                  width=width, height=height,
                                  mask='auto')
        text = f"file:  {name}"
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["textHeight"])
        self.pdf_canvas.drawString(x, y - height - self.style["textHeight"], text)


    def drawTextEmoji(self,char, x, y, c):
        1
        # pdf_canvas.setFont('Noto-COLRv1', 12 * mm)
        # pdf_canvas.drawString(7.25 * mm, 10 * mm, "🥺")

    def drawChatBox(self, y, c, width, Hight):
        x = style["pageWidth"] * c + self.style["contentStartX"]
        self.pdf_canvas.setFillColor(self.style["chatBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, Hight, style["chatBoxradius"],
                                  fill=1, stroke=0)


class Generate:
    def __init__(self, path, style):
        self.paths = paths
        self.style = style
        self.pageNum = 1
        self.curY = self.style["contentStartY"]
        self.curC = 0

    def nextPage(self):
        if self.curC + 1 < style["intcolumn"]:
            self.curC = self.curC + 1
        else:
            self.pageNum += 1
            self.curC = 0
            pdfDraw.nextPage(self.pageNum)
        self.curY = self.style["contentStartY"]

    def main(self):
        with open(self.paths["outputDirPath"] + "output/chatData.txt", "r") as f:
            i = 1
            for line in f:
                i += 1
                obj = json.loads(line)
                try:
                    obj["t"]
                except:
                    print(obj)
                    continue
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

                elif obj["t"] == "img":
                    isFinish = False
                    data = obj["c"]
                    self.curY, isFinish = dataprocessor.procImgMessage(data, 0, self.curY, self.curC)
                    if not isFinish:
                        self.nextPage()
                        self.curY, isFinish = dataprocessor.procImgMessage(data, 0, self.curY, self.curC)

                elif obj["t"] == "img":
                    isFinish = False
                    data = obj["c"]
                    self.curY, isFinish = dataprocessor.procImgMessage(data, 0, self.curY, self.curC)
                    if not isFinish:
                        self.nextPage()
                        self.curY, isFinish = dataprocessor.procImgMessage(data, 0, self.curY, self.curC)

                #if i == 80:
                #    break
                self.curY -= style["MassageSpacing"]
                if self.curY <= style["chatBoxTextMaxY"]:
                    self.nextPage()


# 为防止设置项被设为小写，使用自己的optionxform函数
def my_optionxform(optionstr: str) -> str:
    return optionstr

# 读取ini文件
def read_ini_file(file_path: str) -> dict:
    parser = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes=';', comment_prefixes=';')
    parser.optionxform = my_optionxform
    parser.read(file_path, encoding="utf-8")

    data = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            # 尝试将值转换为 int 类型
            if key[0:3] == "int":
                value = int(value)
                data[key] = value
            elif key[0:3] == "flt":
                value = float(value)
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
    style["pageWidth"] = style["pageSize"][0] / style["intcolumn"]  # 纸张宽度

    # 聊天内容
    style["contentStartX"] = style["leftMargin"] + \
                             style["avatarSize"] + 2 * style["avatarMargin"]  # 聊天内容开始X坐标
    style["contentStartY"] = style["pageHeight"] - style["topMargin"]  # 聊天内容开始Y坐标

    style["contentMaxX"] = style["pageWidth"] - style["rightMargin"]  # 聊天内容最大X坐标
    style["contentMaxY"] = style["bottomMargin"] + style["pageFooterTextHeight"]  # 聊天内容最大Y坐标
    style["contentMaxWidth"] = style["pageWidth"] - style["rightMargin"] - style["leftMargin"]
    style["contentCenter"] = style["contentMaxWidth"] / 2 + style["rightMargin"]

    # 聊天框
    style["chatBoxTextStartX"] = style["contentStartX"] + style["chatBoxPadding"]
    style["chatBoxTextMaxX"] = style["contentMaxX"] - style["chatBoxPadding"]
    style["chatBoxTextMaxY"] = style["contentMaxY"] + style["chatBoxPadding"]
    style["chatBoxTextMaxWidth"] = style["chatBoxTextMaxX"] - style["chatBoxTextStartX"]

    # 图像
    style["imgMaxWidth"] = style["pageWidth"] * style["fltimgDrawScale"]
    style["imgMaxHeight"] = style["pageHeight"] * style["fltimgDrawScale"]
    return style


style = procStyle('GeneratePDF_ReportLab_config.ini')
print(style)

fontName = "simhei"

paths = {
    "fontDirPath": "../../lib/fonts/",
    "outputDirPath": "../../"
}
paths["fontPath"] = paths["fontDirPath"] + fontName + ".ttf"
paths["fontInfoPath"] = paths["fontDirPath"] + fontName + "_aspect_ratio.db"

drawingQuery = DrawingQuery(paths, style)
pdfDraw = PdfDraw(paths, style)
dataprocessor = DataProcessor(paths, style)
generate = Generate(paths, style)
generate.main()
pdfDraw.save()

# 以当前日期时间为文件名
cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
dst_file = os.path.join('old', cur_time + ".pdf")

# 判断目标目录是否存在，不存在则创建
if not os.path.exists('old'):
    os.mkdir('old')

# 复制文件到目标目录
shutil.copy("chatData.pdf", dst_file)