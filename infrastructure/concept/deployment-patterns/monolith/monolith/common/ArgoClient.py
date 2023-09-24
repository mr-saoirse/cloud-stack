"""
placeholder for the argo client for the workflow dispatcher
this is part of the infra fastAPI app (which also includes some workflows)

example all is the kafka map-reduce consumer
the fast api accepts jobs of generic type topic and json -> we post
when consuming we load the types in the generic generator and then map and dispatch the handlers in the module

"""

import json
import yaml
from typing import Union, Optional
from pydantic import BaseModel
import os
import argo_workflows
from argo_workflows.api import workflow_service_api
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_create_request import (
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
)
from loguru import logger
import re
from datetime import datetime

LOCAL_WORKFLOW_PATH = os.environ.get("WORKFLOW_DIR", "/app/workflows")

class ArgoClient:
    def __init__(self):
        configuration = argo_workflows.Configuration(host= os.environ.get('ARGO_SERVER', 
                                                                          "http://127.0.0.1:2746"))
        configuration.verify_ssl = False
        api_client = argo_workflows.ApiClient(configuration)
        self._api_instance = workflow_service_api.WorkflowServiceApi(api_client)
        
    def submit_map_flow(self, name:str,  event : Optional[Union[dict,BaseModel]], parallel=True, context: Optional[dict]=None):
        """
        This submits a specific workflow with some hard coded assumptions about the structure
        it would not be hard to generalize but I have found this simple one fairly reusable
        """
        if hasattr(event, 'dict'):
            event = event.dict()
            
        """
        HARD CODED INDICES - TO GENERALIZE CREATE TYPED WORKFLOWS
        """
        EVENT_PARAM_INDEX = 0
        GENERATOR_FLAG_INDEX = 2
        OP_PARAM_INDEX = 4
        EVENT_PARAM_INDEX = 5
        
        MAP_STEP_INDEX = 2  
        DAG_TEMPLATE_INDEX= 0
        
        with open(f"{LOCAL_WORKFLOW_PATH}/map-reduce-flow.yaml") as f: 
            manifest = yaml.safe_load(f)
        
        ######################         MOD ARGS     ####################################
        #safety - event if None is passed we try the name. always k8-ify and try submit even if not unique
        ts = datetime.utcnow().isoformat().split('.')[0].replace('T','-')
        k8s_id =  re.sub(r'[^a-z0-9\-]+', '-',  f"{name}-{ts}".lower())
        
        logger.debug(f"submitting {k8s_id}")
        manifest['metadata']['name'] = k8s_id
        manifest['spec']['arguments']['parameters'][OP_PARAM_INDEX]['value'] = name
        if event:
           manifest['spec']['arguments']['parameters'][EVENT_PARAM_INDEX]['value'] = json.dumps(event)
        if parallel:
            manifest['spec']['arguments']['parameters'][GENERATOR_FLAG_INDEX]['value'] = True
        else:
            manifest['spec']['templates'][DAG_TEMPLATE_INDEX]['steps'].pop(MAP_STEP_INDEX)
        ##################################################################################
            
        api_response = self._api_instance.create_workflow(
            namespace="argo",
            body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=manifest, _check_type=False),
            _check_return_type=False)
        
        return api_response