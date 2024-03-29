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
            a=a+40
        else:
            a=a
        b=np.mean(y[np.where(np.logical_and(x>start,x<bin))])
        start = bin
        c.append([a,b])
    return c
def axis(data): #fix BC
    out=[]
    for z in range(len(data)): #collect all x or z or vx or vz in Beads
        aa=data[z][0]
        if aa<0:
            aa=aa+20
        bb=data[z][1]
        if bb<0:
            bb=bb+40
        cc=data[z][2]
        dd=data[z][3]
        out.append([aa,bb,cc,dd])
#print out
    return out
def avg(data): #average position and velocity for each grid
    #out=[]
    px=[]
    pz=[]
    vx=[]
    vz=[]
    for z in range(len(data)): #collect all x or z or vx or vz in Beads
        aa=data[z][0]
        if aa<0:
            aa=aa+20
        bb=data[z][1]
        if bb<0:
            bb=bb+40
        cc=data[z][2]
        dd=data[z][3]
        px.append(aa)
        pz.append(bb)
        vx.append(cc)
        vz.append(dd)
        global average_px
        global average_pz
        global average_vx
        global average_vz
        average_px=np.mean(px)
        average_pz=np.mean(pz)
        average_vx=np.mean(vx)
        average_vz=np.mean(vz)
#out.append([average_px,average_pz,average_vx,average_vz])
    return average_px,average_pz,average_vx,average_vz
def sampleDistances_xz(nice_level,data):
    data=axis(data)
    data_trans=zip(*data)
    x=np.array(data_trans[0])#transform data matrix, x direction
    x1=np.array(data_trans[1])#z position
    #x2=np.array(data_trans)[2])#y position
    y=np.array(data_trans[2])#vx
    y1=np.array(data_trans[3])#vz
    beg=min(x) #x direction
    beg1=min(x1) #z direction
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
    for i in range(0,nice_level,1):#collect beads in grid of x direction
        Beads_org=[]
        bin=beg+interval*(i+1)#along x direction
        for ii in range(len(data)):
            print "start=",start,"bin=",bin
            if data[ii][0] > start and data[ii][0] < bin:
                Beads_org.append(data[ii])
        print Beads_org
        for iii in range(0,nice_level,1): #collect beads in grid of z direction
            Beads=[]
            bin1=beg1+interval1*(iii+1)#along z direction
            for iv in range(len(Beads_org)): #put fit balls inside the bin
                print "start1=",start1,"bin1=",bin1
                if Beads_org[iv][1] > start1 and Beads_org[iv][1] < bin1:
                    Beads.append(Beads_org[iv])
                print "round=",iv
        #print Beads
            print "Average collect beads"
            [p_x,p_z,v_x,v_z]=avg(Beads)
            print "put into matrix"
            out.append([p_x,p_z,v_x,v_z])
            print out
            start1 = bin1
        start = bin
    return out
id = sys.argv[1]
[data,data1] = readData(id)
print len(data)
#a=sampleDistances(500,data)
b=sampleDistances_xz(25,data1)
f = file("1-plot-data.txt","w")
for r in b:
    f.write("\t".join(map(str,r)) + "\n")
f.close()
f = file("plot-data.txt","w")
#for r in a:
#    f.write("\t".join(map(str,r)) + "\n")
#f.close()
#v_average=open("vFile" + id + ".txt","w")
#v_average.write("Position= "+ str(v_max[0])+'\n')
#v_average.write("Max-velocity= "+ str(v_max[1])+'\n')
#_average.close()
