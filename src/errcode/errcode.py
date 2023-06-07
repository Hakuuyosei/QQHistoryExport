from enum import Enum, auto

# 错误码

class codes(Enum):
    NORMAL = auto()
    EMOJI_NOT_EXIST = auto()
    IMG_NOT_EXIST = auto()
    IMG_DESERIALIZATION_ERROR = auto()
    IMG_UNKNOWN_TYPE_ERROR = auto()
    MIXMSG_DESERIALIZATION_ERROR = auto()
    MARKETFACE_NOT_EXIST = auto()
    ALL_EXTSTR_NOT_EXIST_TARGET = auto()

class err_code():
    def __init__(self,):
        #日志等级
        self.LOG_LEVEL_INFO = 0
        self.LOG_LEVEL_WARNING = 1
        self.LOG_LEVEL_ERR = 2

        self.logLevel = self.LOG_LEVEL_WARNING

        self.codes = codes


    #设置日志等级
    def setLogLevel(self,logLevel):
        self.logLevel = logLevel


    def log(self, tag, logLevel, info):
        if logLevel >= self.logLevel:
            print(tag + " :" + info["errinfo"])
            if "pyexc" in info.keys():
                print(info["pyexc"])


    # 无错误
    def NORMAL(self):
        info = {
            "code": codes.NORMAL.value
        }
        return info


    # 表情未找到
    def EMOJI_NOT_EXIST(self,qqemojiVer,emojiID):
        info = {
            "code": codes.EMOJI_NOT_EXIST.value,
            "errinfo": "emoji not EXIST in emoticon,emojiType is {},emojiID is {}".format(qqemojiVer, emojiID),
            "qqemojiVer": qqemojiVer,
            "emojiID": emojiID
        }
        self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

    # 图片未找到
    def IMG_NOT_EXIST(self, data):
        info = {
            "code": codes.IMG_NOT_EXIST.value,
            "errinfo": "imgPath is not exist in files,imgPath is {}".format(data),
            "data": data
        }
        #self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

    # 图片反序列化失败
    def IMG_DESERIALIZATION_ERROR(self, data):
        info = {
            "code": codes.IMG_DESERIALIZATION_ERROR.value,
            "errinfo": "Image information deserialization failed",
            "data": data
        }
        self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

    # 图片类型判断失败
    def IMG_UNKNOWN_TYPE_ERROR(self, data):
        info = {
            "code": codes.IMG_UNKNOWN_TYPE_ERROR.value,
            "errinfo": "Unknown type for this image : {}".format(data),
            "data": data
        }
        self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

    # 混合消息反序列化失败
    def MIXMSG_DESERIALIZATION_ERROR(self, data, pyexc):
        info = {
            "code": codes.MIXMSG_DESERIALIZATION_ERROR.value,
            "errinfo": "Mixmsg information deserialization failed",
            "data": data,
            "pyexc": pyexc
        }
        self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

    # MARKETFACE未找到
    def MARKETFACE_NOT_EXIST(self, data):
        info = {
            "code": codes.MARKETFACE_NOT_EXIST.value,
            "errinfo": "imgPath is not exist in files,imgPath is {}".format(data),
            "data": data
        }
        self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

    # 在extstr中没有找到目标字段
    def ALL_EXTSTR_NOT_EXIST_TARGET(self, data, target):
        info = {
            "code": codes.ALL_EXTSTR_NOT_EXIST_TARGET.value,
            "errinfo": "The target field({}) was not found in extstr {}".format(target, data),
            "data": data
        }
        self.log("PARSE", self.LOG_LEVEL_ERR, info)
        return info

