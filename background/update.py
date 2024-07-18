# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: ocr.py
@time: 2024/7/18 上午3:11
@author RoseRin0
"""
import subprocess
import requests
import base64
import re
import os
from config import config, root_path, wait_exit
from version import __version__, release_date, description

# 项目信息
repo_type = "Gitee"  # repo_type = "Github"
owner = 'roseliarin'
repo = 'mc_tool'
version_file_path = 'background/version.py'
branch = 'master'  # 指定分支名称
msg = "请按任意键继续运行脚本"
function_executed = False


# 读取本地版本号和更新内容
def get_local_version_info():
    local_version_file_path = os.path.join(root_path, version_file_path)
    with open(local_version_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    version = __version__
    # 提取更新内容
    update_pattern = re.compile(
        r'# ver' + re.escape(version) + r'\s*'
        r'# update:' + re.escape(release_date) + r'\s*'
        r'# updated by [^\n]*\s*'
        r'((?:# [^\n]*\s*)*)'
    )
    update_match = update_pattern.search(content)
    if update_match:
        update_details = update_match.group(1).strip()
        return {
            '版本': version,
            '更新日期': release_date,
            '描述': description,
            '更新内容': update_details
        }
    return None


# 获取GitHub上的版本号和更新内容
def get_github_version_info():
    if repo_type == "Github":
        url = f'https://api.github.com/repos/{owner}/{repo}/contents/{version_file_path}?ref={branch}'
        headers = {'Accept': 'application/vnd.github+json'}
        response = requests.get(url, headers=headers)
    elif repo_type == "Gitee":
        url = f'https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{version_file_path}?ref={branch}'
        response = requests.get(url)
    else:
        print(f"使用仓库设置不正确。{msg}")
        return
    if response.status_code == 200:
        content = response.json().get('content', '')
        decoded_content = base64.b64decode(content).decode('utf-8')

        # 提取版本号和发布日期
        version_match = re.search(r'__version__\s*=\s*"([^"]+)"', decoded_content)
        date_match = re.search(r'release_date\s*=\s*"([^"]+)"', decoded_content)
        description_match = re.search(r'description\s*=\s*"([^"]+)"', decoded_content)

        if version_match and date_match and description_match:
            version = version_match.group(1)
            release_date = date_match.group(1)
            description = description_match.group(1)

            # 提取更新内容
            update_pattern = re.compile(
                r'# ver' + re.escape(version) + r'\s*'
                r'# update:' + re.escape(release_date) + r'\s*'
                r'# updated by [^\n]*\s*'
                r'((?:\s*# [^\n]*\n)+)'
            )
            update_match = update_pattern.search(decoded_content)
            if update_match:
                update_details = update_match.group(1).strip()
                # 去除每行前面的#
                update_details = re.sub(r'^# ', '', update_details, flags=re.MULTILINE)
                # 截取到第一个空行为止
                update_details = update_details.split('\n\n', 1)[0]
                return {
                    '版本': version,
                    '更新日期': release_date,
                    '描述': description,
                    '更新内容': update_details
                }
    return None


def is_git_repo():
    import git
    # 检查本地文件夹是否是一个Git仓库
    try:
        _ = git.Repo(root_path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def check_git_installed():
    try:
        # 尝试运行 `git --version` 来检查 Git 是否已安装
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Git版本: " + result.stdout.strip())
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def install_chocolatey():
    try:
        powershell_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        # 安装 Chocolatey
        print("正在安装 Chocolatey...")
        subprocess.run([powershell_path, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command',
                        'iex ((New-Object System.Net.WebClient).DownloadString(\'https://chocolatey.org/install.ps1\'))'],
                       check=True)
        print("Chocolatey 安装完成。")
    except subprocess.CalledProcessError as e:
        print(f"安装 Chocolatey 时出错: {e}")


def reload_env_vars():
    try:
        powershell_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        print("重新加载环境变量...")
        subprocess.run(
            [powershell_path, '-NoProfile', '-ExecutionPolicy', 'Bypass',
             '-Command',
             '[System.Environment]::SetEnvironmentVariable("PATH", $Env:Path, [System.EnvironmentVariableTarget]::Machine)'],
            check=True)
        print("环境变量重新加载完成。")
    except subprocess.CalledProcessError as e:
        print(f"重新加载环境变量时出错: {e}")


def install_git():
    install_chocolatey()
    reload_env_vars()
    try:
        powershell_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        print("正在安装 Git...")
        subprocess.run([powershell_path, '-NoProfile', '-ExecutionPolicy', 'Bypass',
                        '-Command',
                        'choco install git -y'], check=True)
        # 验证 Git 是否安装成功
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Git 安装成功: " + result.stdout.strip())
        else:
            print("Git 安装失败: " + result.stderr.strip())
        # 检查 Git 是否在环境变量中
        if any('git' in path.lower() for path in os.environ['PATH'].split(';')):
            print("Git 已正确添加到环境变量中")
            return True
        else:
            print("Git 未能添加到环境变量中，请手动添加")
            return False
    except subprocess.CalledProcessError as e:
        print(f"安装 Git 时出错: {e}")
        return False


def git_clone(repo_url, repo_path):
    try:
        repo_path = os.path.join(root_path, repo)
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)
        print(f"下载完毕，创建本地仓库成功\n本地仓库位置：{repo_path}\n以后请在此位置运行程序(或自行复制到其他文件夹)。")
        command = ['git', 'config', '--global', '--add', 'safe.directory', repo_path]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("设置安全目录成功")
        else:
            print(f"设置安全目录失败: {result.stderr}")
        input("首次更新成功，将打开本地仓库目录，以后请在此处运行脚本，或者复制全部文件到其他位置，按任意键继续。")
        os.startfile(repo_path)
        wait_exit()
    except subprocess.CalledProcessError as e:
        input(f"下载时发生了一个问题: {e.stderr}。{msg}")


def update_git_pull():
    import git
    try:
        repo = git.Repo(root_path)
        repo.remotes.origin.pull()
        print("更新成功，请重启脚本")
        wait_exit()
    except Exception as e:
        input(f"更新中发生错误: {e}。{msg}")


def update_download_file(download_version):
    new_version_file_name = f"{repo}_v{download_version}.zip"
    if repo_type == "Github":
        file_url = f'https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip'
    elif repo_type == "Gitee":
        file_url = f'https://gitee.com/{owner}/{repo}/repository/archive/{branch}.zip'
    else:
        input(f"未知的仓库类型: {repo_type}。{msg}")
        return
    save_path = os.path.join(root_path, new_version_file_name)
    try:
        # 发送 GET 请求下载文件
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"已成功下载文件到: {save_path}，请关闭程序后手动解压覆盖更新。")
            wait_exit()
        else:
            input(f"下载文件时出现错误，错误代码: {response.status_code}。{msg}")
    except Exception as e:
        input(f"尝试下载文件时发生了错误: {str(e)}。{msg}")


# 比较版本号并提示更新
def check_for_updates():
    global function_executed
    if function_executed:
        return
    # 检查是否游戏处于重启中，如果没有在重启中，则检查更新，防止崩溃重启脚本时卡在此步骤
    is_game_restarting_file = os.path.join(config.user_data_root, "isRestarting.dat")
    os.makedirs(os.path.dirname(is_game_restarting_file), exist_ok=True)
    if os.path.exists(is_game_restarting_file):
        function_executed = True
        return
    local_version_info = get_local_version_info()
    github_version_info = get_github_version_info()
    print("\n")  # 换行以免继续打印在logger()函数的信息后面
    if local_version_info and github_version_info:
        local_version = local_version_info['版本']
        github_version = github_version_info['版本']
        if local_version < github_version:
            print(f"有新版本可用: {github_version} (本地版本: {local_version})")
            print(f"更新日期: {github_version_info['更新日期']}")
            print(f"描述: {github_version_info['描述']}")
            print("更新内容:")
            print(github_version_info['更新内容'])
            # 提示用户是否更新
            user_input = input(f"需要从{repo_type}下载最新版本吗? (y/n): ").strip().lower()
            if user_input == 'y':
                print(f"使用{config.UpdateType}更新中...\n")
                if config.UpdateType == "Download":
                    update_download_file(github_version)
                elif config.UpdateType == "Git":
                    print("正在检查Git是否已经安装")
                    is_git_installed = check_git_installed()
                    if is_git_installed:
                        print("Git已安装，执行更新")
                    else:
                        print("Git未安装，尝试安装Git")
                        install_result = install_git()
                        if not install_result:
                            print(f"安装Git失败，请手动安装Git后重试更新。{msg}")
                        else:
                            reload_env_vars()
                    if is_git_repo():
                        update_git_pull()
                    else:
                        if repo_type == "Github":
                            repo_url = f"https://github.com/{owner}/{repo}/tree/{branch}.git"
                        elif repo_type == "Gitee":
                            repo_url = f"https://gitee.com/{owner}/{repo}.git"
                        else:
                            print(f"使用仓库设置不正确。{msg}")
                            function_executed = True
                            return
                        repo_path = root_path
                        git_clone(repo_url, repo_path)
                else:
                    print("未设置更新方式")
            else:
                input(f"用户取消更新。{msg}")
        elif local_version > github_version:
            input(f"您正在使用的版本高于{repo_type}上的版本，可能不是{branch}分支的版本。{msg}")
        else:
            input(f"已经是最新版本({github_version})。{msg}")
    else:
        input(f"网络问题无法获取版本信息。{msg}")
    function_executed = True
