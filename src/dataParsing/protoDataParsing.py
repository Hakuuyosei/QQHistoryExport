import hashlib
import os
import sys
import traceback
import json
import imghdr
import shutil
import blackboxprotobuf

from ..errcode.errcode import err_code
from .textParsing import textParsing


sys.path.append("...")
from proto import Msg_pb2
from proto.RichMsg_pb2 import PicRec
from proto.RichMsg_pb2 import Msg

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


class protoDataParsing():
    def __init__(self, errcodeobj: err_code, textparsingobj: textParsing, chatImgPath):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj

        self.chatImgPath = chatImgPath

        self.imgMD5Map = {}
        self.imgNum = 1

    # 解码大表情
    def decodeMarketFace(self, data):
        emoticon_name = data + ".jif"
        output_path = "output/emoticon2/" + emoticon_name
        lib_path = "...lib/emoticon2/" + emoticon_name

        if os.path.exists(output_path):
            return self.ERRCODE.NORMAL(), output_path
        elif os.path.exists(lib_path):
            shutil.copy(lib_path, output_path)
            return self.ERRCODE.NORMAL(), output_path
        else:
            return self.ERRCODE.MARKETFACE_NOT_EXIST(), ""

    # 解码图片
    def decodePic(self, data):
        msgOutData = {
            "t": "img",
            "c": {"imgPath": "", "imgType": "", "name": ""},
            "e": None
        }
        try:
            doc = PicRec()
            doc.ParseFromString(data)


            url = 'chatimg:' + doc.md5
            filename = hex(crc64(url))
            filename = 'Cache_' + filename.replace('0x', '')
            relpath = os.path.join(self.chatImgPath, filename[-3:], filename)
            imgPath = os.path.join(filename[-3:], filename)
            print(doc.uint32_width, doc.uint32_height, doc.uint32_image_type)
            # msgOutData["c"]["imgType"] = doc.uint32_image_type
            # 数据中，这两项宽高顺序未知，请注意！
            # msgOutData["c"]["imgWidth"] = doc.uint32_height
            # msgOutData["c"]["imgHeight"] = doc.uint32_width

            # 判断文件是否存在
            if not os.path.exists(relpath):
                msgOutData["e"] = self.ERRCODE.IMG_NOT_EXIST(imgPath)
                return msgOutData

            # 计算图片的MD5值
            with open(relpath, 'rb') as f:
                img_data = f.read()
                md5 = hashlib.md5(img_data).hexdigest()

            # 查找图片的MD5值是否已经存在
            if md5 in self.imgMD5Map:
                msgOutData["e"] = self.ERRCODE.NORMAL()
                msgOutData["c"]["imgPath"] = self.imgMD5Map[md5][0]
                msgOutData["c"]["name"] = self.imgMD5Map[md5][1]
                return msgOutData

            # 确定图片类型并添加后缀名
            img_type = imghdr.what(relpath)
            if img_type is None:
                msgOutData["e"] = self.ERRCODE.IMG_UNKNOWN_TYPE_ERROR(imgPath)
                return msgOutData

            new_filename = f'{self.imgNum}.{img_type}'
            self.imgNum = self.imgNum + 1
            new_file_path = os.path.join('output', 'images', new_filename)


            # 移动图片文件到output/images文件夹中，并重命名
            shutil.copy(relpath, new_file_path)

            # 将MD5和新文件路径添加到imgMD5Map中
            self.imgMD5Map[md5] = [new_file_path, new_filename]

            msgOutData["e"] = self.ERRCODE.NORMAL()
            msgOutData["c"]["imgPath"] = new_file_path
            msgOutData["c"]["name"] = new_filename
            return msgOutData

        except:
            msgOutData["e"] = self.ERRCODE.IMG_DESERIALIZATION_ERROR(data)
            return msgOutData

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
                        for msgElem2 in self.textParsing.parse(msgText):
                            msgList.append(msgElem2)
            return self.ERRCODE.NORMAL(), msgList
        except:
            return self.ERRCODE.MIXMSG_DESERIALIZATION_ERROR(data, traceback.format_exc()), msgList

    def parse(self, msgType, msgData, extStr, senderQQ):
        msgOutData = {}
        print(msgType)

        # 图片类型
        if msgType == -2000:
            # print(msgData)
            msgOutData = self.decodePic(msgData)
            #print(extStr)

        # 图文混排
        elif msgType == -1035:
            DeseErrcode, msgDeseData = self.decodeMixMsg(msgData)
            msgOutData = {
                "t": "mixmsg",
                "c": msgDeseData,
                "e": DeseErrcode
            }
            # print(msgOutData)

        # 语音
        elif msgType == -2002:
            doc = Msg_pb2.Voice()
            doc.ParseFromString(msgData)
            filePath = doc.field1
            voiceLength = doc.field19

            # deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
            # print(f"原始数据: {deserialize_data}")
            # print(f"消息类型: {message_type}")

            #print(filePath,voiceLength)
            #slkamrTomp3.slkamrTomp3(filePath)

        # 短视频
        elif msgType == -2022:
            doc = Msg_pb2.ShortVideo()
            doc.ParseFromString(msgData)
            filePath = doc.field3.decode("utf-8")
            print(filePath)


        # 群标识卡片
        elif msgType == -5020:
            deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
            print(f"原始数据: {deserialize_data}")
            print(f"消息类型: {message_type}")
            return

        elif msgType == -5023:  # 该用户通过***向你发起临时会话，前往设置。
            deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
            print(f"原始数据: {deserialize_data}")
            print(f"消息类型: {message_type}")
            print(msgData)
            print(deserialize_data["5"].decode("utf-8"))
            return

        # 大号表情
        elif msgType == -8018:
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


        elif msgType == -5040:# 灰条消息
            extStrJson = json.loads(extStr)

            if "revoke_op_type" in extStrJson.keys():
                # 自己撤回
                if extStrJson["revoke_op_type"] == "0":
                    doc = Msg_pb2.grayTipBar()
                    doc.ParseFromString(msgData)
                    msgText = doc.field5.decode("utf-8")
                    # 撤回消息
                    msgOutData = {
                        "t": "revoke",
                        "c": {"text": msgText, "type": "bySelf"},
                        "e": self.ERRCODE.NORMAL()
                    }
                    # print(extStr)
                # 群主（或管理员，待验证）撤回
                elif extStrJson["revoke_op_type"] == "2":
                    msgOutData = {
                        "t": "revoke",
                        "c": {"text": msgData, "type": "byAdmin"},
                        "e": self.ERRCODE.NORMAL()
                    }
                    # print(extStr)
                else:
                    print(msgData)
                    print(extStr)

            # 被邀请进入群聊
            elif ("inviteeUin" in extStrJson.keys()) or ("invitorUin" in extStrJson.keys()):
                doc = Msg_pb2.grayTipBar()
                doc.ParseFromString(msgData)
                msgDecodedData = doc.field5.decode("utf-8")
                print(doc.field5.decode("utf-8"))
                if ("inviteeUin" in extStrJson.keys()) and ("invitorUin" in extStrJson.keys()):
                    inviteeUin = extStrJson["inviteeUin"]
                    invitorUin = extStrJson["invitorUin"]
                    items = {
                        "inviteeUin": inviteeUin,
                        "invitorUin": invitorUin
                    }
                    msgOutData = {
                        "t": "tip",
                        "c": {"text": msgDecodedData, "type": "invite", "ext": items},
                        "e": self.ERRCODE.NORMAL()
                    }
                else:
                    msgOutData = {
                        "t": "tip",
                        "c": {"type": "invite"},
                        "e": self.ERRCODE.ALL_EXTSTR_NOT_EXIST_TARGET(extStr, "invitee or invitor ")
                    }


            # busi_type
            elif "uint64_busi_type" in extStrJson.keys():
                busi_type = extStrJson["uint64_busi_type"]

                # 签到打卡
                if busi_type == "14":
                    doc = Msg_pb2.grayTipBar()
                    doc.ParseFromString(msgData)
                    #print(doc.field5.decode("utf-8"))
                    #print(extStrJson["bytes_content"])

                # 可能是拍一拍
                elif busi_type == "12":
                    doc = Msg_pb2.grayTipBar()
                    doc.ParseFromString(msgData)
                    print(doc.field5.decode("utf-8"))
                    print(111, extStrJson["bytes_content"])

                else:
                    deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
                    print(f"原始数据: {deserialize_data}")
                    print(deserialize_data["5"].decode("utf-8"))
                    print(extStr)

            else:
                deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
                print(f"原始数据: {deserialize_data}")
                print(deserialize_data["5"].decode("utf-8"))
                print(extStr)

        return msgOutData



