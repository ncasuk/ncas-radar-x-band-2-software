import SETTINGS_unfold as SETTINGS
import os
import re
import argparse
import dateutil.parser as dp
from datetime import date
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
    Runs update_metadata_nxpol1.py for each chunk of files in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    today = date.today().strftime("%Y-%m-%d")
    table = args.table_name[0]

    #Set up directory for Lotus output files based on today's date
    if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
        os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))

    #How many files to process in each chunk. 6 files each hour.   
    chunk_hours=SETTINGS.CHUNK_HOURS
    chunk_size=6*chunk_hours

    start_date = args.start_date[0]
    end_date = args.end_date[0]

    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 

    start_day_dt = dp.parse(start_date[0:8])
    end_day_dt = dp.parse(end_date[0:8])
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    input_dir = SETTINGS.INPUT_DIR

    daydir=os.listdir(input_dir)
    daydir.sort()

    files = []
    for day in daydir:
        day_dt=dp.parse(day);
        if day_dt >= start_day_dt and day_dt <= end_day_dt:
            for each in glob.glob(input_dir + day + '/*RHI*v1.0.0.nc'):
                filetime = os.path.basename(each).split('_')[2].replace('-','')
                filetime_dt=dp.parse(filetime)
                if start_date_dt <= filetime_dt and end_date_dt >= filetime_dt:
                    files.append(each)
    print('number of files = ', len(files))
    files.sort()
    print(files)

    chunk_index=0

    for file_chunk in chunks(files,chunk_size):
        #print(file_chunk)
        file_list=' '.join(file_chunk)
        first_file = file_chunk[0]
        D=os.path.basename(first_file).split('_')[2]
        # command to submit to lotus
        sbatch_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.MAX_RUNTIME} --mem=4000 " \
                             f"-o {SETTINGS.LOTUS_DIR}{today}/{D}_{chunk_index}.out -e {SETTINGS.LOTUS_DIR}{today}/{D}_{chunk_index}.err "\
                             f"--wrap=\"python {SETTINGS.SCRIPT_DIR}update_metadata_chunk.py -f {file_list} -n {table}\""

        print(f"running {chunk_index}")
        print(f"running {sbatch_command}")
        subprocess.call(sbatch_command, shell=True)
        chunk_index=chunk_index+1

def chunks(l, n):

    """Yield successive n-sized chunks from l."""

    for i in range(0, len(l), n):
        yield l[i:i + n]
 
def main():
    """Runs script if called on command line"""

    args = arg_parse_all()
    loop_over_days(args)

if __name__ == '__main__':
    main() 
