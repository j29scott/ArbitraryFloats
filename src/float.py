
class Float():
    def __init__(self,val=None,ne=None,ns=None,width=None):
        self.ne = ne
        self.ns = ns
        self.width = width

        if self.ne == None and self.ns == None:
            assert self.width != None, "Must specify a width!"
            if self.width < 3:
                assert self.width != None, "Not enough Width!"
            elif width < 16:
                if width % 2 == 0:
                    self.ns = self.ne = self.width//2
                else:
                    self.ne = self.width //2
                    self.ns == self.ne + 1
            else:
                self.ns = round((self.width - 5.1)/1.092)
                self.ne = self.width - self.ns

        self.ebv = None
        self.sbv = None
        if val != None:
            self.val(val)
    
    def val(self,val):
        assert isinstance(val,str)
        val = val.split()
        assert len(val) == 1 or len(val) == 2
        pass


    def __eq__(self,val):
        print(val)

    def __float__(self):
        mant = 0.0
        subnormal = 1
        if(int(self.ebv) != 0):
            mant += 1.0
            subnormal = 0
        for i in range(self.nS):
            if self.sbv[i]:
                mant += 2 ** (-(i+1))
        
        ret =  mant *  2 **(int(self.ebv)-self.bias + subnormal)
        if(self.sign):
            ret = -ret
        return ret
    
    def __str__(self):
        bvstr = ""
        if self.sign:
            bvstr = "1 "
        else:
            bvstr = "0 "
        for i in range(self.nE):
            if self.ebv[i]:
                bvstr = bvstr + "1"
            else:
                bvstr = bvstr + "0"
        bvstr = bvstr + " "
        for i in range(self.nS):
            if self.sbv[i]: 
                bvstr = bvstr + "1"
            else:
                bvstr = bvstr + "0"	
        name = ""
        if FIsNan(self):
            name = "NaN"
        if FIsInf(self):
            name = "Inf"
            if self.sign:
                name = "-" + name
            else:
                name = "+" + name
        if name == "":
            name = str(float(self))
        return bvstr + " (" + name + ")"
        
    def __lt__(self,other):
        return FLT(self,other)
        
    def __gt__(self,other):
        return FGT(self,other)
        
    def __leq__(self,other):
        return FLEQ(self,other)
    
    def __geq__(self,other):
        return FGEQ(self,other)

    def __add__(self,other):
        return FAdd(self,other, None)
    def __sub__(self,other):
        return FAdd(self,FNeg(other), None)
    def __mul__(self,other):
        return FMul(self,other,None)
    def __eq__(self,other):
        return FEq(self,other)

def FIsNan(flt):
    expAnd = True
    sigOr = False
    for i in range(flt.nE):
        expAnd = expAnd and flt.ebv[i]
    for i in range(flt.nS):
        sigOr = sigOr or flt.sbv[i]
    return expAnd and sigOr

def FIsInf(flt):
    expAnd = True
    sigOr = False
    for i in range(flt.nE):
        expAnd = expAnd and flt.ebv[i]
    for i in range(flt.nS):
        sigOr = sigOr or flt.sbv[i]
    return expAnd and not sigOr

def FIsZero(flt):
    return int(flt.ebv) == 0 and int(flt.sbv) == 0

