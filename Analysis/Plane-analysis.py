import gtar
import sys
import numpy as np
import operator

def readData(id):
    # read the zip file with gtar
    fname='dump-eql-' +id + '.zip'
    g = gtar.GTAR(fname, 'r')
    types = g.staticRecordNamed('type')
    #nParticles = len(list(g.recordsNamed('position'))[-1][1])
    nFrames = len(list(g.recordsNamed('position')))
    #begFr = 0
    endFr = nFrames
    # handles for file i/o
    print('Unpacking frame ' + str(endFr))
    # extract the data using gtar
    pList = list(g.recordsNamed('position'))[endFr-1][1]
    vList = list(g.recordsNamed('velocity'))[endFr-1][1]
    # grab velocity by type, ignore walls
    v_S1 = vList[types == 0]
    #v_S2 = vList[types == 1]
    # grab position by type, ignore walls
    p_S1 = pList[types == 0]
    #p_S2 = pList[types == 1]
    v=map(list, zip(*v_S1)) #transpose the list
    p=map(list, zip(*p_S1))
    out = [p[2],v[0]]
    out = map(list, zip(*out))
    index, value = max(enumerate(out[1]), key=operator.itemgetter(1))
    v_max=[out[0][index],out[1][index]]
    return out,v_max

def sampleDistances(nice_level,data):
    x=np.array(zip(*data)[0])#transform data matrix
    y=np.array(zip(*data)[1])
    beg=min(x)
    end=max(x)
    start=beg
    interval=(end-beg)/nice_level
    print "interval",interval
    print "beg",beg
    print "end",end
    a={} #position
    b={} #velocity
    c=[] #plot data
    for i in range(0,nice_level,1):
        bin=beg+interval*(i+1)
        a=np.mean(x[np.where(np.logical_and(x>start,x<bin))])
        if a<0:#boundary condition, since wall is put in the middle of the tube
            a=a+15.6
        else:
            a=a
        b=np.mean(y[np.where(np.logical_and(x>start,x<bin))])
        start = bin
        c.append([a,b])
    return c

id = sys.argv[1]
[data,v_max] = readData(id)
print len(data)
a=sampleDistances(500,data)
f = file("plot-data.txt","w")
for r in a:
    f.write("\t".join(map(str,r)) + "\n")
f.close()
v_average=open("vFile" + id + ".txt","w")
v_average.write("Position= "+ str(v_max[0])+'\n')
v_average.write("Max-velocity= "+ str(v_max[1])+'\n')
v_average.close()
