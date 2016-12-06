import numpy as np
import sys

def readfile(filename,cut):
    out = []
    out1= []
    with open(filename) as infile:
        for line in infile:
            Dz=line.split()[0]
            Dzx=line.split()[1]
            out.append(float(Dz))
            out1.append(float(Dzx))
    del out[0:cut]
    del out1[0:cut]
    return out,out1
def estimated_autocorrelation(x):
    x=np.array(x)
    n = len(x)
    variance = np.var(x)
    x = x-x.mean()
    r = np.correlate(x, x, mode = 'full')[-n:]
    assert np.allclose(r, np.array([(x[:n-k]*x[-(n-k):]).sum() for k in range(n)]))
    result = r/(variance*(np.arange(n, 0, -1)))
    return result
def selectsamples(list1,list2,lags):
    b=[]
    c=[]
    d1=[]
    d2=[]
    l=0
    len1=len(list1)
    while l<len1:
        c.append(l)
        l=l+lags
    #print c #c is the index of the sample
    for i in c:
        b.append([list1[i],list2[i]])
    for ii in range(len(b)):
        d1.append(b[ii][0])
        d2.append(b[ii][1])
    return d1,d2  
    
id = sys.argv[1]
lags=int(sys.argv[2])
cut= int(sys.argv[3])
fname = 'dump-flow-eql-' + id + '.txt'
a1,a2=readfile(fname,cut)
out=selectsamples(a1,a2,lags)
#print out
c1=np.array(out[0])
c2=np.array(out[1])
avg1=c1.mean()
avg2=c2.mean()
std1=np.sqrt(c1.var())
std2=np.sqrt(c2.var())
ana='ana' + id + '.txt'
f = open(ana,'w')
#f.write("Dz_avg=%4f, Dz_std=%4f\n" % (avg1,std1))
#f.write("Dzx_avg=%4f, Dzx_std=%4f\n\n" % (avg2,std2))
for i in range(len(out[0])):
    f.write("%4f %4f\n" % (out[0][i],out[1][i]))
f.close()