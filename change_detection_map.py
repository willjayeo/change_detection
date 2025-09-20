#! /usr/bin/env python
"""
Create a simple change detection map from two single band satellite images in a GDAL supported format
Author Will Jay (willjayeo). October 2022
"""

import argparse
import logging
import numpy
import xarray

from matplotlib import pyplot


def setup_logger(verbose: bool = False, debug: bool = False):
    # Set logging level as defined from command line. Otherwise default to only log
    # warnings and errors
    if debug:
        logging.setLevel(logging.DEBUG)
    elif verbose:
        logging.setLevel(logging.INFO)
    else:
        logging.setLevel(logging.WARNING)


def main(img_a_path: str, img_b_path: str, verbose=False, debug=False):
    """ """

    # Open data with xarray
    img_a_dataset = xarray.open_dataset(img_a_path)
    img_b_dataset = xarray.open_dataset(img_b_path)

    # Get numpy arrays from datasets
    # TODO: Output should have the shape (1, 1, rows, cols). Dimension 1 is band, dimension 2 is spatial reference?
    img_a_array = img_a_dataset.to_dataarray()
    img_b_array = img_b_dataset.to_dataarray()

    # Get data value ranges
    min_a = img_a_array.min()
    max_a = img_a_array.max()
    min_b = img_b_array.min()
    max_b = img_b_array.max()

    range_a = max_a - min_a
    range_b = max_b - min_b

    if max_a > max_b:
        range_max = max_a
    else:
        range_min = max_b

    if min_a < min_b:
        range_min = min_a
    else:
        range_min = min_b

    data_range = range_max - range_min

    # Normalise data
    img_a_array_normalised = (img_a_array - range_min) / data_range
    img_b_array_normalised = (img_b_array - range_min) / data_range

    # TODO: Get a good contrast?

    # Stack arrays into RGB
    # TODO: Use differnt cases to control colour
    rgb_array = numpy.vstack(
        (img_a_array_normalised, img_a_array_normalised, img_b_array_normalised)
    )

    # Drop the spatial reference dimension (index 1)
    rgb_array = numpy.squeeze(rgb_array, axis=1)

    # Transpose dimensions so that it has the shape of (row, col, band)
    rgb_array = rgb_array.transpose((1, 2, 0))

    pyplot.imshow(rgb_array, interpolation="nearest")
    pyplot.show()

    # TODO: Resample to larger pixel array if inputs are differnt grids

    # TODO: CROP AREA OF INTEREST WITH COORDINATES

    # TODO: CONTRAST STRETCH THE IMAGES

    # TODO: ASSIGN RGB BANDS TO THE TWO IMAGES

    # TODO WRITE OUT RGB MAP, PERHAPS AS A NICE PLOT?
    # Create plot


if __name__ == "__main__":
    helpstring = (
        "Make single change detection map from two single band satellite images"
    )
    parser = argparse.ArgumentParser(
        description=helpstring,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-a",
        "--img_a",
        type=str,
        default=None,
        required=True,
        help="Path to first input image",
    )
    parser.add_argument(
        "-b",
        "--img_b",
        default=None,
        required=True,
        help="Path to second input image",
    )

    cmdline = parser.parse_args()

    main(cmdline.img_a, cmdline.img_b)
