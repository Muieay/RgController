import tkinter as tk
from tkinter import messagebox
import psutil
import subprocess
import UnloadTopKey
import pystray
import sys
import os
from PIL import Image, ImageTk
import threading

def resource_path(relative_path):
    """ 获取资源绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# -------------------- 常量定义 --------------------
EXE_PATH = r"C:\Program Files (x86)\RG-CloudManagerRemote\CMLauncher.exe"
EXE_NAME = "CMLauncher.exe"
WINDOW_TITLE = "小灰灰控制器"
WINDOW_GEOMETRY = "350x150"
ICON_PATH = resource_path("htl.ico")
QR_CODE_PATH = resource_path("qrcode.bmp")
STATUS_COLOR = {
    "success": "green",
    "error": "red",
    "default": "black"
}
ABOUT_TEXT = """功能说明：
✅ ‌窗口置顶解除‌破解强控制类软件的霸屏行为，恢复窗口正常层级
✅ ‌顽固进程终止‌，强制结束任务管理器无法关闭的进程

本项目仅供学习参考，请勿用于非法用途。

开源地址:
https://github.com/muieay/RgController
扫码关注微信公众号：
"""


# -------------------- 系统托盘类 --------------------
class TrayIcon:
    def __init__(self, root_window):
        self.root = root_window
        self.tray_icon = None
        self.menu_items = (
            pystray.MenuItem("显示窗口", self.show_window),
            pystray.MenuItem("隐藏窗口", self.hide_window),
            pystray.MenuItem("取消置顶", lambda: unset_window_topmost(self.root)),
            pystray.MenuItem("解除控制", lambda: terminate_process_tree(EXE_NAME)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("配置", self.show_config_window),  # 新增配置菜单项
            pystray.MenuItem("关于", self.show_about_window),
            pystray.MenuItem("退出", self.exit_app)
        )
        
        # 加载托盘图标
        try:
            image = Image.open(ICON_PATH)
        except FileNotFoundError:
            image = Image.new('RGB', (16, 16), (255, 255, 255))
        
        self.tray_icon = pystray.Icon(
            "cloud_controller",
            image,
            WINDOW_TITLE,
            self.menu_items
        )

    def run_in_thread(self):
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.root.after(0, self.root.deiconify)
        set_window_topmost(self.root)

    def hide_window(self):
        self.root.withdraw()

    def exit_app(self):
        self.tray_icon.stop()
        self.root.destroy()

    def show_config_window(self):
        """触发显示配置窗口（主线程安全）"""
        self.root.after(0, self._create_config_dialog)

    def _create_config_dialog(self):
        """创建配置对话框"""
        config_win = tk.Toplevel(self.root)
        config_win.title("路径配置")
        config_win.grab_set()  # 设为模态窗口

        # 路径配置
        tk.Label(config_win, text="EXE路径:").grid(row=0, column=0, padx=5, pady=5)
        path_entry = tk.Entry(config_win, width=40)
        path_entry.insert(0, EXE_PATH)
        path_entry.grid(row=0, column=1, padx=5, pady=5)

        # 名称配置
        tk.Label(config_win, text="进程名称:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = tk.Entry(config_win, width=40)
        name_entry.insert(0, EXE_NAME)
        name_entry.grid(row=1, column=1, padx=5, pady=5)

        def save_config():
            """保存配置到全局变量"""
            global EXE_PATH, EXE_NAME
            EXE_PATH = path_entry.get()
            EXE_NAME = name_entry.get()
            config_win.destroy()
            messagebox.showinfo("保存成功", "配置已更新！\n新路径: {}\n新名称: {}".format(EXE_PATH, EXE_NAME))

        # 操作按钮
        btn_frame = tk.Frame(config_win)
        btn_frame.grid(row=2, columnspan=2, pady=10)
        tk.Button(btn_frame, text="保存", command=save_config, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=config_win.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def show_about_window(self):
        """显示关于窗口（主线程安全）"""
        self.root.after(0, self._create_about_dialog)
    def _create_about_dialog(self):
        """创建美观的关于对话框"""
        about_win = tk.Toplevel(self.root)
        about_win.title("关于")
        about_win.geometry("400x500")
        about_win.resizable(False, False)
        about_win.configure(bg="#f0f0f0")
        about_win.grab_set()

        # 主容器
        main_frame = tk.Frame(about_win, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(
            main_frame,
            text=WINDOW_TITLE,
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))

        # 版本信息
        version_label = tk.Label(
            main_frame,
            text="版本: 1.0.0",
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        version_label.pack()

        # 分隔线
        tk.Frame(
            main_frame,
            bg="#bdc3c7",
            height=1
        ).pack(fill=tk.X, pady=15)

        # 项目信息
        info_text = ABOUT_TEXT
        info_label = tk.Label(
            main_frame,
            text=info_text,
            justify=tk.LEFT,
            bg="#f0f0f0",
            fg="#34495e"
        )
        info_label.pack()

        # 二维码区域
        qr_frame = tk.Frame(main_frame, bg="#f0f0f0")
        qr_frame.pack(pady=20)

        try:
            qr_image = Image.open(QR_CODE_PATH)
            qr_photo = ImageTk.PhotoImage(qr_image.resize((150, 150)))
            
            qr_label = tk.Label(
                qr_frame,
                image=qr_photo,
                bg="#ffffff",
                relief=tk.GROOVE,
                bd=2
            )
            qr_label.image = qr_photo  # 保持引用
            qr_label.pack()
            
            # 二维码提示文字
            tk.Label(
                qr_frame,
                text="扫描二维码访问项目",
                bg="#f0f0f0",
                fg="#95a5a6"
            ).pack(pady=(10, 0))
        except Exception as e:
            error_label = tk.Label(
                qr_frame,
                text=f"无法加载二维码\n({str(e)})",
                fg="#e74c3c",
                bg="#f0f0f0"
            )
            error_label.pack()

        # 关闭按钮
        close_btn = tk.Button(
            main_frame,
            text="关 闭",
            command=about_win.destroy,
            width=15,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT
        )
        close_btn.pack(pady=(20, 0))

# -------------------- 业务逻辑函数 --------------------
def set_window_topmost(root_window: tk.Tk) -> None:
    """设置窗口置顶（增加窗口激活）"""
    root_window.deiconify()
    root_window.attributes('-topmost', True)
    update_status("状态：窗口已置顶", STATUS_COLOR["success"])

def unset_window_topmost(root_window: tk.Tk) -> None:
    """取消窗口置顶（增加窗口激活）"""
    root_window.attributes('-topmost', False)
    try:
        UnloadTopKey.main()
        update_status("状态：已取消全部置顶", STATUS_COLOR["success"])
    except Exception as e:
        messagebox.showerror("错误", f"取消置顶失败: {str(e)}")
    root_window.deiconify()
# 已经弃用
# def terminate_process_tree(process_name: str) -> None:
#     """
#     强制终止指定名称的进程及其子进程
    
