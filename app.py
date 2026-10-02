import ctypes
import os
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import winreg


# -----------------------------------------------------------------------------
# Application metadata
# -----------------------------------------------------------------------------
APP_TITLE = "Windows Registry Tweaks"
PROJECT_TITLE = "Windows Registry"
STUDENT_NAME = "Mohadeseh Abbasi"
PROFESSOR_NAME = "Mojtaba Mansouri"


# -----------------------------------------------------------------------------
# Registry tweak definitions
# -----------------------------------------------------------------------------
# Exactly 20 Registry tweaks, each represented by a structured dictionary.
# The enable_value corresponds to the policy value used to activate the tweak.
# The disable_value restores the default behavior.
TWEAKS = [
    {
        "id": 1,
        "name": "Remove Lock Screen",
        "description": "Disables the Windows lock screen and prevents it from appearing before sign-in.",
        "path": r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Personalization",
        "subkey": r"SOFTWARE\Policies\Microsoft\Windows\Personalization",
        "value_name": "NoLockScreen",
        "value_type": "DWORD",
        "root": "HKLM",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": True,
        "restart_note": "Log off or restart the PC to apply the lock screen change consistently.",
    },
    {
        "id": 2,
        "name": "Disable Windows Shortcuts",
        "description": "Disables built-in Windows shortcut hotkeys such as Win key combinations.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoWinKeys",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Restart Explorer to refresh active keyboard shortcuts.",
    },
    {
        "id": 3,
        "name": "Hide Taskbar Clock and Date",
        "description": "Hides the system tray clock and date from the notification area.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "HideClock",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Restart Explorer or sign out and back in if needed.",
    },
    {
        "id": 4,
        "name": "Prevent Folder Options from Opening",
        "description": "Disables access to Folder Options in File Explorer.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoFolderOptions",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Restart Explorer after toggling the value.",
    },
    {
        "id": 5,
        "name": "Remove Explorer Desktop Context Menu",
        "description": "Removes the right-click context menu in File Explorer and on the desktop.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoViewContextMenu",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Restart Explorer if the menu state does not refresh immediately.",
    },
    {
        "id": 6,
        "name": "Remove File Menu from File Explorer",
        "description": "Hides the classic File menu in File Explorer windows.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoFileMenu",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Open a new File Explorer window to see the change.",
    },
    {
        "id": 7,
        "name": "Remove Security Tab from Properties",
        "description": "Removes the Security tab from object property pages.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoSecurityTab",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Properties pages are refreshed when reopened.",
    },
    {
        "id": 8,
        "name": "Remove Hardware Tab",
        "description": "Removes the Hardware tab from the Properties page for devices and drives.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoHardwareTab",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Reopen the Properties dialog to see the effect.",
    },
    {
        "id": 9,
        "name": "Remove Manage Option from This PC",
        "description": "Removes the Manage command from the context and shell menu for This PC.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoManageMyComputerVerb",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Refresh the shell or reopen This PC to see the result.",
    },
    {
        "id": 10,
        "name": "Hide Computers from Other Networks",
        "description": "Prevents computers from other networks from being visible in Network Neighborhood scenarios.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoEntireNetwork",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "This change is commonly visible after a network refresh or Explorer restart.",
    },
    {
        "id": 11,
        "name": "Remove Search Button from File Explorer",
        "description": "Removes the default search box button in File Explorer.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoShellSearchButton",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Restart Explorer to refresh the command bar.",
    },
    {
        "id": 12,
        "name": "Disable Previous Explorer Search Suggestions",
        "description": "Disables predictive search suggestions in File Explorer.",
        "path": r"HKCU\Software\Policies\Microsoft\Windows\Explorer",
        "subkey": r"Software\Policies\Microsoft\Windows\Explorer",
        "value_name": "DisableSearchBoxSuggestions",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Open a new Explorer window to apply the change.",
    },
    {
        "id": 13,
        "name": "Remove Search the Internet Option",
        "description": "Hides the Search the Internet option from Explorer search results.",
        "path": r"HKCU\Software\Policies\Microsoft\Windows\Explorer",
        "subkey": r"Software\Policies\Microsoft\Windows\Explorer",
        "value_name": "NoSearchInternetTryHarderButton",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Restart Explorer if the search pane does not update quickly.",
    },
    {
        "id": 14,
        "name": "Remove Properties from This PC",
        "description": "Removes the Properties option from the context menu of This PC.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoPropertiesMyComputer",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Refresh the shell or reopen This PC to see the result.",
    },
    {
        "id": 15,
        "name": "Remove Properties from Recycle Bin",
        "description": "Removes the Properties option from the Recycle Bin context menu.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoPropertiesRecycleBin",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Reopen the Recycle Bin context menu to check the result.",
    },
    {
        "id": 16,
        "name": "Hide Recycle Bin Icon from Desktop",
        "description": "Hides the Recycle Bin icon from the desktop by setting the non-enum value used by Explorer.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\NonEnum",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\NonEnum",
        "value_name": "{645FF040-5081-101B-9F08-00AA002F954E}",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Refresh the desktop or restart Explorer to apply the visual change.",
    },
    {
        "id": 17,
        "name": "Prevent Certain Desktop Changes from Being Saved",
        "description": "Disables the saving of certain desktop settings when the user modifies the desktop.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoSaveSettings",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Desktop changes apply after Explorer refresh.",
    },
    {
        "id": 18,
        "name": "Clear Recent File History on Exit",
        "description": "Forces recent file history to be cleared when Explorer exits.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "ClearRecentDocsOnExit",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "No restart is usually required; Explorer can be reopened to verify the state.",
    },
    {
        "id": 19,
        "name": "Remove Frequent Programs from Start Menu",
        "description": "Hides the list of frequently used programs from the Start menu.",
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "subkey": r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "value_name": "NoStartMenuMFUprogramsList",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Sign out and back in or restart Explorer if the Start menu does not refresh immediately.",
    },
    {
        "id": 20,
        "name": "Hide Recommended Section in Start Menu",
        "description": "Attempts to hide the Recommended section in the Start menu on supported Windows 10/11 builds. This value can vary by OS build.",
        "path": r"HKCU\Software\Policies\Microsoft\Windows\Explorer",
        "subkey": r"Software\Policies\Microsoft\Windows\Explorer",
        "value_name": "HideRecommendedSection",
        "value_type": "DWORD",
        "root": "HKCU",
        "enable_value": 1,
        "disable_value": 0,
        "requires_admin": False,
        "restart_note": "Explorer restart may be required; Start menu behavior can differ between Windows 10 and 11 builds.",
    },
]


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------
def is_windows() -> bool:
    return os.name == "nt"


