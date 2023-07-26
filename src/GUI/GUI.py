from PyQt5 import QtWidgets
from src.GUI.mainInterface import Ui_MainWindow

from src.errcode import errcode
from src.dataParsing import parsing
from src.generate import GeneratePDF_ReportLab
from src.avatarDownload import download
from src.validateSettings import validateSettings

import webbrowser
import os
import shutil
import commentjson

# pyuic5 src/GUI/maininterface.ui -o src/GUI/maininterface.py
# import src.GUI.res_rc
class mainWindow():
    def __init__(self, window):
        super().__init__()

        self.ERRCODE = None

        ui = Ui_MainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(window)

        self.kcInputModeGroup = [self.ui.kcInputBox]
        self.kcSelectModeGroup = [self.ui.kcPathSelectButton, self.ui.kcPathInputBox]
        self.slowtableDbGroup = [self.ui.qqSlowtableDbPathSelectButton, self.ui.qqSlowtableDbPathInputBox]

        self.chatimgGroup = [self.ui.chatimgPathInputBox, self.ui.chatimgPathSelectButton]
        self.pttGroup = [self.ui.pttPathInputBox, self.ui.pttPathSelectButton]
        self.videoGroup = [self.ui.videoPathSelectButton, self.ui.videoPathInputBox]


        # 绑定触发事件
        self.ui.dataDirPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.ui.dataDirPathInputBox))

        self.ui.qqDbPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择QQ号.db文件路径",
                                         self.ui.qqDbPathInputBox,
                                         "DataBases File", "db"))

        self.ui.qqSlowtableDbPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择QQ号_slowtable.db文件路径",
                                          self.ui.qqSlowtableDbPathInputBox,
                                          "DataBases File", "db"))

        self.ui.kcPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择kc文件路径",
                                          self.ui.kcPathInputBox,
                                          None, None))

        self.ui.pttPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.ui.pttPathInputBox))

        self.ui.videoPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.ui.videoPathInputBox))

        self.ui.chatimgPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.ui.chatimgPathInputBox))



        self.ui.findFilesModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.ui.findFilesModeContainer1))

        self.ui.findFilesModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.ui.findFilesModeContainer2))

        self.ui.kcInputModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcInputModeGroup, None))

        self.ui.kcInputModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcSelectModeGroup, None))

        self.ui.useSlowtableCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.slowtableDbGroup, None))


        self.ui.useImageCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.chatimgGroup, None))

        self.ui.usePttCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.pttGroup, None))

        self.ui.useVideoCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.videoGroup, None))

        # self.ui.chatimgPathSelectButton.toggled.connect(
        #     lambda state: self.checkbox_changed(state, self.chatimgGroup, None,
        #                                         "needImages", True))

        self.ui.starButton.clicked.connect(self.open_git_url)

        self.ui.startParseButton.clicked.connect(self.start_parse)

        self.ui.openSendersJsonButton.clicked.connect(
            lambda: self.open_file("output/senders/senders.json"))
        self.ui.copyPDFconfigButton.clicked.connect(self.copy_generatepdf_config)
        self.ui.downLoadAvatarButton.clicked.connect(self.download_avatar)
        self.ui.startGeneratePDF.clicked.connect(self.generate_pdf)

        self.load_setting_values()



    def checkbox_changed(self, state, selected_enabled_group, selected_enabled_obj):
        """
        checkbox状态改变的处理函数，功能有更改设置项，更改控件enable
        :param state: 按键状态
        :param selected_enabled_group: 当选中后enable(或取消选中后disable)的控件列表，可为空
        :param selected_enabled_obj: 当选中后enable(或取消选中后disable)的单个控件，可为空
        :return:
        """
        if state == True:  # 选中状态
            if selected_enabled_obj:
                selected_enabled_obj.setEnabled(True)
            if selected_enabled_group:
                for i in selected_enabled_group:
                    i.setEnabled(True)


        else:
            if selected_enabled_obj:
                selected_enabled_obj.setEnabled(False)
            if selected_enabled_group:
                for i in selected_enabled_group:
                    i.setEnabled(False)


    def select_file_path(self, caption, textbox_obj, file_type_name, file_type):
        """
        打开文件浏览框
        :param caption: 文件浏览框窗口名
        :param textbox_obj: 路径编辑框对象
        :param file_type_name: 文件选择的文件类型，例如：Databases
        :param file_type: 文件选择的文件后缀名，例如：db(不需要.)

        """
        if not file_type_name:
            path, filter = QtWidgets.QFileDialog.getOpenFileName(
                None, caption, "./",
                f"All Files (*)")
        else:
            path, filter = QtWidgets.QFileDialog.getOpenFileName(
                None, caption, "./",
                f"{file_type_name} Files (*.{file_type});;All Files (*)")
        if path:
            textbox_obj.setText(path)


    def select_dir_path(self, caption, textbox_obj):
        """
        打开文件夹浏览框
        :param caption: 文件夹浏览框窗口名
        :param textbox_obj: 路径编辑框对象
        :return:
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(caption=caption)
        print(path)
        if path:
            textbox_obj.setText(path)

    def open_file(self, path):
        """
        用系统软件打开文件
        :param path:
        :return:
        """
        if os.path.exists(path):
            try:
                if os.name == 'nt':  # Windows
                    abs_path = os.path.abspath(path)
                    os.startfile(abs_path)
                else:
                    self.log(f"你用的什么系统啊，自己去打开{path}吧\n")
            except Exception as e:
                self.log(f"打开{path}失败！{e} \n")

        else:
            self.log(f"{path}不存在！\n")

    def copy_generatepdf_config(self):
        source_file = "config/GeneratePDF_ReportLab_config_example.ini"
        destination_file = "config/GeneratePDF_ReportLab_config.ini"
        try:
            shutil.copy(source_file, destination_file)
            self.log(f"设置项复制成功\n")
            self.open_file(destination_file)
        except FileNotFoundError:
            self.log(f"文件'{source_file}'未找到！\n")
        except Exception as e:
            self.log(f"文件复制失败{e}，请手动复制和打开\n")


    def download_avatar(self):
        self.log(f"头像开始下载……\n")
        try:
            download.avatarDownload()
        except Exception as e:
            self.log(f"头像下载失败{e}，请手动下载\n")
        self.log(f"头像下载完成\n")

    def generate_pdf(self):
        self.log(f"开始生成PDF……")
        try:
            generateInit = GeneratePDF_ReportLab.GenerateInit()
            generateInit.run()
        except Exception as e:
            self.log(f"生成PDF发生错误{e}\n")
            return

        self.log(f"PDF生成成功")


    def open_git_url(self):
        """
        打开git仓库链接

        """
        url = "https://github.com/WhiteWingNightStar/QQHistoryExport"
        webbrowser.open(url)

    def load_setting_values(self):
        """
        从config/parse_config.json中加载设置

        """
        if not os.path.exists("config/parse_config.json"):
            self.log(f"未发现设置文件，未加载设置")
            return

        try:
            with open("config/parse_config.json", 'r', encoding="utf-8") as file:
                try:
                    # 读取带注释的json
                    configs = commentjson.load(file)
                except:
                    self.log(f"加载设置时发生解析错误，加载失败")
                    return
        except:
            self.log(f"加载设置时发生IO错误，加载失败")
            return

        try:
            self.ui.findFilesModeRadioButton1.setChecked(configs['findFilesMode'] == 'dir')

            if configs['findFilesMode'] == 'dir':
                self.ui.useSlowtableCheckBox2.setChecked(configs['needSlowtable'])
                self.ui.dataDirPathInputBox.setText(configs['dataDirPath'])
            else:
                self.ui.useSlowtableCheckBox.setChecked(configs['needSlowtable'])
                self.ui.qqDbPathInputBox.setText(configs['dbPath'])
                self.ui.qqSlowtableDbPathInputBox.setText(configs['dbstPath'])
                self.ui.kcInputModeRadioButton2.setChecked(configs['needKey'])
                self.ui.kcInputBox.setText(configs['key'])
                self.ui.kcPathInputBox.setText(configs['keyPath'])

            self.ui.friendModeRadioButton.setChecked(configs['mode'] == 'friend')
            self.ui.groupModeRadioButton.setChecked(configs['mode'] == 'group')
            self.ui.targetQQInputBox.setText(configs['targetQQ'])
            self.ui.selfQQInputBox.setText(configs['selfQQ'])
            self.ui.useImageCheckBox.setChecked(configs['needQQEmoji'])
            self.ui.qqEmojiVerRadioButton1.setChecked(configs['QQEmojiVer'] == 'old')
            self.ui.qqEmojiVerRadioButton2.setChecked(configs['QQEmojiVer'] == 'new')
            self.ui.useImageCheckBox.setChecked(configs['needImages'])
            self.ui.chatimgPathInputBox.setText(configs['imagesPath'])
            self.ui.usePttCheckBox.setChecked(configs['needVoice'])
            self.ui.pttPathInputBox.setText(configs['voicePath'])
            self.ui.useVideoCheckBox.setChecked(configs['needVideo'])
            self.ui.videoPathInputBox.setText(configs['videoPath'])
            self.ui.checkBox.setChecked(configs['needMarketFace'])
            self.ui.checkBox_4.setChecked(configs['needJavaDeser'])
        except Exception as e:
            self.log(f"加载设置时发生{e}错误，加载失败")
            return

    def read_setting_values(self):
        # Read the values from the controls and store them in the configs dictionary

        # Control values from parseConfigContainer
        configs = {}
        configs['findFilesMode'] = 'dir' if self.ui.findFilesModeRadioButton1.isChecked() else 'files'
        if configs['findFilesMode'] == 'dir':
            configs['needSlowtable'] = self.ui.useSlowtableCheckBox2.isChecked()
            configs['dataDirPath'] = self.ui.dataDirPathInputBox.text()

        else:
            configs['needSlowtable'] = self.ui.useSlowtableCheckBox.isChecked()
            configs['dbPath'] = self.ui.qqDbPathInputBox.text()
            configs['dbstPath'] = self.ui.qqSlowtableDbPathInputBox.text()
            configs['needKey'] = self.ui.kcInputModeRadioButton2.isChecked()
            configs['key'] = self.ui.kcInputBox.text()
            configs['keyPath'] = self.ui.kcPathInputBox.text()

        configs['mode'] = 'friend' if self.ui.friendModeRadioButton.isChecked() else 'group'
        configs['targetQQ'] = self.ui.targetQQInputBox.text()
        configs['selfQQ'] = self.ui.selfQQInputBox.text()
        configs['needQQEmoji'] = self.ui.useImageCheckBox.isChecked()
        configs['QQEmojiVer'] = 'old' if self.ui.qqEmojiVerRadioButton1.isChecked() else 'new'
        configs['needImages'] = self.ui.useImageCheckBox.isChecked()
        configs['imagesPath'] = self.ui.chatimgPathInputBox.text()
        configs['needVoice'] = self.ui.usePttCheckBox.isChecked()
        configs['voicePath'] = self.ui.pttPathInputBox.text()
        configs['needVideo'] = self.ui.useVideoCheckBox.isChecked()
        configs['videoPath'] = self.ui.videoPathInputBox.text()
        configs['needMarketFace'] = self.ui.checkBox.isChecked()
        configs['needJavaDeser'] = self.ui.checkBox_4.isChecked()

        with open("config/parse_config.json", 'w', encoding='utf-8') as json_file:
            commentjson.dump(configs, json_file, indent=4, ensure_ascii=False)

        return configs

    def log(self, info):
        self.ui.logBox.append(info)

    def start_parse(self):
        if self.ui.startParseButton.text() == "停止解析":
            if self.ERRCODE:
                self.ERRCODE.parse_stop("用户停止解析")

        elif self.ui.startParseButton.text() == "开始解析":
            self.ui.startParseButton.setText("停止解析")
            self.ui.parseConfigContainer.setEnabled(False)
            self.ui.statusbar.showMessage("正在解析...")
            configs = self.read_setting_values()
            print("UI output", configs)

            err_code = errcode.ErrCode("func", self.log)
            self.ERRCODE = err_code

            validate_settings = validateSettings.ValidateSettings()
            state, info, v_configs = validate_settings.validate(False, configs)
            self.ui.logBox.append(info)


            if state:
                qq_parse = parsing.QQParse(v_configs, err_code)
                qq_parse.procDb()

            self.ui.startParseButton.setText("开始解析")
            self.ui.parseConfigContainer.setEnabled(True)
            self.ui.statusbar.showMessage("解析停止")


def gui_init():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    main_window = mainWindow(window)
    window.show()
    app.exec_()
