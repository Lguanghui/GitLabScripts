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
import os
from dataclasses import dataclass, field
from dacite import from_dict
from configparser import ConfigParser
from Utils import get_root_path
import json


class Parser(ConfigParser):

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


@dataclass
class FeishuUserInfo:
    name: str
    feishu_openid: str
    default_selected: bool = False


@dataclass
class MergeRequestConfigModel:

    feishu_bot_webhook: str
    send_feishubot_message: bool
    feishu_user_infos: list[FeishuUserInfo] = field(default_factory=list)
    self_open_id: str = field(default_factory=str)


def get_config_model() -> MergeRequestConfigModel:
    file_path = get_root_path() + '/config.json'
    if not os.path.exists(file_path):
        raise SystemExit('⚠️ config.json 文件不存在。请先执行 createMR.sh --init')

    with open(file_path) as f:
        data = json.load(f)
        model = from_dict(MergeRequestConfigModel, data)

        if len(model.self_open_id) == 0:
            print('\r\033[K')
            raise SystemExit('⚠️ config.json -> self_open_id 未配置。请将 self_open_id 设置为自己的飞书 openid。可以参考 '
                             'config_example.json')

        return model
    # parser = Parser()
    # parser.read(get_root_path() + '/MRConfig.ini')
    # raw_dict = parser.as_dict()['Keep']
    # raw_dict['feishu_user_infos'] = eval(raw_dict['feishu_user_infos'])
    # raw_dict['send_feishubot_message'] = parser.getboolean('Keep', 'send_feishubot_message')
    # config_model = from_dict(MergeRequestConfigModel, raw_dict)
    # return config_model


if __name__ == '__main__':
    _model = get_config_model()
    print(_model)
    # _parser = Parser()
    # _parser.read('./MRConfig.ini')
    # print(_parser.as_dict()['Keep'])
    # _dict = _parser.as_dict()['Keep']
    # _dict['feishu_user_infos'] = eval(_dict['feishu_user_infos'])
    # print(type(_dict['send_feishubot_message']), _dict['send_feishubot_message'])
    # _dict['send_feishubot_message'] = _parser.getboolean('Keep', 'send_feishubot_message')
    # print(_dict)
    # _config_model = from_dict(MergeRequestConfigModel, _dict)
    # print(_config_model.feishu_user_infos)
    # print(type(_config_model.send_feishubot_message), _config_model.send_feishubot_message)