#     Args:
#         process_name: 需要终止的进程名称
        
#     Returns:
#         None (通过状态标签显示操作结果)
#     """
#     found = False
#     for proc in psutil.process_iter(['name', 'pid']):
#         try:
#             if proc.info['name'] == process_name:
#                 parent = psutil.Process(proc.info['pid'])
#                 # 终止子进程
#                 for child in parent.children(recursive=True):
#                     child.kill()
#                 # 终止父进程
#                 parent.kill()
#                 found = True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
#             print(f"进程操作异常: {str(e)}")
#             continue
    
#     if found:
#         update_status("状态：云控解除", STATUS_COLOR["success"])
#     else:
#         update_status("状态：未找到进程", STATUS_COLOR["error"])
        
 
# 改进版进程终止函数（支持父子服务依赖关系）
def terminate_process_tree(process_name: str) -> None:
    """
    改进版进程终止函数（支持父子服务依赖关系）
    终止顺序：孙进程 → 子进程 → 父进程
    """
    found = False
    
    def recursive_kill(process):
        """递归终止子进程"""
        try:
            # 获取直接子进程（非递归获取）
            children = process.children()
            for child in children:
                recursive_kill(child)  # 先处理子进程的子进程
                try:
                    child.kill()
                    child.wait(timeout=3)  # 等待进程终止
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
        except psutil.NoSuchProcess:
            return

    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if proc.info['name'] == process_name:
                parent = psutil.Process(proc.info['pid'])
                
                # 先递归终止所有子进程
                recursive_kill(parent)
                
                # 最后终止父进程
                try:
                    parent.kill()
                    parent.wait(timeout=3)  # 等待父进程终止
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"进程操作异常: {str(e)}")
            continue

    if found:
        update_status("状态：云控解除", STATUS_COLOR["success"])
    else:
        update_status("状态：未找到进程", STATUS_COLOR["error"])

def launch_application(exe_path: str) -> None:
    """
    启动指定路径的应用程序
    
    Args:
        exe_path: 可执行文件完整路径
        
    Raises:
        subprocess.SubprocessError: 启动进程失败时抛出
    """
    try:
        subprocess.Popen(exe_path)
        update_status("状态：开启云控", STATUS_COLOR["success"])
    except (FileNotFoundError, PermissionError, subprocess.SubprocessError) as e:
        update_status("状态：启动失败", STATUS_COLOR["error"])
        messagebox.showerror("错误", f"程序启动失败: {str(e)}")

# -------------------- GUI 相关函数 --------------------
def update_status(text: str, color: str = STATUS_COLOR["default"]) -> None:
    """统一更新状态标签"""
    status_label.config(text=text, fg=color)

def create_gui(root_window: tk.Tk) -> None:
    """创建应用程序界面（增加窗口协议处理）"""
    # 窗口配置
    root_window.title(WINDOW_TITLE)
    root_window.geometry(WINDOW_GEOMETRY)
    
    # 设置窗口关闭时的行为
    root_window.protocol('WM_DELETE_WINDOW', lambda: Tray.hide_window())
    
    # 状态标签
    global status_label
    status_label = tk.Label(root_window, text="状态：就绪")
    status_label.pack(pady=10)
    
    # 按钮容器
    button_frame = tk.Frame(root_window)
    button_frame.pack(pady=10)
    
    # 功能按钮
    buttons = [
        ("开启置顶", lambda: set_window_topmost(root_window)),
        ("开启云控", lambda: launch_application(EXE_PATH)),
        ("解除控制", lambda: terminate_process_tree(EXE_NAME)),
        ("取消置顶", lambda: unset_window_topmost(root_window)),
    ]
    
    # 动态创建按钮
    for text, command in buttons:
        btn = tk.Button(
            button_frame,
            text=text,
            command=command,
            width=10
        )
        btn.pack(side=tk.LEFT, padx=5)

# -------------------- 主程序 --------------------
if __name__ == "__main__":
    root = tk.Tk()
    create_gui(root)
    
    # 初始化系统托盘
    global Tray
    Tray = TrayIcon(root)
    Tray.run_in_thread()
    
    root.mainloop()