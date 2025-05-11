from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QFileDialog, QLineEdit, QLabel, 
                           QTextEdit, QMenuBar, QMenu, QAction, QHBoxLayout,
                           QMessageBox)
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QIcon
import sys
import yaml
from pathlib import Path
from enum import Enum
import os
from way1 import organize_photos_by_date

class Language(Enum):
    EN = "English"
    ZH_TW = "繁體中文"
    ZH_CN = "简体中文"

class PhotoOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_config()
        
        # 根據系統語言設置默認語言
        system_locale = QLocale.system().name()
        if system_locale.startswith('zh'):
            self.current_language = Language.ZH_TW
        elif system_locale.startswith('zh'):
            self.current_language = Language.ZH_CN
        else:
            self.current_language = Language.EN
        
        self.initUI()
        self.update_ui_text()
        self.log("status_ready")

    def load_config(self):
        """載入配置文件"""
        config_path = Path(__file__).parent / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.translations = {
            Language.EN: self.config['translations']['en'],
            Language.ZH_TW: self.config['translations']['zh_tw'],
            Language.ZH_CN: self.config['translations']['zh_cn']
        }
        
        self.version = self.config['version']

    def initUI(self):
        # 創建中心小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 創建菜單欄
        self.create_menu_bar()
        
        # 掃描路徑行
        folder_layout = QHBoxLayout()
        folder_label = QLabel(self)
        folder_label.setMinimumWidth(80)
        self.folder_path_label = folder_label
        self.folder_path_input = QLineEdit(self)
        self.folder_path_input.setReadOnly(True)
        self.folder_path_input.setPlaceholderText(self.translations[self.current_language]['select_folder_placeholder'])
        self.folder_button = QPushButton(self)
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: #90EE90;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
                color: black;
            }
            QPushButton:hover {
                background-color: #98FB98;
            }
        """)
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_input)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # 錯誤提示標籤
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # 開始處理按鈕
        self.start_button = QPushButton(self)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                color: black;
            }
            QPushButton:hover {
                background-color: #87CEFA;
            }
        """)
        self.start_button.clicked.connect(self.start_processing)
        layout.addWidget(self.start_button)

        # 添加狀態日誌顯示區域
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.update_log_style()
        layout.addWidget(self.log_text)
        
        # 添加底部信息欄
        bottom_info = QHBoxLayout()
        
        # 版權信息（中間對齊）
        copyright_label = QLabel(self)
        copyright_label.setStyleSheet("color: gray;")
        copyright_label.setAlignment(Qt.AlignCenter)
        bottom_info.addWidget(copyright_label)
        self.copyright_label = copyright_label
        
        # 版本信息（右對齊）
        version_label = QLabel(self)
        version_label.setStyleSheet("color: gray;")
        version_label.setAlignment(Qt.AlignRight)
        bottom_info.addWidget(version_label)
        self.version_label = version_label
        
        layout.addLayout(bottom_info)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle(self.translations[self.current_language]['window_title'])

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # 幫助菜單
        help_menu = menubar.addMenu('')
        self.help_menu = help_menu
        
        # 關於
        about_action = QAction('', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        self.about_action = about_action
        
        # 使用說明
        help_action = QAction('', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        self.help_action = help_action
        
        # 語言菜單
        language_menu = menubar.addMenu('')
        self.language_menu = language_menu
        
        # 添加語言選項
        for lang in Language:
            action = QAction(lang.value, self)
            action.setData(lang)
            action.triggered.connect(self.change_language)
            language_menu.addAction(action)

    def update_ui_text(self):
        """更新界面文字"""
        texts = self.translations[self.current_language]
        
        self.setWindowTitle(texts['window_title'])
        self.folder_path_label.setText(texts['select_folder'])
        self.start_button.setText(texts['start_processing'])
        self.folder_path_input.setPlaceholderText(texts['select_folder_placeholder'])
        
        # 更新菜單文字
        self.help_menu.setTitle(texts['menu_help'])
        self.about_action.setText(texts['menu_about'])
        self.help_action.setText(texts['menu_usage'])
        self.language_menu.setTitle(texts['language'])
        
        # 更新底部信息
        self.copyright_label.setText(texts['copyright'])
        self.version_label.setText(texts['version_text'].format(self.version))
        
        self.folder_button.setText(texts['browse_button'])

    def log(self, message_key, *args):
        """添加日誌消息到日誌區域"""
        message = self.translations[self.current_language][message_key].format(*args)
        self.log_text.append(message)

    def change_language(self):
        """切換語言"""
        action = self.sender()
        if action:
            self.current_language = action.data()
            self.update_ui_text()

    def show_about(self):
        """顯示關於對話框"""
        about_text = f"""
        {self.translations[self.current_language]['window_title']}
        {self.translations[self.current_language]['version_text'].format(self.version)}
        
        {self.translations[self.current_language]['copyright']}
        """
        QMessageBox.about(self, self.translations[self.current_language]['menu_about'], about_text)

    def show_help(self):
        """顯示使用說明對話框"""
        help_text = "\n".join(self.config['usage_steps'][self.current_language.name.lower()])
        QMessageBox.information(self, self.translations[self.current_language]['menu_usage'], help_text)

    def select_folder(self):
        """選擇要整理的資料夾"""
        folder_path = QFileDialog.getExistingDirectory(self, self.translations[self.current_language]['select_folder'])
        if folder_path:
            self.folder_path_input.setText(folder_path)
            self.error_label.setVisible(False)

    def start_processing(self):
        """開始處理照片整理"""
        folder_path = self.folder_path_input.text()
        if not folder_path:
            self.error_label.setText(self.translations[self.current_language]['error_no_input_folder'])
            self.error_label.setVisible(True)
            return

        self.error_label.setVisible(False)
        self.log("status_processing")
        
        try:
            organize_photos_by_date(folder_path)
            self.log("status_complete")
        except Exception as e:
            self.log("status_error", str(e))

    def update_log_style(self):
        """根據系統主題更新日誌區域樣式"""
        palette = self.palette()
        is_dark = palette.color(palette.Window).lightness() < 128
        
        if is_dark:
            # 深色主題
            self.log_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 5px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)
        else:
            # 淺色主題
            self.log_text.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)

    def changeEvent(self, event):
        """處理系統主題變更事件"""
        if event.type() == event.PaletteChange:
            self.update_log_style()
        super().changeEvent(event)

def main():
    app = QApplication(sys.argv)
    ex = PhotoOrganizerApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 