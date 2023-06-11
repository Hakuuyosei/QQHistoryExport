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
import time
import shutil

from src.errcode import errcode


class DrawingQuery:
    def __init__(self, ERRCODE, paths, style):
        self.ERRCODE = ERRCODE
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


class PdfDraw:
    def __init__(self, ERRCODE: errcode.err_code, paths, style):
        self.ERRCODE = ERRCODE
        self.paths = paths
        self.style = style

        pdfmetrics.registerFont(TTFont(self.style["fontName"], self.paths["fontPath"]))
        # pdfmetrics.registerFont(TTFont('ColorEmoji', 'fonts/ColorEmoji.ttf'))
        self.pdf_canvas = canvas.Canvas("output/chatData.pdf", pagesize=self.style["pageSize"])
        self.drawPageFooter(1)

    def save(self):
        self.pdf_canvas.save()

    # pdf绘制页脚
    def drawPageFooter(self, pageNum):
        text = self.style["pageFooterText"].replace("$page", str(pageNum))
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["pageFooterTextHeight"])
        self.pdf_canvas.drawString(self.style["leftMargin"], self.style["bottomMargin"], text)

    # pdf翻页
    def nextPage(self, pageNum):
        self.pdf_canvas.showPage()
        self.drawPageFooter(pageNum)

    def drawText(self, text, x, y, c):
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["textHeight"])
        self.pdf_canvas.drawString(x, y, text)

    def drawName(self, text, x, y, c):
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["nameTextColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["nameTextHeight"])
        self.pdf_canvas.drawString(x, y, text)

    def drawTipText(self, text, x, y, c):
        self.pdf_canvas.setFillColor(self.style["tipTextColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["tipTextHeight"])
        x = self.style["pageWidth"] * c + self.style["contentCenter"]
        y = y
        self.pdf_canvas.drawCentredString(x, y, text)

    def drawTextQQEmoji(self, path, x, y, c):
        x = self.style["pageWidth"] * c + x
        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y,
                                  width=self.style["qqemojiWidth"], height=self.style["qqemojiWidth"],
                                  mask='auto')

    def drawImg(self, path, name, width, height, x, y, c):
        x = self.style["pageWidth"] * c + x
        # print("Img", x, y, width, height)

        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y + self.style["textHeight"],
                                  width=width, height=height,
                                  mask='auto')
        text = f"file:  {name}"
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["textHeight"])
        self.pdf_canvas.drawString(x, y, text)

    def drawTextEmoji(self, char, x, y, c):
        1
        # pdf_canvas.setFont('Noto-COLRv1', 12 * mm)
        # pdf_canvas.drawString(7.25 * mm, 10 * mm, "🥺")

    def drawChatBox(self, width, hight, x, y, c):
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["chatBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=1, stroke=0)

    def drawErrBox(self, width, hight, x, y, c):
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setStrokeColor(self.style["chatBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=0, stroke=1)

    def drawreplyBox(self, width, hight, x, y, c):
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["replyBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=1, stroke=0)

    def drawAvatar(self, path, size, x, y, c):
        x = self.style["pageWidth"] * c + x
        # print("Img", x, y, width, height)

        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y,
                                  width=size, height=size,
                                  mask='auto')

    def bookmark(self, Str, y, level):
        self.pdf_canvas.addOutlineEntry(Str, Str, level)
        self.pdf_canvas.bookmarkHorizontalAbsolute(Str, y, left=0, fit='XYZ')


# drawData说明：[函数,[函数参数],[x,y,c]]
# DataProcessor的函数不直接绘制内容，而是返回drawData
class DataProcessor:
    def __init__(self, ERRCODE: errcode.err_code, paths, style, senders, pdfDraw: PdfDraw, drawingQuery: DrawingQuery):
        self.drawingQuery = drawingQuery
        self.pdfDraw = pdfDraw
        self.ERRCODE = ERRCODE
        self.paths = paths
        self.style = style
        self.senders = senders

    def procAvatar(self, senderUin, heightSpace):
        MsgHeight = self.style["avatarSize"] + self.style["avatarMargin"]
        MsgWidth = self.style["avatarSize"] + 2 * self.style["avatarMargin"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None

        senderAvatarPath = self.senders[senderUin][1]
        detaY = - self.style["avatarSize"]
        drawData = [[self.pdfDraw.drawAvatar, [senderAvatarPath, self.style["avatarSize"]],
                     [-MsgWidth, detaY, 0]]]

        return True, MsgHeight, drawData

    def procName(self, senderUin, heightSpace):
        MsgHeight = self.style["nameTextHeight"] + self.style["nameSpacing"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None

        senderName = self.senders[senderUin][0]
        detaY = - self.style["nameTextHeight"]
        drawData = [[self.pdfDraw.drawName, [senderName], [0, detaY, 0]]]

        return True, MsgHeight, drawData

    def procErrMessage(self, data, heightSpace):
        text = ""
        if self.style["errShowDetails"] == "True":
            text = data["e"]["errinfo"]
        if self.style["errShowPYDetails"] == "True":
            if "pyexc" in data["e"]:
                text += "\n" + data["e"]["pyexc"]

        if text == "":
            drawText = f"错误消息，消息类型：{data['t']}"
        else:
            drawText = f"错误消息，消息类型：{data['t']}\n{text}"
        drawData = [{
            "t": "m",
            "c": {"m": drawText}
        }]
        isFinish = False
        isFinish, textHeight, textWidth, drawData, remaindData \
            = self.processMessageList(drawData, heightSpace)

        errBoxHeight = textHeight + 2 * self.style["chatBoxPadding"]
        errBoxWidth = textWidth + 2 * self.style["chatBoxPadding"]
        errBoxY = - errBoxHeight

        if isFinish:
            # 绘制错误框
            for item in drawData:
                # 将内容偏移
                item[2][0] += self.style["chatBoxPadding"]
            drawData.insert(0, [self.pdfDraw.drawErrBox, [errBoxWidth, errBoxHeight], [0, errBoxY, 0]])
            return isFinish, errBoxHeight, drawData
        return isFinish, errBoxHeight, None

    def procTimeMessage(self, data, heightSpace):
        text = data
        MsgHeight = self.style["tipTextHeight"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None
        drawData = [[self.pdfDraw.drawTipText, [text], [0, - self.style["tipTextHeight"], 0]]]
        return True, MsgHeight, drawData

    def procTipMessage(self, data, heightSpace):
        text = data["c"]["text"]
        MsgHeight = self.style["tipTextHeight"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None
        drawData = [[self.pdfDraw.drawTipText, [text], [0, - self.style["tipTextHeight"], 0]]]
        return True, MsgHeight, drawData

    def procImgMessage(self, data, heightSpace):
        path = data["c"]["imgPath"]
        name = data["c"]["name"]
        imgType = data["c"]["imgType"]

        # 使用PIL读取图片的真实长宽
        with Image.open(self.paths["outputDirPath"] + path) as img:
            imgWidth, imgHeight = img.size
        # 如果是图片表情
        if imgType == "marketface":
            maxWidth = self.style["imgEmoMaxSize"]
            maxHeight = self.style["imgEmoMaxSize"]
        else:
            maxWidth = self.style["imgMaxWidth"]
            maxHeight = self.style["imgMaxHeight"]

        width, height = self.drawingQuery.resize_image(imgWidth, imgHeight, maxWidth, maxHeight)

        detaY = - height - self.style["textHeight"]
        drawData = [[self.pdfDraw.drawImg, [path, name, width, height], [0, detaY, 0]]]

        MsgHeight = self.style["tipTextHeight"] + height
        if MsgHeight > heightSpace:
            return False, MsgHeight, None
        return True, MsgHeight, drawData

    def procChatBoxMessage(self, dataList, heightSpace):
        isFinish = False
        isStart = False
        isFinish, textHeight, textWidth, drawData, remaindData \
            = self.processMessageList(dataList, heightSpace - self.style["chatBoxPadding"])

        chatBoxHeight = textHeight + 2 * self.style["chatBoxPadding"]
        chatBoxWidth = textWidth + 2 * self.style["chatBoxPadding"]
        chatBoxY = - chatBoxHeight

        # 绘制聊天框
        if len(drawData) != 0:
            isStart = True

            for item in drawData:
                # 将内容偏移到聊天框内
                item[2][0] += self.style["chatBoxPadding"]
                item[2][1] -= self.style["chatBoxPadding"]

            remaindData.insert(0, {
                "t": "m",
                "c": {"m": "【续上：】"}
            })
            drawData.insert(0, [self.pdfDraw.drawChatBox, [chatBoxWidth, chatBoxHeight], [0, chatBoxY, 0]])
        return isFinish, chatBoxHeight, drawData, isStart, remaindData

    def processMessageList(self, dataList, heightSpace):
        def lineBreak():
            nonlocal buffer, bufStartX, curX, curY, heightSpace, textHeight, textWidth
            if buffer != "":
                # 绘制缓冲区字符
                drawData.append([self.pdfDraw.drawText, [buffer], [bufStartX, curY - heightSpace, 0]])
                buffer = ""

            # 更新当前坐标到下一行开头，并清空暂存字符串
            if curX > textWidth:
                textWidth = curX
            curX = 0
            bufStartX = curX

            textHeight += self.style["textHeight"] + self.style["lineSpacing"]

            if curY - self.style["textHeight"] - self.style["lineSpacing"] < 0:
                return False
            else:
                curY -= self.style["textHeight"] + self.style["lineSpacing"]
                return True

        buffer = ""
        drawData = []
        textWidth = 0
        textHeight = 0
        curX = 0
        curY = heightSpace
        bufStartX = 0
        lastItem = "start"


        # 遍历列表中的每一个元素
        for itemNum in range(len(dataList)):
            item = dataList[itemNum]
            # 处理 "m" 类型的元素
            if item["t"] == "m":
                if lastItem in ["start", "img", "reply"]:
                    # 校正初次换行
                    textHeight -= self.style["textHeight"] + self.style["lineSpacing"]
                    if not lineBreak():
                        # 没有空间用来换行
                        return False, textHeight, textWidth, drawData, dataList[itemNum:]
                    else:
                        curY += self.style["lineSpacing"]

                lastItem = "m"
                # 暂存一行中的文本
                buffer = ""
                # 遍历字符串中的每一个字符
                msgStr = item["c"]["m"]
                for charNum in range(len(msgStr)):
                    character = msgStr[charNum]
                    # 判断字符是否为表情符号
                    if self.drawingQuery.isEmoji(character):
                        # 如果是表情符号，则绘制符号，并更新当前坐标

                        if buffer != "":
                            drawData.append([self.pdfDraw.drawText, [buffer], [bufStartX, curY - heightSpace, 0]])
                            buffer = ""

                        drawData.append([self.pdfDraw.drawTextEmoji, [character], [curX, curY - heightSpace, 0]])
                        curX += self.style["emojiWidth"]
                        bufStartX = curX + self.style["emojiWidth"]

                    if character == "\n":
                        if not lineBreak():
                            remaindData = []
                            item["c"]["m"] = msgStr[charNum:]
                            remaindData.append(item)
                            if dataList[itemNum + 1:] != []:
                                remaindData.extend(dataList[itemNum + 1:])
                            return False, textHeight, textWidth, drawData, remaindData

                    else:
                        # 如果不是表情符号，先查询其宽度
                        charWidth = self.drawingQuery.queryCharWidth(character)
                        # 判断是否需要换行
                        if curX + charWidth > self.style["chatBoxTextMaxWidth"]:
                            # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则将暂存字符串绘制出来并换行
                            if not lineBreak():
                                remaindData = []
                                item["c"]["m"] = msgStr[charNum:]
                                remaindData.append(item)
                                if dataList[itemNum + 1:] != []:
                                    remaindData.extend(dataList[itemNum + 1:])
                                return False, textHeight, textWidth, drawData, remaindData

                        # 将当前字符加入缓冲区中
                        buffer += character
                        curX += charWidth
                # 处理剩余的暂存字符串
                if buffer:
                    if curX > textWidth:
                        textWidth = curX

                    drawData.append([self.pdfDraw.drawText, [buffer], [bufStartX, curY - heightSpace, 0]])
                    bufStartX = curX


            # 处理 qqemoji 类型的元素
            elif item["t"] == "qqemoji":
                if lastItem in ["start", "img", "reply"]:
                    # 校正初次换行
                    textHeight -= self.style["textHeight"] + self.style["lineSpacing"]
                    if not lineBreak():
                        # 没有空间用来换行
                        return False, textHeight, textWidth, drawData, dataList[itemNum:]
                    else:
                        curY += self.style["lineSpacing"]

                lastItem = "qqemoji"
                if item["e"] == self.ERRCODE.codes.NORMAL.value:
                    if curX + self.style["qqemojiWidth"] > self.style["MaxchatBoxTextWidth"]:
                        # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则先将暂存字符串绘制出来
                        if not lineBreak():
                            remaindData = []
                            remaindData.extend(dataList[itemNum:])
                            return False, textHeight, textWidth, drawData, remaindData

                # 绘制qq表情符号并更新坐标
                drawData.append([self.pdfDraw.drawTextQQEmoji, [item["c"]["path"]], [curX, curY - heightSpace, 0]])
                curX += self.style["qqemojiWidth"]
                if curX > textWidth:
                    textWidth = curX



            elif item["t"] == "reply":
                lastItem = "reply"
                sourceMsgSenderUin = item["c"]["sourceMsgSenderUin"]
                if sourceMsgSenderUin in self.senders:
                    senderInfo = self.senders["sourceMsgSenderUin"]
                else:
                    senderInfo = sourceMsgSenderUin
                sourceMsgTime = item["c"]["sourceMsgTime"]
                sourceMsgTimeStr = time.strftime("%m月%d日 %H:%M", time.localtime(sourceMsgTime))
                sourceMsgText = item["c"]["sourceMsgText"]
                sourceMsgInfo = f"\n{senderInfo} {sourceMsgTimeStr}\n{sourceMsgText}"

                replyMsgHeight = 0
                replyMsgWidth = 0
                replyMsgCurY = curY
                # 暂存一行中的文本
                buffer = ""
                buffers = []
                curX = 0
                # 遍历字符串中的每一个字符
                for charNum in range(len(sourceMsgInfo)):
                    character = sourceMsgInfo[charNum]

                    if character == "\n":
                        buffers.append([buffer, replyMsgCurY])
                        buffer = ""
                        replyMsgHeight += self.style["textHeight"] + self.style["lineSpacing"]
                        replyMsgCurY -= self.style["textHeight"] + self.style["lineSpacing"]
                        curX = 0

                    else:
                        charWidth = self.drawingQuery.queryCharWidth(character)
                        # 判断是否需要换行
                        if curX + charWidth > self.style["chatBoxTextMaxWidth"] - 2 * self.style["chatBoxPadding"]:
                            # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则将暂存字符串绘制出来并换行
                            buffers.append([buffer, replyMsgCurY])
                            buffer = ""
                            replyMsgHeight += self.style["textHeight"] + self.style["lineSpacing"]
                            replyMsgCurY -= self.style["textHeight"] + self.style["lineSpacing"]

                            curX = 0

                        # 将当前字符加入缓冲区中
                        buffer += character
                        curX += charWidth
                        if curX > replyMsgWidth:
                            replyMsgWidth = curX

                # 处理剩余的暂存字符串
                if buffer:
                    if curX > replyMsgWidth:
                        replyMsgWidth = curX
                    buffers.append([buffer, replyMsgCurY])
                    buffer = ""
                    replyMsgHeight += self.style["textHeight"] + self.style["lineSpacing"]
                    replyMsgCurY -= self.style["textHeight"] + self.style["lineSpacing"]
                    curX = 0

                if replyMsgCurY < 0:
                    remaindData = []
                    remaindData.extend(dataList[itemNum:])
                    return False, textHeight, textWidth, drawData, remaindData

                if replyMsgWidth > textWidth:
                    textWidth = replyMsgWidth
                textHeight += replyMsgHeight
                drawData.append([self.pdfDraw.drawChatBox, [replyMsgWidth, textHeight], [0, curY, 0]])
                curY -= replyMsgHeight
                for bufferItem, drawY in buffers:
                    drawData.append([self.pdfDraw.drawText, [bufferItem], [self.style["chatBoxPadding"], drawY - heightSpace, 0]])


            # 处理 "img" 类型的元素
            elif item["t"] == "img":
                lastItem = "img"
                if item["e"] == self.ERRCODE.codes.NORMAL.value:
                    data = item["c"]
                    path = data["imgPath"]
                    name = data["name"]
                    imgType = data["imgType"]

                    # 如果是图片表情
                    if imgType == "marketFace":
                        maxWidth = self.style["imgEmoMaxSize"]
                        maxHeight = self.style["imgEmoMaxSize"]
                    else:
                        maxWidth = self.style["imgMaxWidth"] - 2 * self.style["chatBoxPadding"]
                        maxHeight = self.style["imgMaxHeight"] - 2 * self.style["chatBoxPadding"]

                    width, height = self.drawingQuery.resize_image(data["imgWidth"], data["imgHeight"], maxWidth,
                                                                   maxHeight)

                    if curY - height - self.style["textHeight"] < 0:
                        remaindData = []
                        remaindData.extend(dataList[itemNum:])
                        return False, textHeight, textWidth, drawData, remaindData

                    # 绘制图片并更新坐标
                    drawData.append([self.pdfDraw.drawImg,
                                     [path, name, width, height], [0, curY, 0]])
                    textHeight += height + self.style["textHeight"]
                    curY -= height + self.style["textHeight"]
                    curX = 0
                    if width > textWidth:
                        textWidth = width

        # 留出最后一行的位置
        textHeight += self.style["textHeight"] + self.style["lineSpacing"]
        return True, textHeight, textWidth, drawData, []


class Generate:
    def __init__(self, ERRCODE: errcode.err_code, path, style, pdfDraw: PdfDraw, dataprocessor: DataProcessor):
        self.pdfDraw = pdfDraw
        self.dataprocessor = dataprocessor
        self.ERRCODE = ERRCODE
        self.paths = path
        self.style = style
        self.pageNum = 1
        self.curY = self.style["contentStartY"]
        self.curC = 0
        self.lastTime = 0
        self.lastDate = 0
        self.lastMonth = 0
        self.lastYear = 0

        self.ec = self.ERRCODE.codes
        self.normalerr = [self.ec.IMG_UNKNOWN_TYPE_ERROR.value, self.ec.IMG_DESERIALIZATION_ERROR.value,
                          self.ec.IMG_NOT_EXIST.value,
                          self.ec.MIXMSG_DESERIALIZATION_ERROR.value,
                          self.ec.MARKETFACE_NOT_EXIST.value,
                          self.ec.ALL_EXTSTR_NOT_EXIST_TARGET.value
                          ]
        self.normalcode = self.ec.NORMAL.value

    def nextPage(self):
        if self.curC + 1 < self.style["intcolumn"]:
            self.curC = self.curC + 1
        else:
            self.pageNum += 1
            self.curC = 0
            self.pdfDraw.nextPage(self.pageNum)
        self.curY = self.style["contentStartY"]

    # 处理时间，是否显示时间等
    def procTime(self, thisTime):
        thisDate = time.strftime("%Y年%m月%d日", time.localtime(thisTime))
        thisMonth = time.strftime("%Y年%m月", time.localtime(thisTime))
        thisYear = time.strftime("%Y年", time.localtime(thisTime))
        timeStr = time.strftime("%Y年%m月%d日 %H:%M", time.localtime(thisTime))

        if thisYear != self.lastYear:
            self.drawMsg(self.dataprocessor.procTimeMessage, thisYear, False, False, False)
            self.pdfDraw.bookmark(thisYear, self.curY + self.style["tipTextHeight"], 0)
        if thisMonth != self.lastMonth:
            self.drawMsg(self.dataprocessor.procTimeMessage, thisMonth, False, False, False)
            self.pdfDraw.bookmark(thisMonth, self.curY + self.style["tipTextHeight"], 1)
        if thisDate != self.lastDate:
            self.drawMsg(self.dataprocessor.procTimeMessage, thisDate, False, False, False)
            self.pdfDraw.bookmark(thisDate, self.curY + self.style["tipTextHeight"], 2)

        # 相差n分钟,添加时间标签
        diffMin = abs(self.lastTime - thisTime) / 60
        if diffMin >= self.style["intDiffMin"]:
            self.drawMsg(self.dataprocessor.procTimeMessage, timeStr, False, False, False)

            self.curY -= self.style["MassageSpacing"]
            if self.curY <= self.style["contentMaxY"]:
                self.nextPage()

        self.lastTime = thisTime
        self.lastDate = thisDate
        self.lastMonth = thisMonth
        self.lastYear = thisYear

    def drawDataRun(self, drawData, StartX, StartY, StartC):
        for item in drawData:
            item[2][0] = item[2][0] + StartX
            item[2][1] = item[2][1] + StartY
            item[2][2] = item[2][2] + StartC
            # py语法糖，将item[1]的所有项作为参数给函数item[0]
            item[0](*item[1], *item[2])

    def drawMsg(self, drawFunc, msgData, isDivisible, isWithAvatar, isNeedErr):
        """
        绘制消息

        :param drawFunc:绘制消息函数
        :param msgData:消息内容
        :param isDivisible:消息是否可分割
        :param isWithAvatar:是否显示头像
        :param isNeedErr:是否需要错误处理
        :return:
        """
        isShowAvatar = False
        if self.style["avatarShow"] == "True" and isWithAvatar:
            # 若消息有头像，且设置了avatarShow则显示头像
            isShowAvatar = True
            startX = self.style["contentStartX"]
        else:
            startX = self.style["leftMargin"]

        isShowName = False
        if self.style["nameShow"] == "True" and isWithAvatar:
            # 若消息有头像，且设置了nameShow则显示名称
            isShowName = True


        if isNeedErr:
            if msgData["e"]["code"] != self.normalcode:
                if msgData["e"]["code"] in self.normalerr:
                    self.drawMsg(self.dataprocessor.procErrMessage, msgData, False, True, False)
                    return

        drawDataAva = []
        msgHeightAva = 0
        drawDataName = []
        msgHeightName = 0
        
        senderInfoStartY = self.curY
        SenderInfoHeightSpace = self.curY - self.style["contentMaxY"]
        if isShowName:
            isFinishName, msgHeightName, drawDataName = self.dataprocessor.procName(msgData["s"], SenderInfoHeightSpace)
            if not isFinishName:
                self.nextPage()
                SenderInfoHeightSpace = self.curY - self.style["contentMaxY"]
                senderInfoStartY = self.curY
                isFinishName, msgHeightName, drawDataName = self.dataprocessor.procName(msgData["s"], SenderInfoHeightSpace)
                
        
        if isShowAvatar:
            isFinishAva, msgHeightAva, drawDataAva = self.dataprocessor.procAvatar(msgData["s"], SenderInfoHeightSpace)
            if not isFinishAva:
                self.nextPage()
                SenderInfoHeightSpace = self.curY - self.style["contentMaxY"]
                senderInfoStartY = self.curY
                isFinishAva, msgHeightAva, drawDataAva = self.dataprocessor.procAvatar(msgData["s"], SenderInfoHeightSpace)
                # msgHeight = max(msgHeight, msgHeightAva)

        heightSpace = self.curY - self.style["contentMaxY"] - msgHeightName
        startY = self.curY - msgHeightName

        drawDataSenderInfo = []
        if drawDataAva != []:
            drawDataSenderInfo.extend(drawDataAva)
        if drawDataName != []:
            drawDataSenderInfo.extend(drawDataName)
        msgHeightSender = max(msgHeightAva, msgHeightName)

        if not isDivisible:
            isFinish, msgHeight, drawData = drawFunc(msgData, heightSpace)
            if not isFinish:
                self.nextPage()
                heightSpace = self.curY - self.style["contentMaxY"] - msgHeightName
                startY = self.curY - msgHeightName
                senderInfoStartY = self.curY
                isFinish, msgHeight, drawData = drawFunc(msgData, heightSpace)

            if isShowAvatar or isShowName:
                self.drawDataRun(drawDataSenderInfo, startX, senderInfoStartY, self.curC)
            self.drawDataRun(drawData, startX, startY, self.curC)
            self.curY -= max(msgHeight + msgHeightName, msgHeightSender)

        else:  # Divisible
            isFinish = False
            remaindData = msgData["c"]
            while not isFinish:
                avatarY = self.curY
                isFinish, msgHeight, drawData, isStart, remaindData = drawFunc(
                    remaindData, heightSpace)
                # if isStart: avatarY = self.curY
                if isShowAvatar or isShowName:
                    self.drawDataRun(drawDataSenderInfo, startX, senderInfoStartY, self.curC)
                self.drawDataRun(drawData, startX, startY, self.curC)
                self.curY -= max(msgHeight + msgHeightName, msgHeightSender)
                if not isFinish:
                    self.nextPage()
                    heightSpace = self.curY - self.style["contentMaxY"] - msgHeightName
                    startY = self.curY - msgHeightName
                    senderInfoStartY = self.curY

    def main(self):
        with open(self.paths["outputDirPath"] + "output/chatData.txt", "r") as f:
            i = 1

            for line in f:
                obj = json.loads(line)
                i += 1
                try:
                    obj["t"]
                except:
                    print(obj)
                    continue

                self.procTime(obj["i"])
                # 消息类型
                if obj["t"] == "msg":
                    self.drawMsg(self.dataprocessor.procChatBoxMessage, obj, True, True, True)

                elif obj["t"] == "revoke":
                    self.drawMsg(self.dataprocessor.procTipMessage, obj, False, True, True)

                elif obj["t"] == "tip":
                    self.drawMsg(self.dataprocessor.procTipMessage, obj, False, False, True)


                elif obj["t"] == "img":
                    self.drawMsg(self.dataprocessor.procImgMessage, obj, False, True, True)

                # if i == 80:
                #    break
                self.curY -= self.style["MassageSpacing"]
                if self.curY <= self.style["contentMaxY"]:
                    self.nextPage()


# 为防止设置项被设为小写，使用自己的optionxform函数
def my_optionxform(optionstr: str) -> str:
    return optionstr


class GenerateInit:
    # 读取ini文件
    def read_ini_file(self, file_path: str) -> dict:
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

    # 加载style
    def procStyle(self, file_path):
        style = self.read_ini_file(file_path)
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

    # 读取发送者内容
    def readSenderInfo(self):
        with open('output/senders/senders.json', encoding='utf-8') as f:
            senders = json.load(f)

        return senders

    def run(self):
        style = self.procStyle('config/GeneratePDF_ReportLab_config.ini')
        senders = self.readSenderInfo()
        print(style)

        fontName = "simhei"

        paths = {
            "fontDirPath": "lib/fonts/",
            "outputDirPath": ""
        }
        paths["fontPath"] = paths["fontDirPath"] + fontName + ".ttf"
        paths["fontInfoPath"] = paths["fontDirPath"] + fontName + "_aspect_ratio.db"

        ERRCODE = errcode.err_code()

        drawingQuery = DrawingQuery(ERRCODE, paths, style)

        pdfDraw = PdfDraw(ERRCODE, paths, style)
        dataprocessor = DataProcessor(ERRCODE, paths, style, senders, pdfDraw, drawingQuery)
        generate = Generate(ERRCODE, paths, style, pdfDraw, dataprocessor)
        generate.main()
        pdfDraw.save()

        # 以当前日期时间为文件名
        cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        dst_file = os.path.join('old', cur_time + ".pdf")

        # 判断目标目录是否存在，不存在则创建
        if not os.path.exists('old'):
            os.mkdir('old')

        # 复制文件到目标目录
        shutil.copy("output/chatData.pdf", dst_file)
