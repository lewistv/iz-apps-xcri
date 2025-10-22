# Session 005+ - Production Monitoring and Analytics Integration

**Date**: October 22, 2025
**Session Type**: Monitoring & Analytics
**Duration**: ~60 minutes
**Focus**: Real-time monitoring and Google Analytics integration for production launch

---

## Session Context

**Situation**: XCRI Rankings site launched to coaches, public announcement pending
**Need**: Real-time monitoring during high-traffic launch + analytics tracking
**User Request**: Design monitoring tool and integrate Google Analytics

---

## Work Completed

### 🔧 Real-Time Monitoring Dashboard

**Created**: `monitoring/xcri_monitor.sh` (488 lines)

**Features**:
- 📊 **API Health Monitoring**
  - Status indicator (HEALTHY/DOWN)
  - Response time tracking
  - Process uptime
  - CPU usage (color-coded thresholds)
  - Memory usage (currently ~87.5 MB baseline)

- 🌐 **Traffic Statistics**
  - Total request count
  - Unique visitor IPs
  - Request rate (req/s) with live calculation
  - 5xx errors (server errors)
  - 4xx errors (client errors)

- 💾 **Database Activity**
  - Active connections
  - Running queries
  - Slow query detection (> 5s)

- ⚙️ **System Resources**
  - Load average (color-coded by core count)
  - Disk usage percentage
  - System memory usage

- 🔗 **Endpoint Analytics**
  - Top 5 most-requested endpoints
  - Request distribution analysis

- ⚠️ **Error Tracking**
  - Last 3 XCRI-related errors from Apache log
  - Real-time error monitoring

**Color Coding System**:
- 🟢 **Green**: Normal operation (< 50% CPU, < 100 MB RAM)
- 🟡 **Yellow**: Warning threshold (50-80% CPU, 100-200 MB RAM)
- 🔴 **Red**: Critical threshold (> 80% CPU, > 200 MB RAM)

**Deployment**:
```bash
Location: /home/web4ustfccca/mysql-migration/xcri_monitor.sh
Permissions: 755 (executable)
Usage: ./xcri_monitor.sh [interval_seconds]
```

**Usage Examples**:
```bash
# Default 10-second refresh
./xcri_monitor.sh

# High-traffic monitoring (5-second refresh)
./xcri_monitor.sh 5

# Long-term monitoring (30-second refresh)
./xcri_monitor.sh 30
```

---

### 📖 Comprehensive Monitoring Documentation

**Created**: `monitoring/README.md` (450+ lines)

**Contents**:
1. **Quick Start Guide**
   - Installation instructions
   - Basic usage examples
   - Dashboard feature overview

2. **Performance Baselines**
   - Normal load metrics (< 10 users)
   - Medium load expectations (10-50 users)
   - High load thresholds (50-100 users)

3. **Warning Thresholds**
   - Yellow warnings (investigate if sustained)
   - Red alerts (immediate action needed)

4. **Optimization Tips**
   - High CPU troubleshooting
   - Memory leak detection
   - Response time optimization
   - Error resolution

5. **Advanced Monitoring**
   - Saving logs to file
   - Background monitoring (tmux/screen)
   - Alert configuration

6. **Troubleshooting Guide**
   - Process not found
   - API down status
   - No traffic statistics
   - Database metrics showing 0

**Key Metrics to Watch During Launch**:
- CPU spikes > 50% sustained
- Memory growth > 150 MB
- Response time > 1s
- Any 5xx errors
- Slow queries

---

### 📊 Google Analytics Integration

**Property**: G-FBG8Y8ZSTW (provided by user)
**Approach**: Unified IZ Apps tracking (recommended for cross-app insights)

**Implementation**:
- Added gtag.js to `frontend/index.html`
- Positioned immediately after `<head>` (Google best practice)
- Configured with path prefix: `/iz/xcri` + pathname
- Enables unified tracking across all IZ applications

**Code Added**:
```javascript
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-FBG8Y8ZSTW"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  // Track XCRI with path prefix for unified IZ Apps tracking
  gtag('config', 'G-FBG8Y8ZSTW', {
    'page_path': '/iz/xcri' + window.location.pathname,
    'send_page_view': true
  });
</script>
```

**What's Tracked** (Automatic):
- Page views
- User location (country/city)
- Device type (desktop/mobile)
- Browser type
- Session duration
- User flow between pages

**Enhanced Measurement** (if enabled):
- Scroll tracking
- Outbound clicks
- Site search
- Video engagement
- File downloads

**Deployment**:
- Built frontend with GA integration
- Deployed to production via rsync
- Verified tracking code in production HTML
- Ready for Realtime monitoring in GA4

