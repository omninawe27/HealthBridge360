# TODO: Implement Celery for Asynchronous Email Sending

## Completed Tasks
- [x] Modified `orders/views.py` to use Celery task for sending order confirmation emails asynchronously
- [x] Added Celery configuration to `healthkart360/settings.py`
- [x] Verified existing Celery setup in `healthkart360/celery.py` and `orders/tasks.py`

## Remaining Tasks
- [x] Install Celery and Redis dependencies
- [x] Update requirements.txt with new dependencies
- [ ] Test Celery worker functionality (requires Redis server)
- [x] Update deployment configuration for Celery worker
- [ ] Add environment variables for Redis URL in production

## Local Testing Notes
- Redis server needs to be installed and running locally for Celery worker testing
- For Windows, download Redis from https://redis.io/download or use WSL
- Start Redis: `redis-server`
- Then start Celery worker: `celery -A healthkart360 worker --loglevel=info`

## Dependencies to Install
- celery
- redis (if using Redis as broker)

## Testing Steps
1. Start Redis server (if using local Redis)
2. Start Celery worker: `celery -A healthkart360 worker --loglevel=info`
3. Test order placement to verify emails are queued
4. Check Celery logs for task execution

## Production Deployment
- Ensure Redis is available in production environment
- Add Celery worker to deployment process (e.g., via systemd or Docker)
- Monitor Celery tasks and queues
