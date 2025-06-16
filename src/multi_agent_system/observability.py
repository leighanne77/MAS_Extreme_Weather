"""
Observability and Pattern Monitoring System for Multi-Agent Climate Risk Analysis

This module implements a comprehensive observability system for monitoring and analyzing
agent patterns, interactions, and error handling in the climate risk analysis system.

Key Components:
    - ObservabilityManager: High-level interface for system observability
    - PatternMonitor: Internal implementation for monitoring patterns
    - Checkpoint: System state checkpoint for recovery
    - ErrorContext: Error tracking and context
    - RecoveryStrategy: Error recovery strategies
    - InteractionMetrics: Agent interaction metrics
    - DecisionMetrics: Agent decision metrics
    - AgentPatterns: Agent-specific pattern tracking

Features:
    1. Pattern Monitoring:
       - Interaction pattern tracking
       - Decision pattern analysis
       - Error pattern detection
       - Token usage monitoring
       - Context size tracking
    
    2. Checkpointing:
       - System state snapshots
       - Automatic checkpoint creation
       - Checkpoint restoration
       - State recovery
    
    3. Error Handling:
       - Error severity classification
       - Error context tracking
       - Recovery strategy management
       - Retry mechanism control
    
    4. Metrics Collection:
       - Interaction metrics
       - Decision metrics
       - Error metrics
       - Performance metrics
    
    5. Pattern Analysis:
       - Pattern identification
       - Trend analysis
       - Optimization suggestions
       - Performance insights

Dependencies:
    - aiofiles: For asynchronous file operations
    - logging: For system logging
    - datetime: For timestamp management
    - json: For data serialization

Example Usage:
    ```python
    # Initialize observability manager
    manager = ObservabilityManager(checkpoint_dir="checkpoints")
    
    # Track agent interaction
    metrics = manager.track_interaction(
        agent_id="risk_analyzer",
        interaction_type=InteractionType.SEQUENTIAL,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(seconds=5),
        success=True,
        token_usage={"input": 100, "output": 50},
        context_size=1024,
        compressed_size=512
    )
    
    # Create checkpoint
    checkpoint_id = await manager.create_checkpoint(
        agent_id="risk_analyzer",
        state={"status": "running"},
        context={"location": "New York"},
        tool_calls=[{"tool": "analyze_risks"}]
    )
    ```

Configuration:
    - CHECKPOINT_DIR: Directory for storing checkpoints
    - MAX_RETRIES: Maximum retry attempts
    - BACKOFF_FACTOR: Exponential backoff factor
    - TIMEOUT: Operation timeout
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from enum import Enum
import aiofiles
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Types of agent interactions in the system.
    
    This enum defines the different ways agents can interact with each other
    and the system.
    
    Values:
        SEQUENTIAL: Linear, one-after-another interactions
        PARALLEL: Concurrent, simultaneous interactions
        BRANCHING: Conditional, path-based interactions
        RECURSIVE: Self-referential, iterative interactions
    """
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BRANCHING = "branching"
    RECURSIVE = "recursive"

class DecisionPattern(Enum):
    """Types of agent decision patterns.
    
    This enum defines the different patterns agents use to make decisions
    and process information.
    
    Values:
        LINEAR: Straightforward, sequential decisions
        BRANCHING: Multiple-path, conditional decisions
        BACKTRACKING: Trial-and-error, reversible decisions
        OPTIMIZATION: Goal-oriented, efficiency-focused decisions
    """
    LINEAR = "linear"
    BRANCHING = "branching"
    BACKTRACKING = "backtracking"
    OPTIMIZATION = "optimization"

