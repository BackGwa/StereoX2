import cv2
from .logger import Logger

log = Logger("Frame", "log/Frame")

class Frame:
    def __init__(self, left_source: int | str, right_source: int | str):
        """
        Frame 객체를 초기화합니다.

        :param source: 카메라 소스 (장치 인덱스 또는 비디오 파일 경로)
        :param source_size: 소스의 (너비, 높이) 튜플
        """
        self.left_source = left_source
        self.right_source = right_source
        self.__left_source__ = None
        self.__right_source__ = None

    def attach(self):
        """
        카메라 소스를 연결하고 설정합니다.
        """
        try:
            log.alert("소스를 할당하는 중입니다.")
            self.__left_source__ = cv2.VideoCapture(self.left_source)
            self.__right_source__ = cv2.VideoCapture(self.right_source)
            log.success("소스를 할당했습니다.")
        except Exception as ex:
            log.error(f"소스를 가져오던 중 문제가 발생하였습니다.", ex)

    def detach(self):
        """
        카메라 소스 연결을 해제하고 모든 창을 닫습니다.
        """
        try:
            log.alert("소스를 해제하는 중입니다.")
            self.__left_source__.release()
            self.__right_source__.release()
            cv2.destroyAllWindows()
            log.success("소스를 해제했습니다.")
        except Exception as ex:
            log.error(f"소스 해제를 시도했지만, 문제가 발생했습니다.", ex)

    def read(self) -> tuple:
        """
        카메라에서 프레임을 읽고 좌우로 분할합니다.

        :return: (성공 여부, 왼쪽 프레임, 오른쪽 프레임) 튜플
        """
        left_ret, left_frame = self.__left_source__.read()
        right_ret, right_frame = self.__right_source__.read()

        if not left_ret or not right_ret:
            log.warn("소스를 읽지 못했습니다.")
            return (False, None, None)

        return (True, left_frame, right_frame)