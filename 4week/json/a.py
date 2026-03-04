import importlib
import sys

def classify(module_path, attr_name):
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return "MODULE_NOT_FOUND"
    if not hasattr(module, attr_name):
        return "ATTRIBUTE_NOT_FOUND"
    attr = getattr(module, attr_name)
    if callable(attr):
        return "CALLABLE"
    else:
        return "VALUE"
n = int(sys.stdin.readline().strip())
for _ in range(n):
    module_path, attr_name = sys.stdin.readline().strip().split()
    print(classify(module_path, attr_name))