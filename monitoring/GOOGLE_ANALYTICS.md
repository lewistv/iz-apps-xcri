# Google Analytics Integration for XCRI Rankings

Guide for implementing Google Analytics 4 (GA4) tracking across XCRI and other IZ applications.

---

## Overview

**Two Integration Options**:

1. **XCRI Only** - Track just the XCRI Rankings application
2. **All IZ Apps** - Single GA4 property for all `/iz/*` applications (RECOMMENDED)

---

## Recommended Approach: Unified IZ Apps Tracking

### Why Unified Tracking?

✅ **Single dashboard** for all IZ applications
✅ **Shared user journey** tracking across apps
✅ **Easier cross-app analysis**
✅ **Simplified management** (one property, one tracking ID)
✅ **Better insights** into overall IZ ecosystem usage

**Applications to include**:
- `/iz/xcri/` - XCRI Rankings
- `/iz/xc-scoreboard/` - Cross Country Scoreboard
- `/iz/season-resume/` - Season Resume
- `/iz/records-lists/` - Records & Performance Lists (when deployed)

---

## Setup Steps

### 1. Create Google Analytics 4 Property

1. Go to [Google Analytics](https://analytics.google.com/)
2. Click **Admin** (bottom left)
3. Create new **Property**:
   - **Property name**: "USTFCCCA IZ Apps" or "USTFCCCA InfoZone"
   - **Reporting time zone**: Your timezone
   - **Currency**: USD

4. Create **Data Stream**:
   - Platform: **Web**
   - Website URL: `https://web4.ustfccca.org`
   - Stream name: "IZ Apps Production"
   - ✅ Enable **Enhanced measurement** (recommended)

5. **Copy Measurement ID**: `G-XXXXXXXXXX`

---

### 2. Install gtag.js in XCRI (React SPA)

#### Option A: Direct Installation (Simple)

Add to `frontend/index.html` in the `<head>` section:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  // Track XCRI with path prefix
  gtag('config', 'G-XXXXXXXXXX', {
    'page_path': '/iz/xcri' + window.location.pathname,
    'send_page_view': true
  });
</script>
```

#### Option B: React Integration (Advanced)

**Install package**:
```bash
cd frontend
npm install react-ga4
```

**Create analytics service** (`frontend/src/services/analytics.js`):
```javascript
import ReactGA from 'react-ga4';

const MEASUREMENT_ID = 'G-XXXXXXXXXX';

export const initGA = () => {
  ReactGA.initialize(MEASUREMENT_ID, {
    gaOptions: {
      siteSpeedSampleRate: 100, // Track all page load times
    },
  });
};

export const logPageView = (path) => {
  ReactGA.send({
    hitType: 'pageview',
    page: `/iz/xcri${path}`,
    title: document.title
  });
};

export const logEvent = (category, action, label) => {
  ReactGA.event({
    category: category,
    action: action,
    label: label,
  });
};

// Custom events for XCRI
export const trackDivisionChange = (division) => {
  logEvent('Filter', 'Division Change', division);
};

export const trackGenderChange = (gender) => {
  logEvent('Filter', 'Gender Change', gender);
};

export const trackSearch = (query) => {
  logEvent('Search', 'Athlete Search', query);
};

export const trackAthleteView = (athleteId, athleteName) => {
  logEvent('View', 'Athlete Profile', athleteName);
};

export const trackSCSView = (athleteId) => {
  logEvent('View', 'SCS Modal', `Athlete ${athleteId}`);
};

export const trackSnapshotChange = (date) => {
  logEvent('Snapshot', 'Historical View', date);
};
```

**Initialize in** `frontend/src/main.jsx` or `App.jsx`:
```javascript
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { initGA, logPageView } from './services/analytics';

function App() {
  const location = useLocation();

  useEffect(() => {
    // Initialize GA once on app load
    initGA();
  }, []);

  useEffect(() => {
    // Log page view on route change
    logPageView(location.pathname + location.search);
  }, [location]);

  return (
    // ... your app
  );
}
```

**Track custom events** in components:
```javascript
import { trackDivisionChange, trackAthleteView } from '../services/analytics';

// In DivisionSelector component
const handleDivisionChange = (division) => {
  setDivision(division);
  trackDivisionChange(division); // Track the filter change
};

// In AthleteTable component
const handleAthleteClick = (athlete) => {
  trackAthleteView(athlete.id, athlete.name);
  // ... navigate to athlete details
};
```

---

### 3. Install in Other IZ Apps

#### For Flask Apps (xc-scoreboard, season-resume, records-lists)

Add to base template (`shared/templates/base.html`):

```html
<!-- Add in <head> section -->
{% if config.GOOGLE_ANALYTICS_ID %}
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{ config.GOOGLE_ANALYTICS_ID }}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', '{{ config.GOOGLE_ANALYTICS_ID }}', {
    'page_path': window.location.pathname,
    'send_page_view': true
  });
