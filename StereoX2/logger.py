class Logger:
    def __init__(self):
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

    def error(self, *args):
        self.__debug_message__("충돌", self.RED, *args)
        exit()
        
    def warn(self, *args):
        self.__debug_message__("경고", self.YELLOW, *args)
        
    def success(self, *args):
        self.__debug_message__("성공", self.GREEN, *args)
        
    def alert(self, *args):
        self.__debug_message__("알림", self.CYAN, *args)