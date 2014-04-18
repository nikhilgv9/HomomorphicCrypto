import random
import math
import bigfloat
import ast
from circuit import *
from common import *

debug=False

# Parameters
"""
Lambda #security parameter
w size of the plain text integer
"""
Lambda = 4 #security parameter
w=1 #size of the plain text integer here it is zero or 1 so only 1 bit


def D(gamma,rho,p):
    #q=random.randrange(1,int(2**gamma/p-1))
    q=random.randrange(int(2*gamma),int(2**gamma/p-1)) #Avoiding smaller values
    #q=random.randrange(1,int(2*gamma)) #Control over length of public keys
    r=random.randrange(-2**rho,2**rho)
    #r=1
    x=p*q+r
    return x

def D1(gamma,rho,p,i):
    q=random.randrange(int(2**(gamma+i-1)/p),int(2**(gamma+i)/p-1))
    #q=random.randrange(int(4*(gamma+i-1)/p),int(16*(gamma+i)+1)) #Control over length of public keys
    r=random.randrange(-2**rho,2**rho)
    #r=0
    x=2*(p*q+r)
    return x

def Initialize(Lambda):
    if Params.theta==0:
        Params.rho=int(w*log2(Lambda)) # size of noise
        Params.rho1=int(w*log2(Lambda)+1) # size of secondary noise
        Params.eta=int(Params.rho*Lambda*log2(Lambda)**2) #size of private key
        Params.gamma=int(w*(Params.eta**2)*log2(Lambda)) #Bit length of integers in public key
        Params.tho=int(Params.gamma+w*log2(Lambda))# number of integers in the public key
        Params.kappa = Params.gamma + 2
        Params.theta = Lambda
        Params.bigo = int(w * Params.kappa * log2(Lambda)/32)
        Params.prec = int(log2(Params.theta)+3.5)
        Params.n = Params.prec+1
        Params.logtheta = int(log2(Params.theta))+1

def SomeWhatKeyGen(Lambda):
    Initialize(Lambda)
    largestKey=8**(Params.eta*(2**Params.rho1))-1
    smallestKet=8**(Params.eta*(2**Params.rho1)-1)+1
    p = random.randrange(smallestKet,largestKey,2)
    sk = p
    x0=1
    while mods(x0,p)%2 != 0:
        pk0=[]
        for i in range(0,Params.tho/32+1):
            t=D(Params.gamma,Params.rho,p)
            while t in pk0:
                t=D(Params.gamma,Params.rho,p)
            pk0.append(t)
        x0=max(pk0)
        pk0.remove(x0)
        if x0%2==0:
            x0=x0+1
    m = x0/p
    if m%2==0:
        m+=1
    else:
        m+=2
    x0=m*p
    pk0=[x0]+pk0
    x=[]
    for i in range (1,Params.gamma+1):
        x.append(D1(Params.gamma,Params.rho,p,i))
    pk=(pk0,x)
    return (sk,pk)
    

def SomeWhatEncrypt(pk,m,p=1):
    #use p for  debugging purpose
    (pk0,x)=pk
    t=Params.tho/32
    l=random.randrange(2,int(Params.tho/128))
    s=0
    pk2=pk0[:]
    for i in range(0,l):
        k=pk2[random.randrange(1,t)]
        #pk2.remove(k)
        #t-=1
        s+=k
        #print m,mods((m+2*s)%pk[0],p)%2
    r = random.randrange(-2**Params.rho1,2**Params.rho1)
    #r = 0
    return (m+2*r+2*s)%pk0[0]

def SomeWhatEvaluate(pk,cl,ck):
    (pk0,x0)=pk
    k=ck(cl)
    x=x0[:]
    while x:
        k=k%x[-1]
        del x[-1]
    return k

def SomeWhatDecrypt(sk,c):
    t = sk/2
    if debug:
        x = int(bigfloat.div(c,sk,bigfloat.precision(1000)))
        y = c/sk
        print "SomeWhatDecrypt:x:",x
        print "SomeWhatDecrypt:y:",y
        print "SomeWhatDecrypt:c%sk:",c%sk
        print "SomeWhatDecrypt:c-x*sk:",c-x*sk
    return (c-(c+t)/sk)%2

