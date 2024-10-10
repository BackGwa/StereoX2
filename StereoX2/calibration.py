import cv2
import numpy as np
from .frame import Frame
from .logger import Logger

log = Logger()

class Calibration:
    def __init__(self, source: int | str, source_size: tuple, board_size: tuple, square_size: float):
        self.source = source
        self.width = source_size[0]
        self.height = source_size[1]
        self.board_size = board_size
        self.square_size = square_size

    def start(self, capture_count: int = 128, trigger: int = 32, exit_trigger: int = 27) -> tuple:
        frm = Frame(source=self.source, source_size=(self.width, self.height))
        frm.attach()

        objp = np.zeros((self.board_size[0] * self.board_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.board_size[0], 0:self.board_size[1]].T.reshape(-1, 2)
        objp *= self.square_size

        obj_points = []
        left_image_points = []
        right_image_points = []

        count = 0

        while count < capture_count:
            ret, left_frame, right_frame = frm.read()

            left_gray = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
            right_gray = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)

            left_ret, left_corners = cv2.findChessboardCorners(left_gray, self.board_size, None, cv2.CALIB_CB_FAST_CHECK)
            right_ret, right_corners = cv2.findChessboardCorners(right_gray, self.board_size, None, cv2.CALIB_CB_FAST_CHECK)

            for ret, frame, corners in ((left_ret, left_frame, left_corners), (right_ret, right_frame, right_corners)):
                if ret:
                    cv2.drawChessboardCorners(frame, self.board_size, corners, ret)
                    cv2.putText(frame, "RECOGNIZED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                else:
                    cv2.putText(frame, "NOT RECOGNIZED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                cv2.putText(frame, f"PROGRESS : {count} / {capture_count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("StereoX2 - LEFT CAMERA", left_frame)
            cv2.imshow("StereoX2 - RIGHT CAMERA", right_frame)

            keycode = cv2.waitKey(1) & 0xFF
            if keycode == trigger:
                if left_ret and right_ret:
                    obj_points.append(objp)
                    left_image_points.append(left_corners)
                    right_image_points.append(right_corners)
                    count += 1
            elif keycode == exit_trigger:
                break

        frm.detach()

        return cv2.stereoCalibrate(
            obj_points, left_image_points, right_image_points,
            None, None, None, None,
            left_gray.shape[::-1],
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5),
            flags=cv2.CALIB_FIX_INTRINSIC
        )

    def export(self, data: tuple, path: str = "calibration.npz"):
        try:
            ret, mtx1, dist1, mtx2, dist2, R, T, E, F = data
            np.savez(path, cameraMatrix1=mtx1, distCoeffs1=dist1,
                        cameraMatrix2=mtx2, distCoeffs2=dist2, R=R, T=T)
            log.success(f"'{path}'에 캘리브레이션 파일을 성공적으로 저장했습니다.")
        except Exception as ex:
            log.error(f"'{path}'에 캘리브레이션 파일을 내보내던 중 문제가 발생하였습니다.", ex)