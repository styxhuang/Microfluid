#draw streamlines of the system
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
    # extract the data using gtar. Data in the last frame
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
    out1 = [p[0],p[2],v[0],v[2]] #0 stands for x direction, 2 stands for z direction
    out1 = map(list, zip(*out1))
    #index, value = max(enumerate(out[2]), key=operator.itemgetter(1))
    #v_max=[out[1][index],out[2][index]]
    return out,out1#,v_max

def sampleDistances(nice_level,data):
    x=np.array(zip(*data)[0])#transform data matrix
    y=np.array(zip(*data)[1])
    beg=min(x)
    end=max(x)
    start=beg
    interval=(end-beg)/nice_level
    a={} #position
    b={} #velocity
    c=[] #plot data
    for i in range(0,nice_level,1):
        bin=beg+interval*(i+1)
        a=np.mean(x[np.where(np.logical_and(x>start,x<bin))])
        if a<0:#boundary condition, since wall is put in the middle of the tube
            a=a+30
        else:
            a=a
        b=np.mean(y[np.where(np.logical_and(x>start,x<bin))])
        start = bin
        c.append([a,b])
    return c
def avg(data): #average position and velocity for each grid
    out=[]
    px=[]
    pz=[]
    vx=[]
    vz=[]
    for i in range(len(data)): #collect all x or z or vx or vz in Beads
        aa=data[i][0]
        if aa<0:
            aa=aa+15
        bb=data[i][1]
        if bb<0:
            bb=bb+30
        cc=data[i][2]
        dd=data[i][3]
        px.append(aa)
        pz.append(bb)
        vx.append(cc)
        vz.append(dd)
        average_px=np.mean(px)
        average_pz=np.mean(pz)
        average_vx=np.mean(vx)
        average_vz=np.mean(vz)
#out.append([average_px,average_pz,average_vx,average_vz])
    return average_px,average_pz,average_vx,average_vz
def sampleDistances_xz(nice_level,data):
    data_trans=zip(*data)
    x=np.array(data_trans[0])#transform data matrix, x direction
    x1=np.array(data_trans[1])#z position
    #x2=np.array(data_trans)[2])#y position
    y=np.array(data_trans[2])#vx
    y1=np.array(data_trans[3])#vz
    beg=min(x)
    beg1=min(x1)
    end=max(x)
    end1=max(x1)
    start=beg
    start1=beg1
    interval=(end-beg)/nice_level
    interval1=(end1-beg1)/nice_level
    #Judge where S2 coordinate along y direction
    a={} #position
    b={} #velocity
    c=[] #plot data
    out=[]
    print "interval",interval
    print "interval1",interval1
    print "beg",beg
    print "end",end
    print "beg1",beg1
    print "end1",end1
    for i in range(0,nice_level,1):
        Beads_org=[]
        Beads=[]
        bin=beg+interval*(i+1)#along x direction
        for ii in range(len(data)): #collect beads in grid of x direction
            if data[ii][0] > start and data[ii][0] < bin:
                Beads_org.append(data[ii])
        for iii in range(0,nice_level,1): #collect beads in grid of z direction
            bin1=beg1+interval1*(iii+1)#along z direction
            for iv in range(len(Beads_org)):
                if Beads_org[iv][1] > start1 and Beads_org[iv][1] < bin1:
                    Beads.append(Beads_org[iv])
                    [px,pz,vx,vz]=avg(Beads)
                    out.append([px,pz,vx,vz])
                    #print out
                start1 = bin1
        start = bin
    return out
id = sys.argv[1]
[data,data1] = readData(id)
print len(data)
a=sampleDistances(500,data)
b=sampleDistances_xz(2000,data1)
f = file("1-plot-data.txt","w")
for r in b:
    f.write("\t".join(map(str,r)) + "\n")
f.close()
f = file("plot-data.txt","w")
for r in a:
    f.write("\t".join(map(str,r)) + "\n")
f.close()
#v_average=open("vFile" + id + ".txt","w")
#v_average.write("Position= "+ str(v_max[0])+'\n')
#v_average.write("Max-velocity= "+ str(v_max[1])+'\n')
#_average.close()
