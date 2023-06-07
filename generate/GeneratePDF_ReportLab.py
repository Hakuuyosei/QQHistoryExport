from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Frame, Paragraph, Flowable


# 定义自定义的Flowable子类
class RoundedRectangle(Flowable):
    def __init__(self, width, height, radius, fill_color=None):
        super().__init__()
        self.width = width
        self.height = height
        self.radius = radius
        self.fill_color = fill_color or colors.white

    def wrap(self, *args):
        return (self.width, self.height)

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        self.canv.roundRect(0, 0, self.width, self.height, self.radius, stroke=0, fill=1)


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
