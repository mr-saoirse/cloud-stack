from loguru import logger
import os
from typing import Union, Optional, List
from pydantic import BaseModel
import re
from monolith.common import ArgoClient

API_HOME = os.environ.get("PLATFORM_API_HOME", "http://localhost:5001")
EVENT_TYPE = Union[BaseModel, List[BaseModel], dict, List[dict]]

def _argo_submit(name:str, event: Optional[EVENT_TYPE]=None, parallel=True, context=None):
    """
    wrapper to submit the workflow. simple case assume parallel for generate-map-reduce
    in practice we would inspect the module to decide if that is the right thing to do
    for example, if the function is a handler, we could just set parallel=False
    we could use other logic and attributes to decide...
    """
    return ArgoClient().submit_map_flow(name, event=event, parallel=parallel, context=context)

def invoke_task(name:str, event: Optional[EVENT_TYPE]=None, options: Optional[dict]=None):
    """
    params:
    name: The name must uniquely identify a module or function
    event: the event can be any payload. This should be a Pydantic object or array of such
    id: the id is usually a k8s compatible unique name for workflow jobs
    
    returns:
    probably a response type 
    """
    
    """
    for the generator use case we will only implement calling by name as we will consume event data from kafka
    """

    logger.debug(f"We will invoke a remote uri to run the job {name}")
    
    return _argo_submit(name, event=event,context=options)