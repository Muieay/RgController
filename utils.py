
import sys
import os
def resource_path(relative_path):
    """ 获取资源绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# -------------------- 常量定义 --------------------
EXE_PATH = [
    r"C:\Program Files (x86)\RG-CloudManagerRemote\CMLauncher.exe",
    r"C:\Program Files (x86)\Mythware\极域课堂管理系统软件V6.0 2016 豪华版\StudentMain.exe",
    r"C:\Parasaga\cyberclass\student\Student.exe",
    r"C:\Program Files (x86)\Parasaga\cyberclass\student\Student.exe",
    r"C:\Program Files (x86)\3000soft\Red Spider\REDAgent.exe"
]
EXE_NAME = [
    "CMLauncher.exe", 
    "CMApp.exe",
    "CMService.exe",
    "CMUninstaller.exe",
    "CMUpgrader.exe",
    "REDAgent.exe",
    "repview.exe",
    "PerformanceCheck.exe",
    "FormatPaper.exe",
    "edpaper.exe",
    "Adapter.exe",
    "student.exe", 
    "GtSRun.exe", 
    "lxboard.exe", 
    "msboard.exe", 
    "MTCPerformance.exe", 
    "PsDeskContral.exe", 
    "PsFileLoad.exe", 
    "PsGhost.exe", 
    "PSSound.exe", 
    "PSSoundBig.exe", 
    "secprocess.exe", 
    "SECCService.exe", 
    "SendInfoClient.exe", 
    "SetFirewall.exe", 
    "Student.exe", 
    "QuickWord.exe",
    "TSTalk.exe", 
    "VideoClient.exe", 
    "whiteboard.exe", 
    "编号工具.exe", 
    "远程协助.exe",
    "GATESRV.exe",
    "InstHelpApp.exe",
    "InstHelpApp64.exe",
    "MasterHelper.exe",
    "ProcHelper64.exe",
    "Shutdown.exe",
    "SpecialSet.exe",
    "StudentMain.exe",
    "TDChalk.exe"
]
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
✅ ‌显示窗口快捷键 Ctrl+Alt+W
✅ ‌解除控制快捷键 Ctrl+Alt+E

本项目仅供学习参考，请勿用于非法用途。

开源地址:
https://github.com/muieay/RgController
扫码关注微信公众号：
"""