import os
from datetime import datetime

def __datetime__() -> str:
    now = datetime.now()
    return f"{str(now.year).zfill(4)}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)} {str(now.hour).zfill(2)}_{str(now.minute).zfill(2)}_{str(now.second).zfill(2)}"

class Logger:
    def __init__(self, name: str = "", dir: str = "log"):
        self.dir = os.path.join(dir, f"{name} {__datetime__()}.log")

        try:
            os.makedirs(dir)
        except: pass

        self.RED    = "\033[31m"
        self.GREEN  = "\033[32m"
        self.YELLOW = "\033[33m"
        self.CYAN   = "\033[34m"
        self.BOLD   = "\033[1m"
        self.RESET  = "\033[0m"

    def __debug_message__(self, title: str, color: str, *args):
        print(color + self.BOLD + title + self.RESET + self.BOLD + ": " + self.RESET, end="")
        for message in args:
            print(message)
        try:
            file = open(self.dir, 'a', encoding="UTF-8")
            file.write(f"[{__datetime__()}] {title} : {' '.join(args)}\n")
            file.close()
        except: pass

    def error(self, *args):
        self.__debug_message__("충돌", self.RED, *args)
        exit()
        
    def warn(self, *args):
        self.__debug_message__("경고", self.YELLOW, *args)
        
    def success(self, *args):
        self.__debug_message__("성공", self.GREEN, *args)
        
    def alert(self, *args):
        self.__debug_message__("알림", self.CYAN, *args)