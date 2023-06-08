# amaglyph (WIP)

[![stability-experimental](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#experimental)

Optimization of noisy SVGs through elimination of redundant and/or irrelevant path data points. This is done via Douglas-Ramer-Peucker and Visvalingam-Whyatt line simplification algorithms. 

## About
The project was meant to be an investigation of shape simplification methods and can be used for any such purpose with only minor alterations.
However, the higher purpose lies in storage-efficient digitization of monochromatic shapes - such as glyphs in a typeface. 
This allows for usage in OCR-related tasks such as synthetic data generation and is particularly useful when it comes to historical printings, 
which may feature typefaces that aren't unavailable in digital form or characters outside the standard Unicode range.

## Next steps

- [ ] Extraction pipeline for raster images: segmentation, contour finding, extraction of data points etc. etc.
- [ ] Bezier curve from data points
- [ ] Translation of the optimized path back to SVG coordinates 
- [ ] Search for the best starting point
- [ ] ...
