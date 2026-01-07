import numpy as np
import argparse
import pyart
import warnings
import glob
import os
import gc
import shutil
import sys
import SETTINGS_unfold as SETTINGS

srcdir = '/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/woest/level2/rhi/'
dstdir='/gws/pw/j07/woest/data/ncas-radar-x-band-2/level2/rhi/'

def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--date', nargs=1, required=True, type=str, 
                        help=f'Date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    
    return parser.parse_args()

def move_files(args):

    """ 
    
    :param args: (namespace) Namespace object built from arguments parsed from command line
    """

    day=args.date[0]
    print('Processing ',day)
    table = args.table_name[0]

    filelist = [os.path.basename(x) for x in glob.glob(f'{srcdir}{day}/*rhi*v1.0.0.nc')]
    filelist.sort()
    for f in filelist:
        print('f=',f)
        src=f'{srcdir}{day}/{f}'
        dst=f'{dstdir}{day}/{f}'
        print('copying ',src,' to ',dst)
        shutil.copy2(src,dst)
 
def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    move_files(args)

if __name__ == '__main__':
    main()
