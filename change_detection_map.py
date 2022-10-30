#! /usr/bin/env python
"""
Create a simple change detection map from two single band satellite images in a GDAL supported format or netCDF

Author Will Jay (willjayeo). October 2022
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from cartopy import config
from osgeo import gdal, osr

from . import exceptions

gdal.UseExceptions()


def setup_gdal_drivers(gdal_format, verbose):
    """
    Setup the correct GDAL drivers for writing data to the desired format
    """

    driver = gdal.GetDriverByName(gdal_format)
    metadata = driver.GetMetadata()

    if gdal.DCAP_CREATE in metadata and metadata[gdal.DCAP_CREATE] == "YES":
        logging.debug(
            "Driver {driver} supports `Create()` method".format(driver=driver)
        )
    else:
        raise exceptions.UnsupportedFormatError(
            "GDAL does not support writing data in the '{format}' format".format(
                gdal_format
            )
        )
    if gdal.DCAP_CREATECOPY in metadata and metadata[gdal.DCAP_CREATECOPY] == "YES":
        logging.debug(
            "Driver {driver} supports `CreateCopy()` method".format(driver=driver)
        )
    else:
        raise exceptions.UnsupportedFormatError(
            "GDAL does not support writing data in the '{format}' format".format(
                format=gdal_format
            )
        )

    return driver


def open_img_gdal(img_path):
    """
    Return GDAL dataset object and numpy array of values of a single band image
    """

    # Open image
    ds = gdal.Open(img_path)

    # Return error if there's more than one band
    bands_len = ds.RasterCount
    if bands_len > 1:
        raise IOError(
            "Data {path} has {n} bands. Please input an image with one band "
            "only".format(path=img_path, n=bands_len)
        )
    
    # Open band
    band = ds.GetRasterBand(1)
    # Open band data as numpy array
    array = band.ReadAsArray()

    return ds, array


def get_exent(ds):
    """
    Return data extent as a list in the format of [min_x, max_x, min_y, max_y]
    """

    # Get GDAL geographic information
    x_min, x_res, x_rot, y_min, y_rot, y_res = ds.GetGeoTransform()

    # Get pixel size
    x_pix_size = ds.RasterXSize
    y_pix_size = ds.RasterYSize

    # Calculate minimum extent
    x_min = min_x + (x_pix_size * x_res)
    y_max = min_y + (y_pix_size * y_res)

    # Return extent as a list
    extent = [min_x, max_x, min_y, max_y]

    return extent


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

    # Open data with GDAL
    ds1, array1 = open_img_gdal(input1_img)
    ds2, array1 = open_img_gdal(input2_img)

    #TODO: CROP AREA OF INTEREST WITH COORDINATES

    # Get projection information as WKT
    proj = ds.GetProjection()
    inproj = osr.SpatialReference()
    inproj.ImportFromWkt(proj)
    # Convert WKT to cartopy projection
    proj_cs = inproj.GetAuthorityCode("PROJCS")
    projection = ccrs.epsg(proj_cs)

    # Get extent of imputs
    extent1 = get_extent(ds1)
    extent2 = get_extent(ds2)






    #TODO: CONTRAST STRETCH THE IMAGES


    #TODO: ASSIGN RGB BANDS TO THE TWO IMAGES

    #TODO WRITE OUT RGB MAP, PERHAPS AS A NICE PLOT?
    # Create plot
    subplot = dict(projection=projection)
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=subplot)
    plot = ax.imshow(DATA, transpose((1, 2, 0)), extent=extent)


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

