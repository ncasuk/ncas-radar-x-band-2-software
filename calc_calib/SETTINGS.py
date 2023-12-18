QUEUE = 'short-serial-4hr --account=short4hr'
MAX_RUNTIME = '04:00:00'
EST_RUNTIME = '01:00:00'
PROJ_NAME = 'woest'
SCAN_TYPE = 'bl_scans'

# Range in which there is data for the project
MIN_START_DATE = '20230501'
MAX_END_DATE = '20230930'

#Location for output files
#LOG_DIR = '/gws/smf/j04/ncas_radar/lbennett/logs/'+PROJ_NAME+'/cals/'
#SUCCESS_DIR = LOG_DIR+'success/'
#NO_RAIN_DIR = LOG_DIR+'no_rain/'
#NO_RAYS_DIR = LOG_DIR+'no_rays/'

#LOCATION OF SCRIPTS
SCRIPT_DIR = f'/gws/pw/j07/ncas_obs_vol1/amf/software/ncas-mobile-x-band-radar-2/calc_calib/'

#Location for LOTUS output
LOTUS_OUTPUT_PATH_BASE = f'/home/users/lbennett/logs/lotus-output/{PROJ_NAME}'
LOTUS_DIR = f'{LOTUS_OUTPUT_PATH_BASE}/cals/nxpol2/bl_scans/'

#Location of weather station text files with daily rain amounts
#WXDIR = f'/gws/nopw/j04/ncas_obs/amf/raw_data/ncas-aws-2/incoming/{PROJ_NAME}/NOAA/'
WXDIR= f'/gws/nopw/j04/ncas_radar_vol2/data/ncas-mobile-x-band-radar-2/woest/aws_obs/'

#Location of vertical scans
#VERT_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/vert/'
INPUT_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-2/{PROJ_NAME}/cfradial/uncalib_v1/vert/'

#Location of volume scans
#VOLUME_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/cfradial/uncalib_v1/sur/'
VOLUME_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-2/{PROJ_NAME}/cfradial/uncalib_v1/sur/'

#Location of output of ZDR data for calibration
#ZDR_CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/ZDRcalib/'
ZDR_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-2/{PROJ_NAME}/calibrations/ZDRcalib/'

#Location of output of Z data for calibration
#Z_CALIB_DIR = '/gws/nopw/j04/ncas_radar_vol2/data/xband/'+PROJ_NAME+'/calibrations/Zcalib/'
#Z_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-2/{PROJ_NAME}/calibrations/Zcalib/cloud_scans/'
Z_CALIB_DIR = f'/gws/smf/j07/ncas_radar/data/ncas-mobile-x-band-radar-2/{PROJ_NAME}/calibrations/Zcalib/{SCAN_TYPE}/'

#Location of phi files 
PHI_DIR = Z_CALIB_DIR+'phi_files/'

# Exclusions is a list of tuples (), where each tuple is a pair of 
# tuples.The first tuple of each pair is the start and stop elevation 
# of the segment to exclude. The second tuple contains the start and 
# stop azimuth of the segment to exclude.
#Cloud scans
EXCLUSIONS = [((0,2.6),(57,205)),((0,2.6),(284,313)),((3.4,3.6),(57,150)),((3.4,3.6),(270,315)),((4.4,7.6),(79,150)),((8.4,11.6),(76,93)),((8.4,11.6),(134,150)),((12.9,17.1),(75,103)),((12.9,17.1),(134,150))]
#BL scans
#EXCLUSIONS = [((0,1.1),(0,360)),((1.4,2.6),(57,205)),((1.4,2.6),(284,313)),((3.4,3.6),(57,150)),((3.4,3.6),(299,315)),((4.9,6.6),(57,150))]


