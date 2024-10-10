from StereoX2 import Calibration, Preview

SOURCE = 0
SOURCE_SIZE = (2560, 720)

pv = Preview(SOURCE, SOURCE_SIZE)
pv.source_preview()
pv.calibration_preview()