import numpy as np
import pandas as pd
import warnings
import os
import argparse
import dateutil.parser as dp
import re
import SETTINGS
from abcunit_backend.database_handler import DataBaseHandler
import sys
sys.path.append('/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-radar-x-band-2/')
import utilities
from utilities import calib_functions_teamx

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)

def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--date', nargs=1, required=True, type=str, 
                        help=f'Date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    
    return parser.parse_args()

def process_volume_scans(args):

    """ 
    Processes the volume scans for each day with rain present, to calculate Z bias
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    date=args.date[0]
    print('Processing ',date)
    day_dt = dp.parse(date)
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)

    if day_dt < min_date or day_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    #Directory for input radar data
    inputdir=SETTINGS.VOLUME_DIR
    #scan type sub directory
    #scan_type = SETTINGS.SCAN_TYPE

    #Directory for zdr_ml data
    zdrdir=SETTINGS.ZDR_CALIB_DIR

    #Directory for output calibration data
    zdir=SETTINGS.Z_CALIB_DIR
    outdir= f'{zdir}'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    rh = DataBaseHandler(table_name=f'process_vol_scans_nxpol2_zdr2')

    identifier = f'{date}'

    #If there is no success or a no_rays identifier, continue to process the data
    result=rh.get_result(identifier) 
    if rh.ran_successfully(identifier) or result=='no rays':
        print(f'[INFO] Already processed {date}')

    else:
        fhfile = f'{zdrdir}/freezing_levels.csv'
        fhdata = pd.read_csv(fhfile,index_col=0, parse_dates=True)
        raddir = os.path.join(inputdir, date)
        #print raddir, outdir, date
        if calib_functions_teamx.calibrate_day_att(raddir, outdir, date, fhdata, 0.31):
            rh.insert_success(identifier)
            print("File successfully processed")
        else:
            rh.insert_failure(identifier, 'no suitable rays')
            print("No suitable rays")

def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    process_volume_scans(args)

if __name__ == '__main__':
    main()
