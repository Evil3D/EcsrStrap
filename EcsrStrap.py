import os
import subprocess
import sys
import json
import platform
import time
from colorama import Fore, Style, init

# Init colorama
init(autoreset=True)

# Get the script's own directory regardless of how it's launched
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FASTFLAGS_FILE = os.path.join(SCRIPT_DIR, "fastFlags.json")
LAUNCHER_STATE_FILE = os.path.join(SCRIPT_DIR, "launcher_state.json")

version_prefix = "ECSRClient280825"

# fixed press any key (i think??)
if os.name == "nt":
    import msvcrt
    def press_any_key(prompt="Press any key to continue..."):
        print(Fore.MAGENTA + prompt, end="", flush=True)
        msvcrt.getch()
        print()
else:
    def press_any_key(prompt="Press any key to continue..."):
        input(Fore.MAGENTA + prompt)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_system_info():
    """Get system information for cross-platform compatibility"""
    system = platform.system().lower()
    return {
        'is_windows': system == 'windows',
        'is_linux': system == 'linux',
        'is_macos': system == 'darwin',
        'system_name': system
    }

def get_installation_paths():
    """Get platform-specific installation paths"""
    sys_info = get_system_info()
    
    if sys_info['is_windows']:
        return [
            os.path.expandvars(r"%localappdata%\ECSR/Versions/ECSRClient280825")
        ]
    elif sys_info['is_linux']:
        user = os.getenv('USER', 'user')
        return [
            os.path.expanduser(f"~/.wine/drive_c/users/{user}/AppData/Local/ECSR/Versions/ECSRClient280825"),
            os.path.expanduser(f"~/.local/share/wineprefixes/pekora/drive_c/users/{user}/AppData/Local/ECSR/Versions/ECSRClient280825"),
            os.path.expanduser(f"~/.local/share/wineprefixes/projectx/drive_c/users/{user}/AppData/Local/ECSR/Versions/ECSRClient280825")
        ]
    elif sys_info['is_macos']:
        user = os.getenv('USER', 'user')
        return [
            os.path.expanduser(f"~/.wine/drive_c/users/{user}/AppData/Local/ECSR/Versions/ECSRClient280825"),
            os.path.expanduser(f"~/Library/Application Support/CrossOver/Bottles/*/drive_c/users/{user}/AppData/Local/ECSR/Versions/ECSRClient280825"),
            os.path.expanduser(f"~/Parallels/*.pvm/Windows*/Users/{user}/AppData/Local/ECSR/Versions/ECSRClient280825")
        ]
    else:
        print(Fore.YELLOW + f"[!] Unsupported system: {sys_info['system_name']}")
        return []

def get_executable_paths(folder):
    """Get platform-specific executable paths"""
    sys_info = get_system_info()
    base_paths = get_installation_paths()
    exe_paths = []
    
    for base_path in base_paths:
        if sys_info['is_windows']:
            exe_paths.append(os.path.join(base_path, "RobloxPlayerLauncher.exe"))
        else:
            exe_paths.append(os.path.join(base_path, "RobloxPlayerLauncher.exe"))
    
    return exe_paths

def load_fastflags():
    print(Fore.CYAN + f"[*] Attempting to read FastFlags from '{FASTFLAGS_FILE}'...")
    if not os.path.exists(FASTFLAGS_FILE):
        print(Fore.YELLOW + "[*] File does not exist. Creating a new one...")
        with open(FASTFLAGS_FILE, "w") as f:
            json.dump({}, f, indent=2)
        print(Fore.GREEN + "[*] Created new empty file.")
        return {}
    try:
        with open(FASTFLAGS_FILE, "r") as f:
            raw_content = f.read()
            # Sanitize the content by replacing non-breaking spaces with regular spaces
            sanitized_content = raw_content.replace('\u00A0', ' ')
            
            data = json.loads(sanitized_content)
            
            if isinstance(data, dict):
                print(Fore.GREEN + f"[*] Successfully read {len(data)} FastFlag(s).")
                print(Fore.MAGENTA + f"[*] Read data: {json.dumps(data, indent=2)}")
                return data
            else:
                print(Fore.RED + f"[!] The file '{FASTFLAGS_FILE}' contains invalid data. Expected a JSON object.")
                return {}
    except json.JSONDecodeError as e:
        print(Fore.RED + f"[!] Error reading '{FASTFLAGS_FILE}' - Invalid JSON format: {e}")
        print(Fore.YELLOW + "[*] The file might have been corrupted. Returning an empty set of flags.")
        return {}
    except Exception as e:
        print(Fore.RED + f"[!] An unexpected error occurred while reading '{FASTFLAGS_FILE}': {e}")
        return {}

