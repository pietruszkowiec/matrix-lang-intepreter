from collections import defaultdict
from functools import partial
from matrix_lang_interpreter.writer_maybe import *
from matrix_lang_interpreter import AST
from matrix_lang_interpreter.symbol_table import *


class NodeVisitor:
    def visit(self, node) -> WriterMaybe[Symbol]:
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return WriterNothing(f'TypeChecker: Encountered problem(s)')

class Types:
    ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(None)))
    for op in ['+', '-', '*', '/']:
        ttype[op]['int']['int'] = 'int'
        ttype[op]['int']['float'] = 'float'
        ttype[op]['float']['int'] = 'float'
        ttype[op]['float']['float'] = 'float'

    ttype['+']['string']['string'] = 'string'
    ttype['*']['string']['int'] = 'string'
    ttype['*']['int']['string'] = 'string'

    for op in ['==', '!=', '<=', '>=', '<', '>']:
        ttype[op]['int']['int'] = 'bool'
        ttype[op]['int']['float'] = 'bool'
        ttype[op]['float']['int'] = 'bool'
        ttype[op]['float']['float'] = 'bool'

    for op in ['==', '!=']:
        ttype[op]['bool']['bool'] = 'bool'
        ttype[op]['string']['string'] = 'bool'

    vectorop = set(['.+', '.-', '.*', './'])


