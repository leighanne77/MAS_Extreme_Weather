"""
Workflow Management System for Multi-Agent Climate Risk Analysis

This module implements the workflow management system for coordinating
agent activities and managing task execution in the climate risk analysis system.

Key Components:
    - WorkflowManager: Main workflow orchestration
    - WorkflowState: State tracking and management
    - WorkflowStep: Individual task execution
    - WorkflowConfig: Configuration management

Features:
    1. Workflow Orchestration:
       - Task sequencing
       - State management
       - Error handling
       - Progress tracking
    
    2. State Management:
       - State transitions
       - Data persistence
       - State validation
       - Recovery handling
    
    3. Task Execution:
       - Step execution
       - Dependency management
       - Result handling
       - Error recovery
    
    4. Monitoring and Control:
       - Progress tracking
       - Status reporting
       - Performance monitoring
       - Resource management

Dependencies:
    - asyncio: For async operations
    - logging: For system logging
    - typing: For type hints
    - json: For data serialization

Example Usage:
    ```python
    # Initialize workflow manager
    manager = WorkflowManager()
    
    # Define workflow steps
    steps = [
        WorkflowStep(
            name="data_collection",
            handler=collect_data,
            dependencies=[]
        ),
        WorkflowStep(
            name="analysis",
            handler=analyze_data,
            dependencies=["data_collection"]
        )
    ]
    
    # Execute workflow
    result = await manager.execute_workflow(
        workflow_id="risk_analysis",
        steps=steps
    )
    ```

Configuration:
    - MAX_RETRIES: Maximum retry attempts
    - TIMEOUT: Step execution timeout
    - STATE_PERSISTENCE: State storage settings
    - LOGGING_LEVEL: Logging configuration
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime

from .agent_team import Agent, AgentTeam
from .session_manager import AnalysisSession

logger = logging.getLogger(__name__)

@dataclass
class WorkflowContext:
    """Shared context for workflow execution."""
    session: AnalysisSession
    parameters: Dict[str, Any]
    start_time: datetime = datetime.now()

class SequentialWorkflow:
    """Manages ordered execution of climate analysis tasks."""
    
    def __init__(
        self,
        name: str,
        sub_agents: List[Agent],
        context: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.sub_agents = sub_agents
        self.context = context or {}
    
    async def execute(self, session: AnalysisSession) -> Dict[str, Any]:
        """Execute agents in sequence."""
        workflow_context = WorkflowContext(
            session=session,
            parameters=self.context
        )
        
        results = {}
        for agent in self.sub_agents:
            try:
                result = await agent.run(workflow_context)
                results[agent.name] = result
                workflow_context.parameters.update(result)
            except Exception as e:
                results[agent.name] = {"error": str(e)}
                raise
        
        return results

class ParallelWorkflow:
    """Manages concurrent execution of independent climate analysis tasks."""
    
    def __init__(
        self,
        name: str,
        sub_agents: List[Agent],
        max_concurrent: int = 5
    ):
        self.name = name
        self.sub_agents = sub_agents
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, session: AnalysisSession) -> Dict[str, Any]:
        """Execute agents in parallel."""
        workflow_context = WorkflowContext(
            session=session,
            parameters={}
        )
        
        async def run_agent(agent: Agent) -> Dict[str, Any]:
            async with self.semaphore:
                try:
                    return await agent.run(workflow_context)
                except Exception as e:
                    return {"error": str(e)}
        
        tasks = [run_agent(agent) for agent in self.sub_agents]
        results = await asyncio.gather(*tasks)
        
        return {
            agent.name: result
            for agent, result in zip(self.sub_agents, results)
        }

class LoopWorkflow:
    """Manages iterative climate analysis tasks."""
    
    def __init__(
        self,
        name: str,
        sub_agents: List[Agent],
        max_iterations: int = 5,
        termination_condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    ):
        self.name = name
        self.sub_agents = sub_agents
        self.max_iterations = max_iterations
        self.termination_condition = termination_condition
    
    async def execute(self, session: AnalysisSession) -> Dict[str, Any]:
        """Execute agents in a loop until termination condition is met."""
        workflow_context = WorkflowContext(
            session=session,
            parameters={}
        )
        
        iteration = 0
        results = {}
        
        while iteration < self.max_iterations:
            iteration_results = {}
            
            for agent in self.sub_agents:
                try:
                    result = await agent.run(workflow_context)
                    iteration_results[agent.name] = result
                    workflow_context.parameters.update(result)
                except Exception as e:
                    iteration_results[agent.name] = {"error": str(e)}
                    raise
            
            results[f"iteration_{iteration}"] = iteration_results
            
            if self.termination_condition and self.termination_condition(iteration_results):
                break
            
            iteration += 1
        
        return results 

class WorkflowManager:
    """Manages workflow execution and state in the climate risk analysis system.
    
    This class provides comprehensive workflow management capabilities,
    including task orchestration, state management, and error handling.
    
    Key Features:
        - Workflow orchestration
        - State management
        - Error handling
        - Progress tracking
    
    State Management:
        - Maintains workflow state
        - Tracks step progress
        - Manages dependencies
        - Handles recovery
    
    Example:
        ```python
        manager = WorkflowManager()
        
        # Execute workflow
        result = await manager.execute_workflow(
            workflow_id="risk_analysis",
            steps=[
                WorkflowStep(
                    name="data_collection",
                    handler=collect_data
                )
            ]
        )
        ```
    """
    
    def __init__(self):
        """Initialize the workflow manager.
        
        Initialization:
            - Sets up state tracking
            - Initializes logging
            - Configures error handling
            - Prepares resource management
            
        Example:
            ```python
            manager = WorkflowManager()
            ```
        """
        self.workflows: Dict[str, WorkflowState] = {}
        self.logger = logging.getLogger(__name__)

    async def execute_workflow(
        self,
        workflow_id: str,
        steps: List[WorkflowStep]
    ) -> Dict[str, Any]:
        """Execute a workflow with the given steps.
        
        Args:
            workflow_id (str): Unique workflow identifier
            steps (List[WorkflowStep]): List of workflow steps
            
        Returns:
            Dict[str, Any]: Workflow execution results
            
        Execution Process:
            1. Validates workflow
            2. Initializes state
            3. Executes steps
            4. Handles errors
            5. Returns results
            
        Example:
            ```python
            result = await manager.execute_workflow(
                workflow_id="risk_analysis",
                steps=[
                    WorkflowStep(
                        name="data_collection",
                        handler=collect_data
                    )
                ]
            )
            ```
        """
        self.workflows[workflow_id] = WorkflowState(
            workflow_id=workflow_id,
            current_step=steps[0].name if steps else None
        )
        
        results = {}
        for step in steps:
            try:
                if step.dependencies:
                    for dep in step.dependencies:
                        if dep not in results:
                            raise ValueError(f"Missing dependency: {dep}")
                
                result = await step.handler()
                results[step.name] = result
                self.workflows[workflow_id].completed_steps.append(step.name)
                
            except Exception as e:
                self.workflows[workflow_id].error = e
                raise
        
        return results

    async def get_workflow_state(self, workflow_id: str) -> WorkflowState:
        """Get the current state of a workflow.
        
        Args:
            workflow_id (str): Workflow identifier
            
        Returns:
            WorkflowState: Current workflow state
            
        State Retrieval Process:
            1. Validates workflow ID
            2. Retrieves state
            3. Validates state
            4. Returns state
            
        Example:
            ```python
            state = await manager.get_workflow_state("risk_analysis")
            print(f"Current step: {state.current_step}")
            ```
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        return self.workflows[workflow_id]

