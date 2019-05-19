import z3
import pdb
import copy

rnd = z3.RoundNearestTiesToEven()


class fp:
    def __init__(self,val=None,width=None,ne=None,ns=None):
        self.width = width
        self.ne = ne
        self.ns = ns
        self.z3_ds = None
        if isinstance(val,str):
            self.from_real(val)
        elif isinstance(val,Float):
            self.__dict__ = copy.deepcopy(val.__dict__)
        elif isinstance(val,z3.z3.FPNumRef):
            self.z3_ds = copy.deepcopy(val)
        else:
            assert False, "Unknown type: " + str(type(val))

    def from_real(self,val):
        assert isinstance(val,str)
        if val.lower() == '+inf':
            self._mk_pinf()
        elif val.lower() == '-inf':
            self._mk_ninf()
        elif val.lower() == 'nan':
            self._mk_nan()
        else:
            self.z3_ds = z3.FPVal(val,z3.FPSort(self.ne,self.ns))

    def __abs__(self):
        return Float(val=z3.simplify(z3.fpAbs(self.z3_ds)),ne=self.ne,ns=self.ns)

    def __neg__(self):
        return Float(val=z3.simplify(z3.fpNeg(self.z3_ds)),ne=self.ne,ns=self.ns)

    def __add__(self,other):
        assert isinstance(other,Float) and other.ne == self.ne and other.ns == self.ns
        return Float(val=z3.simplify(z3.fpAdd(rnd, self.z3_ds, other.z3_ds)),ne=self.ne,ns=self.ns)

    def __sub__(self,other):
        assert isinstance(other,Float) and other.ne == self.ne and other.ns == self.ns
        return Float(val=z3.simplify(z3.fpSub(rnd, self.z3_ds, other.z3_ds)),ne=self.ne,ns=self.ns)

    def __mul__(self,other):
        assert isinstance(other,Float) and other.ne == self.ne and other.ns == self.ns
        return Float(val=z3.simplify(z3.fpMul(rnd, self.z3_ds, other.z3_ds)),ne=self.ne,ns=self.ns)

    def __div__(self,other):
        assert isinstance(other,Float) and other.ne == self.ne and other.ns == self.ns
        return Float(val=z3.simplify(z3.fpDiv(rnd, self.z3_ds, other.z3_ds)),ne=self.ne,ns=self.ns)


    def get_succ(self):
        if self.is_pinf():
            return copy.deepcopy(self)
        if self.is_nzero():
            return Float('+0',ne=self.ne,ns=self.ns).get_succ()
        bv_str = self.get_bv_str()
        #print(bv_str)
        sign = bv_str[0]
        if sign == '0':
            succ = int(bv_str[1:],2) + 1
            return Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(succ),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns)

        else:
            succ = int(bv_str[1:],2) - 1
            return -Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(succ),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns)



    def get_pred(self):
        if self.is_ninf():
            return copy.deepcopy(self)
        if self.is_pzero():
            return Float('-0',ne=self.ne,ns=self.ns).get_pred()
        bv_str = self.get_bv_str()
        #print(bv_str)
        sign = bv_str[0]
        if sign == '0':
            succ = int(bv_str[1:],2) - 1
            return Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(succ),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns)

        else:
            succ = int(bv_str[1:],2) + 1
            return -Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(succ),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns)






    def get_bv_str(self):
        bv_str = bin(int(str(z3.simplify(z3.fpToIEEEBV(self.z3_ds)))))
        assert bv_str[0:2] == '0b', bv_str[0:2] + ' vs ' + '0b'
        bv_str = bv_str[2:]
        while len(bv_str) < self.ne + self.ns:
            bv_str = '0' + bv_str
        return bv_str
    
    def is_nan(self):
        bv_str = self.get_bv_str()[1:] #ignore sign bit
        ret = True
        for i in range(self.ne): #all exp = 1
            if bv_str[i] != '1':
                ret = False
                break
        if not ret:
            return ret
        ret = False
        for i in range(self.ne,len(bv_str)): #mantisa contains at least one 1
            if bv_str[i] == '1':
                ret = True
                break
        return ret
    
    def is_inf(self):
        #true if +inf, -inf
        #else false
        bv_str = self.get_bv_str()[1:] #ignore sign bit
        ret = True
        for i in range(self.ne): #all exp = 1
            if bv_str[i] != '1':
                ret = False
                break
        if not ret:
            return ret
        ret = True
        for i in range(self.ne,len(bv_str)): #all sign = 0
            if bv_str[i] == '1':
                ret = False
                break
        return ret

    def is_zero(self):
        ret = True
        bv_str = self.get_bv_str()[1:] #ignore sign bit
        for i in range(len(bv_str)):
            if bv_str[i] == '1':
                ret = False
                break
        return ret

    def is_pzero(self):
        return self.is_zero() and self.get_bv_str()[0] == '0'

    def is_nzero(self):
        return self.is_zero() and self.get_bv_str()[0] == '1'
        

    def is_pinf(self):
        return self.is_inf() and self.get_bv_str()[0] == '0'
    
    def is_ninf(self):
        return self.is_inf() and self.get_bv_str()[0] == '1'

    def _mk_pzero(self):
        self.__dict__ = copy.deepcopy(Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(0),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns).__dict__)

    def _mk_nzero(self):
        bv = '1' + ('0' * (self.ne + self.ns - 1))
        val = int(bv,2)
        self.__dict__ = copy.deepcopy(Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(val),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns).__dict__)
 
    def _mk_pinf(self):
        bv = '0' + ('1' * self.ne) + ('0' * (self.ns -1))
        val = int(bv,2)
        self.__dict__ = copy.deepcopy(Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(val),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns).__dict__)

    def _mk_ninf(self):
        bv = '1' + ('1' * self.ne) + ('0' * (self.ns -1))
        val = int(bv,2)
        self.__dict__ = copy.deepcopy(Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(val),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns).__dict__)

    def _mk_nan(self):
        bv = '0' + ('1' * self.ne) + ('1' * (self.ns -1))
        val = int(bv,2)
        self.__dict__ = copy.deepcopy(Float(val=z3.simplify(z3.fpBVToFP(z3.Int2BV(z3.IntVal(val),num_bits = self.ns + self.ne),z3.FPSort(self.ne,self.ns))),ne=self.ne, ns=self.ns).__dict__)




    def __str__(self):
        return str(self.z3_ds)