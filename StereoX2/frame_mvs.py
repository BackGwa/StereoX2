import cv2
import numpy as np
import threading
from MvCameraControl_class import *
from .logger import Logger

log = Logger("Frame", "log/Frame")

class Frame:
    def __init__(self, left_source: int, right_source: int):
        """
        Frame 객체를 초기화합니다.

        :param left_source: 왼쪽 카메라 장치 인덱스
        :param right_source: 오른쪽 카메라 장치 인덱스
        """
        self.left_source = left_source
        self.right_source = right_source
        self.__left_source__ = MvCamera()
        self.__right_source__ = MvCamera()
        self.running = False
        
        # 디바이스 리스트 초기화
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        self.tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        
    def __connect_camera__(self, camera: MvCamera, device_info) -> bool:
        """
        개별 카메라 연결 및 설정을 수행합니다.
        """
        ret = camera.MV_CC_CreateHandle(device_info)
        if ret != 0:
            log.error(f"Create Handle fail! ret[0x{ret:x}]")
            return False

        ret = camera.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            log.error(f"Open Device fail! ret[0x{ret:x}]")
            return False

        # GigE 카메라인 경우 패킷 크기 최적화
        if device_info.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = camera.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = camera.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                if ret != 0:
                    log.warning(f"Warning: Set Packet Size fail! ret[0x{ret:x}]")

        # 트리거 모드 설정
        ret = camera.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            log.error(f"Set trigger mode fail! ret[0x{ret:x}]")
            return False

        return True

    def attach(self):
        """
        양쪽 카메라 소스를 연결하고 설정합니다.
        """
        try:
            log.alert("소스를 할당하는 중입니다.")
            
            # SDK 초기화
            MvCamera.MV_CC_Initialize()
            
            # 디바이스 검색
            ret = MvCamera.MV_CC_EnumDevices(self.tlayerType, self.deviceList)
            if ret != 0:
                raise Exception(f"Enum Devices fail! ret[0x{ret:x}]")

            if self.deviceList.nDeviceNum < 2:
                raise Exception(f"카메라가 충분하지 않습니다. 발견된 카메라: {self.deviceList.nDeviceNum}")

            # 왼쪽 카메라 연결
            left_device = cast(self.deviceList.pDeviceInfo[self.left_source], 
                             POINTER(MV_CC_DEVICE_INFO)).contents
            if not self.__connect_camera__(self.__left_source__, left_device):
                raise Exception("왼쪽 카메라 연결 실패")

            # 오른쪽 카메라 연결
            right_device = cast(self.deviceList.pDeviceInfo[self.right_source], 
                              POINTER(MV_CC_DEVICE_INFO)).contents
            if not self.__connect_camera__(self.__right_source__, right_device):
                raise Exception("오른쪽 카메라 연결 실패")

            # 이미지 획득 시작
            if self.__left_source__.MV_CC_StartGrabbing() != 0:
                raise Exception("왼쪽 카메라 그래빙 시작 실패")
            if self.__right_source__.MV_CC_StartGrabbing() != 0:
                raise Exception("오른쪽 카메라 그래빙 시작 실패")

            self.running = True
            log.success("소스를 할당했습니다.")

        except Exception as ex:
            self.detach()  # 에러 발생시 연결 해제
            log.error(f"소스를 가져오던 중 문제가 발생하였습니다.", ex)
            raise

    def detach(self):
        """
        카메라 소스 연결을 해제합니다.
        """
        try:
            log.alert("소스를 해제하는 중입니다.")
            
            self.running = False

            # 왼쪽 카메라 해제
            if self.__left_source__ is not None:
                self.__left_source__.MV_CC_StopGrabbing()
                self.__left_source__.MV_CC_CloseDevice()
                self.__left_source__.MV_CC_DestroyHandle()
                self.__left_source__ = None

            # 오른쪽 카메라 해제
            if self.__right_source__ is not None:
                self.__right_source__.MV_CC_StopGrabbing()
                self.__right_source__.MV_CC_CloseDevice()
                self.__right_source__.MV_CC_DestroyHandle()
                self.__right_source__ = None

            # SDK 종료
            MvCamera.MV_CC_Finalize()
            
            log.success("소스를 해제했습니다.")

        except Exception as ex:
            log.error(f"소스 해제를 시도했지만, 문제가 발생했습니다.", ex)
            raise

    def __get_frame__(self, camera: MvCamera) -> np.ndarray:
        """
        단일 카메라에서 프레임을 획득하고 Mat 객체로 변환합니다.
        """
        stOutFrame = MV_FRAME_OUT()
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))
        
        ret = camera.MV_CC_GetImageBuffer(stOutFrame, 1000)
        if ret != 0:
            return None

        numpy_array = np.frombuffer(bytes(stOutFrame.pBufAddr[:stOutFrame.stFrameInfo.nFrameLen]), dtype=np.uint8)
        frame = numpy_array.reshape((stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nWidth))

        camera.MV_CC_FreeImageBuffer(stOutFrame)
        return frame

    def read(self) -> tuple:
        """
        양쪽 카메라에서 프레임을 읽어옵니다.

        :return: (성공 여부, 왼쪽 프레임, 오른쪽 프레임) 튜플
        """
        if not self.running:
            return False, None, None

        try:
            left_frame = self.__get_frame__(self.__left_source__)
            right_frame = self.__get_frame__(self.__right_source__)

            if left_frame is None or right_frame is None:
                return False, None, None

            return True, left_frame, right_frame

        except Exception as ex:
            log.error("프레임 읽기 실패", ex)
            return False, None, None