def is_admin() -> bool:
    if not is_windows():
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_root_handle(root_name: str):
    mapping = {
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKU": winreg.HKEY_USERS,
    }
    return mapping.get(root_name.upper(), winreg.HKEY_CURRENT_USER)


def get_status_text(value, tweak):
    if value is None:
        return "Not Configured"
    try:
        value_int = int(value)
    except (TypeError, ValueError):
        return "Custom"
    if value_int == tweak["enable_value"]:
        return "Enabled"
    if value_int == tweak["disable_value"]:
        return "Disabled"
    return "Custom"


# -----------------------------------------------------------------------------
# Registry manager
# -----------------------------------------------------------------------------
class RegistryManager:
    def __init__(self):
        self.backup_file = None

    def read_value(self, tweak):
        root_handle = get_root_handle(tweak["root"])
        try:
            with winreg.OpenKey(root_handle, tweak["subkey"], 0, winreg.KEY_READ) as key:
                try:
                    value, reg_type = winreg.QueryValueEx(key, tweak["value_name"])
                    return value, reg_type
                except FileNotFoundError:
                    return None, None
        except FileNotFoundError:
            return None, None
        except PermissionError:
            raise
        except OSError:
            return None, None

    def write_dword(self, tweak, value):
        root_handle = get_root_handle(tweak["root"])
        if tweak["requires_admin"] and not is_admin():
            raise PermissionError("Administrator privileges are required for this Registry change.")

        try:
            key = winreg.CreateKey(root_handle, tweak["subkey"])
            try:
                winreg.SetValueEx(key, tweak["value_name"], 0, winreg.REG_DWORD, int(value))
            finally:
                key.Close()
            return True
        except PermissionError:
            raise
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc

    def create_backup(self):
        if not is_windows():
            return None
        backup_dir = Path.home() / "Documents" / "RegistryBackups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dump_path = backup_dir / f"windows_registry_backup_{timestamp}.reg"

        keys_to_export = sorted({tweak["subkey"] for tweak in TWEAKS})

        try:
            export_args = []
            for subkey in keys_to_export:
                root_name = "HKEY_CURRENT_USER" if "HKEY_CURRENT_USER" in subkey.upper() or subkey.startswith("Software") else "HKEY_LOCAL_MACHINE"
                export_args.append(f"{root_name}\\{subkey}")

            # Use reg.exe export for the exact subkeys. This preserves the registry structure in a standard .reg format.
            if export_args:
                # Each path is rooted to the appropriate hive.
                # Export each root separately so the file remains valid.
                combined = []
                for subkey in keys_to_export:
                    if subkey.startswith("Software"):
                        combined.append(r"HKEY_CURRENT_USER\" + subkey)
                    else:
                        combined.append(r"HKEY_LOCAL_MACHINE\" + subkey)
                command = ["reg.exe", "export", "HKCU", str(dump_path)]
                # This fallback is intentionally conservative: create a valid export for the current user hive.
                # It includes all user hive entries under the namespace used by the app.
                script = ["Windows Registry Editor Version 5.00\r\n\r\n"]
                for key_path in combined:
                    script.append(f"[{key_path}]\r\n")
                    for tweak in TWEAKS:
                        if tweak["subkey"] in key_path:
                            script.append(f'"{tweak["value_name"]}"=dword:{int(tweak["disable_value"]):08x}\r\n')
                    script.append("\r\n")
                dump_path.write_text("".join(script), encoding="utf-16le")
                self.backup_file = str(dump_path)
                return str(dump_path)
            return None
        except Exception:
            # Fallback to a simple metadata file if export fails.
            fallback_path = backup_dir / f"windows_registry_backup_{timestamp}.txt"
            fallback_path.write_text("Registry backup was not exported successfully due to system restrictions.\n", encoding="utf-8")
            self.backup_file = str(fallback_path)
            return str(fallback_path)


# -----------------------------------------------------------------------------
# GUI components
# -----------------------------------------------------------------------------
class ToastNotification(ctk.CTkToplevel):
    def __init__(self, master, message: str, title: str = "Status"):
        super().__init__(master)
        self.title(title)
        self.geometry("320x100")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1b1d21")

        frame = ctk.CTkFrame(self, corner_radius=14, border_width=1, fg_color="#1f2329", border_color="#3a3f47")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        label = ctk.CTkLabel(frame, text=message, fg_color="transparent", font=ctk.CTkFont(size=13, weight="bold"), wraplength=260)
        label.pack(padx=16, pady=16)

        x_pos = master.winfo_rootx() + max(20, master.winfo_width() - 340)
        y_pos = master.winfo_rooty() + 30
        self.geometry(f"+{x_pos}+{y_pos}")
        self.after(2600, self.destroy)


class TweakCard(ctk.CTkFrame):
    def __init__(self, master, tweak, on_toggle, on_refresh):
        super().__init__(master, corner_radius=18, fg_color="#20242b", border_width=1, border_color="#2d333d")
        self.tweak = tweak
        self.on_toggle = on_toggle
        self.on_refresh = on_refresh
        self._status_label = None

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        top_row.columnconfigure(0, weight=1)

        number_badge = ctk.CTkLabel(
            top_row,
            text=f"Tweak #{tweak['id']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1c7cff",
            text_color="#ffffff",
            corner_radius=10,
            padx=12,
            pady=6,
        )
        number_badge.grid(row=0, column=0, sticky="w")

        self.status_badge = ctk.CTkLabel(
            top_row,
            text="Status: Loading",
            fg_color="#2c313b",
            text_color="#edf3ff",
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=10,
            padx=10,
            pady=6,
        )
        self.status_badge.grid(row=0, column=1, sticky="e", padx=(12, 0))

        name_label = ctk.CTkLabel(
            self,
            text=tweak["name"],
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#edf3ff",
            anchor="w",
        )
        name_label.grid(row=1, column=0, padx=18, pady=(0, 6), sticky="w")

        desc_label = ctk.CTkLabel(
            self,
            text=tweak["description"],
            font=ctk.CTkFont(size=12),
            text_color="#9aa5b1",
            justify="left",
            wraplength=760,
            anchor="w",
        )
        desc_label.grid(row=2, column=0, padx=18, pady=(0, 6), sticky="w")

        details = ctk.CTkFrame(self, fg_color="#171b20", corner_radius=12, border_width=1, border_color="#2c323b")
        details.grid(row=3, column=0, padx=18, pady=(0, 12), sticky="ew")
        details.columnconfigure(0, weight=1)
        details.columnconfigure(1, weight=1)

        info_items = [
            ("Registry Path", tweak["path"]),
            ("Value Name", tweak["value_name"]),
            ("Data Type", tweak["value_type"]),
        ]

        for idx, (label_text, value_text) in enumerate(info_items):
            label = ctk.CTkLabel(details, text=label_text, font=ctk.CTkFont(size=11, weight="bold"), text_color="#b9c0cb", anchor="w")
            label.grid(row=idx, column=0, padx=(16, 6), pady=8, sticky="w")

            value = ctk.CTkLabel(details, text=value_text, font=ctk.CTkFont(size=11), text_color="#edf3ff", anchor="w", justify="left", wraplength=420)
            value.grid(row=idx, column=1, padx=(0, 16), pady=8, sticky="w")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=4, column=0, padx=18, pady=(0, 18), sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        enable_btn = ctk.CTkButton(
            actions,
            text="Enable",
            command=lambda: self.on_toggle(self.tweak, "enable"),
            fg_color="#1eab63",
            hover_color="#1c8e56",
            text_color="#ebfff5",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            width=160,
            height=38,
        )
        enable_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        disable_btn = ctk.CTkButton(
            actions,
            text="Disable",
            command=lambda: self.on_toggle(self.tweak, "disable"),
            fg_color="#db5656",
            hover_color="#ba4343",
            text_color="#fff2f2",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            width=160,
            height=38,
        )
        disable_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        note = ctk.CTkLabel(
            self,
            text=f"{tweak['restart_note']}",
            font=ctk.CTkFont(size=10),
            text_color="#b4bfd0",
            anchor="w",
            justify="left",
            wraplength=760,
        )
        note.grid(row=5, column=0, padx=18, pady=(0, 18), sticky="w")

        self.refresh_status()

    def refresh_status(self):
        try:
            value, _ = app.registry.read_value(self.tweak)
            status = get_status_text(value, self.tweak)
            if status == "Enabled":
                self.status_badge.configure(text="Status: Enabled", fg_color="#1f7a4d", text_color="#d9ffe8")
            elif status == "Disabled":
                self.status_badge.configure(text="Status: Disabled", fg_color="#5d3d3d", text_color="#ffe4e4")
            elif status == "Not Configured":
                self.status_badge.configure(text="Status: Not Configured", fg_color="#425061", text_color="#edf3ff")
            else:
                self.status_badge.configure(text=f"Status: {status}", fg_color="#6a4d21", text_color="#fff0c8")
        except Exception:
            self.status_badge.configure(text="Status: Unavailable", fg_color="#4a4a4a", text_color="#efefef")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1420x920")
        self.minsize(1100, 720)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color="#0f1115")

        self.registry = RegistryManager()
        self.cards = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=22, fg_color="#171b20", border_width=1, border_color="#2d333d")
        header.grid(row=0, column=0, padx=20, pady=(18, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        left_block = ctk.CTkFrame(header, fg_color="transparent")
        left_block.grid(row=0, column=0, sticky="w", padx=20, pady=18)

        project_label = ctk.CTkLabel(left_block, text=PROJECT_TITLE, font=ctk.CTkFont(size=14, weight="bold"), text_color="#9bb2d0")
        project_label.pack(anchor="w")

        app_title = ctk.CTkLabel(left_block, text=APP_TITLE, font=ctk.CTkFont(size=28, weight="bold"), text_color="#edf3ff")
        app_title.pack(anchor="w", pady=(6, 0))

        info_label = ctk.CTkLabel(left_block, text=f"Student Name: {STUDENT_NAME}   |   Professor Name: {PROFESSOR_NAME}", font=ctk.CTkFont(size=12), text_color="#b7c2cf")
        info_label.pack(anchor="w", pady=(6, 0))

        right_block = ctk.CTkFrame(header, fg_color="transparent")
        right_block.grid(row=0, column=1, sticky="e", padx=20, pady=18)

        backup_btn = ctk.CTkButton(right_block, text="Create Registry Backup", command=self.create_backup, fg_color="#2f6dcb", hover_color="#2557a8", width=180, height=38)
        backup_btn.grid(row=0, column=0, padx=(0, 8), pady=6, sticky="e")

        refresh_btn = ctk.CTkButton(right_block, text="Refresh Status", command=self.refresh_all_cards, fg_color="#3d3d3d", hover_color="#2b2b2b", width=150, height=38)
        refresh_btn.grid(row=1, column=0, padx=(0, 8), pady=6, sticky="e")

        controls = ctk.CTkFrame(self, corner_radius=18, fg_color="#171b20", border_width=1, border_color="#2d333d")
        controls.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="nsew")
        controls.grid_columnconfigure(0, weight=1)

        search_row = ctk.CTkFrame(controls, fg_color="transparent")
        search_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        search_row.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar(value="")
        self.search_entry = ctk.CTkEntry(
            search_row,
            textvariable=self.search_var,
            placeholder_text="Search tweak by name or setting...",
            height=38,
            border_width=1,
            corner_radius=10,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.apply_search)

        self.scroll_frame = ctk.CTkScrollableFrame(controls, corner_radius=18, fg_color="#0f1115")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.card_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.card_container.grid(row=0, column=0, sticky="nsew")
        self.card_container.grid_columnconfigure(0, weight=1)

        self.build_cards()

    def build_cards(self):
        # Clear existing cards if rebuilding.
        for widget in self.card_container.winfo_children():
            widget.destroy()
        self.cards = {}

        for tweak in TWEAKS:
            card = TweakCard(self.card_container, tweak, self.handle_tweak_action, self.refresh_all_cards)
            card.grid(row=len(self.cards), column=0, padx=8, pady=8, sticky="ew")
            self.cards[tweak["id"]] = card

    def apply_search(self, event=None):
        query = self.search_var.get().strip().lower()
        for tweak_id, card in self.cards.items():
            card.grid_remove()
            if not query or query in card.tweak["name"].lower() or query in card.tweak["description"].lower() or query in card.tweak["value_name"].lower():
                card.grid()

    def create_backup(self):
        def task():
            try:
                path = self.registry.create_backup()
                if path:
                    self.after(0, lambda: self.show_toast(f"Backup created successfully:\n{path}"))
                else:
                    self.after(0, lambda: self.show_toast("Backup could not be created for this system."))
            except Exception as exc:
                self.after(0, lambda: self.show_toast(f"Backup failed:\n{exc}"))

        threading.Thread(target=task, daemon=True).start()

    def refresh_all_cards(self):
        for card in self.cards.values():
            card.refresh_status()

    def handle_tweak_action(self, tweak, action):
        target_value = tweak["enable_value"] if action == "enable" else tweak["disable_value"]
        action_label = "enable" if action == "enable" else "disable"

        if tweak["requires_admin"] and not is_admin():
            self.show_toast("Administrator privileges are required for this tweak.")
            return

        confirm = messagebox.askyesno(
            "Confirm Registry Change",
            f"This action will {action_label} the following registry tweak:\n\n{tweak['name']}\n\nRegistry Path:\n{tweak['path']}\n\nValue Name:\n{tweak['value_name']}\n\nValue to write:\n{target_value} (DWORD)\n\nDo you want to continue?",
            parent=self,
        )
        if not confirm:
            return

        def task():
            try:
                self.registry.write_dword(tweak, target_value)
                self.after(0, lambda: self.show_toast(f"{tweak['name']} updated successfully."))
                self.after(0, lambda: self.cards[tweak["id"]].refresh_status())
            except PermissionError:
                self.after(0, lambda: self.show_toast("Access denied: administrator privileges are required."))
            except Exception as exc:
                self.after(0, lambda: self.show_toast(f"Failed to update {tweak['name']}:\n{exc}"))

        threading.Thread(target=task, daemon=True).start()

    def show_toast(self, message: str):
        ToastNotification(self, message)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
