from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
def queryCharWidth(s):
    return 16

def procText(PosiX, PosiY, rowWidth, colWidth, emojiWidth, qqemojiWidth, lst):
    curX = PosiX
    curY = PosiY
    StartX = curX
    buffer = ''
    for item in lst:
        if item[0] == 'm':
            text = item[1]
            for character in text:
                if isEmoji(character):
                    pdfDraw.drawEmoji(character)
                    curX += emojiWidth
                    StartX = curX
                else:
                    charWidth = queryCharWidth(character)
                    if curX + charWidth > rowWidth:
                        pdfDraw.drawText(curX, curY, buffer)
                        curX = PosiX
                        StartX = PosiX
                        curY += colWidth
                        buffer = ''
                    buffer += character
                    curX += charWidth
        elif item[0] == 'qqemoji':
            path = item[2]
            pdfDraw.drawQQEmoji(path, qqemojiWidth)
            curX += qqemojiWidth
            StartX = curX

        elif item[0] == 'img':
            path = item[2]
            pdfDraw.drawQQimg(path)
            curY += colWidth
            curX = PosiX
            StartX = PosiX
    pdfDraw.drawText(buffer)
class pdfDrawing():
    def __init__(self):
        pdfmetrics.registerFont(TTFont('simhei', 'fonts/simhei.ttf'))
        pdfmetrics.registerFont(TTFont('ColorEmoji', 'fonts/ColorEmoji.ttf'))
        self.pdf_canvas = canvas.Canvas("example.pdf", pagesize=A4)
        self.PAGE_HEIGHT = A4[1]
        self.PAGE_WIDTH = A4[0]

    def save(self):
        self.pdf_canvas.save()

    def showPage(self):
        self.pdf_canvas.showPage()

    def drawText(self, x, y):
        self.pdf_canvas.setFont('simhei', 5 * mm)
        self.pdf_canvas.drawString(x * mm, y * mm, "报表")
        
    def drawQQEmoji(self):
        1
    def drawEmoji(self):
        1
        # pdf_canvas.setFont('Noto-COLRv1', 12 * mm)
        # pdf_canvas.drawString(7.25 * mm, 10 * mm, "🥺")
pdfDraw = pdfDrawing()




