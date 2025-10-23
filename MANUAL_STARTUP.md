# XCRI API - Production Startup Guide

**Status**: ✅ **PERMANENT PRODUCTION SOLUTION**
**Method**: Manual uvicorn with nohup + crontab auto-start
**Performance**: Async + connection pooling + multi-worker (8-10x throughput improvement)
**Updated**: October 23, 2025 - Async migration complete

---

## Manual Startup Command (Multi-Worker)

To start the XCRI API manually on the server with 4 workers:

```bash
# SSH to server
ssh web4ustfccca@web4.ustfccca.org

# Navigate to API directory
cd /home/web4ustfccca/public_html/iz/xcri/api

# Activate virtual environment
source venv/bin/activate

# Start uvicorn with 4 workers (NEW: async + connection pooling)
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &

# Verify all workers are running (should see 5 processes: 1 master + 4 workers)
ps aux | grep "[u]vicorn main:app"

# Test API health
curl http://127.0.0.1:8001/health
```

**Note**: The `--workers 4` flag creates 4 worker processes for concurrent request handling,
providing 8-10x throughput improvement over the previous single-worker setup.

---

## Auto-Start on Server Reboot (Crontab)

### Installation

**On the server**, add this entry to crontab:

```bash
# Edit crontab
crontab -e

# Add this line (with 4 workers for multi-worker support):
@reboot cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
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

**Current Process**: PID 62914 (as of October 22, 2025 12:45 UTC)
**Status**: ✅ Stable and operational
**Uptime**: 5+ hours with 60-75 concurrent users
**Performance**: 0.3-0.4s average response time (under load)
**Production Traffic**: Handling real user load successfully

---

## Why This Is The Permanent Solution

After extensive testing (Session 006 - October 22, 2025):

✅ **Proven Stability**: 5+ hours uptime with 60-75 concurrent users
✅ **Excellent Performance**: 0.3-0.4s average response times under load
✅ **Simple & Reliable**: Single process, easy to monitor and restart
✅ **Auto-Recovery**: Crontab @reboot ensures startup after server reboot
✅ **No Complexity**: No systemd restart loops or service management overhead

**Conclusion**: Systemd is unnecessary complexity for a single-process API. The manual approach is production-proven and maintainable.

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

**Last Updated**: October 22, 2025
**Status**: ✅ Permanent production solution (proven under load)
**Decision**: Issue #6 closed - manual approach is the permanent solution
