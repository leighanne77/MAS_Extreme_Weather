from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import asyncio
import json
import hashlib
import hmac
import secrets
from dataclasses import dataclass, field

from .utils.adk_features import MetricsCollector, CircuitBreaker, WorkerPool, Monitoring, Buffer

@dataclass
class SecurityContext:
    """Security context for agent operations."""
    api_key: Optional[str] = None
    user_id: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    session_id: Optional[str] = None
    request_id: Optional[str] = None

@dataclass
class ErrorContext:
    """Error context for detailed error reporting."""
    error_type: str
    error_code: str
    error_message: str
    timestamp: datetime
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """Enhanced base class for all agents with comprehensive ADK features and security."""
    
    def __init__(
        self, 
        name: str,
        security_context: Optional[SecurityContext] = None,
        enable_monitoring: bool = True,
        enable_caching: bool = True
    ):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.security_context = security_context or SecurityContext()
        
        # Initialize ADK features
        self.metrics = MetricsCollector()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=300
        )
        self.cache = {} if enable_caching else None
        self.worker_pool = WorkerPool(max_workers=10)
        self.monitoring = Monitoring() if enable_monitoring else None
        self.buffer = Buffer()
        
        # Security features
        self.request_validator = RequestValidator()
        self.rate_limiter = RateLimiter()
        self.audit_logger = AuditLogger()
        
        # Error handling
        self.error_handler = ErrorHandler()
        self.retry_policy = RetryPolicy()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
    
    async def handle_request(
        self, 
        request: Dict[str, Any],
        security_context: Optional[SecurityContext] = None
    ) -> Dict[str, Any]:
        """Handle incoming requests with comprehensive validation and security."""
        start_time = datetime.now()
        request_id = self._generate_request_id()
        
        try:
            # Update security context
            if security_context:
                self.security_context = security_context
            
            # Validate request
            validation_result = await self.request_validator.validate(request)
            if not validation_result.is_valid:
                return self._create_error_response(
                    "validation_error",
                    validation_result.errors,
                    request_id
                )
            
            # Check rate limits
            if not self.rate_limiter.is_allowed(self.security_context.user_id):
                return self._create_error_response(
                    "rate_limit_exceeded",
                    "Too many requests",
                    request_id
                )
            
            # Log request
            self.audit_logger.log_request(
                request_id=request_id,
                user_id=self.security_context.user_id,
                action="request_received",
                details=request
            )
            
            # Execute request with monitoring
            with self.performance_monitor.track_operation(f"{self.name}_request"):
                result = await self._execute_request(request, request_id)
            
            # Log success
            self.audit_logger.log_request(
                request_id=request_id,
                user_id=self.security_context.user_id,
                action="request_completed",
                details={"status": "success"}
            )
            
            # Add performance metrics
            result["performance"] = {
                "request_id": request_id,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "agent_metrics": self.metrics.get_metrics(),
                "resource_usage": self.metrics.get_resource_usage()
            }
            
            return result
            
        except Exception as e:
            # Handle error
            error_context = ErrorContext(
                error_type="request_processing_error",
                error_code="INTERNAL_ERROR",
                error_message=str(e),
                timestamp=datetime.now(),
                request_id=request_id,
                user_id=self.security_context.user_id,
                stack_trace=self._get_stack_trace(e)
            )
            
            # Log error
            self.error_handler.handle_error(error_context)
            self.audit_logger.log_request(
                request_id=request_id,
                user_id=self.security_context.user_id,
                action="request_failed",
                details={"error": str(e)}
            )
            
            return self._create_error_response(
                "internal_error",
                "An internal error occurred",
                request_id
            )
    
    @abstractmethod
    async def _execute_request(self, request: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Execute the actual request logic. Must be implemented by subclasses."""
        pass
    
    async def execute_with_retry(
        self,
        func: callable,
        *args,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> Any:
        """Execute a function with enhanced retry logic and error handling."""
        return await self.retry_policy.execute_with_retry(
            func, *args, max_retries=max_retries, retry_delay=retry_delay, **kwargs
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive agent metrics."""
        return {
            "name": self.name,
            "timestamp": datetime.now().isoformat(),
            "performance": self.metrics.get_metrics(),
            "resources": self.metrics.get_resource_usage(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "security": {
                "rate_limits": self.rate_limiter.get_status(),
                "validation_stats": self.request_validator.get_stats()
            },
            "errors": self.error_handler.get_error_stats(),
            "audit": self.audit_logger.get_stats()
        }
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
    
    def _create_error_response(
        self, 
        error_type: str, 
        error_message: Union[str, List[str]], 
        request_id: str
    ) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "status": "error",
            "error": {
                "type": error_type,
                "message": error_message,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            },
            "performance": {
                "request_id": request_id,
                "agent_metrics": self.metrics.get_metrics()
            }
        }
    
    def _get_stack_trace(self, exception: Exception) -> str:
        """Get stack trace for an exception."""
        import traceback
        return "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

class RequestValidator:
    """Validates incoming requests for security and correctness."""
    
    def __init__(self):
        self.validation_stats = {
            "total_requests": 0,
            "valid_requests": 0,
            "invalid_requests": 0,
            "validation_errors": {}
        }
    
    async def validate(self, request: Dict[str, Any]) -> 'ValidationResult':
        """Validate a request."""
        self.validation_stats["total_requests"] += 1
        errors = []
        
        # Basic structure validation
        if not isinstance(request, dict):
            errors.append("Request must be a dictionary")
        
        # Required fields validation
        required_fields = self._get_required_fields()
        for field in required_fields:
            if field not in request:
                errors.append(f"Missing required field: {field}")
        
        # Input sanitization
        sanitized_request = self._sanitize_input(request)
        
        # Security validation
        security_errors = await self._validate_security(request)
        errors.extend(security_errors)
        
        # Update stats
        if errors:
            self.validation_stats["invalid_requests"] += 1
            for error in errors:
                self.validation_stats["validation_errors"][error] = \
                    self.validation_stats["validation_errors"].get(error, 0) + 1
        else:
            self.validation_stats["valid_requests"] += 1
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_request=sanitized_request
        )
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields for validation. Override in subclasses."""
        return []
    
    def _sanitize_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input to prevent injection attacks."""
        # Basic sanitization - implement more sophisticated sanitization as needed
        return request
    
    async def _validate_security(self, request: Dict[str, Any]) -> List[str]:
        """Validate security aspects of the request."""
        errors = []
        # Implement security validation logic
        return errors
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self.validation_stats.copy()

