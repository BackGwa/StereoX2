import cv2
from .logger import Logger

log = Logger("Frame", "log/Frame")

class Frame:
    def __init__(self, source: int | str, source_size: tuple):
        """
        Frame 객체를 초기화합니다.

        :param source: 카메라 소스 (장치 인덱스 또는 비디오 파일 경로)
        :param source_size: 소스의 (너비, 높이) 튜플
        """
        self.source = source
        self.__source__ = None
        self.width, self.height = source_size

    def attach(self):
        """
        카메라 소스를 연결하고 설정합니다.
        """
        try:
            log.alert("소스를 할당하는 중입니다.")
            self.__source__ = cv2.VideoCapture(self.source)
            self.__source__.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.__source__.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            log.success("소스를 할당했습니다.")
        except Exception as ex:
            log.error(f"소스를 가져오던 중 문제가 발생하였습니다.", ex)

    def detach(self):
        """
        카메라 소스 연결을 해제하고 모든 창을 닫습니다.
        """
        try:
            log.alert("소스를 해제하는 중입니다.")
            self.__source__.release()
            cv2.destroyAllWindows()
            log.success("소스를 해제했습니다.")
        except Exception as ex:
            log.error(f"소스 해제를 시도했지만, 문제가 발생했습니다.", ex)

    def vsplit(self, frame) -> tuple:
        """
        프레임을 수직으로 반으로 나눕니다.

        :param frame: 분할할 프레임
        :return: (왼쪽 프레임, 오른쪽 프레임) 튜플
        """
        return (frame[:, :self.width//2], frame[:, self.width//2:])

    def read(self) -> tuple:
        """
        카메라에서 프레임을 읽고 좌우로 분할합니다.

        :return: (성공 여부, 왼쪽 프레임, 오른쪽 프레임) 튜플
        """
        ret, frame = self.__source__.read()

        if not ret:
            log.warn("소스를 읽지 못했습니다.")
            return (ret, None, None)

        left_frame, right_frame = self.vsplit(frame)
        return (ret, left_frame, right_frame)