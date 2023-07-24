import hashlib
import os
import sys
import re
import traceback
import json
import imghdr
import shutil
import blackboxprotobuf
import subprocess

from src.errcode.errcode import ErrCode
from .textParsing import textParsing

sys.path.append("...")
from src.proto import Msg_pb2
from src.proto.RichMsg_pb2 import PicRec
from src.proto.RichMsg_pb2 import Msg

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
    """protobuf序列化相关类型解析

    """

    def __init__(self, errcodeobj: ErrCode, textparsingobj: textParsing, configs):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj
        self.configs = configs

        self.imgMD5Map = {}
        self.imgNum = 1
        self.videoNum = 1

    def decodeMarketFace(self, data):
        """解码大表情并移动

        :param data: 数据
        :return: 错误码，文件路径
        """
        emoticon_name = data + ".gif"
        output_path = "output/emoticons/emoticon2/" + emoticon_name
        lib_path = "lib/emoticons/emoticon2/" + emoticon_name

        try:
            if os.path.exists(output_path):
                return {}, output_path
            elif os.path.exists(lib_path):
                shutil.copy(lib_path, output_path)
                return {}, output_path
            else:
                return self.ERRCODE.parse_err("MARKETFACE_NOT_EXIST", [data]), None
        except OSError:
            return self.ERRCODE.parse_err("IO_ERROR", [traceback.format_exc()]), None

    def video_thumb(self, input_path, output_path):
        try:
            # 使用ffmpeg获取视频的第一帧并生成缩略图
            if os.path.exists(output_path):
                os.remove(output_path)

            ffmpeg_cmd = [
                'lib/ffmpeg-lgpl/ffmpeg.exe',
                '-i', input_path,
                '-ss', '00:00:00.000',  # 指定获取的时间点，这里取第一毫秒作为第一帧
                '-vframes', '1',  # 限制只取一帧
                output_path
            ]
            subprocess.run(ffmpeg_cmd, check=True, timeout=3)

            if os.path.exists(output_path):
                return output_path
        except subprocess.TimeoutExpired:
            return ""
        except subprocess.CalledProcessError as e:
            return ""


    def decodePic(self, data):
        """解码图片并移动

        :param data: 数据
        :return: msgOutData
        """
        if self.configs["needImages"] == False:
            msgOutData = {
                "t": "uns",
                "c": {"text": "[图片]"},
                "e": {}
            }
            return msgOutData
        elif self.configs["needImages"] == True:
            msgOutData = {
                "t": "img",
                "c": {"path": "", "type": "", "name": ""},
                "e": None
            }
            try:
                doc = PicRec()
                doc.ParseFromString(data)

                url = 'chatimg:' + doc.md5
                filename = hex(crc64(url))
                filename = 'Cache_' + filename.replace('0x', '')
                relpath = os.path.join(self.configs["imagesPath"], filename[-3:], filename)
                imgPath = os.path.join(filename[-3:], filename)
                # print(doc.uint32_width, doc.uint32_height, doc.uint32_image_type)
                msgOutData["c"]["type"] = "pic"
                # msgOutData["c"]["imgType"] = doc.uint32_image_type
                # 数据中，这两项宽高不可靠，请注意！
                # msgOutData["c"]["imgWidth"] = doc.uint32_height
                # msgOutData["c"]["imgHeight"] = doc.uint32_width

            except:
                # protobuf反序列化失败
                msgOutData["e"] = self.ERRCODE.parse_err("IMG_DESERIALIZATION_ERROR", [data])
                return msgOutData

            try:
                # 转存图片并去重

                # 判断文件是否存在
                if not os.path.exists(relpath):
                    msgOutData["e"] = self.ERRCODE.parse_err("IMG_NOT_EXIST", [relpath])
                    return msgOutData

                # 计算图片的MD5值
                with open(relpath, 'rb') as f:
                    img_data = f.read()
                    md5 = hashlib.md5(img_data).hexdigest()

                # 查找图片的MD5值是否已经存在
                if md5 in self.imgMD5Map:
                    msgOutData["e"] = {}
                    msgOutData["c"]["path"] = self.imgMD5Map[md5][0]
                    msgOutData["c"]["name"] = self.imgMD5Map[md5][1]
                    return msgOutData

                # 确定图片类型并添加后缀名
                img_type = imghdr.what(relpath)
                if img_type is None:
                    msgOutData["e"] = self.ERRCODE.parse_err("IMG_UNKNOWN_TYPE_ERROR", [imgPath])
                    return msgOutData

                new_filename = f'{self.imgNum}.{img_type}'
                self.imgNum = self.imgNum + 1
                new_file_path = os.path.join('output', 'images', new_filename)

                # 移动图片文件到output/images文件夹中，并重命名
                try:
                    shutil.copy(relpath, new_file_path)
                except:
                    msgOutData["e"] = self.ERRCODE.parse_err("IO_ERROR", [relpath, new_file_path])
                    return msgOutData

                # 将MD5和新文件路径添加到imgMD5Map中
                self.imgMD5Map[md5] = [new_file_path, new_filename]

                msgOutData["e"] = {}
                msgOutData["c"]["path"] = new_file_path
                msgOutData["c"]["name"] = new_filename
                return msgOutData
            except OSError:
                msgOutData["e"] = self.ERRCODE.parse_err("OS_ERROR", [traceback.format_exc()])

    def decodeMixMsg(self, data):
        """解码混合消息

        :param data: 数据
        :return: 错误码， msgList
        """
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
            return {}, msgList
        except:
            return self.ERRCODE.parse_err("MIXMSG_DESERIALIZATION_ERROR", [data, traceback.format_exc()]), None

    def decodeVideoMsg(self, data):
        """
        解码移动视频消息
        :param data: proto数据
        :return:
        """
        if self.configs["needVideo"] == False:
            msgOutData = {
                "t": "uns",
                "c": {"text": "[视频]"},
                "e": {}
            }
        elif self.configs["needVideo"] == True:
            msgOutData = {
                "t": "video",
                "c": {},
                "e": {}
            }
            try:
                doc = Msg_pb2.ShortVideo()
                doc.ParseFromString(data)
                filePath = doc.field3.decode("utf-8")
                # deserialize_data, message_type = blackboxprotobuf.decode_message(data)
                # print(f"原始数据: {deserialize_data}")
                # print(f"消息类型: {message_type}")
            except:
                msgOutData["e"] = self.ERRCODE.parse_err("VIDEO_DESERIALIZATION_ERROR", [data])
                return msgOutData

            pattern = r'/([A-F0-9]{32})/'
            match = re.search(pattern, filePath)
            if not match:
                msgOutData["e"] = self.ERRCODE.parse_err("VIDEO_UNKNOWN_PATH_FORMAT", [filePath])
                return msgOutData

            # 判断文件是否存在
            relpath = self.configs["videoPath"] + "\\" + match.group(1)
            print(relpath)
            if not os.path.exists(relpath):
                msgOutData["e"] = self.ERRCODE.parse_err("VIDEO_NOT_EXIST", [relpath])
                return msgOutData

            file_count = 0
            found_file = None
            for root, dirs, files in os.walk(relpath):
                for file in files:
                    if file != '.nomedia':
                        file_count += 1
                        found_file = os.path.join(root, file)

            if file_count == 0:
                msgOutData["e"] = self.ERRCODE.parse_err("VIDEO_NOT_EXIST", [relpath, file_count])
                return msgOutData
            elif file_count > 1:
                msgOutData["e"] = self.ERRCODE.parse_err("VIDEO_NOT_EXIST", [relpath, file_count])
                return msgOutData

            _, file_extension = os.path.splitext(found_file)
            new_filename = f'{self.videoNum}{file_extension}'
            new_picname = f'{self.videoNum}.jpg'
            self.videoNum += 1
            new_file_path = os.path.join('output', 'videos', new_filename)
            new_pic_path = os.path.join('output', 'videos', 'thumbs', new_picname)
            # 移动图片文件到output/videos文件夹中，并重命名
            try:
                shutil.copy(found_file, new_file_path)
            except:
                msgOutData["e"] = self.ERRCODE.parse_err("IO_ERROR", [found_file, new_file_path])
                return msgOutData

            msgOutData["c"]["path"] = new_file_path
            msgOutData["c"]["name"] = new_filename

            msgOutData["c"]["thumb"] = self.video_thumb(new_file_path, new_pic_path)
            return msgOutData

    def parse(self, msgType, msgData, extStr):
        """protobuf序列化相关类型解析

        :param msgType: 消息类型
        :param msgData: 数据
        :param extStr:  extStr
        :return: msgOutData
        """
        msgOutData = {}

        # 图片类型
        if msgType == -2000:
            msgOutData = self.decodePic(msgData)


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

            # print(filePath,voiceLength)
            # slkamrTomp3.slkamrTomp3(filePath)

        # 短视频
        elif msgType == -2022:
            msgOutData = self.decodeVideoMsg(msgData)
            return msgOutData


        # 大号表情
        elif msgType == -8018:
            if self.configs["needMarketFace"] == False:
                msgOutData = {
                    "t": "uns",
                    "c": {"text": "[大表情]"},
                    "e": {}
                }
            elif self.configs["needMarketFace"] == True:
                doc = Msg_pb2.marketFace()
                doc.ParseFromString(msgData)
                marketFaceName = doc.field7.decode("utf-8")[1:]
                descErrcode, msgDeseData = self.decodeMarketFace(marketFaceName)
                msgOutData = {
                    "t": "img",
                    "c": {"path": msgDeseData, "name": marketFaceName, "type": "marketFace"},
                    "e": descErrcode
                }
                print(extStr)
            return msgOutData


        elif msgType == -5040:  # 灰条消息
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
                        "e": {}
                    }
                    # print(extStr)
                # 群主（或管理员，待验证）撤回
                elif extStrJson["revoke_op_type"] == "2":
                    msgOutData = {
                        "t": "revoke",
                        "c": {"text": msgData, "type": "byAdmin"},
                        "e": {}
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
                # print(doc.field5.decode("utf-8"))
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
                        "e": {}
                    }
                else:
                    msgOutData = {
                        "t": "tip",
                        "c": {"type": "invite"},
                        "e": self.ERRCODE.parse_err("EXTSTR_NOT_EXIST_TARGET", [extStr, "invitee or invitor "])
                    }


            # busi_type
            elif "uint64_busi_type" in extStrJson.keys():
                busi_type = extStrJson["uint64_busi_type"]

                # 签到打卡
                if busi_type == "14" and busi_type == "1":
                    doc = Msg_pb2.grayTipBar()
                    doc.ParseFromString(msgData)

                    msgDecodedData = doc.field5.decode("utf-8")
                    print(14, doc.field5.decode("utf-8"))
                    msgOutData = {
                        "t": "tip",
                        "c": {"text": msgDecodedData, "type": "dailyattendance"},
                        "e": {}
                    }

                # 灰条戳一戳
                elif busi_type == "12":
                    doc = Msg_pb2.grayTipBar()
                    doc.ParseFromString(msgData)
                    msgDecodedData = doc.field5.decode("utf-8")
                    print(12, extStrJson["bytes_content"])
                    print(12, doc.field5.decode("utf-8"))
                    msgOutData = {
                        "t": "tip",
                        "c": {"text": msgDecodedData, "type": "paiyipai"},
                        "e": {}
                    }

                else:
                    doc = Msg_pb2.grayTipBar()
                    doc.ParseFromString(msgData)
                    msgDecodedData = doc.field5.decode("utf-8")
                    print(busi_type, doc.field5.decode("utf-8"))
                    msgOutData = {
                        "t": "tip",
                        "c": {"text": msgDecodedData, "type": "unknown"},
                        "e": {}
                    }
                    print(extStr)

            else:
                doc = Msg_pb2.grayTipBar()
                doc.ParseFromString(msgData)
                msgDecodedData = doc.field5.decode("utf-8")
                print(doc.field5.decode("utf-8"))
                msgOutData = {
                    "t": "tip",
                    "c": {"text": msgDecodedData, "type": "unknown"},
                    "e": {}
                }
                print(extStr)



        # 群标识卡片,戳一戳
        elif msgType == -5020:
            doc = Msg_pb2.grayTipBar()
            doc.ParseFromString(msgData)
            msgDecodedData = doc.field5.decode("utf-8")
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDecodedData, "type": "unknown"},
                "e": {}
            }

        elif msgType == -5023:  # 该用户通过***向你发起临时会话，前往设置。
            # deserialize_data, message_type = blackboxprotobuf.decode_message(msgData)
            # print(f"-5023原始数据: {deserialize_data}")
            # print(f"消息类型: {message_type}")
            pass

        return msgOutData
