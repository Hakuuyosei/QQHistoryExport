import os
import json
import binascii
import traceback
import subprocess
import time

from src.errcode.errcode import err_code
from .textParsing import textParsing


class javaSerializedDataParsing():
    """java序列化相关类型的解析

    """
    def __init__(self, errcodeobj: err_code, textparsingobj: textParsing, configs):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj
        self.configs = configs

    def javaDeserializationToJson(self, data):
        """java序列化转json

        :param data: java序列化数据，bytes或者str（形如ACED00...）
        :return: 错误码，json
        """
        dataStr = ""
        if type(data) == bytes:
            dataStr = binascii.hexlify(data).decode()
        elif type(data) == str:
            dataStr = data
        else:
            return self.ERRCODE.parse_err("JAVA_DESER_ERR_INPUT_TYPE", [str(data), str(type(data))]), None

        javaDeserCmd = "java -jar ./lib/javaDeserialization/QQdecode-1.0.jar " + dataStr
        javaDeserCmdOutput = subprocess.getoutput(javaDeserCmd)

        try:
            jsonData = json.loads(javaDeserCmdOutput)
            return {}, jsonData
        except json.JSONDecodeError as e:
            return self.ERRCODE.parse_err("JAVA_DESER_JSON_ERR_DECODE", [dataStr]), None


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
            msgOutData = {
                "t": "msg",
                "c": self.textParsing.parse(msgData.decode("utf-8")),
                "e": {}
            }
            if self.configs["needReplyMsg"] == False:
                msgOutData["c"].insert(0, {"t": "uns",
                                           "c": {"text": "[回复消息]"},
                                           "e": {}
                                           })
            elif self.configs["needReplyMsg"] == True:

                try:
                    # print(extStr)
                    extStrJson = json.loads(extStr)
                except json.JSONDecodeError as e:
                    return self.ERRCODE.parse_err("EXTSTR_JSON_ERR_DECODE", []), None

                if extStrJson:
                    start_time = time.time()
                    sourceMsgInfo = extStrJson["sens_msg_source_msg_info"]
                    err, jsonData = self.javaDeserializationToJson(sourceMsgInfo)

                    # 记录程序结束时间
                    end_time = time.time()
                    run_time = end_time - start_time
                    print(f"程序运行时间为{run_time:.6f}秒")
                    if jsonData:
                        mSourceMsgText = jsonData["mSourceMsgText"]
                        mSourceMsgSenderUin = jsonData["mSourceMsgSenderUin"]
                        mSourceMsgTime = jsonData["mSourceMsgTime"]
                        replyData = {
                            "sourceMsgText": mSourceMsgText,
                            "sourceMsgSenderUin": mSourceMsgSenderUin,
                            "sourceMsgTime": mSourceMsgTime
                        }
                        msgOutData["c"].insert(0, {"t": "reply",
                                             "c": replyData,
                                             "e": err
                                             })
                        print(msgOutData)

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
            err, jsonData = self.javaDeserializationToJson(msgData)

            fileName = ""
            filePath = ""
            fileSize = ""
            if jsonData:
                fileName = jsonData["fileName"]
                fileSize = jsonData["lfileSize"]

            file = {
                "received": False,
                "fileName": fileName,
                "filePath": filePath,
                "fileSize": fileSize
            }
            msgOutData = {
                "t": "file",
                "c": file,
                "e": err
            }
            print(msgOutData)

        # 转发的聊天记录，java序列化
        elif msgType == -2011:
            # print("-2011", type(msgData))
            # print(binascii.hexlify(msgData).decode())
            return


        # 小程序/推荐名片，java 序列化套json
        elif msgType == -5008:
            #print(-5008,jd.javaDeserialization(binascii.hexlify(msgData).decode(),"miniapp"))
            print(binascii.hexlify(msgData).decode())



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
            print(-2007, binascii.hexlify(msgData).decode())
            return

        # 红包
        elif msgType == -2025:
            print(-2025, binascii.hexlify(msgData).decode())
            return

        # 新人入群 java + unknown
        elif msgType == -2059:
            # print(binascii.hexlify(msgData).decode())
            # jd.javaDeserialization(binascii.hexlify(msgData).decode(), "111")
            return

        return msgOutData