def KeyGen(Lambda):
    global globsk #For debugginh
    (sk0,pk0)=SomeWhatKeyGen(Lambda)
    globsk = sk0  #For debugging
    #Params.kappa = int(Params.gamma * Params.eta / Params.rho1)
    
    '''Tweak to approximate to nearest integer'''
    t=sk0/2+1
    xp=int((2**Params.kappa+t)/sk0) # Approximating to nearest integer
    S = []
    lenS=0
    while lenS!=Params.theta:
        i=random.randrange(1,Params.bigo)
        if i not in S:
            S.append(i)
            lenS+=1
    s={}
    for i in range(1,Params.bigo+1):
        if i in S:
            s[i]=1
        else:
            s[i]=0
    
    n = 2**(Params.kappa)      
    m = 2**(Params.kappa+1)
    u = {}
    approx = xp/Params.theta
    var = approx/Params.theta
    for i in range(1,Params.bigo+1):
        u[i]=random.randrange(0,m)
    su=0
    for i in S[:-1]:
        x =random.randrange(approx-var,approx+var)
        u[i]=x
        su+=u[i]
    i=S[-1]
    u[i]=xp-su
    
    y={}
    for i in range(1,Params.bigo+1):
        y[i]=bigfloat.div(u[i],n,bigfloat.precision((Params.kappa+Params.gamma)))
    #DEBUG
    if debug:
        su = 0
        su2=0
        for i in S:
            su2+=u[i]
            su=bigfloat.add(su,y[i],bigfloat.precision(Params.kappa+Params.gamma))
            inv = bigfloat.mul(n,y[i],bigfloat.precision(Params.kappa+Params.gamma))
            print u[i]
            print inv
        print "sumxp=",su2
        print "sumf=",su
        print "xp=", xp
        print "xp/n=", bigfloat.div(xp,n,bigfloat.precision(Params.kappa+Params.gamma))
        print "m=",m
        print Params.theta
        print Params.bigo
        print S
        print s
    #END DEBUG
    (pk1,x)=pk0
    pk = (pk1,x,y)
    return (s,pk)

def Encrypt(pk,m,calcZ=True,s=None):
    #s is the secret key to be used for debugging purposes
    (pk0,x,y)=pk
    c0 = SomeWhatEncrypt((pk0,x), m)
    if calcZ:
        z=[None]*(Params.bigo+1)
        for i in range(1,Params.bigo+1):
            k=bigfloat.mul(c0,y[i],bigfloat.precision((Params.kappa+Params.gamma)))
            z[i]=float(bigfloat.mod(k,2.0,bigfloat.precision(Params.prec)))
            if z[i]>=2.0:
                z[i]=0
        c = (c0,z)
    else:
        c = c0
    if debug:
        su=0
        for i in range(1,Params.bigo+1):
            if s and s[i]==1:
                su=bigfloat.add(su,z[i],bigfloat.precision(Params.kappa+Params.gamma))
        print "Enc_sum%2=",bigfloat.mod(su,8,bigfloat.precision((Params.prec+Params.gamma)))
        q=bigfloat.div(c0,globsk,bigfloat.precision(Params.kappa+Params.gamma))
        print "(Enc_c/sk)%2=",bigfloat.mod(q,8,bigfloat.precision((Params.prec+Params.gamma)))
        print "c0=",c0
    return c

