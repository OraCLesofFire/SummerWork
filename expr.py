#!/usr/bin/env python3
import env
import copy


class Expr:
    def eval(self, e):
        raise Exception()

    def rebuild(self):
        newcopy = copy.deepcopy(self)
        return newcopy.__rebuild__(start=newcopy)

    def __rebuild__(self, start):
        raise Exception()

    def print(self):
        raise Exception()

    def prettyprint(self):
        return self.__pretty_printh__(0)

    def __pretty_printh__(self, depth):
        raise Exception()

    def get_vars(self):
        raise Exception()

    def make_unique(self):
        return copy.deepcopy(self).__make_unique__([])[0]

    def __make_unique__(self, l):
        raise Exception()

    def __change_var__(self, v1, v2):
        raise Exception()


class Var(Expr):
    def __init__(self, name):
        self.name = name
        return

    def eval(self, e):
        assert isinstance(e, env.Env)
        # if the variable is a boolean, return its value
        if isinstance(e[self.name], bool):
            return e[self.name]

        # if the variable is an expression, return the evaluation of its value
        elif isinstance(e[self.name], Expr):
            return e[self.name].eval(env)
    pass

    def __rebuild__(self, start):
        return start

    def print(self):
        return str(self.name)

    def __pretty_printh__(self, depth):
        print("\t"*depth, self.name)

    def get_vars(self):
        return [self.name]

    def __make_unique__(self, l):
        return l.append(self.name)

    def __change_var__(self, v1, v2):
        return


class Boundvar(Expr):
    def __init__(self, name):
        self.name = name
        return

    def eval(self, e):
        assert isinstance(e, env.Env)
        # if the variable is a boolean, return its value
        if isinstance(e[self.name], bool):
            return e[self.name]

        # if the variable is an expression, return the evaluation of its value
        elif isinstance(e[self.name], Expr):
            return e[self.name].eval(env)
    pass

    def __rebuild__(self, start):
        return start

    def print(self):
        return str(self.name)

    def __pretty_printh__(self, depth):
        print("\t"*depth, self.name)

    def get_vars(self):
        return []

    def __make_unique__(self, l):
        return l.append(self.name)

    def __change_var__(self, v1, v2):
        if self.name == v1:
            self.name = v2


class Expr1(Expr):
    def __init__(self, x):
        assert isinstance(x, Expr)
        self.x = x
        return

    def __rebuild__(self, start):
        s = start
        if isinstance(self.x, Let):
            newstart = Let(self.x.v, self.x.e1, s)
            self.x = self.x.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.x.__rebuild__(start=s)
        return s

    def get_vars(self):
        v = []
        v.extend(self.x.get_vars())
        return v

    def __make_unique__(self, l):
        return self, self.x.__make_unique__(l)

    def __change_var__(self, v1, v2):
        self.x.__change_var__(v1, v2)


class Expr2(Expr):
    def __init__(self, x, y):
        assert isinstance(x, Expr)
        assert isinstance(y, Expr)
        self.x = x
        self.y = y
        return

    def __rebuild__(self, start):
        s = start
        if isinstance(self.x, Let):
            newstart = Let(self.x.v, self.x.e1, s)
            self.x = self.x.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.x.__rebuild__(start=s)
        if isinstance(self.y, Let):
            newstart = Let(self.y.v, self.y.e1, s)
            self.y = self.y.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.y.__rebuild__(start=s)
        return s

    def get_vars(self):
        v = []
        v.extend(self.x.get_vars())
        v.extend(self.y.get_vars())
        return v

    def __make_unique__(self, l):
        l = self.x.__make_unique__(l)
        l = self.y.__make_unique__(l)
        return l

    def __change_var__(self, v1, v2):
        self.x.__change_var__(v1, v2)
        self.y.__change_var__(v1, v2)


