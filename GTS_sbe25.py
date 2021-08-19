

import numpy as np
import pandas as pd
import pycnv
import matplotlib.pyplot as plt
import os
import math
from seabird.cnv import fCNV

# Gibson Seawater must be installed (GSW)
CNVfile = 'xxx.cnv'
dest = 'C:/xxx/xxx/xxx/xxx/'
dest_file = dest + CNVfile           #File Destination
cnv = pycnv.pycnv(dest_file)         #Open and Read CNV File

#LaLaLaLaLa = str(int(48.737*1000))
#LoLoLoLoLo = str(int(-123.575*-1000))
#Qc = str(7)

sensor_entries = list(cnv.data.keys())           #Returns all sensor entries
#first_sensor_entrie = list(cnv.data.keys())[3]
#entire_data_of_the_first_entry = cnv.data[first_sensor_entrie]
print(sensor_entries)

#load variables needed
depSM = cnv.data['depSM']
t090C = cnv.data['t090C']
#T0 = cnv.data['T0']
prSM = cnv.data['prSM']   #this is for SBE25 - use GTS_sbe911.py for those cruises.
#p = cnv.data['p']
c0 = cnv.data['c0S/m']
#C0 = cnv.data['C0']
sal00 = cnv.data['sal00']
derived_salinity = cnv.data['sal00']
#flSP = cnv.data['flSP']
sbeox = cnv.data['sbeox0V']
oxy0 = cnv.data['oxy0']
#This3 = cnv.data['sbeox0ML/L']
#flag = cnv.data['flag']


#test = {'depSM': depSM, 't090C': t090C, 'T0': T0, 'c0S/m': This, 'C0': C0, 'flSP': flSP, 'sbeox0V': This2, 'oxy0': oxy0, 'CStarTr0': CStarTr0, 'prDM': prDM, 'p': p, 'sal00': sal00, 'sbeox0ML/L': This3, 'flag': flag }
Header_Hold = {'Depth': depSM, 'Pressure': prSM, 'Temperature': t090C, 'Oxygen': sbeox, 'Salinity':derived_salinity, 'Conductivity': c0}
csv_dataframe = pd.DataFrame(Header_Hold)

#Seperate Upcast and Downcast using max depth as Seperation Point

MaxD = csv_dataframe['Depth'].max()                     #returns max Depth value to
Row_MaxD= csv_dataframe['Depth'].idxmax()               #returns the row of max Depth

#Seperate Upcast and Downcast
Downcast = csv_dataframe[:int(Row_MaxD)+1]
Upcast = csv_dataframe[int(Row_MaxD)+1:]

#Remove Negative Depth
Downcast = Downcast[Downcast['Depth']>0]

# Replace PAD with nan
PAD = -9.99e-29
Downcast[Downcast['Temperature'] == PAD]
Downcast[Downcast['Salinity'] == PAD]


Downcast['Temperature'] = Downcast['Temperature'].replace(PAD, np.nan)
Downcast['Salinity'] = Downcast['Salinity'].replace(PAD, np.nan)
Downcast['Depth'] = Downcast['Depth'].replace(PAD, np.nan)
Downcast['Conductivity'] = Downcast['Conductivity'].replace(PAD, np.nan)

#Plotting Temperature and Salinity Profile before Bin Average
fig, ax = plt.subplots()
ax.plot(Downcast.Temperature, Downcast.Depth, color='green', label='Temperature Before Bin')
#ax.plot(cast_u['cast1'].Fluorescence, cast_u['cast1'].Pressure, '--', color='green', label='cast1')
ax.invert_yaxis()
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_xlabel('Temperature (degree C)')   # Check unit here
ax.set_ylabel('Depth (m)')
#ax.set_ylim([0,10])
ax.legend()

fig, ax = plt.subplots()
ax.plot(Downcast.Salinity, Downcast.Depth, color='blue', label='Salinity Before Bin')
#ax.plot(cast_u['cast1'].Fluorescence, cast_u['cast1'].Pressure, '--', color='green', label='cast1')
ax.invert_yaxis()
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_xlabel('Salinity (PSU)')   # Check unit here
ax.set_ylabel('Depth (m)')
ax.legend()

#Bin Average Downcast
interval= 1
start_d = np.floor(np.nanmin(Downcast.Depth.values))
stop_d = np.ceil(np.nanmax(Downcast.Depth.values))
bins_list = np.arange(start_d - 0.5 , stop_d + 0.5, int(interval))