</script>
{% endif %}
```

**Add to config**:
```python
# In shared/config.py or app config
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', None)
```

**Set environment variable** (in `/Users/lewistv/code/ustfccca/iz-apps-clean/env`):
```bash
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

---

## Custom Events to Track

### XCRI-Specific Events

**Filters**:
- Division selection
- Gender selection
- Region filter
- Conference filter
- Snapshot (historical view)

**User Actions**:
- Athlete search queries
- Athlete profile views
- SCS component modal views
- Team roster views
- Season resume views

**Performance**:
- Page load times
- API response times (via custom dimensions)

### Universal IZ Events

**Navigation**:
- App switching (/xcri → /xc-scoreboard)
- Cross-app user journeys

**Engagement**:
- Time on page
- Scroll depth
- Filter usage
- Search queries

---

## Privacy & Compliance

### Data Collection

**What GA4 Tracks by Default**:
- Page views
- User location (country/city)
- Device type (desktop/mobile)
- Browser type
- Session duration
- User flow between pages

**Enhanced Measurement** (optional but recommended):
- ✅ Scroll tracking
- ✅ Outbound clicks
- ✅ Site search
- ✅ Video engagement
- ✅ File downloads

### Privacy Considerations

**No PII Collection**:
- ✅ No usernames or emails
- ✅ No athlete personal data beyond names (public data)
- ✅ IP anonymization enabled (GA4 default)

**Cookie Consent**:
- Consider adding a cookie consent banner if required
- GA4 respects browser "Do Not Track" settings

