import cv2
import numpy as np
from .logger import Logger

log = Logger("Calculate", "log/Calculate")

class Calculate:
    def mapping(self, left_frame_data: tuple, right_frame_data: tuple) -> tuple:
        left_remap = cv2.remap(left_frame_data[0], left_frame_data[1], left_frame_data[2], cv2.INTER_LINEAR)
        right_remap = cv2.remap(right_frame_data[0], right_frame_data[1], right_frame_data[2], cv2.INTER_LINEAR) 
        return (left_remap, right_remap)
    
    def read_calibration(self, file: str = "calibration.npz") -> tuple:
        try:
            log.alert("캘리브레이션 데이터를 읽는 중입니다.")
            calibration_data = np.load(file)
            mtx1 = calibration_data['cameraMatrix1']
            dist1 = calibration_data['distCoeffs1']
            mtx2 = calibration_data['cameraMatrix2']
            dist2 = calibration_data['distCoeffs2']
            R = calibration_data['R']
            T = calibration_data['T']
            log.success("캘리브레이션 데이터를 읽었습니다.")
            return (mtx1, dist1, mtx2, dist2, R, T)
        except Exception as ex:
            log.error(f"캘리브레이션 데이터를 읽던 중 문제가 발생하였습니다.", ex)

    def rectification(self, data: tuple, source_size: tuple) -> tuple:
        mtx1, dist1, mtx2, dist2, R, T = data
        width, height = source_size
        try:
            log.alert("렉티피케이션 맵 계산을 시작합니다.")
            R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(mtx1, dist1, mtx2, dist2, 
                                                            (width // 2, height), R, T)
            
            map1x, map1y = cv2.initUndistortRectifyMap(mtx1, dist1, R1, P1, 
                                                    (width // 2, height), cv2.CV_32FC1)
            map2x, map2y = cv2.initUndistortRectifyMap(mtx2, dist2, R2, P2, 
                                                    (width // 2, height), cv2.CV_32FC1)
            
            log.success("렉티피케이션 맵 계산을 완료했습니다.")
            return (map1x, map1y, map2x, map2y, roi1, roi2)
        except Exception as ex:
            log.error(f"렉티피케이션 맵을 계산하던 중 문제가 발생하였습니다.", ex)

    def get_roi(self, left_frame, right_frame, roi1, roi2) -> tuple:
        """
        교차 구역의 프레임을 반환합니다.

        :param roi1: 좌측 카메라의 ROI
        :param roi2: 우측 카메라의 ROI
        :return: 교차 구역의 (ret, left_roi, right_roi) 프레임 튜플
        """
        intersect_x1 = max(roi1[0], roi2[0])
        intersect_y1 = max(roi1[1], roi2[1])
        intersect_x2 = min(roi1[0] + roi1[2], roi2[0] + roi2[2])
        intersect_y2 = min(roi1[1] + roi1[3], roi2[1] + roi2[3])

        if intersect_x1 < intersect_x2 and intersect_y1 < intersect_y2:
            left_roi = left_frame[intersect_y1:intersect_y2, intersect_x1:intersect_x2]
            right_roi = right_frame[intersect_y1:intersect_y2, intersect_x1:intersect_x2]

            return (left_roi, right_roi)

    def depth(self, left_image, right_image, num_disparities = 16, block_size: int = 5, uniqueness_ratio: int = 15, speckle_window_size: int = 150, speckle_range: int = 1):
        stereo = cv2.StereoSGBM.create(numDisparities=num_disparities,
                                       blockSize=block_size,
                                       uniquenessRatio=uniqueness_ratio,
                                       speckleWindowSize=speckle_window_size,
                                       speckleRange=speckle_range)
        left_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)
        disparity = stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0
        return disparity
    
    def depth_distance(self, disparity) -> tuple:
        min_val = np.min(disparity)
        max_val = np.max(disparity)
        return (min_val, max_val)