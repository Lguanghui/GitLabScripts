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
from Utils import debugPrint


class MergeRequestURLFetchThread(threading.Thread):
    """
    获取组件库 merge request url 的线程
    """

    @property
    def project_name(self):
        return self.proj.attributes['name']

    def __init__(self, proj: Project, commit_hash: str, t_queue: queue.Queue):
        super().__init__()
        self.commitHash = commit_hash
        self.queue = t_queue
        self.proj = proj

    def run(self) -> None:
        debugPrint(f"project { self.project_name } 开始获取 merge request")
        debugPrint(f"当前线程：{ threading.current_thread().name } project: {self.project_name}")
        # gitlab API 内部使用了同步操作，所以这里使用多线程的意义不大
        mr_list = self.proj.mergerequests.list(state='merged', order_by='updated_at', get_all=True)
        for mr in mr_list:
            commit_list = [commit.id for commit in mr.commits()]
            if self.commitHash in commit_list:
                self.queue.put(mr.web_url)
                debugPrint(f"project { self.project_name } 拿到 merge request: { mr.web_url }")
                return

        # 没有找到对应的 MR 链接，直接返回 commit 对应的链接
        self.queue.put(self.proj.commits.get(self.commitHash).web_url)
        debugPrint(f"project { self.project_name } 没有拿到 merge request，返回 commit 链接：{self.proj.commits.get(self.commitHash).web_url}")
        return
