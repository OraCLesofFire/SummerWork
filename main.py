import BDD
import env
import random
import expr


def randomBDD(v=None):
    # create a random bdd using the variables A-J
    vlookup = [None, "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    if v is None:
        varid = rand.randint(1, 10)
        varid = vlookup[varid]
    else:
        varid = vlookup.index(v)
        decrement = rand.randint(1, varid-1)
        varid = vlookup[varid-decrement]
    left = rand.randrange(0, 2)
    if left == 1 and vlookup.index(varid) > 1:
        left = randomBDD(varid)
    else:
        left = rand.randrange(0, 2)
        left = BDD.NonTerminal.one if left == 1 else BDD.NonTerminal.zero
    right = rand.randrange(0, 2)
    if right == 1 and vlookup.index(varid) > 1:
        right = randomBDD(varid)
    else:
        right = rand.randrange(0, 2)
        right = BDD.NonTerminal.one if right == 1 else BDD.NonTerminal.zero
    if left == right:
        if left == BDD.NonTerminal.zero:
            left = BDD.NonTerminal.one
        else:
            left = BDD.NonTerminal.zero
    return BDD.NonTerminal(varid, left, right)


def randomEnv():
    return randomEnvL(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])


def randomEnvBool():
    # create a random environment using the variables ['x']['y']
    return randomEnvL(['x', 'y'])


def randomEnvL(vlookup):
    # create a random environment using the variables presented
    e = dict()
    for i in range(0, len(vlookup)):
        e[vlookup[i]] = rand.choice([True, False])
    return env.Env(**e)


def randomExpr():
    exprtypes = ["let", "and2", "or2", "xor2", "not", "buf", "ite", "var"]
    size = 0
    exp = rand.choice(exprtypes)
    match exp:
        case "let":
            e1 = randomExprh(size+2)
            e2 = randomExprh(size+2)
            exp = expr.Let(expr.newBoundVar(), e1, e2)
        case "and2":
            e1 = randomExprh(size+2)
            e2 = randomExprh(size+2)
            exp = expr.And2(e1, e2)
        case "or2":
            e1 = randomExprh(size + 2)
            e2 = randomExprh(size + 2)
            exp = expr.Ior2(e1, e2)
        case "xor2":
            e1 = randomExprh(size + 2)
            e2 = randomExprh(size + 2)
            exp = expr.Xor2(e1, e2)
        case "not":
            e1 = randomExprh(size + 2)
            exp = expr.Not(e1)
        case "buf":
            e1 = randomExprh(size + 2)
            exp = e1
        case "ite":
            e1 = randomExprh(size+2)
            e2 = randomExprh(size+2)
            e3 = randomExprh(size+2)
            exp = expr.ITE(e1, e2, e3)
        case "var":
            exp = expr.newVar()
    return exp


def randomExprh(size):
    exprtypes = ["let", "and2", "or2", "xor2", "not", "buf", "ite", "var"]
    if rand.randint(0, 10) >= size:
        exp = "var"
    else:
        if size >= 10:
            exp = "var"
        else:
            exp = rand.choice(exprtypes)
    match exp:
        case "let":
            e1 = randomExprh(size+2)
            e2 = randomExprh(size+2)
            exp = expr.Let(expr.newBoundVar(), e1, e2)
        case "and2":
            e1 = randomExprh(size+2)
            e2 = randomExprh(size+2)
            exp = expr.And2(e1, e2)
        case "or2":
            e1 = randomExprh(size + 2)
            e2 = randomExprh(size + 2)
            exp = expr.Ior2(e1, e2)
        case "xor2":
            e1 = randomExprh(size + 2)
            e2 = randomExprh(size + 2)
            exp = expr.Xor2(e1, e2)
        case "not":
            e1 = randomExprh(size + 2)
            exp = expr.Not(e1)
        case "buf":
            e1 = randomExprh(size + 2)
            exp = e1
        case "ite":
            e1 = randomExprh(size+2)
            e2 = randomExprh(size+2)
            e3 = randomExprh(size+2)
            exp = expr.ITE(e1, e2, e3)
        case "var":
            exp = expr.newVar()
    return exp


def BDDTests():
    A = randomBDD()
    B = randomBDD()
    C = randomBDD()
    E = randomEnv()

    x = A.And(B)
    y = B.And(A)
    assert x == y
    x = C.And(B).And(A)
    y = A.And(B).And(C)
    assert x == y
    x = A.Or(B).Or(C)
    y = C.Or(B).Or(A)
    assert x == y
    x = A.And(B).Not()
    y = A.Not().Or(B.Not())
    assert x == y
    x = A.Or(B).Not()
    y = A.Not().And(B.Not())
    assert x == y
    x = A.And(A)
    y = A
    assert x == y
    x = A.Or(A)
    y = A
    assert x == y
    x = A.Not().Not()
    y = A
    assert x == y
    x = A.And(A.Not())
    y = BDD.NonTerminal.zero
    assert x == y
    x = A.Or(A.Not())
    y = BDD.NonTerminal.one
    assert x == y
    x = A.Or(A.Not().And(B))
    y = A.Or(B)
    assert x == y
    x = A.And(B).Or(A.And(C))
    y = A.And(B.Or(C))
    assert x == y
    x = A.Not().Or(A.And(B))
    y = A.Not().Or(B)
    assert x == y
    x = A.Xor(B)
    y = A.Or(B).And(A.And(B).Not())
    assert x == y
    x = A.Ite(B, C)
    y = A.And(B).Or(A.Not().And(C))
    assert x == y
    x = A.Eval(E).And(B.Eval(E))
    y = A.And(B).Eval(E)
    assert x == y


def EXPRTests():
    x = randomExpr()
    print("___")
    x.prettyprint()

    v = x.get_vars()

    y = x.rebuild()
    # y.prettyprint()
    print("++")

    z = y.rebuild_2()
    z.prettyprint()

    a = z.rebuild_3()
    print("+++")
    a.prettyprint()

    newv = []
    for var in v:
        if var not in newv:
            newv.append(var)
    e = randomEnvL(newv)
    # check that the evaluation using a random evaluator is correct.
    assert x.eval(e) == y.eval(e)
    assert x.eval(e) == z.eval(e)

    b = BDD.BDD()
    c = b.expr_transform(x)
    d = b.expr_transform(y)
    # check that they are equivalent by doing a BDD transformation.
    assert c == d


def main():
    #
    # x = expr.Not(expr.Not(expr.Not(expr.newVar())))
    # x = x.rebuild_2()
    # x.prettyprint()

    n = 0
    end = 10000
    # end = 5
    # end = 0
    test = [end/10 * val for val in range(11)]
    while n < end:
        global rand
        rand = random.Random(n)
        BDDTests()
        EXPRTests()
        n += 1

        # completion percent
        if n in test:
            print((n/(end/100)), "%")
        expr.clearVars()
        expr.clearBoundVars()


global global_vars
global rand
main()
