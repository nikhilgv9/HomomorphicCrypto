import math
import re
import bigfloat

#Definition of Globals

#Globals
"""
These are not the actual values of the parameters. They are set by the security parameter Lambda
"""
# Definition of common classes
class Params:
    #Somewhat homomorphism parameters. The actual values are set in keygen method
    rho=0
    rho1=0
    eta=0
    gamma=0
    tho=0
    n = 0
    
    #Fully homomorphism parameter. The actual values are set in keygen method
    kappa=0
    theta=0
    bigo=0
    prec=0
    logtheta=0
    
    # Key files
    PKF="publickey.txt"
    SKF="privatekey.txt"
    ESKF="encprivatekey.txt"

class Keys:
    PK=None
    SK=None
    ESK=None

class Node:
    def __init__(self, op, left=None, right=None, i=-1 ):
        self.left = left
        self.right = right
        self.data = None
        self.op=op
        self.i = i
        if (op=="+" or op=="-") and (left==None or right==None):
            print "Left or Right Missing"
            exit()

# Definition of common functions
def log2(x):
    return math.log(x,2)

def mods(x,y):
    z=(x%y)
    if z>int(y/2):
        return z-y
    else:
        return z

def add(l):
    return l[0]+l[1]

def mul(l):
    return l[0]*l[1]

def adder(n,w=None):
    l = range(0,n)
    l.reverse()
    carry = None
    outputs = []
    for i in l:
        if w:
            n1 = w[i]
            n2 = w[i+n]
        else:
            n1 = Node("i",i=i)
            n2 = Node("i",i=i+n)
        sum0 = Node("+",n1,n2)
        if carry!=None:
            sum1 = Node("+",sum0,carry)
            c1 = Node("*",n1,n2)
            c2 = Node("*",n1,carry)
            c3 = Node("*",n2,carry)
            s1 = Node("+",c1,c2)
            carry = Node("+",s1,c3)
        else:
            sum1=sum0
            carry = Node("*",n1,n2)
        outputs = [sum1] + outputs
    return outputs

def multiplier(n, w=None):
    Node0=Node(0)
    i = 0
    if w:
        n1 = w[n+i]
    else:
        n1 = Node("i",i=n+i)
    n2Nodes=[]
    W0 = [Node0 for k in range(0,i+1)]
    for j in range(0,n):
        if w:
            n2 = w[j]
        else:
            n2 = Node("i",i=j)
            n2Nodes.append(n2)
        prod = Node("*",n1,n2)
        W0.append(prod)
    W0.extend([Node0 for k in range(0,n-i-1)])
    for i in range(1,n):
        if w:
            n1 = w[n+i]
        else:
            n1 = Node("i",i=n+i)
        W = [Node0 for k in range(0,i+1)]
        for j in range(0,n):
            if w:
                n2 = w[j]
            else:
                n2 = n2Nodes[j]
            prod = Node("*",n1,n2)
            W.append(prod)
        W.extend([Node0 for k in range(0,n-i-1)])
        W0 = adder(2*n,W0+W)
    return W0

def equal(n):
    w=[]
    Node1=Node(1)
    for i in range(0,n):
        n1=Node("i",i=i)
        n2=Node("i",i=n+i)
        n3=Node("+",n1,n2)
        neg=Node("+",n3,Node1)
        w.append(neg)
    res = w[0]
    for i in range(1,n):
        res=Node("*",res,w[i])
    return [res]
 
def weightedSum(n):
    w = []
    for i in range(0,4*n):
        w.append(Node("i",i=i))
    p1 = multiplier(n, w[:2*n])
    p2 = multiplier(n, w[2*n:])
    res = adder(2*n,p1+p2)
    return res

def floatToBin(f,n):
    o=[]
    for i in f:
        i1=int(i*(2**(n-1))+0.5) #0.5 to round up
        b=[int(x) for x in bin(i1)[2:]]
        diff=n-len(b)
        if diff<0:
            print "error"
            exit()
        if diff>0:
            o.extend([0 for i in range(0,diff)])
        o.extend(b)
    return o

def cleanKey(pk):
    pk = re.sub("BigFloat.exact\(","",pk)
    pk = re.sub(", precision=[0-9]+\)","",pk)
    return pk

def reprocessKey(pk):
    (pk0,x0,y0)=pk
    y={}
    for i in range(1,Params.bigo+1):
        k = bigfloat.BigFloat(y0[i],bigfloat.precision(Params.kappa))
        y[i] = k
    pk=(pk0,x0,y)
    return pk  

def bin2float(b,n):
    s=''.join(map(str,b))
    i = int(s,2)
    f = i/float(2**(n-1))
    return f
