from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
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
import sys

# pyuic5 src/GUI/maininterface.ui -o src/GUI/maininterface.py
# import src.GUI.res_rc


class WorkerThread(QThread):
    messageReady = pyqtSignal(str)

    def __init__(self, task_id, task_data=None):
        super().__init__()
        self.task_id = task_id
        self.task_data = task_data

    def run(self):
        if self.task_id == "open_file":
            self.open_file(self.task_data)
        elif self.task_id == "copy_generatepdf_config":
            self.copy_generatepdf_config()
        elif self.task_id == "download_avatar":
            self.download_avatar()
        elif self.task_id == "generate_pdf":
            self.generate_pdf()
        elif self.task_id == "open_git_url":
            self.open_git_url()
        elif self.task_id == "start_parse":
            self.start_parse(self.task_data)


    def log(self, info):
        self.messageReady.emit(info)

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
        download.avatarDownload(self.log)

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

    def start_parse(self, configs):


        err_code = errcode.ErrCode("func", self.log)
        self.ERRCODE = err_code

        validate_settings = validateSettings.ValidateSettings()
        state, info, v_configs = validate_settings.validate(False, configs)
        self.log(info)


        if state:
            qq_parse = parsing.QQParse(v_configs, err_code)
            qq_parse.procDb()




class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.ERRCODE = None

        self.setupUi(self)

        self.kcInputModeGroup = [self.kcInputBox]
        self.kcSelectModeGroup = [self.kcPathSelectButton, self.kcPathInputBox]
        self.slowtableDbGroup = [self.qqSlowtableDbPathSelectButton, self.qqSlowtableDbPathInputBox]

        self.chatimgGroup = [self.chatimgPathInputBox, self.chatimgPathSelectButton]
        self.pttGroup = [self.pttPathInputBox, self.pttPathSelectButton]
        self.videoGroup = [self.videoPathSelectButton, self.videoPathInputBox]


        # 绑定触发事件
        self.dataDirPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.dataDirPathInputBox))

        self.qqDbPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择QQ号.db文件路径",
                                         self.qqDbPathInputBox,
                                         "DataBases File", "db"))

        self.qqSlowtableDbPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择QQ号_slowtable.db文件路径",
                                          self.qqSlowtableDbPathInputBox,
                                          "DataBases File", "db"))

        self.kcPathSelectButton.clicked.connect(
            lambda: self.select_file_path("请选择kc文件路径",
                                          self.kcPathInputBox,
                                          None, None))

        self.pttPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.pttPathInputBox))

        self.videoPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.videoPathInputBox))

        self.chatimgPathSelectButton.clicked.connect(
            lambda: self.select_dir_path("请选择com.tencent.mobileqq文件夹路径",
                                         self.chatimgPathInputBox))



        self.findFilesModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.findFilesModeContainer1))

        self.findFilesModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, None, self.findFilesModeContainer2))

        self.kcInputModeRadioButton1.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcInputModeGroup, None))

        self.kcInputModeRadioButton2.toggled.connect(
            lambda state: self.checkbox_changed(state, self.kcSelectModeGroup, None))

        self.useSlowtableCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.slowtableDbGroup, None))


        self.useImageCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.chatimgGroup, None))

        self.usePttCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.pttGroup, None))

        self.useVideoCheckBox.toggled.connect(
            lambda state: self.checkbox_changed(state, self.videoGroup, None))

        # self.chatimgPathSelectButton.toggled.connect(
        #     lambda state: self.checkbox_changed(state, self.chatimgGroup, None,
        #                                         "needImages", True))



        self.starButton.clicked.connect(
            lambda: self.start_task("open_git_url"))

        self.startParseButton.clicked.connect(
            self.start_parse)

        self.openSendersJsonButton.clicked.connect(
            lambda: self.start_task("worker_thread.open_file", "output/senders/senders.json"))
        self.copyPDFconfigButton.clicked.connect(
            lambda: self.start_task("copy_generatepdf_config"))
        self.downLoadAvatarButton.clicked.connect(
            lambda: self.start_task("download_avatar"))
        self.startGeneratePDF.clicked.connect(
            lambda: self.start_task("worker_thread.generate_pdf"))

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
            path, filter = QFileDialog.getOpenFileName(
                None, caption, "./",
                f"All Files (*)")
        else:
            path, filter = QFileDialog.getOpenFileName(
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
        path = QFileDialog.getExistingDirectory(caption=caption)
        print(path)
        if path:
            textbox_obj.setText(path)

    def start_task(self, task_id, task_data=None):
        """创建并启动子线程执行耗时任务

        """
        self.worker_thread = WorkerThread(task_id, task_data)
        self.worker_thread.messageReady.connect(self.log)
        # self.worker_thread.finished.connect(self.on_task_completed)
        self.worker_thread.start()


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
            self.findFilesModeRadioButton1.setChecked(configs['findFilesMode'] == 'dir')

            if configs['findFilesMode'] == 'dir':
                self.useSlowtableCheckBox2.setChecked(configs['needSlowtable'])
                self.dataDirPathInputBox.setText(configs['dataDirPath'])
            else:
                self.useSlowtableCheckBox.setChecked(configs['needSlowtable'])
                self.qqDbPathInputBox.setText(configs['dbPath'])
                self.qqSlowtableDbPathInputBox.setText(configs['dbstPath'])
                self.kcInputModeRadioButton2.setChecked(configs['needKey'])
                self.kcInputBox.setText(configs['key'])
                self.kcPathInputBox.setText(configs['keyPath'])

            self.friendModeRadioButton.setChecked(configs['mode'] == 'friend')
            self.groupModeRadioButton.setChecked(configs['mode'] == 'group')
            self.targetQQInputBox.setText(configs['targetQQ'])
            self.selfQQInputBox.setText(configs['selfQQ'])
            self.useImageCheckBox.setChecked(configs['needQQEmoji'])
            self.qqEmojiVerRadioButton1.setChecked(configs['QQEmojiVer'] == 'old')
            self.qqEmojiVerRadioButton2.setChecked(configs['QQEmojiVer'] == 'new')
            self.useImageCheckBox.setChecked(configs['needImages'])
            self.chatimgPathInputBox.setText(configs['imagesPath'])
            self.usePttCheckBox.setChecked(configs['needVoice'])
            self.pttPathInputBox.setText(configs['voicePath'])
            self.useVideoCheckBox.setChecked(configs['needVideo'])
            self.videoPathInputBox.setText(configs['videoPath'])
            self.checkBox.setChecked(configs['needMarketFace'])
            self.checkBox_4.setChecked(configs['needJavaDeser'])
        except Exception as e:
            self.log(f"加载设置时发生{e}错误，加载失败")
            return

    def read_setting_values(self):
        # Read the values from the controls and store them in the configs dictionary

        # Control values from parseConfigContainer
        configs = {}
        configs['findFilesMode'] = 'dir' if self.findFilesModeRadioButton1.isChecked() else 'files'
        if configs['findFilesMode'] == 'dir':
            configs['needSlowtable'] = self.useSlowtableCheckBox2.isChecked()
            configs['dataDirPath'] = self.dataDirPathInputBox.text()

        else:
            configs['needSlowtable'] = self.useSlowtableCheckBox.isChecked()
            configs['dbPath'] = self.qqDbPathInputBox.text()
            configs['dbstPath'] = self.qqSlowtableDbPathInputBox.text()
            configs['needKey'] = self.kcInputModeRadioButton2.isChecked()
            configs['key'] = self.kcInputBox.text()
            configs['keyPath'] = self.kcPathInputBox.text()

        configs['mode'] = 'friend' if self.friendModeRadioButton.isChecked() else 'group'
        configs['targetQQ'] = self.targetQQInputBox.text()
        configs['selfQQ'] = self.selfQQInputBox.text()
        configs['needQQEmoji'] = self.useImageCheckBox.isChecked()
        configs['QQEmojiVer'] = 'old' if self.qqEmojiVerRadioButton1.isChecked() else 'new'
        configs['needImages'] = self.useImageCheckBox.isChecked()
        configs['imagesPath'] = self.chatimgPathInputBox.text()
        configs['needVoice'] = self.usePttCheckBox.isChecked()
        configs['voicePath'] = self.pttPathInputBox.text()
        configs['needVideo'] = self.useVideoCheckBox.isChecked()
        configs['videoPath'] = self.videoPathInputBox.text()
        configs['needMarketFace'] = self.checkBox.isChecked()
        configs['needJavaDeser'] = self.checkBox_4.isChecked()

        with open("config/parse_config.json", 'w', encoding='utf-8') as json_file:
            commentjson.dump(configs, json_file, indent=4, ensure_ascii=False)

        return configs

    def log(self, info):
        self.logBox.append(info)

    def start_parse(self):
        if self.startParseButton.text() == "停止解析":
            if self.ERRCODE:
                self.ERRCODE.parse_stop("用户停止解析")

        elif self.startParseButton.text() == "开始解析":
            self.startParseButton.setText("停止解析")
            self.parseConfigContainer.setEnabled(False)
            self.statusbar.showMessage("正在解析...")
            configs = self.read_setting_values()
            print("UI output", configs)

            self.start_task("start_parse", configs)

            self.startParseButton.setText("开始解析")
            self.parseConfigContainer.setEnabled(True)
            self.statusbar.showMessage("解析停止")


def gui_init():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
