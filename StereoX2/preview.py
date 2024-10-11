import cv2
import numpy as np
from .frame import Frame
from .calculate import Calculate
from .logger import Logger

calc = Calculate()
log = Logger("Preview", "log/Preview")

class Preview:
    def __init__(self, source: int | str, source_size: tuple):
        """
        Preview 객체를 초기화합니다.

        :param source: 카메라 소스 (장치 인덱스 또는 비디오 파일 경로)
        :param source_size: 소스의 (너비, 높이) 튜플
        """
        self.source = source
        self.width, self.height = source_size

    def __draw_line__(self, frame, line: int):
        if line > 0:
            line_interval = frame.shape[0] // (line + 1)
            for i in range(line + 1):
                y = i * line_interval
                cv2.putText(frame, f"{i}", (0, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 128, 0), 2)
                cv2.line(frame, (0, y), (frame.shape[1], y), (0, 128, 0), 1)

    def source_preview(self, line: int = 0, exit_trigger: int = 27):
        """
        원본 소스의 프리뷰를 표시합니다.

        :param exit_trigger: 프리뷰를 종료할 키 코드 (기본값: ESC)
        """
        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        log.alert("소스 프리뷰가 시작되었습니다.")
        
        while True:
            ret, left_frame, right_frame = frm.read()

            for frame in (left_frame, right_frame):
                self.__draw_line__(frame, line)

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
        """
        캘리브레이션된 이미지의 프리뷰를 표시합니다.

        :param file: 캘리브레이션 데이터 파일 경로
        :param line: 표시할 수평선의 수
        :param exit_trigger: 프리뷰를 종료할 키 코드 (기본값: ESC)
        """
        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        data = calc.read_calibration(file)
        map1x, map1y, map2x, map2y, roi1, roi2 = calc.rectification(data, (self.width, self.height))

        log.alert("캘리브레이션 프리뷰가 시작되었습니다.")

        while True:
            ret, left_frame, right_frame = frm.read()

            if ret:
                try:
                    left_rectified = cv2.remap(left_frame, map1x, map1y, cv2.INTER_LINEAR)
                    right_rectified = cv2.remap(right_frame, map2x, map2y, cv2.INTER_LINEAR)
                    
                    for frame in (left_rectified, right_rectified):
                        self.__draw_line__(frame, line)

                    cv2.rectangle(left_rectified, (roi1[0], roi1[1]), 
                                  (roi1[0] + roi1[2], roi1[1] + roi1[3]), (255, 0, 0), 2)
                    cv2.rectangle(right_rectified, (roi2[0], roi2[1]), 
                                  (roi2[0] + roi2[2], roi2[1] + roi2[3]), (255, 0, 0), 2)

                    intersect_x1 = max(roi1[0], roi2[0])
                    intersect_y1 = max(roi1[1], roi2[1])
                    intersect_x2 = min(roi1[0] + roi1[2], roi2[0] + roi2[2])
                    intersect_y2 = min(roi1[1] + roi1[3], roi2[1] + roi2[3])

                    if intersect_x1 < intersect_x2 and intersect_y1 < intersect_y2:
                        cv2.rectangle(left_rectified, (intersect_x1, intersect_y1), 
                                      (intersect_x2, intersect_y2), (0, 255, 0), 2)
                        cv2.rectangle(right_rectified, (intersect_x1, intersect_y1), 
                                      (intersect_x2, intersect_y2), (0, 255, 0), 2)

                    cv2.namedWindow("StereoX2 - LEFT CALIBRATED PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.namedWindow("StereoX2 - RIGHT CALIBRATED PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.imshow("StereoX2 - LEFT CALIBRATED PREVIEW", left_rectified)
                    cv2.imshow("StereoX2 - RIGHT CALIBRATED PREVIEW", right_rectified)
                except Exception as ex:
                    log.error(f"캘리브레이션 프리뷰를 처리하던 중 문제가 발생했습니다.", ex)

            if cv2.waitKey(1) & 0xFF == exit_trigger:
                break

        frm.detach()
        log.alert("캘리브레이션 프리뷰가 중단되었습니다.")

    def roi_preview(self, file: str = "calibration.npz", line: int = 0, exit_trigger: int = 27):
        """
        캘리브레이션 후 ROI만 보여주는 프리뷰를 표시합니다.

        :param file: 캘리브레이션 데이터 파일 경로
        :param exit_trigger: 프리뷰를 종료할 키 코드 (기본값: ESC)
        """
        data = calc.read_calibration(file)
        map1x, map1y, map2x, map2y, roi1, roi2 = calc.rectification(data, (self.width, self.height))

        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        log.alert("ROI 프리뷰가 시작되었습니다.")

        while True:
            ret, left_frame, right_frame = frm.read()
            left_rectified, right_rectified = calc.mapping((left_frame, map1x, map1y),
                                                           (right_frame, map2x, map2y))

            left_roi, right_roi = calc.get_roi(left_rectified, right_rectified, roi1, roi2)

            for frame in (left_roi, right_roi):
                self.__draw_line__(frame, line)

            if ret:
                try:
                    cv2.namedWindow("StereoX2 - LEFT ROI PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.namedWindow("StereoX2 - RIGHT ROI PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.imshow("StereoX2 - LEFT ROI PREVIEW", left_roi)
                    cv2.imshow("StereoX2 - RIGHT ROI PREVIEW", right_roi)
                except Exception as ex:
                    log.error(f"ROI 프리뷰를 처리하던 중 문제가 발생했습니다.", ex)

            if cv2.waitKey(1) & 0xFF == exit_trigger:
                break

        frm.detach()
        log.alert("ROI 프리뷰가 중단되었습니다.")

    def overlab_preview(self, file: str = "calibration.npz", line: int = 0, exit_trigger: int = 27):
        """
        캘리브레이션 된 ROI를 겹쳐 보여주는 프리뷰를 표시합니다.

        :param file: 캘리브레이션 데이터 파일 경로
        :param exit_trigger: 프리뷰를 종료할 키 코드 (기본값: ESC)
        """
        data = calc.read_calibration(file)
        map1x, map1y, map2x, map2y, roi1, roi2 = calc.rectification(data, (self.width, self.height))

        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        log.alert("오버랩 프리뷰가 시작되었습니다.")

        while True:
            ret, left_frame, right_frame = frm.read()
            left_rectified, right_rectified = calc.mapping((left_frame, map1x, map1y), (right_frame, map2x, map2y))

            left_roi, right_roi = calc.get_roi(left_rectified, right_rectified, roi1, roi2)

            red_frame = np.zeros_like(left_roi)
            red_frame[:, :, 2] = left_roi[:, :, 2]

            cyan_frame = np.zeros_like(right_roi)
            cyan_frame[:, :, 0] = right_roi[:, :, 0]
            cyan_frame[:, :, 1] = right_roi[:, :, 1]

            overlab_frame = cv2.addWeighted(red_frame, 1, cyan_frame, 1, 0)
            self.__draw_line__(overlab_frame, line)

            if ret:
                try:
                    cv2.namedWindow("StereoX2 - OVERLAB PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.imshow("StereoX2 - OVERLAB PREVIEW", overlab_frame)
                except Exception as ex:
                    log.error(f"ROI 프리뷰를 처리하던 중 문제가 발생했습니다.", ex)

            if cv2.waitKey(1) & 0xFF == exit_trigger:
                break

        frm.detach()
        log.alert("오버랩 프리뷰가 중단되었습니다.")

    def depth_preview(self, file: str = "calibration.npz", num_disparities: int = 16, block_size: int = 5, uniqueness_ratio: int = 15, speckle_window_size: int = 150, speckle_range: int = 1, exit_trigger: int = 27):
        """
        스테레오 카메라로부터 뎁스 맵을 실시간으로 프리뷰합니다.

        :param file: 캘리브레이션 데이터 파일 경로
        :param exit_trigger: 프리뷰를 종료할 키 코드 (기본값: ESC)
        """
        data = calc.read_calibration(file)
        map1x, map1y, map2x, map2y, roi1, roi2 = calc.rectification(data, (self.width, self.height))

        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        log.alert("뎁스 프리뷰가 시작되었습니다.")

        while True:
            ret, left_frame, right_frame = frm.read()
            left_rectified = cv2.remap(left_frame, map1x, map1y, cv2.INTER_LINEAR)
            right_rectified = cv2.remap(right_frame, map2x, map2y, cv2.INTER_LINEAR)
                    
            left_roi, right_roi = calc.get_roi(left_rectified, right_rectified, roi1, roi2)

            if ret:
                try:
                    depth = calc.depth(left_roi, right_roi, num_disparities, block_size, uniqueness_ratio, speckle_window_size, speckle_range)
                    depth_min, depth_max = calc.depth_distance(depth)

                    depth_map_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
                    depth_map_colored = cv2.applyColorMap(depth_map_normalized.astype(np.uint8), cv2.COLORMAP_JET)

                    cv2.putText(depth_map_colored, f'MIN DISTANCE : {depth_min:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                    cv2.putText(depth_map_colored, f'MAX DISTANCE : {depth_max:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)

                    cv2.namedWindow("StereoX2 - DEPTH MAP PREVIEW", flags=cv2.WINDOW_NORMAL)
                    cv2.imshow("StereoX2 - DEPTH MAP PREVIEW", depth_map_colored)
                except Exception as ex:
                    log.error(f"뎁스 프리뷰를 처리하던 중 문제가 발생했습니다.", ex)

            if cv2.waitKey(1) & 0xFF == exit_trigger:
                break

        frm.detach()
        log.alert("뎁스 프리뷰가 중단되었습니다.")