class TypeChecker(NodeVisitor):
    def __init__(self, debug=False):
        self.debug = debug
        self.symbolTable = SymbolTable(None)
        self.assignmentState = False
        self.loopState = False

    def visit_AST(self, node: AST.AST) -> WriterMaybe[Symbol]:
        return concat(
            [self.visit(stmt) for stmt in node.stmt_set],
            default0=WriterJust(Symbol(None, None))
        )

    def visit_Block(self, node: AST.Block) -> WriterMaybe[Symbol]:
        self.symbolTable.pushScope()
        s = concat(
            [self.visit(stmt) for stmt in node.stmt_set],
            default0=WriterJust(Symbol(None, None))
        )
        self.symbolTable.popScope()
        return s

    def visit_AssignStmt(self, node: AST.AssignStmt) -> WriterMaybe[Symbol]:
        def check_assignment(expr: Symbol, lvalue: VariableSymbol) -> WriterMaybe[Symbol]:
            lineno = expr.lineno or lvalue.lineno
            if not isinstance(lvalue, VariableSymbol):
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: Assignment: lvalue is not VariableSymbol - not implemented'
                )
            lvalue.type = expr.type
            lvalue.size = expr.size
            return WriterJust(
                Symbol(None, None, lineno),
                f'Line {lineno:3}: TypeChecker: check_assignment({lvalue}, {expr})' if self.debug else ''
            )

        m_expr = self.visit(node.expr)
        if m_expr.is_just():
            self.assignmentState = True
            m_lvalue = self.visit(node.lvalue)
            self.assignmentState = False
        else:
            m_lvalue = WriterNothing()
        return bind2(m_expr, m_lvalue, check_assignment)

    def check_cond(self, cond: Symbol) -> WriterMaybe[Symbol]:
        lineno = cond.lineno
        if cond.type != 'bool':
            return WriterNothing(f'Line {lineno:3}: TypeChecker: condition is not bool')
        return WriterJust(
            cond,
            f'Line {lineno:3}: TypeChecker: check_cond({cond})' if self.debug else ''
        )

    def visit_IfStmt(self, node: AST.IfStmt) -> WriterMaybe[Symbol]:
        def check_ifStmt(cond: Symbol, stmt: Symbol) -> WriterMaybe[Symbol]:
            lineno = cond.lineno or stmt.lineno
            return WriterJust(
                Symbol(None, None, lineno),
                f'Line {lineno:3}: TypeChecker: check_ifStmt({cond}, {stmt})' if self.debug else ''
            )

        m_cond = self.visit(node.cond)
        m_cond = bind(m_cond, self.check_cond)

        self.symbolTable.pushScope()
        m_stmt = self.visit(node.stmt)
        self.symbolTable.popScope()

        return bind2(m_cond, m_stmt, check_ifStmt)

    def visit_IfElseStmt(self, node: AST.IfElseStmt) -> WriterMaybe[Symbol]:
        def check_ifElseStmt(cond: Symbol, stmt: Symbol, elseStmt: Symbol) -> WriterMaybe[Symbol]:
            lineno = cond.lineno or stmt.lineno or elseStmt.lineno
            return WriterJust(
                Symbol(None, None, lineno),
                f'Line {lineno:3}: TypeChecker: check_ifElseStmt({cond}, {stmt}, ' +
                f'{elseStmt})' if self.debug else ''
            )

        m_cond = self.visit(node.cond)
        m_cond = bind(m_cond, self.check_cond)

        self.symbolTable.pushScope()
        m_stmt = self.visit(node.stmt)
        self.symbolTable.popScope()

        self.symbolTable.pushScope()
        m_elseStmt = self.visit(node.elseStmt)
        self.symbolTable.popScope()

        return bind3(m_cond, m_stmt, m_elseStmt, check_ifElseStmt)

    def visit_WhileLoop(self, node: AST.WhileLoop) -> WriterMaybe[Symbol]:
        def check_whileLoop(cond: Symbol, stmt: Symbol) -> WriterMaybe[Symbol]:
            lineno = cond.lineno or stmt.lineno
            return WriterJust(
                Symbol(None, None, lineno),
                f'Line {lineno:3}: TypeChecker: check_whileLoop({cond}, {stmt})' if self.debug else ''
            )

        m_cond = self.visit(node.cond)
        m_cond = bind(m_cond, self.check_cond)

        self.symbolTable.pushScope()
        prev_state = self.loopState
        self.loopState = True

        m_stmt = self.visit(node.stmt)

        self.loopState = prev_state
        self.symbolTable.popScope()

        return bind2(m_cond, m_stmt, check_whileLoop)

    def visit_ForLoop(self, node: AST.ForLoop) -> WriterMaybe[Symbol]:
        def check_forLoopId(id: Symbol) -> WriterMaybe[Symbol]:
            lineno = id.lineno
            if not isinstance(id, VariableSymbol):
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: ForLoop: problem with variable'
                )
            id.type = 'int'
            id.size = ()
            return WriterJust(
                id,
                f'Line {lineno:3}: TypeChecker: check_forLoopId({id})' if self.debug else ''
            )

        def check_forLoopRangeBeg(beg: Symbol) -> WriterMaybe[Symbol]:
            lineno = beg.lineno
            if beg.type != 'int' or beg.size != ():
                return WriterNothing(f'Line {lineno:3}: TypeChecker: ForLoop: beg variable is not int')
            return WriterJust(
                beg,
                f'Line {lineno:3}: TypeChecker: check_forLoopRangeBeg({beg})' if self.debug else ''
            )

        def check_forLoopRangeEnd(end: Symbol) -> WriterMaybe[Symbol]:
            lineno = end.lineno
            if end.type != 'int' or end.size != ():
                return WriterNothing(f'Line {lineno:3}: TypeChecker: ForLoop: end variable is not int')
            return WriterJust(
                end,
                f'Line {lineno:3}: TypeChecker: check_forLoopRangeEnd({end})' if self.debug else ''
            )

        def check_forLoop(id: Symbol, beg: Symbol, end: Symbol, stmt: Symbol) -> WriterMaybe[Symbol]:
            lineno = beg.lineno or end.lineno or id.lineno or stmt.lineno
            return WriterJust(
                Symbol(None, None, lineno),
                f'Line {lineno:3}: TypeChecker: check_forLoop({id}, {beg}, ' +
                f'{end}, {stmt})' if self.debug else ''
            )

        self.symbolTable.pushScope()
        self.assignmentState = True
        m_id = bind(self.visit(node.id), check_forLoopId)
        self.assignmentState = False

        m_beg = bind(self.visit(node.beg), check_forLoopRangeBeg)
        m_end = bind(self.visit(node.end), check_forLoopRangeEnd)

        prev_state = self.loopState
        self.loopState = True

        m_stmt = self.visit(node.stmt)

        self.loopState = prev_state
        self.symbolTable.popScope()

        return bind4(m_id, m_beg, m_end, m_stmt, check_forLoop)

    def visit_Break(self, node: AST.Break) -> WriterMaybe[Symbol]:
        lineno = node.lineno
        if self.loopState:
            return WriterJust(
                Symbol(None, None),
                f'Line {lineno:3}: TypeChecker: visit_Break({node})' if self.debug else ''
            )
        return WriterNothing(f'Line {lineno:3}: TypeChecker: break outside of a loop')

    def visit_Continue(self, node: AST.Continue) -> WriterMaybe[Symbol]:
        lineno = node.lineno
        if self.loopState:
            return WriterJust(
                Symbol(None, None),
                f'Line {lineno:3}: TypeChecker: visit_Continue({node})' if self.debug else ''
            )
        return WriterNothing(f'Line {lineno:3}: TypeChecker: continue outside of a loop')

    def visit_Print(self, node: AST.Print) -> WriterMaybe[Symbol]:
        return concat(
            [self.visit(expr) for expr in node.expr_set],
            default0=WriterJust(Symbol(None, None))
        )

    def visit_Return(self, node: AST.Return) -> WriterMaybe[Symbol]:
        return concat(
            [self.visit(expr) for expr in node.expr_set],
            default0=WriterJust(Symbol(None, None))
        )

    def visit_BinExpr(self, node: AST.BinExpr) -> WriterMaybe[Symbol]:
        def check_two_symbols_op(op, s1: Symbol, s2: Symbol) -> WriterMaybe[Symbol]:
            lineno = s1.lineno or s2.lineno
            if op not in Types.ttype:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: BinExpr: no such operator as {op}'
                )
            if s1.type not in Types.ttype[op] or s2.type not in Types.ttype[op][s1.type]:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: BinExpr: wrong operator {op} for ' +
                    f'{s1.type} and {s2.type}'
                )
            if s1.size != s2.size:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: BinExpr: incompatible sizes: ' +
                    f'{s1.size} and {s2.size}'
                )
            return WriterJust(
                Symbol(Types.ttype[op][s1.type][s2.type], s1.size, lineno),
                f'Line {lineno:3}: TypeChecker: check_two_symbol_op({op}, {s1}, {s2})' if self.debug else ''
            )
        op = node.op
        m_left = self.visit(node.left)
        m_right = self.visit(node.right)

        m_right = bind2(m_left, m_right, partial(check_two_symbols_op, op))
        return m_right

    def visit_RelationExpr(self, node: AST.RelationExpr) -> WriterMaybe[Symbol]:
        def check_two_symbols_op(op, s1: Symbol, s2: Symbol) -> WriterMaybe[Symbol]:
            lineno = s1.lineno or s2.lineno
            if s1.type not in Types.ttype[op] or s2.type not in Types.ttype[op][s1.type]:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: RelationExpr: wrong operator ' +
                    f'{op} for {s1.type} and {s2.type}'
                )
            if s1.size != s2.size:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: RelationExpr: incompatible sizes: ' +
                    f'{s1.size} and {s2.size}'
                )
            return WriterJust(
                Symbol('bool', (), lineno),
                f'Line {lineno:3}: TypeChecker: check_two_symbol_op({op}, {s1}, {s2})' if self.debug else ''
            )

        op = node.op
        m_left = self.visit(node.left)
        m_right = self.visit(node.right)

        m_right = bind2(m_left, m_right, partial(check_two_symbols_op, op))
        return m_right

    def visit_UnExpr(self, node: AST.UnExpr) -> WriterMaybe[Symbol]:
        def check_symbol_op(op, symbol: Symbol) -> WriterMaybe[Symbol]:
            lineno = symbol.lineno
            if op not in Types.ttype:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: UnExpr: no such operator as {op}'
                )
            if symbol.type not in Types.ttype[op]:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: UnExpr: wrong operator {op} for {symbol.type}'
                )
            return WriterJust(
                symbol,
                f'Line {lineno:3}: TypeChecker: check_symbol_op({op}, {symbol})' if self.debug else ''
            )

        op = node.op
        m_child = self.visit(node.child)
        m_child = bind(m_child, partial(check_symbol_op, op))
        return m_child

    def visit_Vector(self, node: AST.Vector) -> WriterMaybe[Symbol]:
        def check_vectorElems(expr1: Symbol, expr2: Symbol) -> WriterMaybe[Symbol]:
            lineno = expr1.lineno or expr2.lineno
            if expr1.type != expr2.type:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: Vector: wrong type of elems: ' +
                    f'{expr1.type}, {expr2.type}'
                )
            if expr1.size != expr2.size:
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: Vector: wrong size of elems: ' +
                    f'{expr1.size}, {expr2.size}'
                )
            return WriterJust(
                Symbol(expr1.type, expr1.size, lineno),
                f'Line {lineno:3}: TypeChecker: check_vectorElems({expr1}, {expr2})' if self.debug else ''
            )

        def check_vector(size: int, expr: Symbol) -> WriterMaybe[Symbol]:
            lineno = expr.lineno
            return WriterJust(
                Symbol(expr.type, (size, *expr.size), lineno),
                f'Line {lineno:3}: TypeChecker: check_vector({size}, {expr})' if self.debug else ''
            )

        m_expr = concat(
            [self.visit(expr) for expr in node.expr_set],
            check_vectorElems,
            default0=WriterJust(Symbol('int', ()))
        )
        return bind(m_expr, partial(check_vector, len(node.expr_set)))

    def visit_Zeros(self, node: AST.Zeros) -> WriterMaybe[Symbol]:
        def check_sizeType(size: Symbol) -> WriterMaybe[Symbol]:
            lineno = size.lineno
            if len(size.size) != 1 or size.size[0] == 0 or size.type != 'int':
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: Zeros: wrong type of shape parameter: ' +
                    f'({size.type}, {size.size})'
                )
            return WriterJust(
                Symbol('int', tuple([expr.n for expr in node.size.expr_set]), lineno),
                f'Line {lineno:3}: TypeChecker: check_sizeType({size})' if self.debug else ''
            )

        m_size = self.visit(node.size)
        return bind(m_size, check_sizeType)

    def visit_Ones(self, node: AST.Ones) -> WriterMaybe[Symbol]:
        def check_sizeType(size: Symbol) -> WriterMaybe[Symbol]:
            lineno = size.lineno
            if len(size.size) != 1 or size.size[0] == 0 or size.type != 'int':
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: ones: wrong type of shape parameter: ' +
                    f'({size.type}, {size.size})'
                )
            return WriterJust(
                Symbol('int', tuple([expr.n for expr in node.size.expr_set]), lineno),
                f'Line {lineno:3}: TypeChecker: check_sizeType({size})' if self.debug else ''
            )

        m_size = self.visit(node.size)
        return bind(m_size, check_sizeType)

    def visit_Eye(self, node: AST.Eye) -> WriterMaybe[Symbol]:
        def check_sizeType(size: Symbol) -> WriterMaybe[Symbol]:
            lineno = size.lineno
            if len(size.size) != 0 or size.type != 'int':
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: eye: wrong type of shape parameter: ' +
                    f'({size.type}, {size.size})'
                )
            return WriterJust(
                Symbol('int', (node.size.n, node.size.n), lineno),
                f'Line {lineno:3}: TypeChecker: check_sizeType({size})' if self.debug else ''
            )

        m_size = self.visit(node.size)
        return bind(m_size, check_sizeType)

    def visit_Ref(self, node: AST.Ref) -> WriterMaybe[Symbol]:
        def check_idxs(idxs: Symbol) -> WriterMaybe[Symbol]:
            lineno = idxs.lineno
            if len(idxs.size) != 1 or idxs.type != 'int':
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: ref: wrong type of ref parameter: ' +
                    f'({idxs.type}, {idxs.size})'
                )
            return WriterJust(
                idxs,
                f'Line {lineno:3}: TypeChecker: check_idxs({idxs})' if self.debug else ''
            )

        def check_ref(idxs_symbol: Symbol, term: Symbol) -> WriterMaybe[Symbol]:
            lineno = idxs_symbol.lineno or term.lineno
            idxs = tuple([expr.n for expr in node.idxs.expr_set])
            if len(idxs) == 0:
                return WriterNothing(f'Line {lineno:3}: TypeChecker: ref: no index given')
            if len(idxs) > len(term.size):
                return WriterNothing(
                    f'Line {lineno:3}: TypeChecker: ref: accessing dim {len(idxs)} ' +
                    f'larger than dim {len(term.size)}'
                )
            for i in range(len(idxs)):
                if idxs[i] >= term.size[i]:
                    return WriterNothing(
                        f'Line {lineno:3}: TypeChecker: ref: ' +
                        f'accessing element outside of the vector: {idxs[i]} >= {term.size[i]}'
                    )
            return WriterJust(
                VariableSymbol(term.type, (*term.size[len(idxs):],), lineno),
                f'Line {lineno:3}: TypeChecker: check_ref({term})' if self.debug else ''
            )

        m_idxs = self.visit(node.idxs)
        m_idxs = bind(m_idxs, check_idxs)

        m_term = self.visit(node.term)
        return bind2(m_idxs, m_term, check_ref)

    def visit_Id(self, node: AST.Id) -> WriterMaybe[VariableSymbol]:
        lineno = node.lineno
        symbol = self.symbolTable.get(node.id)
        if symbol is not None:
            symbol.lineno = lineno
            return WriterJust(
                symbol,
                f'Line {lineno:3}: TypeChecker: symbolTable.get({node})' if self.debug else ''
            )
        if self.assignmentState:
            symbol = VariableSymbol(None, None, lineno, node.id)
            self.symbolTable.put(node.id, symbol)
            return WriterJust(
                symbol,
                f'Line {lineno:3}: TypeChecker: symbolTable.put({node})' if self.debug else ''
            )
        return WriterNothing(f'Line {lineno:3}: TypeChecker: no such symbol as {node.id}')

    def visit_IntNum(self, node: AST.IntNum) -> WriterMaybe[Symbol]:
        lineno = node.lineno
        return WriterJust(
            Symbol('int', (), lineno),
            f'Line {lineno:3}: TypeChecker: visit_IntNum({node})' if self.debug else ''
        )

    def visit_FloatNum(self, node: AST.FloatNum) -> WriterMaybe[Symbol]:
        lineno = node.lineno
        return WriterJust(
            Symbol('float', (), lineno),
            f'Line {lineno:3}: TypeChecker: visit_FloatNum({node})' if self.debug else ''
        )

    def visit_String(self, node: AST.String) -> WriterMaybe[Symbol]:
        lineno = node.lineno
        return WriterJust(
            Symbol('string', (), lineno),
            f'Line {lineno:3}: TypeChecker: visit_String({node})' if self.debug else ''
        )
