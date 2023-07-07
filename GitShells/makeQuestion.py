from termios import tcflush, TCIFLUSH
import sys
from Utils import Colors
import readline


def make_question(prompt: str, expect_answers: [str] = None):
    """
    获取终端输入
    :param prompt: 提示语
    :param expect_answers: 有效答案
    :return: 有效答案中的其中一个。如果用户直接回车，则返回有效答案中的第一个
    """
    valid = False
    expect_answers = expect_answers if (expect_answers is not None) else []
    while not valid:
        # 获取输入前先清空输入缓冲区的数据，防止干扰
        tcflush(sys.stdin, TCIFLUSH)
        answer = input(Colors.CBOLD + Colors.CGREEN + prompt + Colors.ENDC)
        if (answer in expect_answers) or len(answer) == 0 or (len(expect_answers) == 0 and len(answer) > 0):
            valid = True
            return answer \
                if (len(answer) > 0) \
                else (expect_answers[0] if (expect_answers is not None) and len(expect_answers) > 0 else '')


if __name__ == '__main__':
    make_question('请输入你的性别', ['男', '女'])
