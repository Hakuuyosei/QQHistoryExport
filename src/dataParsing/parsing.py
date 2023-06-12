import hashlib
import sqlite3
import os
import traceback
import json
import shutil


from src.errcode import errcode
from src.dataParsing.unserializedDataParsing import unserializedDataParsing
from src.dataParsing.textParsing import textParsing
from src.dataParsing.protoDataParsing import protoDataParsing
from src.dataParsing.javaSerializedDataParsing import javaSerializedDataParsing


# QQ消息类型以及处理方式
unserializedDataType =      [-1000, -1051, -1012, -2042, -2015, -1034, -2005, -3008, -2016, -4008, -1013]
protoDataType =             [-2000, -1035, -2002, -2022, -5020, -5023, -8018, -5040]
javaSerializedDataType =    [-1049, -2017, -2025, -2011, -5008, -2007, -2025]


class QQParse():
    def __init__(self):
        self.targetQQ = None
        self.key = None
        self.qqemojiVer = 1

        self.DBcursor1 = None

        # 从测试文件中读取测试用信息
        with open('test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.targetQQ = data["targetQQ"]
            self.dbPath = data["fileName"]
            self.chatimgPath = data["chatimgPath"]
            self.key = data["key"]
            self.cmdpre = data["cmd"]
            self.qqemojiVer = 1

        self.ERRCODE = errcode.err_code()
        self.textParsing = textParsing(self.ERRCODE,self.qqemojiVer)
        self.unserializedDataParsing = unserializedDataParsing(self.ERRCODE, self.textParsing)
        self.protoDataParsing = protoDataParsing(self.ERRCODE, self.textParsing, self.chatimgPath)
        self.javaSerializedDataParsing = javaSerializedDataParsing(self.ERRCODE, self.textParsing)

        self.createOutput()
        self.outputFile = open('output/chatData.txt', 'w')

    def createOutput(self):
        dir_path = 'output'

        # 判断目录是否存在并删除
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)
        os.mkdir(dir_path + "/emoticons")
        os.mkdir(dir_path + "/emoticons/emoticon1")
        os.mkdir(dir_path + "/emoticons/emoticon1/new")
        os.mkdir(dir_path + "/emoticons/emoticon1/old")
        os.mkdir(dir_path + "/emoticons/emoticon2")
        os.mkdir(dir_path + "/emoticons/nudgeaction")
        os.mkdir(dir_path + "/images")
        os.mkdir(dir_path + "/temp")
        os.mkdir(dir_path + "/senders")

    def fill_cursors(self, cmd):
        cursors = []
        # slowtable might not contain related message, so just skip it
        try:
            cursors.append(self.DBcursor1.execute(cmd))
        except:
            pass
        cursors.append(self.DBcursor1.execute(cmd))
        return cursors

    # 解密数据
    def decrypt(self, data):
        msg = b''
        if type(data) == bytes:
            msg = b''
            for i in range(0, len(data)):
                msg += bytes([data[i] ^ ord(self.key[i % len(self.key)])])
            return msg
        elif type(data) == str:
            msg = ''
            for i in range(0, len(data)):
                msg += chr(ord(data[i]) ^ ord(self.key[i % len(self.key)]))
            return msg


    # 处理数据库
    def processdb(self):
        self.DBcursor1 = sqlite3.connect(self.dbPath).cursor()

        self.getFriends()
        self.getTroops()
        self.getTroopMembers()
        friendOrTroop = "troop"
        self.senderUins = []

        targetQQmd5 = hashlib.md5(self.targetQQ.encode("utf-8")).hexdigest().upper()

        if self.targetQQ in self.friends.keys():
            self.Mode = "friend"
            cmd = "select msgtype,senderuin,msgData,time,extStr from mr_friend_{}_New order by time".format(
                targetQQmd5)

        elif self.targetQQ in self.troops.keys():
            self.Mode = "troop"
            cmd = "select msgtype,senderuin,msgData,time,extStr from mr_troop_{}_New order by time".format(
                targetQQmd5)
        else:
            print("无效QQ号", self.targetQQ)
            return
        print(cmd)

        if self.cmdpre != "":
            cmd = self.cmdpre

        cursors = self.fill_cursors(cmd)



        allmsg = []
        for cs in cursors:
            for row in cs:
                msgType = row[0]
                senderQQ = self.decrypt(row[1])
                if senderQQ not in self.senderUins:
                    self.senderUins.append(senderQQ)
                msgData = self.decrypt(row[2])
                ltime = row[3]
                extStr = self.decrypt(row[4])
                msgOutData = self.proMsg(msgType, msgData, extStr, senderQQ)
                if msgOutData != None and msgOutData != {}:
                    msgOutData["s"] = senderQQ
                    msgOutData["i"] = ltime
                    json_str = json.dumps(msgOutData)
                    self.outputFile.write(json_str + '\n')
        self.outputFile.close()

        print(self.troopMembers[self.targetQQ])


        senders = {}
        if friendOrTroop == "troop":
            for uin in self.senderUins:
                if uin == self.targetQQ:
                    continue
                    # 如果发送者等于群QQ号，可能是更改群名之类的
                name = self.troopMembers[self.targetQQ][uin][0]
                senders[uin] = [name,""]

        filename = "output/senders/senders.json"
        # 写入 JSON 数据到文件

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(senders, f, ensure_ascii=False, indent=4)




    # 加工信息
    def proMsg(self, msgType, msgData, extStr, senderQQ):
        msgOutData = {}


        if msgType in unserializedDataType:
            msgOutData = self.unserializedDataParsing.parse(msgType, msgData, extStr, senderQQ)
            return msgOutData
        elif msgType in protoDataType:
            msgOutData = self.protoDataParsing.parse(msgType, msgData, extStr, senderQQ)
            return msgOutData
        elif msgType in javaSerializedDataType:
            msgOutData = self.javaSerializedDataParsing.parse(msgType, msgData, extStr, senderQQ)
            return msgOutData
        print(msgType)



        if msgType == -2060:# unknown
            print(-2060, msgData.decode("utf-8"))
            #-2060 {"text":"xxx","bgColor":-7883789,"ts":16464**,"cover":""}

        elif msgType == -7010:# unknown
            print(-7010, msgData.decode("utf-8"))
            #-7010 [{"key_profile_introduction":"人际交往笨拙xxxxx","key_ts":16****,"key_type":20019}]


        else:

            print("unknown:", msgType)
            print(msgData)
            # with open("./11.bin", 'wb') as f:  # 二进制流写到.bin文件
            #     f.write(msgData)
            # 1
        return msgOutData

    # 获取好友列表
    def getFriends(self):
        self.friends = {}
        cmd = "SELECT uin, name ,remark FROM Friends"#从Friends表中取uin, name,remark
        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                friendQQNumber = self.decrypt(row[0])
                FriendName = self.decrypt(row[1])
                FriendRemark = self.decrypt(row[2])
                self.friends[friendQQNumber] = [FriendName,FriendRemark]
        friendsKeys = list(self.friends.keys())
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
                self.friends.pop(friendQQNumber)
        print(self.friends)#还有gulid待分析！！！！！！

    # 获取群列表
    def getTroops(self):

        self.troops = {}
        cmd = "SELECT troopuin, troopname FROM TroopInfoV2"#从Friends表中取uin, remark
        #cmd = "SELECT troopuin, troopInfoExtByte FROM TroopInfoV2"  # 从Friends表中取uin, remark

        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                troopQQNumber = self.decrypt(row[0])
                troopName = self.decrypt(row[1])
                self.troops[troopQQNumber] = [troopName]
                # 解码并添加进friends字典
        print(self.troops)

    #获取群友列表（所有群友实际上都在同一个表里）
    def getTroopMembers(self):
        self.troopMembers = {}
        cmd = "SELECT troopuin, memberuin, friendnick, troopnick FROM TroopMemberInfo"
        cursors = self.fill_cursors(cmd)
        for cs in cursors:
            for row in cs:
                troopQQNumber = self.decrypt(row[0])
                memberQQ = self.decrypt(row[1])
                memberName = self.decrypt(row[2])
                membernick = self.decrypt(row[3])
                self.decrypt(row[2])
                if troopQQNumber in self.troopMembers.keys():
                    self.troopMembers[troopQQNumber][memberQQ] = [memberName,membernick]
                else:
                    self.troopMembers[troopQQNumber] = {memberQQ: [memberName,membernick]}
        # print(self.troopMembers)


