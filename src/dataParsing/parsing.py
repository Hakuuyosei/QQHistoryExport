import hashlib
import sqlite3
import os
import traceback
import json
import shutil
import commentjson


from src.errcode import errcode
from src.dataParsing.unserializedDataParsing import unserializedDataParsing
from src.dataParsing.textParsing import textParsing
from src.dataParsing.protoDataParsing import protoDataParsing
from src.dataParsing.javaSerializedDataParsing import javaSerializedDataParsing


# QQ消息类型以及处理方式
unserializedDataType =      [-1000, -1051, -1012, -2042, -2015, -1034, -2005, -3008,
                             -2016, -4008, -1013, -2009, -1001, -5018, -5012]
protoDataType =             [-2000, -1035, -2002, -2022, -5020, -5023, -8018, -5040]
javaSerializedDataType =    [-1049, -2017, -2025, -2011, -5008, -2007, -2025]


class QQParse:
    """QQ数据库读取，解析

    """
    def __init__(self, configs, errcode_obj):
        self.configs = configs
        self.key = None

        self.configs = configs

        self.DBcursor1 = None
        self.DBcursor2 = None

        self.ERRCODE = errcode_obj
        self.ERRCODE.parse_start()

        self.textParsing = textParsing(self.ERRCODE, self.configs)
        self.unserializedDataParsing = unserializedDataParsing(self.ERRCODE, self.textParsing, self.configs)
        self.protoDataParsing = protoDataParsing(self.ERRCODE, self.textParsing, self.configs)
        self.javaSerializedDataParsing = javaSerializedDataParsing(self.ERRCODE, self.textParsing, self.configs)

        self.createOutputFolder()


    def createOutputFolder(self):
        """创建输出文件夹

        """
        dir_path = 'output'

        # 判断目录是否存在并删除
        try:
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file != 'parse_log.txt':
                                os.remove(file_path)

                    for dir in dirs:
                        dir_path_2 = os.path.join(root, dir)
                        shutil.rmtree(dir_path_2)
            else:
                os.mkdir(dir_path)


            os.mkdir(dir_path + "/emoticons")
            os.mkdir(dir_path + "/emoticons/emoticon1")
            os.mkdir(dir_path + "/emoticons/emoticon1/new")
            os.mkdir(dir_path + "/emoticons/emoticon1/old")
            os.mkdir(dir_path + "/emoticons/emoticon2")
            os.mkdir(dir_path + "/emoticons/nudgeaction")
            os.mkdir(dir_path + "/images")
            os.mkdir(dir_path + "/videos")
            os.mkdir(dir_path + "/videos/thumbs")
            os.mkdir(dir_path + "/voices")
            os.mkdir(dir_path + "/temp")
            os.mkdir(dir_path + "/senders")


            self.outputFile = open('output/chatData.txt', 'w')
        except Exception as e:
            self.ERRCODE.parse_stop(f"清空和创建output文件夹时发生（{e}）错误")
        return


    def fill_cursors(self, cmd):
        cursors = []
        if self.configs["needSlowtable"]:
            cursors.append(self.DBcursor2.execute(cmd))
        cursors.append(self.DBcursor1.execute(cmd))
        return cursors


    def decrypt(self, data):
        """解密消息

        :param data: 数据，str或bytes
        :return: str数据
        """
        msg = b''
        key = self.configs["key"]
        if type(data) == bytes:
            msg = b''
            for i in range(0, len(data)):
                msg += bytes([data[i] ^ ord(key[i % len(key)])])
            return msg
        elif type(data) == str:
            msg = ''
            for i in range(0, len(data)):
                msg += chr(ord(data[i]) ^ ord(key[i % len(key)]))
            return msg


    # 处理数据库
    def procDb(self):
        """处理数据库

        """
        if not self.ERRCODE.parse_quote_state():
            return False

        targetQQ = self.configs["targetQQ"]
        targetQQmd5 = hashlib.md5(targetQQ.encode("utf-8")).hexdigest().upper()
        mode = self.configs["mode"]

        try:
            self.DBcursor1 = sqlite3.connect(self.configs["dbPath"]).cursor()
            if self.configs["needSlowtable"]:
                self.DBcursor2 = sqlite3.connect(self.configs["dbslPath"]).cursor()
        except:
            info = "数据库连接错误！sqlite3.connect error"
            self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_ERR, info)
            return False


        friends = self.getFriends()
        groups = self.getGroups()
        groupMembers = self.getGroupMembers()

        self.senderUins = []

        if mode == "friend":
            if targetQQ not in friends.keys():
                info = f"{targetQQ} 查无此人/无聊天内容"
                self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_ERR, info)
                return False
            else:
                cmd = f"select msgtype,senderuin,msgData,time,extStr from mr_friend_{targetQQmd5}_New order by time"
                cmd_2 = f"SELECT COUNT(*) FROM mr_friend_{targetQQmd5}_New"

        elif mode == "group":
            if targetQQ not in groups.keys():
                info = f"{targetQQ} 查无此群/无聊天内容"
                self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_ERR, info)
                return False
            else:
                cmd = f"select msgtype,senderuin,msgData,time,extStr from mr_troop_{targetQQmd5}_New order by time"
                cmd_2 = f"SELECT COUNT(*) FROM mr_troop_{targetQQmd5}_New"

        # print(cmd)

        # if self.cmdpre != "":
        #     cmd = self.cmdpre
        total_num = 0
        current_num = 0
        last_persent = 0
        # 行数统计
        try:
            cursors = self.fill_cursors(cmd_2)
        except Exception as e:
            info = f"数据库查询出错！sqlite3.execute error {e}"
            self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_ERR, info)
            return False
        for cs in cursors:
            total_num += cs.fetchone()[0]



        try:
            cursors = self.fill_cursors(cmd)
        except Exception as e:
            info = f"数据库查询出错！sqlite3.execute error {e}"
            self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_ERR, info)
            return False

        info = f"""数据库解析初始化成功，共计{total_num}条消息，开始解析……"""
        self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_INFO, info)

        for cs in cursors:
            for row in cs:
                persent = int((current_num+1) / total_num * 100)
                if persent % 5 == 0 and persent != last_persent:
                    last_persent = persent
                    info = f"解析进度：{persent}%, {current_num+1}/{total_num}"
                    self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_INFO, info)
                current_num += 1

                if not self.ERRCODE.parse_quote_state():
                    return False

                msgType = row[0]
                senderQQ = self.decrypt(row[1])
                if senderQQ not in self.senderUins:
                    self.senderUins.append(senderQQ)
                msgData = self.decrypt(row[2])
                ltime = row[3]
                extStr = self.decrypt(row[4])
                msgOutData = self.proMsg(msgType, msgData, extStr)
                if msgOutData != None and msgOutData != {}:
                    msgOutData["s"] = senderQQ
                    msgOutData["i"] = ltime
                    json_str = json.dumps(msgOutData)
                    self.outputFile.write(json_str + '\n')
        self.outputFile.close()

        # print(self.groupMembers[targetQQ])
        info = """聊天记录解析完毕！恭喜！"""
        self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_INFO, info)

        # 读取发送者数据
        senders = {}
        if mode == "group":
            for uin in self.senderUins:
                uin_get_flag = False
                if uin == targetQQ:
                    continue
                    # 如果发送者等于群QQ号，可能是更改群名之类的
                if targetQQ in groupMembers:
                    if uin in groupMembers[targetQQ]:
                        if groupMembers[targetQQ][uin][0]:
                            name = groupMembers[targetQQ][uin][0]
                            senders[uin] = [name, ""]
                            uin_get_flag = True
                        elif groupMembers[targetQQ][uin][1]:
                            name = groupMembers[targetQQ][uin][1]
                            senders[uin] = [name, ""]
                            uin_get_flag = True

                if not uin_get_flag:
                    senders[uin] = ["", ""]
                    info = f"{uin}不在你的数据库中，一会需要你自己去填写昵称"
                    self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_WARN, info)

        elif mode == "friend":
            for uin in self.senderUins:
                uin_get_flag = False

                if uin in friends:
                    if friends[uin][1]:
                        name = friends[uin][1]
                        senders[uin] = [name, ""]
                        uin_get_flag = True
                    elif friends[uin][0]:
                        name = friends[uin][0]
                        senders[uin] = [name, ""]
                        uin_get_flag = True
                if not uin_get_flag:
                    senders[uin] = ["", ""]
                    info = f"{uin}不在你的数据库中，一会需要你自己去填写昵称"
                    self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_WARN, info)


        filename = "output/senders/senders.json"
        # 写入 JSON 数据到文件

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(senders, f, ensure_ascii=False, indent=4)

        info = """下面是解析中发生的错误统计，因为图片，视频可能没被接收，被清理，或者有新的消息类型和存储方式
未被分析，所以出现一些错误是正常的，若某项错误出现次数过多，请检查你的设置项，若确保没问题，可以在
https://github.com/WhiteWingNightStar/QQHistoryExport上提issue，请附上output/parse_log.txt
中的异常部分"""
        self.ERRCODE.log("parse", self.ERRCODE.LOG_LEVEL_INFO, info)
        self.ERRCODE.log_err_count()
        return True


    def proMsg(self, msgType, msgData, extStr):
        """处理单条信息

        :param msgType: 消息类型
        :param msgData: 数据
        :param extStr:  extStr
        :return: msgOutData
        """
        msgOutData = {}


        if msgType in unserializedDataType:
            msgOutData = self.unserializedDataParsing.parse(msgType, msgData, extStr)
            return msgOutData
        elif msgType in protoDataType:
            msgOutData = self.protoDataParsing.parse(msgType, msgData, extStr)
            return msgOutData
        elif msgType in javaSerializedDataType:
            msgOutData = self.javaSerializedDataParsing.parse(msgType, msgData, extStr)
            return msgOutData


        #if msgType == -2060:# unknown
        #    print(-2060, msgData.decode("utf-8"))
        #    # -2060 {"text":"xxx","bgColor":-xxxxx,"ts":16xxxx**,"cover":""}

        #elif msgType == -7010:# unknown
        #    print(-7010, msgData.decode("utf-8"))
        #    # -7010 [{"key_profile_introduction":"人际交往xxxxx","key_ts":16****,"key_type":xxxx}]


        else:
            msgOutData = {
                "t": "err",
                "c": {"text": "[未知类型]", "type": "unknown"}
            }
            self.ERRCODE.parse_err("UNKNOWN_MSG_TYPE", [msgType, msgData, extStr])
            # with open("./11.bin", 'wb') as f:  # 二进制流写到.bin文件
            #     f.write(msgData)
            # 1
            return msgOutData

    def getFriends(self):
        """获取好友列表

        :return: {friendQQNumber: [FriendName, FriendRemark]}
        """
        friends = {}
        cmd = "SELECT uin, name ,remark FROM Friends"# 从Friends表中取uin, name,remark
        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                friendQQNumber = self.decrypt(row[0])
                FriendName = self.decrypt(row[1])
                FriendRemark = self.decrypt(row[2])
                friends[friendQQNumber] = [FriendName, FriendRemark]
        friendsKeys = list(friends.keys())
        for friendQQNumber in friendsKeys:
            # 计算qq号的md5值
            friendQQNumbermd5 = hashlib.md5(friendQQNumber.encode("utf-8")).hexdigest().upper()
            cmd = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s'" \
                  % ("mr_friend_%s_New" % friendQQNumbermd5)
            cursorifin = self.DBcursor1.execute(cmd)
            isin = 0
            for cs in cursorifin:
                isin = cs[0]
            if isin == 0:
                # 假如并不存在聊天数据表就剔除消息
                friends.pop(friendQQNumber)
        return friends

    def getGroups(self):
        """获取群列表

        :return: {groupQQNumber:[groupName]}
        """

        groups = {}
        cmd = "SELECT troopuin, troopname FROM TroopInfoV2"#从Friends表中取uin, remark

        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                groupQQNumber = self.decrypt(row[0])
                groupName = self.decrypt(row[1])
                groups[groupQQNumber] = [groupName]
                # 解码并添加进friends字典
        return groups

    def getGroupMembers(self):
        """获取群友列表（所有群友实际上都在同一个表里）

        :return: {[groupQQNumber]: {memberQQ: [memberName, membernick]}}
        """
        groupMembers = {}
        cmd = "SELECT troopuin, memberuin, friendnick, troopnick FROM TroopMemberInfo"
        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                groupQQNumber = self.decrypt(row[0])
                memberQQ = self.decrypt(row[1])
                memberName = self.decrypt(row[2])
                memberNick = self.decrypt(row[3])
                self.decrypt(row[2])
                if groupQQNumber in groupMembers.keys():
                    groupMembers[groupQQNumber][memberQQ] = [memberName, memberNick]
                else:
                    groupMembers[groupQQNumber] = {memberQQ: [memberName, memberNick]}
        return groupMembers
        # print(self.groupMembers)