def FRound(sign, exp, mantisa, nE, nS, roundBit,stickyBit, roundingMode = None):
    assert isinstance(sign, bool) , "First Argument [sign] is of bool type."
    assert isinstance(exp,int), "Second Argument [exp] is of int type."
    assert isinstance(mantisa,BV), "Third Argument [mantisa] is of the BV type"
    assert isinstance(nE, int) , "Fourth Argument [nE] is of int type."
    assert isinstance(nS,int), "Fifth Argument [nS] is of int type."
    assert isinstance(roundBit,bool), "Sixth Argument [roundBit] is of the bool type"
    assert isinstance(stickyBit,bool), "Sixth Argument [stickyBit] is of the bool type"
    
    assert len(mantisa) == nS, "Correct Precision of Arguments"
    assert len(mantisa) > 0 and mantisa[0] == True, "Leading 1 in Mantisa."
    
    bias = 2**(nE-1)-1
    eMin = -bias + 1
    eMax = 2**nE -1 - bias - 1
    
    ##OVERFLOW HANDLE
    if exp > eMax:
        manAnd = True
        for i in range(nS):
            manAnd = manAnd and mantisa[i]
        if manAnd and (roundBit or stickyBit):
            if sign:
                return Float("-inf")
            else:
                return Float("+inf")
    if exp == eMax:
        manAnd = True
        for i in range(nS):
            manAnd = manAnd and mantisa[i]
        
        if roundingMode == RoundingMode.RNE or roundingMode == RoundingMode.RNA:
            if manAnd and roundBit:
                if sign:
                    return Float("-inf")
                else:
                    return Float("+inf")
            
        elif roundingMode == RoundingMode.RU:
            if manAnd and (roundBit or stickyBit):
                if sign:
                    return Float("-inf")
                else:
                    return Float("+inf")
    
    ##SUBNORMAL HANDLE
    #This is a lazy implimentation... if a problem fix it.
    
    if exp < eMin:
        shiftLen = eMin - exp
        for i in range(min(shiftLen,nS+5)):
            stickyBit = stickyBit or roundBit
            roundBit = mantisa[-1]
            mantisa = mantisa >> 1
        exp = eMin - 1
            
    pred = Float([sign,exp,BV.BV(mantisa[1:])],nE,nS)
    
    if(not roundBit and not stickyBit):
        return pred
    
    bvExpManConCatPlusOne = BV.BV("")
    if exp != eMin - 1:
        bvExpManConCatPlusOne = BV.BVConcat(BV.BV(exp + bias,nE), BV.BV(mantisa.val[1:])) + BV.BV("1")
    else:
        bvExpManConCatPlusOne = BV.BVConcat(BV.BV(0,nE), BV.BV(mantisa.val[1:])) + BV.BV("1")
    
    
    
    
    
    succ_ebv = BV.BV(0,nE)
    succ_sbv = BV.BV(0,nS-1)
    it = 0
    for i in range(nE):
        succ_ebv[i] = bvExpManConCatPlusOne[it]
        it+=1
    for i in range(nS-1):
        succ_sbv[i] = bvExpManConCatPlusOne[it]
        it+=1
    succ = Float([sign,succ_ebv,succ_sbv])

#		if(sign):
#			succ,pred = pred,succ
        
    if roundingMode == RoundingMode.RZ:
        return pred
        
    if not roundBit and not stickyBit:
        return pred
    elif not roundBit and stickyBit:
        if roundingMode == RoundingMode.RU:
            return succ
        else: 
            return pred
    elif roundBit and not stickyBit:
        if roundingMode == RoundingMode.RD:
            return pred
        elif roundingMode == RoundingMode.RU:
            return succ
        ##RZ already taken care of 
        else: # RN
            if roundingMode == RoundingMode.RNE:
                predEven = pred.sbv[-1] == 0
                if predEven:
                    return pred
                else:
                    return succ
            else: #RNA
                if sign:
                    return pred
                else:
                    return succ
    else: ##Round bit and sticky bit
        if roundingMode == RoundingMode.RD:
            return pred
        else:
            return succ
    
                    