**Privacy Policy**:
- Update USTFCCCA privacy policy to mention Google Analytics
- Link to [Google's privacy policy](https://policies.google.com/privacy)

**GDPR Compliance**:
- Enable IP anonymization (on by default in GA4)
- Add data retention controls in GA4 settings
- Provide opt-out mechanism if required

---

## Useful Reports in GA4

### Traffic Analysis

**Realtime Report**:
- See current users on the site
- Which pages they're viewing
- Geographic location

**Pages and Screens**:
- Most visited pages
- Engagement time per page
- Bounce rate

**User Acquisition**:
- Where users come from (direct, referral, search)
- Top referrers

### User Behavior

**Events Report**:
- Custom event tracking (filters, searches, views)
- Event count and engagement

**User Demographics**:
- Country/city
- Device category (desktop 65%, mobile 35%)
- Browser type

**Engagement**:
- Session duration
- Pages per session
- Engagement rate

### Custom Reports

**XCRI Filter Usage**:
- Track which divisions are most viewed
- Popular gender filter combinations
- Region/conference usage

**Cross-App Analysis**:
- User flow: XCRI → Scoreboard → Season Resume
- Which apps drive the most traffic
- Retention across apps

---

## Implementation Checklist

### XCRI Only

- [ ] Create GA4 property
- [ ] Get Measurement ID (G-XXXXXXXXXX)
- [ ] Add gtag.js to `frontend/index.html`
- [ ] Test tracking with GA Debugger Chrome extension
- [ ] Verify page views in GA4 Realtime report
- [ ] (Optional) Install react-ga4 for custom events
- [ ] (Optional) Add custom event tracking
- [ ] Deploy to production
- [ ] Monitor in GA4 dashboard

### All IZ Apps (Recommended)

- [ ] Create unified GA4 property ("USTFCCCA IZ Apps")
- [ ] Get Measurement ID
- [ ] **XCRI**: Add gtag.js to React SPA
- [ ] **XC Scoreboard**: Add to Flask base template
- [ ] **Season Resume**: Add to Flask base template
- [ ] **Records Lists**: Add to Flask base template (when deployed)
- [ ] Add `GOOGLE_ANALYTICS_ID` to environment config
- [ ] Test each app with GA Debugger
- [ ] Deploy all apps
- [ ] Create custom dashboard in GA4
- [ ] Set up useful reports

---

## Testing

### Before Deployment

**Chrome Extension**: [Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/)

1. Install extension
2. Enable debugger
3. Visit your local dev site (`http://localhost:5173` for XCRI)
4. Open browser console
5. Look for GA debug messages

**Expected output**:
```
Running Google Analytics Debugger
Tracking ID: G-XXXXXXXXXX
Page view sent: /iz/xcri/
```

### After Deployment

1. Visit production URL: `https://web4.ustfccca.org/iz/xcri/`
2. Open GA4 → **Realtime** report
3. Verify you see yourself as "1 user by page title"
4. Click through the app (filters, searches, etc.)
5. Verify events appear in Realtime → Events

---

## Advanced: Tag Manager (Optional)

For more complex tracking, consider **Google Tag Manager**:

✅ **Benefits**:
- Add/modify tracking without code deploys
- A/B testing integration
- Third-party tag management
- Version control for tags

❌ **Drawbacks**:
- More complex setup
- Additional script to load
- May be overkill for simple tracking

**When to use**: If you plan to add Facebook Pixel, LinkedIn tracking, or other marketing tags.

---

## Monitoring & Maintenance

### Weekly

- Check Realtime report during high-traffic periods
- Monitor custom events firing correctly

### Monthly

- Review Pages and Screens report
- Analyze user acquisition sources
- Check engagement metrics
- Identify popular features/filters

### Quarterly

- Review and update custom events
- Check privacy compliance
- Analyze cross-app user journeys
- Optimize based on insights

---

## Example: Reading the Data

### Question: "How many users view the XCRI rankings each day?"

**GA4 Path**: Reports → Life Cycle → Engagement → Pages and Screens

- Filter by page path: `/iz/xcri/`
- Metric: "Views"
- Dimension: "Date"
- Date range: Last 30 days

### Question: "Which division is most popular?"

**Requires custom events** (Option B implementation)

**GA4 Path**: Reports → Life Cycle → Engagement → Events

- Event: `division_change`
- Dimension: `event_label` (division code)
- Metric: Event count
- Sort by count descending

### Question: "Do users switch between apps?"

**GA4 Path**: Explore → Path Exploration

- Starting point: Page path contains `/iz/xcri/`
- Show next pages visited
- Look for transitions to `/iz/xc-scoreboard/`, `/iz/season-resume/`

---

## Troubleshooting

### No data appearing in GA4

1. **Check Measurement ID**: Verify it's correct in the code
2. **Check network requests**: Open DevTools → Network → Filter `google-analytics.com`
3. **Ad blockers**: Disable ad blockers during testing
4. **Browser privacy settings**: Some browsers block GA by default
5. **Time delay**: Realtime data is instant, but reports take 24-48 hours

### Page views not recording

1. **SPA routing**: For React, ensure `logPageView()` is called on route change
2. **Path prefix**: Verify `/iz/xcri` prefix is being added
3. **Test with GA Debugger**: Check console output

### Custom events not firing

1. **Check event syntax**: `ReactGA.event({category, action, label})`
2. **Verify event is called**: Add `console.log()` before event tracking
3. **Check Realtime → Events**: Should appear within seconds

---

## Cost

**Google Analytics 4 is FREE** for standard use:
- Up to 10 million events per month (more than enough)
- Unlimited properties
- No credit card required

**Paid version** (Analytics 360):
- Only needed for enterprise (> 10M events/month)
- Costs $150,000+/year
- Not necessary for USTFCCCA

---

## Next Steps

1. **Decide on scope**: XCRI only or all IZ apps?
2. **Create GA4 property**: Get Measurement ID
3. **Implement tracking**: Add gtag.js to applications
4. **Test locally**: Verify with GA Debugger
5. **Deploy to production**: Push changes
6. **Monitor**: Check Realtime report
7. **Analyze**: Review reports after 1 week

---

## Additional Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics/answer/10089681)
- [react-ga4 Documentation](https://github.com/PriceRunner/react-ga4)
- [GA4 Best Practices](https://support.google.com/analytics/answer/9964640)
- [Privacy & Data Collection](https://support.google.com/analytics/topic/2919631)

---

**Recommended**: Start with **Option A (Direct Installation)** for XCRI, then expand to all IZ apps once proven. Add **Option B (React Integration)** later for custom event tracking.

**Last Updated**: October 22, 2025
**Author**: Claude Code
