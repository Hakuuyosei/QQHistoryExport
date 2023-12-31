import os
import json
import traceback

from src.errcode.errcode import ErrCode
from .textParsing import textParsing


class unserializedDataParsing():
    """未序列化的消息类型解析

    """
    def __init__(self, errcodeobj: ErrCode, textparsingobj: textParsing, configs):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj
        self.configs = configs

    def c2cCallParse(self, data):
        """解析私聊电话信息

        :param data: btyes
        :return:data
        """
        # 数据第一个字符是0x16，先去除
        callDatas = data[1:].decode("utf-8").split("|")

        if len(callDatas) != 4:
            return None
        else:
            return callDatas[0]

    
    def parse(self, msgType, msgData, extStr):
        """未序列化类型解析

        :param msgType: 消息类型
        :param msgData: 数据
        :param extStr:  extStr
        :return: msgOutData
        """
        msgOutData = {}
        # print(msgType)

        # 普通文字
        if msgType == -1000 or msgType == -1051:
            try:
                str_data = msgData.decode("utf-8")
                msgOutData = {
                    "t": "msg",
                    "c": self.textParsing.parse(str_data)
                }
            except UnicodeDecodeError:
                self.ERRCODE.parse_err("TEXT_UNICODE_DECODE_ERROR", [msgType, msgData])
                msgOutData = {"t": "err", "c": {"text": "[文字]", "type": "text"}}



            # print(msgOutData)
            # print(extStr)

        # 加群提示
        elif msgType == -1012:
            extStrJson = json.loads(extStr) if extStr else {}
            msgDecodedData = msgData.decode("utf-8")
            msgDecodedData = msgDecodedData[0:msgDecodedData.find("，点击修改TA的群昵称")]
            items = {
                "newmember": extStrJson["troop_new_member_uin"]
            }
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDecodedData, "type": "join_group", "ext": items}
            }
            # print(extStr)

        # 邀请Q群管家
        elif msgType == -2042:
            msgDecodedData = msgData.decode("utf-8")
            msgDecodedData2 = msgDecodedData[msgDecodedData.find("##**##") + 6 :]
            msgDecodedData = msgDecodedData[0:msgDecodedData.find("           ")]
            invitorUin = msgDecodedData2.split(",")[5]
            inviteeUin = msgDecodedData2.split(",")[15]
            items = {
                "inviteeUin": inviteeUin,
                "invitorUin": invitorUin
            }
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDecodedData, "type": "qbot_join_group", "ext": items}
            }


        elif msgType == -2015:  # 发表说说，明文json
            return None

        elif msgType == -1034:  # 似乎是个性签名，明文json
            return None

        elif msgType == -2005:  # 已经被保存到本地的文件，内容为路径
            try:
                isSucceed = True
                fileData = msgData[1:].decode("utf-8").split("|")
                if len(fileData) >= 5:
                    filePath = fileData[-5]
                    fileSize = int(fileData[-4])
                    fileName = os.path.basename(filePath)

                elif 4 >= len(fileData) > 2:
                    filePath = fileData[0]
                    fileSize = int(fileData[1])
                    fileName = os.path.basename(filePath)

                else:
                    self.ERRCODE.parse_err("FILE_UNKNOWN_FORMAT", [msgType, msgData])
                    isSucceed = False

                # 文件信息split后可能并不是准确个数的数据，所以采用倒着索引

            except Exception as e:
                error_info = traceback.format_exc()
                self.ERRCODE.parse_err("FILE_UNKNOWN_FORMAT", [e, error_info, msgType,  msgData])
                isSucceed = False
                # print(error_info)


            # extStrJson = json.loads(extStr) if extStr else {}
            # if "file_pic_width" in extStrJson.keys():
            #     if int(extStrJson["file_pic_width"]) > 0:
            #         # 文件形式的图片
            #
            #         msgOutData = {
            #             "t": "file",
            #             "c": file
            #         }
            #     else:
            #         msgOutData = {
            #             "t": "file",
            #             "c": file
            #         }
            # else:

            # print(fileData, extStr)
            if isSucceed:
                file = {
                    "received": True,
                    "name": fileName,
                    "path": filePath,
                    "size": fileSize
                }
                msgOutData = {
                    "t": "file",
                    "c": file
                }
            else:
                msgOutData = {"t": "err", "c": {"text": "[文件]", "type": "media"}}

        elif msgType == -3008:  # 未被接收的文件，内容为文件名
            fileName = msgData.decode("utf-8")
            file = {
                "received": False,
                "name": fileName
            }
            msgOutData = {
                "t": "file",
                "c": file
            }
            # print(extStr)

        elif msgType == -2016:  # 群语音通话发起
            msgDecodedData = msgData.decode("utf-8")
            msgDataText = msgDecodedData.split("|")
            # print(extStr)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDecodedData, "type": "group_call_start"}
            }

        elif msgType == -4008:  # 群语音通话结束
            msgDataAlreadyDecode = msgData.decode("utf-8")
            # print(extStr)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDataAlreadyDecode, "type": "group_call_end"}
            }

        elif msgType == -1013:  # 你已经和xxx成为好友，现在可以开始聊天了。
            msgDataAlreadyDecode = msgData.decode("utf-8")
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDataAlreadyDecode, "type": "new_friend", "ext": {}}
            }

            print(msgDataAlreadyDecode)

        # 私聊语音通话
        elif msgType == -2009:
            msgDataAlreadyDecode = self.c2cCallParse(msgData)
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDataAlreadyDecode, "type": "friend_call"}
            }

        # 私聊语音通话异常
        elif msgType == -1001:
            msgDataAlreadyDecode = self.c2cCallParse(msgData)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDataAlreadyDecode, "type": "friend_call_err"}
            }

        # 戳一戳
        elif msgType == -5012:
            msgDataAlreadyDecode = json.loads(msgData.decode("utf-8"))
            # print(-5012, msgDataAlreadyDecode)
            msgText = msgDataAlreadyDecode["msg"]
            msgOutData = {
                "t": "nudge",
                "c": {"text": msgText}
            }

        # 戳一戳
        elif msgType == -5018:
            msgDataAlreadyDecode = json.loads(msgData.decode("utf-8"))
            msgText = msgDataAlreadyDecode["msg"]
            msgSummary = msgDataAlreadyDecode["summary"]
            msgOutData = {
                "t": "nudge",
                "c": {"text": msgText}
            }
            


        return msgOutData
