import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd
#from functions import moving_average
from calc_calib import SETTINGS
import warnings
import glob
import gc
import copy
import os
import scipy as scipy
from scipy import signal
#import peakdetect
#from peakdetect import peakdet

plt.switch_backend('agg')

warnings.filterwarnings("ignore", category=UserWarning) 
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
#warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

#---------------------------------------------------------------------------------------
#Calculate hourly median values of melting layer heights to use for Z calibration

def calc_hourly_ML(outdir,date):        
  
    #Output variable 
    hourly_ml_zdr = pd.DataFrame() 
    #Input file (full day)
    file1 = os.path.join(outdir, date, 'day_ml_zdr.csv')
    #Output file (hourly values for each day)
    file2 = os.path.join(outdir, date, 'hourly_ml_zdr.csv')

    if os.path.exists(file1):
        data = pd.read_csv(file1,index_col=0, parse_dates=True)
    
        if data.empty==False:
            hourly_ml = np.zeros(24)*np.nan
            hourly_zdr = np.zeros(24)*np.nan
        
            for hh in range(0,24):
                beg=time(hh,0,0)
                print(beg)
                if hh==23:
                    end=time(23,59,0)            
                    print(end)
                else:
                    end=time(hh+1,0,0)
                    print(end)
                #Find values of melting layer and median ZDR between each hourly period
                #ml_zdr=data[['MLB','ZDR']].between_time(beg,end,include_end=False)
                ml_zdr=data.between_time(beg,end,inclusive='left').copy()
                print(ml_zdr)
                #If there are less than 3 (out of 6) valid values, set all to NaN and continue
                #Else calculate median value of melting layer height and ZDR
                if ml_zdr['ZDR'].count()<3:
                    hourly_ml[hh]=float('nan')
                    hourly_zdr[hh]=float('nan')
                    continue
                else:
                    M=ml_zdr['ZDR'].median()
                    print('M=',M)
                    #Median Absolute Deviation
                    mad=1.4826*(abs(ml_zdr['ZDR']-M)).median()
                    out=mad*2.5
                    #Determine outliers and remove them
                    ind = np.logical_or(ml_zdr['ZDR'] <= M-out, ml_zdr['ZDR'] >= M+out)
                    ml_zdr[ind==True]=np.nan
          
                    hourly_ml[hh]=ml_zdr['MLB'].median()
                    print(hourly_ml)
                    hourly_zdr[hh]=ml_zdr['ZDR'].median()
                    print(hourly_zdr)

            print(hourly_ml)
            print(hourly_zdr)
            if np.isfinite(hourly_ml).any():      
            
                #Construct time array for hourly medians i.e. 00:30, 01:30
                hourly_T = pd.to_datetime(date) + pd.timedelta_range('00:30:00','23:30:00',freq='1H')
                hourly_ml_zdr = pd.DataFrame({'H_MLB' : hourly_ml, 'H_ZDR' : hourly_zdr}, index=hourly_T)
            
                hourly_ml_zdr = hourly_ml_zdr.dropna()
                hourly_ml_zdr.to_csv(file2)
            
                return True        
            else:
                return False

#------------------------------------------------------------------------------------------------------
def extract_fh(time, fhdata):

#Extract freezing height corresponding to radar file time
#fh is the dataframe
#ft = radar file time   
    ft = pd.to_datetime(time)
    ft=ft.tz_convert(None)

#Index of nearest values to ft
    indf = fhdata.index.get_indexer([ft], method='nearest')
    indf = indf[0]
    fh=fhdata['FH'][indf]
#    #print ft, ml_zdr.index[indf] 
##If radar file time is later than last index of fhdata, set fh to last value in file
#    if ft >= fhdata.index[-1]:
#
#        fh=fhdata['FH'][-1]
#
##If radar file time is earlier than first index of fh, set fh to first value in file
#    elif ft <= fhdata.index[0]:
#
#        fh=fhdata['FH'][0]
#
##If radar file time equals an index of fh, set fh to those values.
#    elif ft == fhdata.index[indf]:
#
#        fh=fhdata['FH'][indf]
#   
##Else find time indices either side of file time and linearly interpolate between them               
#    else:
#        if ft > fhdata.index[indf]:
#
#            st = indf
#            fn = indf+1
#
#        elif ft < fhdata.index[indf]:
#
#            st = indf-1
#            fn = indf
#
#        t2 = (abs(ft - fhdata.index[st])).seconds
#        t3 = (abs(fhdata.index[fn]-fhdata.index[st])).seconds
#        t4 = float(t2) / float(t3)
#
#        #Melting layer height interpolated linearly between hourly values
#        fh = fhdata['FH'][st] + (fhdata['FH'][fn] - fhdata['FH'][st]) * t4

    return fh

