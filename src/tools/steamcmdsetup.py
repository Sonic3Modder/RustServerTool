import platform
import subprocess
import shutil
import distro


def install(install_dir):
    system = platform.system().lower()
    distro_id = distro.id()

    steamcmd_installed = shutil.which("steamcmd") is not None

    if steamcmd_installed:
        return

    if system == "windows":
        subprocess.run(
            ["powershell", "-Command", "winget install steamcmd --silent"],
            check=True
        )

    elif system == "linux":

        if distro_id == "ubuntu":
            subprocess.run(["sudo", "add-apt-repository", "multiverse"], check=True)
            subprocess.run(["sudo", "dpkg", "--add-architecture", "i386"], check=True)
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "steamcmd", "-y"], check=True)

        elif distro_id == "debian":
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "software-properties-common", "-y"], check=True)
            subprocess.run(["sudo", "apt-add-repository", "non-free"], check=True)
            subprocess.run(["sudo", "dpkg", "--add-architecture", "i386"], check=True)
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "steamcmd", "-y"], check=True)

        elif distro_id in ["fedora", "rhel"]:
            subprocess.run(["sudo", "dnf", "install", "steamcmd", "-y"], check=True)

        elif distro_id == "gentoo":
            subprocess.run(["sudo", "emerge", "steamcmd"], check=True)

    elif system == "darwin":
        subprocess.run(
            ["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"],
            check=True
        )
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "install", "steamcmd"], check=True)

    steamcmd_installed = shutil.which("steamcmd") is not None

    if steamcmd_installed:
        print("steamcmd installed successfully")
    else:
        print("steamcmd installation failed")