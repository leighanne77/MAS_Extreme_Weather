#!/usr/bin/env python3
"""
Test script to verify agent security context and error context handling
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from multi_agent_system.agents.base_agent import SecurityContext, ErrorContext
from datetime import datetime

def test_security_context_fields():
    ctx = SecurityContext(api_key="test", user_id="user1", permissions=["read"], session_id="sess1", request_id="req1")
    assert ctx.api_key == "test"
    assert ctx.user_id == "user1"
    assert ctx.permissions == ["read"]
    assert ctx.session_id == "sess1"
    assert ctx.request_id == "req1"
    print("✅ SecurityContext fields validated")

def test_error_context_fields():
    err = ErrorContext(error_type="Type", error_code="Code", error_message="Msg", timestamp=datetime.now(), request_id="req1", user_id="user1", stack_trace="trace", context_data={"key": "val"})
    assert err.error_type == "Type"
    assert err.error_code == "Code"
    assert err.error_message == "Msg"
    assert err.request_id == "req1"
    assert err.user_id == "user1"
    assert err.stack_trace == "trace"
    assert err.context_data["key"] == "val"
    print("✅ ErrorContext fields validated")
