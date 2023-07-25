from src import errcode
from src.dataParsing import parsing
from src.generate import GeneratePDF_ReportLab
from src.avatarDownload import download
from src.validateSettings import validateSettings
from src.errcode import errcode
from src.GUI import GUI
test = 5
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
        validate_settings = validateSettings.ValidateSettings()
        validate_settings.validate(True, 'config/parse_config.json')
    if test == 5:
        err_code = errcode.ErrCode("print")

        validate_settings = validateSettings.ValidateSettings()
        state, info, configs = validate_settings.validate(True, 'config/parse_config.json')
        if state:
            qq_parse = parsing.QQParse(configs, err_code)
            qq_parse.procDb()
    if test == 6:
        GUI.gui_init()





