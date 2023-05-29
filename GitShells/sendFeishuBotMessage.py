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
from createMR import get_root_path
from makeQuestion import make_question


# url = "https://open.feishu.cn/open-apis/bot/v2/hook/2f7e2c1c-cd18-4663-85a4-f0bf3c548c63"
# headers = {"Content-Type": "application/json"}
# body = json.dumps({"msg_type": "text","content": {"text": "text<at user_id = \"6978667324467331100\">梁光辉</at>merge request text content 要处理"}})
# response = requests.request("POST", url, headers=headers, data=body)
# print(response.text)


def send_feishubot_message(merge_request_url: str, author: str, message: str) -> bool:
    config = configparser.ConfigParser()
    config.read(get_root_path() + '/MRConfig.ini')

    answer = make_question('是否让机器人发送 merge request 通知 y/n(回车默认不发送): ', ['n', 'y'])
    if answer == 'n':
        return False

    if len(config.sections()) == 0:
        SystemExit('配置文件为空')
        return False
    section = config[config.sections()[0]]
    send_message = section.get('send_feishubot_message')
    webhook = section.get('feishu_bot_webhook')
    at_openid = section.get('feishu_bot_@_user_openid')
    if not send_message or len(webhook) == 0:
        SystemExit('未开启发送机器人通知选项或未填写 webhook 链接')
        return False
    else:
        headers = {"Content-Type": "application/json"}

        content: [[dict]] = []  # 注意，这里面的元素必须是数组，一个元素代表一个段落

        desc_content: [dict] = []
        if len(at_openid) > 0:
            desc_content.append({"tag": "at", "user_id": at_openid})
        desc_content.append({"tag": "text", "text": " 您有一条 merge request 待处理🚀🚀🚀"})
        content.append(desc_content)

        # content.append([{"tag": "text", "text": "commit 信息:"}])
        author_content: [dict] = [{"tag": "text", "text": "    - author: "},
                                  {"tag": "text", "text": author}]
        message_content: [dict] = [{"tag": "text", "text": "    - message: "},
                                   {"tag": "text", "text": message}]
        content.append(author_content)
        content.append(message_content)

        content.append([{"tag": "a", "text": "点我查看 merge request", "href": merge_request_url}])

        body = json.dumps({"msg_type": "post", "content": {
            "post": {"zh_cn": {"title": "待处理 merge request 通知", "content": content}}}})
        # print(body)
        response = requests.request("POST", webhook, headers=headers, data=body)
        if response.status_code == 0:
            print('机器人通知发送成功！🎉')
            return True
        else:
            return False


if __name__ == '__main__':
    send_feishubot_message(merge_request_url='https://www.baidu.com', author='xiaoliang', message='message')
