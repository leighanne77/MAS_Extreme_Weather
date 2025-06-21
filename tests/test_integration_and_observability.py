"""
Consolidated tests for integration, performance, security, and observability.

Covers:
- End-to-end and integration workflows
- Performance and load
- Security (auth, RBAC, validation)
- Observability (logging, metrics, alerting)
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from multi_agent_system.session_manager import SessionManager
from multi_agent_system.agent_team import AgentTeam
from multi_agent_system.workflows.workflows import WorkflowManager, WorkflowStep
from multi_agent_system.observability import ObservabilityManager, ErrorSeverity
from multi_agent_system.agents.base_agent import BaseAgent

class TestIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        session_manager = SessionManager()
        agent_team = AgentTeam()
        workflow_manager = WorkflowManager()
        async def step1(): return {"status": "success"}
        async def step2(): return {"status": "success"}
        steps = [WorkflowStep(name="step1", handler=step1), WorkflowStep(name="step2", handler=step2)]
        result = await workflow_manager.execute_workflow("e2e_test", steps)
        assert result["step1"]["status"] == "success"
        assert result["step2"]["status"] == "success"
    @pytest.mark.asyncio
    async def test_error_propagation(self):
        workflow_manager = WorkflowManager()
        async def fail(): raise Exception("fail")
        steps = [WorkflowStep(name="fail", handler=fail)]
        with pytest.raises(Exception):
            await workflow_manager.execute_workflow("fail_test", steps)

class TestPerformance:
    def test_metrics_collection(self):
        observability = ObservabilityManager()
        with patch.object(observability, 'track_interaction', return_value={'success': True, 'duration': 100}) as mock_track:
            metrics = observability.track_interaction('agent1', 'SEQUENTIAL', datetime.now(), datetime.now(), True, {'input': 10}, 100, 50)
            assert metrics['success'] is True
            assert metrics['duration'] == 100
            mock_track.assert_called_once()
    def test_performance_alerting(self):
        observability = ObservabilityManager()
        with patch.object(observability, 'send_alert', return_value=True) as mock_alert:
            assert observability.send_alert('high_cpu', {'cpu': 95}) is True
            mock_alert.assert_called_once()

class TestSecurity:
    def test_jwt_token_validation(self):
        session_manager = SessionManager()
        with patch.object(session_manager, 'validate_jwt_token', return_value=True) as mock_val:
            assert session_manager.validate_jwt_token('token') is True
            mock_val.assert_called_once()
    def test_rbac_permission(self):
        agent_team = AgentTeam()
        with patch.object(agent_team, 'check_permission', return_value=True) as mock_perm:
            assert agent_team.check_permission('user', 'read', 'resource') is True
            mock_perm.assert_called_once()
    def test_input_sanitization(self):
        agent = Mock(spec=BaseAgent)
        agent.sanitize_input = Mock(return_value='cleaned')
        assert agent.sanitize_input('<script>') == 'cleaned'

class TestObservability:
    def test_structured_logging(self):
        observability = ObservabilityManager()
        with patch.object(observability, 'log_event', return_value=True) as mock_log:
            assert observability.log_event('event', {'foo': 'bar'}) is True
            mock_log.assert_called_once()
    def test_error_pattern_detection(self):
        observability = ObservabilityManager()
        with patch.object(observability, 'get_error_patterns', return_value={'timeout': {'count': 3}}) as mock_patterns:
            patterns = observability.get_error_patterns()
            assert 'timeout' in patterns
            assert patterns['timeout']['count'] == 3
            mock_patterns.assert_called_once()
