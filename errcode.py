from enum import Enum, auto
#错误码
class codes(Enum):
    NORMAL = auto()
    EMOJI_NOT_EXIST = auto()
    IMG_NOT_EXIST = auto()
    IMG_DESERIALIZATION_ERROR = auto()
    MIXMSG_DESERIALIZATION_ERROR = auto()
    MARKETFACE_NOT_EXIST = auto()

class err_code():
    def __init__(self,):
        #日志等级
        self.LOG_LEVEL_INFO = 0
        self.LOG_LEVEL_WARNING = 1
        self.LOG_LEVEL_ERR = 2

        self.logLevel = self.LOG_LEVEL_WARNING

        self.codes = codes()


    #设置日志等级
    def setLogLevel(self,logLevel):
        self.logLevel = logLevel


    def log(self,tag,logLevel,info):
        if logLevel >= self.logLevel:
            print(tag + " :" + info)


    # 无错误
    def NORMAL(self):
        info = {
            "code": codes.NORMAL
        }
        return info


    # 表情未找到
    def EMOJI_NOT_EXIST(self,emojiType,emojiID):
        info = {
            "code": codes.EMOJI_NOT_EXIST,
            "errinfo": "emoji not EXIST in emoticon,emojiType is {},emojiID is {}".format(emojiType,emojiID),
            "emojiType": emojiType,
            "emojiID": emojiID
        }
        return info

    # 图片未找到
    def IMG_NOT_EXIST(self, imgPath):
        info = {
            "code": codes.IMG_NOT_EXIST,
            "errinfo": "imgPath is not exist in files,imgPath is {}".format(imgPath),
            "imgPath": imgPath
        }
        return info

    #图片反序列化失败
    def IMG_DESERIALIZATION_ERROR(self, data):
        info = {
            "code": codes.IMG_DESERIALIZATION_ERROR,
            "errinfo": "Image information deserialization failed",
            "data": data
        }
        return info

    #混合消息反序列化失败
    def MIXMSG_DESERIALIZATION_ERROR(self, data, pyexc):
        info = {
            "code": codes.MIXMSG_DESERIALIZATION_ERROR,
            "errinfo": "Mixmsg information deserialization failed",
            "data": data,
            "pyexc": pyexc
        }
        return info

    # 图片未找到
    def MARKETFACE_NOT_EXIST(self, imgPath):
        info = {
            "code": codes.MARKETFACE_NOT_EXIST,
            "errinfo": "imgPath is not exist in files,imgPath is {}".format(imgPath),
            "imgPath": imgPath
        }
        return info

