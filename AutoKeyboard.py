import ctypes
from ctypes import wintypes

# 加载 user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 定义常量
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# 定义钩子回调函数类型
HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)
)

# 全局变量存储钩子句柄
hook_id = None

def low_level_keyboard_handler(nCode, wParam, lParam):
    """
    低级键盘钩子回调函数
    """
    if wParam == WM_KEYDOWN or wParam == WM_KEYUP:
        # 拦截所有键盘事件
        return 1  # 返回非零值表示拦截事件
    return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

def lock_keyboard():
    """锁定键盘输入"""
    global hook_id
    # 设置低级键盘钩子
    hook_id = user32.SetWindowsHookExA(
        WH_KEYBOARD_LL,
        HOOKPROC(low_level_keyboard_handler),
        ctypes.windll.kernel32.GetModuleHandleW(None),
        0
    )
    if not hook_id:
        raise ctypes.WinError(ctypes.get_last_error())
    print("键盘已锁定，无法输入任何内容。")

def unlock_keyboard():
    """解锁键盘输入"""
    global hook_id
    if hook_id:
        user32.UnhookWindowsHookEx(hook_id)
        hook_id = None
    print("键盘已解锁，恢复正常输入。")

# 示例使用
if __name__ == "__main__":
    lock_keyboard()  # 锁定键盘
    input("按 Enter 解锁键盘...")  # 阻塞等待用户输入
    unlock_keyboard()  # 解锁键盘