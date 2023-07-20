from PyQt5 import QtWidgets
from mainInterface import Ui_MainWindow

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


        # 绑定触发事件
        self.ui.dataDirPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.ui.dataDirPathInputBox,
                                         "dataDirPath"))

        self.ui.qqDbPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择QQ号.db文件路径",
                                         self.ui.qqDbPathInputBox,
                                         "qqDbPath", "DataBases File", "db"))

        self.ui.qqSlowtableDbPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择QQ号_slowtable.db文件路径",
                                          self.ui.qqSlowtableDbPathInputBox,
                                          "qqSlowtableDbPath", "DataBases File", "db"))


        self.ui.findFilesModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.ui.findFilesModeContainer1,
                                                "findFilesMode", "dir", None))

        self.ui.findFilesModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.ui.findFilesModeContainer2,
                                                "findFilesMode", "files", None))

        self.ui.kcInputModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcInputModeGroup, None,
                                                "kcInputMode", "input", None))

        self.ui.kcInputModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcSelectModeGroup, None,
                                                "kcInputMode", "select", None))

        self.ui.qqSlowtableDbPathSelectButton.toggled.connect(
            lambda state: self.checkbox_changed(state, self.slowtableDbGroup, None,
                                                "needSlowtable", True, False))


        self.ui.useImageCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.chatimgGroup, None,
                                                "needImages", True, False))

        self.ui.usePttCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.pttGroup, None,
                                                "needVoice", True, False))

        # self.ui.chatimgPathSelectButton.toggled.connect(
        #     lambda state: self.checkbox_changed(state, self.chatimgGroup, None,
        #                                         "needImages", True))

        self.ui.starButton.clicked.connect(self.open_git_url)

        self.configs = {}


    def checkbox_changed(self, state, selected_enabled_group, selected_enabled_obj, config_key, config_value, unconfig_value):
        """
        checkbox状态改变的处理函数，功能有更改设置项，更改控件enable
        :param state: 按键状态
        :param selected_enabled_group: 当选中后enable(或取消选中后disable)的控件列表，可为空
        :param selected_enabled_obj: 当选中后enable(或取消选中后disable)的单个控件，可为空
        :param config_key: 设置项的键
        :param config_value: 设置项的值
        :param unconfig_value: 取消设置的值
        :return:
        """
        if state == True:  # 选中状态
            if selected_enabled_obj:
                selected_enabled_obj.setEnabled(True)
            if selected_enabled_group:
                for i in selected_enabled_group:
                    i.setEnabled(True)

            self.configs[config_key] = config_value

        else:
            if selected_enabled_obj:
                selected_enabled_obj.setEnabled(False)
            if selected_enabled_group:
                for i in selected_enabled_group:
                    i.setEnabled(False)
            self.configs[config_key] = unconfig_value


    def select_file_path(self, caption, textbox_obj, config_key, file_type_name, file_type):
        """
        打开文件浏览框
        :param caption: 文件浏览框窗口名
        :param textbox_obj: 路径编辑框对象
        :param config_key: 设置选项
        :param file_type_name: 文件选择的文件类型，例如：Databases
        :param file_type: 文件选择的文件后缀名，例如：db(不需要.)

        """
        path, filter = QtWidgets.QFileDialog.getOpenFileName(
            None, caption, "./",
            f"{file_type_name} Files (*.{file_type});;All Files (*)")
        if path:
            textbox_obj.setText(path)
            self.configs[config_key] = path


    def select_dir_path(self, caption, textbox_obj, config_key):
        """
        打开文件夹浏览框
        :param caption: 文件夹浏览框窗口名
        :param textbox_obj: 路径编辑框对象
        :param config_key: 设置选项
        :return:
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(caption=caption)
        print(path)
        if path:
            textbox_obj.setText(path)
            self.configs[config_key] = path


    def open_git_url(self):
        """
        打开git仓库链接

        """
        url = "https://github.com/WhiteWingNightStar/QQHistoryExport"
        webbrowser.open(url)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    main_window = mainWindow(window)
    window.show()
    app.exec_()
