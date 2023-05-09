#  Copyright (c) 2023, Guanghui Liang. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
required packages:
    pip3 install python-gitlab
    pip3 install gitpython
"""

import difflib
import getopt
import getpass
import os
import re
import sys
import time
import git
import gitlab
import configparser
import sendFeishuBotMessage
from loadingAnimation import LoadingAnimation

PODFILE = 'Podfile'
COMMIT_CONFIRM_PROMPT = '''
请确认将要用于生成 merge request 的提交:
    message: {message}
    author: {author}
    authored_date: {authored_date}
'''


def get_root_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    elif __file__:
        return os.path.dirname(__file__)


def make_question(prompt: str, expect_answers: [str] = None):
    """
    获取终端输入
    :param prompt: 提示语
    :param expect_answers: 有效答案
    :return: 有效答案中的其中一个。如果用户直接回车，则返回有效答案中的第一个
    """
    valid = False
    expect_answers = expect_answers if (expect_answers is not None) else []
    while not valid:
        answer = input(prompt)
        if (answer in expect_answers) or len(answer) == 0 or (len(expect_answers) == 0 and len(answer) > 0):
            valid = True
            return answer \
                if (len(answer) > 0) \
                else (expect_answers[0] if (expect_answers is not None) and len(expect_answers) > 0 else '')


def print_step(*values, sep=' ', end='\n', file=None):
    _values = ('❖',) + values
    print(*_values, sep=sep, end=end, file=file)


class CommitHelper:
    @classmethod
    def get_changed_lines(cls, commit: git.Commit, file: str = PODFILE) -> [str]:
        _changed_lines = []

        # 找到跟 file 相关的文件，例如 ExamplePod/Podfile
        relative_paths = []
        for _diff in commit.diff(commit.parents[0]):
            if file in _diff.a_blob.path:
                relative_paths.append(_diff.a_blob.path)

        for path in relative_paths:
            blob = commit.tree[path].data_stream.read().decode()
            parent_blob = commit.parents[0].tree[path].data_stream.read().decode()
            diff = difflib.unified_diff(parent_blob.splitlines(), blob.splitlines(), lineterm='', n=0)
            for line in diff:
                if line.startswith('+'):
                    _changed_lines.append(line)

        return _changed_lines

    @classmethod
    def get_last_commit(cls, repo: git.Repo) -> git.Commit:
        last_commit = repo.head.commit
        if len(last_commit.message) == 0:
            last_commit = last_commit.parents[0]
        return last_commit


class MRHelper:
    def __init__(self):
        self.gitlab = gitlab.Gitlab.from_config('Keep', [get_root_path() + '/MRConfig.ini'])
        self.repo = git.Repo(os.getcwd(), search_parent_directories=True)
        self.current_proj = self.get_gitlab_project(self.get_repo_name(self.repo))
        self.last_commit = CommitHelper.get_last_commit(self.repo)

    @classmethod
    def get_repo_name(cls, repo: git.Repo) -> str:
        local_name = repo.working_tree_dir.split('/')[-1]
        url_name = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
        if len(url_name) > 0:
            return url_name
        else:
            return local_name

    def get_relative_mr(self, repo_url: str, commit: str) -> str | None:
        repo_name = repo_url.split('.git')[0].split('/')[-1]
        proj = self.get_gitlab_project(repo_name)
        mr_list = proj.mergerequests.list(state='merged', order_by='updated_at', get_all=True)
        for mr in mr_list:
            commit_list = [commit.id for commit in mr.commits()]
            if commit in commit_list:
                return mr.web_url

        # 没有找到对应的 MR，则直接返回 commit 对应的链接
        return proj.commits.get(commit).web_url

    @classmethod
    def get_formatted_time(cls, seconds) -> str:
        return time.strftime('%a, %d %b %Y %H:%M', time.gmtime(seconds))

    def get_gitlab_project(self, keyword: str):
        for proj in self.gitlab.projects.list(get_all=True):
            if proj.name == keyword:
                return proj
        return self.gitlab.projects.list(search=keyword, get_all=True)[0]

    def check_has_uncommitted_changes(self) -> bool:
        return self.repo.is_dirty(untracked_files=True)

    def create_merge_request(self):
        if self.check_has_uncommitted_changes():
            raise SystemExit('⚠️有未提交的更改！')
        else:
            # 确认用于生成 MR 的提交
            print(COMMIT_CONFIRM_PROMPT
                  .format(message=self.last_commit.message.strip(),
                          author=self.last_commit.author,
                          authored_date=self.get_formatted_time(self.last_commit.authored_date))
                  .rstrip())
            commit_confirm = make_question('请输入 y(回车)/n: ', ['y', 'n'])
            if commit_confirm == 'n':
                raise SystemExit('取消生成 merge request')

            # 输入目标分支
            mr_target_br = make_question('请输入 MR 目标分支（直接回车会使用默认主分支）:')
            if len(mr_target_br) == 0:
                mr_target_br = 'master' \
                    if ('origin/master' in [ref.name for ref in self.repo.remote().refs]) \
                    else 'main'
            print_step(f'目标分支: {mr_target_br}')

            # 输入 MR 标题
            mr_title = make_question('请输入 MR 标题（直接回车会使用上述提交的 message）:')
            if len(mr_title) == 0:
                mr_title = self.last_commit.message.split('\n')[0]
            print_step(f'message: {mr_title}')

            # 获取关联 MR
            LoadingAnimation.sharedInstance.showWith('处理 Podfile, 获取相关组件库 merge request 中...',
                                                     finish_message='组件库 merge request 处理完成✅',
                                                     failed_message='组件库 merge request 处理失败❌')
            file_changed_lines: [str] = CommitHelper.get_changed_lines(CommitHelper.get_last_commit(self.repo), PODFILE)
            relative_pod_mrs: [str] = []
            for line in file_changed_lines:
                line = re.sub('\s+', '', line)  # 去掉空格，方便提取
                commit_result: [str] = re.findall(r":commit=>\"(.+?)\"", line.replace('\'', '"'))
                url_result: [str] = re.findall(r":git=>\"(.+?)\"", line.replace('\'', '"'))
                if len(commit_result) and len(url_result):
                    mr_url = helper.get_relative_mr(url_result[0], commit_result[0])
                    if mr_url is not None:
                        relative_pod_mrs.append(mr_url)
                    else:
                        # 无法获取对应的 MR 链接，直接获取 commit 的链接
                        pod_repo_name = url_result[0].split('.git')[0].split('/')[-1]
                        pod_commit = helper.get_gitlab_project(pod_repo_name).commits.get(commit_result[0])
                        relative_pod_mrs.append(pod_commit.web_url)
            LoadingAnimation.sharedInstance.finished = True

            description = ''
            if len(relative_pod_mrs) > 0:
                description += "<p>相关组件库提交:</p>"
            for relative_url in relative_pod_mrs:
                description += "<p>" + "    👉: " + relative_url + "</p>"
            if len(description):
                print_step('自动填写 description: ', str(description.replace('<p>', '\n').replace('</p>', '\n')))

            source_branch = self.repo.head.ref.name
            original_source_branch = source_branch
            print_step('当前分支: ', source_branch)

            # 如果当前在主分支，则切换分支
            # if source_branch in ['main', 'master', 'release', 'release_copy']:
            username = getpass.getuser()
            _time = str(int(time.time()))
            source_branch = username + '/mr' + _time
            self.repo.git.checkout('-b', source_branch)
            print_step('自动切换到分支: ', source_branch)

            print_step(f'将分支 {source_branch} push 到 remote')
            # self.repo.git.push('origin', source_branch)
            # 生成 MR。当用户对某些仓库没有管理权限时，使用 gitlab-python 内置的创建 MR 方法会失败，因此使用 shell 指令创建 MR
            cmd = f"git push " \
                  f"-o merge_request.create " \
                  f"-o merge_request.target={mr_target_br} " \
                  f"-o merge_request.title=\"{mr_title}\" " \
                  f"--set-upstream origin {source_branch} "

            os.system(f'{cmd} >/dev/null 2>&1')
            time.sleep(1)   # 等待
            LoadingAnimation.sharedInstance.showWith('获取 merge request 并修改 description 中...',
                                                     finish_message='Done✅',
                                                     failed_message='')
            merge_request_url = ''
            mr_list = self.current_proj.mergerequests.list(state='opened', order_by='updated_at', get_all=True)
            for mr in mr_list:
                commit_list = [commit.id for commit in mr.commits()]
                if self.last_commit.hexsha in commit_list:
                    merge_request_url = mr.web_url
                    mr.description = description
                    mr.save()

            LoadingAnimation.sharedInstance.finished = True

            print_step(f'删除本地分支 {source_branch}，并切换到原分支 {original_source_branch}')
            self.repo.git.checkout(original_source_branch)
            self.repo.delete_head(source_branch)

            if len(merge_request_url) > 0:
                print_step(f'merge request 创建成功，链接: \n    {merge_request_url}')
                print('')
                sendFeishuBotMessage.send_feishubot_message(merge_request_url, author=str(self.last_commit.author), message=self.last_commit.message.strip())
            else:
                raise SystemExit('merge request 创建失败！')


def get_config_new_value(key: str, section: str, config: configparser.ConfigParser) -> str:
    if key in config[section] and len(config[section][key]) > 0:
        return config[section][key]
    else:
        return ''


def create_config_file():
    path = get_root_path() + '/MRConfig.ini'
    if os.path.exists(path):
        current_config = configparser.ConfigParser()
        current_config.read(path)
        section = current_config.sections()[0]
        current_config[section]['url'] = 'https://gitlab.gotokeep.com'
        current_config[section]['private_token'] = get_config_new_value('private_token', section, current_config)
        current_config[section]['api_version'] = '4'
        current_config[section]['send_feishubot_message'] = get_config_new_value('send_feishubot_message', section, current_config)
        current_config[section]['feishu_bot_webhook'] = get_config_new_value('feishu_bot_webhook', section, current_config)
        current_config[section]['feishu_bot_@_user_openid'] = get_config_new_value('feishu_bot_@_user_openid', section, current_config)
        with open(path, 'w') as configfile:
            current_config.write(configfile)
    else:
        f = open(get_root_path() + '/MRConfig.ini', 'w')
        f.seek(0)
        f.truncate()
        f.write("""
