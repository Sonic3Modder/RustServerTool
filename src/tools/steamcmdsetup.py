import shutil
import platform
import distro
import subprocess

def install():
    '''Basic SteamCMD Install script for GUI'''
    system = platform.system().lower()
    distro_id = distro.id()

    if shutil.which("steamcmd") is not None:
        return

    commands = _get_install_commands(system, distro_id)
    if not commands:
        print("Unsupported OS/distro")
        return

    for cmd in commands:
        result = subprocess.run(cmd, text=True)
        print(result.stdout)  # or pipe to a Qt text widget
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return

    if shutil.which("steamcmd") is not None:
        print("steamcmd installed successfully")
    else:
        print("steamcmd installation failed")


def _get_install_commands(system, distro_id):
    if system == "windows":
        return [["powershell", "-Command", "winget install steamcmd --silent"]]
    elif system == "linux":
        if distro_id == "ubuntu":
            return [
                ["sudo", "add-apt-repository", "multiverse"],
                ["sudo", "dpkg", "--add-architecture", "i386"],
                ["sudo", "apt", "update"],
                ["sudo", "apt", "install", "steamcmd", "-y"],
            ]
        elif distro_id == "debian":
            return [
                ["sudo", "apt", "update"],
                ["sudo", "apt", "install", "software-properties-common", "-y"],
                ["sudo", "apt-add-repository", "non-free"],
                ["sudo", "dpkg", "--add-architecture", "i386"],
                ["sudo", "apt", "update"],
                ["sudo", "apt", "install", "steamcmd", "-y"],
            ]
        elif distro_id in ["fedora", "rhel"]:
            return [["sudo", "dnf", "install", "steamcmd", "-y"]]
        elif distro_id == "gentoo":
            return [["sudo", "emerge", "steamcmd"]]
    elif system == "darwin":
        return [
            ["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"],
            ["brew", "update"],
            ["brew", "install", "steamcmd"],
        ]
    return None