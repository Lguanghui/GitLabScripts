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

import numpy as np
import pick
import re
from Utils import debugPrint
from createMR import MRHelper, search_file_path, PODFILE, CommitHelper
from loadingAnimation import LoadingAnimation
from makeQuestion import make_question
from project_latest_commit_get_thread import ProjectLatestCommitModel, ProjectLatestCommitGetThread


def do_lazy_create(helper: MRHelper):
    want_update_models: [ProjectLatestCommitModel] = update_all_project_commit(helper)
    modify_pod_file(want_update_models)
    commit_podfile_changes(helper=helper, messages=[model.latest_commit_message for model in want_update_models])
    helper.last_commit = CommitHelper.get_last_commit(helper.repo)
    helper.create_merge_request()


def update_all_project_commit(helper: MRHelper) -> [ProjectLatestCommitModel]:
    file_path: str = search_file_path(PODFILE)
    latest_commit_threads: [ProjectLatestCommitGetThread] = []

    # 创建 merge request
    LoadingAnimation.sharedInstance.showWith('处理 Podfile 中，请耐心等待...',
                                             finish_message='Podfile 处理完成✅',
                                             failed_message='Podfile 处理失败❌')

    with open(file_path, 'r') as f:
        lines: [str] = f.readlines()
        for line in lines:
            line = re.sub('\s+', '', line)
            project_name, current_commit = helper.get_commit_and_name_from_changed_line(line)
            if len(project_name) and len(current_commit) and ("gotokeep" in line):
                thread = ProjectLatestCommitGetThread(proj=helper.get_gitlab_project(project_name),
                                                      current_commit_hash=current_commit,
                                                      to_queue=helper.queue)
                latest_commit_threads.append(thread)

    LoadingAnimation.sharedInstance.finished = True
    LoadingAnimation.sharedInstance.showWith('获取所有组件库最新 commit 中，请耐心等待...',
                                             finish_message='所有组件库最新 commit 获取完成✅',
                                             failed_message='所有组件库最新 commit 获取失败❌')

    split_arrays = np.array_split(latest_commit_threads, 3)     # 数组拆分，避免开启过多线程，触发警告
    debugPrint(f"所有 project 被拆分为 { len(split_arrays) } 组")
    for threads in split_arrays:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
            debugPrint(f"获取最新 commit 线程 {thread.proj.attributes['name']} 完成")

    LoadingAnimation.sharedInstance.finished = True

    want_update_models: [ProjectLatestCommitModel] = pick_wanted_projects(helper)
    return want_update_models


def pick_wanted_projects(helper: MRHelper) -> [ProjectLatestCommitModel]:
    need_update_models: [ProjectLatestCommitModel] = []

    # 取出队列所有元素
    while not helper.queue.empty():
        item = helper.queue.get()
        if type(item) is ProjectLatestCommitModel:
            item: ProjectLatestCommitModel = item
            if item.current_commit != item.latest_commit:
                need_update_models.append(item)
        else:
            # 不是想要的类型，再放回去
            helper.queue.put(item)

    debugPrint("所有可以更新", need_update_models)
    if len(need_update_models) == 0:
        raise SystemExit("当前没有可更新的组件库")

    # 询问用户
    pick.SYMBOL_CIRCLE_FILLED = '●'
    pick.SYMBOL_CIRCLE_EMPTY = '○'
    options: [str] = [(model.project_name + " " + model.latest_commit_message) for model in need_update_models]
    title = '请从可以更新的组件库中选择你想要更新的组件库(「空格键」选中, 「回车键」结束选择): '
    selected_items = pick.pick(options,
                               title,
                               default_index=0,
                               multiselect=True,
                               min_selection_count=0)

    want_update_models = list(map(lambda x: need_update_models[x[1]], selected_items))

    debugPrint("期望更新", want_update_models)
    return want_update_models


def modify_pod_file(wanted_models: [ProjectLatestCommitModel]):
    file_path: str = search_file_path(PODFILE)
    debugPrint("文件路径", file_path)
    LoadingAnimation.sharedInstance.showWith('修改 Podfile 中...',
                                             finish_message='Podfile 修改完成✅',
                                             failed_message='Podfile 修改失败❌')

    with open(file_path, 'r', encoding='UTF-8') as f:
        file_data = f.read()

    for commit_model in wanted_models:
        commit_model: ProjectLatestCommitModel = commit_model
        debugPrint(f"替换 { commit_model.project_name } 原 commit { commit_model.current_commit } 为 { commit_model.latest_commit }")
        file_data = file_data.replace(commit_model.current_commit, commit_model.latest_commit)

    with open(file_path, 'w', encoding='UTF-8') as f:
        f.write(file_data)

    LoadingAnimation.sharedInstance.finished = True


def commit_podfile_changes(helper: MRHelper, messages: [str]):
    helper.repo.git.add(all=True)
    commit_message: str = ''
    if len(messages):
        # 从备选 message 中选择 message
        options: [str] = messages
        custom_message: str = "没有想要的，我要自己写 message"
        options.append(custom_message)
        title = '请选择提交本次 Podfile 自动更新使用的 message(「回车键」选择): '
        message, index = pick.pick(options,
                                   title,
                                   default_index=0,
                                   multiselect=False,
                                   min_selection_count=1)
        debugPrint("你选择了", message)
        if message != custom_message:
            commit_message = message
    if len(commit_message) == 0:
        commit_message = make_question('请输入提交:')
        debugPrint("你输入了", commit_message)

    debugPrint("commit message:", commit_message)
    helper.repo.git.commit("-m", commit_message)
