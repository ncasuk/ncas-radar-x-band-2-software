import SETTINGS
import os
import re
import argparse
import dateutil.parser as dp
from datetime import date
from datetime import timedelta
import subprocess
import glob

def arg_parse_all():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start_date', nargs=1, required=True, 
                        default=SETTINGS.MIN_START_DATE, type=str, 
                        help=f'Start date string with format YYYYMMDDHHmmSS, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs=1, required=True, 
                        default=SETTINGS.MAX_END_DATE,type=str, 
                        help=f'End date string in format YYYYMMDDHHmmSS, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    
    return parser.parse_args()

def loop_over_days(args):
 
    """ 
    Runs update_metadata_day.py for each day in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    today = date.today().strftime("%Y%m%d")
    table = args.table_name[0]

    #Set up directory for Lotus output files based on today's date
    if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
        os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))

    start_date = args.start_date[0]
    end_date = args.end_date[0]

    min_start_date = dp.isoparse(SETTINGS.MIN_START_DATE)
    max_end_date = dp.isoparse(SETTINGS.MAX_END_DATE)

    #validate dates
    try:
        start_date_dt = dp.isoparse(start_date) 
        end_date_dt = dp.isoparse(end_date) 
    except ValueError:
        raise ValueError('[ERROR] Date format is incorrect, should be YYYYMMDD')

    if start_date_dt < min_start_date or end_date_dt > max_end_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    current_date_time = start_date_dt
    script_directory = os.path.dirname(os.path.abspath(__file__))

    while current_date_time <= end_date_dt:

        current_date = current_date_time.strftime("%Y%m%d")
        print(f"[INFO] Running for: {current_date}")

        cmd = f"python {script_directory}/update_metadata_day.py -d {current_date} -n {table}"
        print(f"[INFO] Running: {cmd}")
        subprocess.call(cmd, shell=True)

        current_date_time += timedelta(days=1)

def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)

if __name__ == '__main__':
    main() 
