import numpy as np
import glob 
import os
import pandas as pd
import pyart
import time
import math
import cartopy
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.optimize import curve_fit
from datetime import datetime
import matplotlib.font_manager as mfm

def moving_average(data, size):
    """
    Run a moving window masked average along
    each ray of a data array (rays, gates), with size indicating the number
    of gates either side of the point to survey in the average.
    Parameters
    ----------
    data
    size
    Returns
    -------
    """
    out = np.ma.zeros(data.shape)  # Create the output array
    assert type(data) == np.ma.masked_array, 'Input data is not a masked array, use an alternative function or ' \
                                             'convert input to masked array before use'
    for ran in range(data.shape[1]):  # for each range gate
        # Normal condition
        if ran >= size:
            window = data[:, ran - size:ran + size]
       	    out[:, ran] = np.ma.average(window,
                                        axis=1)
            out[:, ran] = np.where(out[:, ran].mask == True,
                                   np.nan,
                                   out[:, ran])

        # Shortened window at start of the array
        else:
            out[:,ran] = np.nan
    return out

def moving_linear_masked_average(data, size, weights=False, weight_data=None):
    """
    Run a moving window masked average along
    each ray of a data array (rays, gates), with size indicating the number
    of gates either side of the point to survey in the average.
    Parameters
    ----------
    data
    size
    weights
    weight_data
    Returns
    -------
    """
    out = np.ma.zeros(data.shape)  # Create the output array
    assert type(data) == np.ma.masked_array, 'Input data is not a masked array, use an alternative function or ' \
                                             'convert input to masked array before use'
    for ran in range(data.shape[1]):  # for each range gate
        # Normal condition
        if ran >= size:
            window = data[:, ran - size:ran + size + 1]

            if weights:
                weight_window = weight_data[:, ran - size:ran + size + 1]
        # Shortened window at start of the array
        else:
            window = data[:, :ran + size + 1]
            if weights:
                weight_window = weight_data[:, :ran + size + 1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            if weights:
                out[:, ran] = np.ma.average(window,
                                            weights=weight_window,
                                            axis=1)
                out[:, ran] = np.where(out[:, ran].mask == True,
                                       np.nan,
                                       out[:, ran])
            else:
                out[:, ran] = np.ma.average(window,
                                            axis=1)
                out[:, ran] = np.where(out[:, ran].mask == True,
                                       np.nan,
                                       out[:, ran])
    return out



def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

#Simple running average smooth
def simple_smooth(data,size):
    data_sm = np.zeros(data.shape)
#    first_valid_point = np.isfinite(data)
    for val in range(data.shape[1]): #0 to 999
        #print 'val=' , val
        if size <= val < data.shape[1]-size:
        #   print 'window = ', val-size , ' to ', val+size
            window = data[:, val - size:val + size]
            data_sm[:,val] = np.nanmedian(window,axis=1)            
        else:
            data_sm[:,val] = np.nan
    return data_sm     


def extract_phase(zdrdir,datadir,date,outdir):

    filelist = glob.glob(datadir+date+'/*.nc')
    if len(filelist)>0:
        ml_file = os.path.join(zdrdir,date,'day_ml_zdr.csv')
        ml_data = pd.read_csv(ml_file,index_col=0, parse_dates=True)
        rain_index = np.where(ml_data['ML'].notnull())[0]
        all_phase = []
        time = []
        for file in rain_index[0:10]:
            print(filelist[file])
            rad=pyart.io.read(filelist[file],delay_field_loading=True)                
            try:
                IP = pyart.correct.phase_proc.det_sys_phase(rad, ncp_lev=0.4, rhohv_lev=0.6, ncp_field='SQI', rhv_field='RhoHV', phidp_field='uPhiDP')
                all_phase.append(IP)
                time_of_file = filelist[file][120:135]
                time.append(time_of_file)                
            except:
                print(date, 'no uphidp')
                return False

    pdtime = pd.to_datetime(time,format = '%Y%m%d-%H%M%S')
    data = pd.DataFrame({'Initial Phase' : all_phase}, index=pdtime)
    phase_file = os.path.join(outdir,'initial_phase_'+date+'.csv')
    data.to_csv(phase_file)
    return True 


def my_sine_curve(azim,sine_phase,sine_amplitude,offset=0.0):
    phase_rads=2.0*math.pi*sine_phase/360.0
    azim_rads=2.0*math.pi*azim/360.0
    v=(sine_amplitude*np.sin(azim_rads-phase_rads+(math.pi/2.0)))+offset
    return v

def plot_map_point(place,radar,disp_distance,display):

    spacing_unit=disp_distance/11000
    if place=='Chilbolton':
        lat=51.145
        lon=-1.43921
        offset='SE'
    elif place=='Lyneham':
        lat=51.5071
        lon=-2.00547
        offset='SE'
    elif place=='Wardon Hill':
        lat=50.8183
        lon=-2.5547
        offset='SE'
    elif place=='Clee Hill':
        lat=52.39797
        lon=-2.59687
        offset='SE'
    elif place=='Cobbacombe':
        lat=50.963447
        lon=-3.45270
        offset='SE'
    elif place=='Dean Hill':
        lat=51.03042
        lon=-1.65436
        offset='SE'
    elif place=='Chenies':
        lat=51.68919575983973
        lon=-0.5309956754043771
        offset='NE'
    elif place=='Netheravon':
        lat=51.24716
        lon=-1.75665
        offset='NE'
    elif place=='Ash Farm':
        lat=50.89675
        lon=-2.17791
        offset='SE'
    elif place=='Reading':
        lat=51.44089
        lon=-0.93715
        offset='NE'
    elif place=='Exeter':
        lat=50.72754
        lon=-3.47586
        offset='SE'
    elif place=='Bristol':
        lat=51.47707
        lon=-2.57015
        offset='SE'

    if offset=='SE':
        latshift=-7*spacing_unit
        lonshift=1*spacing_unit
    elif offset=='NE':
        latshift=3*spacing_unit
        lonshift=-40*spacing_unit

    x=pyart.util.sphere_distance(radar.latitude['data'][0], lat, radar.longitude['data'][0], lon)*np.sin(pyart.util.for_azimuth(radar.latitude['data'][0], lat, radar.longitude['data'][0], lon)*(math.pi/180.0))/1000.0
    y=pyart.util.sphere_distance(radar.latitude['data'][0], lat, radar.longitude['data'][0], lon)*np.cos(pyart.util.for_azimuth(radar.latitude['data'][0], lat, radar.longitude['data'][0], lon)*(math.pi/180.0))/1000.0  
    if (np.max([np.abs(x),np.abs(y)])<=1.05*disp_distance):
        display.plot_point(lon, lat, symbol='k.', label_text=place, label_offset=(lonshift, latshift))
    
    return 1

def map_additions(ax,radar,display,sweep,velused='region_based_velocity',omit=[]):
    disp_distance=(sweep*-7)+110
    
    
    # ================================================================================================================
    if 'rangerings' not in omit:
        rings_at_height=np.arange(1000,10000,1000) 
        rings_at_range=np.interp(rings_at_height,radar.gate_z['data'][radar.sweep_start_ray_index['data'][sweep],:],radar.range['data'])
        
        rings_at_height=rings_at_height[rings_at_range<95000]
        rings_at_range=rings_at_range[rings_at_range<95000]
        
        if len(rings_at_range)>5:
            rings_at_height=rings_at_height[np.arange(0,len(rings_at_range),2)]
            rings_at_range=rings_at_range[np.arange(0,len(rings_at_range),2)]        
        
        for ir,rar in enumerate(rings_at_range):
            display.plot_range_ring(rar/1000.0, ax=ax, ls='--', col=0.3*np.array([1,1,1]))
            plt.text(0,rar+1000,'%dkm'%(rings_at_height[ir]/1000.0),va='bottom')

    # ================================================================================================================

    if 'directionarrows' not in omit:
        rings_at_height=np.arange(1000,10000,1000) 
        rings_at_range=np.interp(rings_at_height,radar.gate_z['data'][radar.sweep_start_ray_index['data'][sweep],:],radar.range['data'])
        
        rings_at_height=rings_at_height[rings_at_range<95000]
        rings_at_range=rings_at_range[rings_at_range<95000]
        
        if len(rings_at_range)>5:
            rings_at_height=rings_at_height[np.arange(0,len(rings_at_range),2)]
            rings_at_range=rings_at_range[np.arange(0,len(rings_at_range),2)]        

        SQIlimit=0.6
        if velused=='None':
            print('no wind arrows')
        else:
            zlevels = np.arange(500, 10000, 100)  # height above radar
            zspacing = 1
            winddir = np.copy(zlevels) * np.NaN
            for ilevel,zlevel in enumerate(zlevels):
                [i,j]=np.where( ( (np.abs(radar.gate_altitude['data']-zlevel)<zspacing) & (radar.fields['vel_texture']['data']<=texturelimit) & (radar.fields['SQI']['data']<=SQIlimit) & (~np.isinf(radar.fields[velused]['data'])) & (~np.isnan(radar.fields[velused]['data'])) ) )
                if len(i)>5:
                    try:
                        popt, pcov = curve_fit(my_sine_curve, radar.azimuth['data'][i],radar.fields[velused]['data'][i,j])
                        winddir[ilevel]=popt[0]%360
                    except ValueError:
                        print(radar.azimuth['data'][i])
                        print(radar.fields[velused]['data'][i,j])
            arrow_direction=np.nanmean(winddir[zlevels<np.max(rings_at_height[rings_at_range<95000])])
            arrow_x=(disp_distance*65)*np.sin(math.pi*arrow_direction/180.0)
            arrow_y=(disp_distance*65)*np.cos(math.pi*arrow_direction/180.0)
                
            plt.arrow((-0.85*disp_distance*1000)-arrow_x,(0.75*disp_distance*1000)-arrow_y,2.0*arrow_x,2.0*arrow_y,width=45*disp_distance,head_width=100*disp_distance,color='k')
            plt.arrow((0.72*disp_distance*1000)-arrow_x,(0.75*disp_distance*1000)-arrow_y,2.0*arrow_x,2.0*arrow_y,width=45*disp_distance,head_width=100*disp_distance,color='k')
            plt.arrow((-0.85*disp_distance*1000)-arrow_x,(-0.85*disp_distance*1000)-arrow_y,2.0*arrow_x,2.0*arrow_y,width=45*disp_distance,head_width=100*disp_distance,color='k')
            plt.arrow((0.72*disp_distance*1000)-arrow_x,(-0.85*disp_distance*1000)-arrow_y,2.0*arrow_x,2.0*arrow_y,width=45*disp_distance,head_width=100*disp_distance,color='k')

    # ================================================================================================================
        
    if 'radarpoints' not in omit:        
        plot_map_point('Chilbolton',radar,disp_distance,display)
        plot_map_point('Lyneham',radar,disp_distance,display)
        plot_map_point('Wardon Hill',radar,disp_distance,display)
        plot_map_point('Clee Hill',radar,disp_distance,display)
        plot_map_point('Cobbacombe',radar,disp_distance,display)
        plot_map_point('Dean Hill',radar,disp_distance,display)
        plot_map_point('Chenies',radar,disp_distance,display)

    if 'launchpoints' not in omit:        
        plot_map_point('Netheravon',radar,disp_distance,display)
        plot_map_point('Ash Farm',radar,disp_distance,display)
        plot_map_point('Reading',radar,disp_distance,display)
        plot_map_point('Exeter',radar,disp_distance,display)
        plot_map_point('Bristol',radar,disp_distance,display)

    return 1
