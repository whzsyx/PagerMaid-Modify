""" PagerMaid module to manage plugins. """

import json
from re import search, I
from requests import get
from os import remove, rename, chdir, path, getcwd, makedirs
from os.path import exists, basename, isfile
from sys import exit
from shutil import copyfile, move
from glob import glob
from pyrogram import Client, filters
from main import cmd, par, des, prefix_str

working_dir = getcwd()


def move_plugin(file_path):
    plugin_directory = f"{working_dir}/modules/plugins/"
    if exists(f"{plugin_directory}{file_path}"):
        remove(f"{plugin_directory}{file_path}")
        move(file_path, plugin_directory)
    elif exists(f"{plugin_directory}{file_path}.disabled"):
        remove(f"{plugin_directory}{file_path}.disabled")
        move(file_path, f"{plugin_directory}{file_path}.disabled")
    else:
        move(file_path, plugin_directory)


def update_version(file_path, plugin_content, plugin_name, version):
    plugin_directory = f"{working_dir}/modules/plugins/"
    with open(file_path, 'wb') as f:
        f.write(plugin_content)
    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
        version_json = json.load(f)
        version_json[plugin_name] = version
    with open(f"{plugin_directory}version.json", 'w') as f:
        json.dump(version_json, f)


def __list_plugins():
    plugin_paths = glob(f"{getcwd()}/modules/plugins" + "/*.py")
    if not exists(f"{getcwd()}/modules/plugins"):
        makedirs(f"{getcwd()}/modules/plugins")
    result = [
        basename(file)[:-3]
        for file in plugin_paths
        if isfile(file) and file.endswith(".py") and not file.endswith("__init__.py")
    ]
    return result


async def upload_attachment(client, file_path, chat_id, reply_id, caption=None):
    """ Uploads a local attachment file. """
    if not exists(file_path):
        return False
    try:
        await client.send_document(
            chat_id,
            file_path,
            reply_to_message_id=reply_id,
            caption=caption
        )
    except BaseException as exception:
        raise exception
    return True


cmd.extend(['apt'])
par.extend(['{update|search|show|status|install|remove|enable|disable|upload} <插件名称/文件>'])
des.extend(['用于管理安装到 PagerMaid-Modify 的插件。'])
active_plugins = sorted(__list_plugins())