def identify_first_phase_ray(data, mask, starting_gate, window_size, filter_size, end_gate_limit, missing_points=0):
    valid_data = np.where(np.logical_or(mask,
                                        ~np.isfinite(data)),
                          np.zeros(data.shape),
                          np.ones(data.shape))
    if valid_data[starting_gate:end_gate_limit].sum() < window_size-missing_points:
        return np.nan, np.nan

    j = starting_gate
    start_not_found = True
    while start_not_found:
        if j == data.shape[0]:
            return np.nan, np.nan

        if valid_data[j]:
            valid_sum = valid_data[j:window_size+j].sum()
            #print(valid_sum)
            if valid_sum >= (window_size-missing_points):
                phase = np.nanmedian(data[j:j+filter_size])
                return phase, j
            elif j > end_gate_limit:
                return np.nan, np.nan
            else:
                j += 1
        elif j > end_gate_limit:
            return np.nan, np.nan

        else:
            j += 1

#--------------------------------------------------------------------------------------------------------------------------

def calibrate_day_att(raddir, outdir, day, fhdata, zdr_offset):

    ZDRmax = 2.0
    min_path = 10
    filelist = glob.glob(os.path.join(raddir,'*.nc'))
    filelist.sort()
    nfiles=len(filelist)
    print('Number of files = ',nfiles)

    #Extract number of rays 
    rad=pyart.io.read(filelist[0])
    ss = rad.nrays

    #create empty array for calibration offsets
    delta_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for PhiEst and PhiObs
    phiest_all=np.zeros((nfiles,ss))*np.nan
    phiobs_all=np.zeros((nfiles,ss))*np.nan
    startphi_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for Time
    T = np.zeros((nfiles))*np.nan
    #create empty array for number of good rays in each volume
    good_rays = np.zeros((nfiles))*np.nan
    #Create empty array for good ray index
    ray_index = np.zeros((nfiles,ss))*np.nan
    ray_az = np.zeros((nfiles,ss))*np.nan
    ray_el = np.zeros((nfiles,ss))*np.nan


    for file in range(nfiles):
        print(file)

        #Read file
        rad=pyart.io.read(filelist[file])

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
        T[file] = hh + mm/60.0 + ss/3600.0

        #Extract dimensions
        ind = rad.rays_per_sweep['data'] !=360
        if np.sum(ind)>0:
            print('At least one sweep does not have 360 rays')
            continue        

        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = int(Tdim/Edim)
        if Adim!=360:
            print('azimuths not equal to 360')
            print(Adim)
            continue
        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el2 = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])
            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
            kdp = copy.deepcopy(rad.fields['KDP']['data'])

            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360

       	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
            #Set invalid values (-9e33) to nans
            ind = uphidp.mask==True
            uphidp[ind]=np.nan

        except:
            print("Couldn't load all variables")    
            continue

        #Calculate height of every range gate
        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        mlh=extract_fh(time, fhdata)
        mlh=mlh/1000
        print(mlh)

        zind = beam_height > mlh   
        uzh[zind==True] = np.nan
        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        uphidp[zind==True] = np.nan
        kdp[zind==True] = np.nan
        rhohv[zind==True] = np.nan

        #Get rid of first 2km
        #n=13 for 1us pulse
#        n=26 #for 0.5us pulse
#        uzh = uzh[:,n:]
#        zdr = zdr[:,n:]
#        phidp = phidp[:,n:]
#        uphidp = uphidp[:,n:]
#        kdp = kdp[:,n:] 
#        rhohv = rhohv[:,n:]
#        rg = rg[n:] - rg[n]

        #Create empty arrays for observed and calculated PhiDP
        phiobs = np.zeros([Tdim])*np.nan
        phiest = np.zeros([Tdim])*np.nan        
        startphi = np.zeros([Tdim])*np.nan        

#        c=0

# A list of tuples is imported from the SETTINGS file. This "one-liner" 
# builds a generator from the list of tuples so each tuple defines a 
# binary array which is True where the segment occurs and false 
# elsewhere. All conditions must be met, so between start and stop in 
# both azimuth and elevation. 
# These are then combined to a single array using np.any to create a 
# single exclude binary array which is True where any of the segments 
# are found and False in non-excluded places

        exclusions = SETTINGS.EXCLUSIONS
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)

       	az_index = np.where(~exclude_radials)[0]

        for i in az_index:
        #for i in (778,):
            print('1. az_index = ', i, 'azimuth = ', az[i], 'El = ', el2[i])

