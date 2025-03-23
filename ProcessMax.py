import psutil
import ctypes
import sys
from tkinter import messagebox

# 忽略kill 操作的程序
ignore_names = list(set({
    "System Idle Process", "System", "Registry", "svchost.exe", "csrss.exe", "smss.exe", "wininit.exe",
    "services.exe", "winlogon.exe", "Code.exe", "LsaIso.exe", "lsass.exe", "ChsIME.exe", "fontdrvhost.exe",
    "WUDFHost.exe", "dwm.exe", "powershell.exe", "SDXHelper.exe", "conhost.exe", "SearchProtocolHost.exe",
    "UserOOBEBroker.exe", "amdfendrsr.exe", "atiesrxx.exe", "atieclxx.exe", "RuntimeBroker.exe",
    "MemCompression", "NhNotifSys.exe", "ShellHost.exe", "audiodg.exe", "sihost.exe", "python.exe",
    "qaxdefender.exe", "RtkAudUService64.exe", "taskhostw.exe", "explorer.exe", "osdservice.exe", "spoolsv.exe",
    "MpDefenderCoreService.exe", "wlanext.exe", "HxTsr.exe", "NgcIso.exe", "SystemSettings.exe",
    "Intel_PIE_Service.exe", "FMService64.exe", "OfficeClickToRun.exe", "PixPin.exe", "LCD_Service.exe",
    "TabTip.exe", "SecurityHealthService.exe", "PCManagerMainService.exe", "NahimicService.exe", "mysqld.exe",
    "redis-server.exe", "SessionService.exe", "vmnat.exe", "wallpaperservice32.exe", "vmnetdhcp.exe",
    "MsMpEng.exe", "wallpaper32.exe", "ApplicationFrameHost.exe", "AggregatorHost.exe", "SearchHost.exe",
    "unsecapp.exe", "WmiPrvSE.exe", "HNOfficeCenter.exe", "Lingma.exe", "MBAProcessWatcher.exe", "smartscreen.exe",
    "MBAMessageCenter.exe", "MBAPersistentCenter.exe", "MBAAntiVirus.exe", "HnPerformanceCenter.exe",
    "ctfmon.exe", "Widgets.exe", "StartMenuExperienceHost.exe",  "TextInputHost.exe", "cmd.exe", "NisSrv.exe",
    "WidgetService.exe", "dllhost.exe", "PCManagerTray.exe", "ShellExperienceHost.exe", "HnVirtualPeripheral.exe",
    "pet.exe", "crashpad_handler.exe", "SearchIndexer.exe", "BrainDecision.exe", "AwarenessDecision.exe",
    "SecurityHealthSystray.exe", "trantorAgent.exe","msedge.exe","小灰灰控制器.exe","RgController.exe","chrome.exe","powershell.exe"
}))

def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_system_process(proc):
    """判断是否为系统关键进程"""
    try:
        # 系统特征判断条件
        system_users = {
            'NT AUTHORITY\\SYSTEM',
            'NT AUTHORITY\\LOCAL SERVICE',
            'NT AUTHORITY\\NETWORK SERVICE'
        }
        system_dirs = (
            r'C:\Windows\System32',
            r'C:\Windows\SysWOW64',
            r'C:\Windows\WinSxS'
        )
        
        # 获取进程信息
        username = proc.username()
        exe_path = proc.exe().lower() if proc.exe() else ""
        ppid = proc.ppid()
        
        # 判断条件
        if any([
            username in system_users,
            exe_path.startswith(system_dirs),
            ppid == 4,  # System process
            proc.pid == 4,  # System Idle Process
            proc.pid == 0,  # System process
            'windows' in exe_path,
            '\\system32\\' in exe_path,
            '\\syswow64\\' in exe_path
        ]):
            return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return True  # 无法访问的进程视为系统进程

def safe_terminate(process):
    """安全终止进程树"""
    try:
        children = process.children(recursive=True)
        for child in children:
            if not is_system_process(child):
                child.kill()
                print(f"终止子进程: {child.name()} (PID: {child.pid})")
        process.kill()
        print(f"终止进程: {process.name()} (PID: {process.pid})")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

def terminate_max_processes():
    """主终止逻辑"""
    if not is_admin():
        print("建议以管理员权限运行！")
        # return

    system_process_count = 0
    terminated_count = 0

    for proc in psutil.process_iter():
        try:
            if is_system_process(proc):
                system_process_count += 1
            else:
                if proc.name() not in ignore_names:
                    safe_terminate(proc)
                    terminated_count += 1
        except Exception as e:
            print(f"处理进程时发生错误: {str(e)}")
            continue

    print(f"\n操作完成！\n系统进程保留: {system_process_count}\n终止第三方进程: {terminated_count}")
    
def show_max_processes():
    """主终止逻辑（带确认弹窗）"""
    # 显示确认对话框
    confirm = messagebox.askyesno(
        title="操作确认",
        message="建议手动配置进程无果后再使用该功能！\n确定要执行强制终止操作吗？\n该操作不可逆！",
        icon=messagebox.WARNING
    )
    
    if not confirm:
        return  # 用户取消操作
    terminate_max_processes()
def max_processes():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        show_max_processes()
