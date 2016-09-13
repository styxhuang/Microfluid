# /usr/bin/env hoomd
from hoomd_script import *

import os
import shutil
import re
import sys
import xml.etree.ElementTree as ET
import math as m
import numpy as np


######################
##### Init params #####
######################

# particle numbers
N_solv = 1e4
N_drop = 1

# dumps
dump_period = 1e2
#rsz_steps = 1e4
rsz_steps = 1e3
#eql_steps = 1e5
eql_steps = 1e3

# geometry
#wall_dens = 61.35
wall_dens = 6.135
solv_dens = 4.0

# lattice const determined by wall_dens
a = ((2./3.*m.pi)/wall_dens)**(1./3.)

# geometry params
cyl_dr = 5.
r_in_fctr = 1./5.
r_out_fctr = 1./3.

R_in = 5.0 #set the inner R_cyl
R_out = R_in + (cyl_dr+4*a) #set outside R_cyl

lz = N_solv/(6*solv_dens*cyl_dr**2)
lx = 2*R_out
ly = lx
box_len = lz #store Lz for wall computation

# print for testing
print('Lz is: ' + str(lz))

# get the job index from PBS_ARRAYID, or return 0 if it is not specified (for test jobs)
def get_array_id():
    pbs_arrayid = os.getenv('PBS_ARRAYID');
    if pbs_arrayid is None:
        return 0
    else:
        return int(pbs_arrayid) - 1;

# set up the initial and final box dimensions
# beads are all diameter = 1.0
id = get_array_id();
fName = '-eql-' + str(int(id) + 1)

# function to build up random collection of solvent particles
def random_solv_builder():
    #create the random positions
    print('In random_solv_builder')
    print(N_solv)
    system = init.create_random(N=N_solv, phi_p=phi_init, min_dist=0.1)
    for p in system.particles:
        grid_solv_pos.append([p.position[0],p.position[1],p.position[2]])
    return system.box.Lx

# random solvent **placer**, no system init via hoomd
def random_solv_plcr():
    # from lx,ly,lz randomly pluck positions
    for i in range(int(N_solv)):
        x = lx*np.random.rand()-lx/2.
        y = ly*np.random.rand()-ly/2.
        z = lz*np.random.rand()-lz/2.
        grid_solv_pos.append([x,y,z])
    return

# function to build up cylindrical walls of beads
def cyl_wall_builder(R,a):
    # (*)NOTE: this returns the box lengths
    # create an array of cylinder positions
    rads = [R, R-0.5*a, R-a, R-1.5*a]
    zs = np.linspace(-box_len/2.,box_len/2.,m.ceil(box_len/a))
    for rad in rads:
        cnt = 0
        theta = np.linspace(0,2*m.pi,m.ceil(m.pi*2*rad/a))
        for z in zs:
            for th in theta:
                if cnt % 2 == 0:
                    # shift the positions on even rows
                    th += m.pi/(len(theta))
                r = rad
                x = r*m.cos(th)
                y = r*m.sin(th)
                grid_wall_pos.append((x, y, z))
            cnt += 1
    return

# declare pos array(s)
star_pos = []
grid_solv_pos = []
grid_wall_pos = []
masses = []
diameters = []
bodies = []
types = []
bonds = []

# call parser, which will fill pos and map_pos
#parse = xml_parser()

# create the particle grid
solv_build = random_solv_plcr() #solvent
wall_build = cyl_wall_builder(R_in,a) #inner cyl
wall2_build = cyl_wall_builder(R_out,a) #outer cyl

# ***TESTING***
print('Length of solv_pos: ' + str(len(grid_solv_pos)))
print('Length of wall_pos: ' + str(len(grid_wall_pos)))

# aggreate all arrays
full_pos = grid_solv_pos + grid_wall_pos

# build a single list for each particle field
masses.extend(int(N_solv)*['1.0']) #tack on the solvent
masses.extend(len(grid_wall_pos)*['1.0']) #tack on the walls
diameters.extend(int(N_solv)*['1.0']) #tack on the solvent
diameters.extend(len(grid_wall_pos)*['1.0']) #tack on the walls
bodies.extend(int(N_solv)*['-1']) #tack on the solvent
bodies.extend(len(grid_wall_pos)*['-1']) #tack on the walls
types_solv = int(N_solv)*['S1']
types_wall = len(grid_wall_pos)*['wall']
types = types_solv + types_wall

#print('Print for testing')
print(len(masses))
print(len(diameters))
print(len(bodies))
print(len(types))
print(len(bonds))
print(len(full_pos))

# catch improper configurations
if len(full_pos) != len(masses):
    print('The position and mass arrays are not the same length!')
    sys.exit(-1)

# write out the file
with open('Init' + fName + '.xml', 'w') as inpFile:
    inpFile.write('\n'.join(['<?xml version="1.1" encoding="UTF-8"?>',
                             '<hoomd_xml version="1.5">',
                             '<configuration time_step = "0" dimensions = "3">']))
    inpFile.write('<box lx="{size1}" ly="{size2}" lz="{size3}" />\n'.format(size1=lx,size2=ly,size3=lz))
    inpFile.write('<position>\n' + '\n'.join('{} {} {}'.format(x, y, z) for (x, y, z) in full_pos)
        + '</position>\n')
    inpFile.write('<mass>\n' + '\n'.join(str(mass) for mass in masses) + '</mass>\n')
    inpFile.write('<diameter>\n' + '\n'.join(str(diameter) for diameter in diameters) + '</diameter>\n')
    inpFile.write('<body>\n' + '\n'.join(str(body) for body in bodies) + '</body>\n')
    inpFile.write('<type>\n' + '\n'.join(str(type) for type in types) + '</type>\n')
    inpFile.write('\n</configuration>\n</hoomd_xml>\n')