Depth_in_Bins = pd.cut(Downcast.Depth, bins=bins_list)
obs_count_d = Downcast.groupby(Depth_in_Bins).size()
Binned_d = Downcast.groupby(Depth_in_Bins).mean()

Binned_d['Observation_counts'] = obs_count_d

#Binned_d = Binned_d.dropna() #Drop the NaN value (Empty Bins)

#Kepp the rows where depth is not NA
Binned_d = Binned_d[Binned_d ['Depth'].notna()]
Binned_d = Binned_d[Binned_d ['Salinity'].notna()]
Binned_d = Binned_d[Binned_d ['Temperature'].notna()]

#Plottnig Temperature and Salinity Profile after Bin Average
fig, ax = plt.subplots()
ax.plot(Binned_d.Temperature, Binned_d.Depth, color='green', label='Temperature after Bin')
ax.invert_yaxis()
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_xlabel('Temperature (degree C)')   # Check unit here
ax.set_ylabel('Depth (m)')
ax.legend()

fig, ax = plt.subplots()
ax.plot(Binned_d.Salinity, Binned_d.Depth, color='blue', label='Salinity after Bin')
#ax.plot(cast_u['cast1'].Fluorescence, cast_u['cast1'].Pressure, '--', color='green', label='cast1')
ax.invert_yaxis()
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_xlabel('Salinity (PSU)')   # Check unit here
ax.set_ylabel('Depth (m)')
ax.legend()

#Re-order the header AND Remove Unwanted Channel
#Or we could use the .drop method: Binned_d = Binned_d.drop(columns=['t090C'])
Title = list(Binned_d)
Binned_d = Binned_d[['Depth', 'Temperature', 'Pressure', 'Conductivity', 'Oxygen', 'Salinity']]       #Remember there are 2 [[ ]]


############################## GTS File preparation ##############################

#Section 1: YYMMJ (Day,Month,Year)
date = cnv.date
print(date)
J = str(date).split('-')[0][3]       #Year, Split Year and show last one digit
MM = str(date).split('-')[1]         #Month, Split Date to show Month in two digit
YY = str(date).split('-')[2][0:2]    #Day, Split Date to show Day in two digit

#YY = Day
#MM= Month
#J = Year

#Section 1: GGgg (Hour, Minute)
GG = str(date).split('-')[2][3:5] #Hour
gg = str(date).split('-')[2][6:8] #Minute

#GG = Hour
#gg = Minute

profile = fCNV(dest_file)
lon = profile.attributes['LONGITUDE']
lat = profile.attributes['LATITUDE']     # This won't work if there is no N after lat in the cnv file.
lon = -1 *round(lon, 3)           #Longitude in Thousandth of Decimal
lat = round(lat, 3)           #Latitude in Thousandth Decimal
LaLaLaLaLa = str(int(lat*1000))
LoLoLoLoLo = str(int(lon*1000))
Qc = str(7)

water_depth = cnv.header.split('**')[4].split('*')[0][8:-1]
water_depth = water_depth.replace(' m', '')

# #Section 1: QcLaLaLaLaLa and LoLoLoLoLo
# lon_decimal = math.ceil(cnv.lon * -1) + cnv.lon
# lon_base = math.floor(cnv.lon)
# lon_true = (lon_base * -1) + lon_decimal
# long = round(lon_true, 3)           #Longitude in Thousandth of Decimal
#
# lat = round(cnv.lat, 3)           #Latitude in Thousandth Decimal
# LaLaLaLaLa = str(int(lat*1000))
# LoLoLoLoLo = str(int(long*1000))
# Qc = str(7)
# print(LaLaLaLaLa)
# print(LoLoLoLoLo)



#Section 2: 2z0z0z0z0  Depths in meters, starting with the surface
#           3T0T0T0T0  Temperature in hundredths of a degree Celsius
#           4S0S0S0S0  Salinity Salinity in hundredths of a PSU

Code_D = str(2)
Code_T = str(3)
Code_S = str(4)

Binned_dta = Binned_d[['Depth', 'Temperature', 'Salinity']]       #again, two [[
Binned_dta = Binned_dta.reset_index(drop=True) #remove depth interval index column

#Set Decimal Place
#Binned_d['Temperature']=Binned_d['Temperature'].round(decimals=2)

