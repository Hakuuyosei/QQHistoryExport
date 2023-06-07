import hashlib
import sqlite3
import os
import traceback
import json
import imghdr
import shutil
import binascii

import errcode
from errcode import err_code

from lib.proto import Msg_pb2
from lib.proto.RichMsg_pb2 import PicRec
from lib.proto.RichMsg_pb2 import Msg
from lib.proto.RichMsg_pb2 import Elem

from lib.javaDeserialization import javaDeserialization as jd
from lib.slkamr import slkamrTomp3

import blackboxprotobuf
import ffmpeg

_crc64_init = False
_crc64_table = [0] * 256
def crc64(s):
    global _crc64_init
    if not _crc64_init:
        for i in range(256):
            bf = i
            for j in range(8):
                if bf & 1 != 0:
                    bf = bf >> 1 ^ -7661587058870466123
                else:
                    bf >>= 1
            _crc64_table[i] = bf
        _crc64_init = True
    v = -1
    for i in range(len(s)):
        v = _crc64_table[(ord(s[i]) ^ v) & 255] ^ v >> 8
    return v



class QQ():
    def __init__(self):
        self.targetQQ = None
        self.key = None

        self.qqemojiVer = 1
        self.emoji_map = None
        self.DBcursor1 = None

        self.imgMD5Map = {}
        self.imgNum = 1

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

    # 建立表情索引
    def mapqqEmoji(self):
        with open('lib/emoticon1/face_config.json', encoding='utf-8') as f:
            emojis = json.load(f)
        new_emoji_map = {}
        for e in emojis['sysface']:
            if self.qqemojiVer == 1:
                new_emoji_map[e["AQLid"]] = e["QSid"]
            else:
                if len(e["EMCode"]) == 3:
                    new_emoji_map[e["AQLid"]] = str(int(e["EMCode"]) - 100)
        return new_emoji_map

    # 加工文本信息
    def proText(self, msg):

        msgList = []
        lastpos = -2
        pos = msg.find('\x14')

        if pos == -1:
            msgList.append(["m", msg])
            return msgList

        while 1:
            pos = msg.find('\x14', lastpos + 2)
            if pos == -1:
                if msg[lastpos + 2:] != "":
                    msgList.append(["m", msg[lastpos + 2:]])
                break

            msgList.append(["m", msg[lastpos + 2:pos]])
            num = ord(msg[pos + 1])
            if str(num) in self.emoji_map:
                index = self.emoji_map[str(num)]
                if self.qqemojiVer == 1:
                    filename = "new/s" + index + ".png"
                else:
                    filename = "old/" + index + ".gif"
                emoticon_path = os.path.join('lib/emoticon1', filename)

                output_path = "output/emoticon1/" + filename
                lib_path = "lib/emoticon1/" + filename

                if os.path.exists(output_path):
                    msgList.append(["qqemoji", ERRCODE.NORMAL(), output_path, index])
                elif os.path.exists(lib_path):
                    shutil.copy(lib_path, output_path)
                    msgList.append(["qqemoji", ERRCODE.NORMAL(), output_path, index])
                else:
                    msgList.append(["qqemoji", ERRCODE.EMOJI_NOT_EXIST(self.qqemojiVer, str(num)), None, None])
            else:
                msgList.append(["qqemoji", ERRCODE.EMOJI_NOT_EXIST(self.qqemojiVer, str(num)), None, None])

            lastpos = pos
        return msgList

    def decodeMarketFace(self, data):
        emoticon_name = data + ".jif"
        output_path = "output/emoticon2/" + emoticon_name
        lib_path = "lib/emoticon2/" + emoticon_name

        if os.path.exists(output_path):
            return ERRCODE.NORMAL(), output_path
        elif os.path.exists(lib_path):
            shutil.copy(lib_path, output_path)
            return ERRCODE.NORMAL(), output_path
        else:
            return ERRCODE.MARKETFACE_NOT_EXIST(), ""

    # 解码图片
    def decodePic(self, data):
        try:
            doc = PicRec()
            doc.ParseFromString(data)
            url = 'chatimg:' + doc.md5
            filename = hex(crc64(url))
            filename = 'Cache_' + filename.replace('0x', '')
            relpath = os.path.join(".\\chatimg\\", filename[-3:], filename)

            # 判断文件是否存在
            if not os.path.isfile(relpath):
                return ["img", ERRCODE.IMG_NOT_EXIST(relpath), None]

            # 计算图片的MD5值
            with open(relpath, 'rb') as f:
                img_data = f.read()
                md5 = hashlib.md5(img_data).hexdigest()

            # 查找图片的MD5值是否已经存在
            if md5 in self.imgMD5Map:
                return ["img", ERRCODE.NORMAL(), self.imgMD5Map[md5]]

            # 确定图片类型并添加后缀名
            img_type = imghdr.what(relpath)
            if img_type is None:
                return ["img", ERRCODE.IMG_UNKNOWN_TYPE_ERROR(), relpath]

            new_filename = f'{self.imgNum}.{img_type}'
            self.imgNum = self.imgNum + 1
            new_file_path = os.path.join('output', 'images', new_filename)

            # 移动图片文件到output/images文件夹中，并重命名
            shutil.move(relpath, new_file_path)

            # 将MD5和新文件路径添加到imgMD5Map中
            self.imgMD5Map[md5] = new_file_path

            return ["img", ERRCODE.NORMAL(), new_file_path]

        except:
            print(traceback.format_exc())
            return ["img", ERRCODE.IMG_DESERIALIZATION_ERROR(data), None]

    # 解码混合消息
    def decodeMixMsg(self, data):
        msgList = []
        try:
            doc = Msg()
            doc.ParseFromString(data)
            for elem in doc.elems:
                if elem.picMsg:
                    msgList.append(self.decodePic(elem.picMsg))
                else:
                    msgText = elem.textMsg.decode('utf-8')
                    if msgText != " ":
                        for msgElem2 in self.proText(msgText):
                            msgList.append(msgElem2)
            return ERRCODE.NORMAL(), msgList
        except:
            return ERRCODE.MIXMSG_DESERIALIZATION_ERROR(data,traceback.format_exc()), msgList

    # 处理数据库
    def processdb(self):

        # 从测试文件中读取测试用信息
        with open('test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.targetQQ = data["targetQQ"]
            dbPath = data["fileName"]
            self.key = data["key"]
            cmdpre = data["cmd"]


        self.qqemojiVer = 1
        self.emoji_map = self.mapqqEmoji()
        self.DBcursor1 = sqlite3.connect(dbPath).cursor()

        self.getFriends()
        self.getTroops()
        self.getTroopMembers()

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
            print("无效QQ号",self.targetQQ)
            return
        print(cmd)

        if cmdpre != "":
            cmd = cmdpre

        cursors = self.fill_cursors(cmd)



        allmsg = []
        for cs in cursors:
            for row in cs:
                msgType = row[0]
                senderQQ = self.decrypt(row[1])
                msgData = self.decrypt(row[2])
                ltime = row[3]
                extStr = self.decrypt(row[4])
                msgList = self.proMsg(msgType,msgData,extStr,senderQQ)

    # 加工信息
    def proMsg(self, msgType, msgData, extStr, senderQQ):
        msgOutData = []
        print(msgType)

        # 普通文字
        if msgType == -1000 or msgType == -1051:
            msgOutData = {
                "t": "msg",
                "c": self.proText(msgData.decode("utf-8")),
                "e": ERRCODE.NORMAL()
            }
            # print(msgOutData)
            # print(extStr)

        # 图片类型
        elif msgType == -2000:
            # print(msgData)
            decodeOut = self.decodePic(msgData)
            msgOutData = {
                "t": "img",
                "c": {"filePath": decodeOut[2]},
                "e": decodeOut[1]
            }

        # 图文混排
        elif msgType == -1035:
            DeseErrcode, msgDeseData = self.decodeMixMsg(msgData)
            msgOutData = {
                "t": "mixmsg",
                "c": msgDeseData,
                "e": DeseErrcode
            }
            # print(msgOutData)

        elif msgType == -5040:# 灰条消息
            extStrJson = json.loads(extStr)

            if "revoke_op_type" in extStrJson.keys():
                if extStrJson["revoke_op_type"] == "0":
                    # 撤回消息
                    msgOutData = {
                        "t": "pic",
                        "c": {"text": msgData.decode("utf-8")},
                        "e": ERRCODE.NORMAL()
                    }
                    print("撤回消息样本  ", msgData.decode("utf-8"))
                    print(extStr)
                else:
                    print(msgData)
                    print(extStr)

            # 被邀请进入群聊
            elif ("inviteeUin" in extStrJson.keys()) or ("invitorUin" in extStrJson.keys()):
                doc = Msg_pb2.pai_yi_pai()
                doc.ParseFromString(msgData)
                print(doc.field5.decode("utf-8"))
                if ("inviteeUin" in extStrJson.keys()) and ("invitorUin" in extStrJson.keys()):
                    inviteeUin = extStrJson["inviteeUin"]
                    invitorUin = extStrJson["invitorUin"]
                    msgOutData = {
                        "t": "invite",
                        "c": {"inviteeUin": inviteeUin, "invitorUin":invitorUin},
                        "e": ERRCODE.NORMAL()
                    }
                else:
                    msgOutData = {
                        "t": "invite",
                        "c": {},
                        "e": ERRCODE.ALL_EXTSTR_NOT_EXIST_TARGET(extStr, "invitee or invitor ")
                    }


            # busi_type
            if "uint64_busi_type" in extStrJson.keys():
                busi_type = extStrJson["uint64_busi_type"]

                # 可能是拍一拍
                if busi_type == "14":
                    doc = Msg_pb2.pai_yi_pai()
                    doc.ParseFromString(msgData)
                    print(doc.field5.decode("utf-8"))
                    print(111, extStrJson["bytes_content"])

                # 可能是拍一拍
                elif busi_type == "12":
                    doc = Msg_pb2.pai_yi_pai()
                    doc.ParseFromString(msgData)
                    print(doc.field5.decode("utf-8"))
                    print(111, extStrJson["bytes_content"])

            else:
                deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
                print(f"原始数据: {deserialize_data}")
                print(msgData)
                print(deserialize_data["5"].decode("utf-8"))
                print(extStr)


        elif msgType == -1012:# 加群提示
            msgDecodedData = msgData.decode("utf-8")
            msgDecodedData = msgDecodedData[0:msgDecodedData.find("，点击修改TA的群昵称")]
            msgOutData = [["addtroop",msgDecodedData]]
            msgOutData = {
                "t": "jointroop",
                "c": {"text": msgDecodedData},
                "e": ERRCODE.NORMAL()
            }




        elif msgType == -2016:# 群语音通话发起
            msgDecodedData = msgData.decode("utf-8")
            msgDataText = msgDecodedData.split("|")
            print(extStr)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDecodedData, "type": "troopcallstart"},
                "e": ERRCODE.NORMAL()
            }
            return msgOutData

        elif msgType == -4008:  # 群语音通话结束
            msgDataAlreadyDecode = msgData.decode("utf-8")
            print(extStr)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDataAlreadyDecode, "type": "troopcallend"},
                "e": ERRCODE.NORMAL()
            }
            return msgOutData



        elif msgType == -2005:  # 已经被保存到本地的文件，内容为路径
            fileData = msgData[1:].decode("utf-8").split("|")
            filePath = fileData[-5]
            fileSize = fileData[-4]
            fileName = os.path.basename(filePath)
            file = {
                "received": True,
                "fileName": fileName,
                "filePath": filePath,
                "fileSize": fileSize
            }
            msgOutData = {
                "t": "file",
                "c": file,
                "e": ERRCODE.NORMAL()
            }
            print(extStr)
            return msgOutData

        elif msgType == -3008:  # 未被接收的文件，内容为文件名
            fileName = msgData.decode("utf-8")
            file = {
                "received": False,
                "fileName": fileName
            }
            msgOutData = {
                "t": "file",
                "c": file,
                "e": ERRCODE.NORMAL()
            }
            print(extStr)
            return msgOutData

        elif msgType == -8018:  # 大号表情
            doc = Msg_pb2.marketFace()
            doc.ParseFromString(msgData)
            marketFaceName = doc.u7.decode("utf-8")
            descErrcode, msgDeseData = self.decodeMarketFace(marketFaceName)
            msgOutData = {
                "t": "marketface",
                "c": {"path": msgDeseData, "name": marketFaceName},
                "e": descErrcode
            }
            print(extStr)
            return msgOutData


        elif msgType == -2022:  # 短视频
            doc = Msg_pb2.ShortVideo()
            doc.ParseFromString(msgData)
            filePath = doc.field3.decode("utf-8")
            print(filePath)


        elif msgType == -1049:# 回复引用
            msgOutData = self.proText(msgData.decode("utf-8"))
            try:
                print(extStr)
                extStrJson = json.loads(extStr)
                sourceMsgInfo = extStrJson["sens_msg_source_msg_info"]
                print(sourceMsgInfo)
                #sourceMsgInfoJson = jd.javaDeserialization(sourceMsgInfo,"reply")

                # HACK
                # (目前已弃用)
                # if len(SourceMsgInfo) > 1048:
                #     SourceMsgSenderQQnum = int(SourceMsgInfo[1016:1024],base=16)
                #     SourceMsgTime = int(SourceMsgInfo[1040:1048],base=16)
                #     msgOutData.append(["source",SourceMsgSenderQQnum,SourceMsgTime])
                # else:
                #     print("ERROR,SourceMsgInfo too short",SourceMsgInfo)
                # #print(msgOutData)

            except:
                print(traceback.format_exc())
                pass

        elif msgType == -2011:# 转发的聊天记录，java序列化
            jd.javaDeserialization(binascii.hexlify(msgData).decode(),"111")

            # sourceMsg = binascii.unhexlify("000000230000001d00000001000c766965774d756c74694d73670000000000000000000e5be8818ae5a4a9e8aeb0e5bd955d0000000100046974656d00000001000000120000000000000000000000000000000000000000000000000000000700057469746c650000000c00000000000233340015e7bea4e8818ae79a84e8818ae5a4a9e8aeb0e5bd950000000000013200023132000000057469746c650000000c00072337373737373700000002323600224d61686972757e3a2020e8bf99e4b8aae4bd9ce59381e8a681e698afe781abe4ba860000000000013400023132000000057469746c650000000c000723373737373737000000023236003a4d61686972757e3a2020e58fafe883bde4bc9ae5bc95e8b5b7e4b880e4ba9be4babae58f91e78eb0e8bf99e4b8aae7bb86e58886e9a286e59f9f0000000000013400023132000000057469746c650000000c00072337373737373700000002323600344d61686972757e3a2020e784b6e5908ee9a9ace4b88ae5b0b1e69c89e69bb4e4bc98e7a780e79a84e4baa7e59381e587bae69da50000000000013400023132000000057469746c650000000c00072337373737373700000002323600224d61686972757e3a202077656267616ce79a84e69cabe697a5e5b0b1e69da5e4ba86000000000001340002313200000002687200000009000566616c736500000000000773756d6d6172790000000c0007233737373737370000000232360016e69fa5e79c8b34e69da1e8bdace58f91e6b688e681af0000000000000000000000000000000000000000000000000000000000000000000000013000013000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ffffffffffffffff0000000ce8818ae5a4a9e8aeb0e5bd9500000000000000000000000000000000000300406f6f4e6557352f436a616b772f6c35317079656e4777707a6b79542f362b444749674f387139492f362b5a7a2b6b53707248467a326c4a412f32396c4359317000133731313433343236313033353830303136303700000000000000000000000000000000000000000000000000000000ffffffff0000ffffffff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000400000000000007d000000000")
            return 0

        elif msgType == -2017:# 群文件
            #jd.javaDeserialization(binascii.hexlify(msgData).decode(),"troopfile")
            1

        elif msgType == -5008:# 小程序/推荐名片，java 序列化套json
            #print(-5008,jd.javaDeserialization(binascii.hexlify(msgData).decode(),"miniapp"))
            1



        elif msgType == -2002:# 语音
            doc = Msg_pb2.Voice()
            doc.ParseFromString(msgData)
            filePath = doc.field1
            voiceLength = doc.field19

            # deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
            # print(f"原始数据: {deserialize_data}")
            # print(f"消息类型: {message_type}")

            #print(filePath,voiceLength)
            #slkamrTomp3.slkamrTomp3(filePath)


        # elif msgType ==
        #     # msgOutData = self.decodeMixMsg(msgData)
        #     # print(msgOutData)
        #     print(msgType)
        #     print(msgData.decode("utf-8"))
        #     with open("./11.bin", 'wb') as f:  # 二进制流写到.bin文件
        #         f.write(msgData)
        #     1

        elif msgType == -1013:# 你已经和xxx成为好友，现在可以开始聊天了。
            msgDataAlreadyDecode = msgData.decode("utf-8")

        elif msgType == -5023:  # 该用户通过***向你发起临时会话，前往设置。
            # deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
            # print(f"原始数据: {deserialize_data}")
            # print(f"消息类型: {message_type}")
            # print(msgData)
            # print(deserialize_data["5"].decode("utf-8"))
            return 0

        elif msgType == -5020:# 群标识卡片，proto
            return 0

        elif msgType == -2015:  # 发表说说，明文json
            return 0

        elif msgType == -1034:  # 似乎是个性签名，明文json
            return 0

        elif msgType == -2007:  #推荐名片
            return 0

        elif msgType == -2025:# 群标识卡片，proto
            return 0


        elif msgType == -2060:# unknown
            print(-2060,msgData.decode("utf-8"))
            #-2060 {"text":"xxx","bgColor":-7883789,"ts":16464**,"cover":""}
        elif msgType == -7010:# unknown
            print(-7010,msgData.decode("utf-8"))
            #-7010 [{"key_profile_introduction":"人际交往笨拙 不谙世事 涉世未深 思想不成熟的孩子","key_ts":1657**,"key_type":20019}]





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
                    self.troopMembers[troopQQNumber] = {memberQQ:[memberName,membernick]}
        # print(self.troopMembers)




print(1)
ERRCODE = errcode.err_code()
QQclass = QQ()
QQclass.processdb()