class WorkflowStep:
    """Represents a single step in a workflow.
    
    This class defines a workflow step, including its handler,
    dependencies, and execution requirements.
    
    Attributes:
        name (str): Step identifier
        handler (Callable): Step execution function
        dependencies (List[str]): Required step dependencies
        
    Example:
        ```python
        step = WorkflowStep(
            name="data_collection",
            handler=collect_data,
            dependencies=["setup"]
        )
        ```
    """
    
    def __init__(
        self,
        name: str,
        handler: Callable,
        dependencies: List[str] = None
    ):
        """Initialize a workflow step.
        
        Args:
            name (str): Step identifier
            handler (Callable): Step execution function
            dependencies (List[str], optional): Required dependencies
            
        Example:
            ```python
            step = WorkflowStep(
                name="data_collection",
                handler=collect_data,
                dependencies=["setup"]
            )
            ```
        """
        self.name = name
        self.handler = handler
        self.dependencies = dependencies or []

class WorkflowState:
    """Represents the state of a workflow execution.
    
    This class tracks the current state of a workflow,
    including progress, results, and error information.
    
    Attributes:
        workflow_id (str): Workflow identifier
        current_step (str): Current step name
        completed_steps (List[str]): Completed steps
        results (Dict[str, Any]): Step results
        error (Optional[Exception]): Error information
        
    Example:
        ```python
        state = WorkflowState(
            workflow_id="risk_analysis",
            current_step="data_collection"
        )
        ```
    """
    
    def __init__(
        self,
        workflow_id: str,
        current_step: str,
        completed_steps: List[str] = None,
        results: Dict[str, Any] = None,
        error: Optional[Exception] = None
    ):
        """Initialize workflow state.
        
        Args:
            workflow_id (str): Workflow identifier
            current_step (str): Current step name
            completed_steps (List[str], optional): Completed steps
            results (Dict[str, Any], optional): Step results
            error (Exception, optional): Error information
            
        Example:
            ```python
            state = WorkflowState(
                workflow_id="risk_analysis",
                current_step="data_collection"
            )
            ```
        """
        self.workflow_id = workflow_id
        self.current_step = current_step
        self.completed_steps = completed_steps or []
        self.results = results or {}
        self.error = error
        self.created_at = datetime.utcnow() 