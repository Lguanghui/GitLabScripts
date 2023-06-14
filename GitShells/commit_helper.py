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

import difflib
import git.diff
from git import Commit, Repo
from typing import Union


class CommitHelper:
    @classmethod
    def get_diff_changed_lines(cls, file_diff: git.diff.Diff) -> [str]:
        if file_diff is None:
            return []
        _changed_lines = []
        diff = difflib.unified_diff(file_diff.a_blob.data_stream.read().decode().splitlines(),
                                    file_diff.b_blob.data_stream.read().decode().splitlines(),
                                    lineterm='',
                                    n=0)
        for line in diff:
            if line.startswith('+'):
                _changed_lines.append(line)

        return _changed_lines

    @classmethod
    def get_branches_file_diff(cls, t_repo: git.Repo,
                               file_name: str,
                               target_branch_name: str,
                               source_branch_name: str = '') -> git.diff.Diff | None:
        """
        获取指定文件在两个分支上的 diff
        :param t_repo: 仓库
        :param file_name: 文件名
        :param target_branch_name: 目标分支
        :param source_branch_name: 源分支
        :return: diff
        """
        # last commit of source branch
        feature_branch: Union[git.Tree, git.Commit, None, str, object]
        if source_branch_name is None or len(source_branch_name) == 0:
            feature_branch = t_repo.head.commit.tree
        else:
            feature_branch = t_repo.commit(source_branch_name)
        # last commit of target branch
        target_branch = t_repo.commit(target_branch_name)

        # comparing
        _diff = target_branch.diff(feature_branch)
        _file = None

        # collect new files
        for file_diff in _diff.iter_change_type('A'):
            if file_diff.b_blob is not None and file_diff.b_blob.name == file_name:
                _file = file_diff

        # collect deleted files
        for file_diff in _diff.iter_change_type('D'):
            if file_diff.b_blob is not None and file_diff.b_blob.name == file_name:
                _file = file_diff

        # collect modified files
        for file_diff in _diff.iter_change_type('M'):
            # file.a_blob.name
            if file_diff.b_blob is not None and file_diff.b_blob.name == file_name:
                _file = file_diff

        return _file

    @classmethod
    def get_changed_lines(cls, commit: Commit, t_file: str) -> [str]:
        _changed_lines = []

        # 找到跟 file 相关的文件，例如 ExamplePod/Podfile
        relative_paths = []
        for _diff in commit.diff(commit.parents[0]):
            if _diff.a_blob is None:
                continue
            if t_file in _diff.a_blob.path:
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
    def get_last_commit(cls, repo: Repo) -> Commit:
        last_commit = repo.head.commit
        if len(last_commit.message) == 0:
            last_commit = last_commit.parents[0]
        return last_commit


if __name__ == '__main__':
    pass
    # repo = Repo("/Users/liangguanghui/keep/ios")
    #
    # # last commit of source branch
    # commit_feature_branch = repo.head.commit.tree
    # # last commit of target branch
    # commit_target_branch = repo.commit("script_test_dev")
    # # commit_target_branch = repo.commit("origin/master")
    #
    # new_files = []
    # deleted_files = []
    # modified_files = []
    #
    # # comparing
    # diff_index = commit_target_branch.diff(commit_feature_branch)
    #
    # # collect new files
    # for file in diff_index.iter_change_type('A'):
    #     new_files.append(file)
    #
    # # collect deleted files
    # for file in diff_index.iter_change_type('D'):
    #     deleted_files.append(file)
    #
    # podfile: git.diff.Diff
    # # collect modified files
    # for file in diff_index.iter_change_type('M'):
    #     modified_files.append(file)
    #     # file.a_blob.name
    #     if file.b_blob.name == "Podfile":
    #         podfile = file
    #         print("找到被修改的 Podfile")
    #         changed_lines = CommitHelper.get_diff_changed_lines(file_diff=file)
    #         for line in changed_lines:
    #             print(f"\033[93m {line}\33[0m")
    #
    # print("all new files: ", new_files)
    # print("all deleted files: ", deleted_files)
    # print("all modified files: ", modified_files)
