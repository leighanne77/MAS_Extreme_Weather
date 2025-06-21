"""
Access Agent for managing data access and permissions.
Handles access control, permission management, and user authorization.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from .base_agent import BaseAgent

class AccessAgent(BaseAgent):
    """Agent responsible for managing data access and permissions."""
    
    def __init__(self):
        super().__init__(
            name="access_agent",
            description="Manages data access and permissions",
            capabilities={
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": True
            }
        )
        self.access_control = {}
        self.permission_registry = {}
        self.user_authorizations = {}
        
    async def manage_access(self, data_id: str, user_id: str, permissions: List[str], action: str = "grant") -> Dict[str, Any]:
        """Manage access permissions for user and data."""
        try:
            if action == "grant":
                if data_id not in self.access_control:
                    self.access_control[data_id] = {}
                
                self.access_control[data_id][user_id] = {
                    "permissions": permissions,
                    "granted_at": datetime.utcnow().isoformat()
                }
                
                return {
                    "status": "success",
                    "message": f"Access granted for user {user_id} to {data_id}"
                }
            elif action == "revoke":
                if data_id in self.access_control and user_id in self.access_control[data_id]:
                    del self.access_control[data_id][user_id]
                
                return {
                    "status": "success",
                    "message": f"Access revoked for user {user_id} to {data_id}"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def define_permission(self, permission_id: str, permission: Dict[str, Any]) -> Dict[str, Any]:
        """Define a new permission."""
        try:
            self.permission_registry[permission_id] = {
                "permission": permission,
                "defined_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "message": f"Permission defined: {permission_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def authorize_user(self, user_id: str, authorizations: Dict[str, Any]) -> Dict[str, Any]:
        """Authorize user with specific permissions."""
        try:
            self.user_authorizations[user_id] = {
                "authorizations": authorizations,
                "authorized_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "message": f"User authorized: {user_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_access(self, data_id: str, user_id: str, required_permission: str) -> Dict[str, Any]:
        """Check if user has required permission for data."""
        try:
            if data_id not in self.access_control or user_id not in self.access_control[data_id]:
                return {
                    "status": "error",
                    "error": "Access not granted"
                }
            
            user_permissions = self.access_control[data_id][user_id]["permissions"]
            has_permission = required_permission in user_permissions
            
            return {
                "status": "success",
                "has_permission": has_permission,
                "user_permissions": user_permissions
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get all permissions for a user."""
        try:
            permissions = {}
            for data_id, access_info in self.access_control.items():
                if user_id in access_info:
                    permissions[data_id] = access_info[user_id]
            
            return {
                "status": "success",
                "permissions": permissions
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_data_access(self, data_id: str) -> Dict[str, Any]:
        """Get all access permissions for data."""
        try:
            if data_id not in self.access_control:
                return {
                    "status": "error",
                    "error": f"No access control found for {data_id}"
                }
            
            return {
                "status": "success",
                "access_control": self.access_control[data_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_permission_definition(self, permission_id: str) -> Dict[str, Any]:
        """Get permission definition."""
        try:
            if permission_id not in self.permission_registry:
                return {
                    "status": "error",
                    "error": f"No permission found for {permission_id}"
                }
            
            return {
                "status": "success",
                "permission": self.permission_registry[permission_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_user_authorization(self, user_id: str) -> Dict[str, Any]:
        """Get user authorization information."""
        try:
            if user_id not in self.user_authorizations:
                return {
                    "status": "error",
                    "error": f"No authorization found for {user_id}"
                }
            
            return {
                "status": "success",
                "authorization": self.user_authorizations[user_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 