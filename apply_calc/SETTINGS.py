# Project Choice
PROJ_NAME = 'woest'
#SCAN_TYPE = 'bl_scans'
#SCAN_GEOM = 'sur'

# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 1000000

# Range in which there is data for the project
MIN_START_DATE = '20230501'
MAX_END_DATE = '20230930'

# LOTUS settings
QUEUE = 'short-serial-4hr --account=short4hr'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '01:00:00'

# Where .out and .err files from LOTUS are output to
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
LOTUS_DIR = f'{LOTUS_OUTPUT_PATH_BASE}/cals/nxpol2/'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-radar-x-band-2/apply_calc/'

#Location of uncalibrated/level1 files
INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/level1/'
#Location of processed/level2 files
OUTPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/level2/'

#Location of params files
PARAMS_FILE = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-radar-x-band-2/params/RadxConvert.nxpol2_{PROJ_NAME}_sur.level2' 
PARAMS_FILE_RHI = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-radar-x-band-2/params/RadxConvert.nxpol2_{PROJ_NAME}_rhi.level2' 

CHUNK_HOURS=6

