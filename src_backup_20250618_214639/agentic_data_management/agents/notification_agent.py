"""
Notification Agent for managing system notifications and alerts.
Handles notification delivery, alert management, and user preferences.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from .base_agent import BaseAgent

class NotificationAgent(BaseAgent):
    """Agent responsible for managing system notifications and alerts."""
    
    def __init__(self):
        super().__init__(
            name="notification_agent",
            description="Manages system notifications and alerts",
            capabilities={
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": True
            }
        )
        self.notification_queue = []
        self.alert_registry = {}
        self.user_preferences = {}
        
    async def send_notification(self, user_id: str, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send a notification to a user."""
        try:
            notification_record = {
                "notification_id": f"n{len(self.notification_queue) + 1}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "notification": notification,
                "status": "sent"
            }
            
            self.notification_queue.append(notification_record)
            
            return {
                "status": "success",
                "notification": notification_record
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def create_alert(self, alert_type: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert."""
        try:
            alert_id = f"a{len(self.alert_registry) + 1}"
            alert = {
                "alert_id": alert_id,
                "alert_type": alert_type,
                "created_at": datetime.utcnow().isoformat(),
                "data": alert_data,
                "status": "active"
            }
            
            self.alert_registry[alert_id] = alert
            
            return {
                "status": "success",
                "alert": alert
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user notification preferences."""
        try:
            self.user_preferences[user_id] = {
                "preferences": preferences,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "message": f"Preferences updated for user {user_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_notifications(self, user_id: str) -> Dict[str, Any]:
        """Get notifications for user."""
        try:
            notifications = [
                notification for notification in self.notification_queue
                if notification["user_id"] == user_id
            ]
            
            return {
                "status": "success",
                "notifications": notifications
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_alerts(self, alert_type: Optional[str] = None) -> Dict[str, Any]:
        """Get alerts with optional type filter."""
        try:
            alerts = self.alert_registry
            if alert_type:
                alerts = {
                    alert_id: alert for alert_id, alert in self.alert_registry.items()
                    if alert["alert_type"] == alert_type
                }
            
            return {
                "status": "success",
                "alerts": alerts
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences."""
        try:
            if user_id not in self.user_preferences:
                return {
                    "status": "error",
                    "error": f"No preferences found for user {user_id}"
                }
            
            return {
                "status": "success",
                "preferences": self.user_preferences[user_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        """Mark a notification as read."""
        try:
            for notification in self.notification_queue:
                if notification["notification_id"] == notification_id:
                    notification["status"] = "read"
                    notification["read_at"] = datetime.utcnow().isoformat()
                    
                    return {
                        "status": "success",
                        "message": f"Notification {notification_id} marked as read"
                    }
            
            return {
                "status": "error",
                "error": f"Notification {notification_id} not found"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """Resolve an alert."""
        try:
            if alert_id not in self.alert_registry:
                return {
                    "status": "error",
                    "error": f"Alert {alert_id} not found"
                }
            
            self.alert_registry[alert_id]["status"] = "resolved"
            self.alert_registry[alert_id]["resolved_at"] = datetime.utcnow().isoformat()
            
            return {
                "status": "success",
                "message": f"Alert {alert_id} resolved"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 