import BDDTest
import env
import random
import expr


def randomBDD(v=None):
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
        left = BDDTest.NonTerminal.one if left == 1 else BDDTest.NonTerminal.zero
    right = rand.randrange(0, 2)
    if right == 1 and vlookup.index(varid) > 1:
        right = randomBDD(varid)
    else:
        right = rand.randrange(0, 2)
        right = BDDTest.NonTerminal.one if right == 1 else BDDTest.NonTerminal.zero
    if left == right:
        if left == BDDTest.NonTerminal.zero:
            left = BDDTest.NonTerminal.one
        else:
            left = BDDTest.NonTerminal.zero
    return BDDTest.NonTerminal(varid, left, right)


def randomEnv():
    vlookup = [None, "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    e = dict()
    for i in range(1, 10):
        if rand.randint(0, 1):
            e[vlookup[i]] = rand.choice([True, False])
    return env.Env(**e)


def randomEnvBool():
    e = dict()
    e['x'] = rand.choice([True, False])
    e['y'] = rand.choice([True, False])
    return env.Env(**e)


def randomEnvL(vlookup):
    e = dict()
    for i in range(0, len(vlookup)):
        e[vlookup[i]] = rand.choice([True, False])
    return env.Env(**e)


def randomExpr():
    fvars = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    bvars = ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
    exprtypes = ["let", "and2", "or2", "xor2", "not", "buf", "ite", "var"]
    size = 0
    if rand.randint(0, 10) >= size:
        if len(fvars) == 1:
            exp = "var"
        else:
            exp = rand.choice(exprtypes)
    else:
        exp = "var"
    match exp:
        case "let":
            bvar = rand.choice(bvars)
            bvars.remove(bvar)
            xvars = fvars.copy()
            xvars.append(bvar)
            e1, bvars = randomExprh(fvars, bvars, size+2)
            e2, bvars = randomExprh(xvars, bvars, size+2)
            exp = expr.Let(expr.Boundvar(bvar), e1, e2)
        case "and2":
            e1, bvars = randomExprh(fvars, bvars, size+2)
            e2, bvars = randomExprh(fvars, bvars, size+2)
            exp = expr.And2(e1, e2)
        case "or2":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            e2, bvars = randomExprh(fvars, bvars, size + 2)
            exp = expr.Ior2(e1, e2)
        case "xor2":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            e2, bvars = randomExprh(fvars, bvars, size + 2)
            exp = expr.Xor2(e1, e2)
        case "not":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            exp = expr.Not(e1)
        case "buf":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            exp = e1
        case "ite":
            e1, bvars = randomExprh(fvars, bvars, size+2)
            e2, bvars = randomExprh(fvars, bvars, size+2)
            e3, bvars = randomExprh(fvars, bvars, size+2)
            exp = expr.ITE(e1, e2, e3)
        case "var":
            a = rand.choice(fvars)
            if a in gvars:
                exp = expr.Boundvar(a)
            else:
                exp = expr.Var(a)
    return exp


def randomExprh(fvars, bvars, size):
    exprtypes = ["let", "and2", "or2", "xor2", "not", "buf", "ite", "var"]
    if rand.randint(0, 10) >= size:
        if len(fvars) == 1 or len(bvars) == 0:
            exp = "var"
        else:
            exp = rand.choice(exprtypes)
    else:
        exp = "var"
    match exp:
        case "let":
            bvar = rand.choice(bvars)
            bvars.remove(bvar)
            xvars = fvars.copy()
            xvars.append(bvar)
            e1, bvars = randomExprh(fvars, bvars, size+2)
            e2, bvars = randomExprh(xvars, bvars, size+2)
            exp = expr.Let(expr.Boundvar(bvar), e1, e2)
        case "and2":
            e1, bvars = randomExprh(fvars, bvars, size+2)
            e2, bvars = randomExprh(fvars, bvars, size+2)
            exp = expr.And2(e1, e2)
        case "or2":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            e2, bvars = randomExprh(fvars, bvars, size + 2)
            exp = expr.Ior2(e1, e2)
        case "xor2":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            e2, bvars = randomExprh(fvars, bvars, size + 2)
            exp = expr.Xor2(e1, e2)
        case "not":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            exp = expr.Not(e1)
        case "buf":
            e1, bvars = randomExprh(fvars, bvars, size + 2)
            exp = e1
        case "ite":
            e1, bvars = randomExprh(fvars, bvars, size+2)
            e2, bvars = randomExprh(fvars, bvars, size+2)
            e3, bvars = randomExprh(fvars, bvars, size+2)
            exp = expr.ITE(e1, e2, e3)
        case "var":
            a = rand.choice(fvars)
            if a in gvars:
                exp = expr.Boundvar(a)
            else:
                exp = expr.Var(a)
    return exp, bvars




n = 0
end = 10000
# end = 1
# end = 0
test = [end/10 * val for val in range(10)]
gvars = ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
largest = BDDTest.NonTerminal.zero
while n < end:
    rand = random.Random(n)
    # A = randomBDD()
    # B = randomBDD()
    # C = randomBDD()
    # D = randomBDD()
    #
    # E = randomEnv()

    # # expr tests
    # e = randomEnvBool()
    # x = expr.Var('x')
    # y = expr.Var('y')
    # assert expr.Not(expr.Not(x)).eval(e) == x.eval(e)
    # assert expr.And2(x, x).eval(e) == x.eval(e)
    # assert expr.And2(x, x).eval(e) == x.eval(e)
    # assert expr.And2(x, expr.Not(x)).eval(e) == False
    # assert expr.Ior2(x, x).eval(e) == x.eval(e)
    # assert expr.Ior2(x, expr.Not(x)).eval(e) == True
    # assert expr.And2(x, y).eval(e) == expr.Not(expr.Ior2(expr.Not(x), expr.Not(y))).eval(e)
    # assert expr.Ior2(x, y).eval(e) == expr.Not(expr.And2(expr.Not(x), expr.Not(y))).eval(e)


    # if A.num_vertices() > largest.num_vertices():
    #     largest = A
    # if B.num_vertices() > largest.num_vertices():
    #     largest = B
    # if C.num_vertices() > largest.num_vertices():
    #     largest = C
    # if D.num_vertices() > largest.num_vertices():
    #     largest = D

    # x = A.And(B)
    # y = B.And(A)
    # assert x == y
        # print("FAIL: AB == BA")
        # A.print("A")
        # B.print("B")
        # x.print("L")
        # y.print("R")
        # assert x == y

    # A.And(B)

    # Commutative property
    # ABC = CBA
    # x = C.And(B).And(A)
    # y = A.And(B).And(C)
    # assert x == y
        # print("FAIL: ABC = CBA")
        # A.print("A")
        # B.print("B")
        # C.print("C")
        # x.print("L")
        # y.print("R")
        # assert x == y

    # A + B + C = C + B + A
    # x = A.Or(B).Or(C)
    # y = C.Or(B).Or(A)
    # assert x == y
        # print("FAIL: A+B+C = C+B+A")
        # A.Or(B).print("A+B")
        # x.print("A+B+C")
        # C.Or(B).print("C+B")
        # y.print("C+B+A")

    # DeMorgan's Law
    # ~(AB) = ~A + ~B
    # x = A.And(B).Not()
    # y = A.Not().Or(B.Not())
    # assert x == y
        # print("FAIL: ~(AB) = ~A + ~B")
        # A.print("A")
        # B.print("B")
        # A.And(B).print("AB")
        # A.Not().print("~A")
        # B.Not().print("~B")
        # x.print("L")
        # y.print("R")
        # assert x == y

    # ~(A + B) = ~A~B
    # x = A.Or(B).Not()
    # y = A.Not().And(B.Not())
    # assert x == y
        # print("FAIL: ~(A + B) = ~A~B")
        # x.print("L")
        # y.print("R")

    # Identities
    # A*A = A
    # x = A.And(A)
    # y = A
    # assert x == y
        # print("FAIL: A*A = A")
        # x.print("L")
        # y.print("R")

    # A+A = A
    # x = A.Or(A)
    # y = A
    # assert x == y
        # print("FAIL: A+A = A")
        # x.print("L")
        # y.print("R")

    # ~~A = A
    # x = A.Not().Not()
    # y = A
    # assert x == y
        # print("FAIL: ~~A = A")
        # x.print("L")
        # y.print("R")

    # A*~A = 0
    # x = A.And(A.Not())
    # y = BDDTest.NonTerminal.zero
    # assert x == y
        # print("FAIL: A*~A = 0")
        # x.print("L")
        # y.print("R")

    # A+~A = 1
    # x = A.Or(A.Not())
    # y = BDDTest.NonTerminal.one
    # assert x == y
        # print("FAIL: A+~A = 1")
        # x.print("L")
        # y.print("R")

    # A+(~A)B == A+B
    # x = A.Or(A.Not().And(B))
    # y = A.Or(B)
    # assert x == y
        # print("FAIL: A+(~A)B == A+B")
        # x.print("L")
        # y.print("R")

    # AB + AC == A(B+C)
    # x = A.And(B).Or(A.And(C))
    # y = A.And(B.Or(C))
    # assert x == y
        # print("FAIL: AB + AC == A(B+C)")
        # x.print("L")
        # y.print("R")

    # ~A+AB == ~A+B
    # x = A.Not().Or(A.And(B))
    # y = A.Not().Or(B)
    # assert x == y
        # print("FAIL: ~A+AB == ~A+B")
        # x.print("L")
        # y.print("R")

    # AxorB == A+B * ~(A*B)
    # x = A.Xor(B)
    # y = A.Or(B).And(A.And(B).Not())
    # assert x == y
        # A.print("A")
        # B.print("B")
        # x.print("L")
        # y.print("R")

    # x = A.Ite(B, C)
    # y = A.And(B).Or(A.Not().And(C))
    # assert x==y
        # print("FAIL ITE")
        # A.print("A")
        # B.print("B")
        # C.print("C")
        # x.print("ITE(A B C)")
        # y.print("AB + ~AC")
        # assert x == y

    # env1 = env.Env(A=True, B=True)  # 1
    # env2 = env.Env(A=True)  # B + D + ~C
    # env3 = env.Env(A=False)  # C+ ~B + ~D
    # env4 = env.Env(A=True, B=False)  # D + ~C
    # x = A.Eval(E).And(B.Eval(E))
    # y = A.And(B).Eval(E)
    # assert x == y
        # print("FAIL AT Eval")
        # A.print("A")
        # B.print("B")
        # A.Eval(env1).print("A.Eval")
        # B.Eval(env1).print("B.Eval")
        # x.print("L")
        # y.print("R")
        # assert x == y

    # A.getModel()

    # print(n)
    f = randomExpr()
    # f.prettyprint()
    g = f.rebuild()
    # g.prettyprint()
    e = f.getvars()
    newe = []
    for x in e:
        if x not in newe:
            newe.append(x)
    # print(newe)
    e = randomEnvL(newe)
    # print(e.keys(), e.vals())
    assert f.eval(e) == g.eval(e)
    a = BDDTest.BDD()
    a = a.expr_transform(f)
    # print(a[0], a[1].keys(), a[1].vals())
    b = BDDTest.BDD()
    b = b.expr_transform(g)
    # print(b[0], b[1].keys(), a[1].vals())

    assert a == b


    if n in test:
        print((n/(end/100)), "%")
    n += 1

# print(largest.num_vertices())
# largest.print()
# m = largest.getModel()
# for k in m.keys():
#     print((k, m[k]), end="")
