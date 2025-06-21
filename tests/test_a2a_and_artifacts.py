"""
Consolidated tests for A2A protocol, artifacts, multipart, parts, router, and task manager.

Covers:
- A2A message structure, validation, multipart
- Artifact and artifact manager
- Parts and content handlers
- Router and task manager
- Error handling in A2A
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from multi_agent_system.a2a.message import (
    A2AMessage, create_request_message, create_response_message, create_error_message
)
from multi_agent_system.a2a.multipart import A2AMultiPartMessage
from multi_agent_system.a2a.parts import A2APart
from multi_agent_system.a2a.artifacts import A2AArtifact, ArtifactMetadata
from multi_agent_system.a2a.artifact_manager import A2AArtifactManager
from multi_agent_system.a2a.task_manager import TaskStatus
from multi_agent_system.a2a.router import A2AMessageRouter
from multi_agent_system.a2a.enums import MessageType, Priority, StatusCode, PartType

class TestA2AMessages:
    def test_create_and_validate_request_message(self):
        msg = create_request_message(
            sender="agent1",
            recipients=["agent2"],
            content={"foo": "bar"},
            message_type=MessageType.REQUEST,
            priority=Priority.NORMAL
        )
        assert msg.sender == "agent1"
        assert msg.recipients == ["agent2"]
        assert msg.content == {"foo": "bar"}
        assert msg.message_type == MessageType.REQUEST
        assert msg.priority == Priority.NORMAL
        assert not msg.is_expired()
        assert msg.validate() == []
    def test_create_error_message(self):
        orig = create_request_message(sender="a", recipients=["b"], content={})
        err = create_error_message(orig, StatusCode.BAD_REQUEST, "fail")
        assert err.status_code == StatusCode.BAD_REQUEST
        assert err.error_message == "fail"
    def test_message_expiration_and_retry(self):
        msg = create_request_message(sender="a", recipients=["b"], content={})
        msg.headers.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        assert msg.is_expired()
        msg.headers.retry_count = 2
        assert msg.can_retry()
        msg.headers.retry_count = 3
        assert not msg.can_retry()
    def test_multipart_message(self):
        msg = A2AMultiPartMessage(sender="a", recipients=["b"], content="test")
        part = A2APart(id="p1", part_type=PartType.TEXT, content="hello")
        msg.add_part(part)
        assert msg.has_parts()
        assert msg.get_part_count() == 1
        assert msg.get_total_size() == part.size
        assert msg.validate() == []

class TestA2AArtifacts:
    def test_artifact_versioning(self):
        metadata = ArtifactMetadata(
            title="Test Artifact",
            description="Test artifact for versioning",
            author="test_author"
        )
        artifact = A2AArtifact(
            id="art1",
            content="initial",
            metadata=metadata,
            current_version="1.0.0"
        )
        artifact.versions = []
        artifact.create_new_version("author", ["init"])
        assert len(artifact.versions) == 1
        artifact.update_content("new", "author", ["update"])
        assert len(artifact.versions) == 2
    def test_artifact_expiry(self):
        metadata = ArtifactMetadata(
            title="Test Artifact",
            description="Test artifact for expiry",
            author="test_author"
        )
        artifact = A2AArtifact(
            id="art2",
            content="data",
            metadata=metadata,
            current_version="1.0.0"
        )
        artifact.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        assert artifact.is_expired()

class TestA2AParts:
    def test_part_validation(self):
        part = A2APart(id="p1", part_type=PartType.TEXT, content="hi")
        assert part.validate() == []
        part.id = ""
        assert "Part ID is required" in part.validate()
    def test_part_content_conversion(self):
        part = A2APart(id="p2", part_type=PartType.DATA, content={"foo": 1})
        assert part.get_content_as_dict()["foo"] == 1
        assert "foo" in part.get_content_as_text()

class TestA2AErrorHandling:
    def test_a2a_error_response(self):
        orig = create_request_message(sender="a", recipients=["b"], content={})
        err = create_error_message(orig, StatusCode.INTERNAL_ERROR, "fail")
        assert err.status_code == StatusCode.INTERNAL_ERROR
        assert err.error_message == "fail"

class TestA2ARouterAndTasks:
    @pytest.mark.asyncio
    async def test_router_routing(self):
        router = A2AMessageRouter()
        msg = create_request_message(sender="a", recipients=["b"], content={})
        with patch.object(router, 'route_message', return_value=True) as mock_route:
            result = await router.route_message(msg)
            assert result is True
            mock_route.assert_called_once()
    def test_task_status_enum(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed" 