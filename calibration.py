from StereoX2 import Preview

pre = Preview(source=0, source_size=(2560, 720))

pre.source_preview(line=15)
pre.calibration_preview(line=15)
pre.roi_preview(line=15)
pre.overlap_preview(line=15)
pre.depth_preview(num_disparities=160, block_size=25)
