#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 14:17:37 2022

@author: lcabral4
"""

# Define the new Kernel that mimics RW
def VerticalMovement(particle, fieldset, time):
    
    # set particle salinity at new depth for output
    particle.salt =  fieldset.salt[time, particle.depth, particle.lat, particle.lon]
    particle.temp = fieldset.temp[time, particle.depth, particle.lat, particle.lon]


    # can code vertical diffusivity here with random walk
    # ocean parcels has some random walk functions as well
    # have particle.dt for time step, particle.depth for depth
    
    # for now, lock to depth (surface)
#    particle.depth = 0

def OutOfBounds ( particle , fieldset , time ):

    particle.delete ()
    
from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4, ErrorCode, Variable
from datetime import timedelta, datetime
import numpy as np
import random
import netCDF4
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import cartopy.crs as ccrs 
#from mpl_toolkits.basemap import Basemap
from cartopy import config
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker 
from parcels import plotting
import matplotlib.pylab as pl
import cartopy.feature as cfeature
#from x import *
from Scotia import *


# Load the HYCOM Analysis data in the Gulf of Maine
# The paths/datafiles should be read in from a control file
filenames = {'U': "./hycom_data/HAB2*",
             'V': "./hycom_data/HAB2*",
             'salt': "./hycom_data/HAB2*",
             'temp': "./hycom_data/HAB2*"}
variables = {'U': 'water_u',
             'V': 'water_v',
             'salt': 'salinity',
             'temp': 'water_temp'}
dimensions = {'lat': 'lat', 'lon': 'lon', 'time': 'time'}
fieldset = FieldSet.from_netcdf(filenames, variables, dimensions,allow_time_extrapolation = True)
fieldset.mindepth = fieldset.U.depth[0]  # uppermost layer in the hydrodynamic data



#npart=2
# print the domain boundaries to the screen
print("domain boundaries")
print(fieldset.U.lon[0],fieldset.U.lon[-1],fieldset.U.lat[0],fieldset.U.lat[-1])


# Define a new Particle type including extra Variables
#class ArgoParticle(JITParticle):
#    # Phase of cycle: init_descend=0, drift=1, profile_descend=2, profile_ascend=3, transmit=4
#    cycle_phase = Variable('cycle_phase', dtype=np.int32, initial=0.)
#    cycle_age = Variable('cycle_age', dtype=np.float32, initial=0.)
#    drift_age = Variable('drift_age', dtype=np.float32, initial=0.)
#    S = Variable('S', dtype=np.float32, initial=np.nan)  # store salinity
    
# Define a new Particle type including extra Variables
class HabParticle(JITParticle):
    # Phase of cycle: init_descend=0, drift=1, profile_descend=2, profile_ascend=3, transmit=4
    salt = Variable('salt', dtype=np.float32, initial=np.nan)  # store salinity
    temp = Variable('temp', dtype=np.float32, initial=np.nan)  # store water temperature

# Initiate two Isopycnal Floats with staggered starts and different programmed drift densities initiated from 
# different depths and horizontal locations.  These variables here (lon, lat, time, float_density) should
# be read in from a control file.


x = []
y = []

lonmin 
lonmax 
latmin 
latmax 
n
days
year
month
day
outputminutes
dtminutes
npart = n  # number of particles to be released
for i in range(n):
    lon = lonmin + random.uniform(0, 1)*(lonmax-lonmin)
    x.append(lon)
    lat = latmin + random.uniform(0, 1)*(latmax-latmin)
    y.append(lat)
time = datetime(year,month,day)

pset = ParticleSet(fieldset=fieldset, pclass=HabParticle, lon=x, lat=y, time=time)


fig = plt.figure(figsize=(13,10))


#for i in range(5):
#    pset = ParticleSet.from_list(fieldset=fieldset,
#                                pclass=HabParticle,
#                                lon=[-62 - random.randint(0,5), -57 - random.randint(0,5)],
#                                lat =[43 + random.randint(0,5), 38 + random.randint(0,5)],
#                                depth =[0 + random.randint(0,15), 0+random.randint(0,15)],
#                                time=[datetime(2015,9,1)])

#print(days)
kernels = VerticalMovement + pset.Kernel(AdvectionRK4) 
output_file = pset.ParticleFile(name="float_output/Scotia", outputdt=timedelta(minutes=outputminutes))
pset.execute(kernels, runtime=timedelta(days=days), dt=-timedelta(minutes=dtminutes), output_file=output_file, recovery={ErrorCode.ErrorOutOfBounds: OutOfBounds})
    
#pset.execute(kernels, runtime=timedelta(days=600.), dt=timedelta(minutes=-30), output_file=output_file, recovery={ErrorCode.ErrorOutOfBounds: OutOfBounds})

output_file.export()  # export the trajectory data to a netcdf file

nc = netCDF4.Dataset("float_output/Scotia.nc")

x = nc.variables["lon"][:].squeeze()
time = nc.variables["time"][:].squeeze()
y = nc.variables["lat"][:].squeeze()
z = nc.variables["z"][:].squeeze()
salt = nc.variables["salt"][:].squeeze()
temp = nc.variables["temp"][:].squeeze()
nc.close()
fig = plt.figure(figsize=(13,10))
for p in range(x.shape[0]):
    cb = plt.scatter(x[p,:], y[p,:], c=temp[p,:], s=0.01, marker = "o")
    plt.scatter(x[:,0], y[:,0], s= 20, marker = 's') 
plt.title('Temperature Variable')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.savefig("Scotia.png")
    


fig = plt.figure(figsize=(13,10))
#    for p in range(x.shape[0]):
#        cb = plt.scatter(x[p], y[p], c=temp[p], s=20, marker = "o")
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-74,-1, 70, 20], ccrs.PlateCarree())
ax.coastlines()
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.COASTLINE)
#x = np.linspace(-65, -75)
#y = np.linspace(35, 45)
#plt.title('Temperature Variable')
#ax.set_xlabel("Longitude")
#ax.set_ylabel("Latitude")
#ax.set_xticks(np.arange(-80,-65,100), crs=ccrs.PlateCarree())
lon_formatter = cticker.LongitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.set_xticks([-66, -65], crs=ccrs.PlateCarree())
ax.set_yticks([45, 46], crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(40,50,20), crs=ccrs.PlateCarree())
lat_formatter = cticker.LatitudeFormatter()
#ax.yaxis.set_major_formatter(lat_formatter) 
#lon, lat = np.meshgrid(x, y)
for p in range(x.shape[0]):
    cb = plt.scatter(x[p,:], y[p,:], c=temp[p,:], s=0.0001, marker = "o")
    plt.scatter(x[:,0], y[:,0]) 
print(temp, 'temp')



# plot




plt.title('Temperature Variable')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.savefig("Scotia_Temp.png")    