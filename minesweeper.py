#!/usr/bin/env python3

import sys

import BDD
import bddAPI
import re

def fact(n):
    if n<=1: return 1
    return n*fact(n-1)

def n_choose_k (n,k):
    assert n>=k
    return int(fact(n)/(fact(k)*fact(n-k)))

def Ones(n,k,i):
    if k==0: return [0 for _ in range(n)]
    if n==k: return [1 for _ in range(n)]
    z = n_choose_k(n-1,k)
    if i < z: return [0] + Ones(n-1,k,i)
    return [1] + Ones(n-1,k-1,i-z)

## This function generates all patterns of k out of n bits.
def allOnes(n,k):
    return [Ones(n,k,i) for i in range(n_choose_k(n,k))]

def applyMask(m,vs):
    return [v if p else bddAPI.Not(v) for (p,v) in zip(m,vs)]

## This function generates a k/n constraint.
def allSums(k,vs):
    return bddAPI.Or([bddAPI.And(applyMask(m,vs)) for m in allOnes(len(vs),k)])

## We do this just to make it easy to access the
## periphery of a given cell.
class FixList(list):
    def __getitem__(self,key):
        if (key < 0): return FixList([])
        if (key < len(self)): return list.__getitem__(self,key)
        return FixList([])
    pass


def constraints(K,VARS):
    res = []
    for (r,cols) in enumerate(K):
        for (c,k) in enumerate(cols):
            if k == '?': continue
            ##if k == 0: continue
            vlist = VARS[r-1][c-1] + VARS[r-1][c] + VARS[r-1][c+1] + \
                    VARS[ r ][c-1] +                VARS[ r ][c+1] + \
                    VARS[r+1][c-1] + VARS[r+1][c] + VARS[r+1][c+1]
            if k > len(vlist): raise Exception("bad")
            res += [allSums(k,vlist)]
            continue
        continue
    return res


def variables(K,VARS):
    return [v for (r,cols) in enumerate(K) for (c,k) in enumerate(cols) if k == '?' for v in VARS[r][c]]


def variableEntry(row,col,c):
    if c == '?': return [bddAPI.Bool("({},{})".format(row,col))]
    return []


def variableMatrix(K):
    return FixList([FixList([variableEntry(row,col,c) for (col,c) in enumerate(cols)]) for (row,cols) in enumerate(K)])


def decode(e):
    if e in ['?','x','!','@']: return '?'
    return int(e)


def tuplevar(s):
    if s[0] == '!': return bddAPI.Not(bddAPI.Bool(s[1:]))
    return bddAPI.Bool(s)


def forcedvar(v,row,col):
    if v == '@': return (True,bddAPI.Not(bddAPI.Bool("({},{})".format(row,col))))
    if v == '!': return (True,bddAPI.Bool("({},{})".format(row,col)))
    return (False,None)


def forces(row,entries):
    res = []
    for (col,v) in enumerate(entries):
        (hit,var) = forcedvar(v,row,col)
        if hit: res += [var]
        continue
    return res


def processFile(path):
    K = []
    pat = re.compile("!?\(\d{1}\,\d{1}\)")
    with open(path) as fp:
        cols = None
        ##
        ## This is where we previously had our forces spec .. we might add the bomb count.
        ##
        # line = fp.readline()
        # line = line.strip()
        # if len(line) < 7 or line[0:7] != 'forced:':
        #     raise Exception("first line must be a forced specification")
        # forces = line[7:].split(' ')
        # for f in forces:
        #     if f != '' and not pat.match(f): raise Exception("All force tuples must be of the form [!](r,c) but {} is not".format(f))
        #     continue
        # forces = [tuplevar(f) for f in forces if f != '']
        flist = []
        row = 0
        for line in fp:
            entries = line.strip().split(' ')
            cols  = len(entries) if cols is None else cols
            if cols != len(entries):
                raise Exception("Rows must contain a uniform number of columns but |row(0)| = {} and |row({})| = {}".format(cols,row,len(entries)))
            for (col,e) in enumerate(entries):
                if not e in ['!','@','x','?','0','1','2','3','4','5','6','7','8']:
                    raise Exception("At location row={} col={}: value {} is not a valid entry.".format(row,col,e))
                continue
            flist += forces(row,entries)
            row += 1
            entries = [decode(e) for e in entries]
            K += [entries]
        pass
    return (flist,K)


def pyval(x):
    if bddAPI.is_true(x): return True
    if bddAPI.is_false(x): return False
    raise Exception("We expect only Boolean results : {}".format(x))

# def check():
#     x = Int('x')
#     y = Int('y')
#     variables = [x,y]
#     s = bdd.Solver()
#     s.add([x > 2, y < 10, x + 2*y == 7])
#     if s.check() == sat:
#         m = s.model()
#         res = {k.decl().name():pyval(m.eval(k,model_completion=True)) for k in variables}
#         return res
#     return


def checkSAT(c,vlist):
    s = bddAPI.Solver()
    s.add(c)
    if s.check() != bddAPI.sat: raise Exception("Unsatisfiable Constraints")
    m = s.model()
    solution = {v:pyval(m.eval(v, model_completion=True)) for v in vlist}
    return solution


def checkForce(f, c):
    s = bddAPI.Solver()
    c = bddAPI.And([bddAPI.Not(f),c])
    s.add(c)
    return s.check() != bddAPI.sat


def tuplestr(v):
    assert isinstance(v, BDD.NonTerminal)
    # I have to use nonterminal here, I am slightly concerned
    # return v.varid
    sv = str(v)
    return sv + ' ' if sv[0] == '(' else sv


def confirmUnforced(c, solution):
    acc = True
    for (v,b) in solution.items():
        vx = v if b else bddAPI.Not(v)
        res = checkForce(vx,c)
        print("Tuple {:>5} {}forced {}".format(tuplestr(v), '*IS* ' if res else 'is un', "to {}".format(b) if res else ""))
        acc &= not res
        continue
    return acc


def checkFile(fname, ok=None):
    print("\nChecking: {}".format(fname))
    (forces, K) = processFile(fname)
    VARS = variableMatrix(K)
    c = bddAPI.And(constraints(K, VARS))
    vlist = variables(K, VARS)
    solution = checkSAT(c, vlist)
    acc = True
    forces = []
    if not forces:
        res = confirmUnforced(c, solution)
        acc &= res
        pass
    # print("File {}: {}\n".format(fname,"passed." if acc else "FAILED"))
    return True if ok is None else ok == acc


def main():
    checkFile("test0.mine", 'True')
    checkFile("test1.mine", 'False')
    checkFile("test2.mine", 'True')
    checkFile("test3.mine", 'False')
    checkFile("test4.mine", 'False')
    checkFile("test5.mine", 'False')
    checkFile("caltest.mine", 'True')
    checkFile("caltest2.mine", 'True')
    return
    #
    # fname = sys.argv[1]
    # ok = sys.argv[2] if len(sys.argv) > 2 else 'None'
    # ok = None if ok == 'None' else ok == 'True'
    # return checkFile(fname,ok)

if __name__ == "__main__":
    if main(): sys.exit(0)
    sys.exit(1)
    pass


