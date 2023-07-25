import os
import commentjson
class ValidateSettings:
    def __init__(self):
        self.configs = {}
        self.info = ""
        self.state = True

    def validate(self, is_json_file, configs_data):
        """初始化设置项

        :param is_json_file: 是否是json文件
        :param configs_data: 若是文件则输入文件路径，否则输入设置项
        :return:(解析设置项是否成功bool，提示信息，验证后的设置项)
        """
        configs_validated = {}
        self.configs = {}
        self.info = ""
        self.state = True

        if not is_json_file:
            self.configs = configs_data
        else:
            try:
                with open(configs_data, 'r', encoding="utf-8") as file:
                    try:
                        # 读取带注释的json
                        self.configs = commentjson.load(file)
                    except:
                        return False, "json文件路径不对或IO错误！", configs_validated
            except:
                return False, "json格式错误，解析失败！", configs_validated



        _, configs_validated["mode"] = self.validate_inlist_conf(
            "mode", ["friend", "group"], "群组或私聊模式")
        _, configs_validated["selfQQ"] = self.validate_num_str_conf(
            "selfQQ", "自己的QQ")
        _, configs_validated["targetQQ"] = self.validate_num_str_conf(
            "targetQQ", "目标QQ")

        _, configs_validated["needSlowtable"] = self.validate_bool_conf(
            "needSlowtable", "是否需要两个月以前的聊天记录（slowtable）")


        state, find_files_mode = self.validate_inlist_conf(
            "findFilesMode", ["dir", "files"], "提取文件模式")
        if state:
            if find_files_mode == "dir":
                state, data_dir_path = self.validate_folder_exist_conf(
                    "dataDirPath", "com.tencent.mobileqq文件夹的路径")
                if state:
                    databases_paths = [f"{data_dir_path}/databases",
                                       f"{data_dir_path}/db"]
                    files_paths = [f"{data_dir_path}/files",
                                       f"{data_dir_path}/f"]

                    if "selfQQ" in self.configs:
                        dbfile_paths = [item + f"/{self.configs['selfQQ']}.db" for item in databases_paths]
                        _, configs_validated["dbPath"] = \
                            self.validate_one_of_files_exist(dbfile_paths, "QQ号.db")

                        if configs_validated["needSlowtable"] == True:
                            dbstfile_paths = [item + f"/slowtable_{self.configs['selfQQ']}.db" for item in databases_paths]
                            _, configs_validated["dbstPath"] = \
                                self.validate_one_of_files_exist(dbstfile_paths, "slowtable_QQ号.db")

                    _, if_need_read_kc = self.validate_bool_conf("needKey", "秘钥文件")
                    if if_need_read_kc == True:
                        kcfile_paths = [item + f"/kc" for item in files_paths]
                        _, kcfile_path = \
                            self.validate_one_of_files_exist(kcfile_paths, "kc秘钥文件")
                        _, configs_validated["key"] = self.read_kc(kcfile_path)

                    elif  if_need_read_kc == False:
                        _, configs_validated["key"] = self.validate_num_str_conf(
                            "key", "输入的秘钥")
            elif find_files_mode == "files":
                _, configs_validated["dbPath"] = \
                    self.validate_file_exist_conf("dbPath", "QQ号.db")
                _, configs_validated["dbstPath"] = \
                    self.validate_file_exist_conf("dbstPath", "slowtable_QQ号.db")

                _, if_need_read_kc = self.validate_bool_conf("needKey", "秘钥文件")
                if if_need_read_kc == True:
                    _, kcfile_path = \
                        self.validate_file_exist_conf("keyPath", "kc秘钥文件")
                    _, configs_validated["key"] = self.read_kc(kcfile_path)

                elif if_need_read_kc == False:
                    _, configs_validated["key"] = self.validate_num_str_conf(
                        "key", "输入的秘钥")


        _, configs_validated["needQQEmoji"] = self.validate_bool_conf(
            "needQQEmoji", "是否需要QQ小表情")
        if configs_validated["needQQEmoji"] == True:
            _, configs_validated["QQEmojiVer"] = self.validate_inlist_conf(
                "QQEmojiVer", ["new", "old"], "QQ表情版本")

        _, configs_validated["needImages"] = self.validate_bool_conf(
            "needImages", "是否需要图片")
        if configs_validated["needImages"] == True:
            _, configs_validated["imagesPath"] = self.validate_folder_exist_conf(
                "imagesPath", "聊天图片路径")

        _, configs_validated["needVoice"] = self.validate_bool_conf(
            "needVoice", "是否需要语音解析")
        if configs_validated["needVoice"] == True:
            _, configs_validated["voicePath"] = self.validate_folder_exist_conf(
                "voicePath", "ptt文件夹路径")

        _, configs_validated["needVideo"] = self.validate_bool_conf(
            "needVideo", "是否需要视频解析")
        if configs_validated["needVideo"] == True:
            _, configs_validated["videoPath"] = self.validate_folder_exist_conf(
                "videoPath", "shortvideo文件夹路径")

        _, configs_validated["needMarketFace"] = self.validate_bool_conf(
            "needMarketFace", "是否需要QQ大表情")
        _, configs_validated["needJavaDeser"] = self.validate_bool_conf(
            "needJavaDeser", "是否需要引用消息的引用部分")

        print(self.state, self.info, configs_validated)
        return self.state, self.info, configs_validated

    def validate_inlist_conf(self, key, list, name=""):
        """
        验证设置项值是否在列表中
        :param key: 键名
        :param name: 数据名称
        :return: 状态，值
        """
        if key not in self.configs:
            self.state = False
            self.info += f"设置项中{key} {name}项丢失\n"
            return False, ""

        if self.configs[key] not in list:
            self.state = False
            self.info += f"设置项中{key} {name}的值不在列表{list}中！\n"
            return False, ""

        return True, self.configs[key]

    def validate_bool_conf(self, key, name=""):
        """
        验证布尔值设置项
        :param key: 键名
        :param name: 数据名称
        :return: 状态，值
        """
        if key not in self.configs:
            self.state = False
            self.info += f"设置项中{key} {name}项丢失\n"
            return False, ""

        state, info = self.validate_bool(self.configs[key], f"{key} {name}")
        self.info += info
        return state, self.configs[key]

    def validate_bool(self, value, name=""):
        """
        校验布尔值
        :param value: 要校验的值
        :param name: 数据名称
        :return: 状态，提示信息
        """
        if isinstance(value, bool):
            return True, ""
        else:
            self.state = False
            return False, f"{name}不是有效的布尔值(true/false)\n"

    def validate_num_str_conf(self, key, name=""):
        """
        验证数字字符串设置项
        :param key: 键名
        :param name: 数据名称
        :return: 状态，值
        """
        if key not in self.configs:
            self.state = False
            self.info += f"设置项中{key} {name}项丢失\n"
            return False, ""
        state, info = self.validate_num_str(self.configs[key], f"{key} {name}")
        self.info += info
        return state, self.configs[key]

    def validate_num_str(self, data, name):
        """
        验证数字字符串
        :param data: 数据
        :param name: 数据名称
        :return: 状态，信息
        """
        if type(data) != str:
            state = False
            info = f"{name}不是字符串str！\n"
            return state, info
        elif data == "":
            state = False
            info = f"{name}为空！\n"
            return state, info
        elif not data.isdigit():
            state = False
            info = f"{name}格式不对，含有非数字信息！\n"
            return state, info
        else:
            return True, ""

    def validate_file_exist_conf(self, key, name=""):
        """
        验证文件是否存在，设置项
        :param key: 键名
        :param name: 数据名称
        :return: 状态，值
        """
        if key not in self.configs:
            self.state = False
            self.info += f"设置项中{key} {name}项丢失\n"
            return False, ""
        state, info = self.validate_file_exist(self.configs[key], f"{key} {name}")
        self.info += info
        return state, self.configs[key]

    def validate_one_of_files_exist(self, paths, name=""):
        """
        验证文件是否存在
        :param paths: 路径列表
        :param name: 数据名称
        :return: 状态，路径值
        """
        state = False
        true_path = ""
        info_new = ""
        for path in paths:
            state_new, info = self.validate_file_exist(path, f"{name}")
            info_new += info
            if state_new:
                state = True
                true_path = path
        if not state:
            self.info += info_new
            self.state = False

        return state, true_path

    def validate_file_exist(self, path, name):
        """
        验证文件是否存在

        :param path: 路径
        :param name: 路径名
        :return: state
        """
        if os.path.exists(path):
            if os.path.isfile(path):
                return True, ""
            else:
                state = False
                info = f"{name}错误指向了文件夹路径！\n"
                return state, info
        else:
            state = False
            info = f"{name}文件不存在！！\n"
            return state, info

    def validate_folder_exist_conf(self, key, name=""):
        """
        验证文件夹是否存在，设置项
        :param key: 键名
        :param name: 数据名称
        :return: 状态，值
        """
        if key not in self.configs:
            self.state = False
            self.info += f"设置项中{key} {name}项丢失\n"
            return False, ""

        state, info = self.validate_folder_exist(self.configs[key], f"{key} {name}")
        self.info += info
        return state, self.configs[key]

    def validate_folder_exist(self, path, name):
        """
        验证文件夹是否存在

        :param path: 路径
        :param name: 路径名
        :return: state
        """
        if os.path.exists(path):
            if os.path.isdir(path):
                return True, ""
            else:
                state = False
                info = f"{name}错误指向了文件路径！\n"
                return state, info
        else:
            state = False
            info = f"{name}文件夹不存在！！\n"
            return state, info

    def read_kc(self, path):
        """

        :param path:
        :return:
        """
        try:
            with open(path, 'r') as file:
                kc = file.read()
            state, info, = self.validate_num_str(kc, "从文件里读取出来的秘钥")
            if state == True:
                return True, kc
            else:
                self.info += info
                return False, ""
        except IOError:
            self.info += f"读取秘钥 '{path}' 时出现IO错误\n"
            return False, ""
        except Exception as e:
            self.info += f"读取秘钥 '{path}' 时出现未知错误{e}\n"
            return False, ""