#This function uses a moving window to find the first 10 valid values of phidp and uses this as the starting point of the ray.
            data=phidp[i,:]
            [phase1,r1] = identify_first_phase_ray(data, data.mask, 0, 10, 5, len(data), missing_points=0)
            if np.isnan(r1):
                print('insufficient phidp')
                continue

            #Extract ray
            phidp_f = phidp[i,r1:]
            uphidp_f = uphidp[i,r1:]
            uzh_f = uzh[i,r1:]
            zdr_f = zdr[i,r1:] + zdr_offset
            rhohv_f = rhohv[i,r1:]
            rg_f = rg[r1:]

            #attenuation correction
            #phidp_att = copy.deepcopy(phidp_f)
            phidp_att = phidp_f - phidp_f[0]

            PA = np.maximum.accumulate(phidp_att) 
            uzh_att = uzh_f + 0.28*PA
            zdr_att = zdr_f + 0.04*PA

            #Check for all-nan array, go to next iteration of loop if so
            #if np.sum(np.isfinite(phidp_att)==True)==0:
            #    continue

            #Find minimum value of PhiDP
            #phi1_valid = np.where(np.isfinite(phidp_att))[0]
            #if phi1_valid.size != 0:
            #    phi1 = phi1_valid[0]
            #else:
            #    continue
            phi1=0
#            #Find indices where PhiDP is between 4 and 6 degs    
            ind = np.where(np.logical_and(phidp_att > 4, phidp_att < 6))[0]

            #If values exist, 
            if ind.size != 0:
               #Find the index of the maximum value of PhiDP between 4 and 6
                ib = np.where(phidp_att==max(phidp_att[ind]))[0][0]

                pdpmax = phidp_att[ib]
                print('2. maxmimum phidp=', pdpmax)
                path_len = rg_f[ib]-rg[r1]
                
                if path_len < min_path:
                    print('3. path too short')                

                #if path of significant returns exceeds min_path
                if path_len > min_path:
                    print('3.',  'Path length = ', path_len)                    

                    #exclude rays with large ZDR (heavy rain (mie-scattering))
                    ind = zdr_att[phi1:ib+1] > ZDRmax

                    if np.sum(ind) > 0:                    
                        print('4. Number of large ZDR = ', np.sum(ind)) 

                    if np.sum(ind) < 3:

                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)

                        if np.sum(ind[phi1:ib+1]) > 2:   
                            print('5. number of rhohv<0.98 = ', np.sum(ind[phi1:ib+1]))
                            
                        if np.sum(ind[phi1:ib+1]) < 3:   
                            print('6. all conditions met for az_index = ',i,', azimuth = ',az[i], ', elevation = ', el2[i])

                            #index of good rays (value from 0 to 4320)
                            ray_index[file,i] = i
                            ray_az[file,i] = rad.azimuth['data'][i]
                            ray_el[file,i] = rad.elevation['data'][i]

                            uzh_att[ind] = np.nan
                            zdr_att[ind] = np.nan
                            #phidp_f[ind] = np.nan
                            #uphidp_sm_f[ind] = np.nan
			    #uphidp_sm_f.mask[ind] = np.nan
                            #rhohv_f[ind] = np.nan

                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])

                            phiobs[i] = pdpmax
                            #phiobs_all[file,:] = phiobs

                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
                            kdpest = 1e-05 * (11.74 - 4.020*zdr_att[phi1:] - 0.140*zdr_att[phi1:]**2 + 0.130*zdr_att[phi1:]**3)*10 ** (uzh_att[phi1:]/10)

                            tmpphi = np.nancumsum(kdpest)*rg_sp*2
                            #phiest[c] = tmpphi[ib]
                            phiest[i] = tmpphi[ib]
