# Project Choice
PROJ_NAME = 'teamx'
#PROJ_NAME = 'chilbolton'

#Base directory
#BASE_DIR='/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/'
BASE_DIR='/gws/nopw/j04/team_x/public/data/ACTA/rittner_horn/Meteor50DX-143/'

#Radar long name
#RADAR_LONG = 'ncas-radar-x-band-2'
RADAR_LONG = 'imk-radar-x-band'

#Platform name
PLATFORM = 'rittner-horn'
#PLATFORM = 'plose'
#PLATFORM = 'cao'

#Scan type
SCAN_TYPE = 'vol'
#SCAN_TYPE = 'birdbath'

#Processing level
LEVEL='level1'

# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 10

# Range in which there is data for the project
MIN_START_DATE = '20250601'
MAX_END_DATE = '20250930'
#MIN_START_DATE = '20230901'
#MAX_END_DATE = '20250331'

# LOTUS settings
# LOTUS settings
ACT = 'team_x'
#ACT = 'ncas_radar'
#QUEUE = 'standard'
QUEUE = 'short'
PART = 'standard'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '04:00:00'

# Number of hours passed to convert_hour.py at a time
CHUNK_SIZE = 12

# Radx convert params file
PARAMS_FILE=f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.RittnerHorn.vol'
#PARAMS_FILE=f'/home/users/lbennett/lrose/ingest_params/{PROJ_NAME}/RadxConvert.{PROJ_NAME}.{SCAN_TYPE}.{LEVEL}'

# Where .out and .err files from LOTUS are output to
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
#LOTUS_OUTPUT_PATH = LOTUS_OUTPUT_PATH_BASE + "/{year}/{month}/{day}"

# choice for success / failure output handling
BACKEND = 'db' #'db' or 'file'

# Top level directory for raw data
#INPUT_DIR = f'{BASE_DIR}{PROJ_NAME}/level0/'
INPUT_DIR = f'{BASE_DIR}'
# Output directory for netcdf files (specified in the params file)
#OUTPUT_DIR = f'{BASE_DIR}{PROJ_NAME}/{LEVEL}/'
OUTPUT_DIR = '/gws/smf/j07/ncas_radar/data/rittner_horn/'

