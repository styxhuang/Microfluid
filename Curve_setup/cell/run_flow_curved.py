# /usr/bin/env hoomd
from hoomd_script import *
from hoomd_plugins import fdsa
from hoomd_plugins import dump_zip

import os
import shutil
import re
import sys
import xml.etree.ElementTree as ET
import math as m
import numpy as np

# dumps
dump_period = 1e4
flw_steps = 5e5
run_steps = 1e5

# force params
f_fnl = 0.03

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

# wall params, use system.box for convenience
cyl_r_out = system.box.Lx/2.
cyl_r_in = 4.0

# force field setup
harmonic = bond.harmonic(name="my_bonds")
harmonic.bond_coeff.set('tether', k=40., r0=1.0)
harmonic.bond_coeff.set('tether2', k=400., r0=1.0)

# pair forces
dpd = pair.dpd(r_cut=1.0, T=1.)
dpd.pair_coeff.set(system.particles.types, system.particles.types, A=3.0, gamma= 1.0)
dpd.pair_coeff.set('wall', system.particles.types, A=3.0, gamma= 1.0)
dpd.pair_coeff.set('S1', 'S1', A=25.0, gamma= 1.0)
integrate.mode_standard(dt=0.01)

# set up groups
all = group.all()
groupWALL = group.type(name='groupWALL', type='wall')
notWALL=group.difference(name="particles-not-typeWALL", a=all, b=groupWALL)
integrate.nve(group=notWALL)
#integrate.nve(group=group.all())

#make sure that the neighbor lists do not include particles that are bonded or are in the same body do not interact with one another
nlist.reset_exclusions(exclusions = ['bond', 'body'])

# dump the system data - position, velocity
# NOTE: this is compressed system data that
# will be post processed later with gtar
zipfile = dump_zip.zipfile('dump' + fName + '.zip',
                static=['type'],
                dynamic={'position': dump_period, 'velocity': dump_period})

# logs
analyze.log('energies-flow' + fName + '.txt', quantities=['temperature', 'potential_energy', 'kinetic_energy'], header_prefix='#', period = dump_period, overwrite = True)

# create the wall groups
wallstructure = wall.group()

# add wall cylinder
wallstructure.add_cylinder(r=cyl_r_out, origin=(0,0,0), axis=(0,0,1), inside=True)
wallstructure.add_cylinder(r=cyl_r_in, origin=(0,0,0), axis=(0,0,1), inside=False)

# wall force
lj=wall.lj(wallstructure, r_cut=2.0**(1.0/6.0))
#lj.force_coeff.set(['S1','micelle','polymer','hydroxyl','core'], sigma=1.0,epsilon=100.0)
lj.force_coeff.set(['S1','micelle','polymer','hydroxyl','core'], sigma=1.0,epsilon=100.0, r_extrap=1.1)
lj.force_coeff.set(['wall'], sigma=1.0,epsilon=0.0)

# main run
# apply the constant force
fdsaForce = fdsa.compute.CntrlCnstCylPotential(f=f_fnl)
run(flw_steps)

# adjust dump period
dump_period = 1e3

#start the logs, including restart file
dump.dcd('traj-flow' + fName + '.dcd', period = dump_period, overwrite = True)

# start up the pos writer
pos = dump.pos(filename="dump-flow" + fName + ".pos", period=dump_period)
pos.set_def('S1', 'sphere 1 CC0000')
pos.set_def('wall', 'sphere 1 336600')
pos.set_def('micelle', 'sphere 1 0000FF')

# remove the constant force and run
del fdsaForce
run(2*run_steps)

# dump the final xml
dump.xml(filename='Final-flow' + str(int(id)+1) + '.xml', all=True)

