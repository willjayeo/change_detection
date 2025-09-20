#! /usr/bin/env python
"""
Create a simple change detection map from two single band satellite images in a GDAL supported format
Author Will Jay (willjayeo). October 2022
"""

import argparse
import logging
import xarray


def main(input1_img, input2_img, verbose=False, debug=False):
    """ """

    # Set logging level as defined from command line. Otherwise default to only log
    # warnings and errors
    if debug:
        logging.setLevel(logging.DEBUG)
    elif verbose:
        logging.setLevel(logging.INFO)
    else:
        logging.setLevel(logging.WARNING)

    # Open data with xarray
    xarray.open_dataset(input1_img)
    xarray.open_dataset(input2_img)

    # TODO: CROP AREA OF INTEREST WITH COORDINATES

    # TODO: CONTRAST STRETCH THE IMAGES

    # TODO: ASSIGN RGB BANDS TO THE TWO IMAGES

    # TODO WRITE OUT RGB MAP, PERHAPS AS A NICE PLOT?
    # Create plot


if __name__ == "__main__":
    helpstring = (
        "Make simgple change detection map from two single band satellite images in a "
        "GDAL supported format or netCDF"
    )
    parser = argparse.ArgumentParser(
        description=helpstring,
        formatter_class=argparse.RawDescriptionsHelpFormatter,
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
    parser.add_argument(
        "-v",
        "--verbose",
        type=bool,
        default=False,
        required=True,
        action="store_true",
        help="Display updates of processing",
    )
    parser.add_argument(
        "--debug",
        type=bool,
        default=False,
        required=False,
        action="store_true",
        help="Display debugging information",
    )

    cmdline = parser.parse_args()

    main(cmdline.img_a, cmdline.img_b, cmdline.verbose, cmdline.debug)
