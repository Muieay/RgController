
import sys
import os
def resource_path(relative_path):
    """ 获取资源绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# -------------------- 常量定义 --------------------
EXE_PATH = r"C:\Program Files (x86)\RG-CloudManagerRemote\CMLauncher.exe"
EXE_NAME = ["CMLauncher.exe","student.exe"]
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