#                           print 'phiest = ', phiest[i] 
            else:
                print('2. No PhiDP between 4-6')
        #phiest is a function of ray, phiest(nrays)
        #phiest_all is a function of volume and ray, phiest_all(nvols,nrays)
        #delta is a function of ray, delta(nrays)
        #delta_all is a function of volume and ray, delta_all(nvols,nrays)

       	phiobs_all[file,0:Tdim] = phiobs
       	phiest_all[file,0:Tdim] = phiest
       	startphi_all[file,0:Tdim] = startphi

       	good_rays = np.sum(np.isfinite(phiest));
       	print('file =',file,'rays =',str(good_rays))
       	del rad
       	del zdr, rhohv, kdp, phidp, uzh, uphidp
       	gc.collect()
                    
        #print phiobs.shape   
        #delta = ((phiest-phiobs)/phiobs)*100
        #print delta.shape
        #print file
        #delta_all[file,:] = delta
        #print 'end'    
        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
        #data_save=np.vstack((phiest,phiobs,delta))
        #np.save(filename,data_save)          

    #filename = outdir + 'good_rays'     
    #np.save(filename,good_rays)
    
    print("total rays = ", np.sum(np.isfinite(phiest_all.flatten())))
    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
        print("phiest and phiobs values exist")
        phi_dir=os.path.join(outdir,'phi_files')
        if not os.path.exists(phi_dir):
            os.makedirs(phi_dir) 
        phase_dir=os.path.join(outdir,'phase_files')
        if not os.path.exists(phase_dir):
            os.makedirs(phase_dir) 

        phiest_filename = os.path.join(phi_dir, 'phiest_all_att_' + day)
        np.save(phiest_filename,phiest_all)
        phiobs_filename = os.path.join(phi_dir, 'phiobs_all_att_' + day)
        np.save(phiobs_filename,phiobs_all)
        startphi_filename = os.path.join(phase_dir, 'startphi_all_' + day)
        np.save(startphi_filename,startphi_all)
        return True
    else:
        return False



#--------------------------------------------------------------------------------------------------------------------------

def horiz_zdr(datadir, date, outdir, ml_zdr, zcorr,scan_type):
    
    filelist = glob.glob(datadir + date + '/' + scan_type + '/*.nc')
    filelist.sort()
    nfiles=len(filelist)
    
#   T = np.zeros((nfiles))*np.nan
#   num18 = np.zeros(nfiles)*np.nan
#   stdZDR18  = np.zeros(nfiles)*np.nan
#    medZDR18  = np.zeros(nfiles)*np.nan
    medZDR18=[]
    T_arr = []

    
    for file in range(0,nfiles):
        #print filelist[file]
        print(file)
        rad=pyart.io.read(filelist[file])

        #Create time array
        timeT = rad.metadata['start_datetime']
        print(timeT)
        hh = float(timeT[11:13])
        mm = float(timeT[14:16])
        ss = float(timeT[17:19])
#        T[file] = hh + mm/60.0 + ss/3600.0

       	#T_arr.append(time)

        #Extract dimensions
        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = int(Tdim/Edim)
        
       	exclusions = SETTINGS.EXCLUSIONS
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
       	az_index = np.where(~exclude_radials)[0]

        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])

            uzh = copy.deepcopy(rad.fields['dBuZ']['data'][az_index,:])#[rad.sweep_start_ray_index['data'][0]]
            uzh = uzh + zcorr
            zdr = copy.deepcopy(rad.fields['ZDRu']['data'][az_index,:])
            rhohv = copy.deepcopy(rad.fields['RhoHVu']['data'][az_index,:])
            phidp = copy.deepcopy(rad.fields['PhiDP']['data'][az_index,:])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360
            sqi = copy.deepcopy(rad.fields['SQIu']['data'][az_index,:])
        except:
            print("Couldn't load all variables")    
            continue

        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(Adim*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        beam_height = beam_height[az_index,:]

        #Extract melting layer height for the given radar scan time to use as a threshold on data selection
        mlh, _ = extract_ml_zdr(timeT, ml_zdr)
        print(mlh)
        zind = beam_height > mlh   
        uzh[zind==True] = np.nan    
        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        rhohv[zind==True] = np.nan
        sqi[zind==True] = np.nan

        #Set first three range gates to NaN
        uzh[:,0:3] = np.nan
        zdr[:,0:3] = np.nan
        phidp[:,0:3] = np.nan
        rhohv[:,0:3] = np.nan
        sqi[:,0:3] = np.nan

        ind=np.all([rhohv>0.99, sqi>0.3, phidp>0, phidp<6, uzh>15, uzh<=18],axis=0)
#        ind=np.all([rhohv>0.99, phidp>0, phidp<6, uzh>18, uzh<=21],axis=0)
 #       ind=np.all([rhohv>0.99, phidp>0, phidp<6, uzh>21, uzh<=24],axis=0)
#
        if ind.sum() >10:
#           num18[file] = np.sum(ind==True)
#           stdZDR18[file] = np.nanstd(zdr[ind==True])
       	    T_arr.append(timeT)
            medZDR18.append(np.nanmedian(zdr[ind==True]))

       	del rad
        del zdr, rhohv, uzh, phidp
        gc.collect()
    print(T_arr) 
    return T_arr, medZDR18

