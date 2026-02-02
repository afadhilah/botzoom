"""
Integration tests for transcript API endpoints.
Tests authentication, file validation, and async upload flow.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import io

from main import app
from domains.zoom_resume.transcript.model import TranscriptStatus
from domains.auth.utils import get_current_active_user


# Mock user for testing
def get_mock_user():
    """Mock authenticated user for testing."""
    mock_user = Mock()
    mock_user.id = 123
    mock_user.email = "test@example.com"
    mock_user.is_verified = True
    return mock_user


@pytest.fixture
def client():
    """Test client fixture with auth dependency override."""
    # Override authentication dependency
    app.dependency_overrides[get_current_active_user] = get_mock_user
    client = TestClient(app)
    yield client
    # Clean up
    app.dependency_overrides.clear()


class TestTranscriptUploadEndpoint:
    """Tests for POST /transcripts/upload endpoint."""
    
    @patch('workers.meeting.transcribe_worker.enqueue_transcript')
    @patch('api.zoom_resume.transcripts.TranscriptService.create_transcript')
    @patch('api.zoom_resume.transcripts.FileValidator.validate_upload')
    def test_upload_creates_pending_transcript(
        self,
        mock_validate,
        mock_create,
        mock_enqueue,
        client
    ):
        """Verify upload creates PENDING transcript and enqueues worker."""
        # Arrange
        mock_transcript = Mock()
        mock_transcript.id = 1
        mock_transcript.status = TranscriptStatus.PENDING
        mock_transcript.user_id = 123
        mock_transcript.audio_url = "uploads/test.wav"
        mock_transcript.language = None
        mock_transcript.full_text = None
        mock_transcript.segments = None
        mock_transcript.error_message = None
        mock_transcript.created_at = "2024-01-01T00:00:00"
        mock_transcript.updated_at = "2024-01-01T00:00:00"
        mock_create.return_value = mock_transcript
        
        # Create test file
        test_file = io.BytesIO(b"fake audio data")
        
        # Act
        response = client.post(
            "/transcripts/upload",
            files={"file": ("test.wav", test_file, "audio/wav")}
        )
        
        # Assert
        assert response.status_code == 201
        mock_validate.assert_called_once()
        mock_create.assert_called_once()
        mock_enqueue.assert_called_once_with(1)
    
    def test_upload_requires_authentication(self):
        """Verify upload endpoint requires authentication."""
        # Arrange - Create client WITHOUT auth override
        unauth_client = TestClient(app)
        test_file = io.BytesIO(b"fake audio data")
        
        # Act - No authorization
        response = unauth_client.post(
            "/transcripts/upload",
            files={"file": ("test.wav", test_file, "audio/wav")}
        )
        
        # Assert
        assert response.status_code == 401
    
    @patch('api.zoom_resume.transcripts.FileValidator.validate_upload')
    def test_upload_validates_file_size(self, mock_validate, client):
        """Verify file size validation."""
        # Arrange
        from fastapi import HTTPException
        mock_validate.side_effect = HTTPException(status_code=413, detail="File too large")
        
        test_file = io.BytesIO(b"fake audio data")
        
        # Act
        response = client.post(
            "/transcripts/upload",
            files={"file": ("test.wav", test_file, "audio/wav")}
        )
        
        # Assert
        assert response.status_code == 413
    
    @patch('api.zoom_resume.transcripts.FileValidator.validate_upload')
    def test_upload_validates_file_extension(self, mock_validate, client):
        """Verify file extension validation."""
        # Arrange
        from fastapi import HTTPException
        mock_validate.side_effect = HTTPException(status_code=400, detail="Invalid extension")
        
        test_file = io.BytesIO(b"fake data")
        
        # Act
        response = client.post(
            "/transcripts/upload",
            files={"file": ("test.txt", test_file, "text/plain")}
        )
        
        # Assert
        assert response.status_code == 400


class TestTranscriptListEndpoint:
    """Tests for GET /transcripts endpoint."""
    
    @patch('api.zoom_resume.transcripts.TranscriptService.list_by_user')
    def test_list_returns_user_transcripts(self, mock_list, client):
        """Verify list endpoint returns user's transcripts."""
        # Arrange
        mock_transcripts = [Mock() for _ in range(3)]
        for i, t in enumerate(mock_transcripts):
            t.id = i + 1
            t.status = TranscriptStatus.DONE
            t.user_id = 123
            t.audio_url = f"uploads/test{i}.wav"
            t.language = "en"
            t.full_text = "Test"
            t.segments = []
            t.error_message = None
            t.created_at = "2024-01-01T00:00:00"
            t.updated_at = "2024-01-01T00:00:00"
        mock_list.return_value = (mock_transcripts, 3)
        
        # Act
        response = client.get("/transcripts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
    
    @patch('api.zoom_resume.transcripts.TranscriptService.list_by_user')
    def test_list_supports_pagination(self, mock_list, client):
        """Verify pagination parameters work."""
        # Arrange
        from unittest.mock import ANY
        
        mock_transcripts = [Mock() for _ in range(5)]
        for i, t in enumerate(mock_transcripts):
            t.id = i + 1
            t.status = TranscriptStatus.DONE
            t.user_id = 123
            t.audio_url = f"uploads/test{i}.wav"
            t.language = "en"
            t.full_text = "Test"
            t.segments = []
            t.error_message = None
            t.created_at = "2024-01-01T00:00:00"
            t.updated_at = "2024-01-01T00:00:00"
        mock_list.return_value = (mock_transcripts, 10)
        
        # Act
        response = client.get("/transcripts?skip=5&limit=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 5
        assert data["limit"] == 5
        # Check call with ANY for db session (first parameter)
        mock_list.assert_called_once_with(ANY, 123, 5, 5)


class TestTranscriptStatusEndpoint:
    """Tests for GET /transcripts/{id}/status endpoint."""
    
    @patch('api.zoom_resume.transcripts.TranscriptService.get_by_id')
    def test_status_returns_transcript_status(self, mock_get, client):
        """Verify status endpoint returns current status."""
        # Arrange
        mock_transcript = Mock()
        mock_transcript.id = 1
        mock_transcript.status = TranscriptStatus.PROCESSING
        mock_transcript.error_message = None
        mock_get.return_value = mock_transcript
        
        # Act
        response = client.get("/transcripts/1/status")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROCESSING"
    
    @patch('api.zoom_resume.transcripts.TranscriptService.get_by_id')
    def test_status_returns_404_for_unauthorized_access(self, mock_get, client):
        """Verify 404 when user tries to access another user's transcript."""
        # Arrange
        mock_get.return_value = None  # Not found or unauthorized
        
        # Act
        response = client.get("/transcripts/999/status")
        
        # Assert
        assert response.status_code == 404
