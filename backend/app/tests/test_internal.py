from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_user_created_webhook():
    test_data = {
        "userId": "00000000-0000-0000-0000-000000000005",
        "email": "test@example.com",
        "realmRole": "tutor"
    }
    
    with patch('db.session.db_pool.execute', new_callable=AsyncMock) as mock_execute:
        # We need to mock the db_pool.connect as well if we use the real app object
        # but since we are mocking execute, we can just bypass the connection for this test
        # or use a mock for the whole db_pool
        
        response = client.post("/api/custom/internal/user-created", json=test_data)
        
        assert response.status_code == 201
        assert response.json() == {"status": "created"}
        assert mock_execute.call_count == 2 # 1 for user, 1 for profile