def save_fastflags(fastflags):
    try:
        with open(FASTFLAGS_FILE, "w") as f:
            json.dump(fastflags, f, indent=2)
        print(Fore.GREEN + "[*] FastFlags saved successfully!")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to save FastFlags: {e}")

def apply_fastflags(fastflags):
    success = False
    base_paths = get_installation_paths()
    
    for base_path in base_paths:
        # Check if the base path (e.g., .../ECSRClient280825) exists
        if os.path.exists(base_path):
            client_settings_dir = os.path.join(base_path, "ClientSettings")
            try:
                # Create the ClientSettings folder if it doesn't exist
                os.makedirs(client_settings_dir, exist_ok=True)
                
                settings_path = os.path.join(client_settings_dir, "ClientAppSettings.json")
                
                # Overwrite any existing file
                with open(settings_path, "w") as f:
                    json.dump(fastflags, f, indent=2)
                print(Fore.GREEN + f"[*] Applied FastFlags successfully.")
                print(Fore.CYAN + f"[*] Location: {settings_path}")
                success = True
                # Break after the first successful application
                break
            except Exception as e:
                print(Fore.RED + f"[!] Failed to write to {base_path}: {e}")
    
    return success

def auto_detect_value_type(value_str):
    value_str = value_str.strip()
    
    # boooooooolean
    if value_str.lower() in ['true', 'false']:
        return value_str.lower() == 'true'
    
    # int 
    try:
        if '.' not in value_str and 'e' not in value_str.lower():
            return int(value_str)
    except ValueError:
        pass
    
    # fLOATIES
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # string
    return value_str

def ask_fastflags():
    while True:
        clear()
        print(Fore.YELLOW + "FastFlags Configuration")
        fastflags = load_fastflags()
        
        if fastflags:
            print(Fore.CYAN + "Current FFlags:")
            for i, (k, v) in enumerate(fastflags.items(), 1):
                value_type = type(v).__name__
                print(Fore.YELLOW + f" {i}. {k} = {v} ({value_type})")
        else:
            print(Fore.MAGENTA + "No fflags set yet")
        
        print(Fore.GREEN + "\nOptions:")
        print("1. Add FastFlag")
        print("2. Remove FastFlag") 
        print("3. Clear all FastFlags")
        print("4. Apply FastFlags")
        print("5. Import FastFlags from JSON")
        print("0. Back to main menu")
        
        choice = input(Fore.WHITE + "\nEnter choice: ").strip()
        
        if choice == "1":
            add_fastflag(fastflags)
        elif choice == "2":
            remove_fastflag(fastflags)
        elif choice == "3":
            clear_fastflags()
        elif choice == "4":
            if fastflags:
                if apply_fastflags(fastflags):
                    print(Fore.GREEN + "[*] FastFlags applied successfully.")
                else:
                    print(Fore.RED + "[!] Failed to apply FastFlags")
            else:
                print(Fore.YELLOW + "[*] No FastFlags to apply")
            press_any_key()
        elif choice == "5":
            import_fastflags()
        elif choice == "0":
            break
        else:
            print(Fore.RED + "Invalid choice!")
            press_any_key()

def add_fastflag(fastflags):
    print(Fore.GREEN + "\nAdd New FastFlag:")
    print(Fore.CYAN + "Tip: Values are auto-converted.")
    print(Fore.CYAN + "Common example:")
    print(Fore.YELLOW + "  FFlagDebugGraphicsDisableMetal = true")
    
    key = input(Fore.WHITE + "\nKey: ").strip()
    if not key:
        print(Fore.RED + "[*] Cancelled - no key provided")
        press_any_key()
        return
    
    value_input = input(Fore.WHITE + "Value: ").strip()
    if value_input == "":
        print(Fore.RED + "[*] Cancelled - no value provided")
        press_any_key()
        return
    
    value = auto_detect_value_type(value_input)
    fastflags[key] = value
    save_fastflags(fastflags)
    
    value_type = type(value).__name__
    print(Fore.GREEN + f"[*] Added FastFlag: {key} = {value} ({value_type})")
    press_any_key()

