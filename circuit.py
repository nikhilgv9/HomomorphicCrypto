from pprint import pprint
from common import *
import fullyHomo
import bigfloat
import copy
import types


class Tree:
    redectionVector=None
    cipherMode=False
    yvector=None
    decrypt=None
    PRINT_MAX_DEPTH = 8
    MAX_MULTS_WO_BS = 2
    MAX_ADDS_WO_BS = 2048
    
    def __init__(self,roots, public_key=None, decrypt=None):
        self.mul_count=self.MAX_MULTS_WO_BS
        self.add_count=self.MAX_ADDS_WO_BS
        self.roots=roots
        self.decrypt = decrypt
        if public_key:
            (pk0,x,y)=public_key
            self.redectionVector = x
            self.yvector = y
    
    def printTrees(self):
        print "Printing Trees"
        for root in self.roots:
            print "Tree..."
            self.printTree(root,0)
    
    def printTreesWithValues(self, sk):
        print "Printing Trees, with values"
        for root in self.roots:
            print "Tree..."
            self.printTreeWithValue(root,sk,0)
    
    def printTreeWithValue(self, node, sk, depth):
        if(node==None):
            print
            return
        if depth!=0:
            for i in range(0,depth-1):
                print "\t",
            print "|\t",
            print "->",node.op,
            print "(",self.quickDecrypt(node.data,sk),")",
        else:
            print node.op,
            print "(",self.quickDecrypt(node.data,sk),")",
        if depth==self.PRINT_MAX_DEPTH:
            print "***"
            return
        else:
            print
        self.printTreeWithValue(node.left,sk,depth+1)
        self.printTreeWithValue(node.right,sk,depth+1)
    
    def quickDecrypt(self, c, sk):
        y0 = self.yvector
        if y0==None:
            # Running in non cipher mode. Decryption not required
            return c
        su=0
        if c==None:
            return -1
        for i in range(1,Params.bigo+1):
            if sk[i]==1:
                su+=(y0[i]*c)%2
        su=int(su+0.5)
        return (c-su)%2
        
    
    def printNthTree(self,n):
        self.printTree(self.roots[n], 0)
        
    def printTree(self,node,depth):
        if(node==None):
            print
            return
        if depth!=0:
            for i in range(0,depth-1):
                print "\t",
            print "|\t",
            print "->",node.op,
        else:
            print node.op,
        if depth==self.PRINT_MAX_DEPTH:
            print "***"
            return
        else:
            print
        self.printTree(node.left,depth+1)
        self.printTree(node.right,depth+1)
        
    def setReductionVector(self,v):
        self.redectionVector=v
        
    def removeReductionVector(self):
        self.redectionVector=None
        
    def clean(self):
        for root in self.roots:
            self.flush(root)
            
    def flush(self,node):
        if node==None:
            return
        if node.data==None:
            return
        node.data=None
        self.flush(node.left)
        self.flush(node.right)
        
    def eval(self, inputs):
        self.mul_count=self.MAX_MULTS_WO_BS
        outputs = []
        self.inputs=inputs[:]
        self.clean()
        for root in self.roots:
            outputs.append(self.dfs(root))
        self.inputs=None
        return outputs
    
    def dfs(self,node):
        if node.data!=None:
            return node.data
        elif node.op=="+":
            d1=self.dfs(node.left)
            d2=self.dfs(node.right)
            k=d1+d2
            if self.redectionVector!=None:
                x=self.redectionVector[:]
                while x:
                    k=k%x[-1]
                    del x[-1]
            if self.decrypt and k!=0:
                self.add_count-=1
                if self.add_count==0:
                    k=self.decrypt.recrypt(k)
                    self.add_count=self.MAX_ADDS_WO_BS
                    
            node.data=k
            return node.data
        
        elif node.op=="*":
            d1=self.dfs(node.left)
            d2=self.dfs(node.right)
            k=d1*d2
            if self.redectionVector!=None:
                x=self.redectionVector[:]
                while x:
                    k=k%x[-1]
                    del x[-1]
            
            if self.decrypt and k!=0:
                self.mul_count-=1
                if self.mul_count==0:
                    k=self.decrypt.recrypt(k)
                    self.mul_count=self.MAX_MULTS_WO_BS
            node.data=k
            return node.data
        elif node.op=="i":
            k=self.inputs[node.i]
#             if self.cipherMode:
#                 k = self.appendZVector(k)
            node.data = k
            return node.data
        else:
            k=node.op
#             if self.cipherMode:
#                 k = self.appendZVector(k)
            node.data = k
            return node.data
            
