# StereoX2
Keeworks 스테레오 카메라 라이브러리

## 예제

- ### 캘리브레이션
    ```py
    from StereoX2 import Calibration

    cali = Calibration(source=0, source_size=(2560, 720),
                       board_size=(8, 6), square_size=0.025)

    result = cali.start()   # 캘리브레이션 시작
    cali.export(result)     # 캘리브레이션 파일 내보내기 (.npz)
    ```

- ### 미리보기
    ```py
    from StereoX2 import Preview

    pre = Preview(source=0, source_size=(2560, 720))
    
    pre.source_preview()        # 프레임 미리보기
    pre.calibration_preview()   # 캘리브레이션 미리보기
    pre.roi_preview()           # ROI 영역 미리보기
    pre.overlap_preview()       # 오버랩 미리보기
    pre.depth_preview()         # 뎁스 맵 미리보기
    ```

- ### 렉티피케이션 맵 계산
    ```py
    from StereoX2 import Calculate

    calc = Calculate()

    # 캘리브레이션 데이터 가져오기 & 렉티피케이션 맵 계산
    data = calc.read_calibration()
    map_data = calc.rectification(data, (2560, 720))
    ```

- ### 뎁스 맵 계산
    ```py
    from StereoX2 import Frame, Calculate

    frm = Frame(source=0, source_size=(2560, 720))
    calc = Calculate()

    # 소스 할당 및 읽기
    frm.attach()
    ret, left_frame, right_frame = frm.read()

    # 캘리브레이션 데이터 가져오기 & 렉티피케이션 맵 계산
    data = calc.read_calibration()
    map1x, map1y, map2x, map2y, roi1, roi2 = calc.rectification(data, (2560, 720))

    # 렉티피케이션 맵 매핑
    left_rectified, right_rectified = calc.mapping((left_frame, map1x, map1y),
                                                   (right_frame, map2x, map2y))

    # ROI 프레임 가져오기
    left_roi, right_roi = calc.get_roi(left_rectified, right_rectified, roi1, roi2)

    # 뎁스 맵 계산
    depth = calc.depth(left_roi, right_roi)
    ```

## 패키지 빌드
```sh
conda create -n StereoX2 python=3.11    # 개발 환경 생성
conda activate StereoX2                 # 개발 환경 활성화
pip install -r requirements.txt         # 필수 패키지 설치

python setup.py sdist bdist_wheel       # 패키지 빌드 (.whl)
                                        # .whl 파일은 dist 폴더 내에 빌드됩니다.
```

## 패키지 설치
```sh
conda create -n [env_name] python=3.11  # 개발 환경 생성
conda activate [env_name]               # 개발 환경 활성화

pip install [whl_file_path]             # 패키지 설치
```

## 기여자
- 미래 광학기술 연구소 - [현장실습생 강찬영](https://github.com/BackGwa)