import wrapt
import functools
from pydantic import BaseModel
from typing import Optional, Union, Any
from collections.abc import Iterator
from inspect import getmembers, isfunction
import pkgutil
import sys
import importlib
from loguru import logger
from monolith import modules as MODULE

class CallableModule(BaseModel):
    name: str
    namespace: Optional[str]
    fullname: Optional[str]
    interval_hours: Union[Any,None] = None
    interval_minutes: Union[Any,None] = None
    interval_days: Union[Any,None] = None   
    options: Optional[dict] = None
    
def deployment_attributes(memory=None, sem_var=None, cron=None, on_error=None, interval_minutes=None, interval_hours=None, namespace=None):
    def _adorned(func):     
        func.meta = {
            "memory": memory,
            "sem_var": sem_var,
            "memory": memory,
            "cron": cron,
            "interval_minutes": interval_minutes,
            "interval_hours": interval_hours,
            "namespace": namespace,
            
        }
        return func
    return _adorned

def deployment(obj=None): 
    """
    A deployment wrapper to work with K8s tooling such as argo workflows
    """
    # to allow with or without args we trap the case where there is no obj
    if obj is None:
        return functools.partial(deployment)
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        try:
            data = wrapped(*args, **kwargs)
            return data
        except:
            pass
        finally:
            pass
    return wrapper(obj)

def _get_module_callables(name):
    MODULE_ROOT = 'monolith.modules.'
    fname = name.replace(MODULE_ROOT,'')
    namespace = f".".join(fname.split('.')[:2])        
    for name, op in getmembers(importlib.import_module(fname), isfunction):
        if name in ['generator', 'handler']:
            d = {
                "name": f"{namespace}.{name}",
                "fullname": f"{fname}.{name}",
                "namespace": namespace,
                "options": {} if not hasattr(op,'meta') else op.meta,
            }
            if hasattr(op,'meta'):
                #take non none values to override
                d.update({k:v for k,v in op.meta.items() if v is not None})
            yield CallableModule(**d)
            
def load_op(module, op='handler', default = None):
    """
    much of this library depends on simple conventions so can be improved
    in this case we MUST be able to find the modules 
     'monolith.modules.<NAMESPACE>.<op>'
    these ops currently live in the controller so a test is that they are exposed to the module surface
    or we do more interesting inspection of modules 
    """
    
    def default_handler(event, **kwargs):
        """
        this is the default when the handler does not provide a handler
        """
        logger.info(f"<<<< Proxy handling for {module}.{op} >>>>")
        logger.info(f"processing {event}, {kwargs}")
        return {}
        
    
    MODULE_ROOT = 'monolith.modules.'
    module = module.replace(MODULE_ROOT,'')
    module = f"{MODULE_ROOT}{module}"
    try:
        logger.debug(f"Loading function {op} from {module}")
        return getattr(__import__(module, fromlist=[op]), op)
    except Exception as ex:
        logger.warning(f"Failed loading function {op} from {module} - {repr(ex)}")
        if default:
            return default
        return default_handler
                
def inspect_modules(filter=None)-> Iterator[CallableModule]:
    """
    We go through looking for callable methods in our modules obeying some norms
    """
    path_list = []
    spec_list = []
 
    for importer, modname, ispkg in pkgutil.walk_packages(MODULE.__path__):
        import_path = f"{MODULE.__name__}.{modname}"
        if ispkg:
            spec = pkgutil._get_spec(importer, modname)
            importlib._bootstrap._load(spec)
            spec_list.append(spec)
        else:
            path_list.append(import_path)
            logger.debug(import_path)
            for mod in _get_module_callables(import_path):
                yield mod 
                
    for spec in spec_list:
        del sys.modules[spec.name]