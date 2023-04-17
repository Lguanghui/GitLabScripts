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
import time
import re
import gitlab
import difflib
import git
import os
import getpass

PODFILE = 'Podfile'
PY_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

COMMIT_CONFIRM_PROMPT = '''
请确认将要用于生成 merge request 的提交:
    message: {message}
    author: {author}
    authored_date: {authored_date}
'''


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


class CommitHelper:
    @classmethod
    def get_changed_lines(cls, commit: git.Commit, file: str = PODFILE) -> [str]:
        changed_lines = []
        if commit.tree.__contains__(file) and commit.parents[0].tree.__contains__(file):
            blob = commit.tree[file].data_stream.read().decode()
            parent_blob = commit.parents[0].tree[file].data_stream.read().decode()
            diff = difflib.unified_diff(blob.splitlines(), parent_blob.splitlines(), lineterm='', n=0)
            for line in diff:
                if line.startswith('+'):
                    changed_lines.append(line)
        return changed_lines

    @classmethod
    def get_last_commit(cls, repo: git.Repo) -> git.Commit:
        last_commit = repo.head.commit
        if len(last_commit.message) == 0:
            last_commit = last_commit.parents[0]
        return last_commit


class MRHelper:
    def __init__(self):
        self.gitlab = gitlab.Gitlab.from_config('Keep', [PY_FILE_DIR + '/MRConfig.ini'])
        self.repo = git.Repo(os.getcwd(), search_parent_directories=True)
        self.current_proj = self.get_gitlab_project(self.get_repo_name(self.repo))
        self.last_commit = CommitHelper.get_last_commit(self.repo)

    @classmethod
    def get_repo_name(cls, repo: git.Repo) -> str:
        local_name = repo.working_tree_dir.split('/')[-1]
        if len(local_name) > 0:
            return local_name
        else:
            return repo.remotes.origin.url.split('.git')[0].split('/')[-1]

    def get_relative_mr(self, repo_url: str, commit: str) -> str | None:
        repo_name = repo_url.split('.git')[0].split('/')[-1]
        proj = self.get_gitlab_project(repo_name)
        mr_list = proj.mergerequests.list(state='merged', order_by='updated_at')
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
            print(f'目标分支: {mr_target_br}')

            # 输入 MR 标题
            mr_title = make_question('请输入 MR 标题（直接回车会使用上述提交的 message）:')
            if len(mr_title) == 0:
                mr_title = self.last_commit.message.split('\n')[0]

            # 获取关联 MR
            changed_lines: [str] = CommitHelper.get_changed_lines(CommitHelper.get_last_commit(self.repo), PODFILE)
            relative_pod_mrs: [str] = []
            for line in changed_lines:
                line = re.sub('\s+', '', line)  # 去掉空格，方便提取
                commit_result: [str] = re.findall(r":commit=>\"(.+?)\"", line)
                url_result: [str] = re.findall(r":git=>\"(.+?)\"", line)
                if len(commit_result) and len(url_result):
                    mr_url = self.get_relative_mr(url_result[0], commit_result[0])
                    if mr_url is not None:
                        relative_pod_mrs.append(mr_url)
            # print(relative_pod_mrs)
            for relative_url in relative_pod_mrs:
                mr_title += '\n' + '    👉:' + relative_url
            print(f'message: {mr_title}')

            source_branch = self.repo.head.ref.name
            original_source_branch = source_branch
            print('当前分支: ', source_branch)

            # 如果当前在主分支，则切换分支
            # if source_branch in ['main', 'master', 'release', 'release_copy']:
            username = getpass.getuser()
            _time = str(int(time.time()))
            source_branch = username + '/mr' + _time
            self.repo.git.checkout('-b', source_branch)
            print('自动切换到分支: ', source_branch)

            print(f'将分支 {source_branch} push 到 remote')
            self.repo.git.push('origin', source_branch)

            print(f'删除本地分支 {source_branch}，并切换到原分支 {original_source_branch}')
            self.repo.git.checkout(original_source_branch)
            self.repo.delete_head(source_branch)

            # 生成 MR
            new_mr = self.current_proj.mergerequests.create({'source_branch': source_branch,
                                                             'target_branch': mr_target_br,
                                                             'title': mr_title})

            print(f'merge request 创建成功，URL: {new_mr.web_url}')


if __name__ == '__main__':
    helper = MRHelper()
    helper.create_merge_request()