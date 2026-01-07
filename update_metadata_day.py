import SETTINGS
import os
import re
import argparse
import dateutil.parser as dp
from datetime import date
from datetime import timedelta
import subprocess
import glob

def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--idate', nargs=1, type=str, required=True,
                        help=f'Date to find scans from, fromat YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}',
                        metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    
    return parser.parse_args()

def loop_over_chunks(args):
 
    """ 
    Runs update_metadata_chunk.py for each chunk of files in the given time range
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    today = date.today().strftime("%Y%m%d")
    table = args.table_name[0]
    idate = args.idate[0]

    #Set up directory for Lotus output files based on today's date
    if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
        os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))

    try:
        day_date_time = dp.isoparse(idate)
    except ValueError:
        raise ValueError('[ERROR] Date format is incorrect, should be YYYYMMDD')

    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)

    if day_date_time < min_date or day_date_time > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - '
                         f'{SETTINGS.MAX_END_DATE}')

    if 24 % SETTINGS.CHUNK_SIZE != 0:
        raise ValueError(f'Chunk size ({SETTINGS.CHUNK_SIZE}) does not divide '
                         'evenly into 24')

    n_chunks = 24 / SETTINGS.CHUNK_SIZE

    if n_chunks < 1:
        raise ValueError('SETTINGS.CHUNK_SIZE must be 24 or less')

    start_day = day_date_time.day
    current_day_date_time = day_date_time
    script_directory = os.path.dirname(os.path.abspath(__file__))

    while current_day_date_time.day == start_day:

        hours = []

        for hour in [current_day_date_time + timedelta(hours=x) for x in range(SETTINGS.CHUNK_SIZE)]:
            hour_str = hour.strftime("%Y%m%d%H")
            hours.append(hour_str)

        current_day_date_time += timedelta(hours=SETTINGS.CHUNK_SIZE)

        print(f"[INFO] Running for {hours}")

        hour_range = hours[0][-2:] + '-' + hours[-1][-2:]
        year=day_date_time.year
        month=day_date_time.month
        day=day_date_time.day

        output_base = f'{SETTINGS.LOTUS_DIR}/{today}/{idate}'

        if not os.path.exists(output_base):
            os.makedirs(output_base)

        output_base += f'/update_metadata_{hour_range}'

        wrap_command = (f"python {script_directory}/update_metadata_hour.py "
                        f"{' '.join(hours)} -n {table}"
                        )

        # command to submit to lotus
        slurm_command = f"sbatch -A {SETTINGS.ACT} -p {SETTINGS.QUEUE} -q {SETTINGS.PART} -t {SETTINGS.MAX_RUNTIME} --mem=4000 " \
                             f" -o {output_base}.out" \
                             f" -e {output_base}.err"\
                             f" --wrap=\"{wrap_command}\""

        print(f"running {slurm_command}")
        subprocess.call(slurm_command, shell=True)


def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    loop_over_chunks(args)

if __name__ == '__main__':
    main() 
