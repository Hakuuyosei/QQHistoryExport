from PyQt5 import QtWidgets
from src.GUI.mainInterface import Ui_MainWindow

from src.errcode import errcode
from src.dataParsing import parsing
from src.generate import GeneratePDF_ReportLab
from src.avatarDownload import download
from src.validateSettings import validateSettings

import webbrowser

# pyuic5 src/GUI/maininterface.ui -o src/GUI/maininterface.py
class mainWindow():
    def __init__(self, window):
        super().__init__()

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

        self.ui.qqSlowtableDbPathSelectButton.toggled.connect(
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


    def open_git_url(self):
        """
        打开git仓库链接

        """
        url = "https://github.com/WhiteWingNightStar/QQHistoryExport"
        webbrowser.open(url)

    def read_control_values(self):
        # Read the values from the controls and store them in the configs dictionary

        # Control values from parseConfigContainer
        configs = {}
        configs['findFilesMode'] = 'dir' if self.ui.findFilesModeRadioButton1.isChecked() else 'file'
        if configs['findFilesMode'] == 'dir':
            configs['needSlowtable'] = self.ui.useSlowtableCheckBox2.isChecked()
            configs['dataDirPath'] = self.ui.dataDirPathInputBox.text()

        else:
            configs['needSlowtable'] = self.ui.useSlowtableCheckBox.isChecked()
            configs['dbPath'] = self.ui.qqDbPathInputBox.text()
            configs['dbstPath'] = self.ui.qqSlowtableDbPathInputBox.text()
            configs['needKey'] = self.ui.usePttCheckBox.isChecked()
            configs['key'] = self.ui.kcInputBox.text()
            configs['keyPath'] = self.ui.kcPathInputBox.text()

        configs['mode'] = 'friend' if self.ui.friendModeRadioButton.isChecked() else 'group'
        configs['targetQQ'] = self.ui.targetQQInputBox.text()
        configs['selfQQ'] = self.ui.selfQQInputBox.text()
        configs['needQQEmoji'] = self.ui.useImageCheckBox.isChecked()
        configs['QQEmojiVer'] = 'new' if self.ui.qqEmojiVerRadioButton1.isChecked() else 'old'
        configs['needImages'] = self.ui.useImageCheckBox.isChecked()
        configs['imagesPath'] = self.ui.chatimgPathInputBox.text()
        configs['needVoice'] = self.ui.usePttCheckBox.isChecked()
        configs['voicePath'] = self.ui.pttPathInputBox.text()
        configs['needVideo'] = self.ui.useVideoCheckBox.isChecked()
        configs['videoPath'] = self.ui.videoPathInputBox.text()
        configs['needMarketFace'] = self.ui.checkBox.isChecked()
        configs['needJavaDeser'] = self.ui.checkBox_4.isChecked()

        return configs

    def log(self, info):
        self.ui.logBox.append(info)

    def start_parse(self):
        self.ui.startParseButton.setEnabled(False)
        self.ui.parseConfigContainer.setEnabled(False)
        configs = self.read_control_values()
        print(configs)

        err_code = errcode.ErrCode("func",self.log)

        validate_settings = validateSettings.ValidateSettings()
        state, info, v_configs = validate_settings.validate(False, configs)
        self.ui.logBox.append(info)


        if state:
            qq_parse = parsing.QQParse(v_configs, err_code)
            qq_parse.procDb()
            pass
        else:
            self.ui.startParseButton.setEnabled(True)
            self.ui.parseConfigContainer.setEnabled(True)




def gui_init():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    main_window = mainWindow(window)
    window.show()
    app.exec_()
