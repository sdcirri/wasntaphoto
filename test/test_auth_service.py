from sqlalchemy.exc import IntegrityError
from unittest.mock import AsyncMock
import pytest

from service import AuthService


@pytest.mark.asyncio
async def test_yield_session_retries_on_collision():
    session_repo = AsyncMock()
    session_repo.save.side_effect = [
        IntegrityError('INSERT', {}, Exception('duplicate key value violates unique constraint')),
        None
    ]
    auth_service = AuthService(
        user_repo=AsyncMock(),
        session_repo=session_repo,
        redis=AsyncMock()
    )
    token = await auth_service.yield_session(1)
    assert isinstance(token, str)
    assert session_repo.save.call_count == 2
