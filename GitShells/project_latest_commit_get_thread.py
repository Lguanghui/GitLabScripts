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

import threading
import queue
from gitlab.v4.objects.projects import Project
# from gitlab.v4.objects.commits import ProjectCommit
from Utils import debugPrint
from dataclasses import dataclass
import datetime as dt


@dataclass
class ProjectLatestCommitModel:
    # 当前 commit hash
    current_commit: str = ''
    # 最新 commit hash
    latest_commit: str = ''
    # 最新 commit message
    latest_commit_message: str = ''
    # 仓库名
    project_name: str = ''


class ProjectLatestCommitGetThread(threading.Thread):
    """
    获取组件库最新 commit 的线程
    """

    @property
    def project_name(self):
        return self.proj.attributes['name']

    def __init__(self, proj: Project, current_commit_hash: str, to_queue: queue.Queue):
        """
        初始化线程
        :param proj: gitlab project 实例
        :param current_commit_hash: 当前 commit hash
        :param to_queue: 数据队列
        """
        super().__init__()
        self.current_commit = current_commit_hash
        self.queue = to_queue
        self.proj = proj

    def run(self) -> None:
        debugPrint(f"project { self.project_name } 开始获取最新 commit")
        debugPrint(f"当前线程：{ threading.current_thread().name } project: {self.project_name}")
        since_time = (dt.date.today() - dt.timedelta(days=7)).isoformat()
        commits = self.proj.commits.list(since=since_time)
        if len(commits) > 0:
            latest_commit = commits[0]
            latest_commit_hash: str = latest_commit.id
            latest_commit_message: str = str(latest_commit.message).split('\n')[0]
            debugPrint(f"project { self.project_name } 获取到七天内最新 commit: { latest_commit_hash }")
            self.queue.put(ProjectLatestCommitModel(current_commit=self.current_commit,
                                                    latest_commit=latest_commit_hash,
                                                    latest_commit_message=latest_commit_message,
                                                    project_name=self.project_name))
        return
