# TODO: Implement Rate Limiting for API Endpoints

## Steps to Complete:
- [x] Uncomment the rate limiting logic in core/middleware.py to enable rate limiting
- [ ] Verify that rate limiting applies to API endpoints (excluding static and admin paths)
- [ ] Test the rate limiting functionality
- [ ] Adjust settings in settings.py if needed (currently 1000 requests per hour per IP)

## Notes:
- Rate limiting is already implemented but disabled for load testing.
- Middleware skips static files and admin paths, so APIs should be covered.
- Settings: 1000 requests/hour per IP.
