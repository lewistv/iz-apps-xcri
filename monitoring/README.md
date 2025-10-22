# XCRI Rankings - Monitoring Tools

Real-time monitoring and analytics for the XCRI Rankings application.

---

## Quick Start

### Real-Time Monitor

Monitor API performance, traffic, and resource usage in real-time:

```bash
# On the server
ssh ustfccca-web4
cd /home/web4ustfccca/mysql-migration
./xcri_monitor.sh

# Custom refresh interval (default: 10 seconds)
./xcri_monitor.sh 5   # Refresh every 5 seconds
./xcri_monitor.sh 30  # Refresh every 30 seconds
```

**Features**:
- ✅ API health and response time
- ✅ CPU and memory usage
- ✅ Request rate and traffic statistics
- ✅ Database connection monitoring
- ✅ System resource usage
- ✅ Top endpoints usage
- ✅ Recent error tracking

---

## Monitoring Dashboard

### API Status
- **Status**: HEALTHY/DOWN indicator
- **Response Time**: /health endpoint latency
- **PID**: Process ID of uvicorn
- **Uptime**: How long the API has been running
- **CPU Usage**: Percentage (color-coded: green < 50%, yellow < 80%, red > 80%)
- **Memory**: MB used (color-coded: green < 100MB, yellow < 200MB, red > 200MB)

### Traffic Statistics
- **Total Requests**: All XCRI requests since server start
- **Unique IPs**: Number of unique visitors
- **Request Rate**: Requests per second (live calculation)
- **5xx Errors**: Server errors (red if > 0)
- **4xx Errors**: Client errors (yellow if > 0)

### Database Activity
- **Connections**: Active database connections
- **Active Queries**: Currently running queries
- **Slow Queries**: Queries running > 5 seconds (yellow if > 0)

### System Resources
- **Load Average**: CPU load (color-coded based on core count)
- **Disk Usage**: Percentage used (yellow > 80%, red > 90%)
- **Memory Usage**: System RAM percentage (yellow > 80%, red > 90%)

### Top Endpoints
Shows the 5 most requested endpoints from the last 100 requests:
- `/iz/xcri/` - Frontend
- `/iz/xcri/api/athletes/` - Athlete rankings
- `/iz/xcri/api/teams/` - Team rankings
- `/iz/xcri/api/health` - Health check
- etc.

### Recent Errors
Displays last 3 errors from Apache error log related to XCRI

---

## Installation

### 1. Deploy to Server

```bash
# From your local machine
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri

# Copy monitoring script to server
scp monitoring/xcri_monitor.sh ustfccca-web4:/home/web4ustfccca/mysql-migration/

# Set executable permissions
ssh ustfccca-web4 'chmod +x /home/web4ustfccca/mysql-migration/xcri_monitor.sh'
```

### 2. Test the Monitor

```bash
ssh ustfccca-web4
cd /home/web4ustfccca/mysql-migration
./xcri_monitor.sh
```

Press `Ctrl+C` to exit.

---

## Usage Examples

### Monitor During High Traffic

When you announce the site to the public:

```bash
# Start monitoring with 5-second refresh
./xcri_monitor.sh 5
```

Watch for:
- **CPU spikes** > 80% (may need to optimize or scale)
- **Memory growth** > 200MB (potential memory leak)
- **Response time** > 1s (slow API responses)
- **5xx errors** (application errors)
- **Slow queries** (database bottlenecks)

### Monitor Performance Baseline

Establish normal performance during low traffic:

```bash
# Run with default 10-second refresh
./xcri_monitor.sh 10
```

Record typical values:
- CPU usage: ~5-10%
- Memory: ~80-100MB
- Response time: <0.3s
- Request rate: ~0-2 req/s

### Troubleshooting Issues

If users report slowness:

```bash
# Quick check with 3-second refresh
./xcri_monitor.sh 3
```

Look for:
- High CPU usage (> 50%)
- Many slow queries
- Elevated response times
- High error rates

---

## Log Files

The monitor displays data from:

### Apache Access Log
**Path**: `/var/log/apache2/access.log`
**Contains**: All HTTP requests, response codes, request times

**Example entry**:
```
192.168.1.1 - - [21/Oct/2025:14:23:45] "GET /iz/xcri/api/athletes/?division=2030&gender=M HTTP/1.1" 200 1234 0.123
```

### Apache Error Log
**Path**: `/var/log/apache2/error.log`
**Contains**: Application errors, PHP errors, Apache errors

**Example entry**:
```
[Mon Oct 21 14:23:45 2025] [error] [client 192.168.1.1] FastCGI: comm with server "/iz/xcri/api-proxy.cgi" aborted
```

