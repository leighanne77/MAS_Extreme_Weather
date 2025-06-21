"""
Agent communication module with A2A protocol and ADK features.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

from .a2a import A2AMessage, A2AMultiPartMessage, A2APart, create_request_message, create_response_message
from .a2a.enums import MessageType, Priority, StatusCode
from .a2a.router import A2AMessageRouter
from .a2a.content_handlers import content_handler_registry
from .utils.adk_features import MetricsCollector, CircuitBreaker, WorkerPool, Monitoring, Buffer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a message between agents with ADK features."""
    sender_id: str
    receiver_id: str
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Dict = None
    monitoring_enabled: bool = True
    metrics_collection: bool = True
    circuit_breaker: bool = True

class AgentCommunication:
    """Manages communication between agents with A2A protocol and ADK features.
    
    This class handles agent communication including:
    - A2A message routing and addressing
    - Part type handling and content serialization
    - Multi-part message support
    - Message validation and error handling
    - Buffering and parallel processing
    - Metrics collection
    
    Attributes:
        router (A2AMessageRouter): A2A message router
        metrics_collector (MetricsCollector): ADK metrics collector
        circuit_breaker (CircuitBreaker): ADK circuit breaker
        worker_pool (WorkerPool): ADK worker pool
        monitoring (Monitoring): ADK monitoring
        buffer (Buffer): ADK buffer
        message_queue (asyncio.Queue): Message queue
    """
    
    def __init__(self):
        """Initialize the agent communication with A2A protocol and ADK features."""
        # Initialize A2A router
        self.router = A2AMessageRouter()
        
        # Initialize ADK features
        self.metrics_collector = MetricsCollector()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=300
        )
        self.worker_pool = WorkerPool(max_workers=10)
        self.monitoring = Monitoring()
        self.buffer = Buffer()
        
        # Initialize message queue
        self.message_queue = asyncio.Queue()
        
    async def start(self):
        """Start the agent communication system."""
        await self.router.start()
        logger.info("Agent communication system started")
        
    async def stop(self):
        """Stop the agent communication system."""
        await self.router.stop()
        logger.info("Agent communication system stopped")
        
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any], message_handler: Optional[callable] = None):
        """Register an agent with the communication system."""
        self.router.register_agent(agent_id, agent_info)
        if message_handler:
            # Store message handler for direct delivery
            self.router.agents[agent_id]['message_handler'] = message_handler
        logger.info(f"Agent {agent_id} registered with communication system")
        
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the communication system."""
        self.router.unregister_agent(agent_id)
        logger.info(f"Agent {agent_id} unregistered from communication system")
        
    async def send_message(self, sender_id: str, receiver_id: str, content: Union[str, Dict[str, Any]], 
                          message_type: MessageType = MessageType.REQUEST, priority: Priority = Priority.NORMAL) -> A2AMessage:
        """Send an A2A message between agents.
        
        Args:
            sender_id (str): ID of the sending agent
            receiver_id (str): ID of the receiving agent
            content (Union[str, Dict[str, Any]]): Message content
            message_type (MessageType): Type of message
            priority (Priority): Message priority
            
        Returns:
            A2AMessage: Sent A2A message
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("send_message"):
                raise Exception("Circuit breaker is open for message sending")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("send_message"):
                # Create A2A message
                message = create_request_message(
                    sender=sender_id,
                    recipients=[receiver_id],
                    content=content,
                    message_type=message_type,
                    priority=priority
                )
                
                # Validate message
                errors = message.validate()
                if errors:
                    raise ValueError(f"Message validation failed: {errors}")
                
                # Route message
                success = await self.router.route_message(message)
                if not success:
                    raise Exception(f"Failed to route message to {receiver_id}")
                
                # Update monitoring
                self.monitoring.track_operation("send_message", {
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "message_type": message_type.value,
                    "priority": priority.value,
                    "timestamp": message.timestamp.isoformat()
                })
                
                return message
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("send_message")
            logger.error(f"Error sending message: {str(e)}")
            raise
            
    async def send_multipart_message(self, sender_id: str, receiver_id: str, parts: List[A2APart],
                                   message_type: MessageType = MessageType.REQUEST, priority: Priority = Priority.NORMAL) -> A2AMultiPartMessage:
        """Send a multi-part A2A message.
        
        Args:
            sender_id (str): ID of the sending agent
            receiver_id (str): ID of the receiving agent
            parts (List[A2APart]): Message parts
            message_type (MessageType): Type of message
            priority (Priority): Message priority
            
        Returns:
            A2AMultiPartMessage: Sent multi-part A2A message
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("send_multipart_message"):
                raise Exception("Circuit breaker is open for multipart message sending")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("send_multipart_message"):
                # Create multi-part message
                from .a2a.multipart import create_multipart_message
                message = create_multipart_message(
                    sender=sender_id,
                    recipients=[receiver_id],
                    parts=parts,
                    message_type=message_type,
                    priority=priority
                )
                
                # Validate message and parts
                errors = message.validate()
                if errors:
                    raise ValueError(f"Multi-part message validation failed: {errors}")
                
                # Route message
                success = await self.router.route_message(message)
                if not success:
                    raise Exception(f"Failed to route multi-part message to {receiver_id}")
                
                # Update monitoring
                self.monitoring.track_operation("send_multipart_message", {
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "message_type": message_type.value,
                    "priority": priority.value,
                    "part_count": len(parts),
                    "timestamp": message.timestamp.isoformat()
                })
                
                return message
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("send_multipart_message")
            logger.error(f"Error sending multi-part message: {str(e)}")
            raise
            
    async def receive_message(self, receiver_id: str) -> Optional[A2AMessage]:
        """Receive an A2A message for an agent.
        
        Args:
            receiver_id (str): ID of the receiving agent
            
        Returns:
            Optional[A2AMessage]: Received A2A message
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("receive_message"):
                raise Exception("Circuit breaker is open for message receiving")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("receive_message"):
                # Get agent info
                agent_info = self.router.get_agent_info(receiver_id)
                if not agent_info:
                    raise ValueError(f"Agent {receiver_id} not found")
                
                # Check message queue
                if 'message_queue' in agent_info:
                    try:
                        message = await asyncio.wait_for(
                            agent_info['message_queue'].get(), timeout=1.0
                        )
                        
                        # Update monitoring
                        self.monitoring.track_operation("receive_message", {
                            "receiver_id": receiver_id,
                            "sender_id": message.sender,
                            "message_type": message.message_type.value,
                            "timestamp": message.timestamp.isoformat()
                        })
                        
                        return message
                    except asyncio.TimeoutError:
                        return None
                
                return None
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("receive_message")
            logger.error(f"Error receiving message: {str(e)}")
            raise
            
    async def broadcast_message(self, sender_id: str, content: Union[str, Dict[str, Any]], 
                              message_type: MessageType = MessageType.NOTIFICATION) -> List[A2AMessage]:
        """Broadcast an A2A message to all agents.
        
        Args:
            sender_id (str): ID of the sending agent
            content (Union[str, Dict[str, Any]]): Message content
            message_type (MessageType): Type of message
            
        Returns:
            List[A2AMessage]: Sent A2A messages
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("broadcast_message"):
                raise Exception("Circuit breaker is open for message broadcasting")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("broadcast_message"):
                # Create broadcast message
                message = create_request_message(
                    sender=sender_id,
                    recipients=["broadcast"],
                    content=content,
                    message_type=message_type,
                    priority=Priority.NORMAL
                )
                
                # Route message
                success = await self.router.route_message(message)
                if not success:
                    raise Exception("Failed to broadcast message")
                
                # Update monitoring
                active_agents = self.router.get_active_agents()
                self.monitoring.track_operation("broadcast_message", {
                    "sender_id": sender_id,
                    "message_type": message_type.value,
                    "recipient_count": len(active_agents),
                    "timestamp": message.timestamp.isoformat()
                })
                
                return [message]
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("broadcast_message")
            logger.error(f"Error broadcasting message: {str(e)}")
            raise
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get ADK metrics and A2A routing statistics.
        
        Returns:
            Dict[str, Any]: Metrics including performance, resource usage, circuit breaker status, and routing stats
        """
        return {
            "performance": self.metrics_collector.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "worker_pool": self.worker_pool.get_stats(),
            "monitoring": self.monitoring.get_metrics(),
            "buffer": self.buffer.get_stats(),
            "routing": self.router.get_routing_stats()
        } 