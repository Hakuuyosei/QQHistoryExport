import os
import commentjson


def validate_settings(is_json_file, configs_data):
    """初始化设置项

    :param is_json_file: 是否是json文件
    :param configs_data: 若是文件则输入文件路径，否则输入设置项
    :return:(解析设置项是否成功bool，提示信息，验证后的设置项)
    """
    configs_validated = {}
    state = True
    info = ""
    if not is_json_file:
        configs = configs_data
    else:
        try:
            with open(configs_data, 'r', encoding="utf-8") as file:
                try:
                    # 读取带注释的json
                    configs = commentjson.load(file)
                except:
                    return False, "json文件路径不对或IO错误！", configs_validated
        except:
            return False, "json格式错误，解析失败！", configs_validated

    # 模式
    exist_state, info_new = validate_key_exist(configs, "mode")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["mode"] in ["Friend", "Troop"]:
            configs_validated["mode"] = configs["mode"]
        else:
            state = False
            info += "模式并不在Friend和Troop中！\n"

    # 自己QQ号
    exist_state, info_new = validate_key_exist(configs, "selfQQ")
    state = exist_state and state
    info += info_new
    if exist_state:
        state_new, info_new, configs_validated["selfQQ"] = validate_num_string(configs["selfQQ"], "selfQQ")
        state = state_new and state
        info += info_new

    # 目标QQ号
    exist_state, info_new = validate_key_exist(configs, "targetQQ")
    state = exist_state and state
    info += info_new
    if exist_state:
        state_new, info_new, configs_validated["targetQQ"] = validate_num_string(configs["selfQQ"], "targetQQ")
        state = state_new and state
        info += info_new

    exist_state_needsl, info_new = validate_key_exist(configs, "needSlowtable")
    state = exist_state_needsl and state
    info += info_new
    if exist_state_needsl:
        if "needSlowtable" not in [True, False]:
            exist_state_needsl = False
            info += "needSlowtable的值非布尔true, false！\n"


    # 数据库
    exist_state, info_new = validate_key_exist(configs, "findFilesMode")
    state = exist_state and state
    info += info_new
    if exist_state:
        # 文件夹读入模式
        if configs["findFilesMode"] == "dir":
            exist_state, info_new = validate_key_exist(configs, "dataDirPath")
            state = exist_state and state
            info += info_new
            if exist_state:

                # 支持自动判断文件夹名db或databases
                exist_state1, info_new1, path_new1 = validate_folder_exist(configs["dataDirPath"] + "/databases")
                exist_state2, info_new2, path_new2 = validate_folder_exist(configs["dataDirPath"] + "/db")
                if exist_state1:
                    dbDirPath = path_new1
                elif exist_state2:
                    dbDirPath = path_new2
                else:
                    state = False
                    info += info_new1 + info_new2

                exist_state3, _ = validate_key_exist(configs, "selfQQ")
                if exist_state1 and exist_state2 and exist_state3:
                    # QQ号.db文件
                    exist_state, info_new, configs_validated["dbPath"] = \
                        validate_file_exist(f"{dbDirPath}/{configs['selfQQ']}.db")
                    state = exist_state and state
                    info += info_new

                    if exist_state_needsl:
                        # slowtable_QQ号.db文件
                        exist_state, info_new, configs_validated["dbstPath"] = \
                            validate_file_exist(f"{dbDirPath}/slowtable_{configs['selfQQ']}.db")
                        state = exist_state and state
                        info += info_new

                exist_state1, info_new1, path_new1 = validate_folder_exist(configs["dataDirPath"] + "/files")
                exist_state2, info_new2, path_new2 = validate_folder_exist(configs["dataDirPath"] + "/f")
                if exist_state1:
                    fDirPath = path_new1
                elif exist_state2:
                    fDirPath = path_new2
                else:
                    state = False
                    info += info_new1 + info_new2

                if exist_state1 and exist_state2:
                    # kc文件
                    exist_state, info_new, kcPath = \
                        validate_file_exist(f"{fDirPath}/kc")
                    state = exist_state and state
                    info += info_new
                    # 读取kc文件
                    if exist_state:
                        state_new, info_new, configs_validated["kc"] = read_kc(kcPath)
                        state = exist_state and state
                        info += info_new

        # 单个文件读入模式
        elif configs["findFilesMode"] == "files":
            exist_state, info_new = validate_key_exist(configs, "dbPath")
            state = exist_state and state
            info += info_new
            if exist_state:
                exist_state, info_new, configs_validated["dbPath"] = \
                    validate_file_exist(configs["dbPath"], "dbPath")
                info += info_new
                state = exist_state and state

            if exist_state_needsl:
                # 需要Slowtable
                if configs["needSlowtable"] == True:
                    exist_state, info_new = validate_key_exist(configs, "dbstPath")
                    info += info_new
                    if exist_state:
                        exist_state, info_new, configs_validated["dbstPath"] = \
                            validate_file_exist(configs["dbstPath"], "dbstPath")
                        info += info_new
                        state = exist_state and state
                        if exist_state:
                            state_new, info_new, configs_validated["kc"] = read_kc(configs["dbstPath"])
                            state = exist_state and state
                            info += info_new
                else:
                    pass
                # 此处exist_state_needsl在前面已经判断了needSlowtable不合法的情况


            exist_state, info_new = validate_key_exist(configs, "needKey")
            state = exist_state and state
            info += info_new
            if exist_state:
                # 需要从文件中读取秘钥
                if configs["needKey"] == True:
                    exist_state, info_new = validate_key_exist(configs, "keyPath")
                    info += info_new
                    if exist_state:
                        exist_state, info_new, configs_validated["kcPath"] = \
                            validate_file_exist(configs["kcPath"], "dbPath")
                        info += info_new
                        state = exist_state and state
                        if exist_state:
                            state_new, info_new, configs_validated["kc"] = read_kc(configs["kcPath"])
                            state = exist_state and state
                            info += info_new

                # 手动输入秘钥
                elif configs["needKey"] == False:
                    exist_state, info_new = validate_key_exist(configs, "key")
                    state = exist_state and state
                    info += info_new
                    if exist_state:
                        state_new, info_new, configs_validated["kc"] = \
                            validate_num_string(configs["key"], "key")
                        state = state_new and state
                        info += info_new

                else:
                    state = False
                    info += "key读入模式未知，needKey非True or False！\n"

        else:
            state = False
            info += "数据库文件寻找模式无效（不是dir也不是files）！\n"

    exist_state, info_new = validate_key_exist(configs, "noSelectNeedDisplay")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["noSelectNeedDisplay"] in [True, False]:
            configs_validated["noSelectNeedDisplay"] = configs["noSelectNeedDisplay"]
        else:
            state = False
            info += "noSelectNeedDisplay非true or false！\n"



    exist_state, info_new = validate_key_exist(configs, "needQQEmoji")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["needQQEmoji"] == True:
            if configs["QQEmoji"] == "new" or configs["needQQEmoji"] == "old":
                configs_validated["needQQEmoji"] = configs["needQQEmoji"]
            else:
                state = False
                info += "needImages非True or False！\n"
            configs_validated["needQQEmoji"] = True
        elif configs["needQQEmoji"] == False:
            configs_validated["needQQEmoji"] = False
        else:
            state = False
            info += "needImages非True or False！\n"

    exist_state, info_new = validate_key_exist(configs, "needImages")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["needImages"] == True:
            exist_state, info_new, configs_validated["imagesPath"] = validate_folder_exist(configs["imagesPath"], "imagesPath")
            state = exist_state and state
            info += info_new
            configs_validated["needImages"] = True

        elif configs["needImages"] == False:
            configs_validated["needImages"] = False
        else:
            state = False
            info += "needImages非true or false！\n"

    # if configs["needShortVideo"]:
    #     shortvideoPath = configs["shortvideoPath"]
    #
    #     if os.path.exists(shortvideoPath):
    #         self.configs["shortvideoPath"] = shortvideoPath
    #     else:
    #         return False
    #
    # if configs["needVoice"]:
    #     voicePath = configs["voicePath"]
    #
    #     if os.path.exists(voicePath):
    #         self.configs["voicePath"] = voicePath
    #     else:
    #         return False

    exist_state, info_new = validate_key_exist(configs, "needMarketFace")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["needMarketFace"] in [True ,False]:
            configs_validated["needMarketFace"] = configs["needMarketFace"]
        else:
            state = False
            info += "needMarketFace非true or false！\n"

    exist_state, info_new = validate_key_exist(configs, "needMarketFace")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["needMarketFace"] in [True, False]:
            configs_validated["needMarketFace"] = configs["needMarketFace"]
        else:
            state = False
            info += "needMarketFace非true or false！\n"

    exist_state, info_new = validate_key_exist(configs, "needReplyMsg")
    state = exist_state and state
    info += info_new
    if exist_state:
        if configs["needReplyMsg"] in [True, False]:
            configs_validated["needReplyMsg"] = configs["needReplyMsg"]
        else:
            state = False
            info += "needReplyMsg非true or false！\n"


    print(info, state)
    return state, info, configs_validated


