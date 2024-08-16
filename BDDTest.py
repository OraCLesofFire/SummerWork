import itertools
import env
import expr


class Solver():

    def __init__(self):
        self.explist = []
        self.checked = False
        self.sat = False
        self.model = None

    def add(self, x):
        self.checked = False
        assert isinstance(x, BDD)
        self.explist.append(x)

    def check(self):
        if not self.checked:
            x = self.explist[0]
            assert isinstance(x, BDD)
            for i in range(len(self.explist[1:])):
                y = self.explist[i]
                assert isinstance(y, BDD)
                x = x.And(y)
            x = x.getModel()
            if x is None:
                self.sat = "no"
                self.model = None
            else:
                self.sat = 'sat'
                self.model = x
        self.checked = True
        return self.sat
    def model(self):
        if self.checked:
            return self.model
        else:
            self.check()
            return self.model


class BDD(object):
    vertexList = dict()
    id = itertools.count()

    def __init__(self):
        self.mark = False

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return super().__hash__()

    @classmethod
    def non_terminal(cls, v, l, r):
        if l == r:
            return l
        else:
            return NonTerminal(v, l, r)

    @classmethod
    def bool(cls, v):
        return NonTerminal(v, NonTerminal.one, NonTerminal.zero)

    def num_vertices(self):
        if isinstance(self, Terminal):
            return 1
        else:
            assert isinstance(self, NonTerminal)
            return self.left.num_vertices() + self.right.num_vertices()

    def print(self, string=None):
        print(string)
        if isinstance(self, Terminal):
            print("Terminal at ", self.val)
        elif isinstance(self, NonTerminal):
            self.reset_marks()
            self._print()
        print()

    def _print(self):
        if not self.mark:
            if isinstance(self, NonTerminal):
                print("vertex id", self.id, "with varid", self.varid, " points to: ")
                print("\t", self.left.id if isinstance(self.left, NonTerminal) else self.left.val, " left and",
                      self.right.id if isinstance(self.right, NonTerminal) else self.right.val, "right")
            if isinstance(self.left, NonTerminal):
                self.left._print()
            if isinstance(self.right, NonTerminal):
                self.right._print()
        self.mark = True

    def reset_marks(self):
        self.mark = False
        if isinstance(self, NonTerminal):
            self.left.reset_marks()
            self.right.reset_marks()

    def And(self, v2):
        return self.apply_operation("and", [v2])

    def Or(self, v2):
        return self.apply_operation("or", [v2])

    def Not(self):
        return self.apply_operation("not", [])

    def Xor(self, v2):
        return self.apply_operation("xor", [v2])

    def Ite(self, v1, v2):
        return self.apply_operation("ite", [v1, v2])

    def getModel(self):
        if isinstance(self, Terminal):
            # temp result here
            return None
        else:
            assert isinstance(self, NonTerminal)
            e = dict()
            solutionExists = False
            e[self.varid] = False
            e, solutionExists = self.left._getModel(e, solutionExists)
            if solutionExists:
                return env.Env(**e)
            else:
                assert isinstance(e, dict)
                e[self.varid] = True
                e, solutionExists = self.right._getModel(e, solutionExists)
            if solutionExists:
                return env.Env(**e)
            else:
                return None

    def _getModel(self, e, solutionExists):

        # if our solution is already found, just return
        if solutionExists:
            return e, solutionExists

        # if this is a terminal node return true, or take a step back
        if isinstance(self, Terminal):
            if self.val == 0:
                return e, solutionExists
            else:
                return e, True

        # otherwise take a step further in
        else:
            assert isinstance(e, dict)
            assert isinstance(self, NonTerminal)
            e[self.varid] = False
            e, solutionExists = self.left._getModel(e, solutionExists)
            if not solutionExists:
                assert isinstance(e, dict)
                e[self.varid] = True
                e, solutionExists = self.right._getModel(e, solutionExists)
                assert isinstance(e, dict)
                if not solutionExists:
                    e.pop(self.varid)
                    print(e)
                    return e, solutionExists
            return e, solutionExists

    def expr_transform(self, expression, e=None):
        if e is None:
            e = env.Env()
        # if isinstance(expression, expr.ExprN):
        #     args = [self.expr_transform(exp, e) for exp in expression.args]
        #     assert isinstance(all(args), BDD)
        #     e1 = args[0]
        #     if isinstance(expression, expr.And):
        #         for e in args[1:]:
        #             e1 = e1.And(e)
        #     if isinstance(expression, expr.Ior):
        #         for e in args[1:]:
        #             e1 = e1.Or(e)
        #     if isinstance(expression, expr.Xor):
        #         for e in args[1:]:
        #             e1 = e1.Xor(e)
        #     return e1, e
        if isinstance(expression, expr.Expr2):
            x = self.expr_transform(expression.x, e)
            y = self.expr_transform(expression.y, e)
            assert isinstance(x, BDD)
            assert isinstance(y, BDD)
            if isinstance(expression, expr.And2):
                return x.And(y)
            if isinstance(expression, expr.Ior2):
                return x.Or(y)
            if isinstance(expression, expr.Xor2):
                return x.Xor(y)
        if isinstance(expression, expr.Expr1):
            x = self.expr_transform(expression.x, e)
            assert isinstance(x, BDD)
            if isinstance(expression, expr.Not):
                return x.Not()
            if isinstance(expression, expr.Buf):
                return x
        if isinstance(expression, expr.Expr):
            if isinstance(expression, expr.ITE):
                i = self.expr_transform(expression.i, e)
                t = self.expr_transform(expression.t, e)
                el = self.expr_transform(expression.e, e)
                assert isinstance(i, BDD)
                assert isinstance(t, BDD)
                assert isinstance(el, BDD)
                return i.Ite(t, el)
            elif isinstance(expression, expr.Let):
                if expression.v.name not in e:
                    e = e(**{expression.v.name: self.expr_transform(expression.e1, e)})
                e2 = self.expr_transform(expression.e2, e)
                assert isinstance(e2, BDD)
                return e2
        if isinstance(expression, expr.Var):
            if expression.name in e:
                return e[expression.name]
            else:
                a = BDD.bool(expression.name)
                return a
        if isinstance(expression, expr.Boundvar):
            if expression.name in e:
                return e[expression.name]
            else:
                a = BDD.bool(expression.name)
                return a

    def Eval(self, environment):
        if isinstance(self, NonTerminal):
            if self.varid in environment:
                if environment[self.varid] == 1:
                    return self.right.Eval(environment)
                else:
                    return self.left.Eval(environment)
            if isinstance(self.left, NonTerminal) and self.left.varid in environment:
                if environment[self.left.varid] == 1:
                    left = self.left.right
                else:
                    left = self.left.left
            else:
                left = self.left
            if isinstance(self.right, NonTerminal) and self.right.varid in environment:
                if environment[self.right.varid] == 1:
                    right = self.right.right
                else:
                    right = self.right.left
            else:
                right = self.right
            return BDD.non_terminal(self.varid, left.Eval(environment), right.Eval(environment))
        else:
            return self

    def apply_operation(self, operation, vertices):
        assert isinstance(vertices, list)

        # negation
        if len(vertices) == 1 and self.id == vertices[0].id * -1:
            if operation == "and":
                return NonTerminal.zero
            if operation == "or" or operation == "xor":
                return NonTerminal.one

        # not case
        if operation == "not":

            # negation
            if self.id * -1 in BDD.vertexList:
                return BDD.vertexList[self.id * -1]
            if isinstance(self, Terminal):
                return self.perform_operation(operation, vertices)
            else:
                assert isinstance(self, NonTerminal) and isinstance(self.left, BDD) and isinstance(self.right, BDD)
                return self.non_terminal(self.varid, self.left.apply_operation(operation, vertices),
                                         self.right.apply_operation(operation, vertices))

        # case of equivalent ID
        equal = True
        for v in vertices:
            assert isinstance(v, BDD)
            equal = True if v.id == self.id and equal else False
        if equal:
            return NonTerminal.zero if operation == "xor" else self

        # terminal case
        for v in vertices:
            if isinstance(v, Terminal):
                if operation == "ite":
                    v1 = vertices[0]
                    v2 = vertices[1]
                    if v1 == v2:
                        return v1
                    elif isinstance(v1, Terminal):
                        return self.Or(v2) if v1.val == 1 else self.Not().And(v2)
                    elif isinstance(v2, Terminal):
                        return self.Not().Or(v1) if v2.val == 1 else self.And(v1)
                else:
                    vertices.remove(v)
                    return v.perform_operation(operation, [self])
        if isinstance(self, Terminal):
            return self.perform_operation(operation, vertices)

        # equivalent varid
        assert isinstance(self, NonTerminal)
        vid = self.varid
        equal = True
        for v in vertices:
            equal = True if v.varid == vid and equal else False
        if equal:
            if operation == "ite":
                v1 = vertices[0]
                v2 = vertices[1]
                assert isinstance(self.left, BDD) and isinstance(self.right, BDD)
                return self.non_terminal(self.varid, self.left.apply_operation(operation, [v1.left, v2.left]),
                                         self.right.apply_operation(operation, [v1.right, v2.right]))
            else:
                v1 = vertices[0]
                assert isinstance(self.left, BDD) and isinstance(self.right, BDD)
                return self.non_terminal(self.varid, self.left.apply_operation(operation, [v1.left]),
                                         self.right.apply_operation(operation, [v1.right]))

        # non-equivalent varid
        largest = self
        for v in vertices:
            largest = v if v.varid > largest.varid else largest
        largestList = [v for v in vertices if v.varid == largest.varid]
        if self.varid == largest.varid:
            largestList.append(self)

        if operation == "ite":
            vertsleft = [self]
            vertsleft.extend(vertices)
            vertsright = vertsleft.copy()
            for i in range(len(vertsleft)):
                v = vertsleft[i]
                if v in largestList:
                    vertsright[i] = v.right
                    vertsleft[i] = v.left
            return self.non_terminal(largest.varid,
                                     vertsleft[0].apply_operation(operation, [vertsleft[1], vertsleft[2]]),
                                     vertsright[0].apply_operation(operation, [vertsright[1], vertsright[2]])
                                     )

        else:
            v1 = self
            v2 = vertices[0]
            if v2 == largest:
                (v1, v2) = (v2, v1)
            return self.non_terminal(v1.varid, v1.left.apply_operation(operation, [v2]),
                                     v1.right.apply_operation(operation, [v2]))


