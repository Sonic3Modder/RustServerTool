from elevate import elevate
import subprocess
import platform

def check_for_ports() -> dict:
    """Returns which ports are already open and which are not."""
    result = {
        "28015": False,  # Game port (UDP)
        "27015": False,  # Steam query port (UDP)
        "28016": False,  # RCON port (TCP)
    }

    if platform.system() == "Windows":
        for port in result:
            check = subprocess.run(
                ["powershell", "-Command",
                 f"Get-NetFirewallRule | Where-Object {{ $_.DisplayName -like '*{port}*' -and $_.Enabled -eq 'True' }}"],
                capture_output=True, text=True
            )
            result[port] = bool(check.stdout.strip())

    elif platform.system() == "Linux":
        for port in result:
            check = subprocess.run(
                ["sudo", "ufw", "status"],
                capture_output=True, text=True
            )
            result[port] = port in check.stdout

    return result


def firewall_access():
    already_open = check_for_ports()

    try:
        elevate()
        if platform.system() == "Windows":
            for port, is_open in already_open.items():
                if is_open:
                    print(f"Port {port} is already open, skipping.")
                else:
                    print(f"Opening port {port}...")
                    subprocess.run([
                        "powershell", "-Command",
                        f"New-NetFirewallRule -DisplayName 'RUST_{port}' "
                        f"-Direction Inbound -LocalPort {port} -Protocol UDP -Action Allow"
                    ])

        elif platform.system() == "Linux":
            for port, is_open in already_open.items():
                if is_open:
                    print(f"Port {port} is already open, skipping.")
                else:
                    print(f"Opening port {port}...")
                    subprocess.run(["sudo", "ufw", "allow", port])

    except subprocess.CalledProcessError as e:
        print(f"Command Failed: {e}")
    except PermissionError:
        print("Permission denied. Please allow the use of elevation.")