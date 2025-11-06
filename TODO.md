# TODO: Investigate Reminder Email Issues in Time Slots

## Information Gathered
- Reminder system uses `scripts/reminder_scheduler.py` to run `send_reminders` management command every 60 seconds.
- `send_reminders` checks for due reminders within a time window (default 10 minutes) around current time.
- Time slots defined: morning (07:00), afternoon (14:00), evening (18:00), night (21:00).
- Emails sent via `NotificationService.send_email_notification` with retry logic.
- Possible causes for missing emails in time slots:
  - Scheduler not running (check `reminder_service.pid`).
  - Time window too narrow (was 5 minutes, increased to 10).
  - Email sending failures (SMTP issues, auth, network).
  - Missing environment variables (e.g., SECRET_KEY causing command failure).
  - Reminders not active or incorrectly configured.

## Plan
- [x] Check if reminder scheduler is running (verify pid file and process).
- [x] Run `send_reminders` command manually with verbosity to test functionality.
- [x] Increase default time window from 5 to 10 minutes in `send_reminders.py` for better tolerance.
- [ ] Check logs for errors (reminder_scheduler.log, command output).
- [ ] Verify environment variables are set (SECRET_KEY, SENDGRID_API_KEY).
- [ ] Test email sending for a specific reminder.

## Dependent Files to Edit
- `reminders/management/commands/send_reminders.py`: Increase window default.

## Followup Steps
- Set environment variables (SECRET_KEY, SENDGRID_API_KEY) in .env or system environment.
- Run the updated command and monitor logs.
- Test during a time slot to confirm emails are sent.
- If issues persist, check SMTP configuration and reminder data.
