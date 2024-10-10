import cv2
import numpy as np
from .frame import Frame
from .logger import Logger

log = Logger()

class Preview:
    def __init__(self, source: int | str, source_size: tuple):
        self.source = source
        self.width = source_size[0]
        self.height = source_size[1]

    def source_preview(self, exit_trigger: int = 27):
        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        while True:
            ret, left_frame, right_frame = frm.read()

            if ret:
                cv2.namedWindow("StereoX2 - LEFT PREVIEW", flags=cv2.WINDOW_NORMAL)
                cv2.namedWindow("StereoX2 - RIGHT PREVIEW", flags=cv2.WINDOW_NORMAL)
                cv2.imshow("StereoX2 - LEFT PREVIEW", left_frame)
                cv2.imshow("StereoX2 - RIGHT PREVIEW", right_frame)

            if cv2.waitKey(1) & 0xFF == exit_trigger:
                break

        frm.detach()
        log.alert("소스 프리뷰가 중단되었습니다.")

    def calibration_preview(self, file: str = "calibration.npz", line: int = 0, exit_trigger: int = 27):
        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        try:
            log.alert(f"캘리브레이션 데이터를 읽는 중입니다.")
            calibration_data = np.load(file)
            mtx1 = calibration_data['cameraMatrix1']
            dist1 = calibration_data['distCoeffs1']
            mtx2 = calibration_data['cameraMatrix2']
            dist2 = calibration_data['distCoeffs2']
            R = calibration_data['R']
            T = calibration_data['T']
            log.success(f"캘리브레이션 데이터를 읽었습니다.")
        except Exception as ex:
            log.error(f"캘리브레이션 데이터를 읽던 중 문제가 발생하였습니다.", ex)

        try:
            log.alert(f"렉티피케이션 맵 계산을 시작합니다.")
            R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(mtx1, dist1, mtx2, dist2, 
                                                            (self.width // 2, self.height), R, T)
            
            map1x, map1y = cv2.initUndistortRectifyMap(mtx1, dist1, R1, P1, 
                                                    (self.width // 2, self.height), cv2.CV_32FC1)
            map2x, map2y = cv2.initUndistortRectifyMap(mtx2, dist2, R2, P2, 
                                                    (self.width // 2, self.height), cv2.CV_32FC1)
            log.success(f"렉티피케이션 맵 계산을 완료했습니다.")
        except Exception as ex:
            log.error(f"렉티피케이션 맵을 계산하던 중 문제가 발생하였습니다.", ex)

        while True:
            ret, left_frame, right_frame = frm.read()

            if ret:
                try:
                    left_rectified = cv2.remap(left_frame, map1x, map1y, cv2.INTER_LINEAR)
                    right_rectified = cv2.remap(right_frame, map2x, map2y, cv2.INTER_LINEAR)
                except Exception as ex:
                    log.error("왜곡 보정 및 렉티피케이션을 적용하던 중 문제가 발생했습니다.", ex)

                if line > 0:
                    try:
                        line_interval = self.height // (line + 1)

                        for i in range(line + 1):
                            y = i * line_interval
                            cv2.line(left_rectified, (0, y), (self.width // 2, y), (0, 0, 255), 1)
                            cv2.line(right_rectified, (0, y), (self.width // 2, y), (0, 255, 0), 1)
                    except Exception as ex:
                        log.error("수평선을 표시하는데 문제가 발생했습니다.", ex)

                try:
                    combined = np.hstack((left_rectified, right_rectified))
                    cv2.namedWindow("StereoX2 - CALIBRATED PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.imshow("StereoX2 - CALIBRATED PREVIEW", combined)
                except Exception as ex:
                    log.error("캘리브레이션 프리뷰를 표시하던 중 문제가 발생했습니다.", ex)

            if cv2.waitKey(1) & 0xFF == exit_trigger:
                break

        frm.detach()
        log.alert("캘리브레이션 프리뷰가 중단되었습니다.")