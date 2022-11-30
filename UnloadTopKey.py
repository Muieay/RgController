import win32gui
import win32con

# 获取所有窗口置顶状态
def get_top_windows():
    top_windows = []
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if style & win32con.WS_EX_TOPMOST:
                top_windows.append(hwnd)
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return top_windows

# 取消窗口置顶
def unset_topmost(hwnd):
    title = win32gui.GetWindowText(hwnd)
    if "粘滞键" not in title:
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def main():
    top_windows = get_top_windows()
    
    if not top_windows:
        print("没有置顶的窗口。")
        return
    
    print("以下窗口当前是置顶的：")
    for hwnd in top_windows:
        title = win32gui.GetWindowText(hwnd)
        print(f"窗口句柄: {hwnd}, 标题: {title}")
    
    for hwnd in top_windows:
        unset_topmost(hwnd)
        title = win32gui.GetWindowText(hwnd)
        print(f"已取消窗口 '{title}' 的置顶状态。")
