#!/usr/bin/env python
"""
Reminder Service Launcher
This script starts the reminder scheduler as a background process
that runs independently of your Django server.
"""

import os
import sys
import subprocess
import signal
import time
import atexit

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def start_reminder_service():
    """Start the reminder scheduler in the background"""
    try:
        print("🚀 Starting Reminder Service...")

        # Start the scheduler as a background process
        process = subprocess.Popen([
            sys.executable,
            os.path.join(PROJECT_ROOT, 'scripts', 'reminder_scheduler.py')
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PROJECT_ROOT)

        print(f"✅ Reminder service started with PID: {process.pid}")
        print("📝 Logs will be written to: reminder_scheduler.log")
        print("🛑 To stop the service, use: kill", process.pid)

        # Save PID to file for later management
        with open('reminder_service.pid', 'w') as f:
            f.write(str(process.pid))

        return process

    except Exception as e:
        print(f"❌ Failed to start reminder service: {str(e)}")
        return None

def stop_reminder_service():
    """Stop the reminder service if it's running"""
    try:
        if os.path.exists('reminder_service.pid'):
            with open('reminder_service.pid', 'r') as f:
                pid = int(f.read().strip())

            os.kill(pid, signal.SIGTERM)
            os.remove('reminder_service.pid')
            print(f"🛑 Reminder service stopped (PID: {pid})")
        else:
            print("ℹ️  No reminder service PID file found")
    except Exception as e:
        print(f"❌ Failed to stop reminder service: {str(e)}")

def check_service_status():
    """Check if the reminder service is running"""
    try:
        if os.path.exists('reminder_service.pid'):
            with open('reminder_service.pid', 'r') as f:
                pid = int(f.read().strip())

            # Check if process is still running
            try:
                os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
                print(f"✅ Reminder service is running (PID: {pid})")
                return True
            except OSError:
                # Process is not running, remove stale PID file
                print("❌ Reminder service process not found (stale PID file)")
                os.remove('reminder_service.pid')
                return False
        else:
            print("❌ Reminder service is not running")
            return False
    except Exception as e:
        print(f"❌ Error checking service status: {str(e)}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python start_reminder_service.py [start|stop|status]")
        print("  start  - Start the reminder service")
        print("  stop   - Stop the reminder service")
        print("  status - Check service status")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'start':
        start_reminder_service()
    elif command == 'stop':
        stop_reminder_service()
    elif command == 'status':
        check_service_status()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: start, stop, or status")
