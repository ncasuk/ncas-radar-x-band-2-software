import argparse
import glob
import pyart
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import SETTINGS
import sys
import os 

#sys.path.append('/opt/scripts/utilities/')
#sys.path.append('/opt/scripts/')
rain_file = '/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/calibrations/days_with_rain.csv'
zdr_dir = '/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/calibrations/ZDRcalib/'
def arg_parse_day():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--date', required=True, type=str, 
                        help=f'Date string with format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-n', '--table_name', nargs=1, type=str, required=True,metavar='')
    return parser.parse_args()

def extract_birdbath_data(args):
    
    table = args.table_name[0]
    day=args.date
    YY, MM, DD = day[:4], day[4:6], day[6:8]
    day_dash=f'{YY}-{MM}-{DD}'

    #First see if data has already been extracted for this date
    if os.path.exists(os.path.join(zdr_dir,f'zdr_data_{day_dash}.csv')):
        sys.exit('Birdbath data already extracted for ' + day)

    #Read csv file to see if yesterday had any rain.
    rain=pd.read_csv(rain_file)
    if int(day) in rain['date'].values:
        print(f"{day} had rain")
    
        birdbath_files = glob.glob(f'/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/level1/birdbath/{day}/*.nc')
        print(len(birdbath_files))
        birdbath_files.sort()
        results = {'Z':{},
                   'V':{},
                   'CC':{},
                   'ZDR':{},
                   'RainN':{},
                   'RainM':{},
                   'RainStd':{},
                   'RainH':{},
                   'IceN':{},
                   'IceM':{},
                   'IceStd':{},
                   'IceH':{}}
        
        for bb_file in birdbath_files[::]:
            print(bb_file)
            radar = pyart.io.read(bb_file, delay_field_loading=True)
            Z_profile  = np.nanmean(np.where(radar.fields['SNRu']['data']>20,
                                             radar.fields['dBuZ']['data'],
                                             np.nan),axis=0)
            ZDR_profile = np.nanmean(np.where(radar.fields['SNRu']['data']>20,
                                             radar.fields['ZDRu']['data'],
                                             np.nan),axis=0)
            CC_profile = np.nanmean(np.where(radar.fields['SNRu']['data']>20,
                                             radar.fields['RhoHVu']['data'],
                                             np.nan),axis=0)
            V_profile = np.nanmean(np.where(radar.fields['SNRu']['data']>20,
                                             radar.fields['Vu']['data'],
                                             np.nan),axis=0)
            time_of_bb = pd.to_datetime(radar.time['units'][14:])
            results['Z'].update({time_of_bb:Z_profile})
            results['ZDR'].update({time_of_bb:ZDR_profile})
            results['CC'].update({time_of_bb:CC_profile})
            results['V'].update({time_of_bb:V_profile})
        
            valid_hydro_mask = np.all([radar.fields['dBuZ']['data']>10,
                                       radar.fields['RhoHVu']['data']>0.98,
                                       radar.fields['SNRu']['data']>20,
                                       radar.fields['SNRvu']['data']>20,
                                       radar.gate_z['data']>1000,
                                       radar.fields['Vu']['data']<=-1],axis=0)
        
            valid_rain_mask = np.all([valid_hydro_mask,
                                      radar.fields['Vu']['data']<=-3],axis=0)
               
            valid_ice_mask = np.all([valid_hydro_mask,
                                     radar.fields['Vu']['data']>-3],axis=0)
        
            results['RainN'].update({time_of_bb:valid_rain_mask.sum()})
            results['RainM'].update({time_of_bb: np.nanmean(np.where(valid_rain_mask,
                                                                    radar.fields['ZDRu']['data'],
                                                                    np.nan))})
            results['RainStd'].update({time_of_bb:np.nanstd(np.where(valid_rain_mask,
                                                                    radar.fields['ZDRu']['data'],
                                                                    np.nan))})
            results['RainH'].update({time_of_bb:np.nanmean(np.where(valid_rain_mask,
                                                                    radar.gate_altitude['data'],
                                                                    np.nan))})
            results['IceN'].update({time_of_bb:valid_ice_mask.sum()})
            results['IceM'].update({time_of_bb: np.nanmean(np.where(valid_ice_mask,
                                                                    radar.fields['ZDRu']['data'],
                                                                    np.nan))})
            results['IceStd'].update({time_of_bb:np.nanstd(np.where(valid_ice_mask,
                                                                    radar.fields['ZDRu']['data'],
                                                                    np.nan))})
            results['IceH'].update({time_of_bb:np.nanmean(np.where(valid_ice_mask,
                                                                   radar.gate_altitude['data'],
                                                                   np.nan))})
                                                   
        test = pd.DataFrame(results)
        outf=f'{zdr_dir}/zdr_data_{day_dash}.csv'
        test.to_csv(outf)

    else:
        print('No rain on this day or aws file not yet processed')

def main():
    """Runs script if called on command line"""

    args = arg_parse_day()
    extract_birdbath_data(args)

if __name__ == '__main__':
    main() 
