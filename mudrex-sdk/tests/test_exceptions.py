"""
Tests for Mudrex SDK Exceptions
===============================
"""

from mudrex.exceptions import (
    MudrexAPIError,
    MudrexAuthenticationError,
    MudrexRateLimitError,
    MudrexValidationError,
    raise_for_error,
    ERROR_CODE_MAP,
)


class TestMudrexAPIError:
    def test_basic_error(self):
        error = MudrexAPIError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
    
    def test_error_with_details(self):
        error = MudrexAPIError(
            message="Invalid request",
            code="INVALID_REQUEST",
            status_code=400,
            request_id="req_12345",
        )
        
        assert "Invalid request" in str(error)
        assert "INVALID_REQUEST" in str(error)
        assert "400" in str(error)
        assert "req_12345" in str(error)


class TestMudrexRateLimitError:
    def test_retry_after(self):
        error = MudrexRateLimitError(
            message="Rate limit exceeded",
            retry_after=5.0,
        )
        
        assert error.retry_after == 5.0


class TestRaiseForError:
    def test_success_response(self):
        response = {"success": True, "data": {}}
        # Should not raise
        raise_for_error(response, 200)
    
    def test_auth_error(self):
        response = {
            "success": False,
            "code": "UNAUTHORIZED",
            "message": "Invalid API key",
            "requestId": "req_123",
        }
        
        try:
            raise_for_error(response, 401)
            assert False, "Should have raised"
        except MudrexAuthenticationError as e:
            assert e.code == "UNAUTHORIZED"
            assert e.request_id == "req_123"
    
    def test_validation_error(self):
        response = {
            "success": False,
            "code": "INVALID_REQUEST",
            "message": "Leverage out of range",
        }
        
        try:
            raise_for_error(response, 400)
            assert False, "Should have raised"
        except MudrexValidationError as e:
            assert "Leverage" in e.message


class TestErrorCodeMap:
    def test_mapping(self):
        assert ERROR_CODE_MAP["UNAUTHORIZED"] == MudrexAuthenticationError
        assert ERROR_CODE_MAP["RATE_LIMIT_EXCEEDED"] == MudrexRateLimitError
        assert ERROR_CODE_MAP["INVALID_REQUEST"] == MudrexValidationError
