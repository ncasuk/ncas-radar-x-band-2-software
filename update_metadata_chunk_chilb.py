# FIRST UP, IMPORT MODULES
import numpy as np # For working with the data arrays
import glob # For accessing multiple files using wild cards (useful to loop processing / plotting)
import time
from datetime import datetime
import warnings
from utilities import functions
import netCDF4
from netCDF4 import Dataset
import shutil
import argparse
from abcunit_backend.database_handler import DataBaseHandler
import os
import SETTINGS

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)
#warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def arg_parse_chunk():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--files', nargs='+', required=True,
                        help=f'List of files to process', metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    
    return parser.parse_args()

def loop_over_files(args):

    input_files = args.files
    print("input_files= ",input_files)

    table = args.table_name[0]

    failure_count=0

#    try:
#        os.listdir('/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/woest/level2/')
#    except FileNotFoundError:
#        time.sleep(5)
#        os.listdir('/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/woest/level2/')  

    for ncfile in input_files:

        if failure_count >= SETTINGS.EXIT_AFTER_N_FAILURES:
            raise ValueError('[WARN] Exiting after failure count reaches limit: '
                                 f'{SETTINGS.EXIT_AFTER_N_FAILURES}')

        print("ncfile= ",ncfile)
        ncdate = os.path.basename(ncfile).split('_')[2].replace('-','')
        rh = DataBaseHandler(table_name=table)
        identifier = f'{ncdate}'

        #If there is a success identifier, continue to next file in the loop
        result=rh.get_result(identifier) 
        if rh.ran_successfully(identifier):
            print(f'[INFO] Already processed {ncdate} successfully')
            continue
        #If there is no success identifier then continue processing the file
        # Remove previous results for this file
        rh.delete_result(identifier)

        # Load the data file
        rad = Dataset(ncfile,'a')    

        if 'Sub_conventions' in rad.ncattrs():
            rad.delncattr('Sub_conventions')
        if 'version' in rad.ncattrs(): 
            rad.delncattr('version')

        #Update metadata 
        rad.variables['azimuth'].axis = 'radial_azimuth_coordinate'
        rad.variables['elevation'].axis = 'radial_elevation_coordinate'

        for varname in ['radar_antenna_gain_h', 
                        'radar_antenna_gain_v',
                        'r_calib_two_way_waveguide_loss_h',
                        'r_calib_two_way_waveguide_loss_v',
                        'r_calib_two_way_radome_loss_h',
                        'r_calib_two_way_radome_loss_v',
                        'r_calib_receiver_mismatch_loss',
                        'r_calib_radar_constant_h',
                        'r_calib_radar_constant_v',
                        'r_calib_antenna_gain_h',
                        'r_calib_antenna_gain_v',
                        'r_calib_receiver_gain_hc',
                        'r_calib_receiver_gain_vc',
                        'r_calib_receiver_gain_hx',
                        'r_calib_receiver_gain_vx',
                        'r_calib_dynamic_range_db_hc',
                        'r_calib_dynamic_range_db_vc',
                        'r_calib_dynamic_range_db_hx',
                        'r_calib_dynamic_range_db_vx',
                        'r_calib_power_measure_loss_h',
                        'r_calib_power_measure_loss_v',
                        'r_calib_coupler_forward_loss_h',
                        'r_calib_coupler_forward_loss_v',
                        'r_calib_dbz_correction',
                        'r_calib_zdr_correction',
                        'r_calib_ldr_correction_h',
                        'r_calib_ldr_correction_v']:
            rad.variables[varname].units = 'dB'

        rad.variables['nyquist_velocity'].units = 'm s-1'
        for varname in ['target_scan_rate','scan_rate']:
            try:
                rad.variables[varname].units = 'degrees s-1'
            except:
                print('One or more scan_rate variables does not exist')
                pass

        rad.close() 

#        expected_file = newfile
        print("[INFO] Checking that the output file has been produced.")
#        try:
#            rad2=Dataset(expected_file,'r')
#        except IOError:
#            print(f'[ERROR] Expected file {expected_file} not found')
#            rh.insert_failure(identifier,'bad_output')
#            failure_count += 1
#            continue
#        print(f'[INFO] Found expected file {expected_file}')
        rh.insert_success(identifier)

def main():
    """Runs script if called on command line"""

    args = arg_parse_chunk()
    loop_over_files(args)

if __name__ == '__main__':
    main()    