---

### 📘 Google Analytics Integration Guide

**Created**: `monitoring/GOOGLE_ANALYTICS.md` (400+ lines)

**Contents**:
1. **Integration Options**
   - XCRI only (simple)
   - All IZ Apps (recommended)
   - Why unified tracking is better

2. **Setup Instructions**
   - Creating GA4 property
   - Installing gtag.js (2 approaches)
   - React integration with react-ga4
   - Flask apps integration

3. **Custom Event Tracking**
   - Filter changes (division, gender, region)
   - Search queries
   - Athlete profile views
   - SCS modal opens
   - Team roster views

4. **Privacy & Compliance**
   - What data is collected
   - GDPR considerations
   - Cookie consent
   - Privacy policy updates

5. **Useful Reports**
   - Traffic analysis (Realtime, Pages and Screens)
   - User behavior (Events, Demographics)
   - Custom reports (filter usage, cross-app flow)

6. **Implementation Checklist**
   - Step-by-step for XCRI
   - Expansion to all IZ apps
   - Testing and verification

**Future Enhancements** (Optional):
- Custom event tracking with react-ga4
- Cross-app user journey analysis
- Performance monitoring via GA4
- A/B testing integration

---

## Files Created/Modified

### New Files (3)
1. **`monitoring/xcri_monitor.sh`** (488 lines)
   - Real-time monitoring dashboard
   - Production-ready bash script

2. **`monitoring/README.md`** (450+ lines)
   - Complete monitoring documentation
   - Usage guide and troubleshooting

3. **`monitoring/GOOGLE_ANALYTICS.md`** (400+ lines)
   - GA4 integration guide
   - Privacy and compliance documentation

### Modified Files (1)
1. **`frontend/index.html`**
   - Added Google Analytics tracking code
   - Positioned after `<head>` opening tag

**Total New Content**: ~1,340 lines of documentation and code

---

## Git Commits

### Commit 1: Monitoring Tools
```
[XCRI] Add real-time monitoring tools and Google Analytics integration guide

Created comprehensive monitoring solution for XCRI production deployment:
- monitoring/xcri_monitor.sh - Real-time monitoring dashboard
- monitoring/README.md - Complete monitoring documentation
- monitoring/GOOGLE_ANALYTICS.md - GA4 integration guide

Deployed xcri_monitor.sh to production server.
```

### Commit 2: GA Integration
```
[XCRI] Integrate Google Analytics tracking (G-FBG8Y8ZSTW)

Added Google Analytics 4 tracking to XCRI Rankings frontend.
Enables tracking across all IZ applications with single property.
```

### Commit 3: GA Placement Fix
```
[XCRI] Fix Google Analytics placement - move immediately after <head>

Following Google's best practice, moved gtag.js scripts to be the
first elements after <head> opening tag for optimal tracking.
```

**Total Commits**: 3
**Pushed to**: main branch

---

## Performance Baselines Established

### Current API Status (Pre-Launch)
Based on process monitoring:
- **PID**: 3909139
- **CPU Usage**: ~0.5% (very low - excellent)
- **Memory**: ~87.5 MB (stable baseline)
- **Uptime**: Since Oct 21 (24+ hours, very stable)
- **Response Time**: < 0.3s (excellent)

### Expected Load Scenarios

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

### Alert Thresholds

**⚠️ Yellow Warnings** (investigate if sustained):
- CPU > 50%
- Memory > 100 MB
- Response Time > 0.5s
- Disk > 80%
- 4xx errors present

**🔴 Red Alerts** (immediate action needed):
- CPU > 80%
- Memory > 200 MB
- Response Time > 2s
- 5xx errors present
- Slow queries (> 5s)
- Disk > 90%

---

## Verification & Testing

### Monitoring Script
- ✅ Deployed to `/home/web4ustfccca/mysql-migration/xcri_monitor.sh`
- ✅ Executable permissions set (755)
- ✅ Tested for basic functionality
- ✅ Color coding verified
- ✅ All metrics displaying correctly

### Google Analytics
- ✅ Tracking code added to index.html
- ✅ Positioned immediately after `<head>` tag
- ✅ Measurement ID: G-FBG8Y8ZSTW
- ✅ Path prefix configured: `/iz/xcri`
- ✅ Built and deployed to production
- ✅ HTML source verified in production

**Verification Steps for User**:
1. Visit https://web4.ustfccca.org/iz/xcri/
2. Open Google Analytics → Realtime
3. Should see yourself as "1 user"
4. Browser DevTools → Network → Filter "google-analytics.com"
5. Should see GA requests

---

## Production Readiness

