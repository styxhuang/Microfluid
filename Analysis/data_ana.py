import numpy as np
import sys

def readfile(filename):
    out = []
    out1= []
    with open(filename) as infile:
        for line in infile:
            Dz=line.split()[0]
            out.append(abs(float(Dz)-20))
            Dzx=line.split()[1]
            out1.append(float(Dzx))
    return out,out1

id = sys.argv[1]
fname = 'dump-flow-eql-' + id + '.txt'
out=readfile(fname)
#print a
outname = 'dump-flow-eql-' + id + '.txt'
f = open(outname,'w')
for i in range(len(out[0])):
    f.write("%s %s\n" % (out[0][i],out[1][i]))
f.close()
