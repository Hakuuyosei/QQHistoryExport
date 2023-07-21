from enum import Enum, auto

# 错误码
codes = {
    'Normal': '一切正常',
    'EMOJI_NOT_EXIST': '表情不存在',
    'IMG_NOT_EXIST': '图片不存在',
    'MARKETFACE_NOT_EXIST': '大表情不存在',
    'IMG_DESERIALIZATION_ERROR': '图片反序列化错误',
    'IMG_UNKNOWN_TYPE': '图片类型未知',
    'MIXMSG_DESERIALIZATION_ERROR': '混合消息反序列化错误',
    'EXTSTR_NOT_EXIST_TARGET': 'EXTSTR不存在目标',
    'EXTSTR_JSON_ERR_DECODE': 'EXTSTR JSON解码错误',
    'IO_ERROR': 'IO读取写入错误',
    'JAVA_DESER_ERR_INPUT_TYPE': 'Java反序列化错误  输入类型错误',
    'JAVA_DESER_JSON_ERR_DECODE': 'Java反序列化错误 - JSON解码错误'

}


class err_code():
    def __init__(self, mode):
        self.mode = mode
        #日志等级
        self.LOG_LEVEL_INFO = 0
        self.LOG_LEVEL_WARNING = 1
        self.LOG_LEVEL_ERR = 2

        self.logLevel = self.LOG_LEVEL_WARNING

        self.codes = codes

        self.counts = None


    #设置日志等级
    def setLogLevel(self, logLevel):
        self.logLevel = logLevel


    def log(self, tag, logLevel, info):
        if logLevel >= self.logLevel:
            if self.mode == "print":
                print(tag + " :" + "errinfo")
            elif self.mode == "log":
                pass

    def parse_err(self, code, errdata):
        if code not in codes:
            print(f"code not in codes! code is {code}")
            return {}

        if code == 'Normal':
            return {"s": True}
        if code in self.counts:
            self.counts[code] += 1
        else:
            self.counts[code] = 1

        err = {
            "s": False,
            "errinfo": codes[code] + f"相关信息：{errdata}"

        }
        return {}