Binned_dta['Salinity'] = 100 * round(Binned_dta['Salinity'], 2)
Binned_dta['Temperature'] = 100 * round(Binned_dta['Temperature'], 2)
Max_Depth = round(max(Binned_dta['Depth']))         #Get Max depth
Binned_dta['Depth'] = round(Binned_dta['Depth'])   #Don't multiple 100 for Depth

#Binned_dta['Depth_float'] = Binned_dta['Depth'].astype('float') - Binned_dta['Depth'].astype('int') # get the float part of the depth
#Binned_dta = Binned_dta[Binned_dta['Depth_float']<0.1]
Binned_dta = Binned_dta.astype(int)     #to get rid of decimal

#Drop Duplicate and reorganize the list
Binned_dta = Binned_dta.drop_duplicates(subset = ['Depth'])
Binned_dta = Binned_dta.reset_index(drop=True)

#Overlapping subset, Depth Selection
#print(Binned_dta.Depth.values)         #List all depth and maunally depth selection
#selected_depth_pick = [0, 2, 6, 9, 25...]
selected_depth = [2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 320, 340, 360, 380, 400, 420]#, 440, 460, 480, 500, 550, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2700, 3000, 3500, 4000, 4500, 5000]

val = np.intersect1d(Binned_dta['Depth'], selected_depth)
Binned_dta = Binned_dta[Binned_dta.Depth.isin(val)]
Binned_dta = Binned_dta.reset_index(drop=True)

#Plottnig Temperature and Salinity Profile after Bin Average (SH: After depth selection)
fig, ax = plt.subplots()
ax.plot(Binned_dta.Temperature, Binned_dta.Depth, color='green', label='T depth selection')
ax.invert_yaxis()
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_xlabel('Temperature (degree C)')   # Check unit here
ax.set_ylabel('Depth (m)')
ax.legend()

fig, ax = plt.subplots()
ax.plot(Binned_dta.Salinity, Binned_dta.Depth, color='blue', label='S depth selection')
#ax.plot(cast_u['cast1'].Fluorescence, cast_u['cast1'].Pressure, '--', color='green', label='cast1')
ax.invert_yaxis()
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_xlabel('Salinity (PSU)')   # Check unit here
ax.set_ylabel('Depth (m)')
ax.legend()
plt.show()

#Add 5000 to negative temperature
for num in range(0,len(Binned_dta['Temperature'])):
    if Binned_dta['Temperature'][num] < 0:
        Binned_dta['Temperature'][num] = abs(Binned_dta['Temperature'][num]) +5000


#Creating a Hold File for section 2 CTD information
CreateFile = open('CTD_Hold.DTA', "x")


#Open Hold File and import CTD Information
Hold = open('CTD_Hold.DTA', "w")
for i in range(0, len(Binned_dta['Depth'])):
    Hold.write(str(2) + str(Binned_dta['Depth'][i]).zfill(4) + ' ' + str(3) + str(Binned_dta['Temperature'][i]).zfill(4) + ' ' + str(4) + str(Binned_dta['Salinity'][i]).zfill(4) + " " )
Hold.write('55555 1' + str(water_depth).zfill(4))
Hold.close()


#Hold File Re-Format the length of each lines to 60 characters
CTD_Hold = open('CTD_Hold.DTA', 'r')
Content = CTD_Hold.read()
CTD_Hold.close()


Formatted_CTD = open('Formatted_CTD.DTA','w')
for i in range(len(Content)):
    Formatted_CTD.write(Content[i])
    if (i + 1)%72 ==0:
        Formatted_CTD.write('\r')
Formatted_CTD.close()


#Final File
CTD_Data = open('Formatted_CTD.DTA' , 'r')
Section2 = CTD_Data.read()
CTD_Data.close()


Section1 = str('KKYY ') + YY + MM + J + ' ' + GG + gg + '/ ' + Qc + LaLaLaLaLa + ' ' + LoLoLoLoLo + str(' 88881') + str(' 83099')

#Section3 = str('CGBW =')          #<Vector Ship Callsign  
#Section3 = str('CG2958 =')           # < Tully line P call sign
Section3 = str('CG7677 =')           #SoG Neocaligus


#Final_File = open('2020_IGOSS_TESAC_Test.DTA' , 'w')
Final_File = open(CNVfile[0:13] + '.DTA', 'w')
Final_File.write(Section1 + '\n')
Final_File.write(Section2 + '\n')
Final_File.write(Section3)
Final_File.close()


#Delete Unneeded file
os.remove("CTD_Hold.DTA")
os.remove("Formatted_CTD.DTA")