def validate_num_string(data, name):
    """
    验证字符串设置项
    :param data: 待验证数据
    :param name: 待验证数据名称
    :return:state, info, data
    """
    if type(data) != str:
        return False, f"{name}不是字符串str！\n", None
    elif data == "":
        return False, f"{name}为空！\n", None
    elif not data.isdigit():
        return False, f"{name}格式不对，含有非数字信息！\n", None
    else:
        return True, "", data


def validate_key_exist(configs, key):
    """

    :param configs: 设置项
    :param key: 键
    :return: state, info
    """
    if key in configs:
        return True, ""
    else:
        return False, f"{key}键不存在！！\n"


def validate_file_exist(path, name=None):
    """
    验证文件是否存在

    :param path: 路径
    :param name: 路径名
    :return: state, info
    """
    print(path, 123)
    if name is None:
        name = path
    if os.path.exists(path):
        if os.path.is_file(path):
            return True, "", path
        else:
            return False, f"{name}错误指向了文件夹路径！\n", path
    else:
        return False, f"{name}文件不存在！！\n", path


def validate_folder_exist(path, name=None):
    """
    验证文件夹是否存在

    :param path: 文件夹路径
    :param name: 文件夹名称（可选）
    :return: state, info
    """
    if name is None:
        name = path

    if os.path.exists(path):
        if os.path.isdir(path):
            return True, "", path
        else:
            return False, f"{name}错误指向了文件路径！\n", path
    else:
        return False, f"{name}文件夹不存在！！\n", path


def read_kc(path):
    """

    :param path:
    :return:
    """
    try:
        with open(path, 'r') as file:
            kc = file.read()
        state_new, info_new, = validate_num_string(kc, "从文件里读取出来的kc")
        return True, "", kc
    except IOError:
        return False, f"读取文件 '{path}' 时出现IO错误\n", None
    except Exception as e:
        return False, f"读取 '{path}' 时出现未知错误{e}\n", None
