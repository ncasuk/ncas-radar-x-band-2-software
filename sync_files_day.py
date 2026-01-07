import numpy as np
import argparse
import pyart
import warnings
import glob
import os
import gc
import shutil
import sys
import SETTINGS

#srcdir = '/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/woest/level2/sur/'
#dstdir='/gws/pw/j07/woest/data/ncas-radar-x-band-2/level2/sur/'

srcdir = '/gws/pw/j07/ncas_obs_vol1/amf/raw_data/ncas-radar-x-band-2/incoming/20250603_teamx/teamx_v1.vol/'
dstdir = '/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/level0/teamx_v1.vol/'

def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()
    #type_choices = ['bl_scans', 'cloud_scans']

    parser.add_argument('-d', '--date', nargs=1, required=True, type=str, 
                        help=f'Date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
   # parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    #parser.add_argument('-t', '--scan_type', nargs=1, type=str,choices=type_choices, required=True,
    #                    help=f'Type of scan, one of: {type_choices}',
    #                    metavar='')
    
    return parser.parse_args()

def move_files(args):

    """ 
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    day=args.date[0]
    YY, MM, DD = day[:4], day[4:6], day[6:8]
    day_dash=f'{YY}-{MM}-{DD}'
    print('Processing ',day)
   # table = args.table_name[0]
    #scan_type = args.scan_type[0]

  #  filelist = [os.path.basename(x) for x in glob.glob(f'{srcdir}{day_dash}/*.vol')]
  #  filelist.sort()

    shutil.copytree(f'{srcdir}{day_dash}', f'{dstdir}{day_dash}', dirs_exist_ok=True)

  #  if os.path.exists(f'{dstdir}{day_dash}')==False:
  #      os.makedirs(f'{dstdir}{day_dash}')
  #  for f in filelist:
  #      print('f=',f)
        #src=f'{srcdir}{day}/{scan_type}/{f}'
        #dst=f'{dstdir}{day}/{scan_type}/{f}'
  #      print('copying ',src,' to ',dst)
  #      shutil.copy2(src,dst)
 
def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    move_files(args)

if __name__ == '__main__':
    main()
