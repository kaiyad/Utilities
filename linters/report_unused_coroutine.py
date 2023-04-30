import ast
import builtins
import os

from dataclasses import dataclass
# TODO: Map the async func calls to appropriate corouitnes
async_funcs = []
async_func_calls = []
func_calls = []

@dataclass
class FuncCall:
    name: str
    module: str
    lineno: int
    
    
def get_async_func_list(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            async_funcs.append(node.name)

def get_func_calls(module, tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name not in dir(builtins):
                    func_call = FuncCall(name=func_name, module=module, lineno=node.lineno)
                    func_calls.append(func_call)


def get_async_func_calls(module, tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Await):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    func_name = node.value.func.id
                    if func_name not in dir(builtins):
                        func_call = FuncCall(name=func_name, module=module, lineno=node.lineno)
                        async_func_calls.append(func_call)

def get_python_files(workspace):
    python_files = []
    for dirpath, dirnames, filenames in os.walk(workspace):
        if '.venv' in dirpath:
            continue
        for filename in filenames:
            if filename.endswith('.py'):
                python_files.append(os.path.join(dirpath, filename))
    return python_files

def main(workspace):
    modules = get_python_files(workspace)
    print(modules)
    for module in modules:
        with open(module, 'r') as mod:
            source = mod.read()
        
        tree = ast.parse(source)
        get_async_func_list(tree)
        get_func_calls(module, tree)
        get_async_func_calls(module, tree)
    
    print(func_calls)
    print(async_funcs)
    print(async_func_calls)
    regular_calls = [ func_call for func_call in func_calls if func_call not in async_func_calls ]
    for func in async_funcs:
        for func_call in regular_calls:
            if func in func_call.name:
                print(f"Missing Await: Mark '{func_call.name}' with 'await' in '{func_call.module}' at line number: {func_call.lineno}")

if __name__ == '__main__':
    workspace = input("Enter Workspace Path: ") or os.getcwd()
    main(workspace)
