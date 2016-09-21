import sys
import numpy as np
def readfile():
    datafile=open('1.txt')
    data=datafile.readlines()
    file_params=open('3.txt','r')
    lines=file_params.readlines()
    line1=lines[0] #s2 particle number
    line2=lines[1] #frame number
    datafile.close()
    return data,line1,line2

def split_file(lines,partiN): #gather all particle velocity in one frame
    out_dict = {}
    for i in range(int(partiN)-1,-1,-1):
        # Split on white-space; grab frame/distance
        columns = lines[i].split()
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
            i = i+40
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
    pbc_x1 = all(x > -8 for x in f[0]) #x direction range 20
    pbc_x2 = all(x < 8 for x in f[0])  
    pbc_z1 = all(z > -18 for z in f[2])#z direction range 40
    pbc_z2 = all(z < 18 for z in f[2])
    if (pbc_x1 == False and pbc_x2 == False):
        for i in x:
            if i < 0:
                i = i+20
            x_real.append(i)
    else:
        x_real=x
    if (pbc_z1 == False and  pbc_z2 == False):
        for ii in z:
            if ii < 0:
                ii = ii+40
            z_real.append(ii)
    else:
        z_real = z
    #print z_real 
    #print count
    out=[x_real,y,z_real]
    return out
[lines,partiN,frameN]=readfile()
D=[]
#for i in range(1): #(int(frameN)):
for i in range(int(frameN)):
    #a=[lines[j] for j in range(((int(partiN)+1)*i+int(partiN)),(int(partiN)+1)*i+1,-1)] #all velocities in frame i
    a=[lines[j] for j in range((int(partiN)+1)*i+1,(int(partiN)+1)*i+int(partiN)+1)]
    f=split_file(a,partiN)
    real_f = check_pbc(f)
    Rg=gyration(real_f)
    dz=Dz(real_f)
    dzx=Dzx(real_f)
    d=[dz,dzx]
    D.append(d)
filename=sys.argv[1]
filename+='.txt'
f = open(filename,'w')
for output in D:
    f.write("%s %s\n" % (output[0],output[1]))
f.close()
#print Out
