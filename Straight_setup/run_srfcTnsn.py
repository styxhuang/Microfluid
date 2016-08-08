# /usr/bin/env hoomd
from hoomd_script import *
from hoomd_plugins import fdsa

import os
import shutil
import re
import sys
import xml.etree.ElementTree as ET
import math as m
import numpy as np

# params
N_solv = 384000
r_drop = 5.0

# geometry
wall_dens = 61.35
solv_dens = 4.0
a = ((2./3.*m.pi)/wall_dens)**(1./3.) #wall scale factor

# dumps
dump_period = 1e2
run_steps = 1e5

# DPD interaction coeffs
aS11 = 20.0
aS22 = 20.0
aS12 = 20.0

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

# read in the Init file
system = init.create_random(N=N_solv, phi_p=solv_dens, min_dist=0.1,name='S1')
#system = init.read_xml(filename='Init' + fName + '.xml')

# manipulate particle type(s)
system.particles.types.add('S2')
for p in system.particles:
    # make the top half of the box type 'S2'
    if p.position[2] > 0.0:
        p.type='S2'

# NOTE: in these simulations epsilon has ben rescaled so that the ODT for the given volume fraction
# is closer to that of the cores.
dpd = pair.dpd(r_cut=1.0, T=1.)
dpd.pair_coeff.set('S1', 'S2', A=aS12, gamma= 1.0)
dpd.pair_coeff.set('S1', 'S1', A=aS11, gamma= 1.0)
dpd.pair_coeff.set('S2', 'S2', A=aS22, gamma= 1.0)
#dpd.pair_coeff.set(system.particles.types, system.particles.types, A=20.0, gamma= 1.0)
integrate.mode_standard(dt=0.01)

# set up groups
all = group.all()
integrate.nve(group=group.all())

#make sure that the neighbor lists do not include particles that are bonded or are in the same body do not interact with one another
nlist.reset_exclusions(exclusions = ['bond', 'body'])

#start the logs, including restart file
#dump.pos(filename="dump" + fName + ".pos", period=dump_period)
#dump.dcd('traj' + fName + '.dcd', period = dump_period, overwrite = True)

# logs
analyze.log('energies' + fName + '.txt', quantities=['temperature', 'potential_energy', 'kinetic_energy', 'pressure_xx', 'pressure_yy', 'pressure_zz'], header_prefix='#', period = dump_period, overwrite = True)

# exit for testing
dump.xml(filename='Init' +  fName  + '.xml', all=True)

# run
run(run_steps)