def remove_fastflag(fastflags):
    if not fastflags:
        print(Fore.YELLOW + "[*] No FastFlags to remove")
        press_any_key()
        return
    
    print(Fore.YELLOW + "\nRemove FastFlag:")
    key = input(Fore.WHITE + "Enter key to remove: ").strip()
    
    if key in fastflags:
        del fastflags[key]
        save_fastflags(fastflags)
        print(Fore.GREEN + f"[*] Removed FastFlag: {key}")
    else:
        print(Fore.RED + f"[!] FastFlag '{key}' not found")
    
    press_any_key()

def clear_fastflags():
    confirm = input(Fore.RED + "Are you sure you want to clear ALL FastFlags? (y/N): ").strip().lower()
    if confirm == 'y':
        save_fastflags({})
        print(Fore.GREEN + "[*] All FastFlags cleared")
    else:
        print(Fore.YELLOW + "[*] Cancelled")
    press_any_key()

def import_fastflags():
    print(Fore.CYAN + "\nImport FastFlags from JSON:")
    print(Fore.YELLOW + "Example format: {\"FFlagDebugGraphicsDisableMetal\": true, \"DFIntTaskSchedulerTargetFps\": 144}")
    print(Fore.YELLOW + "Paste JSON content and press Enter twice when done:")
    
    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2 or (len(lines) > 0 and lines[-1] == ""):
                break
        else:
            empty_count = 0
        lines.append(line)
    
    # idk waht this does smb told me to addd
    while lines and lines[-1] == "":
        lines.pop()
    
    json_text = "\n".join(lines)
    
    if not json_text.strip():
        print(Fore.YELLOW + "[*] No content provided")
        press_any_key()
        return
    
    try:
        imported_flags = json.loads(json_text)
        if not isinstance(imported_flags, dict):
            print(Fore.RED + "[!] JSON must be an object/dictionary")
            press_any_key()
            return
        
        current_flags = load_fastflags()
        current_flags.update(imported_flags)
        save_fastflags(current_flags)
        
        print(Fore.GREEN + f"[*] Imported {len(imported_flags)} FastFlag(s)")
        for k, v in imported_flags.items():
            print(Fore.CYAN + f"  + {k} = {v}")
            
    except json.JSONDecodeError as e:
        print(Fore.RED + f"[!] Invalid JSON format: {e}")
    
    press_any_key()

