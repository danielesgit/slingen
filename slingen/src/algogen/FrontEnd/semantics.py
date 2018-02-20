from grako.ast import AST
from FrontEnd.exceptions import *
from core.expression import BaseExpression, Symbol, Matrix, Vector, Scalar,\
                            Equal, Plus, Minus, Times, Transpose,\
                            Inverse
from storage import ST_LOWER, ST_UPPER, ST_FULL


class cl1ckSemantics(object):
    def __init__(self):
        super().__init__()
        self._cache = dict()

    def declarations(self, ast):
        decs = [d for d in ast]
        return decs

    def declaration(self, ast):
        if ast['name'] not in self._cache:
            if ast['vartype'] == 'Matrix':
                rows, cols = ast['dims']
                rows, cols = Symbol(rows), Symbol(cols)
                var = Matrix(ast['name'], (rows, cols))
                for prop in ast.props:
                    var.set_property(prop)
            elif ast['vartype'] == 'Vector':
                rows = ast['dims'][0]
                rows = Symbol(rows)
                var = Vector(ast['name'], (rows,))
            elif ast['vartype'] == 'Scalar':
                var = Scalar(ast['name'])
            else:
                raise Exception

            var.set_property(ast.iotype)
            if "LowerStorage" in ast.props:
                storage = ST_LOWER
            elif "UpperStorage" in ast.props:
                storage = ST_UPPER
            else:
                if "LowerTriangular" in ast.props:
                    storage = ST_LOWER
                elif "UpperTriangular" in ast.props:
                    storage = ST_UPPER
                else:
                    storage = ST_FULL
            # overwritting
            ow = ast.ow
            if ow:
                ow = self.id2variable(ow)
            else:
                ow = var
            var.st_info = (storage, ow)

            self._cache[ast['name']] = var
            return var
        else:
            raise RedeclarationError('Variable %s redeclared', ast.name)

    def equation(self, ast):
        lhs = ast['lhs']
        rhs = ast['rhs']
        if lhs.get_size() != rhs.get_size():
            raise SizeError('Equation\'s lhs and rhs have different sizes' % (lhs.get_size(), rhs.get_size()))
        return Equal([lhs, rhs])

    def expression(self, ast):
        if isinstance(ast, BaseExpression):
            return ast
        elif isinstance(ast, AST):
            if ast.ops[0] == "+":
                return Plus(ast.args)
            elif ast.ops[0] == "-":
                return Plus([ast.args[0], Minus([ast.args[1]])])

    def term(self, ast):
        if isinstance(ast, BaseExpression):
            return ast
        elif isinstance(ast, AST):
            if ast.ops[0] == "-":
                return Minus(ast.args)
            elif ast.ops[0] == "*":
                return Times(ast.args)
        else:
            print(ast.__class__)

    def factor(self, ast):
        if isinstance(ast, str):
            return self.id2variable(ast)
        elif isinstance(ast, BaseExpression):
            return ast
        elif isinstance(ast, AST):
            if ast.func == "trans":
                return Transpose([ast.arg])
            elif ast.func == "inv":
                return Inverse([ast.arg])
        else:
            print(ast.__class__)
            raise Exception

    def constant(self, ast):
        raise NotImplemented
        try:
            return Literal(int(ast))
        except ValueError:
            return Literal(float(ast))

    def id2variable(self, name):
        try:
            return self._cache[name]
        except ValueError:
            return UndeclaredError('%s not declared' % name)

