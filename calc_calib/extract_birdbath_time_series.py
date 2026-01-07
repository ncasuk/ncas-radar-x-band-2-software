import SETTINGS
import os
import argparse
import dateutil.parser as dp
from datetime import date
import subprocess

def arg_parse_all():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start_date', nargs=1, required=True, 
                        default=SETTINGS.MIN_START_DATE, type=str, 
                        help=f'Start date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs=1, required=True, 
                        default=SETTINGS.MAX_END_DATE,type=str, 
                        help=f'End date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    
    return parser.parse_args()

def loop_over_days(args):
 
    """ 
    Runs process_vert_scans.py for each day in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """
    

    #Set up directory for Lotus output files based on today's date
    today = date.today().strftime("%Y%m%d")
    output_base = f'{SETTINGS.LOTUS_DIR}/{today}'
    if not os.path.exists(output_base):
        os.makedirs(output_base)

    start_date = args.start_date[0]
    end_date = args.end_date[0]
    table = args.table_name[0]

    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')
 
    proc_dates = os.listdir(SETTINGS.INPUT_DIR)
    proc_dates.sort()
    
    current_directory = os.getcwd()  # get current working directory

    for day in proc_dates:
        day_dt=dp.parse(day);
        if day_dt >= start_date_dt and day_dt <= end_date_dt:
    
            print(day)
    
            wrap_command = (f"python {SETTINGS.SCRIPT_DIR}/extract_birdbath_data.py "
                            f"-d {day} -n {table}"
                            )

            # command to submit to lotus
            slurm_command = f"sbatch -A {SETTINGS.ACT} -p {SETTINGS.QUEUE} -q {SETTINGS.PART} -t {SETTINGS.MAX_RUNTIME} --mem=4000" \
                             f" -o {output_base}/{day}/bb.out -e {output_base}/{day}/bb.err" \
                             f" --wrap=\"{wrap_command}\""
    
            subprocess.call(slurm_command, shell=True)
    
            print(f"[INFO] Running: {slurm_command}")
   
def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)


if __name__ == '__main__':
    main() 