def debug():
    clear()
    sys_info = get_system_info()
    print(Fore.MAGENTA + "Debug info")

    # check paths
    base_paths = get_installation_paths()
    
    print(Fore.CYAN + "Checking installation paths:")
    for base_path in base_paths:
        if os.path.exists(base_path):
            print(Fore.GREEN + f"  ✓ Found: {base_path}")
            exe_path = os.path.join(base_path, "RobloxPlayerLauncher.exe")
            if os.path.exists(exe_path):
                print(Fore.GREEN + f"    ✓ Executable found: {exe_path}")
            else:
                print(Fore.RED + f"    ✗ Executable NOT found: {exe_path}")
        else:
            print(Fore.RED + f"  ✗ Not found: {base_path}")
    
    # check ClientSettings
    exe_paths = get_installation_paths()
    
    print(Fore.CYAN + f"\nClientSettings status:")
    for base_path in exe_paths:
        if os.path.exists(base_path):
            client_settings_dir = os.path.join(base_path, "ClientSettings")
            settings_file = os.path.join(client_settings_dir, "ClientAppSettings.json")
            print(Fore.YELLOW + f"ClientSettings path: {settings_file}")
            if os.path.exists(settings_file):
                print(Fore.GREEN + "  ✓ Exists")
                try:
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                    print(Fore.CYAN + f"  Active FastFlags: {len(settings)}")
                    if settings:
                        print(Fore.YELLOW + "  Current flags:")
                        for k, v in list(settings.items())[:3]:  # Show first 3
                            print(Fore.CYAN + f"    {k} = {v}")
                        if len(settings) > 3:
                            print(Fore.CYAN + f"    ... and {len(settings) - 3} more")
                except Exception as e:
                    print(Fore.RED + f"  ✗ Error reading: {e}")
            else:
                print(Fore.RED + "  ✗ Not found")

    # fastflags file
    print(Fore.CYAN + f"\nLocal FastFlags file: {FASTFLAGS_FILE}")
    if os.path.exists(FASTFLAGS_FILE):
        print(Fore.GREEN + "  ✓ Exists")
        try:
            local_flags = load_fastflags()
            print(Fore.CYAN + f"  Stored FastFlags: {len(local_flags)}")
        except:
            print(Fore.RED + "  ✗ Error reading local file")
    else:
        print(Fore.RED + "  ✗ Not found")

    # Wine check for non-Windows systems
    if not sys_info['is_windows']:
        print(Fore.CYAN + f"\nWine Configuration:")
        try:
            wine_version = subprocess.check_output(["wine64", "--version"], stderr=subprocess.DEVNULL).decode().strip()
            print(Fore.GREEN + f"  ✓ Wine installed: {wine_version}")
        except:
            try:
                wine_version = subprocess.check_output(["wine", "--version"], stderr=subprocess.DEVNULL).decode().strip()
                print(Fore.GREEN + f"  ✓ Wine installed: {wine_version}")
            except:
                print(Fore.RED + "  ✗ Wine not found - required for running Windows executables") 

    print(Fore.CYAN + f"\nSystem Information:")
    print(Fore.YELLOW + f"OS: {platform.system()} {platform.release()}")
    print(Fore.YELLOW + f"Architecture: {platform.machine()}")
    print(Fore.YELLOW + f"CPU: {platform.processor() or 'Unknown'}")
    print(Fore.YELLOW + f"Python: {sys.version.split()[0]}")
    
    if sys_info['is_linux']:
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                for line in os_info.split('\n'):
                    if line.startswith('PRETTY_NAME='):
                        distro = line.split('=')[1].strip('"')
                        print(Fore.YELLOW + f"Distribution: {distro}")
                        break
        except:
            pass

    print(Fore.MAGENTA + "=" * 50)
    press_any_key()

