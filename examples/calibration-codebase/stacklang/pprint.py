"""Pretty-print the AST as an indented S-expression.

Useful for debugging the parser and for the `pprint` CLI subcommand. Each node
renders as `(NodeName child ...)`; literals render inline.
"""

from . import ast_nodes as ast


def pretty(node, indent=0):
    pad = "  " * indent
    if isinstance(node, ast.Program):
        body = "\n".join(pretty(s, indent + 1) for s in node.statements)
        return "{}(program\n{})".format(pad, body)
    if isinstance(node, ast.NumberLit):
        return "{}(number {})".format(pad, node.value)
    if isinstance(node, ast.StringLit):
        return "{}(string {!r})".format(pad, node.value)
    if isinstance(node, ast.BoolLit):
        return "{}(bool {})".format(pad, str(node.value).lower())
    if isinstance(node, ast.NilLit):
        return "{}(nil)".format(pad)
    if isinstance(node, ast.Identifier):
        return "{}(ident {})".format(pad, node.name)
    if isinstance(node, ast.Unary):
        return "{}(unary {}\n{})".format(pad, node.op, pretty(node.operand, indent + 1))
    if isinstance(node, ast.Binary):
        return "{}(binary {}\n{}\n{})".format(
            pad, node.op, pretty(node.left, indent + 1), pretty(node.right, indent + 1)
        )
    if isinstance(node, ast.Logical):
        return "{}(logical {}\n{}\n{})".format(
            pad, node.op, pretty(node.left, indent + 1), pretty(node.right, indent + 1)
        )
    if isinstance(node, ast.Assign):
        return "{}(assign {}\n{})".format(pad, node.name, pretty(node.value, indent + 1))
    if isinstance(node, ast.Let):
        return "{}(let {}\n{})".format(pad, node.name, pretty(node.value, indent + 1))
    if isinstance(node, ast.ExprStmt):
        return "{}(expr-stmt\n{})".format(pad, pretty(node.expr, indent + 1))
    if isinstance(node, ast.Print):
        return "{}(print\n{})".format(pad, pretty(node.expr, indent + 1))
    if isinstance(node, ast.Block):
        body = "\n".join(pretty(s, indent + 1) for s in node.statements)
        return "{}(block\n{})".format(pad, body)
    if isinstance(node, ast.If):
        parts = [pretty(node.condition, indent + 1), pretty(node.then_branch, indent + 1)]
        if node.else_branch is not None:
            parts.append(pretty(node.else_branch, indent + 1))
        return "{}(if\n{})".format(pad, "\n".join(parts))
    if isinstance(node, ast.While):
        return "{}(while\n{}\n{})".format(
            pad, pretty(node.condition, indent + 1), pretty(node.body, indent + 1)
        )
    if isinstance(node, ast.FuncDef):
        params = " ".join(node.params)
        return "{}(func {} [{}]\n{})".format(
            pad, node.name, params, pretty(node.body, indent + 1)
        )
    if isinstance(node, ast.Return):
        if node.value is None:
            return "{}(return)".format(pad)
        return "{}(return\n{})".format(pad, pretty(node.value, indent + 1))
    if isinstance(node, ast.Call):
        parts = [pretty(node.callee, indent + 1)]
        parts.extend(pretty(a, indent + 1) for a in node.args)
        return "{}(call\n{})".format(pad, "\n".join(parts))
    return "{}(unknown {})".format(pad, type(node).__name__)
