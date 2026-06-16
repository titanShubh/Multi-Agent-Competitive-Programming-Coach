import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import uuid

# Test 1: Config loads correctly
def test_settings_load():
    from app.config import Settings
    s = Settings(openai_api_key="test-key", database_url="postgresql+asyncpg://test", jwt_secret="test-secret")
    assert s.openai_api_key == "test-key"
    assert s.jwt_secret == "test-secret"

# Test 2: Database URL sanitization (postgres:// -> postgresql+asyncpg://)
def test_database_url_sanitize_postgres():
    from app.config import Settings
    s = Settings(openai_api_key="k", database_url="postgres://user:pass@host/db", jwt_secret="s")
    assert s.database_url.startswith("postgresql+asyncpg://")

# Test 3: Database URL sanitization (postgresql:// -> postgresql+asyncpg://)
def test_database_url_sanitize_postgresql():
    from app.config import Settings
    s = Settings(openai_api_key="k", database_url="postgresql://user:pass@host/db", jwt_secret="s")
    assert s.database_url.startswith("postgresql+asyncpg://")

# Test 4: Password hashing
def test_password_hash():
    from app.services.auth_service import hash_password, verify_password
    h = hash_password("mypassword")
    assert h != "mypassword"
    assert verify_password("mypassword", h)
    assert not verify_password("wrongpassword", h)

# Test 5: JWT token creation and decode
def test_jwt_token():
    from app.services.auth_service import create_access_token
    token = create_access_token({"sub": "test-user-id"})
    assert isinstance(token, str)
    assert len(token) > 20

# Test 6: Reasoning block parsing
def test_parse_reasoning_block():
    from app.api.sessions import parse_reasoning_block
    text = '''<reasoning>
    <current_understanding>Student understands arrays</current_understanding>
    <key_observation>This is a DP problem</key_observation>
    <possible_approaches>
    <approach>Brute force O(N^2)</approach>
    <approach>DP O(N)</approach>
    </possible_approaches>
    <why_not_direct_answer>Student should discover</why_not_direct_answer>
    <next_step_for_student>Analyze constraints</next_step_for_student>
    <pedagogical_goal>Teach constraint analysis</pedagogical_goal>
    </reasoning>
    
    Great question! What are the constraints?'''
    frame = parse_reasoning_block(text)
    assert frame is not None
    assert "Student understands arrays" in frame["current_understanding"]
    assert len(frame["possible_approaches"]) == 2

# Test 7: Reasoning block stripping
def test_strip_reasoning_block():
    from app.api.sessions import strip_reasoning_block
    text = '<reasoning><current_understanding>test</current_understanding></reasoning>\n\nHello student!'
    result = strip_reasoning_block(text)
    assert '<reasoning>' not in result
    assert 'Hello student!' in result

# Test 8: Schema validation - UserRegister
def test_user_register_schema():
    from app.schemas.auth import UserRegister
    u = UserRegister(email="test@test.com", username="testuser", password="pass123")
    assert u.email == "test@test.com"

# Test 9: Schema validation - UserRegister rejects short password
def test_user_register_short_password():
    from app.schemas.auth import UserRegister
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UserRegister(email="test@test.com", username="testuser", password="hi")

# Test 10: Schema validation - SessionCreate
def test_session_create_schema():
    from app.schemas.session import SessionCreate
    s = SessionCreate(problem_statement="Find the maximum subarray sum given an array of N integers.")
    assert s.session_mode == "learning"
    assert s.timer_duration_minutes is None
