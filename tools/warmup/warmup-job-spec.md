# Server warm-up job: specification

Replaces the Claude task "gfmreview.co.uk and gfmreview.net warm-up" (trig_01Bats6JN76yy5Hu6XpxMhEo) once it has run one clean day. Rules are carried over unchanged. Agreed by Brett Hurll on 24 November 2026.

## Schedule and windows
- Weekdays, starting about 09:36 London, with timing varied by a few minutes each day.
- gfmreview.co.uk: Monday 23 November to Friday 11 December 2026.
- gfmreview.net: from the first weekday the connector lists its mailboxes, to Friday 18 December 2026.
- After 18 December: send nothing; send Brett one alert saying the warm-up has finished.

## Mailboxes
- New on gfmreview.co.uk: alix@, alix.middleton@, margaret@, sam@, sam.jones@, max@, max.marlow@.
- New on gfmreview.net: alix@, alix.middleton@, sam@, sam.jones@, max@, max.marlow@ (no Margaret mailbox on .net, on purpose).
- Partners (Microsoft 365): brett@gfmreview.com, brett.hurll@gfmreview.com, margaret@gfmreview.com, alix.middleton@gfmreview.com.
- Use only mailboxes the connector lists; skip any it does not and record that in the log.
- email_type "warmup" only. Never email outside gfmreview.com, gfmreview.co.uk and gfmreview.net. If the connector refuses a .net warm-up, leave .net out of that day.

## Daily volume (new emails per new mailbox)
- gfmreview.co.uk: week of 23 Nov 2, week of 30 Nov 3, week of 7 Dec 4.
- gfmreview.net: up to Fri 4 Dec 2, week of 7 Dec 3, week of 14 Dec 4.
- Recipients mostly partners, some other new mailboxes on either domain; never the same pair twice in a day; never a mailbox to itself.

## Content
- Use warmup-bank.json in this folder. Notes ("kind": "note") for new emails, replies ("kind": "reply") for answers. Fill {first_name} with the recipient's first name. Never reuse the same item for the same pair. Plain text; the connector adds the signature.

## Steps each day
1. Replies: in each new mailbox, warm-up replies received since the previous working day 09:00: mark read, reply to about half with a reply item.
2. Send the day's new emails from each new mailbox.
3. After about 8 minutes, partner side: for messages from .co.uk and .net since 09:30: check Junk first and move any found there to the Inbox (record by domain); mark read; flag about one in four; reply to about two thirds; then move each handled message to Archive. Touch nothing else.
4. Check sending_status for bounces and the cold-email cap per new mailbox.

## Log and alerts
- Write warmup-log-YYYY-MM-DD.json to this folder: per domain, emails sent per mailbox, replies, Junk found and moved, bounces or errors, mailboxes left out, cold-email cap per mailbox. The evening report reads it.
- Alert Brett once only if a warm-up email bounced, more than one message from either new domain was found in Junk that day, or the connector refused .net. No other reports.