class DecryptionCircuit:
    Node0=Node(0)
    Node1=Node(1)
    original_sk=None #Used for debugging
    sk=None
    pk=None
    t=None
    yvector=None
    n=Params.n
    
    def __init__(self,public_key=None, encrypted_secret_key=None):
        if public_key!=None:
            self.pk=public_key
            self.yvector=public_key[2]
            self.sk = encrypted_secret_key
            self.n=Params.n
            w = self.decryptionCircuit(Params.bigo, self.n, Params.logtheta)
            self.t=Tree(w,public_key)
                
    
    def recrypt(self, cp):
        c0=copy.deepcopy(cp)
        if self.t==None:
            print "Error: description circuit not formed"
            exit()
        else:
            cipher=self.appendZVector(c0)
            v = self.cipherToVector(cipher)
            vc=[]
            for i in v:
                c=fullyHomo.Encrypt(self.pk, i, calcZ=False)
                vc.append(c)
            inputs = self.sk+vc
            c2=self.t.eval(inputs)
            cipher=c2[0]
#             if isinstance(cipher, list):
#                 print "Error Wrong type"
#                 exit()
            #cipher=self.appendZVector(c2[0])
            return cipher
    def  recryptWrapper(self, cp):
        c=self.recrypt(cp)
        cipher=self.appendZVector(c)
        return cipher
    
    def partialRecrypt(self, cp):
        c0=copy.deepcopy(cp)
        circuit0 = self.sumOfProdCircuit(Params.bigo, self.n)
        circuit1=self.rationalSumCircuit(Params.bigo, self.n, Params.logtheta, circuit0)
        self.t=Tree(circuit1[0]+circuit1[1],self.pk)
        #self.t.printTrees()
        cipher=self.appendZVector(c0)
        v = self.cipherToVector(cipher)
        vc=[]
        for i in v:
            c=fullyHomo.Encrypt(self.pk, i, calcZ=False)
            vc.append(c)
        inputs = self.sk+vc
        c2=self.t.eval(inputs)
        #self.t.printTreesWithValues(self.original_sk)
        cipher=[]
        for i in c2:
            c=self.appendZVector(i)
            cipher.append(c)
        return cipher
    
    def setPrivateKey(self, sk):
        self.original_sk=sk
    
    def cipherToVector(self, c):
        x = c[1][1:]
        y = c[0]%2
        a = floatToBin(x,self.n)
        a.append(y)
        return a;
    
    def appendZVector(self, c0):
        y = self.yvector
        z=[None]*(Params.bigo+1)
        for i in range(1,Params.bigo+1):
            k=bigfloat.mul(c0,y[i],bigfloat.precision(Params.gamma+Params.kappa))
            z[i]=float(bigfloat.mod(k,2,bigfloat.precision(Params.prec)))
            # Sometimes mod goes wrong
            if z[i]>=2.0:
                z[i]=0
        c = (c0,z)
        return c
    
    def hammingWeight(self,s,i=3):
        t=len(s)
        output=[]
        P = [[0 for k in xrange(t+1)] for k in xrange(2**i+1)]
        P[0][0] = 1
        for k in range(1,t+1):
            for j in range(2**i,0,-1):
                P[j][k]=(s[k-1]*P[j-1][k-1]+P[j][k-1])%2
            P[0][k]=1
        j=1
        for k in range (0,i):
            output=[P[j][t]]+output
            j*=2
        pprint(output)
        return output


    def hammingWeightCircuit(self,t,i=3,s=None,fromInput=True):
        if s==None:
            s=range(0,t)
        output=[]
        P = [[self.Node0 for k in xrange(t+1)] for k in xrange(2**i+1)]
        P[0][0] = self.Node1
        for k in range(1,t+1):
            for j in range(2**i,0,-1):
                if fromInput:
                    temp1 = Node("i",i=s[k-1])
                else:
                    temp1=s[k-1]
                temp2 = Node("*",temp1,P[j-1][k-1])
                P[j][k]=Node("+",temp2,P[j][k-1])
            P[0][k]=self.Node1
        j=1
        for k in range (0,i):
            output=[P[j][t]]+output
            j*=2
        return output
    
    def rationalAdd3(self,w1,w2,w3):
        l1=len(w1)
        l2=len(w2)
        l3=len(w3)
        l=max([l1,l2,l3])
        if l1<l:
            w1=[self.Node0 for i in range(0,l-l1)]+w1
        if l2<l:
            w2=[self.Node0 for i in range(0,l-l2)]+w2
        if l3<l:
            w3=[self.Node0 for i in range(0,l-l3)]+w3
        s=[]
        c=[]
        s.append(self.Node0)
        for i in range(0,l):
            sum0 = Node("+",w1[i],w2[i])
            sum1 = Node("+",sum0,w3[i])
            c1 = Node("*",w1[i],w2[i])
            c2 = Node("*",w2[i],w3[i])
            c3 = Node("*",w1[i],w3[i])
            s1 = Node("+",c1,c2)
            carry = Node("+",s1,c3)
            s.append(sum1)
            c.append(carry)
        c.append(self.Node0)
        return [s,c]
    
    # Adds only relevant 3 bits
    def addFromTrees(self,W1,W2):
        l=len(W1)
        index=l-Params.n-1
        w1=W1[index:index+3]
        w2=W2[index:index+3]
        
        n = len(w1)
        l = range(0,n)
        l.reverse()
        carry = None
        outputs = []
        for i in l:
            n1 = w1[i]
            n2 = w2[i]
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
    
    # a0  to a,  Each ai is of size n
    # Theta is number of non zero ai
    
    def getWVectors(self,m,n,theta,w=None):
        tot=m*n
        W=[]
        for i in range(0,n):
            if w!=None:
                s = w[i:tot:n]
                c=self.hammingWeightCircuit(m, theta, s, False)
            else:
                s = range(i,tot,n)
                c=self.hammingWeightCircuit(m, theta, s, True)
            c.extend([self.Node0 for j in range(0,n-i)])
    #         t=Tree(c)
    #         t.printTrees()
            W.append(c)
        return W
    
    def rationalSumCircuit(self,m,n,theta=3,w=None):
        W=self.getWVectors(m, n, theta, w)
        # Recursively performing 3 by 2 additions
        l = n
        while l>2:
            res=self.rationalAdd3(W[0],W[1],W[2])
            W=W+res
    #         t=Tree(res[0])
    #         t.printTrees()
    #         t=Tree(res[1])
    #         t.printTrees()
            W=W[3:]
            l-=1
        if l==2:
            res=self.addFromTrees(W[0], W[1])
            #t=Tree(res)
        else:
            res=W[0]
        return res
    
    def sumOfProdCircuit(self,m,n):
        a=[]
        for i in range(0,m):
            si=Node("i",i=i)
            for j in range(0,n):
                zj=Node("i",i=m+i*n+j)
                p = Node("*",si,zj)
                a.append(p)
        return a
    
    def decryptionCircuit(self,m,n,theta):
        # m is bigo
        # n is prec
        # theta is Theta only :P
        circuit0 = self.sumOfProdCircuit(m, n)
        circuit1=self.rationalSumCircuit(m, n, theta, circuit0)
        # Round Mode and Subtract
        n0 = Node("+",circuit1[0],circuit1[1])
        c0 = Node("i",i=m+m*n) # The input node for last bit of cipher text
        final_circuit = Node("+",n0,c0)
        return [final_circuit]
    
    # INTERNAL METHOD-TESTING PROCEDURES
    def testHammingCircuit(self):
        s=[0,1,1,1,0,1,1,0,1,1]
        w=self.hammingWeightCircuit(10,3)
        t=Tree(w)
        t.setReductionVector([2])
        print t.eval(s)
    
    def test3for2(self,w=None):
        if w==None:
            w=[[1,0,1,0],[1,0,1,0],[0,1,0,1]]
        w1=map(Node,w[0])
        w2=map(Node,w[1])
        w3=map(Node,w[2])
        w=self.rationalAdd3(w1,w2,w3)
        ww=self.addFromTrees(w[0], w[1])
        t=Tree(ww)
        t.setReductionVector([2])
        r = t.eval([])
        print r
        return r
    
    def testWVectors(self):
        x=[0.99,0.12,0.0]
        prec=3
        m=3
        theta=4
        n=int(log2(10**prec)+1.5)
        a = floatToBin(x,n)
        print a
        W=self.getWVectors(m, n, theta)
        for w in W:
            t=Tree(w)
            t.setReductionVector([2])
            b=t.eval(a)
            print b
            print bin2float(b, n+1)
    
    def testRationalSum(self,x=None):
        if x==None:
            x=[0.99,1.12,0.0,0.0,1.1,0.0,0.0,0.0,0.0,0.0,0.1,0.0]
        m=len(x)
        prec=5
        theta=4
        n=int(log2(10**prec)+1.5)
        a = floatToBin(x,n)
        print a
        print len(a)/float(m)
        w=self.rationalSumCircuit(m, n, theta)
        t=Tree(w)
        t.setReductionVector([2])
        b=t.eval(a)
        print bin2float(b, n+1)
    #    t.printTrees()
    
    def testSumOfProds(self,x=None,s=None):
        if x==None:
            x=[0.99,1.12,0.0,0.0,1.1,0.0,0.0,0.0,0.0,0.0,0.1,0.0, 1.99,0.12,0.0,0.0,0.1,0.0,0.0,0.0,0.0,0.0,0.1,0.0]
        m=len(x)
        if s==None:
            s=[1 for i in range(0,m)]
            s[0]=0
        prec=5
        theta=8
        n=int(log2(10**prec)+1.5)
        a = floatToBin(x,n)
        w = s+a
        c = self.sumOfProdCircuit(m, n)
        c1 = self.rationalSumCircuit(m, n, theta, c)
        t = Tree(c1)
        t.setReductionVector([2])
        b=t.eval(w)
        print bin2float(b, n+1)
    
    def testDecryption(self,x=None,s=None):
        if x==None:
            x=[0.99,1.12,0.0,0.0,1.1,0.0,0.0,0.0,0.0,0.0,0.1,0.0]
        m=len(x)
        if s==None:
            s=[1 for i in range(0,m)]
        prec=5
        theta=4
        n=int(log2(10**prec)+1.5)
        a = floatToBin(x,n)
        w = s+a+[0]
        c = self.decryptionCircuit(m, n, theta)
        t = Tree(c)
        t.setReductionVector([2])
        b=t.eval(w)
        print b
        
    @staticmethod
    def selfTest():
        d=DecryptionCircuit()
        s=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        x=[1.3125, 1.5, 0.296875, 0.75, 0.0263671875, 1.5625, 0.84375, 0.21875, 1.3125, 0.5, 1.5625, 0.625, 0.21875, 0.40625, 1.5, 1.75, 0.625, 1.625, 1.9375, 1.6875, 1.625, 1.625, 0.1875, 1.875, 1.5, 0.5625, 1.3125, 1.0625, 0.71875, 0.40625, 1.8125, 0.3125, 0.75, 0.6875, 0.1328125, 0.34375, 0.5, 0.10546875, 0.453125, 1.9375, 1.875, 0.78125, 0.029296875, 1.6875, 0.875, 1.4375, 0.28125, 1.25, 1.75, 0.28125, 1.25, 1.125, 1.875, 1.375, 0.0625, 1.625, 0.5, 1.125, 0.90625, 0.625, 1.6875, 1.0625, 0.09375, 0.11328125, 0.296875, 1.125, 0.75, 1.9375, 1.0, 0.875, 0.1796875, 0.08203125, 0.1640625, 0.359375, 1.375, 1.875, 0.0703125, 1.3125, 0.06640625, 0.140625, 0.9375, 0.2265625, 0.78125, 1.1875, 0.625, 1.75, 0.75, 1.25, 0.6875, 0.5, 1.125, 0.484375, 0, 1.25, 1.25, 0.5625, 1.3125, 1.4375, 0.625, 0.625, 1.9375, 0.59375, 1.6875, 1.6875, 1.6875, 0.59375, 0.125, 1.375, 0.041015625, 0, 0.59375, 1.3125, 1.6875, 0.1640625, 0.9375, 1.625, 0.0625, 1.8125, 0, 1.75, 0.3125, 0.59375, 0.71875, 1.125, 1.8125, 0.25, 1.25, 0.75]
        d.testSumOfProds(x,s)
        #d.testDecryption(x)


class Circuits:
    ADDER_8=adder(8)
    ADDER_4=adder(4)
    MULTIPLIER_4=multiplier(4)
    WEIGHTED_SUM_4=weightedSum(4)
    EQUAL_4=equal(4)
    DECRYPTION=None
    @staticmethod
    def initializeDecryptionCircuit():
        Circuits.DECRYPTION=DecryptionCircuit(Keys.PK,Keys.ESK)

# Testing procedures.........

def testTree():
    t=Tree(adder(8))
    print t.eval([1,0,0,1,1,0,1,1,0,1,1,1,0,0,1,0])



def testFloatBin():
    x=[0.924]
    m=3
    n=int(log2(10**m)+1.5)
    a = floatToBin(x,n)
    print a
    b = bin2float(a, n)
    print b



if __name__=="__main__":
    DecryptionCircuit.selfTest()
    
