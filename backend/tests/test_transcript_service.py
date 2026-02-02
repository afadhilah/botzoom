"""
Unit tests for TranscriptService domain logic.
Tests CRUD operations, status lifecycle, and file cleanup.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from domains.zoom_resume.transcript.service import TranscriptService
from domains.zoom_resume.transcript.model import Transcript, TranscriptStatus


class TestTranscriptService:
    """Tests for TranscriptService business logic."""
    
    def test_create_transcript_returns_pending_status(self):
        """Verify new transcripts are created with PENDING status."""
        # Arrange
        mock_db = Mock()
        mock_transcript = Transcript(
            id=1,
            user_id=123,
            audio_url="/path/to/audio.wav",
            status=TranscriptStatus.PENDING
        )
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))
        
        # Act
        with patch('domains.zoom_resume.transcript.service.Transcript', return_value=mock_transcript):
            result = TranscriptService.create_transcript(
                mock_db,
                user_id=123,
                audio_url="/path/to/audio.wav"
            )
        
        # Assert
        assert result.status == TranscriptStatus.PENDING
        assert result.user_id == 123
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_update_status_changes_transcript_status(self):
        """Verify status updates work correctly."""
        # Arrange
        mock_db = Mock()
        mock_transcript = Mock(spec=Transcript)
        mock_transcript.id = 1
        mock_transcript.status = TranscriptStatus.PENDING
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_transcript
        mock_db.query.return_value = mock_query
        
        # Act
        result = TranscriptService.update_status(
            mock_db,
            transcript_id=1,
            status=TranscriptStatus.PROCESSING
        )
        
        # Assert
        assert mock_transcript.status == TranscriptStatus.PROCESSING
        mock_db.commit.assert_called_once()
    
    def test_update_status_raises_error_for_nonexistent_transcript(self):
        """Verify ValueError raised when transcript not found."""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            TranscriptService.update_status(
                mock_db,
                transcript_id=999,
                status=TranscriptStatus.PROCESSING
            )
    
    @patch('domains.zoom_resume.transcript.service.Path')
    def test_cleanup_audio_file_deletes_existing_file(self, mock_path_class):
        """Verify audio file cleanup deletes file."""
        # Arrange
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_file_path.unlink = Mock()
        mock_path_class.return_value = mock_file_path
        
        # Act
        TranscriptService.cleanup_audio_file("/path/to/audio.wav")
        
        # Assert
        mock_file_path.unlink.assert_called_once()
    
    @patch('domains.zoom_resume.transcript.service.Path')
    def test_cleanup_audio_file_handles_nonexistent_file(self, mock_path_class):
        """Verify cleanup handles missing files gracefully."""
        # Arrange
        mock_file_path = Mock()
        mock_file_path.exists.return_value = False
        mock_path_class.return_value = mock_file_path
        
        # Act - should not raise exception
        TranscriptService.cleanup_audio_file("/path/to/missing.wav")
        
        # Assert
        mock_file_path.unlink.assert_not_called()
    
    @patch('domains.zoom_resume.transcript.service.TranscriptService.cleanup_audio_file')
    def test_save_result_calls_cleanup_when_enabled(self, mock_cleanup):
        """Verify save_result cleans up file when cleanup_file=True."""
        # Arrange
        mock_db = Mock()
        mock_transcript = Mock(spec=Transcript)
        mock_transcript.id = 1
        mock_transcript.audio_url = "/path/to/audio.wav"
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_transcript
        mock_db.query.return_value = mock_query
        
        # Act
        TranscriptService.save_result(
            mock_db,
            transcript_id=1,
            language="en",
            full_text="Test transcript",
            segments=[{"id": 0, "text": "Test"}],
            cleanup_file=True
        )
        
        # Assert
        mock_cleanup.assert_called_once_with("/path/to/audio.wav")
    
    @patch('domains.zoom_resume.transcript.service.TranscriptService.cleanup_audio_file')
    def test_save_result_skips_cleanup_when_disabled(self, mock_cleanup):
        """Verify save_result skips cleanup when cleanup_file=False."""
        # Arrange
        mock_db = Mock()
        mock_transcript = Mock(spec=Transcript)
        mock_transcript.id = 1
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_transcript
        mock_db.query.return_value = mock_query
        
        # Act
        TranscriptService.save_result(
            mock_db,
            transcript_id=1,
            language="en",
            full_text="Test",
            segments=[],
            cleanup_file=False
        )
        
        # Assert
        mock_cleanup.assert_not_called()
    
    def test_save_result_updates_status_to_done(self):
        """Verify save_result marks transcript as DONE."""
        # Arrange
        mock_db = Mock()
        mock_transcript = Mock(spec=Transcript)
        mock_transcript.id = 1
        mock_transcript.status = TranscriptStatus.PROCESSING
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_transcript
        mock_db.query.return_value = mock_query
        
        # Act
        with patch('domains.zoom_resume.transcript.service.TranscriptService.cleanup_audio_file'):
            TranscriptService.save_result(
                mock_db,
                transcript_id=1,
                language="en",
                full_text="Test",
                segments=[]
            )
        
        # Assert
        assert mock_transcript.status == TranscriptStatus.DONE
        assert mock_transcript.language == "en"
        assert mock_transcript.full_text == "Test"
    
    def test_get_by_id_returns_transcript_for_authorized_user(self):
        """Verify get_by_id returns transcript when user authorized."""
        # Arrange
        mock_db = Mock()
        mock_transcript = Mock(spec=Transcript)
        mock_transcript.id = 1
        mock_transcript.user_id = 123
        
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_transcript
        mock_db.query.return_value = mock_query
        
        # Act
        result = TranscriptService.get_by_id(mock_db, transcript_id=1, user_id=123)
        
        # Assert
        assert result == mock_transcript
    
    def test_list_by_user_returns_paginated_results(self):
        """Verify list_by_user returns correct pagination."""
        # Arrange
        mock_db = Mock()
        mock_transcripts = [Mock(spec=Transcript) for _ in range(5)]
        
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 10
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_transcripts
        mock_db.query.return_value = mock_query
        
        # Act
        transcripts, total = TranscriptService.list_by_user(
            mock_db,
            user_id=123,
            skip=0,
            limit=5
        )
        
        # Assert
        assert len(transcripts) == 5
        assert total == 10
