import dateutil.parser as dp
from datetime import date
import os
import re
import argparse
import dateutil.parser as dp
from datetime import date
import subprocess
import sys
import SETTINGS

def arg_parse_all():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
#    type_choices = ['bl_scans', 'cloud_scans']

    parser.add_argument('-s', '--start_date', nargs=1, required=True, 
                        default=SETTINGS.MIN_START_DATE, type=str, 
                        help=f'Start date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs=1, required=True, 
                        default=SETTINGS.MAX_END_DATE,type=str, 
                        help=f'End date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
 #   parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
 #   parser.add_argument('-t', '--scan_type', nargs=1, type=str,choices=type_choices, required=True,
 #                       help=f'Type of scan, one of: {type_choices}',
 #                       metavar='')
    
    return parser.parse_args()

def loop_over_days(args):
 
    """ 
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    today = date.today().strftime("%Y-%m-%d")
#    table = args.table_name[0]
  #  scan_type = args.scan_type[0]

    #Set up directory for Lotus output files based on today's date
    if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
        os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))

    start_date = args.start_date[0]
    end_date = args.end_date[0]

    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    #list only date directories
#   inputdir = "/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/woest/level2/sur/"
    inputdir = "/gws/pw/j07/ncas_obs_vol1/amf/raw_data/ncas-radar-x-band-2/incoming/20250603_teamx/teamx_v1.vol/"
#    pattern = re.compile(r'(\d{8})')
#    proc_dates = [x for x in os.listdir(inputdir) if pattern.match(x)]
    proc_dates = os.listdir(inputdir)
#    proc_dates.sort()
#    print(proc_dates)
    for day in proc_dates:
        day_dt=dp.parse(day);
        if day_dt >= start_date_dt and day_dt <= end_date_dt:
    
            print(day)
    
            # command to submit to lotus
            #sbatch_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.MAX_RUNTIME} --mem=4000 -o " \
            #                 f"{SETTINGS.LOTUS_DIR}{today}/{day}_sync_files.out -e {SETTINGS.LOTUS_DIR}{today}/{day}_sync_files.err "\
            #                 f"--wrap=\"python sync_files_day.py -d {day} -n {table} -t {scan_type}\""
            sbatch_command = f"sbatch -A {SETTINGS.ACT} -p {SETTINGS.QUEUE} -q {SETTINGS.PART} -t {SETTINGS.MAX_RUNTIME} --mem=4000 -o " \
                             f"{SETTINGS.LOTUS_DIR}{today}/{day}_sync_files.out -e {SETTINGS.LOTUS_DIR}{today}/{day}_sync_files.err "\
                             f"--wrap=\"python sync_files_day.py -d {day}\""
    
            subprocess.call(sbatch_command, shell=True)
    
            print(f"running {sbatch_command}")
   
def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)

if __name__ == '__main__':
    main() 
 
