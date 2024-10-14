from StereoX2 import Calibration, Preview, Logger

SOURCE = 0
SOURCE_SIZE = (2560, 720)

# cali = Calibration(source=SOURCE, source_size=SOURCE_SIZE, board_size=(8, 6), square_size=0.025)
pre = Preview(source=SOURCE, source_size=SOURCE_SIZE)

# data = cali.start()
# cali.export(data)

# pre.source_preview(line=15)
pre.calibration_preview(line=25)
# pre.roi_preview(line=15)
# pre.overlap_preview(line=15)

pre.depth_preview(num_disparities=16 * 8,
                  block_size=5,
                  uniqueness_ratio=15,
                  speckle_window_size=150,
                  speckle_range=1)