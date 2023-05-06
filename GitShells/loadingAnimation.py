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

from threading import Thread
from threading import Event
import threading
import time


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LoadingAnimation(metaclass=Singleton):
    def __init__(self):
        self.message = ""
        self.finish_message = ""
        self.__failed = False
        self.__finished = False
        self.failed_message = ""
        self.__threadEvent = Event()
        self.__thread = Thread(target=self.__loading, daemon=True)
        self.__threadBlockEvent = Event()

    @classmethod
    @property
    def sharedInstance(cls):
        return LoadingAnimation()

    @property
    def finished(self):
        return self.__finished

    @finished.setter
    def finished(self, finished):
        if isinstance(finished, bool):
            self.__finished = finished
            if finished:
                self.__threadEvent.set()
        else:
            raise ValueError

    @property
    def failed(self):
        return self.__failed

    @failed.setter
    def failed(self, failed):
        if isinstance(failed, bool):
            self.__failed = failed
            if failed:
                self.__threadEvent.set()
        else:
            raise ValueError

    def showWith(self, loading_message: str, finish_message: str = '✅ Finished', failed_message='❌ Failed'):
        self.message = loading_message
        self.finish_message = finish_message
        self.failed_message = failed_message
        self.showLoading()

    def showLoading(self):
        self.finished = False
        self.failed = False
        self.__threadEvent.clear()
        if not self.__thread.is_alive():
            self.__thread.start()
        else:
            self.__threadBlockEvent.set()

    def __loading(self):
        symbols = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
        i = 0
        while True:
            print('')
            while not self.finished and not self.failed:
                i = (i + 1) % len(symbols)
                print('\r\033[K%s %s' % (symbols[i], self.message), flush=True, end='')
                self.__threadEvent.wait(0.1)
                self.__threadEvent.clear()
            if self.finished == True and not self.failed:
                print('\r\033[K%s' % self.finish_message, flush=True)
            else:
                print('\r\033[K%s' % self.failed_message, flush=True)
            print('')
            self.__threadBlockEvent.wait()
            self.__threadBlockEvent.clear()

if __name__ == '__main__':
    lock = LoadingAnimation.sharedInstance
    lock.showWith('加载中...', finish_message='Finished!✅')
    time.sleep(3)
    lock.failed = True
    # loading again
    time.sleep(1)
    lock.showLoading()
    time.sleep(3)
    lock.finished = True
    time.sleep(3)