class ErrorSeverity(Enum):
    """Severity levels for system errors.
    
    This enum defines the different levels of error severity for
    proper error handling and recovery.
    
    Values:
        LOW: Minor issues, non-critical
        MEDIUM: Significant issues, requires attention
        HIGH: Major issues, impacts functionality
        CRITICAL: System-threatening issues
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Checkpoint:
    """Represents a system checkpoint with enhanced persistence capabilities."""
    id: str
    agent_id: str
    timestamp: datetime
    state: Dict[str, Any]
    context: Dict[str, Any]
    tool_calls: List[Dict[str, Any]]
    recovery_point: str  # Identifies the specific point in execution
    metadata: Dict[str, Any]  # Additional metadata for recovery

    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create checkpoint from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class ErrorContext:
    """Context information for system errors.
    
    This class captures detailed information about errors that occur
    in the system, aiding in debugging and recovery.
    
    Attributes:
        error_type (str): Type of error that occurred
        severity (ErrorSeverity): Severity level of the error
        timestamp (datetime): When the error occurred
        agent_id (str): ID of the agent that encountered the error
        tool_name (Optional[str]): Name of the tool that failed
        retry_count (int): Number of retry attempts
        context (Dict[str, Any]): Error context information
        stack_trace (Optional[str]): Error stack trace
        
    Example:
        ```python
        error = ErrorContext(
            error_type="timeout",
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            agent_id="risk_analyzer",
            tool_name="analyze_risks",
            retry_count=1,
            context={"location": "New York"},
            stack_trace="..."
        )
        ```
    """
    error_type: str
    severity: ErrorSeverity
    timestamp: datetime
    agent_id: str
    tool_name: Optional[str]
    retry_count: int
    context: Dict[str, Any]
    stack_trace: Optional[str]

@dataclass
class RecoveryStrategy:
    """Strategy for error recovery.
    
    This class defines how the system should handle and recover from
    different types of errors.
    
    Attributes:
        max_retries (int): Maximum number of retry attempts
        backoff_factor (float): Factor for exponential backoff
        timeout (float): Operation timeout in seconds
        fallback_actions (List[str]): List of fallback actions
        requires_rollback (bool): Whether state rollback is needed
        
    Example:
        ```python
        strategy = RecoveryStrategy(
            max_retries=3,
            backoff_factor=1.5,
            timeout=30.0,
            fallback_actions=["retry", "rollback", "skip"],
            requires_rollback=False
        )
        ```
    """
    max_retries: int
    backoff_factor: float
    timeout: float
    fallback_actions: List[str]
    requires_rollback: bool

@dataclass
class InteractionMetrics:
    """Metrics for agent interactions.
    
    This class tracks various metrics related to agent interactions
    for performance analysis and optimization.
    
    Attributes:
        agent_id (str): ID of the agent
        interaction_type (InteractionType): Type of interaction
        start_time (datetime): When the interaction started
        end_time (datetime): When the interaction ended
        success (bool): Whether the interaction succeeded
        token_usage (Dict[str, int]): Token usage statistics
        context_size (int): Size of the context
        compressed_size (int): Size after compression
        error_type (Optional[str]): Type of error if any
        retry_count (int): Number of retry attempts
        
    Example:
        ```python
        metrics = InteractionMetrics(
            agent_id="risk_analyzer",
            interaction_type=InteractionType.SEQUENTIAL,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=5),
            success=True,
            token_usage={"input": 100, "output": 50},
            context_size=1024,
            compressed_size=512
        )
        ```
    """
    agent_id: str
    interaction_type: InteractionType
    start_time: datetime
    end_time: datetime
    success: bool
    token_usage: Dict[str, int]
    context_size: int
    compressed_size: int
    error_type: Optional[str] = None
    retry_count: int = 0

@dataclass
class DecisionMetrics:
    """Metrics for agent decisions.
    
    This class tracks various metrics related to agent decision-making
    processes for analysis and optimization.
    
    Attributes:
        agent_id (str): ID of the agent
        pattern (DecisionPattern): Type of decision pattern
        start_time (datetime): When the decision process started
        end_time (datetime): When the decision process ended
        branches (int): Number of decision branches
        max_depth (int): Maximum depth of decision tree
        success_rate (float): Rate of successful decisions
        error_rate (float): Rate of decision errors
        optimization_score (float): Score for decision optimization
        
    Example:
        ```python
        metrics = DecisionMetrics(
            agent_id="risk_analyzer",
            pattern=DecisionPattern.BRANCHING,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=5),
            branches=3,
            max_depth=2,
            success_rate=0.8,
            error_rate=0.2,
            optimization_score=0.9
        )
        ```
    """
    agent_id: str
    pattern: DecisionPattern
    start_time: datetime
    end_time: datetime
    branches: int
    max_depth: int
    success_rate: float
    error_rate: float
    optimization_score: float

@dataclass
class AgentPatterns:
    """Patterns for an agent.
    
    This class maintains a history of patterns and metrics for a specific
    agent, providing insights into its behavior and performance.
    
    Attributes:
        agent_id (str): ID of the agent
        interaction_history (List[InteractionMetrics]): History of interactions
        decision_history (List[DecisionMetrics]): History of decisions
        error_history (List[ErrorContext]): History of errors
        checkpoints (List[Checkpoint]): History of checkpoints
        
    Example:
        ```python
        patterns = AgentPatterns(
            agent_id="risk_analyzer",
            interaction_history=[],
            decision_history=[],
            error_history=[],
            checkpoints=[]
        )
        ```
    """
    agent_id: str
    interaction_history: List[InteractionMetrics]
    decision_history: List[DecisionMetrics]
    error_history: List[ErrorContext]
    checkpoints: List[Checkpoint]

class PatternMonitor:
    """Internal implementation for monitoring patterns.
    
    This class handles the low-level pattern monitoring and tracking
    functionality, providing the core implementation for the
    ObservabilityManager.
    
    Attributes:
        checkpoint_dir (str): Directory for storing checkpoints
        agent_patterns (Dict[str, AgentPatterns]): Patterns for each agent
        interaction_patterns (Dict[InteractionType, int]): Interaction pattern counts
        decision_patterns (Dict[DecisionPattern, int]): Decision pattern counts
        error_patterns (Dict[str, int]): Error pattern counts
        retry_patterns (Dict[str, int]): Retry pattern counts
        token_usage_patterns (Dict[str, Dict[str, int]]): Token usage patterns
        context_patterns (Dict[str, Dict[str, int]]): Context patterns
        
    Example:
        ```python
        monitor = PatternMonitor(checkpoint_dir="checkpoints")
        ```
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """Initialize the pattern monitor.
        
        Args:
            checkpoint_dir (str): Directory for storing checkpoints
            
        Initialization:
            1. Creates checkpoint directory if it doesn't exist
            2. Initializes pattern tracking structures
            3. Sets up logging and monitoring
            
        Example:
            ```python
            monitor = PatternMonitor(checkpoint_dir="checkpoints")
            ```
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.agent_patterns: Dict[str, AgentPatterns] = {}
        self.interaction_patterns: Dict[str, int] = {}
        self.decision_patterns: Dict[str, int] = {}
        self.error_patterns: Dict[str, int] = {}
        self.retry_patterns: Dict[str, int] = {}
        self.token_usage_patterns: Dict[str, Dict[str, int]] = {}
        self.context_patterns: Dict[str, Dict[str, int]] = {}
        self._checkpoint_lock = asyncio.Lock()  # For concurrent checkpoint operations
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
    def _ensure_agent_patterns(self, agent_id: str) -> None:
        """Ensure agent patterns exist for the given agent.
        
        Args:
            agent_id (str): ID of the agent
            
        Pattern Initialization:
            1. Creates AgentPatterns if not exists
            2. Initializes empty history lists
            3. Sets up pattern tracking
            
        Example:
            ```python
            monitor._ensure_agent_patterns("risk_analyzer")
            ```
        """
        if agent_id not in self.agent_patterns:
            self.agent_patterns[agent_id] = AgentPatterns(
                agent_id=agent_id,
                interaction_history=[],
                decision_history=[],
                error_history=[],
                checkpoints=[]
            )

    async def _save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk asynchronously."""
        async with self._checkpoint_lock:
            checkpoint_path = self.checkpoint_dir / f"{checkpoint.id}.json"
            async with aiofiles.open(checkpoint_path, 'w') as f:
                await f.write(json.dumps(checkpoint.to_dict()))

    async def _load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint from disk asynchronously."""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if not checkpoint_path.exists():
            return None
        async with aiofiles.open(checkpoint_path, 'r') as f:
            data = json.loads(await f.read())
            return Checkpoint.from_dict(data)

    async def create_checkpoint(
        self,
        agent_id: str,
        state: Dict[str, Any],
        context: Dict[str, Any],
        tool_calls: List[Dict[str, Any]],
        recovery_point: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a checkpoint with enhanced persistence."""
        self._ensure_agent_patterns(agent_id)
        
        checkpoint = Checkpoint(
            id=f"checkpoint_{datetime.now().isoformat()}",
            agent_id=agent_id,
            timestamp=datetime.now(),
            state=state,
            context=context,
            tool_calls=tool_calls,
            recovery_point=recovery_point,
            metadata=metadata or {}
        )
        
        await self._save_checkpoint(checkpoint)
        return checkpoint.id

    async def restore_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Restore a checkpoint with enhanced error handling."""
        checkpoint = await self._load_checkpoint(checkpoint_id)
        if checkpoint:
            self._ensure_agent_patterns(checkpoint.agent_id)
        return checkpoint

    async def list_checkpoints(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available checkpoints, optionally filtered by agent_id."""
        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                async with aiofiles.open(checkpoint_file, 'r') as f:
                    data = json.loads(await f.read())
                    if agent_id is None or data['agent_id'] == agent_id:
                        checkpoints.append(data)
            except Exception as e:
                print(f"Error loading checkpoint {checkpoint_file}: {e}")
        return sorted(checkpoints, key=lambda x: x['timestamp'], reverse=True)

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint file."""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            return True
        return False

    async def cleanup_old_checkpoints(self, max_age_days: int = 7) -> int:
        """Clean up checkpoints older than max_age_days."""
        cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        deleted = 0
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                if checkpoint_file.stat().st_mtime < cutoff:
                    checkpoint_file.unlink()
                    deleted += 1
            except Exception as e:
                print(f"Error cleaning up checkpoint {checkpoint_file}: {e}")
        return deleted
    
    def track_error(
        self,
        agent_id: str,
        error_type: str,
        severity: ErrorSeverity,
        tool_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> ErrorContext:
        """Track an error occurrence.
        
        Args:
            agent_id (str): ID of the agent
            error_type (str): Type of error
            severity (ErrorSeverity): Error severity
            tool_name (Optional[str]): Name of the tool that failed
            context (Optional[Dict[str, Any]]): Error context
            stack_trace (Optional[str]): Error stack trace
            
        Returns:
            ErrorContext: Created error context
            
        Error Tracking:
            1. Creates error context
            2. Updates agent patterns
            3. Logs error details
            4. Returns error context
            
        Example:
            ```python
            error = monitor.track_error(
                agent_id="risk_analyzer",
                error_type="timeout",
                severity=ErrorSeverity.MEDIUM,
                tool_name="analyze_risks",
                context={"location": "New York"}
            )
            ```
        """
        self._ensure_agent_patterns(agent_id)
        error_context = ErrorContext(
            error_type=error_type,
            severity=severity,
            timestamp=datetime.now(),
            agent_id=agent_id,
            tool_name=tool_name,
            retry_count=0,
            context=context or {},
            stack_trace=stack_trace
        )
        self.agent_patterns[agent_id].error_history.append(error_context)
        
        return error_context
    
    def get_recovery_strategy(
        self,
        error_type: str,
        severity: ErrorSeverity
    ) -> RecoveryStrategy:
        """Get recovery strategy for an error.
        
        Args:
            error_type (str): Type of error
            severity (ErrorSeverity): Error severity
            
        Returns:
            RecoveryStrategy: Strategy for error recovery
            
        Strategy Selection:
            1. Determines error type
            2. Assesses severity
            3. Selects strategy
            4. Returns strategy
            
        Example:
            ```python
            strategy = monitor.get_recovery_strategy(
                error_type="timeout",
                severity=ErrorSeverity.MEDIUM
            )
            ```
        """
        # Use custom strategy if defined
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type]
        
        # Adjust default strategy based on severity
        strategy = self.recovery_strategies["default"]
        if severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy(
                max_retries=5,
                backoff_factor=2.0,
                timeout=60.0,
                fallback_actions=["rollback", "retry", "skip"],
                requires_rollback=True
            )
        elif severity == ErrorSeverity.HIGH:
            return RecoveryStrategy(
                max_retries=4,
                backoff_factor=1.8,
                timeout=45.0,
                fallback_actions=["retry", "rollback", "skip"],
                requires_rollback=True
            )
        elif severity == ErrorSeverity.MEDIUM:
            return RecoveryStrategy(
                max_retries=3,
                backoff_factor=1.5,
                timeout=30.0,
                fallback_actions=["retry", "skip", "rollback"],
                requires_rollback=False
            )
        else:  # LOW severity
            return RecoveryStrategy(
                max_retries=2,
                backoff_factor=1.2,
                timeout=15.0,
                fallback_actions=["retry", "skip"],
                requires_rollback=False
            )
    
    async def handle_error(
        self,
        agent_id: str,
        error_type: str,
        severity: ErrorSeverity,
        tool_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle an error occurrence.
        
        Args:
            agent_id (str): ID of the agent
            error_type (str): Type of error
            severity (ErrorSeverity): Error severity
            tool_name (Optional[str]): Name of the tool that failed
            context (Optional[Dict[str, Any]]): Error context
            stack_trace (Optional[str]): Error stack trace
            
        Returns:
            Dict[str, Any]: Error handling result
            
        Error Handling:
            1. Tracks error
            2. Gets recovery strategy
            3. Applies strategy
            4. Returns result
            
        Example:
            ```python
            result = await monitor.handle_error(
                agent_id="risk_analyzer",
                error_type="timeout",
                severity=ErrorSeverity.MEDIUM,
                tool_name="analyze_risks"
            )
            ```
        """
        # Track error
        error_context = self.track_error(
            agent_id=agent_id,
            error_type=error_type,
            severity=severity,
            tool_name=tool_name,
            context=context,
            stack_trace=stack_trace
        )
        
        # Get recovery strategy
        strategy = self.get_recovery_strategy(error_type, severity)
        
        # Find latest checkpoint if rollback needed
        latest_checkpoint = None
        if strategy.requires_rollback:
            checkpoints = self.agent_patterns[agent_id].checkpoints
            if checkpoints:
                latest_checkpoint = checkpoints[-1]
        
        # Create recovery plan
        recovery_plan = {
            "error_context": asdict(error_context),
            "recovery_strategy": asdict(strategy),
            "latest_checkpoint": asdict(latest_checkpoint) if latest_checkpoint else None,
            "suggested_actions": strategy.fallback_actions,
            "requires_rollback": strategy.requires_rollback,
            "max_retries": strategy.max_retries,
            "timeout": strategy.timeout
        }
        
        return recovery_plan
    
    def track_interaction(
        self,
        agent_id: str,
        interaction_type: InteractionType,
        start_time: datetime,
        end_time: datetime,
        success: bool,
        token_usage: Dict[str, int],
        context_size: int,
        compressed_size: int,
        error_type: Optional[str] = None,
        retry_count: int = 0
    ) -> InteractionMetrics:
        """Track an agent interaction.
        
        Args:
            agent_id (str): ID of the agent
            interaction_type (InteractionType): Type of interaction
            start_time (datetime): When the interaction started
            end_time (datetime): When the interaction ended
            success (bool): Whether the interaction succeeded
            token_usage (Dict[str, int]): Token usage statistics
            context_size (int): Size of the context
            compressed_size (int): Size after compression
            error_type (Optional[str]): Type of error if any
            retry_count (int): Number of retry attempts
            
        Returns:
            InteractionMetrics: Created interaction metrics
            
        Interaction Tracking:
            1. Creates metrics
            2. Updates agent patterns
            3. Logs interaction
            4. Returns metrics
            
        Example:
            ```python
            metrics = monitor.track_interaction(
                agent_id="risk_analyzer",
                interaction_type=InteractionType.SEQUENTIAL,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(seconds=5),
                success=True,
                token_usage={"input": 100, "output": 50},
                context_size=1024,
                compressed_size=512
            )
            ```
        """
        self._ensure_agent_patterns(agent_id)
        metrics = InteractionMetrics(
            agent_id=agent_id,
            interaction_type=interaction_type,
            start_time=start_time,
            end_time=end_time,
            success=success,
            token_usage=token_usage,
            context_size=context_size,
            compressed_size=compressed_size,
            error_type=error_type,
            retry_count=retry_count
        )
        self.agent_patterns[agent_id].interaction_history.append(metrics)
        
        return metrics
    
    def track_decision(
        self,
        agent_id: str,
        pattern: DecisionPattern,
        start_time: datetime,
        end_time: datetime,
        branches: int,
        max_depth: int,
        success_rate: float,
        error_rate: float,
        optimization_score: float
    ) -> DecisionMetrics:
        """Track an agent decision.
        
        Args:
            agent_id (str): ID of the agent
            pattern (DecisionPattern): Type of decision pattern
            start_time (datetime): When the decision started
            end_time (datetime): When the decision ended
            branches (int): Number of decision branches
            max_depth (int): Maximum depth of decision tree
            success_rate (float): Rate of successful decisions
            error_rate (float): Rate of decision errors
            optimization_score (float): Score for decision optimization
            
        Returns:
            DecisionMetrics: Created decision metrics
            
        Decision Tracking:
            1. Creates metrics
            2. Updates agent patterns
            3. Logs decision
            4. Returns metrics
            
        Example:
            ```python
            metrics = monitor.track_decision(
                agent_id="risk_analyzer",
                pattern=DecisionPattern.BRANCHING,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(seconds=5),
                branches=3,
                max_depth=2,
                success_rate=0.8,
                error_rate=0.2,
                optimization_score=0.9
            )
            ```
        """
        self._ensure_agent_patterns(agent_id)
        metrics = DecisionMetrics(
            agent_id=agent_id,
            pattern=pattern,
            start_time=start_time,
            end_time=end_time,
            branches=branches,
            max_depth=max_depth,
            success_rate=success_rate,
            error_rate=error_rate,
            optimization_score=optimization_score
        )
        self.agent_patterns[agent_id].decision_history.append(metrics)
        
        return metrics
    
    def get_agent_patterns(self, agent_id: str) -> Optional[AgentPatterns]:
        """Get patterns for a specific agent.
        
        Args:
            agent_id (str): ID of the agent
            
        Returns:
            Optional[AgentPatterns]: Agent patterns if found, None otherwise
        """
        self._ensure_agent_patterns(agent_id)
        return self.agent_patterns.get(agent_id)
    
    def get_interaction_patterns(self) -> Dict[InteractionType, int]:
        """Get interaction pattern statistics.
        
        Returns:
            Dict[InteractionType, int]: Count of each interaction type
            
        Pattern Analysis:
            1. Aggregates interaction data
            2. Counts pattern types
            3. Returns statistics
            
        Example:
            ```python
            patterns = monitor.get_interaction_patterns()
            print(f"Sequential interactions: {patterns[InteractionType.SEQUENTIAL]}")
            ```
        """
        patterns = {t: 0 for t in InteractionType}
        for agent in self.agent_patterns.values():
            for interaction in agent.interaction_history:
                patterns[interaction.interaction_type] += 1
        return patterns
    
    def get_decision_patterns(self) -> Dict[DecisionPattern, int]:
        """Get decision pattern statistics.
        
        Returns:
            Dict[DecisionPattern, int]: Count of each decision pattern
            
        Pattern Analysis:
            1. Aggregates decision data
            2. Counts pattern types
            3. Returns statistics
            
        Example:
            ```python
            patterns = monitor.get_decision_patterns()
            print(f"Branching decisions: {patterns[DecisionPattern.BRANCHING]}")
            ```
        """
        patterns = {p: 0 for p in DecisionPattern}
        for agent in self.agent_patterns.values():
            for decision in agent.decision_history:
                patterns[decision.pattern] += 1
        return patterns
    
    def get_error_patterns(self) -> Dict[str, int]:
        """Get error pattern statistics.
        
        Returns:
            Dict[str, int]: Count of each error type
            
        Pattern Analysis:
            1. Aggregates error data
            2. Counts error types
            3. Returns statistics
            
        Example:
            ```python
            patterns = monitor.get_error_patterns()
            print(f"Timeout errors: {patterns['timeout']}")
            ```
        """
        patterns = {}
        for agent in self.agent_patterns.values():
            for error in agent.error_history:
                patterns[error.error_type] = patterns.get(error.error_type, 0) + 1
        return patterns
    
    def get_retry_patterns(self) -> Dict[str, int]:
        """Get retry pattern statistics.
        
        Returns:
            Dict[str, int]: Count of retries by error type
            
        Pattern Analysis:
            1. Aggregates retry data
            2. Counts retry types
            3. Returns statistics
            
        Example:
            ```python
            patterns = monitor.get_retry_patterns()
            print(f"Timeout retries: {patterns['timeout']}")
            ```
        """
        patterns = {}
        for agent in self.agent_patterns.values():
            for error in agent.error_history:
                if error.retry_count > 0:
                    patterns[error.error_type] = patterns.get(error.error_type, 0) + error.retry_count
        return patterns
    
    def get_token_usage_patterns(self) -> Dict[str, Dict[str, int]]:
        """Get token usage pattern statistics.
        
        Returns:
            Dict[str, Dict[str, int]]: Token usage by agent and type
            
        Pattern Analysis:
            1. Aggregates token data
            2. Calculates usage patterns
            3. Returns statistics
            
        Example:
            ```python
            patterns = monitor.get_token_usage_patterns()
            print(f"Risk analyzer input tokens: {patterns['risk_analyzer']['input']}")
            ```
        """
        patterns = {
            "input": {t.value: 0 for t in InteractionType},
            "output": {t.value: 0 for t in InteractionType}
        }
        for agent in self.agent_patterns.values():
            for interaction in agent.interaction_history:
                patterns["input"][interaction.interaction_type.value] += interaction.token_usage.get("input", 0)
                patterns["output"][interaction.interaction_type.value] += interaction.token_usage.get("output", 0)
        return patterns
    
    def get_context_patterns(self) -> Dict[str, Dict[str, int]]:
        """Get context pattern statistics.
        
        Returns:
            Dict[str, Dict[str, int]]: Context size patterns by agent
        
        Pattern Analysis:
            1. Aggregates context data
            2. Calculates size patterns
            3. Returns statistics
            
        Example:
            ```python
            patterns = monitor.get_context_patterns()
            print(f"Risk analyzer context size: {patterns['risk_analyzer']['size']}")
            ```
        """
        patterns = {
            t.value: {"original": 0, "compressed": 0}
            for t in InteractionType
        }
        for agent in self.agent_patterns.values():
            for interaction in agent.interaction_history:
                patterns[interaction.interaction_type.value]["original"] += interaction.context_size
                patterns[interaction.interaction_type.value]["compressed"] += interaction.compressed_size
        return patterns
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze all system patterns.
        
        Returns:
            Dict[str, Any]: Comprehensive pattern analysis
            
        Pattern Analysis:
            1. Aggregates all pattern data
            2. Calculates statistics
            3. Identifies trends
            4. Returns analysis
            
        Example:
            ```python
            analysis = monitor.analyze_patterns()
            print(f"Most common interaction: {analysis['common_interaction']}")
            ```
        """
        interaction_patterns = self.get_interaction_patterns()
        decision_patterns = self.get_decision_patterns()
        error_patterns = self.get_error_patterns()
        retry_patterns = self.get_retry_patterns()
        token_patterns = self.get_token_usage_patterns()
        context_patterns = self.get_context_patterns()
        
        total_interactions = sum(interaction_patterns.values())
        total_decisions = sum(decision_patterns.values())
        total_errors = sum(error_patterns.values())
        total_retries = sum(retry_patterns.values())
        
        total_input_tokens = sum(token_patterns["input"].values())
        total_output_tokens = sum(token_patterns["output"].values())
        
        total_original_context = sum(p["original"] for p in context_patterns.values())
        total_compressed_context = sum(p["compressed"] for p in context_patterns.values())
        
        return {
            "interaction_patterns": {
                "total": total_interactions,
                "by_type": {t.value: c for t, c in interaction_patterns.items()}
            },
            "decision_patterns": {
                "total": total_decisions,
                "by_type": {p.value: c for p, c in decision_patterns.items()}
            },
            "error_analysis": {
                "total_errors": total_errors,
                "by_type": error_patterns,
                "total_retries": total_retries,
                "retry_patterns": retry_patterns
            },
            "token_usage": {
                "total": total_input_tokens + total_output_tokens,
                "input": total_input_tokens,
                "output": total_output_tokens,
                "by_type": token_patterns
            },
            "context_compression": {
                "total_original": total_original_context,
                "total_compressed": total_compressed_context,
                "compression_ratio": total_compressed_context / total_original_context if total_original_context > 0 else 0,
                "by_type": context_patterns
            }
        }

class ObservabilityManager:
    """High-level interface for system observability and monitoring.
    
    This class provides a comprehensive interface for monitoring and analyzing
    agent patterns, interactions, and error handling in the climate risk analysis system.
    
    It wraps the PatternMonitor implementation while providing a cleaner, more
    focused API for the rest of the system.
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """Initialize the observability manager.
        
        Args:
            checkpoint_dir (str): Directory for storing checkpoints
        """
        self._pattern_monitor = PatternMonitor(checkpoint_dir)
    
    async def create_checkpoint(
        self,
        agent_id: str,
        state: Dict[str, Any],
        context: Dict[str, Any],
        tool_calls: List[Dict[str, Any]]
    ) -> str:
        """Create a system checkpoint.
        
        Args:
            agent_id (str): ID of the agent being checkpointed
            state (Dict[str, Any]): Current agent state
            context (Dict[str, Any]): Current context
            tool_calls (List[Dict[str, Any]]): Recent tool calls
            
        Returns:
            str: Checkpoint ID
        """
        return await self._pattern_monitor.create_checkpoint(
            agent_id, state, context, tool_calls
        )
    
    async def restore_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Restore a system checkpoint.
        
        Args:
            checkpoint_id (str): ID of the checkpoint to restore
            
        Returns:
            Optional[Checkpoint]: Restored checkpoint if successful
        """
        return await self._pattern_monitor.restore_checkpoint(checkpoint_id)
    
    def track_error(
        self,
        agent_id: str,
        error_type: str,
        severity: ErrorSeverity,
        tool_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> ErrorContext:
        """Track system errors.
        
        Args:
            agent_id (str): ID of the agent that encountered the error
            error_type (str): Type of error
            severity (ErrorSeverity): Error severity level
            tool_name (Optional[str]): Name of the tool that failed
            context (Optional[Dict[str, Any]]): Error context
            stack_trace (Optional[str]): Error stack trace
            
        Returns:
            ErrorContext: Error context information
        """
        return self._pattern_monitor.track_error(
            agent_id, error_type, severity, tool_name, context, stack_trace
        )
    
    def get_recovery_strategy(
        self,
        error_type: str,
        severity: ErrorSeverity
    ) -> RecoveryStrategy:
        """Get recovery strategy for an error.
        
        Args:
            error_type (str): Type of error
            severity (ErrorSeverity): Error severity level
            
        Returns:
            RecoveryStrategy: Recovery strategy
        """
        return self._pattern_monitor.get_recovery_strategy(error_type, severity)
    
    async def handle_error(
        self,
        agent_id: str,
        error_type: str,
        severity: ErrorSeverity,
        tool_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle system errors.
        
        Args:
            agent_id (str): ID of the agent that encountered the error
            error_type (str): Type of error
            severity (ErrorSeverity): Error severity level
            tool_name (Optional[str]): Name of the tool that failed
            context (Optional[Dict[str, Any]]): Error context
            stack_trace (Optional[str]): Error stack trace
            
        Returns:
            Dict[str, Any]: Error handling result
        """
        return await self._pattern_monitor.handle_error(
            agent_id, error_type, severity, tool_name, context, stack_trace
        )
    
    def track_interaction(
        self,
        agent_id: str,
        interaction_type: InteractionType,
        start_time: datetime,
        end_time: datetime,
        success: bool,
        token_usage: Dict[str, int],
        context_size: int,
        compressed_size: int,
        error_type: Optional[str] = None,
        retry_count: int = 0
    ) -> InteractionMetrics:
        """Track agent interactions.
        
        Args:
            agent_id (str): ID of the agent
            interaction_type (InteractionType): Type of interaction
            start_time (datetime): When the interaction started
            end_time (datetime): When the interaction ended
            success (bool): Whether the interaction succeeded
            token_usage (Dict[str, int]): Token usage statistics
            context_size (int): Size of the context
            compressed_size (int): Size after compression
            error_type (Optional[str]): Type of error if any
            retry_count (int): Number of retry attempts
            
        Returns:
            InteractionMetrics: Interaction metrics
        """
        return self._pattern_monitor.track_interaction(
            agent_id, interaction_type, start_time, end_time, success,
            token_usage, context_size, compressed_size, error_type, retry_count
        )
    
    def track_decision(
        self,
        agent_id: str,
        pattern: DecisionPattern,
        start_time: datetime,
        end_time: datetime,
        branches: int,
        max_depth: int,
        success_rate: float,
        error_rate: float,
        optimization_score: float
    ) -> DecisionMetrics:
        """Track agent decisions.
        
        Args:
            agent_id (str): ID of the agent
            pattern (DecisionPattern): Type of decision pattern
            start_time (datetime): When the decision process started
            end_time (datetime): When the decision process ended
            branches (int): Number of decision branches
            max_depth (int): Maximum depth of decision tree
            success_rate (float): Rate of successful decisions
            error_rate (float): Rate of decision errors
            optimization_score (float): Score for decision optimization
            
        Returns:
            DecisionMetrics: Decision metrics
        """
        return self._pattern_monitor.track_decision(
            agent_id, pattern, start_time, end_time, branches,
            max_depth, success_rate, error_rate, optimization_score
        )
    
    def get_agent_patterns(self, agent_id: str) -> Optional[AgentPatterns]:
        """Get patterns for a specific agent.
        
        Args:
            agent_id (str): ID of the agent
            
        Returns:
            Optional[AgentPatterns]: Agent patterns if found, None otherwise
        """
        self._pattern_monitor._ensure_agent_patterns(agent_id)
        return self._pattern_monitor.agent_patterns.get(agent_id)
    
    def get_interaction_patterns(self) -> Dict[InteractionType, int]:
        """Get interaction patterns.
        
        Returns:
            Dict[InteractionType, int]: Interaction pattern counts
        """
        return self._pattern_monitor.get_interaction_patterns()
    
    def get_decision_patterns(self) -> Dict[DecisionPattern, int]:
        """Get decision patterns.
        
        Returns:
            Dict[DecisionPattern, int]: Decision pattern counts
        """
        return self._pattern_monitor.get_decision_patterns()
    
    def get_error_patterns(self) -> Dict[str, int]:
        """Get error patterns.
        
        Returns:
            Dict[str, int]: Error pattern counts
        """
        return self._pattern_monitor.get_error_patterns()
    
    def get_retry_patterns(self) -> Dict[str, int]:
        """Get retry patterns.
        
        Returns:
            Dict[str, int]: Retry pattern counts
        """
        return self._pattern_monitor.get_retry_patterns()
    
    def get_token_usage_patterns(self) -> Dict[str, Dict[str, int]]:
        """Get token usage patterns.
        
        Returns:
            Dict[str, Dict[str, int]]: Token usage pattern statistics
        """
        return self._pattern_monitor.get_token_usage_patterns()
    
    def get_context_patterns(self) -> Dict[str, Dict[str, int]]:
        """Get context patterns.
        
        Returns:
            Dict[str, Dict[str, int]]: Context pattern statistics
        """
        return self._pattern_monitor.get_context_patterns()
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze system patterns.
        
        Returns:
            Dict[str, Any]: Pattern analysis results
        """
        return self._pattern_monitor.analyze_patterns() 