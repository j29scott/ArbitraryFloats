import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

from math import ceil,floor,log2

class BV:
    def __init__(self,lit,length=-1):
        self.val = []
        self.sign = False
        assert isinstance(length,int), "Length Argument needs to be an integer."
        assert isinstance(lit,str) or (isinstance(lit,int) and lit >= 0) or isinstance(lit,list) , "BV literal needs to be either a positive integer, a string of 0s and 1s, or a boolean array"
#		assert (not isinstance(lit,int) or length >= 0) , "BV int literal needs specified length"
        if(isinstance(lit,str) or isinstance(lit,list)):
            length = max(length, len(lit))
        elif isinstance(lit,int) and length == -1:
            if lit != 0:
                logval = log2(float(lit))
                length = ceil(log2(float(lit)))
                if ceil(logval) == floor(logval):
                    length += 1
            else:
                length = 0
        self.n = length
        for i in range(length):
            self.val.append(False)
        if isinstance(lit,str):
            for i in range(length):
                assert lit[-i-1] == '0' or lit[-i-1] == '1', "Str Characters need to be either 0 or 1"
                if lit[-i-1] == '0':
                    self.val[-i-1] = False
                else:
                    self.val[-i-1] = True
        elif isinstance(lit,list):
            for i in range(self.n):
                assert isinstance(lit[i],bool), "BV requires array of booleans"
                self.val[i] = lit[i]
        else: ##lit == int
            it = 0
            while lit > 0 and it < length:
                self.val[-1-it] = lit % 2 == 1
                lit = int(lit/2)
                it+=1
    

    def AddFront(self,n=1,v=False):
        newVal = []
        for i in range(n):
            newVal.append(v)
        newVal.extend(self.val[:])
        self.val = newVal
        self.n += n
                
    def AddEnd(self,n=1,v=False):
        for i in range(n):
            self.val.append(v)
        self.n += n
    
    def __getitem__(self, i):
        return self.val[i]
    def __setitem__(self, key, value):
        self.val[key] = value
    def __len__(self):
        return self.n
    def __int__(self):
        ret = 0
        for i in range(len(self.val)):
            if(self.val[-i-1]):
                ret += 2**i
        return ret
    def __str__(self):
        bvstr = ""
        for i in range(self.n):
            c = " "
            if(self.val[i] == True):
                c = "1"
            else:
                c = "0"
            bvstr = bvstr + c
    
        return bvstr + " (" + str(int(self)) + ")"
    def __add__(self,other):
        ret = []
        for i in range(len(self.val)):
            ret.append(False)
        c = False
        for i in range(len(self.val)):
            a = self.val[-i-1]
            b = False
            if(i < len(other.val)):
                b = other.val[-i-1]

            aXORb = (a or b) and not(a and b)
            ret[-i-1] = (aXORb or c) and not(aXORb and c)
            
            c = (a and b) or (c and aXORb)
        retBV = BV(0,len(self.val))
        retBV.val = ret
        #print(ret)
        return retBV
    def __mul__(self,other):
        multTable = []
        n = max(len(self.val),len(other.val))
        initRow = []
        for i in range(2*n):
            initRow.append(False)

        for i in range(len(other.val)):
            row = initRow[:]
            if(other.val[-i-1]):
                for j in range(len(self.val)):
                    row[-1-j-i] = self.val[-j-1]
            #print(row)
            multTable.append(row[:])
        valRet = []
        
        for i in range(len(self.val)):
            valRet.append(False)
        
        if(len(multTable) == 0):
            return BV(0,0)

        carry = 0
        for i in range(len(valRet)):
            V = 0
            for j in range(len(multTable)):
                if(multTable[j][-i-1]):
                    V += 1
            V += carry
            valRet[-i-1] = (V % 2) == 1
            carry = int(V / 2)
        ret = BV(0,len(self.val))
        ret.val = valRet
        return ret
    def __lshift__(self,other):
        ret = []
        for i in range(self.n):
            ret.append(False)
        for i in range(self.n - other):
            ret[i] = self.val[i + other]
        retBV = BV(0,self.n)
        retBV.val = ret
        return retBV
    def __rshift__(self,other):
    
        ret = []
        for i in range(self.n):
            ret.append(False)
        for i in range(self.n - other):
            ret[i + other] = self.val[i]
        retBV = BV(0,self.n)
        retBV.val = ret
        return retBV
    def Signed(self):
        self.sign = True
    def UnSign(self):
        self.sign = False
    def pop(self):
        if(self.n!=0):
            self.n-=1
            return self.val.pop()
        return None
        
    def __eq__(self,other):
        if isinstance(other, (str, int)):
            other = BV(other)
        assert isinstance(other, BV) , "comparison type error"
        if len(self) == len(other):
            for i in range(self.n):
                if self[i] != other[i]:
                    return False
            return True
        return False
        
    def __neq__(self,other):
        return not self == other
    

# Functions

def BVConcat(bv1, bv2):
    
    ret = BV("")
    
    ret.val = bv1.val[:]
    ret.val.extend(bv2.val[:])
    ret.length = len(ret.val)
    
    return ret

def BVTwosCompliment(bv):
    assert isinstance(bv,BV), "BV required to take 2's compliment"
    ret = bv
    if bv.sign == False:
        return ret
    if len(bv) == 0:
        assert False, "Nonsense Two's Compliment attempt"
    for i in range(bv.n):
        bv.val[i] = not bv.val[i]
    return ret + BV("1")