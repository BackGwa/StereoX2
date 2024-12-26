import cv2
import numpy as np
from .frame_mvs import MVSFrame
from .logger import Logger

log = Logger("Calibration", "log/Calibration")

class Calibration:
    def __init__(self, left_source: int, right_source: int, board_size: tuple, square_size: float):
        """
        Calibration 객체를 초기화합니다.

        :param left_source: 좌측 카메라 소스 번호
        :param right_source: 우측 카메라 소스 번호
        :param board_size: 체스보드의 (열, 행) 튜플
        :param square_size: 체스보드의 각 사각형 크기
        """
        self.left_source = left_source
        self.right_source = right_source
        self.board_size = board_size
        self.square_size = square_size

    def start(self, capture_count: int = 128, trigger: int = 32, exit_trigger: int = 27) -> tuple:
        """
        캘리브레이션 프로세스를 시작합니다.

        :param capture_count: 캡처할 이미지 수
        :param trigger: 캡처를 트리거하는 키 코드
        :param exit_trigger: 캡처 프로세스를 종료하는 키 코드
        :return: 캘리브레이션 데이터 튜플
        """
        try:
            frm = MVSFrame(self.left_source, self.right_source)
            frm.attach()

            objp = np.zeros((np.prod(self.board_size), 3), np.float32)
            objp[:, :2] = np.indices(self.board_size).T.reshape(-1, 2)
            objp *= self.square_size

            obj_points = []
            left_image_points = []
            right_image_points = []

            count = 0

            log.alert("캘리브레이션 캡처 프로세스를 시작합니다.")

            while count < capture_count:
                ret, left_frame, right_frame = frm.read()
                if not ret:
                    log.warn("프레임 캡처에 실패했습니다. 건너뜁니다...")
                    continue

                # left_gray = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
                # right_gray = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)

                left_ret, left_corners = cv2.findChessboardCorners(left_frame, self.board_size, None, cv2.CALIB_CB_FAST_CHECK)
                right_ret, right_corners = cv2.findChessboardCorners(right_frame, self.board_size, None, cv2.CALIB_CB_FAST_CHECK)

                for ret, frame, corners, label in [
                    (left_ret, left_frame, left_corners, "LEFT"),
                    (right_ret, right_frame, right_corners, "RIGHT")
                ]:
                    status = "RECOGNIZED" if ret else "NOT RECOGNIZED"
                    color = (0, 255, 0) if ret else (0, 0, 255)
                    frame = cv2.cvtColor(frame.copy(), cv2.COLOR_GRAY2BGR)
                    if ret:
                        cv2.drawChessboardCorners(frame, self.board_size, corners, ret)
                    cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
                    cv2.putText(frame, f"PROGRESS : {count} / {capture_count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.namedWindow(f"StereoX2 - {label} CAMERA", cv2.WINDOW_FREERATIO)
                    cv2.imshow(f"StereoX2 - {label} CAMERA", frame)

                keycode = cv2.waitKey(1) & 0xFF
                if keycode == trigger:
                    if left_ret and right_ret:
                        obj_points.append(objp)
                        left_image_points.append(left_corners)
                        right_image_points.append(right_corners)
                        count += 1
                        log.alert(f"프레임 {count}/{capture_count} 캡처됨")
                    else:
                        log.warn("양쪽 프레임에서 체스보드가 감지되지 않았습니다. 건너뜁니다...")
                elif keycode == exit_trigger:
                    log.alert("사용자에 의해 캡처 프로세스가 종료되었습니다.")
                    break

            frm.detach()

            if count < capture_count:
                log.warn(f"캡처 프로세스가 조기에 종료되었습니다. {count}/{capture_count} 프레임만 캡처되었습니다.")
            
            log.alert("개별 카메라 캘리브레이션을 시작합니다.")

            # 임시 코드 추가
            ret1, mtx1, dist1, _, _ = cv2.calibrateCamera(obj_points, left_image_points, left_frame.shape[::-1], None, None)
            ret2, mtx2, dist2, _, _ = cv2.calibrateCamera(obj_points, right_image_points, right_frame.shape[::-1], None, None)

            log.success("개별 카메라 캘리브레이션이 성공적으로 완료되었습니다.")

            log.alert("스테레오 캘리브레이션을 시작합니다... 이 작업은 오랜 시간이 소요됩니다.")

            calibrate_data = cv2.stereoCalibrate(
                obj_points, left_image_points, right_image_points,
                mtx1, dist1, mtx2, dist2,
                left_frame.shape[::-1],
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5),
                flags=cv2.CALIB_FIX_INTRINSIC
            )

            log.success("캘리브레이션이 성공적으로 완료되었습니다.")
            return calibrate_data

        except Exception as ex:
            log.error(f"캘리브레이션 중 오류가 발생했습니다.", ex)

    def export(self, data: tuple, path: str = "calibration.npz"):
        """
        캘리브레이션 데이터를 파일로 내보냅니다.

        :param data: 캘리브레이션 데이터 튜플
        :param path: 캘리브레이션 파일을 저장할 경로
        """
        try:
            ret, mtx1, dist1, mtx2, dist2, R, T, E, F = data
            np.savez(path, cameraMatrix1=mtx1, distCoeffs1=dist1,
                     cameraMatrix2=mtx2, distCoeffs2=dist2, R=R, T=T)
            log.success(f"캘리브레이션 데이터가 '{path}'에 성공적으로 저장되었습니다.")
        except Exception as ex:
            log.error(f"'{path}'에 캘리브레이션 데이터를 내보내는 데 실패했습니다.", ex)