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
import emoji

from src.errcode import errcode


class DrawingQuery:
    """PDF查询相关功能，包括字宽，图片大小等

    """
    def __init__(self, ERRCODE: errcode.ErrCode, paths, style):
        """

        :param ERRCODE: errcode.ErrCode
        :param paths: 相关路径字典
        :param style: 样式设置字典
        """
        self.ERRCODE = ERRCODE
        self.paths = paths
        self.style = style

        # 连接数据库
        self.conn = sqlite3.connect(paths["fontInfoPath"])

    def queryCharWidth(self, char):
        """查询字体宽度

        :param char: 字符
        :return: 宽度
        """
        c = self.conn.cursor()
        c.execute(f"SELECT aspect_ratio FROM font_metrics WHERE unicode={ord(char)}")
        result = c.fetchone()

        if result:
            aspect_ratio = result[0]
            # 计算宽度并返回结果
            width = round(aspect_ratio * self.style["textHeight"])
            return width

        return None

    def resize_image(self, img_width, img_height, max_width, max_height):
        """计算图片缩放后的大小

        :param img_width: 图片宽度
        :param img_height: 图片高度
        :param max_width: 最大宽度
        :param max_height: 最大高度
        :return: 新宽度，新高度
        """
        # 比较宽高的大小，计算缩放比例
        ratio = min(max_width / img_width, max_height / img_height)
        # 根据比例计算新的宽高
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        return new_width, new_height

    def convert_filesize(self, size):
        """将以字节为单位的文件大小转换成合适的单位，并保留两位小数。

        :param size: 文件大小，单位为字节。
        :return: 字符串格式的文件大小，包含单位。
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size >= 1024 and index < 4:
            size /= 1024
            index += 1
        return '{:.2f}{}'.format(size, units[index])

    def get_emoji_info(self, str):
        """获取文本中的emoji信息

        :param str: 输入字符串
        :return:

        示例输出：[{'match_start': 2, 'match_end': 5, 'emoji': '👩‍🚀'}, {'match_start': 15, 'match_end': 16, 'emoji': '🚀'}]
        """
        return emoji.emoji_list(str)

    def is_emoji_start(self, emoji_info, pos):
        """输入emoji_info和当前位置，返回当前位置是否是emoji字符的起始位置。
        若是起始位置，则一并返回emoji字符。

        :param emoji_info: 文本中的emoji信息
        :param pos: 当前位置
        :return: 是否在emoji中，若是起始位置则返回emoji
        """
        for e in emoji_info:
            if e['match_start'] == pos:
                return True, e['emoji']
            elif e['match_start'] < pos < e['match_end']:
                return True, None
        return False, None

    def unicode_emoji_to_filename(self, emoji_unicode):
        """将Unicode emoji转为字符串文件名表示

        :param emoji_unicode: 字符
        :return: 文件名
        """
        fileName = "emoji_u"
        for char in emoji_unicode:
            # 获取字符的 Unicode 码并转化为十六进制字符串
            hex_code = hex(ord(char))[2:]  # 去掉 '0x' 前缀
            # 补齐到四位十六进制数
            # hex_code = hex_code.zfill(4)
            if fileName == "emoji_u":
                fileName += hex_code
            else:
                fileName += f"_{hex_code}"
        fileName += ".png"
        return fileName

    def get_unicode_file(self, emoji_unicode):
        """提取emoji文件（彩色emoji）

        :param emoji_unicode: emoji字符
        :return:
        """
        fileName = self.unicode_emoji_to_filename(emoji_unicode)
        filePath = f"output/temp/{fileName}"
        print(filePath, emoji_unicode)

        with sqlite3.connect(self.paths["emojiFontDBPath"]) as conn:
            cursor = conn.execute('''SELECT start_offset, end_offset FROM files_info
                                     WHERE file_name = ?''', (fileName,))
            row = cursor.fetchone()
            if not row:
                print("文件不存在")
                return
            start_offset, end_offset = row

        # 从大文件中还原小文件
        with open(self.paths["emojiFontPath"], "rb") as merged_file, \
                open(filePath, "wb") as output_file:
            merged_file.seek(start_offset)
            output_file.write(merged_file.read(end_offset - start_offset))

        return filePath


class PdfDraw:
    """
    直接操作PDF数据的层，除绘制书签外，一般不直接调用，通过PDF消息处理层调用
    基本上后三个参数为x，y，c，xy为左下角绘制坐标，c为column列数
    """
    def __init__(self, ERRCODE: errcode.ErrCode, drawingQuery: DrawingQuery, paths, style):
        """

        :param ERRCODE: errcode.ErrCode
        :param drawingQuery: DrawingQuery
        :param path: 相关路径字典
        :param style: 样式设置字典
        """

        self.ERRCODE = ERRCODE
        self.drawingQuery = drawingQuery
        self.paths = paths
        self.style = style

        pdfmetrics.registerFont(TTFont(self.style["fontName"], self.paths["fontPath"]))
        if self.style["ifUseColorEmoji"] == "False":
            pdfmetrics.registerFont(TTFont(self.style["EmojiFontName"], self.paths["emojiFontPath"]))
        self.pdf_canvas = canvas.Canvas("output/chatData.pdf", pagesize=self.style["pageSize"])
        self.drawPageFooter(1)

    def save(self):
        """保存PDF文件

        """
        self.pdf_canvas.save()

    # pdf绘制页脚
    def drawPageFooter(self, pageNum):
        """绘制指定页码的页面底部文本

        :param pageNum: 当前页码
        """
        text = self.style["pageFooterText"].replace("$page", str(pageNum))
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["pageFooterTextHeight"])
        self.pdf_canvas.drawString(self.style["leftMargin"], self.style["bottomMargin"], text)

    # pdf翻页
    def nextPage(self, pageNum):
        """结束当前页面，并开始绘制下一页。同时绘制下一页的页面底部文本
        若需翻页请调用Generate.nextPage而不是此函数

        :param pageNum: 当前页码
        """
        self.pdf_canvas.showPage()
        self.drawPageFooter(pageNum)

    def drawText(self, text, x, y, c):
        """绘制文本

        :param text: 要绘制的文本
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["textColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["textHeight"])
        self.pdf_canvas.drawString(x, y, text)

    def drawName(self, text, x, y, c):
        """绘制名称

        :param text: 要绘制的名称文本
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["nameTextColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["nameTextHeight"])
        self.pdf_canvas.drawString(x, y, text)

    def drawTipText(self, text, x, y, c):
        """绘制灰条提示文本

        :param text: 要绘制的提示文本
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        self.pdf_canvas.setFillColor(self.style["tipTextColor"])
        self.pdf_canvas.setFont(self.style["fontName"], self.style["tipTextHeight"])
        x = self.style["pageWidth"] * c + self.style["contentCenter"]
        y = y
        self.pdf_canvas.drawCentredString(x, y, text)

    def drawTextQQEmoji(self, path, x, y, c):
        """绘制QQ表情

        :param path: QQ表情图像的路径
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """

        x = self.style["pageWidth"] * c + x
        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y,
                                  width=self.style["qqemojiWidth"], height=self.style["qqemojiWidth"],
                                  mask='auto')

    def drawImg(self, path, name, width, height, x, y, c):
        """绘制图像并绘制图像名称文本

        :param path: 图像文件的路径
        :param name: 图像的名称
        :param width: 图像的宽度
        :param height: 图像的高度
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
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
        """绘制文本unicode表情

        :param char: 要绘制的emoji字符
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 页绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x - 10

        if self.style["ifUseColorEmoji"] == "False":
            self.pdf_canvas.setFont(self.paths["emojiFontName"], self.style["textHeight"])
            self.pdf_canvas.drawString(x, y, char+"标记🌎")
        elif self.style["ifUseColorEmoji"] == "True":
            path = self.drawingQuery.get_unicode_file(char)
            self.pdf_canvas.drawImage(path, x, y,
                                      width=self.style["emojiWidth"], height=self.style["emojiWidth"],
                                      mask='auto')


    def drawChatBox(self, width, hight, x, y, c):
        """绘制聊天框

        :param width: 聊天框的宽度
        :param hight: 聊天框的高度
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 页绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["chatBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=1, stroke=0)

    def drawErrBox(self, width, hight, x, y, c):
        """绘制错误框

        :param width: 错误框的宽度
        :param hight: 错误框的高度
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setStrokeColor(self.style["chatBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=0, stroke=1)

    def drawReplyBox(self, width, hight, x, y, c):
        """绘制回复框

        :param width: 回复框的宽度
        :param hight: 回复框的高度
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setFillColor(self.style["replyBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=1, stroke=0)

    def drawGeneralBox(self, width, hight, x, y, c):
        """绘制通用框

        :param width: 通用框的宽度
        :param hight: 通用框的高度
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        self.pdf_canvas.setStrokeColor(self.style["generalBoxFillColor"])
        self.pdf_canvas.roundRect(x, y, width, hight, self.style["chatBoxradius"],
                                  fill=0, stroke=1)

    def drawAvatar(self, path, size, x, y, c):
        """绘制头像

        :param path: 头像图像的路径
        :param size: 头像的尺寸
        :param x: 绘制起始点的 x 坐标
        :param y: 绘制起始点的 y 坐标
        :param c: 绘制起始点的 c 坐标（列）
        """
        x = self.style["pageWidth"] * c + x
        # print("Img", x, y, width, height)

        path = self.paths["outputDirPath"] + path
        self.pdf_canvas.drawImage(path, x, y,
                                  width=size, height=size,
                                  mask='auto')

    def bookmark(self, str, y, level):
        """添加书签

        :param str: 书签的名称
        :param y: 书签在页面上的垂直位置
        :param level: 书签的级别
        """
        self.pdf_canvas.addOutlineEntry(str, str, level)
        self.pdf_canvas.bookmarkHorizontalAbsolute(str, y, left=0, fit='XYZ')


class DataProcessor:
    """PDF消息处理层

    接收垂直空间，处理消息数据，返回绘制细节数据drawData
    DataProcessor的函数不直接绘制内容，而是返回drawData
    drawData说明：[函数,[函数参数],[x,y,c]]
    """
    def __init__(self, ERRCODE: errcode.ErrCode, paths, style, senders, pdfDraw: PdfDraw, drawingQuery: DrawingQuery):
        """PDF消息处理层
        接收垂直空间，处理消息数据，返回绘制细节数据

        :param ERRCODE: errcode.ErrCode
        :param path: 相关路径字典
        :param style: 样式设置字典
        :param senders: 发送者信息字典
        :param pdfDraw: PdfDraw
        :param drawingQuery: DrawingQuery
        """

        self.drawingQuery = drawingQuery
        self.pdfDraw = pdfDraw
        self.ERRCODE = ERRCODE
        self.paths = paths
        self.style = style
        self.senders = senders

    def procAvatar(self, senderUin, heightSpace):
        """处理头像绘制相关的细节，并返回绘制细节数据

        :param senderUin: 发送者Uin
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息高度，绘制数据
        """
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
        """处理姓名绘制相关的细节，并返回绘制细节数据

        :param senderUin: 发送者Uin
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息高度，绘制数据
        """
        MsgHeight = self.style["nameTextHeight"] + self.style["nameSpacing"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None

        senderName = self.senders[senderUin][0]
        detaY = - self.style["nameTextHeight"]
        drawData = [[self.pdfDraw.drawName, [senderName], [0, detaY, 0]]]

        return True, MsgHeight, drawData

    def procErrMessage(self, data, heightSpace):
        """根据给定的数据和可用的垂直空间处理错误消息，并返回绘制细节数据
        
        :param data: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息框高度，绘制数据
        """

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

    def procFileMessage(self, data, heightSpace):
        """根据给定的数据和可用的垂直空间处理文件消息，并返回绘制细节数据

        :param data: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息框高度，绘制数据
        """
        fileName = data["c"]["fileName"]
        drawText = f"发送文件：{fileName}"
        if "fileSize" in data["c"]:
            fileSize = data["c"]["fileSize"]
            fileSizeStr = self.drawingQuery.convert_filesize(fileSize)
            drawText += f"\n文件大小：{fileSizeStr}"
        drawData = [{
            "t": "m",
            "c": {"m": drawText}
        }]
        isFinish = False
        isFinish, textHeight, textWidth, drawData, remaindData \
            = self.processMessageList(drawData, heightSpace)

        generalBoxHeight = textHeight + 2 * self.style["chatBoxPadding"]
        generalBoxWidth = textWidth + 2 * self.style["chatBoxPadding"]
        generalBoxY = - generalBoxHeight

        if isFinish:
            # 绘制错误框
            for item in drawData:
                # 将内容偏移
                item[2][0] += self.style["chatBoxPadding"]
            drawData.insert(0, [self.pdfDraw.drawGeneralBox, [generalBoxWidth, generalBoxHeight], [0, generalBoxY, 0]])
            return isFinish, generalBoxHeight, drawData
        return isFinish, generalBoxHeight, None

    def procTimeMessage(self, data, heightSpace):
        """根据给定的数据和可用的垂直空间处理时间信息，并返回绘制细节数据

        :param data: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息框高度，绘制数据
        """
        text = data
        MsgHeight = self.style["tipTextHeight"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None
        drawData = [[self.pdfDraw.drawTipText, [text], [0, - self.style["tipTextHeight"], 0]]]
        return True, MsgHeight, drawData

    def procTipMessage(self, data, heightSpace):
        """根据给定的数据和可用的垂直空间处理灰条提示信息，并返回绘制细节数据

        :param data: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息框高度，绘制数据
        """
        text = data["c"]["text"]
        MsgHeight = self.style["tipTextHeight"]
        if MsgHeight > heightSpace:
            return False, MsgHeight, None
        drawData = [[self.pdfDraw.drawTipText, [text], [0, - self.style["tipTextHeight"], 0]]]
        return True, MsgHeight, drawData

    def procImgMessage(self, data, heightSpace):
        """根据给定的数据和可用的垂直空间处理图片消息，并返回绘制细节数据

        :param data: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息框高度，绘制数据
        """
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
        """根据给定的数据和可用的垂直空间处理带框消息（普通消息，混合消息，回复消息等），并返回绘制细节数据

        :param data: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 是否绘制完毕，消息框高度，绘制数据，在当前页是否已经开始绘制，剩余数据
        """
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
        """根据给定的数据和可用的垂直空间处理混合文本列表，并返回绘制细节数据
        本函数包含计算文本换行，手动文本排版等内容
        注意，一般不直接调用

        :param dataList: 消息数据
        :param heightSpace: 可用的垂直空间
        :return: 文本高度，文本宽度，绘制数据，剩余数据
        """
        def lineBreak():
            """根据当前绘制状态和样式进行换行操作，并更新绘制数据、当前坐标等

            :return: 是否成功换行
            """
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
                emojiInfo = self.drawingQuery.get_emoji_info(item["c"]["m"])
                for charNum in range(len(msgStr)):
                    character = msgStr[charNum]
                    # 判断字符是否为表情符号
                    isInEmoji, emojiStr = self.drawingQuery.is_emoji_start(emojiInfo, charNum)
                    if isInEmoji:
                        if emojiStr:
                            # print(emojiInfo, msgStr)
                            # print(emojiStr, character)
                            # 如果是emoji初位置，则绘制符号，并更新当前坐标
                            if buffer != "":
                                drawData.append([self.pdfDraw.drawText, [buffer], [bufStartX, curY - heightSpace, 0]])
                                buffer = ""


                            if curX + self.style["emojiWidth"] > self.style["chatBoxTextMaxWidth"]:
                                # 如果该字符加上前面已暂存字符串的宽度会超出列宽，则将暂存字符串绘制出来并换行
                                if not lineBreak():
                                    remaindData = []
                                    item["c"]["m"] = msgStr[charNum:]
                                    remaindData.append(item)
                                    if dataList[itemNum + 1:] != []:
                                        remaindData.extend(dataList[itemNum + 1:])
                                    return False, textHeight, textWidth, drawData, remaindData
                            curX += self.style["emojiWidth"]
                            bufStartX = curX
                            drawData.append([self.pdfDraw.drawTextEmoji, [emojiStr], [curX, curY - heightSpace, 0]])
                            if curX > textWidth:
                                textWidth = curX


                        else:
                            continue

                    elif character == "\n":
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
                sourceMsgSenderUin = str(item["c"]["sourceMsgSenderUin"])
                if sourceMsgSenderUin in self.senders:
                    senderInfo = self.senders[sourceMsgSenderUin][0]
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
                    replyMsgHeight += self.style["chatBoxPadding"]
                    replyMsgCurY -= self.style["chatBoxPadding"]
                    curX = 0

                if replyMsgCurY < 0:
                    remaindData = []
                    remaindData.extend(dataList[itemNum:])
                    return False, textHeight, textWidth, drawData, remaindData

                if replyMsgWidth > textWidth:
                    textWidth = replyMsgWidth
                textHeight += replyMsgHeight
                curY -= replyMsgHeight
                drawData.append([self.pdfDraw.drawReplyBox, [replyMsgWidth, textHeight], [0, curY- heightSpace, 0]])
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
    """生成PDF总控制层

    """
    def __init__(self, ERRCODE: errcode.ErrCode, path, style,
                 pdfDraw: PdfDraw, dataprocessor: DataProcessor):
        """

        :param ERRCODE: errcode.ErrCode
        :param path: 相关路径字典
        :param style: 样式设置字典
        :param pdfDraw: PdfDraw
        :param dataprocessor: DataProcessor
        """
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
        """根据当前的页码和列数，判断是否需要翻页或是换列，并更新相关的页码和列数。

        """
        if self.curC + 1 < self.style["intcolumn"]:
            self.curC = self.curC + 1
        else:
            self.pageNum += 1
            self.curC = 0
            self.pdfDraw.nextPage(self.pageNum)
        self.curY = self.style["contentStartY"]

    def procTime(self, thisTime):
        """时间管理，是否显示时间，添加书签等，在绘制每条消息前调用

        :param thisTime: 当前消息时间戳
        :return:
        """
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
        """运行绘制函数

        :param drawData: 格式为[[func,[args],[x,y,c(column)]]]的绘制命令列表
        :param StartX: X偏移量
        :param StartY: Y偏移量
        :param StartC: Column偏移量
        :return:无
        """
        for item in drawData:
            item[2][0] = item[2][0] + StartX
            item[2][1] = item[2][1] + StartY
            item[2][2] = item[2][2] + StartC
            # py语法糖，将item[1]的所有项作为参数给函数item[0]
            item[0](*item[1], *item[2])

    def drawMsg(self, drawFunc, msgData, isDivisible, isWithAvatar, isNeedErr):
        """绘制消息

        :param drawFunc: 绘制消息函数
        :param msgData: 消息内容
        :param isDivisible: 消息是否可分割
        :param isWithAvatar: 消息本身是否显示头像名称
        :param isNeedErr: 是否需要错误处理
        :return:无
        """
        # 判断是否显示头像
        isShowAvatar = False
        # 若设置显示头像，并且此消息类型也需要显示头像
        if self.style["avatarShow"] == "True" and isWithAvatar:
            # 若消息有头像，且设置了avatarShow则显示头像
            isShowAvatar = True
            startX = self.style["contentStartX"]
        else:
            startX = self.style["leftMargin"]

        # 判断是否显示名称
        isShowName = False
        if self.style["nameShow"] == "True" and isWithAvatar:
            # 若消息有头像，且设置了nameShow则显示名称
            isShowName = True

        # 错误处理
        if isNeedErr:
            if msgData["e"]["code"] != self.normalcode:
                if msgData["e"]["code"] in self.normalerr:
                    self.drawMsg(self.dataprocessor.procErrMessage, msgData, False, True, False)
                    return

        # 初始化头像和名称的绘制数据和高度，若不用绘制则会使用初始化的值
        drawDataAva = []
        msgHeightAva = 0
        drawDataName = []
        msgHeightName = 0

        # 发送者信息的起始位置
        senderInfoStartY = self.curY
        SenderInfoHeightSpace = self.curY - self.style["contentMaxY"]

        # 处理名称的绘制数据和高度
        if isShowName:
            isFinishName, msgHeightName, drawDataName = self.dataprocessor.procName(msgData["s"], SenderInfoHeightSpace)
            if not isFinishName:
                # 假如没有绘制成功，需要分页处理
                self.nextPage()
                SenderInfoHeightSpace = self.curY - self.style["contentMaxY"]
                senderInfoStartY = self.curY
                isFinishName, msgHeightName, drawDataName = self.dataprocessor.procName(msgData["s"], SenderInfoHeightSpace)

        # 处理头像的绘制数据和高度
        if isShowAvatar:
            isFinishAva, msgHeightAva, drawDataAva = self.dataprocessor.procAvatar(msgData["s"], SenderInfoHeightSpace)
            if not isFinishAva:
                # 假如没有绘制成功，需要分页处理
                self.nextPage()
                SenderInfoHeightSpace = self.curY - self.style["contentMaxY"]
                senderInfoStartY = self.curY
                isFinishAva, msgHeightAva, drawDataAva = self.dataprocessor.procAvatar(msgData["s"], SenderInfoHeightSpace)
                # msgHeight = max(msgHeight, msgHeightAva)

        # 计算消息内容的起始位置和高度
        heightSpace = self.curY - self.style["contentMaxY"] - msgHeightName
        startY = self.curY - msgHeightName

        # 添加准备绘制细节信息
        drawDataSenderInfo = []
        if drawDataAva != []:
            drawDataSenderInfo.extend(drawDataAva)
        if drawDataName != []:
            drawDataSenderInfo.extend(drawDataName)
        msgHeightSender = max(msgHeightAva, msgHeightName)

        # 绘制不可分割的消息
        if not isDivisible:
            isFinish, msgHeight, drawData = drawFunc(msgData, heightSpace)
            if not isFinish:
                # 假如没有绘制成功，需要分页处理
                self.nextPage()
                heightSpace = self.curY - self.style["contentMaxY"] - msgHeightName
                startY = self.curY - msgHeightName
                senderInfoStartY = self.curY
                isFinish, msgHeight, drawData = drawFunc(msgData, heightSpace)

            # 绘制头像和名称
            if isShowAvatar or isShowName:
                self.drawDataRun(drawDataSenderInfo, startX, senderInfoStartY, self.curC)
            # 绘制消息内容
            self.drawDataRun(drawData, startX, startY, self.curC)
            self.curY -= max(msgHeight + msgHeightName, msgHeightSender)

        # 绘制可分割的消息
        else:
            isFinish = False
            remaindData = msgData["c"]
            while not isFinish:
                isFinish, msgHeight, drawData, isStart, remaindData = drawFunc(
                    remaindData, heightSpace)
                # 绘制头像和名称
                if isStart:
                    # 若在本页/列已经绘制了一部分的消息再绘制头像名称，若没有的话直接换页/列
                    if isShowAvatar or isShowName:
                        self.drawDataRun(drawDataSenderInfo, startX, senderInfoStartY, self.curC)
                # 绘制消息内容
                self.drawDataRun(drawData, startX, startY, self.curC)
                self.curY -= max(msgHeight + msgHeightName, msgHeightSender)
                if not isFinish:
                    # 若没有绘制完成则分页处理
                    self.nextPage()
                    heightSpace = self.curY - self.style["contentMaxY"] - msgHeightName
                    startY = self.curY - msgHeightName
                    senderInfoStartY = self.curY

    def main(self):
        """绘制PDF主函数

        """
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
                    self.drawMsg(self.dataprocessor.procTipMessage, obj, False, False, True)

                elif obj["t"] == "tip":
                    self.drawMsg(self.dataprocessor.procTipMessage, obj, False, False, True)


                elif obj["t"] == "img":
                    self.drawMsg(self.dataprocessor.procImgMessage, obj, False, True, True)

                elif obj["t"] == "file":
                    self.drawMsg(self.dataprocessor.procFileMessage, obj, False, True, True)

                # if i == 80:
                #    break
                self.curY -= self.style["MassageSpacing"]
                if self.curY <= self.style["contentMaxY"]:
                    self.nextPage()


# 为防止设置项被设为小写，使用自己的optionxform函数
def my_optionxform(optionstr: str) -> str:
    return optionstr


class GenerateInit:
    """初始化绘制，加载设置项，初始化绘制层

    """
    def __init__(self):
        pass

    def read_ini_file(self, file_path: str) -> dict:
        """读取给定路径下的INI文件，并返回解析后的字典数据。
        将自动将flt开头的数据转化为float，int同理，其它数据若能转化为数字则转化为mm长度数据

        :param file_path: INI文件的路径
        :return: 解析后的字典数据
        """

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
        """加载给定路径下的样式设置文件，计算有关数据，并返回样式设置数据

        :param file_path: 样式文件的路径
        :return: 样式设置字典
        """
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

    def readSenderInfo(self):
        """读取发送者信息

        :return: 发送者数据字典
        """
        with open('output/senders/senders.json', encoding='utf-8') as f:
            senders = json.load(f)

        return senders

    def run(self):
        """运行PDF绘制

        """
        style = self.procStyle('config/GeneratePDF_ReportLab_config.ini')
        senders = self.readSenderInfo()
        print(style)

        fontName = style["fontName"]
        emojiFontName = style["emojiFontName"]
        paths = {
            "fontDirPath": "resources/fonts/",
            "outputDirPath": ""
        }
        paths["fontPath"] = paths["fontDirPath"] + fontName + ".ttf"
        paths["fontInfoPath"] = paths["fontDirPath"] + fontName + "_aspect_ratio.db"
        if style["ifUseColorEmoji"] == "False":
            paths["emojiFontPath"] = paths["fontDirPath"] + emojiFontName + ".ttf"
        elif style["ifUseColorEmoji"] == "True":
            paths["emojiFontPath"] = paths["fontDirPath"] + f"{emojiFontName}/{emojiFontName}"
            paths["emojiFontDBPath"] = paths["fontDirPath"] + f"{emojiFontName}/{emojiFontName}.db"


        ERRCODE = errcode.ErrCode()

        drawingQuery = DrawingQuery(ERRCODE, paths, style)

        pdfDraw = PdfDraw(ERRCODE, drawingQuery, paths, style)
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