def FAdd(x,y, roundingMode = None):
    assert isinstance (x,Float) and isinstance(y,Float), "Non Float instance"
    assert x.nS == y.nS and x.nE == y.nE, "different precision addition not ready yet."
    
    xe = x.eval
    ye = y.eval
    
    if(int(x.ebv) == 0):
        xe = x.eMin
    if(int(y.ebv) == 0):
        ye = y.eMin
    
    if not (xe >= ye):
        x,y = y,x
    roundBit = False
    stickyBit = False
    alignDist = xe - ye
    
    xMant = BV.BV(x.sbv[:])
    yMant = BV.BV(y.sbv[:])

    #Add Leading 1
    if int(x.ebv) == 0:
        xMant.AddFront(1)
    else:
        xMant.AddFront(1,True)
    
    if int(y.ebv) == 0:
        yMant.AddFront(1)
    else:
        yMant.AddFront(1,True)
    

    
    
    xMant.AddEnd(alignDist)
    yMant.AddFront(alignDist)
    
    
    signZ = (x.sign and not y.sign) or (not x.sign and  y.sign)
    
    result = BV.BV(0)
    rSign = False
    rExp = xe
    if signZ:
        yMant.Signed()
        yMant = BV.BVTwosCompliment(yMant)
        
        #Add sign bit
        xMant.AddFront(1,False)
        yMant.AddFront(1,True)	
        
        result = xMant + yMant
        if(result[0] == True):
            result = BV.BVTwosCompliment(BV.BV(result.val[1:]))
            rSign = True
        else:
            result = BV.BV(result[1:])
        it = 0
        while result[0] != True and it < x.nS+5:
            result = result << 1
            rExp -= 1
            it += 1
        
    else:
        #Add Carry bit
        xMant.AddFront(1)
        yMant.AddFront(1)		
        result = xMant + yMant
        if(result[0] == True):
            roundBit = result[-1]
            result = result >> 1
            rExp +=1
        result = BV.BV(result[1:])
        

    assert len(result) >= x.nS+1, "Something in Addition went horribly wrong."
    
    while len(result) > x.nS+1:
        stickyBit = stickyBit or roundBit
        roundBit = result.pop()
    return FRound((not x.sign and rSign) or (x.sign and not rSign) , rExp, result,x.nE,x.nS+1,roundBit,stickyBit,roundingMode)
    
def FNeg(float):
    x = copy.deepcopy(float)
    x.sign = not x.sign
    return x

def FIsSubnormal(flt):
    return int(flt.ebv) == 0 and int(flt.sbv) != 0


def FMakeZero(sign,nE,nS):
    return Float([sign,BV.BV(0,nE), BV.BV(0,nS-1)],nE,nS)

def FMakeInf(sign,nE,nS):
    ret = Float(0.0,nE,nS)
    ret.sign = sign
    for i in range(len(ret.ebv)):
        ret.ebv[i] = True
    for i in range(len(ret.sbv)):
        ret.sbv[i] = False
    return ret
    
def FMakeNan(nE,nS):
    ret = Float(0.0,nE,nS)
    ret.sign = False
    for i in range(len(ret.ebv)):
        ret.ebv[i] = True
    for i in range(len(ret.sbv)):
        ret.sbv[i] = True
    return ret