def save_state(state):
    try:
        with open(LAUNCHER_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(Fore.RED + f"[!] Failed to save launcher state: {e}")

def load_state():
    if not os.path.exists(LAUNCHER_STATE_FILE):
        return {}
    try:
        with open(LAUNCHER_STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(Fore.RED + "[!] Error reading launcher_state.json - invalid JSON format.")
        return {}

def register_uri_handler():
    """
    Registers the script as the handler for the 'ecsr-player' URI scheme.
    This is necessary for 'xdg-open' or browser clicks to work correctly.
    """
    clear()
    sys_info = get_system_info()
    
    script_path = os.path.abspath(sys.argv[0])

    print(Fore.CYAN + "Checking for existing URI handler...")
    
    if sys_info['is_windows']:
        try:
            # Check if the registry key exists
            import winreg
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\ecsr-player")
                print(Fore.GREEN + "[*] URI handler for 'ecsr-player' is already registered.")
                print(Fore.CYAN + "You can now launch games directly from the browser.")
                press_any_key()
                return
            except FileNotFoundError:
                pass
            
            print(Fore.YELLOW + "[*] Registering URI handler for Windows...")
            
            # Use subprocess to call the reg.exe command line tool
            reg_script = f"""Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\Software\\Classes\\ecsr-player]
@="URL:ECSR Player Protocol"
"URL Protocol"=""

[HKEY_CURRENT_USER\\Software\\Classes\\ecsr-player\\shell]

[HKEY_CURRENT_USER\\Software\\Classes\\ecsr-player\\shell\\open]

[HKEY_CURRENT_USER\\Software\\Classes\\ecsr-player\\shell\\open\\command]
@="\\"{sys.executable}\\" \\"{script_path}\\" \\"%1\\""
"""
            reg_file = "ecsr_register.reg"
            with open(reg_file, "w") as f:
                f.write(reg_script)
            
            subprocess.run(["reg", "import", reg_file], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            os.remove(reg_file)
            
            print(Fore.GREEN + "[*] Successfully registered the URI handler!")
            print(Fore.CYAN + "You can now launch games directly from the browser.")
            
        except ImportError:
            print(Fore.RED + "[!] winreg module not found. Registration failed.")
        except Exception as e:
            print(Fore.RED + f"[!] Failed to register URI handler: {e}")
        
    elif sys_info['is_linux']:
        print(Fore.YELLOW + "[*] Registering URI handler for Linux...")
        
        desktop_file_content = f"""[Desktop Entry]
Name=ECS:R Player
Exec={sys.executable} {script_path} %u
Terminal=true
Type=Application
StartupNotify=true
MimeType=x-scheme-handler/ecsr-player;
"""
        desktop_dir = os.path.expanduser("~/.local/share/applications/")
        os.makedirs(desktop_dir, exist_ok=True)
        desktop_file_path = os.path.join(desktop_dir, "ecsr-player.desktop")
        
        try:
            with open(desktop_file_path, "w") as f:
                f.write(desktop_file_content)
            
            os.chmod(desktop_file_path, 0o755)
            
            # Try the modern xdg-mime command first
            try:
                subprocess.run(["xdg-mime", "default", "ecsr-player.desktop", "x-scheme-handler/ecsr-player"], check=True)
                print(Fore.GREEN + "[*] Successfully registered URI handler using xdg-mime!")
                save_state({"uri_registered": True})
            except FileNotFoundError:
                print(Fore.YELLOW + "[!] xdg-mime not found. Falling back to update-desktop-database...")
                try:
                    subprocess.run(["update-desktop-database"], check=True)
                    print(Fore.GREEN + "[*] Successfully registered URI handler.")
                    save_state({"uri_registered": True})
                except subprocess.CalledProcessError as e:
                    print(Fore.RED + f"[!] Failed to register with update-desktop-database: {e}")
                    print(Fore.YELLOW + "This is often due to system permissions. You may need to run the command manually.")
                    print(Fore.YELLOW + f"Try running: {Fore.WHITE}sudo update-desktop-database{Fore.YELLOW}")
            except subprocess.CalledProcessError as e:
                print(Fore.RED + f"[!] Failed to register with xdg-mime: {e}")
                print(Fore.YELLOW + "This is often due to system permissions. You may need to run this command manually.")
                print(Fore.YELLOW + f"Try running: {Fore.WHITE}xdg-mime default ecsr-player.desktop x-scheme-handler/ecsr-player{Fore.YELLOW}")
                print(Fore.YELLOW + "Or manually update the database:")
                print(Fore.YELLOW + f"Try running: {Fore.WHITE}sudo update-desktop-database{Fore.YELLOW}")
            
        except Exception as e:
            print(Fore.RED + f"[!] Failed to register URI handler: {e}")
            print(Fore.RED + "Make sure you have a desktop environment that supports .desktop files.")

    elif sys_info['is_macos']:
        print(Fore.YELLOW + "[*] Registering URI handler for macOS is currently not supported.")
        print(Fore.YELLOW + "You will need to manually configure this in your system settings.")
        
    else:
        print(Fore.RED + f"[!] Unsupported system: {sys_info['system_name']}. Cannot register URI handler automatically.")
        
    press_any_key()

def check_fastflags_file():
    """Reads the fastFlags.json file as raw text and prints its contents."""
    clear()
    print(Fore.CYAN + f"[*] Checking raw contents of '{FASTFLAGS_FILE}'...")
    if not os.path.exists(FASTFLAGS_FILE):
        print(Fore.RED + f"[!] File not found: '{FASTFLAGS_FILE}'")
        print(Fore.YELLOW + "[*] Please create the file or try the FastFlags menu to create it.")
    else:
        try:
            with open(FASTFLAGS_FILE, "r") as f:
                content = f.read()
            print(Fore.GREEN + "[*] Raw file content:")
            print(Fore.WHITE + "--- START ---")
            print(content)
            print(Fore.WHITE + "--- END ---")
        except Exception as e:
            print(Fore.RED + f"[!] An error occurred while reading the file: {e}")
    press_any_key()


def main_menu():
    while True:
        clear()
        sys_info = get_system_info()

        gradient = [
            (7, 200, 249),
            (5, 157, 230),
            (4, 123, 220),
            (3, 98, 210),
            (2, 74, 200),
            (1, 58, 195),
            (0, 50, 185),
            (13, 65, 225),
        ]

        ascii_logo = [
            "  ______ _____  _____  _____     _____ _                   ",
            " |  ____/ ____|/ ____||  __ \   / ____| |                  ",
            " | |__ | |    | (___(_) |__) | | (___ | |_ _ __ __ _ _ __  ",
            " |  __|| |     \___ \ |  _  /   \___ \| __| '__/ _` | '_ \ ",
            " | |___| |____ ____) || | \ \   ____) | |_| | | (_| | |_) |",
            " |______\_____|_____(_)_|  \_\ |_____/ \__|_|  \__,_| .__/ ",
            "                                                    | |    ",
            "                                                    |_|    "
        ]

        for (r, g, b), line in zip(gradient, ascii_logo):
            print(f"\033[38;2;{r};{g};{b}m{line}\033[0m")

        print(Fore.BLUE + "Made with <3 by 1w4md on ECS:R and usertest on Pekora")
        
        # platform info
        platform_name = "Windows" if sys_info['is_windows'] else ("Linux" if sys_info['is_linux'] else ("macOS" if sys_info['is_macos'] else "Unknown"))
        print(Fore.CYAN + f"Running on: {platform_name}")
        if not sys_info['is_windows']:
            print(Fore.YELLOW + "Note: Wine is required for Windows executables")
        
        print()
        print(Fore.YELLOW + "Select your option:")
        
        # Platform-specific menu logic
        if sys_info['is_linux']:
            state = load_state()
            uri_registered = state.get("uri_registered", False)
            
            print(Fore.GREEN + "1 - Wait for ECS:R Launch")
            if not uri_registered:
                print(Fore.GREEN + "2 - Register URI Handler")
                print(Fore.GREEN + "3 - Set FastFlags")
            else:
                print(Fore.GREEN + "2 - Set FastFlags")
            print(Fore.RED + "0 - Exit")
            
            choice = input(Fore.WHITE + "\nEnter your choice: ")
            
            if choice == "1":
                print(Fore.CYAN + "[*] Waiting for an ECS:R URI launch request...")
                print(Fore.YELLOW + "Note: You must have this script registered as the handler for 'ecsr-player://' URIs.")
                print(Fore.YELLOW + "Press Ctrl+C to stop waiting.")
                while True:
                    time.sleep(1)
            elif choice == "2":
                if not uri_registered:
                    register_uri_handler()
                else:
                    ask_fastflags()
            elif choice == "3" and not uri_registered:
                ask_fastflags()
            elif choice == "0":
                print(Fore.CYAN + "Goodbye!")
                sys.exit()
            elif choice.lower() == "chkff":
                check_fastflags_file()
            else:
                print(Fore.RED + "Invalid choice! Try again.")
                press_any_key()
                
        elif sys_info['is_windows']:
            print(Fore.GREEN + "1 - Set FastFlags")
            print(Fore.RED + "0 - Exit")
            
            choice = input(Fore.WHITE + "\nEnter your choice: ")
            
            if choice == "1":
                ask_fastflags()
            elif choice == "0":
                print(Fore.CYAN + "Goodbye!")
                sys.exit()
            elif choice.lower() == "chkff":
                check_fastflags_file()
            else:
                print(Fore.RED + "Invalid choice! Try again.")
                press_any_key()
        else:
            # Fallback for other systems
            print(Fore.GREEN + "1 - Set FastFlags")
            print(Fore.RED + "0 - Exit")

            choice = input(Fore.WHITE + "\nEnter your choice: ")
            if choice == "1":
                ask_fastflags()
            elif choice == "0":
                print(Fore.CYAN + "Goodbye!")
                sys.exit()
            elif choice.lower() == "chkff":
                check_fastflags_file()
            else:
                print(Fore.RED + "Invalid choice! Try again.")
                press_any_key()
                
def kill_existing_process(process_name):
    """
    Kills any running process with the given name.
    """
    sys_info = get_system_info()
    if sys_info['is_windows']:
        try:
            # Check for the process and kill it if found
            subprocess.run(["taskkill", "/im", process_name, "/f"], check=True, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True)
            print(Fore.YELLOW + f"[*] Terminated existing {process_name} process.")
        except subprocess.CalledProcessError as e:
            # This is expected if the process is not found
            if "The process \"" in e.stderr.decode() and "not found." in e.stderr.decode():
                print(Fore.CYAN + f"[*] No existing {process_name} process found.")
            else:
                print(Fore.RED + f"[!] Error terminating process: {e.stderr.decode()}")
    elif sys_info['is_linux']:
        try:
            # Find the process ID and kill it
            pid = subprocess.check_output(["pgrep", process_name]).decode().strip().split('\n')
            for p in pid:
                subprocess.run(["kill", p], check=True)
            print(Fore.YELLOW + f"[*] Terminated existing {process_name} process.")
        except subprocess.CalledProcessError:
            print(Fore.CYAN + f"[*] No existing {process_name} process found.")
        except Exception as e:
            print(Fore.RED + f"[!] Error terminating process: {e}")
    else:
        print(Fore.YELLOW + "[*] Process termination not supported on this platform.")

def launch_version(uri, folder):
    clear()
    sys_info = get_system_info()

    # Step 1: Terminate any existing processes
    kill_existing_process("RobloxPlayerLauncher.exe")
    
    # Step 2: Apply FastFlags
    fastflags = load_fastflags()
    
    # This is the corrected line. It will now always print the correct number of flags.
    print(Fore.CYAN + f"[*] Applying {len(fastflags)} FastFlag(s)...")

    success = apply_fastflags(fastflags)
    
    if not success:
        print(Fore.RED + "[!] Failed to apply FastFlags to any valid location.")

    # Step 3: Launch the game
    print(Fore.CYAN + f"Launching {folder} with URI: {uri}...")

    exe_path = None
    base_paths = get_installation_paths()
    for base_path in base_paths:
        full_path = os.path.join(base_path, "RobloxPlayerLauncher.exe")
        if os.path.isfile(full_path):
            exe_path = full_path
            break
    
    if exe_path:
        try:
            launch_args = [exe_path, uri] # Pass the URI as a command-line argument
            if sys_info['is_windows']:
                subprocess.Popen(launch_args)
            elif sys_info['is_linux']:
                subprocess.Popen([
                    "env",
                    "__NV_PRIME_RENDER_OFFLOAD=1",
                    "__GLX_VENDOR_LIBRARY_NAME=nvidia",
                    "wine64",
                ] + launch_args)
            elif sys_info['is_macos']:
                subprocess.Popen(["wine64"] + launch_args)
            
            print(Fore.GREEN + "[*] Launch successful!")
        except Exception as e:
            print(Fore.RED + f"Error while launching:\n{e}")
            if not sys_info['is_windows']:
                print(Fore.YELLOW + "Make sure Wine is installed and configured properly.")
    else:
        print(Fore.RED + "Could not find executable. Error code: EXECNFOUND")
        print(Fore.YELLOW + "Searched paths:")
        for path in [os.path.join(bp, "RobloxPlayerLauncher.exe") for bp in base_paths]:
            print(Fore.YELLOW + f"  - {path}")
        
        if not sys_info['is_windows']:
            print(Fore.CYAN + "\nTroubleshooting tips:")
            print(Fore.YELLOW + "- Make sure Wine is installed")
            print(Fore.YELLOW + "- Verify your Wine prefix is configured")
            print(Fore.YELLOW + "- Check that the game is installed in the Wine prefix")

    press_any_key()

if __name__ == "__main__":
    # Check if a URI was passed as a command-line argument
    if len(sys.argv) > 1 and sys.argv[1].startswith("ecsr-player:"):
        # The script was launched by xdg-open to handle a URI
        uri = sys.argv[1]
        launch_version(uri, "ECS:R")
    else:
        # The script was launched directly, show the main menu
        main_menu()
