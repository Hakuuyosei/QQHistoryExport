import os
import json
import binascii
import traceback
import subprocess
import javaobj

from src.errcode.errcode import ErrCode
from .textParsing import textParsing


class javaSerializedDataParsing():
    """java序列化相关类型的解析

    """
    def __init__(self, errcodeobj: ErrCode, textparsingobj: textParsing, configs):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj
        self.configs = configs


    def javaDeserializationToJson(self, data):
        """java序列化转json

        :param data: java序列化数据，bytes或者str（形如ACED00...）
        :return: state，json
        """
        dataStr = ""
        if type(data) == bytes:
            dataStr = binascii.hexlify(data).decode()
        elif type(data) == str:
            dataStr = data
        else:
            self.ERRCODE.parse_err("JAVA_DESER_ERR_INPUT_TYPE", [str(data), str(type(data))])
            return True, None


        # 使用javaobj解析
        try:
            # 解析Java序列化数据
            deserialized_obj = javaobj.loads(bytes.fromhex(dataStr))
        except Exception as e:
            self.ERRCODE.parse_err("JAVA_DESER_JSON_ERR_DECODE", [dataStr, e])
            return False, None
        # 返回json
        return True, deserialized_obj.__dict__

        # Editor: NoahShen admin@noahshen.top
        # Date: 2023/9/14
        # Reason: 使用javaobj替代原有链接到jvm的解析方式，优化运行速度


    def parse(self, msgType, msgData, extStr):
        """java序列化相关类型解析

        :param msgType: 消息类型
        :param msgData: 数据
        :param extStr:  extStr
        :return: msgOutData
        """
        msgOutData = {}
        # print(msgType)

        # 带回复引用的消息
        if msgType == -1049:
            try:
                str_data = msgData.decode("utf-8")
                msgOutData = {
                    "t": "msg",
                    "c": self.textParsing.parse(str_data)
                }
            except UnicodeDecodeError:
                self.ERRCODE.parse_err("TEXT_UNICODE_DECODE_ERROR", [msgType, msgData])
                msgOutData = {"t": "err", "c": {"text": "[文字]", "type": "text"}}

            if self.configs["needJavaDeser"] == False:
                msgOutData["c"].insert(0, {"t": "uns",
                                           "c": {"text": "[回复消息]", "type": "text"}
                                           })
            elif self.configs["needJavaDeser"] == True:

                try:
                    # print(extStr)
                    extStrJson = json.loads(extStr) if extStr else {}
                except json.JSONDecodeError as e:
                    self.ERRCODE.parse_err("EXTSTR_JSON_ERR_DECODE", [e, extStr])
                    return msgOutData

                if extStrJson:
                    # start_time = time.time()
                    if "sens_msg_source_msg_info" not in extStrJson:
                        self.ERRCODE.parse_err("EXTSTR_NOT_EXIST_TARGET", [extStr, "sens_msg_source_msg_info"])
                        return msgOutData
                    sourceMsgInfo = extStrJson["sens_msg_source_msg_info"]
                    state, jsonData = self.javaDeserializationToJson(sourceMsgInfo)

                    # 记录程序结束时间
                    # end_time = time.time()
                    # run_time = end_time - start_time
                    # print(f"程序运行时间为{run_time:.6f}秒")
                    if state:
                        mSourceMsgText = jsonData["mSourceMsgText"]
                        mSourceMsgSenderUin = jsonData["mSourceMsgSenderUin"]
                        mSourceMsgTime = jsonData["mSourceMsgTime"]
                        replyData = {
                            "text": mSourceMsgText,
                            "uin": mSourceMsgSenderUin,
                            "time": mSourceMsgTime
                        }
                        msgOutData["c"].insert(0, {"t": "reply",
                                             "c": replyData
                                             })
                        # print(msgOutData)
                    else:
                        msgOutData["c"].insert(0, {"t": "uns",
                                                   "c": {"text": "[回复消息]", "type": "text"}
                                                   })
                    # print(msgOutData)

                    # HACK
                    # (目前已弃用)
                    # if len(SourceMsgInfo) > 1048:
                    #     SourceMsgSenderQQnum = int(SourceMsgInfo[1016:1024],base=16)
                    #     SourceMsgTime = int(SourceMsgInfo[1040:1048],base=16)
                    #     msgOutData.append(["source",SourceMsgSenderQQnum,SourceMsgTime])
                    # else:
                    #     print("ERROR,SourceMsgInfo too short",SourceMsgInfo)
                    # #print(msgOutData)

        # 群文件
        elif msgType == -2017:
            if not self.configs["needJavaDeser"]:
                msgOutData = {
                    "t": "uns",
                    "c": {"text": "[文件]", "type": "media"}
                }
            else:
                err, jsonData = self.javaDeserializationToJson(msgData)
                if not err:

                    fileName = ""
                    filePath = ""
                    fileSize = ""
                    if jsonData:
                        fileName = jsonData["fileName"]
                        fileSize = jsonData["lfileSize"]

                    file = {
                        "received": False,
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
                # print(msgOutData)

        # 转发的聊天记录，java序列化
        elif msgType == -2011:
            # print("-2011", type(msgData))
            # print(binascii.hexlify(msgData).decode())
            return


        # 小程序/推荐名片，java 序列化套json
        elif msgType == -5008:
            pass
            #print(-5008,jd.javaDeserialization(binascii.hexlify(msgData).decode(),"miniapp"))
            #print(binascii.hexlify(msgData).decode())



        # elif msgType ==
        #     # msgOutData = self.decodeMixMsg(msgData)
        #     # print(msgOutData)
        #     print(msgType)
        #     print(msgData.decode("utf-8"))
        #     with open("./11.bin", 'wb') as f:  # 二进制流写到.bin文件
        #         f.write(msgData)
        #     1

        # 推荐名片
        elif msgType == -2007:
            # print(-2007, binascii.hexlify(msgData).decode())
            self.ERRCODE.parse_err("DIDNOT_PARSE_MSG", [msgType, msgData, extStr])
            msgOutData = {
                "t": "uns",
                "c": {"text": "[名片]", "type": "media"}
            }
            return msgOutData



        # 红包
        elif msgType == -2025:
            # print(-2025, binascii.hexlify(msgData).decode())
            self.ERRCODE.parse_err("DIDNOT_PARSE_MSG", [msgType, msgData, extStr])
            msgOutData = {
                "t": "uns",
                "c": {"text": "[红包]", "type": "media"}
            }
            return msgOutData

        # 新人入群 java + unknown
        elif msgType == -2059:
            # print(binascii.hexlify(msgData).decode())
            # jd.javaDeserialization(binascii.hexlify(msgData).decode(), "111")
            self.ERRCODE.parse_err("DIDNOT_PARSE_MSG", [msgType, msgData, extStr])
            msgOutData = {
                "t": "uns",
                "c": {"text": "[新人入群]", "type": "media"}
            }
            return msgOutData

        return msgOutData
