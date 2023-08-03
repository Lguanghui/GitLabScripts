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
此脚本用于更新 iOS 所有组件库的最低系统支持版本
"""

import re
import gitlab
import queue
import threading
from gitlab.v4.objects.projects import Project
from gitlab.v4.objects import ProjectFile

# 改动分支
FEATURE_BRANCH_NAME: str = "modify_minimum_target"


def list_cut(obj: list, sublist_max_count):
    return [obj[i:i + sublist_max_count] for i in range(0, len(obj), sublist_max_count)]


class MinimumTargetModifierThread(threading.Thread):

    @property
    def project_name(self):
        return self.proj.attributes['name']

    def __init__(self, proj: Project, to_queue: queue.Queue):
        """
        初始化线程
        :param proj: gitlab project 实例
        :param to_queue: 数据队列
        """
        super().__init__()
        self.queue = to_queue
        self.proj = proj

    def run(self) -> None:
        url = Modifier.modify_project(project=self.proj)
        if len(url) > 0:
            self.queue.put(url)
        return


class Modifier:
    def __init__(self):
        token = input("请输入 Gitlab token: ")
        self.gitlab = gitlab.Gitlab(url="https://gitlab.gotokeep.com", private_token=token)
        # self.gitlab = gitlab.Gitlab.from_config('Keep', [search_shell_file_path('MRConfig.ini')])
        # self.projects: [Project] = self.gitlab.projects.list(get_all=True)

    def start(self):
        groups = self.gitlab.groups.list()
        print([group.name for group in groups])
        groups = list(filter(lambda x: x.name not in ['FD Core', 'App', 'SE', 'iOS'], groups))
        print('过滤后', [group.name for group in groups])
        all_urls: dict = {}
        processed_proj_names: [str] = []
        for group in groups:
            projects = group.projects.list(get_all=True)
            group_url_list = set()
            group_threads: [MinimumTargetModifierThread] = []
            output_queue: [queue.Queue] = queue.Queue()
            for group_project in projects:
                project = self.gitlab.projects.get(group_project.id, lazy=False)
                if project.name not in processed_proj_names:
                    thread = MinimumTargetModifierThread(proj=project, to_queue=output_queue)
                    group_threads.append(thread)
                    processed_proj_names.append(project.name)
            split_arrays = list_cut(group_threads, 9)  # 数组拆分，避免开启过多线程，触发警告
            print(f"正在处理 group: {group.name}")
            for threads in split_arrays:
                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                while not output_queue.empty():
                    group_url_list.add(output_queue.get())
            all_urls[group.name] = group_url_list

        for (key, urls) in all_urls.items():
            print(f"{key} 相关组件库 merge request")
            print(urls)

    @classmethod
    def modify_project(cls, project: Project) -> str:
        # 创建分支
        try:
            project.branches.delete(FEATURE_BRANCH_NAME)
        except Exception as e:
            print(f"project {project.name} 没有分支：{FEATURE_BRANCH_NAME}")
        else:
            print(f"project {project.name} 删除分支 {FEATURE_BRANCH_NAME}")

        try:
            project.branches.create({'branch': FEATURE_BRANCH_NAME,
                                     'ref': project.default_branch})
        except Exception as e:
            print(f"project {project.name} 无法创建分支 {FEATURE_BRANCH_NAME}，跳过这个仓库")
            return ''

        file_items: [dict] = project.repository_tree(ref=project.default_branch, recursive=True, all=True)
        podspec_modified = Modifier.modify_project_podspec(project=project, file_items=file_items)
        xcodeproj_modified = Modifier.modify_project_xcodeproj(project=project, file_items=file_items)
        podfile_modified = Modifier.modify_project_podfile(project=project, file_items=file_items)

        if podfile_modified or podspec_modified or xcodeproj_modified:
            # 创建 merge request
            try:
                mr = project.mergerequests.create({'source_branch': 'modify_minimum_target',
                                                   'target_branch': project.default_branch,
                                                   'title': 'feature: 调整组件库最低支持版本至 iOS 12',
                                                   'squash': True})
                mr.save()
                return mr.web_url
            except Exception as e:
                mr_list = project.mergerequests.list(state='opened',
                                                     order_by='updated_at',
                                                     get_all=True)
                for mr in mr_list:
                    if mr.source_branch == FEATURE_BRANCH_NAME:
                        print(f"project {project.name} 已有 merge request")
                        return mr.web_url
                return ''
        return ''

    @classmethod
    def modify_project_podspec(cls, project: Project, file_items: [dict]) -> bool:
        try:
            items: [dict] = project.repository_tree(ref='master', recursive=True, all=True)
            filenames = [f['path'] for f in items if ('.podspec' in f['path'])]
            if len(filenames) == 0:
                return False

            f: ProjectFile = project.files.get(file_path=filenames[0], ref=project.default_branch)
            new_content = re.sub(rb"ios.deployment_target = [\'\"]([1-9]\d?(\.([1-9]?\d)))[\'\"]",
                                 b'ios.deployment_target = \'12.0\'',
                                 f.decode())
            # new_content = f.decode().replace(b'11.0', b'12.0')
            f.content = new_content.decode('utf-8')  # 字节转字符串
            f.save(branch=FEATURE_BRANCH_NAME, commit_message='feature: 调整组件库最低支持版本至 iOS 12')
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def modify_project_xcodeproj(cls, project: Project, file_items: [dict]) -> bool:
        try:
            filenames = [f['path'] for f in file_items if ('.pbxproj' in f['path'])]
            if len(filenames) == 0:
                print(f"project {project.name} 没有找到 pbxproj 格式文件")
                return False

            for file in filenames:
                print(f"project {project.name} 修改 {file} 文件中")
                f: ProjectFile = project.files.get(file_path=file, ref=project.default_branch)
                new_content = re.sub(rb"IPHONEOS_DEPLOYMENT_TARGET = ([1-9]\d?(\.([1-9]?\d)));",
                                     b'IPHONEOS_DEPLOYMENT_TARGET = 12.0;',
                                     f.decode())
                f.content = new_content.decode('utf-8')  # 字节转字符串
                f.save(branch=FEATURE_BRANCH_NAME, commit_message='feature: 调整组件库最低支持版本至 iOS 12')
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def modify_project_podfile(cls, project: Project, file_items: [dict]) -> bool:
        try:
            filenames = [f['path'] for f in file_items if ('Podfile' in f['path'])]
            if len(filenames) == 0:
                print(f"project {project.name} 没有找到 Podfile 文件")
                return False

            for file in filenames:
                print(f"project {project.name} 修改 {file} 文件中")
                f: ProjectFile = project.files.get(file_path=file, ref=project.default_branch)
                new_content = re.sub(rb"platform :ios, [\'\"]([1-9]\d?(\.([1-9]?\d)))[\'\"]",
                                     b'platform :ios, \'12.0\'',
                                     f.decode())
                f.content = new_content.decode('utf-8')  # 字节转字符串
                f.save(branch=FEATURE_BRANCH_NAME, commit_message='feature: 调整组件库最低支持版本至 iOS 12')
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    modifier = Modifier()
    modifier.start()
