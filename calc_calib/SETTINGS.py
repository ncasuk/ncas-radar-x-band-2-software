# Project Choice
PROJ_NAME = 'teamx'

# LOTUS settings
ACT = 'team_x'
QUEUE = 'standard'
PART = 'short'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '02:00:00'

# Exclusions is a list of tuples (), where each tuple is a pair of 
# tuples.The first tuple of each pair is the start and stop elevation 
# of the segment to exclude. The second tuple contains the start and 
# stop azimuth of the segment to exclude.
EXCLUSIONS = [((0,0.4),(0,360)),((20,75),(0,360)),((0,3.0),(318,360)),((0,3.0),(0,20)),((0,3),(93,135)),((0,90),(120,168))]

# Range in which there is data for the project
MIN_START_DATE = '20230601'
MAX_END_DATE = '20250930'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-radar-x-band-2/calc_calib/'

#Location of weather station text files with daily rain amounts
#WXDIR= f'/data/aws_obs/'

#Location of vertical scans
INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/level1/birdbath/'

#Location of volume scans
VOLUME_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/level1/vol/'

#Location of output of ZDR data for calibration
ZDR_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/calibrations/ZDRcalib/'

#Location of output of Z data for calibration
Z_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/calibrations/Zcalib/'

LOGDIR=f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/{PROJ_NAME}/calibrations/logs/'

LOTUS_DIR = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'