def Evaluate(pk,cl,ck,s={}):
    #S is for debugging
    (pk0,x,y)=pk
    cl0=[]
    for (i,j) in cl:
        cl0.append(i)
    c0 = SomeWhatEvaluate((pk0,x), cl0, ck)
    z=[None]*(Params.bigo+1)
    for i in range(1,Params.bigo+1):
        k=bigfloat.mul(c0,y[i],bigfloat.precision((Params.kappa+Params.gamma)))
        z[i]=float(bigfloat.mod(k,2,bigfloat.precision((Params.prec))))
    if debug:
        su=0
        yo=0
        for i in range(1,Params.bigo+1):
            if s[i]==1:
                yo=bigfloat.add(yo,y[i],bigfloat.precision((Params.kappa+Params.gamma)))
                su=bigfloat.add(su,z[i],bigfloat.precision(Params.kappa+Params.gamma))
        print "Enc_sum%2=",bigfloat.mod(su,8,bigfloat.precision((Params.prec+Params.gamma)))
        q=bigfloat.div(c0,globsk,bigfloat.precision(Params.kappa+Params.gamma))
        print "(c0/sk)=",q
        q=bigfloat.mul(c0,yo,bigfloat.precision((Params.kappa+Params.gamma)))
        print "(c0*yo)=",q
        q=bigfloat.div(1,globsk,bigfloat.precision(Params.kappa+Params.gamma))
        print "(1/sk)=",q
        print "(yo)=",yo
        print "(c0*1/sk)=",bigfloat.mul(q,c0,bigfloat.precision((Params.prec+Params.gamma)))
        q=bigfloat.div(c0,globsk,bigfloat.precision((Params.prec+Params.gamma)))
        print "(c0/sk)=",q
    c = (c0,z)
    return c

def Decrypt(sk,c,calcZ=True,sk1=1):
    #sk1 is for debugging purpose
    su=0
    if calcZ:
        (c0,z) = c
        for i in range(1,Params.bigo+1):
            if sk[i]!=0:
                su=bigfloat.add(su,z[i],bigfloat.precision(Params.prec))
    else:
        c0 = c
        if Keys.PK==None:
            print "Error: Z vector must be provided when public key not available"
            exit()
        y = Keys.PK[2]
        for i in range(1,Params.bigo+1):
            if sk[i]!=0:
                z = bigfloat.mul(c0,y[i],bigfloat.precision(Params.kappa))
                z = float(bigfloat.mod(z,2,bigfloat.precision(Params.prec)))
                su=bigfloat.add(su,z,bigfloat.precision(Params.prec))
    su=int(bigfloat.round(su))
    m = (c0-su) % 2
    return m

def EncryptVector(pk,v,calcZ=True):
    l=v[:]
    c=[]
    while l:
        m = l[0]
        c0 = Encrypt(pk, m, calcZ=calcZ)
        c.append(c0)
        del l[0]
    return c

def DecryptVector(sk,c, calcZ=True):
    l=c[:]
    v=[]
    while l:
        c0 = l[0]
        v0 = Decrypt(sk, c0, calcZ)
        v.append(v0)
        del l[0]
    return v

def EvaluateVector(pk,cl,ck,calcZ=True):
    (pk0,x0,y)=pk
    r=[]
    if calcZ:
        cl0=[]
        for (i,j) in cl:
            cl0.append(i)
    else:
        cl0=cl
    
    ck.setReductionVector(x0)  #This is added to Trees constructor
    r0 = ck.eval(cl0)
    if calcZ:
        for c0 in r0:
            z=[None]*(Params.bigo+1)
            for i in range(1,Params.bigo+1):
                k=bigfloat.mul(c0,y[i],bigfloat.precision(Params.kappa))
                z[i]=float(bigfloat.mod(k,2,bigfloat.precision(Params.prec)))
            c = (c0,z)
            r.append(c)
    else:
        r=r0
    return r

def EncryptKey(sk,pk):
    v=[]
    for i in range(1,Params.bigo+1):
        m = sk[i]
        c=Encrypt(pk, m, calcZ=False)
        #c = sk[i]
        v.append(c)
    return v



def TestSomeWhatCrypt():
    (sk,pk) = SomeWhatKeyGen(Lambda)
    m1=1
    m2=1
    for i in range(0,1000):
        c1=SomeWhatEncrypt(pk, m1)
        c2=SomeWhatEncrypt(pk, m2)
        c=SomeWhatEvaluate(pk,[c1,c2],mul)
        print SomeWhatDecrypt(sk, c)

def Test():
    m1=0
    m2=0
    m3=1
    m4=1
    (sk,pk)=KeyGen(Lambda)
    c1=Encrypt(pk, m1)
    for i in range(0,100):
        
        c2=Encrypt(pk, m2)
        cc1=Encrypt(pk, m3)
        cc2=Encrypt(pk, m4)
        #print c1
        c3=Evaluate(pk,[cc1,cc2],mul,sk)
        c4=Evaluate(pk,[c1,c2],mul,sk)
        c5=Evaluate(pk,[c2,c3],mul,sk)
        c6=Evaluate(pk,[c1,c3],mul,sk)
        c7=Evaluate(pk,[c4,c5],add,sk)
        c=Evaluate(pk,[c7,c6],add,sk)
        #print c
        print Decrypt(sk, c)
        c1 = c



