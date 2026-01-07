# Maximum number of failures before convert_hour.py raises an error
EXIT_AFTER_N_FAILURES = 10

PROJ_NAME = 'teamx'
#PROJ_NAME = 'chilbolton'
# LOTUS settings
ACT = 'team_x'
#ACT = 'ncas_radar'
QUEUE = 'standard'
PART = 'short'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '01:00:00'

# Range in which there is data for the project
MIN_START_DATE = '20250619'
MAX_END_DATE = '20250930'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-radar-x-band-2/'

#Location for LOTUS output
LOTUS_DIR = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}/'

#INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/woest/level2/sur/'
INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/level2/vol/'
#INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/level1/vol/'
#INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/level1/birdbath/'
#INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/chilbolton/level1/birdbath/'

CHUNK_SIZE = 12
