import numpy as np
import sys
def loadfile(filename):
    f = open(filename,'r')
    lines = f.readlines()
    f.close()

    # Read the data from the bottom
    out_dict = {}
    for i in range(len(lines)-1,-1,-1):

        # Split on white-space; grab frame/distance
        columns = lines[i].split()
        #print columns
        X = float(columns[1])
        Y = float(columns[2])
        Z = float(columns[3])
        out_dict[i] = [X,Y,Z]
    keys=out_dict.keys()
    X = [(out_dict[k][0]) for k in keys]
    Y = [(out_dict[k][1]) for k in keys]
    Z = [(out_dict[k][2]) for k in keys]
    #print X
    out = [X,Y,Z]
    return out

def gyration(f):
    x=f[0]
    y=f[1]
    z=f[2]
    x1=(x-np.mean(x))**2
    y1=(y-np.mean(y))**2
    z1=(z-np.mean(z))**2
    Rg_x=np.sqrt(np.mean(x1))
    Rg_y=np.sqrt(np.mean(y1))
    Rg_z=np.sqrt(np.mean(z1))
    Rg=[Rg_x,Rg_y,Rg_z]
    return Rg
    
def Dz(f):
    Z=f[2]
    z=[]
    for i in Z:
        if i < 0:
            i = i+15.6
        z.append(i)
    dz=np.mean(z)
    return dz
    
def Dzx(f):
    rx=gyration(f)[0]
    rz=gyration(f)[2]
    rz_rx=rz/rx
    dzx=(rz_rx-1)/(rz_rx+1)
    return dzx
    
def check_pbc(f):
    x=f[0]
    y=f[1]
    z=f[2]
    x_real=[]
    z_real=[]
    pbc_x1 = all(x > -7 for x in f[0])
    pbc_x2 = all(x < 7 for x in f[0])
    pbc_z1 = all(z > -7 for z in f[2])
    pbc_z2 = all(z < 7 for z in f[2])
    if (pbc_x1 == False and pbc_x2 == False):
        for i in x:
            if i < 0:
                i = i+15.6
            x_real.append(i)
    else:
        x_real=x
    if (pbc_z1 == False and  pbc_z2 == False):
        for ii in z:
            if ii < 0:
                ii = ii+15.6
            z_real.append(ii)
    else:
        z_real = z
    #print z_real 
    #print count
    out=[x_real,y,z_real]
    return out
        
filename=sys.argv[1]
#filename='frame.ak'
f=loadfile(filename)
real_f = check_pbc(f)
Rg=gyration(real_f)
dz=Dz(real_f)
dzx=Dzx(real_f)
#print real_f[0]
print dz
print dzx