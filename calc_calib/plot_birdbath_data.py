import glob
import pyart
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import matplotlib.dates as mdates

bb_dir='/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/calibrations/ZDRcalib/'

def parse_space_array(s):
    if isinstance(s, float) and np.isnan(s):
        return np.nan
    if isinstance(s, np.ndarray):
        return s    
        # Remove brackets and split by spaces
    s_clean = s.strip("[]")
    # Split on whitespace, filter empty strings
    parts = [p for p in s_clean.split() if p]
    # Convert to float array
    return np.array(parts, dtype=float)


blank_profile = np.zeros(133)
blank_profile[:] = np.nan
blank_row = {'Z':blank_profile, 'ZDR': blank_profile, 'V':blank_profile, 'CC':blank_profile}

birdbath_files = glob.glob(f'{bb_dir}zdr_data*.csv')
len(birdbath_files)
birdbath_files.sort()
sample_nc_file = '/gws/smf/j07/ncas_radar/data/ncas-radar-x-band-2/teamx/level1/birdbath/20250620/ncas-radar-x-band-2_plose_20250620-000448_birdbath_v1.0.0.nc'
radar=pyart.io.read(sample_nc_file, delay_field_loading=True)

array_cols = ['Z', 'V', 'CC', 'ZDR']
# List to collect individual DataFrames
dfs = []

for bb_file in birdbath_files[:]:
    #print(bb_file)
    df=pd.read_csv(bb_file,index_col=0,parse_dates=True)
    #print(np.sum(df['RainN']))
    df.index = pd.to_datetime(df.index).tz_localize(None)
    for col in array_cols:
        df[col] = df[col].apply(parse_space_array)
    dfs.append(df)
        # Concatenate all DataFrames into one
combined = pd.concat(dfs)
test=combined
#print(test)

for i, time_index in enumerate(test.index[:-1]):
        
   if test.index[i+1]-test.index[i]>pd.Timedelta('15min'):
      time_ = test.index[i]+pd.to_timedelta('5min')       
      test.loc[time_, :] = blank_row
      time_ = test.index[i+1]-pd.to_timedelta('5min')
      test.loc[time_, :] = blank_row
test = test.sort_index()


#RainN is the mask for rain
#RainM is the mean of ZDR
#RainStd is the std for ZDR
#RainH is the altitude
#IceN is the mask for ice
#IceM is the mean of ZDR for ice
#IceStd is the std for Ice
#IceH is the altitude for ice

start_date=test.index[0]
end_date=test.index[-1]
#print(start_date, end_date)
tick_dates = [start_date + timedelta(days=i) for i in range(0, (end_date - start_date).days + 1, 4)]
tick_dates

fig, axes = plt.subplots(4, 1, figsize=(14, 16), sharex=True)

variables = [
     ('Z', 'Reflectivity (dBZ)', None, None),
     ('CC', 'Correlation coefficient', 0.6, 1),
     ('ZDR', 'Differential Reflectivity (dB)', -1, 3),
     ('V', 'Velocity (m/s)', -8, 2)
]

for ax, (var, label, vmin, vmax) in zip(axes, variables):
    mesh = ax.pcolormesh(
         test.index,
         radar.range['data'] / 1000,
         np.array([Z for Z in test[var].values]).T,
         vmin=vmin,
         vmax=vmax
    )     
    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label(label)
    ax.set_ylim(0, 10)
    ax.set_ylabel("Height (km)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    ax.set_xticks(tick_dates)

axes[-1].set_xlabel("Time", fontsize=14)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(f"{bb_dir}birdbath_timeseries.png", dpi=300, bbox_inches='tight')

p1=0

#RAIN
daily_mean_ZDR_R = test['RainM'][test['RainN']>p1].resample('D').mean()
daily_median_ZDR_R = test['RainM'][test['RainN']>p1].resample('D').median()
daily_mean_ZDR_R = daily_mean_ZDR_R.dropna()
daily_median_ZDR_R = daily_median_ZDR_R.dropna()
#print('daily mean ZDR_R =', daily_mean_ZDR_R, 'daily median ZDR_R = ', daily_median_ZDR_R)

overall_mean_ZDR_R = round(test['RainM'][test['RainN']>p1].mean(),2)
overall_std_ZDR_R = round(test['RainM'][test['RainN']>p1].std(),2)
overall_median_ZDR_R = round(test['RainM'][test['RainN']>p1].median(),2)
#print('Overall mean+std for Rain = ', overall_mean_ZDR_R, '+/-', overall_std_ZDR_R, 'and median=',overall_median_ZDR_R)

#ICE
daily_mean_ZDR_I = test['IceM'][test['IceN']>p1].resample('D').mean()
daily_median_ZDR_I = test['IceM'][test['IceN']>p1].resample('D').median()
daily_mean_ZDR_I = daily_mean_ZDR_I.dropna()
daily_median_ZDR_I = daily_median_ZDR_I.dropna()
#print('daily mean ZDR_I =', daily_mean_ZDR_I, 'daily median ZDR_I = ', daily_median_ZDR_I)

overall_mean_ZDR_I = round(test['IceM'][test['IceN']>p1].mean(),2)
overall_std_ZDR_I = round(test['IceM'][test['IceN']>p1].std(),2)
overall_median_ZDR_I = round(test['IceM'][test['IceN']>p1].median(),2)
#print('Overall mean+std for Ice =', overall_mean_ZDR_I, '+/-', overall_std_ZDR_I, 'and median=', overall_median_ZDR_I)


#Plot ZDR timeseries
#x1=test.index[test['RainN']>p1]
#x2=test.index[test['IceN']>p1]
#y1=test['RainM'][test['RainN']>p1]
#y2=test['IceM'][test['IceN']>p1]
plt.figure(figsize=(10,6))
##plt.plot(x1,y1, 'rx', linestyle='none', label='Rain Average')
##plt.plot(x2,y2, 'bx', linestyle='none', label='Ice Average')
plt.plot(daily_median_ZDR_R.index+ pd.Timedelta(hours=12),daily_median_ZDR_R,marker='o', linestyle='-',color='red',label='Rain Median')
plt.plot(daily_mean_ZDR_R.index+ pd.Timedelta(hours=12),daily_mean_ZDR_R,marker='o', linestyle='--',color='red',label='Rain Mean')
plt.plot(daily_median_ZDR_I.index+ pd.Timedelta(hours=12),daily_median_ZDR_I,marker='o', linestyle='-',color='blue',label='Ice Median')
plt.plot(daily_mean_ZDR_I.index+ pd.Timedelta(hours=12),daily_mean_ZDR_I,marker='o', linestyle='--',color='blue',label='Ice Mean')
ax=plt.gca()
ax.set_xticks(tick_dates)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
plt.xticks(rotation=45)
plt.grid()
plt.ylim(-0.8,0.6)
plt.legend()
title_str = (f'Overall mean & std for Rain = {overall_mean_ZDR_R} +/- {overall_std_ZDR_R} and median = {overall_median_ZDR_R} for p>{p1}\n'
                     f'Overall mean & std for Ice = {overall_mean_ZDR_I} +/- {overall_std_ZDR_I} and median = {overall_median_ZDR_I} for p>{p1}')
plt.title(title_str)
plt.savefig(f"{bb_dir}average_zdr_timeseries_p{str(p1)}.png", dpi=300, bbox_inches='tight')

