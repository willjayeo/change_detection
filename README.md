# change_detection #

Make simple change detection map from two single band satellite images.

## Installation ##

You can install the dependencies to run this program by creating a conda environment with the provided YAML file:

```bash
conda env create -f environment.yml
```

This should create a new environment called `change_detection` which you can activate with:

```bash
conda activate change_detection
```

## Usage ##

This program creates a change map of two single band images, such as satellite data spectral bands. Identify the appropriate bands that have the clearest contrast of the features you want to visualise the change of and input them as arguments for the`change_detection_map.py` script.

Run the code by executing `change_detection_map.py` script. It requires two arguments:

 * `--image_a` or `-a`: The path to the first input image
 * `--image_b` or `-b`: The path to the second input image

There are two further optional arguents:

 * `--rgb`: This allows you to control what colour channel each image uses. It expects a string of three characters, either 'a', 'b' or '0'. 'a' represents `--image_a`, 'b' represents `--image_b` and '0' represents an empty channel. The order of these characters need to follow the order you would like them assigned to the Red, Green and Blue channels, in that order.
 * `--bbox`: This allows you to input a bounding box of coordinates to spatially subset an area of interest for the output image. These coordinates must match the input data coordinate system. It expects four coordinates in the order of:
 1) Minimum longitude
 2) Maximum longitude 
 3) Minimum latitude
 4) Maximum latitude

Examples:

 * `--rgb abb` would procude a map where 'bright' pixels in image a but not in image b would be red, 'bright' pixels in image b but not in image a would be cyan, pixels of equal brightness would be greyscale. The output image comprises the following channels:
  * Red:   `--image_a`
  * Green: `--image_b`
  * Blue:  `--image_b`
 * `--rgb a0b` would procude a map where 'bright' pixels in image a but not in image b would be red, 'bright' pixels in image b but not in image a would be blue, pixels of equal brightness would be greyscale. The output image comprises the following channels:
  * Red:  `--image_a`
  * Green: empty
  * Blue:  `--image_b`

Example below using two Landsat 5 band images:

```bash
image_a_path=~/data/change_detection/aral_sea/inputs/LT05_L1TP_161028_19880602_20200917_02_T1_B5.TIF
image_b_path=~/data/change_detection/aral_sea/inputs/LT05_L1TP_161028_20100530_20200824_02_T1_B5.TIF

./change_detection_map.py -a ${image_a_path} -b ${image_b_path}
```

These images are from the same location of the Aral Sea. The first image is from 1988 and the second image is from 2010, where a significant reduction of water is visible.

The Landsat 5 Thematic Mapper band 5 was chosen as this measures the radiance of shortwave infrared which is strongly absorbed by water, giving a strong contrast between the land and water we want to visualise the change of.

Below is the output of this change map. Blue pixels represent pixels that are bright (land) in the second image and dark (water) in the first image.

[Shrinking of the Aral Sea](docs/images/aral_sea_ltm_19880602-20100917.png "Aral Sea: 1988 - 2010")
