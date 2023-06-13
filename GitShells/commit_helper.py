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
from git import Commit, Repo


class CommitHelper:
    @classmethod
    def get_changed_lines(cls, commit: Commit, file: str) -> [str]:
        _changed_lines = []

        # 找到跟 file 相关的文件，例如 ExamplePod/Podfile
        relative_paths = []
        for _diff in commit.diff(commit.parents[0]):
            if _diff.a_blob is None:
                continue
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
    def get_last_commit(cls, repo: Repo) -> Commit:
        last_commit = repo.head.commit
        if len(last_commit.message) == 0:
            last_commit = last_commit.parents[0]
        return last_commit