[Keep]
url = https://gitlab.gotokeep.com
private_token = *****
api_version = 4
send_feishubot_message = no
feishu_bot_webhook = 
feishu_bot_@_user_openid = 
            """.strip())
        f.close()
    raise SystemExit('配置文件创建成功')


if __name__ == '__main__':
    # 创建配置文件
    opts, args = getopt.getopt(sys.argv, "", ["--init"])
    if '--init' in args:
        create_config_file()

    # 创建 merge request
    LoadingAnimation.sharedInstance.showWith('获取仓库配置中，需要联网，请耐心等待...', finish_message='仓库配置获取完成✅', failed_message='仓库配置获取失败❌')
    try:
        helper = MRHelper()
    except Exception as e:
        LoadingAnimation.sharedInstance.failed = True
        time.sleep(0.2)
        raise SystemExit()
    LoadingAnimation.sharedInstance.finished = True
    helper.create_merge_request()

    # DEBUG
    # changed_lines = CommitHelper.get_changed_lines(helper.last_commit, PODFILE)
    # print(changed_lines)
    # relative_pod_mrs: [str] = []
    # for line in changed_lines:
    #     line = re.sub('\s+', '', line)  # 去掉空格，方便提取
    #     commit_result: [str] = re.findall(r":commit=>\"(.+?)\"", line)
    #     url_result: [str] = re.findall(r":git=>\"(.+?)\"", line.replace('\'', '"'))
    #     if len(commit_result) and len(url_result):
    #         repo_name = url_result[0].split('.git')[0].split('/')[-1]
    #         commit = helper.get_gitlab_project(repo_name).commits.get(commit_result[0])
    #         print(commit.web_url)