### ✅ Monitoring Ready
- Real-time dashboard deployed
- Documentation complete
- Baselines established
- Alert thresholds defined

### ✅ Analytics Ready
- Google Analytics integrated
- Tracking code verified
- Documentation provided
- Privacy considerations documented

### ✅ Launch Support Ready
- Monitor traffic spikes
- Track user behavior
- Identify performance issues
- Debug errors in real-time

---

## Usage Guide for Launch Day

### Start Monitoring (Before Public Announcement)
```bash
# SSH to server
ssh ustfccca-web4

# Navigate to monitoring directory
cd /home/web4ustfccca/mysql-migration

# Start monitor with 5-second refresh
./xcri_monitor.sh 5

# Press Ctrl+C to exit when done
```

### What to Watch
1. **Request Rate**: Should spike when public announcement goes out
2. **Response Time**: Should stay < 1s
3. **CPU Usage**: Watch for spikes > 50%
4. **Memory**: Watch for growth > 150 MB
5. **Errors**: Any 5xx errors need immediate attention

### Long-Term Monitoring (Optional)
```bash
# Use tmux for persistent monitoring
tmux new -s xcri-monitor
./xcri_monitor.sh 30
# Ctrl+B, D to detach

# Reattach later
tmux attach -t xcri-monitor
```

---

## Google Analytics Setup Verification

### Check GA4 Dashboard
1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property (USTFCCCA IZ Apps or similar)
3. Reports → Realtime
4. Visit the site
5. Verify you appear as "1 user by page title"

### View Reports (After 24 hours)
- **Pages and Screens**: Most visited pages
- **User Acquisition**: Traffic sources
- **User Demographics**: Country, city, device type
- **Events**: Page views and interactions

---

## Future Enhancements (Optional)

### Advanced Analytics
- **Custom Events**: Track filter changes, searches, athlete views
- **React Integration**: Install react-ga4 for programmatic tracking
- **Cross-App Analysis**: Expand to all IZ apps with same property
- **Custom Dashboards**: Create focused reports in GA4

### Monitoring Improvements
- **Automated Alerts**: Email/SMS when thresholds exceeded
- **Log Aggregation**: Centralized log collection
- **Performance Profiling**: Detailed API endpoint analysis
- **Database Query Monitoring**: MySQL slow query log integration

---

## Related Documentation

- **Monitoring**: `monitoring/README.md`
- **Google Analytics**: `monitoring/GOOGLE_ANALYTICS.md`
- **Security**: `docs/SECURITY.md`
- **Session 005 Report**: `docs/sessions/session-005-october-21-2025.md`

---

## Session Statistics

### Code & Documentation
- **New Files**: 3
- **Modified Files**: 1
- **Lines Added**: ~1,340
- **Git Commits**: 3

### Tools Deployed
- ✅ Real-time monitoring dashboard
- ✅ Google Analytics tracking
- ✅ Comprehensive documentation

### Time Estimates
- **Monitoring Tool Development**: 30 minutes
- **Documentation Writing**: 20 minutes
- **GA Integration**: 10 minutes
- **Testing & Deployment**: 10 minutes
- **Total**: ~70 minutes

---

## Success Metrics

### Immediate (Today)
- ✅ Monitoring tool deployed and functional
- ✅ Google Analytics tracking live
- ✅ Documentation complete
- ✅ Ready for production launch

### Short-Term (This Week)
- Monitor traffic during public announcement
- Verify GA data collection in reports
- Establish actual performance baselines
- Identify any optimization needs

### Long-Term (Ongoing)
- Track user behavior patterns
- Optimize based on analytics insights
- Expand monitoring to other IZ apps
- Use data for future enhancements

---

## Next Steps

### For User
1. **Test Monitoring**:
   ```bash
   ssh ustfccca-web4
   cd /home/web4ustfccca/mysql-migration
   ./xcri_monitor.sh
   ```

2. **Verify Google Analytics**:
   - Visit GA4 → Realtime
   - Check for active users

3. **Monitor Launch**:
   - Run monitor during public announcement
   - Watch for performance issues
   - Track traffic spike

### For Future Sessions
- Remaining issues: #1, #3 (cosmetic fixes)
- Issue #6: Systemd service resolution
- Optional: Custom event tracking in GA4
- Optional: Expand GA to all IZ apps

---

**Session Status**: ✅ **COMPLETE**
**Production Status**: ✅ **READY FOR HIGH-TRAFFIC LAUNCH**
**Next Session**: Remaining cosmetic fixes and final polish

---

**Prepared By**: Claude Code (Session 005+)
**Date**: October 22, 2025
**Focus**: Production monitoring and analytics integration
