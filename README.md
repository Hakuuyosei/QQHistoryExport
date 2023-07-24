# QQHistoryExport

安卓设备聊天记录导出，支持图片/视频/音频/引用/文件 大部分消息，支持几乎所有的重要消息类型，支持PDF导出，未来将支持html导出

## 前言

本项目的消息解密，数据库读取，QQ表情（emoticon1）来自[Yiyiyimu/QQ-History-Backup](https://github.com/Yiyiyimu/QQ-History-Backup)，感谢为QQ聊天记录解析的一众大佬

本项目支持更多（大部分重要的消息类型）解析了java序列化类型消息，支持PDF导出，未来将支持html导出。

## features

-  支持对话，群聊导出
-  支持自动查找密钥
-  自动合并 db 和 slow-table
-  支持新旧 QQ emoji
- 支持混合消息，图片消息

以上功能来自[Yiyiyimu/QQ-History-Backup](https://github.com/Yiyiyimu/QQ-History-Backup)

以下为本项目独立实现的功能

- 详细的文档
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
- 有很多自定义**可设置**项
- 有**GUI界面**

## 使用说明

### 0.有关测试

目前该仓库处于私有仓库测试阶段

先修改main函数的测试部分到你需要的测试部分，再测试

### 1.下载软件

[Releases · WhiteWingNightStar/QQHistoryExport (github.com)](https://github.com/WhiteWingNightStar/QQHistoryExport/releases)

在这里下载编译好的软件，目前只编译Windows版本，python编译版本3.8，理论上支持win7

建议系统：win10 win11

放在一个没有中文路径的目录防止出错，exe和lib都要解压出来。

### 2.提取文件

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

### 2.运行程序

本程序目前提供了基于PyQt5的UI。可以直接通过UI设置解析。

建议使用纯ANSCII路径（纯英文数字或anscii符号），防止出现问题。

也可以复制`config/parse_config_example.json`到`config/parse_config.json`，有设置项检验程序。

**注意：解析回复的原消息部分，解析群文件信息，需要用户安装java环境。**

命令行输入`java -version`检查java环境是否安装成功。

### 3.生成PDF

接下来可以运行自动下载头像，将会访问QQ接口下载头像。

你也可以不运行这个，自己导入头像图片或者不用头像。

解析完毕后，会生成一个output文件夹，里面的chatData.txt即为符合`output格式.md`的解析完的聊天数据。

里面有一个文件夹senders。senders/senders.json现在是这个样子。每一个键是一个用户。

格式为：{用户QQ号:[用户昵称, 用户头像路径]}

![image-20230724145118110](README/image-20230724145118110.png)

你也可以自己编辑这个senders/senders.json，而不使用接口下载头像，或者如果你不想用从数据库里提取出来的昵称，也要修改这个文件。

**注意！头像的路径是相对于项目根目录的相对路径！**

**注意！目前friend模式无法获取用户自身的昵称，需要你修改这个文件，将你的昵称填进去！**

修改完后记得保存，再运行生成PDF。



## 项目原理

### 项目结构

```
config:设置，设置样本文件
lib:依赖库，依赖文件等
	emoticons:QQ表情资源文件
		emoticon1:QQ小表情
		emoticon2:QQ大表情
		nudgeaction:戳一戳等表情（还未投入使用）
	fonts:字体
	javaDeserialization:java反序列化程序
	
scripts:独立脚本
	colorEmojiImage:将文件夹中unicode emoji表情图片合并成一个文件并创建信息数据库
	fontQuerySize:通过PIL查询字体宽高比并存入字体信息数据库
	nudgeactionResDownload:下载nudgeaction类型图片（还未投入使用）
	
src:主程序
	errcode:错误管理模块
	dataParsing:数据解析模块
		parsing.py:总解析模块
		textParsing.py:文本信息解析
		unserializedDataParsing.py:未序列化类型数据解析
		javaSerializedDataParsing.py:java序列化类型数据解析
		protoDataParsing.py:protobuf序列化类型解析
	avatarDownload:通过接口下载头像模块
	generate:生成可视文件图片
		GeneratePDF_ReportLab.py:使用ReportLab生成PDF
	proto:proto反序列化相关文件
	GUI:GUI模块
		res:资源文件夹
		GUI.py:GUI操作文件
		mainInterface.py:由pyuic5生成的界面代码
		mainInterface.ui:由QtDesigner绘制的界面
		res_rc.py:由pyrcc5生成的资源文件代码
	validateSettings:设置项验证模块
		
```

### 解析

解析QQ聊天记录本地数据库，目前只支持安卓。

因为历史原因，QQ聊天记录结构复杂多样~~（屎山）~~，分析难度很高，各种序列化模式混用，有protobuf，json，java序列化或是字符串分隔。所以解析代码写的很长。

~~吐槽：为什么QQ的数据库里，群组是group啊~~

具体的分析，请看这几篇博客：

[QQ安卓端聊天记录数据分析 一 | 寄东南のBlog (sendtosoutheast.github.io)](https://sendtosoutheast.github.io/2022/07/29/逆向分析/QQ聊天记录/qqhistory1/)

[QQ安卓端聊天记录数据分析 二 | 寄东南のBlog (sendtosoutheast.github.io)](https://sendtosoutheast.github.io/2022/11/09/逆向分析/QQ聊天记录/qqhistory2/)

[QQ安卓端聊天记录数据分析 三 | 寄东南のBlog (sendtosoutheast.github.io)](https://sendtosoutheast.github.io/2022/11/24/逆向分析/QQ聊天记录/qqhistory3/)

解析完毕后，会生成一个output文件夹，里面的chatData.txt即为符合`output格式.md`的解析完的聊天数据。里面的路径指向以下资源的相对路径。

```
emoticons文件夹是依赖的表情，只会将用到的复制到output中
images文件夹是聊天图片
senders文件夹是发送者相关信息，若使用自动获取头像，将会修改这里的信息
videos文件夹是聊天视频资源，里面有一个文件夹thumbs，是使用ffmpeg生成的缩略图
voices文件夹是语音，使用slik_v3_decoder和ffmpeg转码为了mp3
```

你可以参考`output格式.md`，写其它生成脚本，欢迎贡献代码。

目前写完了PDF导出，基于reportLab：

[QQ安卓端聊天记录数据分析 四 | 寄东南のBlog (sendtosoutheast.github.io)](https://sendtosoutheast.github.io/2023/06/12/逆向分析/QQ聊天记录/qqhistory4/)

## TODO

说明：因为此项目功能数量多，功能分散，测试样本具有局限性，开发时间跨度大，难以保证每行代码都没问题，各位遇到问题积极提出Issue，有能力的可以直接提pr

- [ ] web导出
- [x] 音频消息导出
- [x] 视频消息导出
- [ ] PDF生成程序的错误处理
- [x] 程序UI
- [ ] 使用说明
- [ ] 支持卡片消息
- [x] 完善错误管理
- [ ] 添加多几种emoji表情供选择
- [ ] 增加PDF绘制图片自定义尺寸，非统一管理缩放
- [x] 明确设置群组好友格式，防止QQ群号和用户号重复
- [ ] 红包解析



## 局限性

### 消息解析

- [ ] 一个消息的总ERRCODE只支持一个，可能遇到不足的问题

- [ ] 灰条消息（撤回，获得群荣誉，修改群名等等等）直接从protobuf提取出来的字符串，可能存在“icon”等字符（可以通过解析extStr中的html解决，但挺费力）

- [ ] 灰条消息（撤回，获得群荣誉，修改群名等等等）直接从protobuf提取出来的字符串，相关人员的名称使用的可能是当时的昵称，无法自由配置（可以通过解析extStr中的html解决，但挺费力）

- [ ] json格式的卡片消息类型较多（参考：[QQ发送卡片消息 - 言成言成啊 - 博客园 (cnblogs.com)](https://www.cnblogs.com/meethigher/p/13581506.html)），难以提取出关键信息

- [ ] 无法解析合并转发消息的第二层序列化，入群消息（xx座男一枚，xxxx这种）

- [ ] 视频解析因为会清理，若视频被清理了就找不到视频了，然而QQ的shortvideo/thumb下的缩略图因分析不出命名规则，无法使用这缩略图

- [ ] 转发的聊天记录的序列化方式是java序列化+其它，无法分析，解析

- [ ] 解析时抛弃了一些属性，若有需要可修改，提交pr

  

### PDF生成

- [ ] 灰条消息没有写换行
- [ ] 没有错误处理
- [ ] 排版引擎在计算字体宽度时大约有3%的误差，略不美观，望大佬指点

## 作者

白羽夜星制作组 制作

<table>
    <tr>
        <td align="center">
            <a href="https://github.com/sunface">
                <img src="https://avatars.githubusercontent.com/u/108645779?s=200&v=4" width="160px"   alt=""/>
                <br />
                <sub><b>白羽夜星制作组</b></sub>
            </a>
        </td>
        <td align="center">
            <a href="https://github.com/SendToSouthEast">
                <img src="https://avatars.githubusercontent.com/u/93421418?v=4?s=100"  width="160px" alt=""/>
                <br />
                <sub><b>寄东南</b></sub>
            </a>
        </td>
        <td align="center">
            <a href="https://github.com/ahzvenol">
                <img src="https://avatars.githubusercontent.com/u/68780890?v=4?s=100" width="160px" alt=""/>
                <br />
                <sub><b>灵弦</b></sub>
            </a>
        </td>
    </tr>
</table>



## license

***由于本项目的特殊性质，本项目禁止一切形式的商业用途。***

***由于本项目的特殊性质，本项目禁止一切形式的商业用途。***

***由于本项目的特殊性质，本项目禁止一切形式的商业用途。***

## 感谢

本项目的本消息解密，数据库读取，QQ表情（emoticon1），来自：

https://github.com/Yiyiyimu/QQ_History_Backup

https://github.com/roadwide/qqmessageoutput

https://gist.github.com/WincerChan/362331456a6e0417c5aa1cf3ff7be2b7

消息反序列化分析用到了：

https://github.com/protocolbuffers/protobuf

https://github.com/nccgroup/blackboxprotobuf（测试阶段使用，不在项目代码中）

https://github.com/rohankumardubey/SerializationDumper（测试阶段使用，不在项目代码中）

音频转码用到了：

https://github.com/kn007/silk-v3-decoder

https://github.com/FFmpeg/FFmpeg （LGPL bulid）

视频缩略图用到了：

https://github.com/FFmpeg/FFmpeg （LGPL bulid）
