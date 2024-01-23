import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticks 
import pandas as pd
import dateutil
import dateutil.parser as dp
import argparse
import datetime as dt
from datetime import timedelta
from matplotlib.dates import (MO,TU,WE,TH,FR,SA,SU)

import warnings
import glob
import os
import re
import SETTINGS

plt.switch_backend('agg')
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def arg_parse():
    """
    Parses arguments given at the command line
    :return: Namespace object built from attributes parsed from command line.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start_date', nargs='?', default=SETTINGS.MIN_START_DATE, 
                        type=str, help=f'Start date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-e', '--end_date', nargs='?', default=SETTINGS.MAX_END_DATE,
                        type=str, help=f'End date string in format YYYYMMDD, between '
                        f'{SETTINGS.MIN_START_DATE} and {SETTINGS.MAX_END_DATE}', metavar='')
    parser.add_argument('-p','--make_plots',nargs=1, required=True, default=0, type=int,
                        help=f'Make plots of individual days if p is set to 1 or the whole time period if p is set to 2',metavar='')
    parser.add_argument('-t','--scan',nargs=1, required=True, type=int,
                        help=f'Choose BL (1) or cloud scans (2)',metavar='')
    
    return parser.parse_args()

def plot_zdr(args):
    """
    Loops through the horizontal ZDR files, concatenates the data and 
    make a plot of the time series of bias
    
    :param args: (namespace) Namespace object built from attributes 
    parsed from command line
    """

    plot=args.make_plots[0]
    start_date = args.start_date
    end_date = args.end_date
    scan = args.scan[0]
    print(scan)
    if scan==1:
        scan_type = 'bl_scans'
    elif scan==2:
        scan_type = 'cloud_scans'
    print(scan_type)

    start_date_dt = dp.parse(start_date) 
    end_date_dt = dp.parse(end_date) 
  
    min_date = dp.parse(SETTINGS.MIN_START_DATE)
    max_date = dp.parse(SETTINGS.MAX_END_DATE)
 
    if start_date_dt < min_date or end_date_dt > max_date:
        raise ValueError(f'Date must be in range {SETTINGS.MIN_START_DATE} - {SETTINGS.MAX_END_DATE}')

    #filesdir = os.path.join(SETTINGS.ZDR_CALIB_DIR,f'horz/{scan_type}')
    filesdir = os.path.join(SETTINGS.ZDR_CALIB_DIR,f'horz/{scan_type}/no1point5/')
    print(filesdir)
    img_dir=os.path.join(SETTINGS.ZDR_CALIB_DIR,f'horz/images/')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    all_data=pd.DataFrame()
    
    filelist = glob.glob(filesdir + '/*.csv')
    filelist.sort()
    #print(filelist)

    for f in range(0,len(filelist)):
        _file = filelist[f]
        print(_file)
        data = pd.read_csv(_file,index_col=0, parse_dates=True)
        #data = data.iloc[1::2, :]
        #if f==0:
        #    print(data)
        all_data = pd.concat([all_data, data])

        if plot==1:
            date = os.path.basename(_file)[0:8]
            fig,ax1=plt.subplots(figsize=(15,8))
            plt.plot(data.index,data['ZDR'], 'kx-',markersize='6',linewidth=2)
            plt.yticks(size=16)
            plt.xticks(size=16)
            plt.xlim(pd.to_datetime(date),pd.to_datetime(date) + pd.to_timedelta(24, unit='h'))
            plt.ylim(-0.5,1.0)
            plt.grid()
            plt.ylabel('Median ZDR (dB)', fontsize=18)
            plt.xlabel('Time (UTC)', fontsize=18) 
            #img_name = f'{img_dir}/'+date+'_horz_zdr_{scan_type}.png'
            img_name = f'{img_dir}/{date}_horz_zdr_{scan_type}.png'
            print('Saving single day',img_name)
            plt.savefig(img_name,dpi=150)
            plt.close()

    overall_median=np.nanmedian(all_data.loc[start_date_dt:end_date_dt]['ZDR'])
    overall_mean=np.nanmean(all_data.loc[start_date_dt:end_date_dt]['ZDR'])
    overall_std=np.nanstd(all_data.loc[start_date_dt:end_date_dt]['ZDR'])
    print('Median Bias for whole period = ',overall_median)
    daily_mean = all_data.resample('D').mean()
    daily_std = all_data.resample('D').std()
    daily_med = all_data.resample('D').median()

    x1=start_date_dt+timedelta(days=-1)
    x2=end_date_dt+timedelta(days=1)

    if plot==2:
        plt.figure(figsize=(15,8))
        plt.errorbar(daily_mean.index,daily_mean['ZDR'],yerr=daily_std['ZDR'],color='black',fmt='o',
                     markersize='6', elinewidth=2,capsize=4)
        #plt.plot(all_data.index,all_data['ZDR'],'kx',label='All data')
#        plt.plot(daily_mean.index,daily_mean['ZDR'],'ro',label='Daily mean')
        plt.plot(daily_med.index,daily_med['ZDR'],'go',label='Daily median')
    
        plt.plot([x1,x2],[overall_mean,overall_mean],'g-',label='Mean of all values')
        plt.plot([x1,x2],[overall_mean+overall_std,overall_mean+overall_std],'g-.',label='Std of all values')
        plt.plot([x1,x2],[overall_mean-overall_std,overall_mean-overall_std],'g-.')
        plt.plot([x1, x2],[overall_median,overall_median],'r-',label='Median of all values')
    
        plt.legend()
    
        plt.yticks(size=12)
        plt.xticks(size=12)
        plt.grid()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1,byweekday=MO))
        plt.gca().xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=90)
        #plt.ylim([-0.5, 1])
        plt.xlim([x1,x2])
        title_str= 'Mean, Std, Median of all values = '\
                    +str(round(overall_mean,2))+'+/-'+str(round(overall_std,2))\
                    +', '+str(round(overall_median,2))
        plt.title(title_str) 
        plt.ylabel('Horizontal ZDR Bias (dB)', fontsize=18)
        plt.xlabel('Date', fontsize=18)
        plt.tight_layout()

        img_name = f'{img_dir}/{start_date}_{end_date}_horz_zdr_{scan_type}_no1point5.png'
        print('Saving ',img_name)
        plt.savefig(img_name,dpi=150)
        plt.close()

def main():
    """Runs script if called on command line"""

    args = arg_parse()
    plot_zdr(args)


if __name__ == '__main__':
    main()     
