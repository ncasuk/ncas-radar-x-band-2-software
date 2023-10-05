#!/usr/bin/env python

import argparse
import dateutil.parser as dp
import glob
import os
import re
import subprocess

from netCDF4 import Dataset
#imports the databasehandler module
from abcunit_backend.database_handler import DataBaseHandler
import SETTINGS


def arg_parse_hour():
    """
    Parses arguments given at the command line

    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['sur', 'rhi']

    parser.add_argument('-t', '--scan_type',  nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',
                        metavar='')
 
    parser.add_argument('hours', nargs='+', type=str, help='The hours you want '
                        'to run in the format YYYYMMDDHH', metavar='')

    return parser.parse_args()


def _get_input_files(hour, scan_type):
    """
    Finds input files from SETTINGS.INPUT_DIR

    :param hour: (str) Hour of the data in the format YYYYMMDDHH

    :return: Sorted list of input file paths
    """

    date_dir = None
    try:
        date_dir = dp.isoparse(hour[:-2]).strftime("%Y%m%d")
    except ValueError:
        raise ValueError('[ERROR] DateHour format is incorrect, '
                         'should be YYYYMMDDHH')

    files_path = SETTINGS.INPUT_DIR

    dbz_files = glob.glob(f"{files_path}/{scan_type}/{hour[:-2]}/*{hour[:-2]}-{hour[-2:]}*.nc")
    return dbz_files

def loop_over_hours(args):
    """
    Processes each file for each hour passed in the comand line arguments.

    :param args: (namespace) Namespace object built from attributes parsed
    from command line
    """

    scan_type = args.scan_type[0]
    hours = args.hours

# error types are failure (RadxPid doesnt complete) and bad_output (no output file found)
    rh = DataBaseHandler(table_name="pid_results")

    failure_count = 0

    for hour in hours:

        print(f'[INFO] Processing: {hour}')

        input_files = _get_input_files(hour, scan_type)

        year, month, day = hour[:4], hour[4:6], hour[6:8]
        date = year + month + day

        for dbz_file in input_files:

            if failure_count >= SETTINGS.EXIT_AFTER_N_FAILURES:
                raise ValueError('[WARN] Exiting after failure count reaches limit: '
                                 f'{SETTINGS.EXIT_AFTER_N_FAILURES}')

            fname = os.path.basename(dbz_file)
            input_dir = os.path.dirname(dbz_file)
            
            #This is the file identifier used in the database
            identifier = fname[36:55]

            # Check if this file has already been processed successfully
            #If yes, then go to the next iteration of the loop, i.e. next file
            if rh.ran_successfully(identifier):
                print(f'[INFO] Already ran {dbz_file} successfully')
                continue

            #If there is no success identifier then continue processing the file
            # Remove previous results for this file
            rh.delete_result(identifier)

            time_digits = fname[45:51]

            # Run RadxPid
            script_cmd = f"RadxPid -v -params {SETTINGS.PARAMS_FILE} -f {dbz_file}"
            print(f'[INFO] Running: {script_cmd}')
            #If RadxPid fails, create a failure outcome in the database 
            if subprocess.call(script_cmd, shell=True) != 0:
                print('[ERROR] RadxPid call resulted in an error')
                rh.insert_failure(identifier, 'failure')
                failure_count += 1
                continue

            expected_file = f'{SETTINGS.OUTPUT_DIR}/{date}/' \
                            f'cfrad.{date}_{time_digits}.000_ncas-mobile-x-band-radar-1_{scan_type.upper()}.nc'

            # Check netcdf file exists and can be opened
            # If the file can't be found, create a bad_output failure identifier
            try:
                ds = Dataset(expected_file, 'r', format="NETCDF4")
                found_vars = set(ds.variables.keys())
                ds.close()
            except FileNotFoundError:
                print(f'[ERROR] Expected file {expected_file} not found')
                rh.insert_failure(identifier, 'bad_output')
                failure_count += 1
                continue

            # If all of the above is succesful, create a success identifier
            rh.insert_success(identifier)

    rh.close()


def main():
    """Runs script if called on command line"""

    args = arg_parse_hour()
    loop_over_hours(args)


if __name__ == '__main__':
    main()
