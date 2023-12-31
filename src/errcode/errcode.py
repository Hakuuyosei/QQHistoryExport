import os

# 错误码:[提示信息,触发警告需要的次数(每n次警告一次)]
codes = {
    'Normal': ['一切正常', 0],
    'UNKNOWN_MSG_TYPE': ['未知消息类型', 100],
    'DIDNOT_PARSE_MSG': ['解析不完全消息(解析代码不完全)', 100],
    'TEXT_UNICODE_DECODE_ERROR': ['文本消息utf8解码失败', 20],
    'FILE_UNKNOWN_FORMAT': ['文件信息格式未知', 100],
    'EMOJI_NOT_EXIST': ['QQ表情在resourses中不存在', 100],
    'IMG_NOT_EXIST': ['图片不存在', 100],
    'MARKETFACE_NOT_EXIST': ['大表情在resourses中不存在', 100],
    'MARKETFACE_DESERIALIZATION_ERROR': ['大表情反序列化错误', 30],
    'IMG_DESERIALIZATION_ERROR': ['图片反序列化错误', 30],
    'IMG_UNKNOWN_TYPE': ['图片类型未知', 100],
    'VIDEO_DESERIALIZATION_ERROR': ['视频反序列化错误', 100],
    'VIDEO_UNKNOWN_PATH_FORMAT': ['解析出的视频路径格式不对', 100],
    'VIDEO_NOT_EXIST': ['视频不存在', 100],
    'VOICE_UNKNOWN_PATH_FORMAT': ['解析出的语音路径格式不对', 100],
    'VOICE_DESERIALIZATION_ERROR': ['语音反序列化错误', 30],
    'VOICE_NOT_EXIST': ['语音不存在', 100],
    'VOICE_UNKNOWN_FILEHEADER': ['未知的语音文件文件头', 100],
    'VOICE_CONVERT_ERROR': ['语音格式转换失败', 30],
    'MIXMSG_DESERIALIZATION_ERROR': ['混合消息反序列化错误', 30],
    'EXTSTR_NOT_EXIST_TARGET': ['EXTSTR不存在目标', 100],
    'EXTSTR_JSON_ERR_DECODE': ['EXTSTR JSON解码错误', 100],
    'IO_ERROR': ['IO读取写入错误', 30],
    'JAVA_DESER_PROC_ERR': ['Java反序列化进程错误', 30],
    'JAVA_DESER_PROC_TIMEOUT': ['Java反序列化超时', 30],
    'JAVA_DESER_ERR_INPUT_TYPE': ['Java反序列化错误  输入类型错误', 30],
    'JAVA_DESER_JSON_ERR_DECODE': ['Java反序列化错误 - JSON解码错误', 30],
    'UNEXPECTED_ERR': ['预期外的错误（建议上报）', 10]
}



class ErrCode:
    def __init__(self, mode, log_func=None):
        self.mode = mode
        self.log_func = log_func
        self.codes = codes
        #日志等级
        self.LOG_LEVEL_INFO = 0
        self.LOG_LEVEL_WARN = 1
        self.LOG_LEVEL_ERR = 2

        self.logLevel = self.LOG_LEVEL_INFO

        self.parse_state = False

        self.counts = {}
        self.log_file = None


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
            try:
                self.log_file.write(tag + " :" + info + "\n")
            except:
                print("写入日志失败")

            if self.mode == "print":
                print(tag + " :" + info)
            elif self.mode == "func":
                self.log_func(tag + " :" + info)


    def parse_start(self):
        """
        开始解析
        """
        self.parse_state = True
        try:
            if not os.path.exists("output"):
                if not os.path.isdir("output"):
                    os.makedirs("output")

            self.log_file = open("output/parse_log.txt", 'w', encoding='utf-8')
        except Exception as e:
            self.parse_state = False
            log_info = f"创建日志时发生错误：{e} 解析停止！"
            self.log("parse", self.LOG_LEVEL_ERR, log_info)


    def parse_stop(self, info):
        """
        关闭解析
        :param info:错误信息
        """
        self.parse_state = False
        log_info = f"{info} 解析停止!"
        self.log("parse", self.LOG_LEVEL_ERR, log_info)
        try:
            self.log_file.close()
        except Exception as e:
            log_info = f"保存日志时发生错误{e}，解析日志可能并没有正确保存"
            self.log("parse", self.LOG_LEVEL_WARN, log_info)

    def parse_quote_state(self):
        """
        查询解析状态
        :return: bool
        """
        return self.parse_state


    def parse_err(self, code, errdata):
        """
        解析错误处理
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

        errinfo = codes[code][0] + f"，相关信息：{errdata}"
        self.count_check(code)
        print(errinfo)
        try:
            self.log_file.write("parse :" + errinfo + "\n")
        except:
            print("写入日志失败")


    def log_err_count(self):
        for key, value in self.counts.items():
            info = f"解析发生错误次数：{key} {codes[key][0]}  {value}次\n"
            self.log("parse", self.LOG_LEVEL_WARN, info)
        if not self.counts:
            info = f"解析未发生错误，恭喜！\n"
            self.log("parse", self.LOG_LEVEL_WARN, info)

    def count_check(self, code):
        """检查错误码有没有过量，及时弹出警告信息
        要求输入code是为了节省性能，只在某code的数量改变时检查

        :param code:错误码
        :return:无
        """
        if self.counts[code] % codes[code][1] == 0:
            errinfo = f"解析时已经发生{self.counts[code]}次“{codes[code][0]}”的错误，请检查你的设置"
            self.log("parse_count", self.LOG_LEVEL_WARN, errinfo)





