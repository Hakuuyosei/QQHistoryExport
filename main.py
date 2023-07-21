from src import errcode
from src.dataParsing import parsing
from src.generate import GeneratePDF_ReportLab
from src.avatarDownload import download
from src.validateSettings import validateSettings
test = 4
if __name__ == '__main__':
    if test == 1:
        qqParse = parsing.QQParse()
        print(qqParse.configsInit(False, None))
        qqParse.procDb()
    if test == 2:
        generateInit = GeneratePDF_ReportLab.GenerateInit()
        generateInit.run()
    if test == 3:
        download.avatarDownload()
    if test == 4:
        validateSettings.validate_settings(False, None)



