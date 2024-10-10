# StereoX2
Keeworks 스테레오 카메라 라이브러리

## 예제

- ### 캘리브레이션
    ```py
    from StereoX2 import Calibration

    # 캘리브레이션 인스턴스 생성
    cali = Calibration(source=0, source_size=(2560, 720),
                       board_size=(8, 6), square_size=0.025)

    result = cali.start()   # 캘리브레이션 시작
    cali.export(result)     # 캘리브레이션 파일 내보내기 (.npz)
    ```

- ### 미리보기
    ```py
    from StereoX2 import Preview

    pv = Preview(source=0, source_size=(2560, 720))
    
    pv.source_preview()         # 프레임 미리보기
    pv.calibration_preview()    # 캘리브레이션 미리보기
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