######################
###### Main Run ######
######################

# read in the Init file
system = init.read_xml(filename='Init' + fName + '.xml')

# wall params
cyl_r_in = system.box.Lx*r_in_fctr
cyl_r_out = system.box.Lx*r_out_fctr

# NOTE: in these simulations epsilon has ben rescaled so that the ODT for the given volume fraction
# is closer to that of the cores.
dpd = pair.dpd(r_cut=1.0, T=1.)
dpd.pair_coeff.set(system.particles.types, system.particles.types, A=20.0, gamma= 1.0)
dpd.pair_coeff.set('wall', system.particles.types, A=0.0, gamma= 1.0)
integrate.mode_standard(dt=0.01)

# set up groups
all = group.all()
groupWALL = group.type(name='groupWALL', type='wall')
notWALL=group.difference(name="particles-not-typeWALL", a=all, b=groupWALL)
integrate.nve(group=notWALL)
#integrate.nve(group=group.all())

#make sure that the neighbor lists do not include particles that are bonded or are in the same body do not interact with one another
nlist.reset_exclusions(exclusions = ['bond', 'body'])

#start the logs, including restart file
#dump.pos(filename="dump" + fName + ".pos", period=dump_period)
#dump.dcd('traj-eql' + fName + '.dcd', period = dump_period, overwrite = True)

# logs
#analyze.log('energies-eql' + fName + '.txt', quantities=['temperature', 'potential_energy', 'kinetic_energy'], header_prefix='#', period = dump_period, overwrite = True)

# create the wall groups
wallstructure = wall.group()

# add wall cylinder
wallstructure.add_cylinder(r=cyl_r_out, origin=(0,0,0), axis=(0,0,1), inside=True)
wallstructure.add_cylinder(r=cyl_r_in, origin=(0,0,0), axis=(0,0,1), inside=False)

# wall force
lj=wall.lj(wallstructure, r_cut=2.0**(1.0/6.0))
lj.force_coeff.set(['S1','polymer','hydroxyl','core'], sigma=1.0,epsilon=100.0, r_extrap=1.1)
lj.force_coeff.set(['wall'], sigma=1.0,epsilon=0.0)

# run to set up geometry
run(rsz_steps)

# release the walls and equilibrate
dpd.pair_coeff.set('wall', system.particles.types, A=100.0, gamma= 1.0)
lj.force_coeff.set(['S1','polymer','hydroxyl','core'], sigma=1.0,epsilon=100.0)

# wall params
cyl_r_out = system.box.Lx/2.
cyl_r_in = 4.0

# move the walls
wallstructure.cylinders[0].r=cyl_r_out
wallstructure.cylinders[1].r=cyl_r_in

# eql, release walls, eql
run(eql_steps)


######################
#### Micelle Init ####
######################

# add the types via snapshot
snap = system.take_snapshot(bonds=True)
snap.bonds.types = ['tether', 'tether2']
#system.restore_snapshot(snap, bonds=True)
system.restore_snapshot(snap)

# read the coordinates into a single flat list
micelle = []
f = open('micelle.txt', 'r')
for line in f:
    line = line.strip()
    for number in line.split():
        # check for small numbers, set to 0
        if abs(float(number)) < 1e-14:
            number = 0.0
        micelle.append(float(number))

# resphape the list into proper x, y, z coordinates
micelle = [micelle[3*i : 3*(i+1)] for i in range(int(len(micelle)/3))]
num_mbr_bds = len(micelle)

# manipulate particle type(s)
system.particles.types.add('micelle')
for m in range(len(N_drop*micelle)):
    system.particles.add('micelle')

# add the particles, shift the positions
# drops are stacked along the z-axis, upper quadrant
cnt = 0
mcl_z_arr_idx = 0
mcl_z_arr = np.linspace(-1*system.box.Lz/4.75,system.box.Lz/4.75,N_drop)
for p in system.particles:
    if p.type=='micelle':
        if cnt % num_mbr_bds == 0 and cnt > 0:
            mcl_z_arr_idx += 1
        x_new = micelle[cnt % len(micelle)][0] + system.box.Lx/4.75
        y_new = micelle[cnt % len(micelle)][1] + system.box.Ly/4.75
        z_new = micelle[cnt % len(micelle)][2] + mcl_z_arr[mcl_z_arr_idx]
        p.position = (x_new, y_new, z_new)
        p.diameter = 1.0
        cnt += 1

# Set up lists to identify which particles should be bonded
# Calculate the distance from p_i to all other particles, p_j
# If this distance is ~particle diameter, then add a bond
# NOTE: Will need to keep two lists of tags
cnt = 0
r_max = 0.75
tags_list = []
tags_mcls = []
groupM = group.type(name="micelle-particles", type='micelle')
for p in groupM:
    tags = []
    tags_mcls.append(p.tag)
    p_i = p.position
    for p in groupM:
        p_j = p.position
        dx = p_j[0] - p_i[0]
        dy = p_j[1] - p_i[1]
        dz = p_j[2] - p_i[2]
        r = (dx**2 + dy**2 + dz**2)**(1./2.)
        if r > 0.1 and r < r_max:
            tags.append(p.tag)
    tags_list.append(tags)

# loop through lists, add the bonds
cnt = 0
for t_i in tags_mcls:
    for t_j in tags_list[cnt]:
        if t_i == t_j:
            pass
        else:
            system.bonds.add("tether", t_i, t_j)
    cnt += 1

# dump the final xml
dump.xml(filename='Init' +  fName  + '.xml', all=True)

