from PyQt5 import QtWidgets
from mainInterface import Ui_MainWindow

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
                                                "findFilesMode", "dir"))

        self.ui.findFilesModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.ui.findFilesModeContainer2,
                                                "findFilesMode", "files"))

        self.ui.kcInputModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcInputModeGroup, None,
                                                "kcInputMode", "input"))

        self.ui.kcInputModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcSelectModeGroup, None,
                                                "kcInputMode", "select"))

        self.ui.qqSlowtableDbPathSelectButton.toggled.connect(
            lambda state: self.checkbox_changed(state, self.slowtableDbGroup, None,
                                                "needSlowtable", True))


        self.ui.useImageCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.chatimgGroup, None,
                                                "needImages", False))

        self.ui.usePttCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.pttGroup, None,
                                                "needVoice", False))

        # self.ui.chatimgPathSelectButton.toggled.connect(
        #     lambda state: self.checkbox_changed(state, self.chatimgGroup, None,
        #                                         "needImages", True))

        self.configs = {}


    def checkbox_changed(self, state, selected_enabled_group, selected_enabled_obj, config_key, config_value):
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


    def select_file_path(self, caption, textbox_obj, config_item, file_type_name, file_type):
        path, filter = QtWidgets.QFileDialog.getOpenFileName(
            None, caption, "./",
            f"{file_type_name} Files (*.{file_type});;All Files (*)")
        if path:
            textbox_obj.setText(path)
            self.configs[config_item] = path


    def select_dir_path(self, caption, textbox_obj, config_item):
        path = QtWidgets.QFileDialog.getExistingDirectory(caption=caption)
        print(path)
        if path:
            textbox_obj.setText(path)
            self.configs[config_item] = path


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    main_window = mainWindow(window)
    window.show()
    app.exec_()
