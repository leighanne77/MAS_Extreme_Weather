"""
Agent communication module with ADK features.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

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
    """Manages communication between agents with ADK features.
    
    This class handles agent communication including:
    - Message routing
    - Buffering
    - Parallel processing
    - Metrics collection
    
    Attributes:
        metrics_collector (MetricsCollector): ADK metrics collector
        circuit_breaker (CircuitBreaker): ADK circuit breaker
        worker_pool (WorkerPool): ADK worker pool
        monitoring (Monitoring): ADK monitoring
        buffer (Buffer): ADK buffer
        message_queue (asyncio.Queue): Message queue
    """
    
    def __init__(self):
        """Initialize the agent communication with ADK features."""
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
        
    async def send_message(self, sender_id: str, receiver_id: str, content: Dict[str, Any]) -> Message:
        """Send a message between agents with ADK features.
        
        Args:
            sender_id (str): ID of the sending agent
            receiver_id (str): ID of the receiving agent
            content (Dict[str, Any]): Message content
            
        Returns:
            Message: Sent message with ADK metadata
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("send_message"):
                raise Exception("Circuit breaker is open for message sending")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("send_message"):
                # Create message
                message = Message(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    content=content,
                    timestamp=datetime.now(),
                    metadata={
                        "monitoring_enabled": True,
                        "metrics_collection": True,
                        "circuit_breaker": True
                    }
                )
                
                # Add to buffer
                await self.buffer.add(message)
                
                # Add to queue
                await self.message_queue.put(message)
                
                # Update monitoring
                self.monitoring.track_operation("send_message", {
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "timestamp": message.timestamp.isoformat()
                })
                
                return message
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("send_message")
            logger.error(f"Error sending message: {str(e)}")
            raise
            
    async def receive_message(self, receiver_id: str) -> Optional[Message]:
        """Receive a message for an agent with ADK features.
        
        Args:
            receiver_id (str): ID of the receiving agent
            
        Returns:
            Optional[Message]: Received message with ADK metadata
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("receive_message"):
                raise Exception("Circuit breaker is open for message receiving")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("receive_message"):
                # Get message from queue
                message = await self.message_queue.get()
                
                # Check if message is for this receiver
                if message.receiver_id != receiver_id:
                    # Put message back in queue
                    await self.message_queue.put(message)
                    return None
                    
                # Update monitoring
                self.monitoring.track_operation("receive_message", {
                    "receiver_id": receiver_id,
                    "sender_id": message.sender_id,
                    "timestamp": message.timestamp.isoformat()
                })
                
                return message
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("receive_message")
            logger.error(f"Error receiving message: {str(e)}")
            raise
            
    async def broadcast_message(self, sender_id: str, content: Dict[str, Any], receiver_ids: List[str]) -> List[Message]:
        """Broadcast a message to multiple agents with ADK features.
        
        Args:
            sender_id (str): ID of the sending agent
            content (Dict[str, Any]): Message content
            receiver_ids (List[str]): IDs of receiving agents
            
        Returns:
            List[Message]: Sent messages with ADK metadata
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("broadcast_message"):
                raise Exception("Circuit breaker is open for message broadcasting")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("broadcast_message"):
                # Create messages
                messages = []
                for receiver_id in receiver_ids:
                    message = await self.send_message(sender_id, receiver_id, content)
                    messages.append(message)
                    
                # Update monitoring
                self.monitoring.track_operation("broadcast_message", {
                    "sender_id": sender_id,
                    "receiver_count": len(receiver_ids),
                    "timestamp": datetime.now().isoformat()
                })
                
                return messages
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("broadcast_message")
            logger.error(f"Error broadcasting message: {str(e)}")
            raise
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get ADK metrics for the agent communication.
        
        Returns:
            Dict[str, Any]: Metrics including performance, resource usage, and circuit breaker status
        """
        return {
            "performance": self.metrics_collector.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "monitoring": self.monitoring.get_metrics(),
            "resource_usage": self.worker_pool.get_resource_usage(),
            "buffer": self.buffer.get_metrics(),
            "queue_size": self.message_queue.qsize()
        } 