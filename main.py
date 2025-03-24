import tkinter as tk
from tkinter import messagebox
import psutil
from utils import *
import subprocess
import UnloadTopKey
import pystray
from PIL import Image, ImageTk
import threading
import time
from ProcessMax import max_processes


# -------------------- 系统托盘类 --------------------
class TrayIcon:
    def __init__(self, root_window):
        self.root = root_window
        self.tray_icon = None
        self.menu_items = (
            pystray.MenuItem("显示窗口", lambda: set_window_topmost(self.root)),
            # pystray.MenuItem("隐藏窗口", self.hide_window),
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
        path_entry.insert(0, ';'.join(EXE_PATH))
        path_entry.grid(row=0, column=1, padx=5, pady=5)

        # 名称配置
        tk.Label(config_win, text="进程名称:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = tk.Entry(config_win, width=40)
        name_entry.insert(0, "; ".join(EXE_NAME))
        name_entry.grid(row=1, column=1, padx=5, pady=5)

        def save_config():
            """保存配置到全局变量"""
            global EXE_PATH, EXE_NAME
            EXE_PATH = [p.strip() for p in path_entry.get().split(';') if p.strip()]
            # 从输入框获取字符串并转换为列表
            names_str = name_entry.get()
            EXE_NAME = [name.strip() for name in names_str.split(";") if name.strip()]
            config_win.destroy()
            messagebox.showinfo("保存成功", 
                "配置已更新！\n新路径: {}\n新名称: {}".format(EXE_PATH, "; ".join(EXE_NAME)))

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
    """设置窗口置顶，并启动定时检查确保始终置顶"""
    def check_topmost():
        """定时检查窗口是否置顶"""
        while getattr(root_window, '_keep_topmost', False):  # 检查标志位
            if not root_window.attributes('-topmost'):
                root_window.attributes('-topmost', True)  # 重新置顶
            time.sleep(1)  # 每秒检查一次

    # 设置标志位，表示需要保持置顶
    root_window._keep_topmost = True

    # 首次置顶
    root_window.deiconify()
    root_window.attributes('-topmost', True)
    update_status("状态：窗口已置顶", STATUS_COLOR["success"])

    # 启动后台线程定时检查
    threading.Thread(target=check_topmost, daemon=True).start()

def unset_window_topmost(root_window: tk.Tk) -> None:
    """取消窗口置顶，并停止定时检查"""
    # 清除标志位，停止定时检查
    if hasattr(root_window, '_keep_topmost'):
        root_window._keep_topmost = False

    # 取消置顶
    root_window.attributes('-topmost', False)
    try:
        UnloadTopKey.main()  # 取消置顶
        update_status("状态：已取消全部置顶", STATUS_COLOR["success"])
    except Exception as e:
        messagebox.showerror("错误", f"取消置顶失败: {str(e)}")
    root_window.deiconify()
        

# 改进版进程终止函数（支持父子服务依赖关系）
def terminate_process_tree(process_names: list[str]) -> None:
    """
    改进版进程终止函数（支持父子服务依赖关系）
    终止顺序：孙进程 → 子进程 → 父进程
    :param process_names: 需要终止的进程名称列表
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
            if proc.info['name'] in process_names:
                target_process = psutil.Process(proc.info['pid'])  # 重命名变量更准确
                
                # 先递归终止所有子进程
                recursive_kill(target_process)
                
                # 最后终止目标进程
                try:
                    target_process.kill()
                    target_process.wait(timeout=3)  # 等待进程终止
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

def launch_application(exe_paths: list[str]) -> None:
    """
    启动指定路径的应用程序
    
    Args:
        exe_path: 可执行文件完整路径
        
    Raises:
        subprocess.SubprocessError: 启动进程失败时抛出
    """
    success = False
    for path in exe_paths:
        try:
            subprocess.Popen(path)
            success = True
        except (FileNotFoundError, PermissionError, subprocess.SubprocessError) as e:
            print(f"启动失败: {str(e)}")
    if success:
        update_status("状态：云控已启动", STATUS_COLOR["success"])
    else:
        update_status(f"启动失败: {os.path.basename(path)}", STATUS_COLOR["error"])
        messagebox.showerror("错误", f"未找到指定程序，请手动配置！")

def processes_max() -> None:
    max_processes()
    update_status("状态：强解！", STATUS_COLOR["success"])

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
    
    # 第一行按钮容器
    button_frame_row1 = tk.Frame(root_window)
    button_frame_row1.pack()
    
    # 原功能按钮
    buttons_row1 = [
        ("开启置顶", lambda: set_window_topmost(root_window)),
        ("开启云控", lambda: launch_application(EXE_PATH)),
        ("解除控制", lambda: terminate_process_tree(EXE_NAME)),
        ("取消置顶", lambda: unset_window_topmost(root_window))
    ]
    
    # 创建第一行按钮
    for text, command in buttons_row1:
        btn = tk.Button(
            button_frame_row1,
            text=text,
            command=command,
            width=10
        )
        btn.pack(side=tk.LEFT, padx=2, pady=2)  # 减小间距

    # 第二行按钮容器（新增）
    button_frame_row2 = tk.Frame(root_window)
    button_frame_row2.pack(pady=10)  # 添加垂直间距
    
    # 新增功能按钮
    buttons_row2 = [
        ("强解 |《解控无效再使用》| 高危", lambda: processes_max()),
        # ("清理缓存", lambda: print("执行缓存清理"))
    ]
    
    # 创建第二行按钮（居中显示）
    for text, command in buttons_row2:
        btn = tk.Button(
            button_frame_row2,
            text=text,
            command=command,
            width=30  # 加宽按钮
        )
        btn.pack(side=tk.LEFT, padx=20, ipady=3)  # 增加水平间距和垂直内边距

    # 底部留白
    tk.Frame(root_window, height=10).pack()
        

# -------------------- 主程序 --------------------
if __name__ == "__main__":
    root = tk.Tk()
    create_gui(root)
    
    # 初始化系统托盘
    global Tray
    Tray = TrayIcon(root)
    Tray.run_in_thread()
    
    root.mainloop()