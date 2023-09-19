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
from Utils import Colors, debugPrint
from makeQuestion import make_question
from config_handler import MergeRequestConfigModel, FeishuUserInfo
import pick


def send_feishubot_message(merge_request_url: str,
                           author: str,
                           message: str,
                           repo_name: str,
                           target_branch: str,
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

        at_str: str = ''
        if len(at_openids) > 0:
            for openid in at_openids:
                at_str += f"<at id={ openid }></at>"

        body = json.dumps({
            "msg_type": "interactive",
            "card": {
                "elements": [{
                    "tag": "div",
                    "text": {
                        "content": at_str + "您有一条 merge request 待处理🚀🚀🚀",
                        "tag": "lark_md"
                    }
                },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": "🛖 **仓库名：**\n" + repo_name
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": "🧑🏻‍💻 **作者：**\n" + author
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": "🛠️ **合入分支：**\n" + target_branch
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": "✏️ **提交信息：**\n" + message
                                }
                            }
                        ]
                    },
                    {
                        "tag": "hr"
                    }, {
                        "actions": [{
                            "tag": "button",
                            "text": {
                                "content": "点我查看 merge request :玫瑰:",
                                "tag": "lark_md"
                            },
                            "url": merge_request_url,
                            "type": "primary",
                            "value": {}
                        }],
                        "tag": "action"
                    }],
                "header": {
                    "template": "blue",
                    "title": {
                        "content": "🔥 待处理 merge request 通知",
                        "tag": "plain_text"
                    }
                }
            }
        })
        # debugPrint(body)
        response = requests.request("POST", config.feishu_bot_webhook, headers=headers, data=body)
        debugPrint('status code: ', response.status_code)
        if response.status_code == 200:
            print('机器人通知发送成功！🎉')
            return True
        else:
            print('机器人通知发送失败！☹️')
            return False


def pick_at_userid(user_infos: [FeishuUserInfo]) -> [str]:
    # pick.SYMBOL_CIRCLE_FILLED = '✔'
    # pick.SYMBOL_CIRCLE_EMPTY = '☐'
    pick.SYMBOL_CIRCLE_FILLED = '●'
    pick.SYMBOL_CIRCLE_EMPTY = '○'
    at_openid: [str] = []
    if len(user_infos) == 0:
        print(Colors.WARNING + "未配置 feishu_user_infos，无法 @ 指定人员" + Colors.ENDC)
    else:
        if len(user_infos) == 1 and user_infos[0].default_selected is True:
            at_openid.append(user_infos[0].feishu_openid)
            debugPrint('当前仅配置了一个艾特人员，且默认选中')
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

            at_openid = list(map(lambda x: user_infos[x[1]].feishu_openid, selected_items))
            debugPrint('当前选中 ', at_openid)
    return at_openid


if __name__ == '__main__':
    import config_handler

    send_feishubot_message(merge_request_url='https://www.baidu.com',
                           author='xiaoliang',
                           message='feature: 腿部动作能力测评腿部动作能力测评腿部动作能力测评腿部动作能力测评腿部动作能力测评',
                           target_branch="master",
                           config=config_handler.get_config_model(),
                           repo_name="Keep")
