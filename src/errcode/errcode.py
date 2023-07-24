
# 错误码:[提示信息,触发警告需要的次数(每n次警告一次)]
codes = {
    'Normal': ['一切正常', 0],
    'EMOJI_NOT_EXIST': ['表情不存在', 100],
    'IMG_NOT_EXIST': ['图片不存在', 100],
    'MARKETFACE_NOT_EXIST': ['大表情不存在', 100],
    'IMG_DESERIALIZATION_ERROR': ['图片反序列化错误', 100],
    'IMG_UNKNOWN_TYPE': ['图片类型未知', 100],
    'VIDEO_DESERIALIZATION_ERROR': ['视频反序列化错误', 100],
    'VIDEO_UNKNOWN_PATH_FORMAT': ['解析出的视频路径格式不对', 100],
    'VIDEO_NOT_EXIST': ['视频不存在', 100],
    'MIXMSG_DESERIALIZATION_ERROR': ['混合消息反序列化错误', 100],
    'EXTSTR_NOT_EXIST_TARGET': ['EXTSTR不存在目标', 100],
    'EXTSTR_JSON_ERR_DECODE': ['EXTSTR JSON解码错误', 100],
    'IO_ERROR': ['IO读取写入错误', 100],
    'JAVA_DESER_ERR_INPUT_TYPE': ['Java反序列化错误  输入类型错误', 100],
    'JAVA_DESER_JSON_ERR_DECODE': ['Java反序列化错误 - JSON解码错误', 100]
}



class ErrCode():
    def __init__(self, mode):
        self.mode = mode
        #日志等级
        self.LOG_LEVEL_INFO = 0
        self.LOG_LEVEL_WARN = 1
        self.LOG_LEVEL_ERR = 2

        self.logLevel = self.LOG_LEVEL_INFO

        self.codes = codes

        self.counts = {}


    #设置日志等级
    def setLogLevel(self, logLevel):
        """设置日志等级

        :param logLevel: 日志等级
        :return: 无
        """
        self.logLevel = logLevel


    def log(self, tag, logLevel, info):
        """输出日志信息

        :param tag: 发送者标签
        :param logLevel: 日志等级
        :param info: 信息
        :return: 无
        """
        if logLevel >= self.logLevel:
            if self.mode == "print":
                print(tag + " :" + info)
            elif self.mode == "log":
                pass

    def parse_err(self, code, errdata):
        """

        :param code:
        :param errdata:
        :return:
        """
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
            "errinfo": codes[code][0] + f"相关信息：{errdata}"

        }
        return err

    def count_check(self, code):
        """检查错误码有没有过量，及时弹出警告信息
        要求输入code是为了节省性能，只在某code的数量改变时检查

        :param code:错误码
        :return:无
        """
        if self.counts[code] % codes[code][1] == 0:
            errinfo = f"解析时已经发生{self.counts[code]}次“{codes[code][0]}”的错误，请检查你的设置"
            self.log("parse_count", self.LOG_LEVEL_WARN, errinfo)





