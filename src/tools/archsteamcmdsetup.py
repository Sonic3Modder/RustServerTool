import platform
import subprocess
import sys
import distro



def install_cmd():
    distro_id = distro.id()
    if platform.system().lower() == "linux" and distro_id in ["arch", "manjaro"]:
        subprocess.run(["sudo", "pacman", "-Syy", "base-devel", "--noconfirm"], check=True)
        subprocess.run(["pacman", "-Syu", "git", "--noconfirm"], check=True)
        subprocess.run(["git", "clone", "https://aur.archlinux.org/steamcmd.git"], check=True)
        subprocess.run(["makepkg", "-si", "--noconfirm"], cwd="steamcmd", check=True)
    

