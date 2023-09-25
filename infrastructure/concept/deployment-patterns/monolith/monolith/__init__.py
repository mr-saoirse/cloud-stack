"""
To simplify the code I use some conventions for what a module is
A module lives in modules/namespace/module_name
it contains schema/types
it contains a controller which contains one or more controllers 
for simplicity of discovery we surface the ops so they appear as namespace.module.op
"""

from pathlib import Path
from importlib import import_module
m = import_module("monolith")

MODULE_HOME =  Path(m.__file__).parent / 'modules'
