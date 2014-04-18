from fullyHomo import *
import timeit


# Wrapper for initialize
def initialize():
    Initialize(Lambda)

# Returns a Triplet of (secret_key, public_key, encrypted_secret key). Each a string.
# Also writes keys to respective files

def getNewKey():
    (sk,pk) = KeyGen(Lambda)
    esk = EncryptKey(sk, pk)
    (ssk,spk) = (str(sk),str(pk))
    spk = cleanKey(spk)
    sesk = str(esk)
    fp = open(Params.SKF,"w")
    fp.write(ssk)
    fp.close()
    
    fp = open(Params.PKF,"w")
    fp.write(spk)
    fp.close()
    
    fp = open(Params.ESKF,"w")
    fp.write(sesk)
    fp.close()
    
    Keys.SK=sk
    Keys.PK=pk
    Keys.ESK=esk
    Circuits.initializeDecryptionCircuit()
    return (ssk,spk,sesk)

def refreshKeyFromFile():
    fp = open(Params.SKF,"r")
    ssk=fp.read().strip()
    fp.close()
    if ssk!=None and ssk!="":
        Keys.SK = ast.literal_eval(ssk)
    else:
        Keys.SK = None
    
    fp = open(Params.PKF,"r")
    spk=fp.read().strip()
    fp.close()
    if spk!=None and spk!="":
        Keys.PK = ast.literal_eval(spk)
        Keys.PK=reprocessKey(Keys.PK)
    else:
        Keys.PK = None
    
    fp = open(Params.ESKF,"r")
    sesk=fp.read().strip()
    fp.close()
    if sesk!=None and sesk!="":
        Keys.ESK = ast.literal_eval(sesk)  
    else:
        Keys.ESK = None
    Circuits.initializeDecryptionCircuit()

# Takes keys in string format. and writes into file
def writeKeyToFile(sk="None",pk="None",esk="None"):
    if sk!="None":
        fp = open(Params.SKF,"w")
        fp.write(sk)
        fp.close()
    
    if pk!="None":
        fp = open(Params.PKF,"w")
        fp.write(pk)
        fp.close()
    
    if esk!="None":
        fp = open(Params.ESKF,"w")
        fp.write(esk)
        fp.close()
    
    Keys.SK=ast.literal_eval(sk)
    Keys.PK=ast.literal_eval(pk)
    Keys.PK=reprocessKey(Keys.PK)
    Keys.ESK=ast.literal_eval(esk)
    Circuits.initializeDecryptionCircuit()

# Takes an integer (string type) and returns the encrypted text (string type)
def getEncryptedText(text):
    p = int(text)
    b=[int(x) for x in bin(p)[2:]]
    c=EncryptVector(Keys.PK, b, calcZ=False)
    cipher=str(c)
    return cipher

def getDecryptedText(cipher):
    c = ast.literal_eval(cipher)
    b = ""
    # We are not using decrypt vector to save time for type conversion from list to string
    for c0 in c:
        m = Decrypt(Keys.SK, c0, calcZ=False)
        b=b+str(m)
    p = int(b,2)
    text = str(p)
    return text

def do4BitMultiplication(cipher1, cipher2):
    c1 = ast.literal_eval(cipher1)
    c1 = [0]*(4-len(c1))+c1[-4:]
    c2 = ast.literal_eval(cipher2)
    c2 = [0]*(4-len(c2))+c2[-4:]
    w = c1+c2
    t=Tree(Circuits.MULTIPLIER_4, Keys.PK, Circuits.DECRYPTION)
    res=EvaluateVector(Keys.PK, w, t, calcZ=False)
    resStr=str(res)
    return resStr

def do8BitAddition(cipher1, cipher2):
    c1 = ast.literal_eval(cipher1)
    c1 = [0]*(8-len(c1))+c1[-8:]
    c2 = ast.literal_eval(cipher2)
    c2 = [0]*(8-len(c2))+c2[-8:]
    w = c1+c2
    t=Tree(Circuits.ADDER_8, Keys.PK, Circuits.DECRYPTION)
    res=EvaluateVector(Keys.PK, w, t, calcZ=False)
    resStr=str(res)
    return resStr

def do4BitAddition(cipher1, cipher2):
    c1 = ast.literal_eval(cipher1)
    c1 = [0]*(4-len(c1))+c1[-4:]
    c2 = ast.literal_eval(cipher2)
    c2 = [0]*(4-len(c2))+c2[-4:]
    w = c1+c2
    t=Tree(Circuits.ADDER_4, Keys.PK, Circuits.DECRYPTION)
    res=EvaluateVector(Keys.PK, w, t, calcZ=False)
    resStr=str(res)
    return resStr

