"""
Unit tests for domains/zoom_resume/transcript/whisper.py
Tests Whisper transcription with mocked model and file system.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from domains.zoom_resume.transcript.whisper import transcribe_audio_file


class TestWhisperTranscription:
    """Tests for Whisper audio transcription."""
    
    @patch('domains.zoom_resume.transcript.whisper._model')
    @patch('domains.zoom_resume.transcript.whisper.Path')
    def test_transcribe_audio_file_returns_expected_schema(self, mock_path_class, mock_model):
        """Verify transcription returns correct data structure."""
        # Arrange
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        # Mock __str__ properly
        type(mock_audio_path).__str__ = Mock(return_value="/path/to/audio.wav")
        mock_path_class.return_value = mock_audio_path
        
        mock_result = {
            "language": "en",
            "text": "This is a test transcription.",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.5,
                    "text": "This is a test"
                },
                {
                    "id": 1,
                    "start": 2.5,
                    "end": 5.0,
                    "text": "transcription."
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        
        # Act
        result = transcribe_audio_file("/path/to/audio.wav")
        
        # Assert
        assert "language" in result
        assert "text" in result
        assert "segments" in result
        assert "model" in result
        assert "device" in result
        assert result["language"] == "en"
        assert result["text"] == "This is a test transcription."
        assert len(result["segments"]) == 2
    
    @patch('domains.zoom_resume.transcript.whisper.Path')
    def test_transcribe_handles_nonexistent_file(self, mock_path):
        """Verify transcription raises FileNotFoundError for missing file."""
        # Arrange
        mock_audio_path = Mock()
        mock_audio_path.exists.return_value = False
        mock_path.return_value = mock_audio_path
        
        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            transcribe_audio_file("/path/to/nonexistent.wav")
        
        assert "not found" in str(exc_info.value).lower()
    
    @patch('domains.zoom_resume.transcript.whisper._model')
    @patch('domains.zoom_resume.transcript.whisper.Path')
    def test_transcribe_detects_language_correctly(self, mock_path_class, mock_model):
        """Verify language detection is included in result."""
        # Arrange
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        type(mock_audio_path).__str__ = Mock(return_value="/path/to/audio.wav")
        mock_path_class.return_value = mock_audio_path
        
        mock_result = {
            "language": "id",  # Indonesian
            "text": "Ini adalah tes transkripsi.",
            "segments": []
        }
        mock_model.transcribe.return_value = mock_result
        
        # Act
        result = transcribe_audio_file("/path/to/audio.wav")
        
        # Assert
        assert result["language"] == "id"
    
    @patch('domains.zoom_resume.transcript.whisper._model')
    @patch('domains.zoom_resume.transcript.whisper.Path')
    def test_transcribe_segments_include_timestamps(self, mock_path_class, mock_model):
        """Verify segments contain start and end timestamps."""
        # Arrange
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        type(mock_audio_path).__str__ = Mock(return_value="/path/to/audio.wav")
        mock_path_class.return_value = mock_audio_path
        
        mock_result = {
            "language": "en",
            "text": "Test",
            "segments": [
                {
                    "id": 0,
                    "start": 1.5,
                    "end": 3.7,
                    "text": "Test segment"
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        
        # Act
        result = transcribe_audio_file("/path/to/audio.wav")
        
        # Assert
        segment = result["segments"][0]
        assert "start" in segment
        assert "end" in segment
        assert segment["start"] == 1.5
        assert segment["end"] == 3.7
        assert isinstance(segment["start"], float)
        assert isinstance(segment["end"], float)
    
    @patch('domains.zoom_resume.transcript.whisper._model')
    @patch('domains.zoom_resume.transcript.whisper.Path')
    def test_transcribe_segments_include_speaker_field(self, mock_path_class, mock_model):
        """Verify segments include speaker field (default for now)."""
        # Arrange
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        type(mock_audio_path).__str__ = Mock(return_value="/path/to/audio.wav")
        mock_path_class.return_value = mock_audio_path
        
        mock_result = {
            "language": "en",
            "text": "Test",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Test"
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        
        # Act
        result = transcribe_audio_file("/path/to/audio.wav")
        
        # Assert
        segment = result["segments"][0]
        assert "speaker" in segment
        assert segment["speaker"] == "Speaker 1"
    
    @patch('domains.zoom_resume.transcript.whisper._model')
    @patch('domains.zoom_resume.transcript.whisper.Path')
    def test_transcribe_handles_empty_audio(self, mock_path_class, mock_model):
        """Verify transcription handles empty/silent audio gracefully."""
        # Arrange
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        type(mock_audio_path).__str__ = Mock(return_value="/path/to/empty.wav")
        mock_path_class.return_value = mock_audio_path
        
        mock_result = {
            "language": "en",
            "text": "",
            "segments": []
        }
        mock_model.transcribe.return_value = mock_result
        
        # Act
        result = transcribe_audio_file("/path/to/empty.wav")
        
        # Assert
        assert result["text"] == ""
        assert result["segments"] == []
        assert "language" in result