def TestVector():
#     m1=[1,0,0,1,1,0,1,1]
#     m2=[0,1,1,1,0,0,1,0]
    
    m1=[1,0,0,1]
    w1=[0,0,1,0]
    m2=[0,1,1,1]
    w2=[0,0,1,1]
    (sk,pk)=KeyGen(Lambda)
    for i in range(0,1):
        c1=EncryptVector(pk, m1)
        wc1=EncryptVector(pk, w1)
        c2=EncryptVector(pk, m2)
        wc2=EncryptVector(pk, w2)
        #print c1
        t=Tree(Circuits.WEIGHTED_SUM_4, pk)
        c=EvaluateVector(pk,c1+wc1+c2+wc2,t)
        print c
        print DecryptVector(sk, c1)
        print DecryptVector(sk, c2)
        print DecryptVector(sk, c)

def TestHamming():
    m1=[1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,1]
    (sk,pk)=KeyGen(Lambda)
    c1=EncryptVector(pk, m1)
    d = DecryptionCircuit()
    w=d.hammingWeightCircuit(len(m1),3)
    t=Tree(w)
    c2=EvaluateVector(pk, c1, t)
    print DecryptVector(sk, c2)
    
def TestDecryption():
    m1 = 1
    (sk,pk)=KeyGen(Lambda)

    for i in range(0,100):
        esk = EncryptKey(sk, pk)
        c1=Encrypt(pk, m1, sk)
#         sum = 0
#         for i in range(1,Params.bigo+1):
#             if sk[i]==1:
#                 print floatToBin([c1[1][i]],Params.n)
#                 sum+=c1[1][i]
#         print sum


        d = DecryptionCircuit(pk,esk)
        d.setPrivateKey(sk)
#         c2=d.partialRecrypt(c1[0])
#         m2 = DecryptVector(sk, c2)
#         l=len(m2)/2
#         m3=m2[0:l]
#         m4=m2[l:]
#         print m3
#         print m4
#         print bin2float(m3, Params.n+1)
#         print bin2float(m4, Params.n+1)

#         d = DecryptionCircuit(pk,esk)
#         c2=d.partialRecrypt(c1[0])
#         m2 = DecryptVector(sk, c2)
#         print c1[0]%2
#         print bin2float(m2, Params.prec+3)
#         m3 = Decrypt(sk, c1)
#         print "D=",m3


        c2=d.recryptWrapper(c1[0])
        m2 = Decrypt(sk, c2)
        print m2
        
        #print bin2float(m2, 19)

def TestVectorWithBootStrap():
#     m1=[1,0,0,1,0,1,1,0]
#     m2=[0,0,1,1,0,1,0,1]
    m1=[1,0,0,1]
    w1=[0,0,1,1]
    m2=[0,1,1,1]
    w2=[0,0,1,1]
    (sk,pk)=KeyGen(Lambda)
    Keys.PK=pk
    for i in range(0,1):
        c1=EncryptVector(pk, m1, calcZ=False)
        wc1=EncryptVector(pk, w1, calcZ=False)
        c2=EncryptVector(pk, m2, calcZ=False)
        wc2=EncryptVector(pk, w2, calcZ=False)
        #print c1
        esk=EncryptKey(sk, pk)
        d=DecryptionCircuit(pk,esk)
        t=Tree(Circuits.WEIGHTED_SUM_4,pk,d)
        c=EvaluateVector(pk,c1+wc1+c2+wc2,t,calcZ=False)
        print c
        print DecryptVector(sk, c1, calcZ=False)
        print DecryptVector(sk, c2, calcZ=False)
        print DecryptVector(sk, c, calcZ=False)   
    



if __name__=="__main__":  
    import profile
    #profile.run('TestVector()')
    TestVectorWithBootStrap()