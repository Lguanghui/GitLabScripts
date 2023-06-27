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

import requests
import json
import configparser
from Utils import Colors, debugPrint
from makeQuestion import make_question
from config_handler import MergeRequestConfigModel, FeishuUserInfo
import pick


def send_feishubot_message(merge_request_url: str,
                           author: str,
                           message: str,
                           repo_name: str,
                           config: MergeRequestConfigModel) -> bool:

    answer = make_question('是否让机器人发送 merge request 通知 y/n(回车默认不发送): ', ['n', 'y'])
    if answer == 'n':
        return False

    if config is None:
        SystemExit('配置文件为空')
        return False

    at_openids: [str] = pick_at_userid(user_infos=config.feishu_user_infos)

    if config.send_feishubot_message is False or len(config.feishu_bot_webhook) == 0:
        SystemExit('未开启发送机器人通知选项或未填写 webhook 链接')
        return False
    else:
        headers = {"Content-Type": "application/json"}

        content: [[dict]] = []  # 注意，这里面的元素必须是数组，一个元素代表一个段落

        desc_content: [dict] = []
        if len(at_openids) > 0:
            for openid in at_openids:
                desc_content.append({"tag": "at", "user_id": openid})
        desc_content.append({"tag": "text", "text": " 您有一条 merge request 待处理🚀🚀🚀"})
        content.append(desc_content)

        # content.append([{"tag": "text", "text": "commit 信息:"}])
        repo_content: [dict] = [{"tag": "text", "text": "    - repo: "},
                                {"tag": "text", "text": repo_name}]
        author_content: [dict] = [{"tag": "text", "text": "    - author: "},
                                  {"tag": "text", "text": author}]
        message_content: [dict] = [{"tag": "text", "text": "    - message: "},
                                   {"tag": "text", "text": message}]

        content.append(repo_content)
        content.append(author_content)
        content.append(message_content)

        content.append([{"tag": "a", "text": "点我查看 merge request", "href": merge_request_url}])

        body = json.dumps({"msg_type": "post", "content": {
            "post": {"zh_cn": {"title": "待处理 merge request 通知", "content": content}}}})
        # debugPrint(body)
        response = requests.request("POST", config.feishu_bot_webhook, headers=headers, data=body)
        debugPrint('status code: ', response.status_code)
        if response.status_code == 200 or response.status_code == 0:
            print('机器人通知发送成功！🎉')
            return True
        else:
            return False


def pick_at_userid(user_infos: [FeishuUserInfo]) -> [str]:
    pick.SYMBOL_CIRCLE_FILLED = '✔'
    pick.SYMBOL_CIRCLE_EMPTY = '☐'
    at_openid: [str] = []
    if len(user_infos) == 0:
        print(Colors.WARNING + "未配置 feishu_user_infos，无法 @ 指定人员" + Colors.ENDC)
    else:
        if len(user_infos) == 1 and user_infos[0].default_selected is True:
            at_openid.append(user_infos[0].feishu_openid)
        else:
            title = '请选择需要 @ 的人员 (按「空格键」选中, 按「回车键」结束选择): '
            options = [user.name for user in user_infos]
            # default_selected_index = next(user for user in user_infos if user.default_selected is True)
            default_selected_index = 0
            for (index, user) in enumerate(user_infos):
                if user.default_selected is True:
                    default_selected_index = index
                    break

            selected_items = pick.pick(options,
                                       title,
                                       default_index=default_selected_index,
                                       multiselect=True,
                                       min_selection_count=0)

            selected_ids = list(map(lambda x: user_infos[x[1]].feishu_openid, selected_items))
            debugPrint('当前选中 ', selected_ids)
            return selected_ids


if __name__ == '__main__':
    # send_feishubot_message(merge_request_url='https://www.baidu.com', author='xiaoliang', message='message')
    _config = configparser.ConfigParser()
    _config.read('./MRConfig.ini')
    _section = _config[_config.sections()[0]]
    dict_data = _section.get("feishu_user_infos")
    print(type(dict_data))
    dict_data = eval(dict_data)
    print(type(dict_data))
    print(dict_data)
    print(type(dict_data[0]['default_selected']))
