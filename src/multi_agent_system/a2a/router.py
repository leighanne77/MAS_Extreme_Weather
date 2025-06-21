"""
A2A Message Router

Implements message routing and addressing for the A2A protocol.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from .message import A2AMessage, create_response_message
from .enums import StatusCode, MessageType

logger = logging.getLogger(__name__)


class A2AMessageRouter:
    """A2A Message Router for handling message routing and addressing."""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.routing_table: Dict[str, str] = {}
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.broadcast_handlers: List[Callable] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Start the message router."""
        self.is_running = True
        asyncio.create_task(self._process_message_queue())
        logger.info("A2A Message Router started")
    
    async def stop(self):
        """Stop the message router."""
        self.is_running = False
        logger.info("A2A Message Router stopped")
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> None:
        """Register an agent with the router."""
        self.agents[agent_id] = {
            'info': agent_info,
            'registered_at': datetime.utcnow(),
            'last_heartbeat': datetime.utcnow(),
            'status': 'active'
        }
        self.routing_table[agent_id] = agent_id
        logger.info(f"Agent {agent_id} registered with router")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the router."""
        if agent_id in self.agents:
            del self.agents[agent_id]
        if agent_id in self.routing_table:
            del self.routing_table[agent_id]
        logger.info(f"Agent {agent_id} unregistered from router")
    
    def update_agent_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat timestamp."""
        if agent_id in self.agents:
            self.agents[agent_id]['last_heartbeat'] = datetime.utcnow()
            self.agents[agent_id]['status'] = 'active'
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information."""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[str]:
        """Get list of all registered agent IDs."""
        return list(self.agents.keys())
    
    def get_active_agents(self) -> List[str]:
        """Get list of active agent IDs."""
        return [
            agent_id for agent_id, info in self.agents.items()
            if info['status'] == 'active'
        ]
    
    async def route_message(self, message: A2AMessage) -> bool:
        """Route a message to its destination(s)."""
        try:
            # Validate message
            errors = message.validate()
            if errors:
                logger.error(f"Message validation failed: {errors}")
                return False
            
            # Check if message is expired
            if message.is_expired():
                logger.warning(f"Message {message.id} has expired")
                return False
            
            # Route based on message type
            if message.message_type == MessageType.DISCOVERY:
                return await self._handle_discovery_message(message)
            elif message.message_type == MessageType.HEARTBEAT:
                return await self._handle_heartbeat_message(message)
            else:
                return await self._route_to_recipients(message)
                
        except Exception as e:
            logger.error(f"Error routing message {message.id}: {e}")
            return False
    
    async def _route_to_recipients(self, message: A2AMessage) -> bool:
        """Route message to specific recipients."""
        success_count = 0
        
        for recipient in message.recipients:
            try:
                if recipient in self.agents:
                    # Route to specific agent
                    await self._deliver_to_agent(recipient, message)
                    success_count += 1
                elif recipient == "broadcast":
                    # Broadcast to all agents
                    await self._broadcast_message(message)
                    success_count += 1
                else:
                    logger.warning(f"Recipient {recipient} not found")
                    
            except Exception as e:
                logger.error(f"Error routing to {recipient}: {e}")
        
        return success_count > 0
    
    async def _deliver_to_agent(self, agent_id: str, message: A2AMessage) -> None:
        """Deliver message to a specific agent."""
        agent_info = self.agents.get(agent_id)
        if not agent_info:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Add message to agent's queue or call handler
        if 'message_handler' in agent_info:
            await agent_info['message_handler'](message)
        else:
            # Store message for later pickup
            if 'message_queue' not in agent_info:
                agent_info['message_queue'] = asyncio.Queue()
            await agent_info['message_queue'].put(message)
    
    async def _broadcast_message(self, message: A2AMessage) -> None:
        """Broadcast message to all active agents."""
        active_agents = self.get_active_agents()
        for agent_id in active_agents:
            try:
                await self._deliver_to_agent(agent_id, message)
            except Exception as e:
                logger.error(f"Error broadcasting to {agent_id}: {e}")
    
    async def _handle_discovery_message(self, message: A2AMessage) -> bool:
        """Handle discovery messages."""
        # Return list of available agents
        response_content = {
            'agents': [
                {
                    'id': agent_id,
                    'info': agent_info['info'],
                    'status': agent_info['status']
                }
                for agent_id, agent_info in self.agents.items()
            ]
        }
        
        # Create response message using the imported function
        response = create_response_message(
            original_message=message,
            content=response_content,
            status_code=StatusCode.OK
        )
        
        # Route response back to sender
        await self._deliver_to_agent(message.sender, response)
        return True
    
    async def _handle_heartbeat_message(self, message: A2AMessage) -> bool:
        """Handle heartbeat messages."""
        self.update_agent_heartbeat(message.sender)
        return True
    
    async def _process_message_queue(self) -> None:
        """Process messages in the queue."""
        while self.is_running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                await self.route_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def add_message_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Add a message handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def add_broadcast_handler(self, handler: Callable) -> None:
        """Add a broadcast message handler."""
        self.broadcast_handlers.append(handler)
    
    async def send_message(self, message: A2AMessage) -> bool:
        """Send a message through the router."""
        await self.message_queue.put(message)
        return True
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            'total_agents': len(self.agents),
            'active_agents': len(self.get_active_agents()),
            'queue_size': self.message_queue.qsize(),
            'registered_agents': list(self.agents.keys())
        } 