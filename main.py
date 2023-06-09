from src import errcode
from src.dataParsing import parsing
from src.generate import GeneratePDF_ReportLab

test = 1
if __name__ == '__main__':
    if test == 1:
        qqParse = parsing.QQParse()
        qqParse.processdb()
    if test == 2:
        generateInit = GeneratePDF_ReportLab.GenerateInit()
        generateInit.run()
