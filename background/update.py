# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: ocr.py
@time: 2024/7/18 上午3:11
@author RoseRin0
"""
import requests
import base64
import re
import os
from config import config, root_path, wait_exit
from version import __version__, release_date, description

# GitHub 项目信息
owner = 'RoseRin0'
repo = 'mc_auto_boss'
version_file_path = 'background/version.py'
branch = 'RoseRin'  # 指定分支名称


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
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{version_file_path}?ref={branch}'
    headers = {'Accept': 'application/vnd.github+json'}
    response = requests.get(url, headers=headers)
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
                # 去除每行前面的
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


# 比较版本号并提示更新
def check_for_updates():
    # 检查是否游戏处于重启中，如果没有在重启中，则检查更新，防止崩溃重启脚本时卡在此步骤
    is_game_restarting_file = os.path.join(config.user_data_root, "isRestarting.dat")
    os.makedirs(os.path.dirname(is_game_restarting_file), exist_ok=True)
    if os.path.exists(is_game_restarting_file):
        return
    local_version_info = get_local_version_info()
    github_version_info = get_github_version_info()
    msg = "请按任意键继续运行脚本"
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
            user_input = input("需要下载最新版本吗? (y/n): ").strip().lower()
            if user_input == 'y':
                print("更新中...")
                new_version_file_name = f"mc_auto_boss_v{github_version}.zip"
                file_url = f'https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip'
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
            else:
                input(f"用户取消更新。{msg}")
        elif local_version > github_version:
            input(f"您正在使用的版本高于Github上的版本，可能不是{branch}分支的版本。{msg}")
        else:
            input(f"已经是最新版本。{msg}")
    else:
        input(f"网络问题无法获取版本信息。{msg}")