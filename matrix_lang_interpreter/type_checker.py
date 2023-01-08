from collections import defaultdict
from typing import List
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
        raise Exception(f'TypeChecker: {type(node)} is not handled')

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

    def visit_AST(self, node: AST.AST) -> bool:
        return concat(
            [self.visit(stmt) for stmt in node.stmt_set],
            default0=WriterJust(None)
        )

    def visit_Block(self, node: AST.Block) -> WriterMaybe[Symbol]:
        self.symbolTable.pushScope()
        s = concat(
            [self.visit(stmt) for stmt in node.stmt_set],
            default0=WriterJust(None)
        )
        self.symbolTable.popScope()
        return s

    def visit_AssignStmt(self, node: AST.AssignStmt) -> WriterMaybe[Symbol]:
        def check_assignment(expr: Symbol, lvalue: VariableSymbol) -> WriterMaybe[Symbol]:
            if not isinstance(lvalue, VariableSymbol):
                return WriterNothing(f'{expr.lineno}: Assignment: lvalue is not VariableSymbol - not implemented')
            if (lvalue.type and lvalue.type != expr.type) or (lvalue.size and lvalue.size != expr.size):
                return WriterNothing(f'{expr.lineno}: Assignment: can\'t assign {(expr.type, expr.size)} to {(lvalue.type, lvalue.size)} variable')
            lvalue.type = expr.type
            lvalue.size = expr.size
            return WriterJust(
                Symbol(None, None, expr.lineno or lvalue.lineno),
                f'{expr.lineno}: check_assignment({lvalue}, {expr})' if self.debug else ''
            )

        m_expr = self.visit(node.expr)
        self.assignmentState = m_expr.is_just()
        m_lvalue = self.visit(node.lvalue)
        self.assignmentState = False
        return bind2(m_expr, m_lvalue, check_assignment)

    def check_cond(self, cond: Symbol) -> WriterMaybe[Symbol]:
        if cond.type != 'bool':
            return WriterNothing(f'{cond.lineno}: condition is not bool')
        return WriterJust(
            cond,
            f'{cond.lineno}: check_cond({cond})' if self.debug else ''
        )

    def visit_IfStmt(self, node: AST.IfStmt) -> WriterMaybe[Symbol]:
        def check_ifStmt(cond: Symbol, stmt: Symbol) -> WriterMaybe[Symbol]:
            return WriterJust(
                Symbol(None, None, cond.lineno or stmt.lineno),
                f'{cond.lineno}: check_ifStmt({cond}, {stmt})' if self.debug else ''
            )

        m_cond = self.visit(node.cond)
        m_cond = bind(m_cond, self.check_cond)

        self.symbolTable.pushScope()
        m_stmt = self.visit(node.stmt)
        self.symbolTable.popScope()

        return bind2(m_cond, m_stmt, check_ifStmt)

    def visit_IfElseStmt(self, node: AST.IfElseStmt) -> WriterMaybe[Symbol]:
        def check_ifElseStmt(cond: Symbol, stmt: Symbol, elseStmt: Symbol) -> WriterMaybe[Symbol]:
            return WriterJust(
                Symbol(None, None, cond.lineno or stmt.lineno or elseStmt.lineno),
                f'{cond.lineno}: check_ifElseStmt({cond}, {stmt}, {elseStmt})' if self.debug else ''
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
            return WriterJust(
                Symbol(None, None, cond.lineno or stmt.lineno),
                f'{cond.lineno}: check_whileLoop({cond}, {stmt})' if self.debug else ''
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
            if not isinstance(id, VariableSymbol):
                return WriterNothing(f'{id.lineno}: ForLoop: problem with variable')
            id.type = 'int'
            id.size = ()
            return WriterJust(
                id,
                f'{id.lineno}: check_forLoopId({id})' if self.debug else ''
            )

        def check_forLoopRangeBeg(beg: Symbol) -> WriterMaybe[Symbol]:
            if beg.type != 'int' or beg.size != ():
                return WriterNothing(f'{beg.lineno}: ForLoop: beg variable is not int')
            return WriterJust(
                beg,
                f'{beg.lineno}: check_forLoopRangeBeg({beg})' if self.debug else ''
            )

        def check_forLoopRangeEnd(end: Symbol) -> WriterMaybe[Symbol]:
            if end.type != 'int' or end.size != ():
                return WriterNothing(f'{end.lineno}: ForLoop: end variable is not int')
            return WriterJust(
                end,
                f'{end.lineno}: check_forLoopRangeEnd({end})' if self.debug else ''
            )

        def check_forLoop(id: Symbol, beg: Symbol, end: Symbol, stmt: Symbol) -> WriterMaybe[Symbol]:
            return WriterJust(
                Symbol(None, None, beg.lineno or end.lineno or id.lineno or stmt.lineno),
                f'{beg.lineno}: check_forLoop({id}, {beg}, {end}, {stmt})' if self.debug else ''
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
        if self.loopState:
            return WriterJust(None, f'{node.lineno}: visit_Break({node})' if self.debug else '')
        return WriterNothing(f'{node.lineno}: break outside of a loop')

    def visit_Continue(self, node: AST.Continue) -> WriterMaybe[Symbol]:
        if self.loopState:
            return WriterJust(None, f'{node.lineno}: visit_Continue({node})' if self.debug else '')
        return WriterNothing(f'{node.lineno}: continue outside of a loop')

    def visit_Print(self, node: AST.Print) -> WriterMaybe[Symbol]:
        return concat(
            [self.visit(expr) for expr in node.expr_set],
            default0=WriterJust(None)
        )

    def visit_Return(self, node: AST.Return) -> WriterMaybe[Symbol]:
        return concat(
            [self.visit(expr) for expr in node.expr_set],
            default0=WriterJust(None)
        )

    def visit_BinExpr(self, node: AST.BinExpr) -> WriterMaybe[Symbol]:
        def check_two_symbols_op(op, s1: Symbol, s2: Symbol) -> WriterMaybe[Symbol]:
            if op not in Types.ttype:
                return WriterNothing(f'{s1.lineno}: BinExpr: no such operator as {op}')
            if s1.type not in Types.ttype[op] or s2.type not in Types.ttype[op][s1.type]:
                return WriterNothing(f'{s1.lineno}: BinExpr: wrong operator {op} for {s1.type} and {s2.type}')
            if s1.size != s2.size:
                return WriterNothing(f'{s1.lineno}: BinExpr: incompatible sizes: {s1.size} and {s2.size}')
            return WriterJust(
                Symbol(Types.ttype[op][s1.type][s2.type], s1.size, s1.lineno or s2.lineno),
                f'{s1.lineno}: check_two_symbol_op({op}, {s1}, {s2})' if self.debug else ''
            )
        op = node.op
        m_left = self.visit(node.left)
        m_right = self.visit(node.right)

        m_right = bind2(m_left, m_right, partial(check_two_symbols_op, op))
        return m_right

    def visit_RelationExpr(self, node: AST.RelationExpr) -> WriterMaybe[Symbol]:
        def check_two_symbols_op(op, s1: Symbol, s2: Symbol) -> WriterMaybe[Symbol]:
            if s1.type not in Types.ttype[op] or s2.type not in Types.ttype[op][s1.type]:
                return WriterNothing(f'{s1.lineno}: RelationExpr: wrong operator {op} for {s1.type} and {s2.type}')
            if s1.size != s2.size:
                return WriterNothing(f'{s1.lineno}: RelationExpr: incompatible sizes: {s1.size} and {s2.size}')
            return WriterJust(
                Symbol('bool', (), s1.lineno or s2.lineno),
                f'{s1.lineno}: check_two_symbol_op({op}, {s1}, {s2})' if self.debug else ''
            )
        op = node.op
        m_left = self.visit(node.left)
        m_right = self.visit(node.right)

        m_right = bind2(m_left, m_right, partial(check_two_symbols_op, op))
        return m_right

    def visit_UnExpr(self, node: AST.UnExpr) -> WriterMaybe[Symbol]:
        def check_symbol_op(op, symbol: Symbol) -> WriterMaybe[Symbol]:
            if op not in Types.ttype:
                return WriterNothing(f'{symbol.lineno}: UnExpr: no such operator as {op}')
            if symbol.type not in Types.ttype[op]:
                return WriterNothing(f'{symbol.lineno}: UnExpr: wrong operator {op} for {symbol.type}')
            return WriterJust(
                symbol,
                f'{symbol.lineno}: check_symbol_op({op}, {symbol})' if self.debug else ''
            )

        op = node.op
        m_child = self.visit(node.child)
        m_child = bind(m_child, partial(check_symbol_op, op))
        return m_child

    def visit_Vector(self, node: AST.Vector) -> WriterMaybe[Symbol]:
        def check_vectorElems(expr1: Symbol, expr2: Symbol) -> WriterMaybe[Symbol]:
            if expr1.type != expr2.type:
                return WriterNothing(f'{expr1.lineno}: Vector: wrong type of elems: {expr1.type}, {expr2.type}')
            if expr1.size != expr2.size:
                return WriterNothing(f'{expr1.lineno}: Vector: wrong size of elems: {expr1.size}, {expr2.size}')
            return WriterJust(
                Symbol(expr1.type, expr1.size, expr1.lineno or expr2.lineno),
                f'{expr1.lineno}: check_vectorElems({expr1}, {expr2})' if self.debug else ''
            )

        def check_vector(size: int, expr: Symbol) -> WriterMaybe[Symbol]:
            return WriterJust(
                Symbol(expr.type, (size, *expr.size), expr.lineno),
                f'{expr.lineno}: check_vector({size}, {expr})' if self.debug else ''
            )

        m_expr = concat(
            [self.visit(expr) for expr in node.expr_set],
            check_vectorElems,
            default0=WriterJust(Symbol('int', ()))
        )
        return bind(m_expr, partial(check_vector, len(node.expr_set)))

    def visit_Zeros(self, node: AST.Zeros) -> WriterMaybe[Symbol]:
        def check_sizeType(size: Symbol) -> WriterMaybe[Symbol]:
            if len(size.size) != 1 or size.size[0] == 0 or size.type != 'int':
                return WriterNothing(f'{size.lineno}: Zeros: wrong type of shape parameter: ({size.type}, {size.size})')
            return WriterJust(
                Symbol('int', tuple([expr.n for expr in node.size.expr_set]), size.lineno),
                f'{size.lineno}: check_sizeType({size})' if self.debug else ''
            )

        m_size = self.visit(node.size)
        return bind(m_size, check_sizeType)

    def visit_Ones(self, node: AST.Ones) -> WriterMaybe[Symbol]:
        def check_sizeType(size: Symbol) -> WriterMaybe[Symbol]:
            if len(size.size) != 1 or size.size[0] == 0 or size.type != 'int':
                return WriterNothing(f'{size.lineno}: ones: wrong type of shape parameter: ({size.type}, {size.size})')
            return WriterJust(
                Symbol('int', tuple([expr.n for expr in node.size.expr_set]), size.lineno),
                f'{size.lineno}: check_sizeType({size})' if self.debug else ''
            )

        m_size = self.visit(node.size)
        return bind(m_size, check_sizeType)

    def visit_Eye(self, node: AST.Eye) -> WriterMaybe[Symbol]:
        def check_sizeType(size: Symbol) -> WriterMaybe[Symbol]:
            if len(size.size) != 0 or size.type != 'int':
                return WriterNothing(f'{size.lineno}: eye: wrong type of shape parameter: ({size.type}, {size.size})')
            return WriterJust(
                Symbol('int', (node.size.n, node.size.n), size.lineno),
                f'{size.lineno}: check_sizeType({size})' if self.debug else ''
            )

        m_size = self.visit(node.size)
        return bind(m_size, check_sizeType)

    def visit_Ref(self, node: AST.Ref) -> WriterMaybe[Symbol]:
        def check_idxs(idxs: Symbol) -> WriterMaybe[Symbol]:
            if len(idxs.size) != 1 or idxs.type != 'int':
                return WriterNothing(f'{idxs.lineno}: ref: wrong type of ref parameter: ({idxs.type}, {idxs.size})')
            return WriterJust(
                idxs,
                f'{idxs.lineno}: check_idxs({idxs})' if self.debug else ''
            )

        def check_ref(idxs_symbol: Symbol, term: Symbol) -> WriterMaybe[Symbol]:
            idxs = tuple([expr.n for expr in node.idxs.expr_set])
            if len(idxs) == 0:
                return WriterNothing(f'{term.lineno}: ref: no index given')
            if len(idxs) > len(term.size):
                return WriterNothing(f'{term.lineno}: ref: accessing dim {len(idxs)} larger than dim {len(term.size)}')
            for i in range(len(idxs)):
                if idxs[i] >= term.size[i]:
                    return WriterNothing(f'{term.lineno}: ref: accessing element outside of the vector: {idxs[i]} >= {term.size[i]}')
            return WriterJust(
                VariableSymbol(term.type, (*term.size[len(idxs):],), term.lineno),
                f'{term.lineno}: check_ref({term})' if self.debug else ''
            )

        m_idxs = self.visit(node.idxs)
        m_idxs = bind(m_idxs, check_idxs)

        m_term = self.visit(node.term)
        return bind2(m_idxs, m_term, check_ref)

    def visit_Id(self, node: AST.Id) -> WriterMaybe[VariableSymbol]:
        symbol = self.symbolTable.get(node.id)
        if symbol is not None:
            return WriterJust(symbol, f'{node.lineno}: symbolTable.get({node})' if self.debug else '')
        if self.assignmentState:
            symbol = VariableSymbol(None, None, node.lineno, node.id)
            self.symbolTable.put(node.id, symbol)
            return WriterJust(symbol, f'{node.lineno}: symbolTable.put({node})' if self.debug else '')
        return WriterNothing(f'{node.lineno}: no such symbol as {node.id}')

    def visit_IntNum(self, node: AST.IntNum) -> WriterMaybe[Symbol]:
        return WriterJust(Symbol('int', (), node.lineno), f'{node.lineno}: visit_IntNum({node})' if self.debug else '')

    def visit_FloatNum(self, node: AST.FloatNum) -> WriterMaybe[Symbol]:
        return WriterJust(Symbol('float', (), node.lineno), f'{node.lineno}: visit_FloatNum({node})' if self.debug else '')

    def visit_String(self, node: AST.String) -> WriterMaybe[Symbol]:
        return WriterJust(Symbol('string', (), node.lineno), f'{node.lineno}: visit_String({node})' if self.debug else '')
