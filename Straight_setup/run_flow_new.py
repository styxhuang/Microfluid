# /usr/bin/env hoomd
from hoomd_script import *
from hoomd_plugins import dump_zip
import os
import shutil
import re
import sys
import xml.etree.ElementTree as ET
import math as m
import numpy as np

# dumps
dump_period = 1e3
flw_steps = 1e5

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
system = init.read_xml(filename='Init' + fName + '.xml')

# force params
fx_arr = np.linspace(0.001,0.1,10)
fx_fnl = fx_arr[id]

# pair forces
dpd = pair.dpd(r_cut=1.0, T=1.)
dpd.pair_coeff.set('wall', 'S1', A=3.0, gamma= 1.0)
dpd.pair_coeff.set('wall', 'wall', A=0.0, gamma= 1.0)
dpd.pair_coeff.set('S2','S1',A=60.0,gamma=1.0)
dpd.pair_coeff.set('S1','S1',A=25.0,gamma=1.0)
dpd.pair_coeff.set('S2','S2',A=25.0,gamma=1.0)
dpd.pair_coeff.set('S2','wall',A=10.0,gamma=1.0)
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
#dump.dcd('traj-flow' + fName + '.dcd', period = dump_period, overwrite = True)

# dump the system data - position, velocity
# NOTE: this is compressed system data that
# will be post processed later with gtar
zipfile = dump_zip.zipfile('dump' + fName + '.zip',
                static=['type'],
                dynamic={'position': dump_period, 'velocity': dump_period})

# logs
analyze.log('energies-flow' + fName + '.txt', quantities=['temperature', 'potential_energy', 'kinetic_energy'], header_prefix='#', period = dump_period, overwrite = True)

# start up the pos writer
pos = dump.pos(filename="dump-flow" + fName + ".pos", period=dump_period)
pos.set_def('S1', 'sphere 1 CC0000')
pos.set_def('wall', 'sphere 1 336600')
#pos.set_def('S2', 'sphere 1 0000FF')

# main run
# apply the constant force
const = force.constant(fx=fx_fnl, fy=0.0, fz=0.0)
run(flw_steps)

# dump the final xml
dump.xml(filename='Final-flow' + str(int(id)+1) + '.xml', all=True)

