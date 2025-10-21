# Feedback Form Setup Guide

The XCRI feedback form creates GitHub issues automatically when users submit feedback. This requires a GitHub Personal Access Token.

---

## Quick Setup (One-Time)

### 1. Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Token settings:
   - **Note**: "XCRI Feedback Form"
   - **Expiration**: Choose duration (recommend "90 days" or "No expiration")
   - **Scopes**: Check `repo` (Full control of private repositories)
     - This gives access to create issues in the repository
4. Click **"Generate token"**
5. **IMPORTANT**: Copy the token immediately (you won't see it again!)

### 2. Add Token to Server .env File

SSH to server and edit the .env file:

```bash
ssh ustfccca-web4
cd /home/web4ustfccca/public_html/iz/xcri/api
nano .env
```

Add/update these lines:

```bash
# GitHub Integration (for feedback form)
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_REPO=lewistv/iz-apps-xcri
```

Save and exit (Ctrl+X, Y, Enter).

### 3. Install httpx Dependency

```bash
cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate
pip install httpx>=0.25.0
```

### 4. Restart API

```bash
cd /home/web4ustfccca/public_html/iz/xcri
./deployment/restart-api.sh
```

Or manually:

```bash
pkill -f "uvicorn main:app --host 127.0.0.1 --port 8001"
cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-access.log 2>> /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log &
```

---

## Testing

### 1. Check Feedback Status

```bash
curl https://web4.ustfccca.org/iz/xcri/api/feedback/status | jq
```

Should return:

```json
{
  "configured": true,
  "repository": "lewistv/iz-apps-xcri",
  "rate_limits": {
    "per_hour": 3,
    "per_day": 10
  }
}
```

If `"configured": false`, the GitHub token is not set correctly.

### 2. Test Feedback Submission

1. Go to: https://web4.ustfccca.org/iz/xcri/feedback
2. Fill out the form with test data
3. Submit
4. Check GitHub issues: https://github.com/lewistv/iz-apps-xcri/issues
5. You should see a new issue labeled "user-feedback"

---

## Rate Limiting

To prevent spam, the feedback form has rate limits:

- **3 submissions per hour** per IP address
- **10 submissions per day** per IP address

These limits are tracked in-memory and reset when the API restarts.

---

## Security Notes

- Token is stored server-side only (never exposed to frontend)
- Token has minimal permissions (only `repo` scope for issue creation)
- Rate limiting prevents abuse
- Input is validated and sanitized before creating issues

---

## Troubleshooting

### "GitHub integration not configured" error

**Problem**: GITHUB_TOKEN not set in .env

**Solution**:
1. Check .env file exists: `ls -la /home/web4ustfccca/public_html/iz/xcri/api/.env`
2. Check token is set: `grep GITHUB_TOKEN /home/web4ustfccca/public_html/iz/xcri/api/.env`
3. Restart API after adding token

### "Failed to create GitHub issue" error

**Problem**: Token invalid or insufficient permissions

**Solution**:
1. Verify token is correct (no typos)
2. Ensure token has `repo` scope
3. Check token hasn't expired
4. Try creating new token

### Rate limit errors

**Problem**: User exceeded 3/hour or 10/day limit

**Solution**:
- Wait for rate limit to reset
- Limits are per IP address
- Limits reset hourly/daily

---

## Email Notifications

GitHub will automatically send email notifications when new issues are created:

1. Go to: https://github.com/lewistv/iz-apps-xcri/settings/notifications
2. Ensure "Issues" notifications are enabled
3. You'll receive an email for each user feedback submission

---

## Maintenance

### Rotating Tokens

If you need to rotate the token:

1. Create new token (follow setup steps above)
2. Update .env with new token
3. Restart API
4. Revoke old token in GitHub settings

### Disabling Feedback Form

To temporarily disable the feedback form:

1. Remove or comment out GITHUB_TOKEN from .env
2. Restart API
3. Users will see "GitHub integration not configured" error

---

## Files Reference

- **Backend**: `api/routes/feedback.py` - Feedback submission logic
- **Frontend**: `frontend/src/pages/Feedback.jsx` - Feedback form
- **Config**: `api/.env` - GitHub token configuration
- **Docs**: `FEEDBACK_SETUP.md` - This file

---

**Last Updated**: October 21, 2025
**Status**: Implemented, awaiting GitHub token configuration
