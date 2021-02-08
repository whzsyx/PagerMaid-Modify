""" Pulls in the new version of PagerMaid from the git server. """

import platform
from subprocess import run, PIPE
from datetime import datetime
from os import remove
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pyrogram import Client, filters
from main import cmd, par, des, prefix_str
from modules.system import execute

cmd.extend(['update'])
par.extend(['<true/debug>'])
des.extend(['从远程来源检查更新，并将其安装到 PagerMaid-Modify。'])


@Client.on_message(filters.me & filters.command('update', list(prefix_str)))
async def update(client, message):
    if len(message.text.split()) > 2:
        await message.edit("无效的参数。")
        return
    await message.edit("正在检查远程源以进行更新 . . .")
    parameter = None
    if len(message.text.split()) == 2:
        parameter = message.text.split()[1]
    repo_url = 'https://github.com/xtaodada/PagerMaid-Modify.git'

    if parameter:
        if parameter == "debug":
            # Version info
            git_version = run("git --version", stdout=PIPE, shell=True).stdout.decode().strip().replace("git version ",
                                                                                                        "")
            git_change = bool(run("git diff-index HEAD --", stdout=PIPE, shell=True).stdout.decode().strip())
            git_change = "是" if git_change else "否"
            git_date = run("git log -1 --format='%at'", stdout=PIPE, shell=True).stdout.decode()
            git_date = datetime.utcfromtimestamp(int(git_date.replace('\n', '').replace("'", ''))).strftime("%Y/%m/%d %H:%M:%S")
            git_hash = run("git rev-parse --short HEAD", stdout=PIPE, shell=True).stdout.decode().strip()
            get_hash_link = f"https://github.com/xtaodada/PagerMaid-Modify/commit/{git_hash}"
            # Generate the text
            text = "系统名称及版本号：`" + str(platform.platform()) + "`\n系统版本号：`" + str(platform.version()) + "`\n系统位数：`" + \
                   platform.architecture()[0] + "`\nPython 版本号：`" + str(
                platform.python_version()) + "`\n\nGit 版本号：`" + git_version + "`\n本地修改：" + git_change + "\n哈希值：[" + \
                   git_hash + "](" + get_hash_link + ")\n提交时间：`" + git_date + "`"
            await message.edit(text, disable_web_page_preview=True)
            return

    try:
        repo = Repo()
    except NoSuchPathError as exception:
        await message.edit(f"出错了呜呜呜 ~ 目录 {exception} 不存在。")
        return
    except InvalidGitRepositoryError:
        await message.edit(f"此 PagerMaid-Modify 实例不是从源安装,"
                           f" 请通过您的本机软件包管理器进行升级。")
        return
    except GitCommandError as exception:
        await message.edit(f'出错了呜呜呜 ~ 收到了来自 git 的错误: `{exception}`')
        return

    active_branch = repo.active_branch.name
    if not await branch_check(active_branch):
        await message.edit(
            f"出错了呜呜呜 ~ 该分支未维护: {active_branch}.")
        return

    try:
        repo.create_remote('upstream', repo_url)
    except BaseException:
        pass

    upstream_remote = repo.remote('upstream')
    upstream_remote.fetch(active_branch)
    changelog = await changelog_gen(repo, f'HEAD..upstream/{active_branch}')

    if not parameter:
        if not changelog:
            await message.edit(f"`PagerMaid-Modify 在分支 ` **{active_branch}**` 中已是最新。`")
            return
        changelog_str = f'**找到分支 {active_branch} 的更新.\n\n更新日志:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await message.edit("更新日志太长，正在附加文件。")
            file = open("output.log", "w+")
            file.write(changelog_str)
            file.close()
            await client.send_document(
                message.chat.id,
                "output.log",
                reply_to_message_id=message.message_id,
            )
            remove("output.log")
        else:
            await message.edit(changelog_str + "\n**执行 \"" + prefix_str[0] + "update true\" 来安装更新。**")
        return

    await message.edit('找到更新，正在拉取 . . .')

    try:
        try:
            upstream_remote.pull(active_branch)
        except:
            await execute(
                """git status | grep modified | sed -r "s/ +/ /" | cut -f2 | awk -F " " '{print "mkdir -p $(dirname 
                ../for-update/" $2 ") && mv " $2 " ../for-update/" $2}' | sh""")
            await execute("git pull")
            await execute(
                """cd ../for-update/ && find -H . -type f | awk '{print "cp " $1 " ../PagerMaid-Modify/" $1}' | sh && cd ../PagerMaid-Modify""")
            await execute("rm -rf ../for-update/")
        await execute("python3 -m pip install -r requirements.txt --upgrade")
        await execute("python3 -m pip install -r requirements.txt")
        await message.edit(
            '更新成功，PagerMaid-Modify 正在重新启动。'
        )
        exit()
    except GitCommandError:
        upstream_remote.git.reset('--hard')
        await message.edit(
            '更新时出现错误，PagerMaid-Modify 正在重新启动。'
        )
        exit()


async def changelog_gen(repo, diff):
    result = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        result += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return result


async def branch_check(branch):
    official = ['master', 'beta']
    if branch in official:
        return 1
    return
