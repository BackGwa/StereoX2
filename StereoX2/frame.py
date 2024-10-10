import cv2
from .logger import Logger

log = Logger()

class Frame:
    def __init__(self, source: int | str, source_size: tuple):
        self.source = source
        self.__source__ = None
        self.width = source_size[0]
        self.height = source_size[1]

    def attach(self):
        try:
            log.alert(f"소스를 할당하는 중 입니다.")
            self.__source__ = cv2.VideoCapture(self.source)
            self.__source__.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.__source__.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            log.success(f"소스를 할당했습니다.")
        except Exception as ex:
            log.error(f"소스를 가져오던 중 문제가 발생하였습니다.", ex)

    def detach(self):
        try:
            log.alert(f"소스를 해제하는 중 입니다.")
            self.__source__.release()
            cv2.destroyAllWindows()
            log.success(f"소스를 해제했습니다.")
        except Exception as ex:
            log.error("소스 해제를 시도했지만, 문제가 발생했습니다.", ex)

    def vsplit(self, frame) -> tuple:
        return (frame[:, :self.width//2], frame[:, self.width//2:])

    def read(self) -> tuple:
        ret, frame = self.__source__.read()

        if not ret:
            log.warn("소스를 읽지 못했습니다.")

        left_frame, right_frame = self.vsplit(frame)
        return (ret, left_frame, right_frame)