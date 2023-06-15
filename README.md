# QQHistoryExport

安卓设备聊天记录导出，支持图片视频/音频/引用/文件 大部分消息，支持几乎所有的重要消息类型，支持PDF导出，未来将支持html导出

## 前言

本项目的消息解码，数据库读取，QQ表情（emoticon1）来自[Yiyiyimu/QQ-History-Backup](https://github.com/Yiyiyimu/QQ-History-Backup)，感谢为QQ聊天记录解析的一众大佬

本项目支持更多（大部分重要的消息类型）解析了java序列化类型消息，支持PDF导出，未来将支持html导出。

## features

-  支持对话，群聊导出
-  支持自动查找密钥
-  自动合并 db 和 slow-table
-  支持新旧 QQ emoji
- 支持混合消息，图片消息

以上功能来自[Yiyiyimu/QQ-History-Backup](https://github.com/Yiyiyimu/QQ-History-Backup)

以下为本项目独立实现的功能

- 有详细的文档
- 支持java序列化类型消息解析
- 支持读取**好友表，群聊表，群友表**数据库
- 支持extStr解析，获取了**消息的更多属性**
- 支持**引用消息**
- 支持**文件类型消息**
- 支持**QQ大表情**（marketFace）
- 支持**图片导出**，将图片从巨大的chatimg中复制出来，**猜测类型**并md5**防重复**
- PDF文档相同的图片只储存一份
- 支持大部分**灰条消息**（包括但不限于 撤回 修改群名称 获得群标签 戳一戳）
- 自动通过网络接口**获取头像**
- 支持导出带**书签**带**头像**带**时间**带**页脚**的PDF文件
- 自己写的**排版引擎**，在（混合消息）PDF的文字中方便的放入QQemoji，图片等
- PDF**可设置**间距大小栏数，字体大小，是否显示头像等等
- PDF生成支持**彩色emoji**
- 支持**视频消息**

## How to use

### 测试方法

目前该仓库处于私有仓库测试阶段

测试方法如下

test.json格式：

key可填IMEI码

```json
{
	"targetQQ":"7xxxxx",
	"fileName":"./QQdb/xxxxx.db",
	"chatimgPath":"xxxx/chatimg",
	"key":"8xxxxxxxx",
	"cmd":"",
	"ext":""
}
```

先修改main函数的测试部分到你需要的测试部分，再测试

### 需要提取的文件

#### 根目录

**data/data/com.tencent.mobileqq**

方案一：（有root）直接提取出来整个文件夹并填写目录即可

方案二：（有root）只提取以下三个文件,和上述方法的效果是一样的

```
data/data/com.tencent.mobileqq/databases/{你的QQ号}.db
data/data/com.tencent.mobileqq/databases/slowtable_{QQ}.db
//下面这一项其实是手机IMEI码，你也可以不提取这个，直接将IMEI码输入程序
data/data/com.tencent.mobileqq/files/kc
```

方案三：（无root）通过手机备份功能拿出QQ的数据，里面有db，f等文件夹，不需要重命名，直接输入程序即可

#### 内部存储

**Android/data/com.tencent.mobileqq/Tencent/MobileQQ/**

该目录不需要root权限，按需提取：

```
图片文件：上述目录/chatpic/chatimg（文件夹）
视频文件：上述目录/shortvideo（文件夹）
语音文件：上述目录/{你的QQ号}/ptt(文件夹）
```



## Instruction for folders

config:设置，设置样本文件

lib:依赖库，依赖文件等

scripts:独立脚本

​	colorEmojiImage:将文件夹中unicode emoji表情图片合并成一个文件并创建信息数据库

​	fontQuerySize:通过PIL查询字体宽高比并存入字体信息数据库

​	nudgeactionResDownload:下载nudgeaction类型图片（还未投入使用）

src:主程序

​	errcode:错误管理模块

​	dataParsing:数据解析模块

​		parsing.py:总解析模块

​		textParsing.py:文本信息解析

​		unserializedDataParsing.py:未序列化类型数据解析

​		javaSerializedDataParsing.py:java序列化类型数据解析

​		protoDataParsing.py:protobuf序列化类型解析

​	avatarDownload:通过接口下载头像模块

​	generate:生成可视文件图片

​		GeneratePDF_ReportLab.py:使用ReportLab生成PDF

​	proto:proto反序列化相关文件

## TODO

- [ ] web导出
- [ ] 音频消息导出（coding）
- [ ] 视频消息导出（coding）
- [ ] PDF生成程序的错误处理
- [ ] 程序UI
- [ ] 使用说明
- [ ] 支持卡片消息
- [ ] 完善错误管理
- [ ] 添加多几种emoji表情供选择
- [ ] 增加PDF绘制图片自定义尺寸，非统一管理缩放
- [ ] 明确设置群组好友格式，防止QQ群号和用户号重复



## limitations

### 消息解析

- [ ] 一个消息的总ERRCODE只支持一个，可能遇到不足的问题

- [ ] 灰条消息（撤回，获得群荣誉，修改群名等等等）直接从protobuf提取出来的字符串，可能存在“icon”等字符（可以通过解析extStr中的html解决，但挺费力）

- [ ] 灰条消息（撤回，获得群荣誉，修改群名等等等）直接从protobuf提取出来的字符串，相关人员的名称使用的可能是当时的昵称，无法自由配置（可以通过解析extStr中的html解决，但挺费力）

- [ ] json格式的卡片消息类型较多（参考：[QQ发送卡片消息 - 言成言成啊 - 博客园 (cnblogs.com)](https://www.cnblogs.com/meethigher/p/13581506.html)），难以提取出关键信息

- [ ] 无法解析合并转发消息的第二层序列化，入群消息（xx座男一枚，xxxx这种）

- [ ] 解析时抛弃了一些属性，若有需要可修改，提交pr

  

### PDF生成

- [ ] 灰条消息没有写换行
- [ ] 没有错误处理
- [ ] 排版引擎在计算字体宽度时大约有3%的误差，略不美观，望大佬指点

## license

由于本项目的特殊性质，本项目禁止一切形式的商业用途。

## Final thanks to

https://github.com/Yiyiyimu/QQ_History_Backup

https://github.com/roadwide/qqmessageoutput

https://gist.github.com/WincerChan/362331456a6e0417c5aa1cf3ff7be2b7

https://github.com/protocolbuffers/protobuf

https://github.com/nccgroup/blackboxprotobuf（测试阶段使用，不在项目代码中）

https://github.com/rohankumardubey/SerializationDumper（测试阶段使用，不在项目代码中）

https://github.com/kn007/silk-v3-decoder

https://github.com/FFmpeg/FFmpeg （LGPL bulid）
