from src import errcode
from src.dataParsing import parsing
from src.generate import GeneratePDF_ReportLab
from src.avatarDownload import download
test = 2
if __name__ == '__main__':
    if test == 1:
        qqParse = parsing.QQParse()
        qqParse.parseInit(True, None)
        qqParse.processdb()
    if test == 2:
        generateInit = GeneratePDF_ReportLab.GenerateInit()
        generateInit.run()
    if test == 3:
        download.avatarDownload()

