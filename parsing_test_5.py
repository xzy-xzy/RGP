import re
from config import config
from itertools import product
import ast, astor
from collections.abc import Iterable

k, u = config.k, config.u

def extract_strings_from_code(code):
    pattern = r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
    matches = re.findall(pattern, code)

    strings = [match[1:-1] for match in matches]
    return strings


def remove_comments(code):
    code = re.sub(r'#.*', '', code)

    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)

    code = '\n'.join([line for line in code.splitlines() if line.strip()])

    return code


def extract_assignments(code):
    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^=].*)'

    matches = re.findall(pattern, code)

    assignments = []
    for match in matches:
        left, right = match
        assignments.append((left.strip(), right.strip()))

    return assignments


def find_variable_in_code(code, variable_name):
    pattern = r'(?<!\w)' + re.escape(variable_name) + r'(?!\w)'

    matches = re.findall(pattern, code)

    return len(matches) > 0


class DictExtractor(ast.NodeVisitor):
    def __init__(self):
        self.dicts = []

    def visit_Dict(self, node):
        try:
            keys = [ast.literal_eval(key) for key in node.keys]
        except:
            keys = [ast.unparse(key).strip() for key in node.keys]
        try:
            values = [ast.literal_eval(value) for value in node.values]
        except:
            values = [ast.unparse(value).strip() for value in node.values]
        dict_content = dict(zip(keys, values))
        self.dicts.append(dict_content)
        self.generic_visit(node)

def extract_dicts_from_code(code):
    try:
        tree = ast.parse(code)
        extractor = DictExtractor()
        extractor.visit(tree)
        return extractor.dicts
    except SyntaxError:
        print("Invalid Python code.")
        return []

import ast
import astor


def find_dict_assignments(code):
    try:
        tree = ast.parse(code)
        dict_assignments = [ ]
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Dict):
                    dict_assignments.append((node.lineno, node.end_lineno))

            elif isinstance(node, ast.DictComp):
                dict_assignments.append((node.lineno, node.end_lineno))

        lineno = [ ]
        for start, end in dict_assignments:
            for i in range(start, end + 1):
                lineno.append(i - 1)

        return lineno

    except SyntaxError:
        print("Invalid Python code.")
        return []


def extract_assignments(code):
    try:
        tree = ast.parse(code)

        assignments = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets
                value = node.value

                if isinstance(value, ast.Tuple) and all(isinstance(target, ast.Tuple) for target in targets):
                    left_elements = [ast.unparse(el) for target in targets for el in target.elts]
                    right_elements = [ast.unparse(el) for el in value.elts]

                    if len(left_elements) == len(right_elements):
                        for left, right in zip(left_elements, right_elements):
                            assignments.append((left, right))
                else:
                    for target in targets:
                        assignments.append((ast.unparse(target), ast.unparse(value)))

        return assignments
    except SyntaxError:
        print("Invalid Python code.")
        return []


class Node:
    def __init__(self, expr, indent, space):
        self.expr = expr
        self.indent = indent
        self.space = space
        self.out_num = 0
        strings = extract_strings_from_code(expr)
        for s in strings:
            for c in s:
                if c in ['*', '.']:
                    self.out_num += 1
        self.children = [ ]

    def print_node(self, g_space):
        print(f"expr: {self.expr}")
        print(f"indent: {self.indent}")
        print(f"space: {self.space}")
        print(f"g_space: {g_space}")
        print(f"out_num: {self.out_num}")
        print("-" * 20)