@dataclass
class ValidationResult:
    """Result of request validation."""
    is_valid: bool
    errors: List[str]
    sanitized_request: Dict[str, Any]

class RateLimiter:
    """Implements rate limiting for agent requests."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.window_start = datetime.now()
    
    def is_allowed(self, user_id: Optional[str]) -> bool:
        """Check if a request is allowed based on rate limits."""
        current_time = datetime.now()
        
        # Reset window if needed
        if (current_time - self.window_start).total_seconds() > 60:
            self.request_counts.clear()
            self.window_start = current_time
        
        # Check rate limit
        user_key = user_id or "anonymous"
        current_count = self.request_counts.get(user_key, 0)
        
        if current_count >= self.requests_per_minute:
            return False
        
        self.request_counts[user_key] = current_count + 1
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get rate limiter status."""
        return {
            "requests_per_minute": self.requests_per_minute,
            "current_counts": self.request_counts.copy(),
            "window_start": self.window_start.isoformat()
        }

class AuditLogger:
    """Logs audit events for security and compliance."""
    
    def __init__(self):
        self.audit_events = []
        self.stats = {
            "total_events": 0,
            "events_by_type": {}
        }
    
    def log_request(
        self, 
        request_id: str, 
        user_id: Optional[str], 
        action: str, 
        details: Dict[str, Any]
    ):
        """Log an audit event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "action": action,
            "details": details
        }
        
        self.audit_events.append(event)
        self.stats["total_events"] += 1
        self.stats["events_by_type"][action] = self.stats["events_by_type"].get(action, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics."""
        return self.stats.copy()

class ErrorHandler:
    """Handles and tracks errors for monitoring and debugging."""
    
    def __init__(self):
        self.errors = []
        self.error_stats = {
            "total_errors": 0,
            "errors_by_type": {},
            "errors_by_code": {}
        }
    
    def handle_error(self, error_context: ErrorContext):
        """Handle an error context."""
        self.errors.append(error_context)
        self.error_stats["total_errors"] += 1
        
        # Update type statistics
        self.error_stats["errors_by_type"][error_context.error_type] = \
            self.error_stats["errors_by_type"].get(error_context.error_type, 0) + 1
        
        # Update code statistics
        self.error_stats["errors_by_code"][error_context.error_code] = \
            self.error_stats["errors_by_code"].get(error_context.error_code, 0) + 1
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return self.error_stats.copy()

class RetryPolicy:
    """Implements retry policies for resilient operations."""
    
    async def execute_with_retry(
        self,
        func: callable,
        *args,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic."""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        
        raise last_exception

class PerformanceMonitor:
    """Monitors performance of operations."""
    
    def __init__(self):
        self.operation_times = {}
    
    def track_operation(self, operation_name: str):
        """Context manager to track operation performance."""
        return PerformanceTracker(operation_name, self.operation_times)

class PerformanceTracker:
    """Tracks performance of a single operation."""
    
    def __init__(self, operation_name: str, operation_times: Dict[str, List[float]]):
        self.operation_name = operation_name
        self.operation_times = operation_times
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            if self.operation_name not in self.operation_times:
                self.operation_times[self.operation_name] = []
            self.operation_times[self.operation_name].append(duration) 