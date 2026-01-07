#!/usr/bin/env python

import argparse
import dateutil.parser as dp
import glob
import os
import pyart
import re
import subprocess

from netCDF4 import Dataset
#imports the databasehandler module
from abcunit_backend.database_handler import DataBaseHandler
#from convert import SETTINGS
import SETTINGS


def arg_parse_hour():
    """
    Parses arguments given at the command line

    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    type_choices = ['vol', 'ele', 'azi']

    parser.add_argument('-t', '--scan_type',  nargs=1, type=str,
                        choices=type_choices, required=True,
                        help=f'Type of scan, one of: {type_choices}',
                        metavar='')
    # Not sure if this will work along side having a tagged parameter
    parser.add_argument('hours', nargs='+', type=str, help='The hours you want '
                        'to run in the format YYYYMMDDHH', metavar='')

    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')

    return parser.parse_args()


def _map_scan_type(type):
    """
    Converts (two way) between <> scan names and <> scan names.

    :param type: (str) Scan type in either <> or <> format

    :return: (str) Converted scan type
    """

    scan_dict = {
        'vol': 'vol',
        'ele': 'rhi',
        'azi': 'birdbath',
        'SUR': 'vol',
        'RHI': 'rhi',
        'VER': 'azi'
    }

    if type in scan_dict:
        return scan_dict[type]

    raise KeyError(f'Cannot match scan type {type}')


def _get_input_files(hour, scan_type):
    """
    Finds raw input files from SETTINGS.INPUT_DIR

    :param hour: (str) Hour of the data in the format YYYYMMDDHH
    :param scan_type: (str) Type of scan, one of 'vol', 'ele', or 'azi'

    :return: Sorted list of raw input file paths
    """

    # Probably needs a try round it to format check
    date_dir = None
    try:
        date_dir = dp.isoparse(hour[:-2]).strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError('[ERROR] DateHour format is incorrect, '
                         'should be YYYYMMDDHH')

    files_path = SETTINGS.INPUT_DIR
#    print(files_path)
    # They're all dirs but feels good to check
    dirs = [name for name in os.listdir(files_path) if os.path.isdir(os.path.join(files_path, name))]
    print('dirs = ', dirs)

    # Pattern to find data folders (anything that has an underscore .scan_type)
    if scan_type == 'azi':
        pattern = re.compile(f"^.*.azi$")
    else:
        pattern = re.compile(f"^.*_.*.{scan_type}$")

    filtered_dirs = [os.path.join(files_path, name) for name in dirs if pattern.match(name)]
    print('filtered dirs = ', filtered_dirs) 
    dbz_files = []

    for dr in filtered_dirs:
        target_dir = f'{dr}/{date_dir}'
        print(target_dir)
        if os.path.exists(target_dir):
            #print(target_dir)
            files = os.listdir(target_dir)
            pattern = re.compile(f"^{hour}.*dBZ.{scan_type}$")
            dbz_files.extend([os.path.join(target_dir, fname) for fname in files if pattern.match(fname)])
    return sorted(set(dbz_files))


def loop_over_hours(args):
    """
    Processes each file for each hour passed in the comand line arguments.

    :param args: (namespace) Namespace object built from attributes parsed
    from command line
    """

    scan_type = args.scan_type[0]
    hours = args.hours
    table = args.table_name[0]

# error types are bad_num (different number of variables in raw vs nc)
# failure (RadxConvert doesnt complete) and bad_output (no output file found)
    #rh = _get_results_handler(4, '.')
    #rh = DataBaseHandler(table_name=table)
    rh = DataBaseHandler(table_name=table)

    failure_count = 0
    mapped_scan_type = _map_scan_type(scan_type)

    for hour in hours:

        print(f'[INFO] Processing: {hour}')

        input_files = _get_input_files(hour, scan_type)
        print(input_files)
        year, month, day = hour[:4], hour[4:6], hour[6:8]
        date = year + month + day

        for dbz_file in input_files:

            if failure_count >= SETTINGS.EXIT_AFTER_N_FAILURES:
                raise ValueError('[WARN] Exiting after failure count reaches limit: '
                                 f'{SETTINGS.EXIT_AFTER_N_FAILURES}')

            fname = os.path.basename(dbz_file)
            input_dir = os.path.dirname(dbz_file)
            
            #This is the file identifier used in the database
            identifier = f'{year}.{month}.{day}.{os.path.splitext(fname)[0]}'
            print(identifier)

            # Check if this file has already been processed successfully
            #If yes, then go to the next iteration of the loop, i.e. next file
            if rh.ran_successfully(identifier):
                print(f'[INFO] Already ran {dbz_file} successfully')
                continue

            if rh.get_result(identifier)=='bad_num':
                print(f'[INFO] Already ran {dbz_file} with mismatched input/output vars')
                #continue

            #If there is no success identifier then continue processing the file
            # Remove previous results for this file
            rh.delete_result(identifier)

            # Get expected variables
            fname_base = fname[:16]
            time_digits = fname[8:14]

#            #Check if the filename time is the actual starttime, as some data we didn't put the "time operator" in Rainbow in the correct place
#
#            result = subprocess.run(["grep", "-ira","<starttime>", dbz_file],capture_output=True, text=True)
#            match = re.search(r"(\d{2}:\d{2}:\d{2})", result.stdout)
#            real_starttime=match.group(0).replace(":", "")
#            if time_digits==real_starttime:
#                true_time_digits=time_digits
#            else:
#                true_time_digits=real_starttime

            pattern = f'{input_dir}/{fname_base}*.{scan_type}'
            expected_vars = set([os.path.splitext(os.path.basename(name)[16:])[0] for name in glob.glob(pattern)])

            # 'Process the uncalibrated data' (where output is generated)
            script_cmd = f"RadxConvert -v -params {SETTINGS.PARAMS_FILE} -f {dbz_file}"
            print(f'[INFO] Running: {script_cmd}')
            #If RadxConvert fails, create a failure outcome in the database 
            if subprocess.call(script_cmd, shell=True) != 0:
                print('[ERROR] RadxConvert call resulted in an error')
                rh.insert_failure(identifier, 'failure')
                failure_count += 1
                continue

            # Check for expected netcdf output
            scan_dir_name = None

            if mapped_scan_type == 'VER':
                scan_dir_name = 'birdbath'
            else:
                scan_dir_name = mapped_scan_type.lower()

            # This should probably be a default path that is formatted
#            expected_file = f'{SETTINGS.OUTPUT_DIR}/{scan_dir_name}/{date}/' \
#                            f'{SETTINGS.RADAR_LONG}_{SETTINGS.PLATFORM}_{date}-{true_time_digits}_{mapped_scan_type}_v1.0.0.nc'
            expected_file = f'{SETTINGS.OUTPUT_DIR}/{scan_dir_name}/{date}/' \
                            f'{SETTINGS.RADAR_LONG}_{SETTINGS.PLATFORM}_{date}-{time_digits}_{mapped_scan_type}_v1.0.0.nc'

            # Read netcdf file to find variables
            # If the file can't be found, create a bad_output failure identifier
            #found_vars = None
            try:
                 rad2=pyart.io.read(expected_file, delay_field_loading=True)
#                ds = Dataset(expected_file, 'r', format="NETCDF4")
#                found_vars = set(ds.variables.keys())
#                ds.close()
            except FileNotFoundError:
                print(f'[ERROR] Expected file {expected_file} not found')
                rh.insert_failure(identifier, 'bad_output')
                failure_count += 1
                continue
            else:
                output_vars=set(rad2.fields.keys())

            print('[INFO] Checking that the output variables match those in the input files')
            #print('expected vars = ', expected_vars)
            #print('output_vars = ', output_vars)

            #Checks that the variables in the nc file are identical to the variables in the input files
            #If not, create a failure identifier called bad_num
            if not expected_vars.issubset(output_vars):
                print('[ERROR] Output variables are not the same as input files'
                      f'{output_vars} != {expected_vars}')
                failure_count += 1
                rh.insert_failure(identifier, 'bad_num')
                continue
            else:
                print(f'[INFO] All expected variable were found: {expected_vars}')

            # If all of the above is succesful, create a success identifier
            rh.insert_success(identifier)

    #rh.close()


def main():
    """Runs script if called on command line"""

    args = arg_parse_hour()
    loop_over_hours(args)


if __name__ == '__main__':
    main()