def do4BitWeightedSum(cipher1, weight1, cipher2, weight2):
    c1 = ast.literal_eval(cipher1)
    c1 = [0]*(4-len(c1))+c1[-4:]
    wc1= ast.literal_eval(weight1)
    wc1 = [0]*(4-len(wc1))+wc1[-4:]
    c2 = ast.literal_eval(cipher2)
    c2 = [0]*(4-len(c2))+c2[-4:]
    wc2 = ast.literal_eval(weight2)
    wc2 = [0]*(4-len(wc2))+wc2[-4:]
    
    w = c1+wc1+c2+wc2
    t=Tree(Circuits.WEIGHTED_SUM_4, Keys.PK, Circuits.DECRYPTION)
    res=EvaluateVector(Keys.PK, w, t, calcZ=False)
    resStr=str(res)
    return resStr

def doNBitBinaryOp(cipher1, cipher2, circuit, n):
    c1 = ast.literal_eval(cipher1)
    c1 = [0]*(n-len(c1))+c1[-n:]
    c2 = ast.literal_eval(cipher2)
    c2 = [0]*(n-len(c2))+c2[-n:]
    
    w = c1+c2
    t=Tree(circuit, Keys.PK, Circuits.DECRYPTION)
    res=EvaluateVector(Keys.PK, w, t, calcZ=False)
    resStr=str(res)
    return resStr

def do4BitIsEqual(cipher1, cipher2):
    pass

def selfTest():
    # Student Mark and Weights
    p1="9"
    w1="2"
    p2="7"
    w2="3"
    
    #Create Key
    initialize()
    (sk,pk,esk)=getNewKey()
    print "Got Key"
    print "SK", sk[:10],"..."
    print "len(PK),PK[0]=", len(pk), pk[0:100], "..."
    print "ESK[0]",esk[0:100], "..."
    
    
    #
    '''Now we have to send keys to Server. For this moment lets assume we
     got keys. The following line is not necessary if we are going to perform eval
      on client. since we this is a test, the following two function calls are placed'''
    writeKeyToFile(sk,pk,esk)
    print "Wrote key to file"''
    
    #
    '''Refresh keys from file. Have to Do it when application wakes up and dont 
    want to change the key. No need to do this now. But just to test'''
    refreshKeyFromFile()
    print "Refreshed key from file"
    
    
    #
    print p1
    print p2
    c1 = getEncryptedText(p1)
    c2 = getEncryptedText(p2)
    wc1 = getEncryptedText(w1)
    wc2 = getEncryptedText(w2)
    #res = do4BitWeightedSum(c1, wc1, c2, wc2)
    res = do8BitAddition(c1, c2)
    #res=do4BitMultiplication(c1,c2)
    resText = getDecryptedText(res)
    print "Result=",resText

_c1,_c2,_circuit,_i = 0,0,0,0
def timeTest():
    global _c1,_c2,_circuit,_i
    initialize()
    (sk,pk,esk)=getNewKey()
    P1=["7","12","30","55","120","250","500","999"]
    P2=["6","10","28","50","110","220","470","879"]
    for _i in range(3,11):
        p1=P1[_i-3]
        p2=P2[_i-3]
        _c1 = getEncryptedText(p1)
        _c2 = getEncryptedText(p2)
        _circuit = weightedSum(_i)
        #doNBitBinaryOp(c1, c2, circuit, i)
        time = timeit.timeit('__main__.do4BitWeightedSum(__main__._c1, __main__._c2,__main__._c1, __main__._c2)', setup="import __main__ ", number=1)
        print _i,"bit weighted sum &",time,"\\\\"
    for _i in range(3,11):
        p1=P1[_i-3]
        p2=P2[_i-3]
        _c1 = getEncryptedText(p1)
        _c2 = getEncryptedText(p2)
        _circuit = adder(_i)
        #doNBitBinaryOp(c1, c2, circuit, i)
        time = timeit.timeit('__main__.doNBitBinaryOp(__main__._c1, __main__._c2, __main__._circuit, __main__._i)', setup="import __main__ ", number=1)
        print _i,"bit addition &",time,"\\\\"
        
    for _i in range(3,11):
        p1=P1[_i-3]
        p2=P2[_i-3]
        _c1 = getEncryptedText(p1)
        _c2 = getEncryptedText(p2)
        _circuit = multiplier(_i)
        #doNBitBinaryOp(c1, c2, circuit, i)
        time = timeit.timeit('__main__.doNBitBinaryOp(__main__._c1, __main__._c2, __main__._circuit, __main__._i)', setup="import __main__ ", number=1)
        print _i,"bit multiplication &",time,"\\\\"
    
if __name__=="__main__":
    timeTest()