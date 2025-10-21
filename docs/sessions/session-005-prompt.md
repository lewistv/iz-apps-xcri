# Session 005 - Next Session Prompt

## Context

XCRI Rankings web application is 82% complete (14 of 17 issues closed). Session 004 completed the shared header integration, Athletic.net branding, and season resume integration. The application is fully deployed and operational.

**Production URL**: https://web4.ustfccca.org/iz/xcri/

---

## Remaining Open Issues

### Issue #18: Security Sweep
**Priority**: High
**Labels**: deployment, infrastructure, security
**URL**: https://github.com/lewistv/iz-apps-xcri/issues/18

**Tasks**:
- Review .env file security and permissions
- Check for exposed secrets or API keys
- Review CORS configuration
- Verify database user permissions (read-only)
- Check file permissions on server
- Review .htaccess security headers
- Ensure no sensitive data in git history
- Validate input sanitization in API endpoints

---

### Issue #6: Fix systemd service restart loop
**Priority**: Medium
**Labels**: bug, deployment, infrastructure
**URL**: https://github.com/lewistv/iz-apps-xcri/issues/6

**Current Status**: API is running via manual uvicorn + crontab (Option C from MANUAL_STARTUP.md)

**Problem**: systemd user service was configured but may have restart loop issues

**Tasks**:
- Investigate systemd service logs for restart loop cause
- Option 1: Fix systemd service configuration
- Option 2: Document crontab approach as permanent solution
- Update deployment documentation with chosen approach

---

## Additional Considerations

### Code Quality
- Review error handling across API endpoints
- Check for any TODO or FIXME comments in code
- Verify all components have proper TypeScript types (if applicable)
- Ensure consistent code style

### Performance
- Review API response times under load
- Check database query efficiency
- Verify frontend bundle size is optimized
- Test loading times for large datasets

### Documentation
- Update README.md with any new features from Session 004
- Ensure CLAUDE.md is fully up-to-date
- Verify deployment documentation is accurate
- Check that API documentation matches implementation

---

## Session 005 Suggested Focus

**Primary Goal**: Security sweep and infrastructure stability

**Suggested Approach**:

1. **Security Sweep (Issue #18)**:
   - Start with security review as it's highest priority
   - Check all environment variables and secrets
   - Review API security (CORS, input validation, SQL injection prevention)
   - Verify file permissions on server
   - Document security best practices for future maintenance

2. **Systemd Service Investigation (Issue #6)**:
   - Review current crontab setup
   - Investigate systemd service logs
   - Decide on permanent solution (systemd vs crontab)
   - Update documentation accordingly

3. **General Cleanup**:
   - Address any security findings
   - Update documentation
   - Test all functionality one final time
   - Prepare for production stability monitoring

---

## Success Criteria

Session 005 should aim to:
- ✅ Complete security sweep with no critical issues
- ✅ Resolve or document systemd service approach
- ✅ Update all documentation to reflect current state
- ✅ Achieve 100% issue completion (17/17 issues closed)

---

## Starting Point for Next Session

```
Hi Claude,

This is Session 005 for the XCRI Rankings application. We're in the final stages with 82% completion (14 of 17 issues closed).

The application is fully deployed and operational at https://web4.ustfccca.org/iz/xcri/

Focus areas for this session:
1. Security sweep (Issue #18) - Review environment security, API security, file permissions
2. Systemd service investigation (Issue #6) - Resolve restart loop or document crontab approach
3. Final documentation updates

Let's start with the security sweep. Please review:
- Environment variables and secrets (.env files)
- API security (CORS, input validation, SQL injection prevention)
- File permissions on server
- .htaccess security headers

Working directory: /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
```

---

## Reference Files

- **Main Documentation**: CLAUDE.md
- **Session History**: docs/sessions/session-004-october-21-2025.md
- **Deployment Script**: deployment/deploy-frontend.sh
- **Startup Documentation**: MANUAL_STARTUP.md
- **API Configuration**: api/.env (NOT in git)
- **GitHub Issues**: https://github.com/lewistv/iz-apps-xcri/issues

---

**Prepared**: October 21, 2025
**Previous Session**: Session 004 (Complete - Shared header integration)
**Next Session**: Session 005 (Security sweep and infrastructure)
