import copy
import sys
import os
import subprocess
import winreg
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, \
    QButtonGroup, QSpinBox, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from logger import logger
from core_by_config import dynv6_updater, Status, set_conf_file, Config, load_conf_file


class Dynv6UpdaterThread(QThread):
    signal_config_error = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        res = dynv6_updater()
        if res is None:
            logger.logger.info('Dynv6 Updater Quit Normally')
        elif res in ['Config Error', 'Config Initialized']:
            self.signal_config_error.emit()


class ConfigEditor(QWidget):
    restart_app = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.config = copy.deepcopy(Config)

    def initUI(self):
        # 创建布局
        main_layout = QVBoxLayout()

        # domain 文本框
        domain_layout = QHBoxLayout()
        domain_label = QLabel("Domain:")
        self.domain_input = QLineEdit()
        domain_layout.addWidget(domain_label)
        domain_layout.addWidget(self.domain_input)
        main_layout.addLayout(domain_layout)

        # token 文本框
        token_layout = QHBoxLayout()
        token_label = QLabel("Token:")
        self.token_input = QLineEdit()
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        main_layout.addLayout(token_layout)

        # 单选框
        radio_layout = QHBoxLayout()
        radio_label = QLabel("mode:")
        self.interval_radio = QRadioButton("interval")
        self.once_radio = QRadioButton("once")
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.interval_radio)
        self.radio_group.addButton(self.once_radio)
        self.interval_radio.setChecked(True)
        radio_layout.addWidget(radio_label)
        radio_layout.addWidget(self.interval_radio)
        radio_layout.addWidget(self.once_radio)
        main_layout.addLayout(radio_layout)

        # 数值设置
        value_layout = QHBoxLayout()
        value_label = QLabel("interval time(s):")
        self.value_spinbox = QSpinBox()
        self.value_spinbox.setMaximum(99999999)
        self.value_spinbox.setMinimum(5)
        self.value_spinbox.setValue(600)
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_spinbox)
        main_layout.addLayout(value_layout)

        # 保存按钮
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        main_layout.addWidget(save_button)

        # 设置布局
        self.setLayout(main_layout)

        # 设置窗口属性
        self.setWindowTitle('Dynv6 Updater Config Editor')
        self.setGeometry(300, 300, 500, 400)

        # 图标
        self.setWindowIcon(QIcon("logo.ico"))

    def init_values(self, config: Config):
        self.domain_input.setText(config['domain'])
        self.token_input.setText(config['token'])
        if config['mode'] == 'interval':
            self.interval_radio.setChecked(True)
        else:
            self.once_radio.setChecked(True)
        self.value_spinbox.setValue(config['seconds'])

    def set_values(self):
        self.config['domain'] = self.domain_input.text()
        self.config['token'] = self.token_input.text()
        self.config['mode'] = "interval" if self.interval_radio.isChecked() else "once"
        self.config['seconds'] = self.value_spinbox.value()

    def save_config(self):
        self.set_values()
        set_conf_file(self.config)
        self.restart_app.emit()
        self.close()

    def closeEvent(self, event):
        # 隐藏窗口而不退出程序
        self.hide()
        event.ignore()


class SystemTrayApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.core_thread = Dynv6UpdaterThread()
        self.core_thread.signal_config_error.connect(self.config_setting)
        self.destroyed.connect(self.close_thread)
        self.config_editor: ConfigEditor = None
        self.start_dynv6_updater()
        self.update_tip_timer()

    def update_tip_timer(self):
        self.tip_timer = QTimer()
        self.tip_timer.timeout.connect(self.update_tip)
        self.tip_timer.start(10 * 1000)

    def update_tip(self):
        if Status['running']:
            ipv4 = Status['ipv4']
            msg = 'Dynv6 Updater'
            if len(ipv4):
                msg += f'\nIPv4: {ipv4}'
            ipv6 = Status['ipv6']
            if len(ipv6):
                msg += f'\nIPv6: {ipv6}'
            self.tray_icon.setToolTip(msg)

    def start_dynv6_updater(self):
        self.core_thread.start()

    def close_thread(self):
        Status['running'] = False

    def config_setting(self):
        if self.config_editor is None:
            self.config_editor = ConfigEditor()
            current_conf = load_conf_file()
            self.config_editor.init_values(current_conf)
            self.config_editor.restart_app.connect(self.restart_app)
            self.config_editor.show()
        else:
            current_conf = load_conf_file()
            self.config_editor.init_values(current_conf)
            self.config_editor.show()

    def reset_config(self):
        set_conf_file()

    def initUI(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("logo.ico"))
        self.tray_icon.setToolTip("Dynv6 Updater")

        # 创建菜单
        menu = QMenu()

        # 查看状态菜单项
        self.view_status_action = QAction("查看状态/Status", self)
        self.view_status_action.triggered.connect(self.view_status)
        menu.addAction(self.view_status_action)

        # 配置
        self.setting_action = QAction("设置/Setting", self)
        self.setting_action.triggered.connect(self.config_setting)
        menu.addAction(self.setting_action)

        # 重新启动菜单项
        self.restart_action = QAction("重新启动/Restart", self)
        self.restart_action.triggered.connect(self.restart_app)
        menu.addAction(self.restart_action)

        # 开机自启菜单项
        self.autostart_action = QAction("开机自启/Auto Start", self, checkable=True)
        self.autostart_action.setChecked(self.is_autostart_enabled())
        self.autostart_action.triggered.connect(self.toggle_autostart)
        menu.addAction(self.autostart_action)

        self.stop_thread_action = QAction("暂停/Pause", self)
        self.stop_thread_action.triggered.connect(self.close_thread)
        menu.addAction(self.stop_thread_action)

        self.reset_config_action = QAction("重置配置/Reset Conf", self)
        self.reset_config_action.triggered.connect(self.reset_config)
        self.reset_config_action.triggered.connect(self.restart_app)
        menu.addAction(self.reset_config_action)

        self.exit_app_action = QAction("退出/Exit", self)
        self.exit_app_action.triggered.connect(lambda: sys.exit(1))
        menu.addAction(self.exit_app_action)

        # 将菜单添加到系统托盘图标
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def view_status(self):
        current_conf = load_conf_file()
        log_path = os.path.abspath(current_conf['log'])
        try:
            os.startfile(log_path)
        except FileNotFoundError:
            logger.logger.error(f"Log file in {current_conf['log']} not found!")

    def restart_app(self):
        try:
            # 获取当前 Python 可执行文件路径
            python = sys.executable
            # 构建命令列表
            command = [python] + sys.argv
            # 使用 subprocess.Popen 启动新进程
            subprocess.Popen(command)
            # 退出当前进程
            sys.exit()
        except Exception as e:
            print(f"重启时出现错误: {e}")

    def is_autostart_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_READ)
            if getattr(sys, 'frozen', False):
                # 如果是打包后的可执行文件
                exe_path = sys.executable
            else:
                # 如果是开发环境运行
                exe_path = os.path.abspath(sys.argv[0])
            _, _ = winreg.QueryValueEx(key, os.path.basename(exe_path))
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, OSError):
            return False

    def toggle_autostart(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                             winreg.KEY_ALL_ACCESS)
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            exe_path = sys.executable
        else:
            # 如果是开发环境运行
            exe_path = os.path.abspath(sys.argv[0])
        if self.autostart_action.isChecked():
            # 添加到开机自启
            winreg.SetValueEx(key, os.path.basename(exe_path), 0, winreg.REG_SZ, exe_path)
        else:
            # 从开机自启中移除
            try:
                winreg.DeleteValue(key, os.path.basename(exe_path))
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)


def exception_hook(exc_type, exc_value, exc_traceback):
    logger.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == '__main__':
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    tray_app = SystemTrayApp()
    sys.exit(app.exec_())