class Terminal(BDD):

    def __init__(self, val):
        super().__init__()
        self.val = val
        if val == 0:
            self.id = -1
        if val == 1:
            self.id = 1

    def perform_operation(self, operation, vertices):
        assert isinstance(vertices, list)
        match operation:
            case "and":
                return vertices[0] if self.val == 1 else NonTerminal.zero
            case "or":
                return NonTerminal.one if self.val == 1 else vertices[0]
            case "not":
                return NonTerminal.one if self.val == 0 else NonTerminal.zero
            case "xor":
                return vertices[0].Not() if self.val == 1 else vertices[0]
            case "ite":
                v1 = vertices[0]
                v2 = vertices[1]
                if isinstance(self, Terminal):
                    return v1 if self.val == 1 else v2
                elif isinstance(v1, Terminal):
                    return self.Or(v2) if v1.val == 1 else self.Not().And(v2)
                elif isinstance(v2, Terminal):
                    return self.Not().Or(v1) if v2.val == 1 else self.And(v1)


class NonTerminal(BDD):
    zero = Terminal(0)
    one = Terminal(1)

    def __init__(self, varid, left, right):
        super().__init__()
        self.left = left
        self.right = right
        self.varid = varid
        vertex = (varid, left.id, right.id)
        invertedVertex = (varid, left.id * -1, right.id * -1)

        # check if it already exists
        if vertex in BDD.vertexList.keys():
            self.id = BDD.vertexList[vertex]

        # check if negation exists
        elif invertedVertex in BDD.vertexList.keys():
            self.id = BDD.vertexList[invertedVertex] * -1
            BDD.vertexList[vertex] = self.id

        # if neither it nor its negation exists, create a new ID
        else:
            self.id = next(BDD.id) + 2
            BDD.vertexList[vertex] = self.id
            # print((varid, left.id, right.id), "Added to vertex list as", self.id)

        # metadata
        self.numVertices = self.left.num_vertices() + self.right.num_vertices()

    def __str__(self):
        return self.varid

    def num_vertices(self):
        return self.numVertices

    def get_subgraph(self):
        d = dict()
        if not self.mark:
            d[self.id] = self
            if isinstance(self.left, NonTerminal):
                d.update(self.left.get_subgraph())
            else:
                d[self.left.id] = self.left
            if isinstance(self.right, NonTerminal):
                d.update(self.right.get_subgraph())
            else:
                d[self.right.id] = self.right
            self.mark = True
        return d
