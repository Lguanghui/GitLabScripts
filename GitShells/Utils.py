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
from collections import namedtuple

DEBUG_MODE = False

MergeRequestInfo = namedtuple('MergeRequestInfo', ['url', 'id'])


def print_step(*values, sep=' ', end='\n', file=None):
    _values = ('❖',) + values
    print(*_values, sep=sep, end=end, file=file)


def update_debug_mode(value: bool):
    """
    更新 DEBUG 模式的开关状态
    :param value: 是否开启
    :return:
    """
    global DEBUG_MODE
    DEBUG_MODE = value


def debugPrint(*values, sep=' ', end='\n', file=None):
    """
    只在 DEBUG 模式开启的状态下输出信息到控制台
    :param values: 要打印到控制台的信息
    :param sep: 分隔符
    :param end: 结束符
    :param file: 文件
    :return:
    """
    if DEBUG_MODE is True:
        _values = (f'\r\033[K{Colors.WARNING}🐞',) + values + (Colors.ENDC,)
        print(*_values, sep=sep, end=end, file=file)


def get_mr_url_from_local_log(log_path: str) -> MergeRequestInfo:
    """
    从本地 log 获取生成的 merge request 链接
    :param log_path: log 路径
    :return: merge request 信息，包含链接、ID 等
    """
    mr_url = ""
    mr_id = ""
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.replace(' ', '').startswith("remote:http"):
                mr_url = line.replace(' ', '').lstrip("remote:")
                break
    if len(mr_url.split("/")) > 0:
        mr_id = mr_url.split("/")[-1]
    return MergeRequestInfo(mr_url, mr_id)


def search_file_path(file_name: str) -> str:
    """
    在当前工作目录下搜索指定文件，输出指定文件的路径
    :param file_name: 指定文件名
    :return: 指定文件路径
    """
    for root, _, files in os.walk(os.getcwd()):
        if file_name in files:
            return os.path.join(root, file_name)
    return ''


class Colors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CEND = '\33[0m'
    CBOLD = '\33[1m'
    CITALIC = '\33[3m'
    CURL = '\33[4m'
    CBLINK = '\33[5m'
    CBLINK2 = '\33[6m'
    CSELECTED = '\33[7m'

    CBLACK = '\33[30m'
    CRED = '\33[31m'
    CGREEN = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE = '\33[36m'
    CWHITE = '\33[37m'

    CBLACKBG = '\33[40m'
    CREDBG = '\33[41m'
    CGREENBG = '\33[42m'
    CYELLOWBG = '\33[43m'
    CBLUEBG = '\33[44m'
    CVIOLETBG = '\33[45m'
    CBEIGEBG = '\33[46m'
    CWHITEBG = '\33[47m'

    CGREY = '\33[90m'
    CRED2 = '\33[91m'
    CGREEN2 = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2 = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2 = '\33[96m'
    CWHITE2 = '\33[97m'

    CGREYBG = '\33[100m'
    CREDBG2 = '\33[101m'
    CGREENBG2 = '\33[102m'
    CYELLOWBG2 = '\33[103m'
    CBLUEBG2 = '\33[104m'
    CVIOLETBG2 = '\33[105m'
    CBEIGEBG2 = '\33[106m'
    CWHITEBG2 = '\33[107m'


if __name__ == '__main__':
    # url = get_mr_url_from_local_log("/Users/liangguanghui/Desktop/mrLog.txt")
    # print(url)
    file_path = search_file_path('Podfile')
    print(file_path)