def FMul(x,y,roundingMode = None):
    
    rSign = (not x.sign and  y.sign) or (x.sign and not y.sign)
    
    if FIsZero(x) or FIsZero(y):
        return FMakeZero(rSign,x.nE, x.nS+1)
        
    if (FIsZero(x) and FIsInf(y)) or (FIsZero(y) and FIsInf(x)):
        return FMakeNan(x.nE,x.nS+1)
        
    if FIsInf(x) or FIsInf(y):
        return FMakeInf(rSign,x.nE,x.nS+1)
    
    
    
    xMant = BV.BV(x.sbv[:])
    yMant = BV.BV(y.sbv[:])
            
    
    
    ex = x.eval
    ey = y.eval
    if(FIsSubnormal(x)):
        while not xMant[0]: # we know X is not zero from earlier checks.
            ex-=1
            xMant = xMant<<1
        xMant.AddEnd(1,False) # add 1 to keep length.
    else:
        xMant.AddFront(1,True)
    if(FIsSubnormal(y)):
        while not yMant[0]:
            ey-=1
            yMant = yMant<<1
        yMant.AddEnd(1,False)	

    else:
        yMant.AddFront(1,True)
    
    
    #Add extra length
    xMant.AddFront(x.nS + 5)
    yMant.AddFront(x.nS + 5)
    
    rExp = ex + ey
    

    roundBit = False
    stickyBit = False
    
    assert len(xMant) == len(yMant), "Yikes"
    result = xMant * yMant
    
    #Truncate so it has leading 1
    gamma = 0
    for i in range(len(result)):
        if result[i]:
            gamma = i
            break
    result = BV.BV(result[gamma:])
    assert len(result) == 2*(x.nS+1)-1 or len(result) == 2*(x.nS+1)
    
    if len(result) == 2*(x.nS+1):
        rExp += 1
        stickyBit = result[-1]
        result = result >> 1
        result = BV.BV(result[1:])
    
    roundBit = result[1+x.nS+1]
    for i in range(1+x.nS+1+1,len(result)):
        stickyBit = stickyBit or result[i]
    
    assert len(result) >= x.nS+1, "Something in Mult went horribly wrong."
    
    while len(result) > x.nS+1:
        stickyBit = stickyBit or roundBit
        roundBit = result.pop()
    return FRound(rSign , rExp, result,x.nE,x.nS+1,roundBit,stickyBit,roundingMode)


def FEq(x,y):
    if FIsNan(x) or FIsNan(y):
        return False
    if FIsZero(x) and FIsZero(y):
        return True
    if FIsInf(x) or FIsInf(y):
        return False
    return x.sign == y.sign and x.sbv == y.sbv and x.ebv == y.ebv

def FIsPositive(x):
    return x.sign == False

def FIsNegative(x):
    return x.sign == True

def FSqrt(x,roundingMode = None):
    if FIsZero(x):
        return FMakeZero(x.sign,x.nE,x.nS)
    if FIsNan(x) or FIsNegative(x):
        return FMakeNan(x.nE, x.nS)
    gamma = 0
    xMant = BV.BV(x.sbv[:])
    if FIsSubnormal(x):
        gamma += 1
        for bit in x.sbv:
            if bit:
                break
            else:
                gamma += 1

        xMant.AddFront(1,False)
        while not xMant[0]:
            xMant = xMant << 1
    else:
        xMant = x.sbv
        xMant.AddFront(1,True)
    c = 0
    if BV.BV(abs(x.eval))[-1]:
        c=1
    d = int((x.eval - gamma)/2)
    result = BV.BV([True])
    p = x.nS + 1
    Q = 2 ** (p)
    R = 2 ** (p+c) - 2**p
    for i in range(1,p+1):
        T = 2*R - (2*Q + 2**(p-i))
        if T < 0:
            R = 2*R
            result.AddEnd(1,False)
        else:
            Q = Q + 2 **(p-i)
            R = T
            result.AddEnd(1,True)
    roundBit = result.pop()
    stickyBit = roundBit
    return FRound(False,d,result,x.nE,x.nS+1,roundBit,stickyBit,roundingMode)
    
def FAbs(x):
    ret = copy.deepcopy(x)
    ret.sign = False
    return ret

def FLT(x,y):
    if x.sign != y.sign:
        if FIsZero(x) and FIsZero(y):
            return False
        if x.sign:
            return True
        else:
            return False
    
    xBvExpManConCat =  BV.BVConcat(x.ebv, x.sbv)
    yBvExpManConCat =  BV.BVConcat(y.ebv,y.sbv)
    return (int(xBvExpManConCat) < int(yBvExpManConCat)) == (x.sign == False)
    
def FLEQ(x,y):
    return FEq(x,y) or FLT(x,y)
def FGT(x,y):
    return not FLT(x,y)
def FGEQ(x,y):
    return FEq(x,y) or FGT(x,y)