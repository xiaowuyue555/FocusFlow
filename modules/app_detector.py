import platform

def get_active_app_info():
    os_name = platform.system()
    if os_name == "Darwin":
        return _get_active_app_mac()
    elif os_name == "Windows":
        return _get_active_app_windows()
    return "Unknown", "N/A"

def _get_active_app_mac():
    import Quartz
    try:
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements, 
            Quartz.kCGNullWindowID
        )
        for win in window_list:
            owner = win.get("kCGWindowOwnerName", "")
            title = win.get("kCGWindowName", "")
            layer = win.get("kCGWindowLayer", 0)
            alpha = win.get("kCGWindowAlpha", 1)
            
            system_noise = ["WindowManager", "Dock", "Window Server", "ControlCenter", "NotificationCenter", "loginwindow"]
            
            if owner and layer == 0 and alpha > 0:
                if owner in system_noise: continue
                app_name = owner
                file_path = f"[{app_name}]"
                if title:
                    if ("After Effects" in owner) or ("Premiere" in owner):
                        if ".aep" in title.lower() or ".prproj" in title.lower():
                            file_path = title.split(" - ", 1)[-1].replace("*", "").strip() if " - " in title else title.replace("*", "").strip()
                    elif "Photoshop" in owner:
                        if ".psd" in title.lower() or ".psb" in title.lower():
                            file_path = title.split(" @ ")[0].replace("*", "").strip() if " @ " in title else title.replace("*", "").strip()
                    else:
                        file_path = title.strip()
                return app_name, file_path
        return "Unknown", "N/A"
    except:
        return "Unknown", "N/A"

def _get_active_app_windows():
    try:
        import win32gui
        import win32process
        import psutil
        
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd: return "Unknown", "N/A"
        
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        app_name = psutil.Process(pid).name().replace(".exe", "")
        
        system_noise = ["SearchHost", "ShellExperienceHost", "explorer"]
        if app_name in system_noise: return "Unknown", "N/A"
        
        file_path = f"[{app_name}]"
        if title:
            if "After Effects" in app_name or "Premiere" in app_name:
                if ".aep" in title.lower() or ".prproj" in title.lower():
                    file_path = title.split(" - ", 1)[-1].replace("*", "").strip() if " - " in title else title.replace("*", "").strip()
            elif "Photoshop" in app_name:
                if ".psd" in title.lower() or ".psb" in title.lower():
                    file_path = title.split(" @ ")[0].replace("*", "").strip() if " @ " in title else title.replace("*", "").strip()
            else:
                file_path = title.strip()
        return app_name, file_path
    except:
        return "Unknown", "N/A"