### API Application Log
**Path**: `/home/web4ustfccca/public_html/iz/xcri/logs/api-live.log` (if created)
**Contains**: Uvicorn/FastAPI application logs

---

## Performance Metrics

### Expected Performance

**Normal Load** (< 10 concurrent users):
- CPU: 5-10%
- Memory: 80-100 MB
- Response Time: < 0.3s
- Request Rate: 0-5 req/s

**Medium Load** (10-50 concurrent users):
- CPU: 20-40%
- Memory: 100-150 MB
- Response Time: 0.3-0.7s
- Request Rate: 10-30 req/s

**High Load** (50-100 concurrent users):
- CPU: 50-80%
- Memory: 150-200 MB
- Response Time: 0.7-1.5s
- Request Rate: 30-50 req/s

### Warning Thresholds

**⚠️ Yellow Warnings** (investigate if sustained):
- CPU > 50%
- Memory > 100 MB
- Response Time > 0.5s
- Disk > 80%
- Memory > 80%
- 4xx errors present

**🔴 Red Alerts** (immediate action needed):
- CPU > 80%
- Memory > 200 MB
- Response Time > 2s
- 5xx errors present
- Slow queries (> 5s)
- Disk > 90%
- System memory > 90%

---

## Optimization Tips

### If CPU is High

1. **Check endpoint usage**: Which endpoints are most requested?
2. **Database queries**: Are there slow queries?
3. **Caching**: Consider implementing Redis for frequently accessed data
4. **Code optimization**: Profile slow endpoints

### If Memory is Growing

1. **Memory leak**: Check for unbounded list/dict growth
2. **Connection pooling**: Verify database connections are being closed
3. **Cache size**: If using Redis, check cache eviction policy
4. **Restart API**: Temporary fix while investigating

### If Response Time is Slow

1. **Database**: Check for slow queries (> 1s)
2. **Network**: Test database connectivity
3. **Load**: Check if CPU/memory maxed out
4. **Pagination**: Ensure queries use LIMIT/OFFSET

### If 5xx Errors Occur

1. **Check error log**: `tail -50 /var/log/apache2/error.log | grep xcri`
2. **API logs**: Check uvicorn output for Python errors
3. **Database**: Verify database connectivity
4. **Restart API**: May resolve temporary issues

---

## Advanced Monitoring

### Save Monitoring Data to File

Capture monitoring output for later analysis:

```bash
./xcri_monitor.sh 60 | tee xcri_monitor_$(date +%Y%m%d_%H%M%S).log
```

### Run in Background (tmux/screen)

For long-term monitoring:

```bash
# Using tmux
tmux new -s xcri-monitor
./xcri_monitor.sh 30
# Press Ctrl+B, then D to detach

# Reattach later
tmux attach -t xcri-monitor

# Or using screen
screen -S xcri-monitor ./xcri_monitor.sh 30
# Press Ctrl+A, then D to detach
# Reattach: screen -r xcri-monitor
```

### Create Alerts

Modify the script to send alerts when thresholds are exceeded:

```bash
# Add to xcri_monitor.sh
if [ "$cpu" -gt 80 ]; then
    echo "ALERT: High CPU usage: $cpu%" | mail -s "XCRI Alert" admin@ustfccca.org
fi
```

---

## Google Analytics Integration

See `GOOGLE_ANALYTICS.md` for:
- Setting up GA4 for XCRI
- Installing gtag.js in React SPA
- Tracking custom events
- Analyzing user behavior
- Privacy considerations

---

## Troubleshooting

### Monitor Shows "Process not found"

The API is not running:

```bash
# Check if uvicorn is running
ps aux | grep uvicorn | grep xcri

# Start the API
cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 &> ../logs/api-live.log 2>&1 &
```

### Monitor Shows "DOWN" Status

The API is running but not responding:

```bash
# Test health endpoint directly
curl http://127.0.0.1:8001/health

# Check API logs
tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log

# Restart API if needed
pkill -f "uvicorn main:app"
# Then start again (see above)
```

### No Traffic Statistics

Apache logs may not be readable:

```bash
# Check log permissions
ls -la /var/log/apache2/access.log

# If not readable, may need to run as different user or adjust permissions
```

### Database Metrics Show 0

MySQL config file not found:

```bash
# Check if config exists
ls -la ~/.mysql/web4.cnf

# Create if missing (see XCRI CLAUDE.md for database credentials)
```

---

## Related Documentation

- **API Documentation**: `../api/README.md`
- **Deployment Guide**: `../CLAUDE.md`
- **Security Documentation**: `../docs/SECURITY.md`
- **Google Analytics**: `./GOOGLE_ANALYTICS.md`

---

**Last Updated**: October 22, 2025
**Version**: 1.0.0
**Author**: Claude Code (Session 005+)
