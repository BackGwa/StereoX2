# StereoX2
Keeworks Stereo Camera Library

## Example

- ### Calibration 
    ```py
    # Example Code
    ```

## Package Build
```sh
conda create -n StereoX2 python=3.11    # Create Environment
conda activate StereoX2                 # Activate Environment
pip install -r requirements.txt         # Requirements Package Install

python setup.py sdist bdist_wheel       # Package Build (.whl)
                                        # .whl file is built inside the dist folder.
```

## Package Install
```sh
conda create -n [env_name] python=3.11  # Create Environment
conda activate [env_name]               # Activate Environment

pip install [whl_file_path]             # Install Package
```

## Contributor
- 미래 광학기술 연구소 - [현장실습생 강찬영](https://github.com/BackGwa)