import BDDTest


def Not(x):
    assert isinstance(x, BDDTest.BDD)
    return BDDTest.BDD.Not(x)


def And(args):
    if len(args) == 0:
        return BDDTest.NonTerminal.one
    assert isinstance(args[0], BDDTest.BDD)
    if len(args) == 1:
        return args[0]
    else:
        v1 = args[0]
        for v in args[1:]:
            assert isinstance(v, BDDTest.BDD)
            v1 = v1.And(v)
        return v1


def Or(args):
    if len(args) == 0:
        return BDDTest.NonTerminal.zero
    assert isinstance(args[0], BDDTest.BDD)
    if len(args) == 1:
        return args[0]
    else:
        v1 = args[0]
        for v in args[1:]:
            assert isinstance(v, BDDTest.BDD)
            v1 = v1.Or(v)
        return v1


def Bool(x):
    # create a new variable with name x
    return BDDTest.NonTerminal(x, BDDTest.NonTerminal.zero, BDDTest.NonTerminal.one)


def is_true(x):
    # test whether the variable resolves to true
    return x
    # return x == BDDTest.NonTerminal.one


def is_false(x):
    # test whether the variable resolves to false
    # is always false .. might just be python False
    return not x
    # return x == BDDTest.NonTerminal.zero


class Solver():
    def __init__(self):
        self.x = BDDTest.Solver()
        return

    def add(self, c):
        # 'and' clause c to the existing set of clauses
        return self.x.add(c)

    def check(self):
        # return 'sat' if satisfiable.
        return self.x.check()

    def model(self):
        # return a variable assignement that satisfies the conjunction of the clauses.
        return Model(self.x.model())
    pass


class Model():
    # This is just a mapping from variables to values
    def __init__(self, x):
        self.x = dict(x)
        return

    def eval(self, variable, model_completion=True):
        # Return the value of the named variable.
        assert isinstance(self.x, dict)
        assert isinstance(variable, BDDTest.NonTerminal)
        return self.x.get(variable.varid, False)
    pass

sat = 'sat'