def get_space_from_key(x):
    x = str(x)
    space = {x: set() for x in range(k)}
    for c in x:
        if ord('A') <= ord(c) < ord('A') + k * u:
            space[(ord(c) - ord('A')) // u].add(c)
    if "else" in x:
        for z in range(k):
            if len(space[z]) != 0:
                space[z].add('*')
    return space


def calculate_space(x):
    return sum([len(x[i]) for i in range(k)])


def atom(x):
    if type(x) == tuple and len(x) == 2 and type(x[0]) == int and type(x[1]) == int:
        return True
    if type(x) == str and len(x) == 1:
        return True
    return not (hasattr(x, '__iter__') or '__getitem__' in dir(x))


def union_space(space1, space2):
    return {x: space1[x] | space2[x] for x in range(k)}


def calculate_estimate(code):

    code = remove_comments(code)

    dicts = extract_dicts_from_code(code)
    c_dict_n, c_dict_m = 0, 0
    saved_space = set( )
    for d in dicts:
        for key, value in d.items( ):
            space = get_space_from_key(key)
            if atom(value):
                inc = 1
            else:
                value = [v for v in value]
                while not all([atom(v) for v in value]):
                    n_value = [ ]
                    for v in value:
                        if not atom(v):
                            n_value.extend([x for x in v])
                    value = n_value
                inc = len(value)
            hashable_space = tuple(tuple(sorted(space[i])) for i in range(k))
            if hashable_space not in saved_space:
                saved_space.add(hashable_space)
                c_dict_n += calculate_space(space)
            c_dict_m += inc


    dict_lineno = find_dict_assignments(code)
    code = code.split("\n")
    code = "\n".join([code[i] for i in range(len(code)) if i not in dict_lineno])

    assignment = extract_assignments(code)
    assign_store = { }
    for l, r in assignment:
        if l not in assign_store:
            assign_store[l] = get_space_from_key(r)
        else:
            assign_store[l] = union_space(assign_store[l], get_space_from_key(r))
        for el in assign_store:
            if find_variable_in_code(r, el):
                assign_store[l] = union_space(assign_store[l], assign_store[el])

    root = Node("", -1, {x: set() for x in range(k)})
    node_stack = [root]

    if_stack = [(-1, {x: set() for x in range(k)})]

    code = code.split("\n")

    for x in code:
        x = x.rstrip()
        if not x:
            continue
        # indent is the spaces at the beginning of the line
        indent = len(x) - len(x.lstrip())
        x = x.lstrip()
        # extract component value and get the space
        strings = extract_strings_from_code(x)
        space = {x: set( ) for x in range(k)}
        for s in strings:
            for c in s:
                if ord('A') <= ord(c) < ord('A') + k * u:
                    space[(ord(c) - ord('A')) // u].add(c)
        for l in assign_store:
            if find_variable_in_code(x, l):
                space = union_space(space, assign_store[l])
        # if-elif-else block
        while indent < if_stack[-1][0]:
            if_stack.pop()
        if x.startswith("if"):
            if_stack.append((indent, space))
        elif x.startswith("elif"):
            if_stack[-1] = (indent, union_space(if_stack[-1][1], space))
        elif x.startswith("else"):
            if_space = if_stack[-1][1]
            space = {z: {'*'} if len(if_space[z]) != 0 else set() for z in range(k)}
        if "else" in x:
            for z in range(k):
                if len(space[z]) != 0:
                    space[z].add('*')
        # node and link
        node = Node(x, indent, space)
        while indent <= node_stack[-1].indent:
            node_stack.pop()
        node_stack[-1].children.append(node)
        node_stack.append(node)

    c_block_n = [ ]
    c_block_m = [ ]
    saved_space = set( )

    def dfs(x: Node, space):
        if x.out_num != 0:
            c_block_m.append(x.out_num)
        if not x.children:
            if x.out_num != 0:
                hashable_space = tuple(tuple(sorted(space[i])) for i in range(k))
                if hashable_space not in saved_space:
                    c_block_n.append(calculate_space(space))
                    saved_space.add(hashable_space)
        if x.children:
            for y in x.children:
                dfs(y, union_space(space, y.space))

    dfs(root, root.space)
    c_block_n = sum(c_block_n)
    c_block_m = sum(c_block_m)

    return c_dict_n, c_dict_m, c_block_n, c_block_m