class ExprN(Expr):
    def __init__(self, *args):
        assert all(isinstance(arg, Expr) for arg in args)
        self.args = args
        return

    def __rebuild__(self, start):
        s = start
        for i in range(len(self.args)):
            if isinstance(self.args[i], Let):
                newstart = Let(self.args[i].v, self.args[i].e1, s)
                # convert the touple to a list, change first element, then change back............
                l = list(self.args)
                l[i] = self.args[i].e2
                l = tuple(l)
                self.args = l

                s = newstart.__rebuild__(start=newstart)
            else:
                assert isinstance(self.args[i], Expr)
                s = self.args[i].__rebuild__(start=s)
        return s

    def get_vars(self):
        v = []
        for a in self.args:
            v.extend(a.get_vars())
        return v

    def __make_unique__(self, l):
        for a in self.args:
            assert isinstance(a, Expr)
            l = a.__make_unique__(l)
        return l

    def __change_var__(self, v1, v2):
        for a in self.args:
            assert isinstance(a, Expr)
            a.__change_var__(v1, v2)


class Let(Expr):
    def __init__(self, v, e1, e2):
        assert isinstance(v, Boundvar)
        assert isinstance(e1, Expr)
        assert isinstance(e2, Expr)
        self.v = v
        self.e1 = e1
        self.e2 = e2

    def eval(self, e):
        assert isinstance(e, env.Env)
        e = e(**{self.v.name: self.e1.eval(e)})
        return self.e2.eval(e)

    def __rebuild__(self, start):
        s = start
        if isinstance(self.e1, Let):
            newstart = Let(self.e1.v, self.e1.e1, s)
            self.e1 = self.e1.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.e1.__rebuild__(start=s)
        if not isinstance(self.e2, Let):
            self.e2 = self.e2.__rebuild__(start=self.e2)
        return s

    def print(self):
        return "Let: " + self.v.print() + " = " + self.e1.print() + " do: " + self.e2.print()

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(Let ", self.v.print(), " = ")
        self.e1.__pretty_printh__(depth + 1)
        print("\t"*depth, "Do")
        self.e2.__pretty_printh__(depth + 1)
        print("\t"*depth, ")")

    def get_vars(self):
        v = []
        v.extend(self.e1.get_vars())
        v.extend(self.e2.get_vars())
        return v

    def __make_unique__(self, l):
        if self.v in l:
            newv = self.v
            while newv in l:
                newv = newv + newv
            l.append(newv)
            self.v = Boundvar(newv)
            self.e2.__change_var__(self.v, newv)
        self.e1.__make_unique__(l)
        self.e2.__make_unique__(l)
        return l

    def __change_var__(self, v1, v2):
        self.e1.__change_var__(v1, v2)
        self.e1.__change_var__(v1, v2)
        self.e2.__change_var__(v1, v2)


class LetN(Expr):
    def __init__(self, vlist, elist, e2):
        assert all(isinstance(v, Boundvar) for v in vlist)
        assert all(isinstance(e, Expr) for e in elist)
        assert len(vlist) == len(elist)
        assert isinstance(e2, Expr)
        self.vlist = vlist
        self.elist = elist
        self.e2 = e2

    def eval(self, e):
        assert isinstance(e, env.Env)
        for i in range(len(self.vlist)):
            e = e(**{self.vlist[i].name: self.elist[i].eval(e)})
        return self.e2.eval(e)

    def __rebuild__(self, start):
        print("Please god no")
        pass


class ITE(Expr):
    def __init__(self, i, t, e):
        assert isinstance(i, Expr)
        assert isinstance(t, Expr)
        assert isinstance(e, Expr)
        self.i = i
        self.t = t
        self.e = e
        return

    def eval(self, e):
        assert isinstance(e, env.Env)
        return self.t.eval(e) if self.i.eval(e) else self.e.eval(e)

    def __rebuild__(self, start):
        s = start
        if isinstance(self.i, Let):
            newstart = Let(self.i.v, self.i.e1, s)
            self.i = self.i.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.i.__rebuild__(start=s)
        if isinstance(self.t, Let):
            newstart = Let(self.t.v, self.t.e1, s)
            self.t = self.t.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.t.__rebuild__(start=s)
        if isinstance(self.e, Let):
            newstart = Let(self.e.v, self.e.e1, s)
            self.e = self.e.e2
            s = newstart.__rebuild__(newstart)
        else:
            s = self.e.__rebuild__(start=s)
        return s

    def print(self):
        return "If: " + self.i.print() + " Then: " + self.t.print() + " Else: " + self.e.print()

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(If: ")
        self.i.__pretty_printh__(depth + 1)
        print("\t"*depth, "Then: ")
        self.t.__pretty_printh__(depth + 1)
        print("\t"*depth, "Else: ")
        self.e.__pretty_printh__(depth + 1)
        print("\t"*depth, ")")

    def get_vars(self):
        v = []
        v.extend(self.i.get_vars())
        v.extend(self.t.get_vars())
        v.extend(self.e.get_vars())
        return v

    def __make_unique__(self, l):
        l = self.i.__make_unique__(l)
        l = self.t.__make_unique__(l)
        l = self.e.__make_unique__(l)
        return l


class And(ExprN):
    def eval(self, e):
        assert isinstance(e, env.Env)
        f = self.args[0].eval(e)
        if len(self.args) == 1:
            return f
        for x in self.args[1:]:
            f = f and x.eval(e)
        return f

    def print(self):
        s = ""
        for i in range(len(self.args)):
            s += self.args[i].print() + " And "
        l = len(s)
        return s[:l-6]
    pass

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(And ")
        for a in self.args:
            a.__prettyprinth(depth+1)
        print("\t"*depth, ")")


class Ior(ExprN):
    def eval(self, e):
        assert isinstance(e, env.Env)
        f = self.args[0].eval(e)
        if len(self.args) == 1:
            return f
        for x in self.args[1:]:
            f = f or x.eval(e)
        return f

    def print(self):
        s = ""
        for i in range(len(self.args)):
            s += self.args[i].print() + " Or "
        l = len(s)
        return s[:l-5]

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(Or")
        for a in self.args:
            a.__prettyprinth(depth+1)
        print("\t"*depth, ")")
    pass


class Xor(ExprN):
    def eval(self, e):
        assert isinstance(e, env.Env)
        f = self.args[0].eval(e)
        if len(self.args) == 1:
            return f
        for x in self.args[1:]:
            f = f ^ x.eval(e)
        return f

    def print(self):
        s = ""
        for i in range(len(self.args)):
            s += self.args[i].print() + " Xor "
        l = len(s)
        return s[:l-6]

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(Xor")
        for a in self.args:
            a.__prettyprinth(depth+1)
        print("\t"*depth, ")")


class And2(Expr2):
    def eval(self, e):
        assert isinstance(e, env.Env)
        return self.x.eval(e) and self.y.eval(e)

    def print(self):
        return self.x.print() + " AND " + self.y.print()

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(And")
        self.x.__pretty_printh__(depth + 1)
        self.y.__pretty_printh__(depth + 1)
        print("\t"*depth, ")")


class Ior2(Expr2):
    def eval(self, e):
        assert isinstance(e, env.Env)
        return self.x.eval(e) or self.y.eval(e)

    def print(self):
        return self.x.print() + " Or " + self.y.print()

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(Or")
        self.x.__pretty_printh__(depth + 1)
        self.y.__pretty_printh__(depth + 1)
        print("\t"*depth, ")")


class Xor2(Expr2):
    def eval(self, e):
        assert isinstance(e, env.Env)
        return self.x.eval(e) ^ self.y.eval(e)

    def print(self):
        return self.x.print() + " Xor " + self.y.print()

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(Xor")
        self.x.__pretty_printh__(depth + 1)
        self.y.__pretty_printh__(depth + 1)
        print("\t"*depth, ")")


class Not(Expr1):
    def eval(self, e):
        assert isinstance(e, env.Env)
        return not self.x.eval(e)

    def print(self):
        return "Not " + self.x.print()

    def __pretty_printh__(self, depth):
        print("\t"*depth, "(Not")
        self.x.__pretty_printh__(depth + 1)
        print("\t"*depth, ")")


class Buf(Expr1):
    def eval(self, e):
        assert isinstance(e, env.Env)
        return self.x.eval(e)

    def print(self):
        return self.x.print()
    pass

    def __pretty_printh__(self, depth):
        self.x.__pretty_printh__(depth + 1)
