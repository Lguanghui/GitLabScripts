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
from Utils import debugPrint


def post_merge_request_create(merge_request_url: str,
                              bot_message_at_ids: [str],
                              personal_openid: str,
                              bot_webhook_url: str,
                              author: str
                              ):
    headers = {"Content-Type": "application/json"}
    iid: str = merge_request_url.split("/")[-1]
    body = json.dumps({"merge_request_url": merge_request_url,
                       "iid": iid,
                       "bot_message_at_ids": bot_message_at_ids,
                       "personal_openid": personal_openid,
                       "bot_webhook_url": bot_webhook_url,
                       "author": author
                       })
    response = requests.request("POST", "http://68.183.233.56:8080/merge-request/create", headers=headers, data=body)
    debugPrint('向服务器发送创建请求，status code: ', response.status_code)


if __name__ == '__main__':
    from config_handler import get_config_model

    config = get_config_model()
    post_merge_request_create(merge_request_url="https://gitlab.gotokeep.com/ios/app/fd/KEPMessageModule/-/merge_requests/59",
                              bot_message_at_ids=["6978667324467331100", "6919418530309193730"],
                              personal_openid=config.self_open_id,
                              bot_webhook_url=config.feishu_bot_webhook,
                              author="xiaoliang"
                              )