@Client.on_message(filters.me & filters.command('apt', list(prefix_str)))
async def plugin(client, message):
    if len(message.text.split()) == 1:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    reply = message.reply_to_message
    plugin_directory = f"{working_dir}/modules/plugins/"
    if message.text.split()[1] == "install":
        if len(message.text.split()) == 2:
            await message.edit("安装插件中 . . .")
            if reply:
                file_path = await client.download_media(reply)
            else:
                file_path = await message.download_media()
            if file_path is None or not file_path.endswith('.py'):
                await message.edit("出错了呜呜呜 ~ 无法从附件获取插件文件。")
                try:
                    remove(str(file_path))
                except FileNotFoundError:
                    pass
                return
            move_plugin(file_path)
            await message.edit(f"插件 {path.basename(file_path)[:-3]} 已安装，PagerMaid-Modify 正在重新启动。")
            exit()
        elif len(message.text.split()) >= 3:
            await message.edit("安装插件中 . . .")
            success_list = []
            failed_list = []
            noneed_list = []
            for x in range(len(message.text.split()) - 2):
                plugin_name = message.text.split()[2 + x]
                plugin_online = \
                    json.loads(
                        get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/list.json").content)[
                        'list']
                if exists(f"{plugin_directory}version.json"):
                    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                        version_json = json.load(f)
                    try:
                        plugin_version = version_json[plugin_name]
                    except:
                        plugin_version = False
                else:
                    temp_dict = {}
                    with open(f"{plugin_directory}version.json", 'w') as f:
                        json.dump(temp_dict, f)
                    plugin_version = False
                flag = False
                for i in plugin_online:
                    if i['name'] == plugin_name:
                        flag = True
                        if plugin_version:
                            if (float(i['version']) - float(plugin_version)) <= 0:
                                noneed_list.append(plugin_name)
                                break
                            else:
                                file_path = plugin_name + ".py"
                                plugin_content = get(
                                    f"https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/"
                                    f"{plugin_name}.py").content
                                update_version(file_path, plugin_content, plugin_name, i['version'])
                                move_plugin(file_path)
                                success_list.append(path.basename(file_path)[:-3])
                                break
                        else:
                            file_path = plugin_name + ".py"
                            plugin_content = get(
                                f"https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/"
                                f"{plugin_name}.py").content
                            update_version(file_path, plugin_content, plugin_name, i['version'])
                            move_plugin(file_path)
                            success_list.append(path.basename(file_path)[:-3])
                if not flag:
                    failed_list.append(plugin_name)
            msg = ""
            if len(success_list) > 0:
                msg += "安装成功 : %s\n" % ", ".join(success_list)
            if len(failed_list) > 0:
                msg += "安装失败 : %s\n" % ", ".join(failed_list)
            if len(noneed_list) > 0:
                msg += "无需更新 : %s\n" % ", ".join(noneed_list)
            restart = len(success_list) > 0
            if restart:
                msg += "PagerMaid-Modify 正在重启。"
            await message.edit(msg)
            if restart:
                exit()
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "remove":
        if len(message.text.split()) == 3:
            if exists(f"{plugin_directory}{message.text.split()[2]}.py"):
                remove(f"{plugin_directory}{message.text.split()[2]}.py")
                with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                    version_json = json.load(f)
                version_json[message.text.split()[2]] = '0.0'
                with open(f"{plugin_directory}version.json", 'w') as f:
                    json.dump(version_json, f)
                await message.edit(f"成功删除插件 {message.text.split()[2]}, PagerMaid-Modify 正在重新启动。")
                exit()
            elif exists(f"{plugin_directory}{message.text.split()[2]}.py.disabled"):
                remove(f"{plugin_directory}{message.text.split()[2]}.py.disabled")
                with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                    version_json = json.load(f)
                version_json[message.text.split()[2]] = '0.0'
                with open(f"{plugin_directory}version.json", 'w') as f:
                    json.dump(version_json, f)
                await message.edit(f"已删除的插件 {message.text.split()[2]}.")
            elif "/" in message.text.split()[2]:
                await message.edit("出错了呜呜呜 ~ 无效的参数。")
            else:
                await message.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "status":
        if len(message.text.split()) == 2:
            inactive_plugins = sorted(__list_plugins())
            disabled_plugins = []
            if not len(inactive_plugins) == 0:
                for target_plugin in active_plugins:
                    inactive_plugins.remove(target_plugin)
            chdir("modules/plugins/")
            for target_plugin in glob(f"*.py.disabled"):
                disabled_plugins += [f"{target_plugin[:-12]}"]
            chdir(working_dir)
            active_plugins_string = ""
            inactive_plugins_string = ""
            disabled_plugins_string = ""
            for target_plugin in active_plugins:
                active_plugins_string += f"{target_plugin}, "
            active_plugins_string = active_plugins_string[:-2]
            for target_plugin in inactive_plugins:
                inactive_plugins_string += f"{target_plugin}, "
            inactive_plugins_string = inactive_plugins_string[:-2]
            for target_plugin in disabled_plugins:
                disabled_plugins_string += f"{target_plugin}, "
            disabled_plugins_string = disabled_plugins_string[:-2]
            if len(active_plugins) == 0:
                active_plugins_string = "`没有运行中的插件。`"
            if len(inactive_plugins) == 0:
                inactive_plugins_string = "`没有加载失败的插件。`"
            if len(disabled_plugins) == 0:
                disabled_plugins_string = "`没有关闭的插件`"
            output = f"**插件列表**\n" \
                     f"运行中: {active_plugins_string}\n" \
                     f"已关闭: {disabled_plugins_string}\n" \
                     f"加载失败: {inactive_plugins_string}"
            await message.edit(output)
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "enable":
        if len(message.text.split()) == 3:
            if exists(f"{plugin_directory}{message.text.split()[2]}.py.disabled"):
                rename(f"{plugin_directory}{message.text.split()[2]}.py.disabled",
                       f"{plugin_directory}{message.text.split()[2]}.py")
                await message.edit(f"插件 {message.text.split()[2]} 已启用，PagerMaid-Modify 正在重新启动。")
                exit()
            else:
                await message.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "disable":
        if len(message.text.split()) == 3:
            if exists(f"{plugin_directory}{message.text.split()[2]}.py") is True:
                rename(f"{plugin_directory}{message.text.split()[2]}.py",
                       f"{plugin_directory}{message.text.split()[2]}.py.disabled")
                await message.edit(f"插件 {message.text.split()[2]} 已被禁用，PagerMaid-Modify 正在重新启动。")
                exit()
            else:
                await message.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "upload":
        if len(message.text.split()) == 3:
            file_name = f"{message.text.split()[2]}.py"
            reply_id = None
            if reply:
                reply_id = reply.message_id
            if exists(f"{plugin_directory}{file_name}"):
                copyfile(f"{plugin_directory}{file_name}", file_name)
            elif exists(f"{plugin_directory}{file_name}.disabled"):
                copyfile(f"{plugin_directory}{file_name}.disabled", file_name)
            if exists(file_name):
                await message.edit("上传插件中 . . .")
                await upload_attachment(client, file_name,message.chat.id, reply_id,
                                        caption=f"PagerMaid-Modify {message.text.split()[2]} plugin.")
                remove(file_name)
                await message.delete()
            else:
                await message.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "update":
        unneed_update = "无需更新："
        need_update = "\n已更新："
        need_update_list = []
        if not exists(f"{plugin_directory}version.json"):
            await message.edit("安装一个仓库内插件再试试？")
            return
        with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
            version_json = json.load(f)
        plugin_online = \
            json.loads(get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/list.json").content)[
                'list']
        for key, value in version_json.items():
            if value == "0.0":
                continue
            for i in plugin_online:
                if key == i['name']:
                    if (float(i['version']) - float(value)) <= 0:
                        unneed_update += "\n`" + key + "`：Ver  " + value
                    else:
                        need_update_list.extend([key])
                        need_update += "\n`" + key + "`：Ver  " + value + " --> Ver  " + i['version']
                    continue
        if unneed_update == "无需更新：":
            unneed_update = ''
        if need_update == "\n已更新：":
            need_update = ''
        if unneed_update == '' and need_update == '':
            await message.edit("不如去安装一些插件？")
        else:
            if len(need_update_list) == 0:
                await message.edit('正在读取云端插件列表...完成\n正在读取本地插件版本信息...完成\n**没有需要更新的插件。**')
            else:
                print(6)
                await message.edit('正在读取云端插件列表...完成\n正在读取本地插件版本信息...完成\n正在更新插件...')
                plugin_directory = f"{working_dir}/modules/plugins/"
                for i in need_update_list:
                    file_path = i + ".py"
                    plugin_content = get(
                        f"https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/{i}.py").content
                    with open(file_path, 'wb') as f:
                        f.write(plugin_content)
                    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                        version_json = json.load(f)
                    for m in plugin_online:
                        if m['name'] == i:
                            version_json[i] = m['version']
                    with open(f"{plugin_directory}version.json", 'w') as f:
                        json.dump(version_json, f)
                    move_plugin(file_path)
                await message.edit('正在读取云端插件列表...完成\n正在读取本地插件版本信息...完成\n' + need_update)
                await message.client.disconnect()
    elif message.text.split()[1] == "search":
        if len(message.text.split()) == 2:
            await message.edit("没插件名我怎么搜索？")
        elif len(message.text.split()) == 3:
            search_result = []
            plugin_name = message.text.split()[2]
            plugin_online = \
                json.loads(
                    get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/list.json").content)[
                    'list']
            for i in plugin_online:
                if search(plugin_name, i['name'], I):
                    search_result.extend(['`' + i['name'] + '` / `' + i['version'] + '`\n  ' + i['des-short']])
            if len(search_result) == 0:
                await message.edit("未在插件仓库中搜索到相关插件。")
            else:
                await message.edit('以下是插件仓库的搜索结果：\n\n' + '\n\n'.join(search_result))
        else:
            await message.edit("出错了呜呜呜 ~ 无效的参数。")
    elif message.text.split()[1] == "show":
        if len(message.text.split()) == 2:
            await message.edit("没插件名我怎么显示？")
        elif len(message.text.split()) == 3:
            search_result = ''
            plugin_name = message.text.split()[2]
            plugin_online = \
                json.loads(
                    get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/beta/list.json").content)[
                    'list']
            for i in plugin_online:
                if plugin_name == i['name']:
                    if i['supported']:
                        search_support = '仍在周期中'
                    else:
                        search_support = '已弃疗'
                    search_result = '插件名：`' + i['name'] + '`\n版本：`Ver  ' + i['version'] + '`\n分类：`' + i[
                        'section'] + '`\n作者：`' + \
                                    i['maintainer'] + '`\n大小：`' + i['size'] + '`\n支持周期：' + search_support + '\n说明：' + i[
                                        'des-short'] + '\n\n' + i['des']
                    break
            if search_result == '':
                await message.edit("未在插件仓库中搜索到相关插件。")
            else:
                await message.edit(search_result)
    else:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
