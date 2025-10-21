# XCRI API - Manual Startup Guide

**Status**: Production workaround (Option C)
**Reason**: systemd service has restart loop issue
**Current Process**: Manual uvicorn with nohup + crontab auto-start

---

## Manual Startup Command

To start the XCRI API manually on the server:

```bash
# SSH to server
ssh web4ustfccca@web4.ustfccca.org

# Navigate to API directory
cd /home/web4ustfccca/public_html/iz/xcri/api

# Activate virtual environment
source venv/bin/activate

# Start uvicorn in background with nohup
nohup uvicorn main:app --host 127.0.0.1 --port 8001 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log 2>> /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log &

# Verify it's running
ps aux | grep "uvicorn main:app"

# Test API health
curl http://127.0.0.1:8001/health
```

---

## Auto-Start on Server Reboot (Crontab)

### Installation

**On the server**, add this entry to crontab:

```bash
# Edit crontab
crontab -e

# Add this line:
@reboot cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && nohup uvicorn main:app --host 127.0.0.1 --port 8001 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log 2>> /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log &
```

### Verification

```bash
# List current crontab entries
crontab -l

# After server reboot, check if process started
ps aux | grep "uvicorn main:app"
```

---

## Process Management

### Check if Running

```bash
# Find process
ps aux | grep "uvicorn main:app --host 127.0.0.1 --port 8001"

# Or check by port
netstat -tuln | grep 8001
```

### Stop Process

```bash
# Find PID
ps aux | grep "uvicorn main:app --host 127.0.0.1 --port 8001" | grep -v grep

# Kill by PID
kill <PID>

# Or kill by pattern
pkill -f "uvicorn main:app --host 127.0.0.1 --port 8001"
```

### Restart Process

```bash
# Stop
pkill -f "uvicorn main:app --host 127.0.0.1 --port 8001"

# Wait 2 seconds
sleep 2

# Start
cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && nohup uvicorn main:app --host 127.0.0.1 --port 8001 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log 2>> /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log &
```

---

## Monitoring

### Check Logs

```bash
# API access log
tail -f /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log

# API error log
tail -f /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log

# Last 50 lines
tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log
```

### Health Check

```bash
# Local (on server)
curl http://127.0.0.1:8001/health | jq

# Remote (from anywhere)
curl https://web4.ustfccca.org/iz/xcri/api/health | jq
```

### Process Uptime

```bash
# Find process and check start time
ps -p <PID> -o pid,etime,cmd
```

---

## Current Production Status

**Current Process**: PID 3858399 (as of October 21, 2025 16:08 UTC)
**Status**: Stable and operational
**Uptime**: Running since deployment
**Performance**: All endpoints responding < 300ms

---

## Future Migration Plan

When ready to fix systemd service properly:

**Option A**: Test updated systemd service (Restart=on-failure)
**Option B**: Implement Gunicorn supervisor with UvicornWorker

See `NEXT_SESSION_PROMPT.md` for detailed instructions.

---

## Troubleshooting

### API Not Responding

1. Check if process is running: `ps aux | grep uvicorn`
2. Check logs: `tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log`
3. Check port: `netstat -tuln | grep 8001`
4. Restart manually (see commands above)

### Multiple Processes Running

```bash
# Kill all uvicorn processes for this app
pkill -f "uvicorn main:app --host 127.0.0.1 --port 8001"

# Verify all stopped
ps aux | grep uvicorn

# Start fresh
cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && nohup uvicorn main:app --host 127.0.0.1 --port 8001 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log 2>> /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log &
```

### After Code Deployment

```bash
# Stop old process
pkill -f "uvicorn main:app --host 127.0.0.1 --port 8001"

# Clear Python bytecode cache
cd /home/web4ustfccca/public_html/iz/xcri/api
find . -name '*.pyc' -delete
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Start new process
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log 2>> /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log &
```

---

**Last Updated**: October 21, 2025
**Status**: Production workaround active
**Next Review**: When systemd service fix is prioritized
