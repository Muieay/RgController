import sys
import keyboard
from utils import resource_path
from PyQt5.QtCore import QUrl, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QCloseEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QLineEdit, QPushButton, QToolBar, QProgressBar,
                             QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class ModernBrowser(QMainWindow):
    toggle_topmost_signal = pyqtSignal()
    toggle_visibility_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("学习通浏览器")
        self.setGeometry(100, 100, 1280, 800)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon(resource_path("ODLS.png")))

        # 窗口状态相关属性
        self.is_topmost = False
        self.tray_icon = None
        self.is_hiding = False

        # 初始化定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_topmost_status)

        self.init_ui()
        self.init_style()
        self.init_connections()
        self.init_tray_icon()

        # 注册全局快捷键
        keyboard.add_hotkey('ctrl+alt+q', self.emit_toggle_signal)
        # keyboard.add_hotkey('ctrl+alt+w', self.emit_toggle_visibility)
    def init_tray_icon(self):
        """初始化系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("ODLS.png")))

        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = QAction("显示窗口", self)
        quit_action = QAction("退出程序", self)

        # 连接菜单动作
        show_action.triggered.connect(self.show_normal)
        quit_action.triggered.connect(self.quit_app)

        # 添加菜单项
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # 双击托盘图标恢复窗口
        self.tray_icon.activated.connect(self.tray_icon_activated)



    def init_ui(self):
        """初始化界面组件"""
        # 创建主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 导航工具栏
        self.nav_bar = QToolBar()
        self.nav_bar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.nav_bar)

        # 导航按钮
        self.back_btn = QPushButton()
        self.forward_btn = QPushButton()
        self.reload_btn = QPushButton()

        # 地址栏
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("输入网址或搜索内容...")

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        # 添加组件到工具栏
        self.nav_bar.addWidget(self.back_btn)
        self.nav_bar.addWidget(self.forward_btn)
        self.nav_bar.addWidget(self.reload_btn)
        self.nav_bar.addWidget(self.url_bar)

        # 浏览器视图
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://chat.baidu.com/search"))

        # 布局管理
        main_layout.addWidget(self.nav_bar)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.browser)

    def tray_icon_activated(self, reason):
        """处理托盘图标点击事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()

    def show_normal(self):
        """恢复窗口显示"""
        self.show()
        self.activateWindow()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

    def quit_app(self):
        """安全退出应用程序"""
        self.tray_icon.hide()
        keyboard.unhook_all_hotkeys()
        QApplication.quit()

    def emit_toggle_signal(self):
        self.toggle_topmost_signal.emit()

    def emit_toggle_visibility(self):
        self.toggle_visibility_signal.emit()

    def toggle_visibility(self):
        """切换窗口可见性"""
        if self.isVisible():
            self.hide()
        else:
            self.show_normal()

    def toggle_topmost(self):
        """优化后的置顶切换逻辑"""
        if self.is_topmost:
            # 如果当前是置顶状态：取消置顶并隐藏窗口
            self.is_topmost = False
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.timer.stop()
            self.hide()  # 新增隐藏窗口操作
        else:
            # 如果当前非置顶状态：显示窗口并置顶
            self.is_topmost = True
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            # 确保窗口可见（修复最小化时无法显示的问题）
            if self.isMinimized() or not self.isVisible():
                self.showNormal()
            self.activateWindow()
            self.timer.start(1000)
        self.show()  # 必须调用show使窗口标志生效

    def check_topmost_status(self):
        """优化状态检查"""
        if self.is_topmost and not self.isActiveWindow():
            # 如果应该置顶但失去焦点，重新激活窗口
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """优化关闭事件处理"""
        if not self.is_hiding:
            # 关闭时强制取消置顶状态
            self.is_topmost = False
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.timer.stop()
            self.hide()
            event.ignore()
        else:
            super().closeEvent(event)
    def init_style(self):
        """初始化样式设置"""
        # 字体设置
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)

        # 主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6f8;
            }
            QToolBar {
                background-color: #ffffff;
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QLineEdit {
                background: #f1f3f4;
                border: 1px solid #dfe1e5;
                border-radius: 20px;
                padding: 8px 20px;
                font-size: 14px;
                min-width: 400px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
                background: white;
            }
            QPushButton {
                background: transparent;
                border: none;
                padding: 6px;
                min-width: 32px;
                min-height: 32px;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: #f1f3f4;
            }
            QPushButton:pressed {
                background: #e8f0fe;
            }
            QProgressBar {
                background: transparent;
                border: none;
                height: 3px;
            }
            QProgressBar::chunk {
                background-color: #1a73e8;
            }
        """)

        # 按钮图标（使用本地资源路径）
        self.back_btn.setIcon(QIcon(resource_path("back.png")))
        self.forward_btn.setIcon(QIcon(resource_path("next.png")))
        self.reload_btn.setIcon(QIcon(resource_path("refresh.png")))

        # 设置图标大小
        for btn in [self.back_btn, self.forward_btn, self.reload_btn]:
            btn.setIconSize(btn.sizeHint())

        # 初始URL
        self.url_bar.setText("https://chat.baidu.com/search")

    def init_connections(self):
        """初始化信号连接"""
        self.toggle_topmost_signal.connect(self.toggle_topmost)
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        # 浏览器事件
        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadFinished.connect(self.on_load_finish)

        # 按钮事件
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)

        # 地址栏事件
        self.url_bar.returnPressed.connect(self.navigate_to_url)

    def navigate_to_url(self):
        """导航到指定URL"""
        url = self.url_bar.text().strip()
        if not url:
            return

        # 自动补全协议
        if not url.startswith(("http://", "https://")):
            if "." in url:  # 假定包含域名
                url = "https://" + url
            else:  # 作为搜索
                url = f"https://chat.baidu.com/search?word={url}"

        self.browser.setUrl(QUrl(url))

    def update_url(self, qurl):
        """更新地址栏显示"""
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

    def update_progress(self, progress):
        """更新加载进度"""
        self.progress_bar.setValue(progress)
        self.progress_bar.setVisible(progress < 100)

    def on_load_finish(self):
        """加载完成处理"""
        self.progress_bar.hide()
        # self.setWindowTitle(f"{self.browser.title()} - 学习通浏览器")
        self.setWindowTitle(f"学习通浏览器")

def main():
    app = QApplication(sys.argv)
    # 确保应用在所有窗口关闭后继续运行
    app.setQuitOnLastWindowClosed(False)
    browser = ModernBrowser()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
