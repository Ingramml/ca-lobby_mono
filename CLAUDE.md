# CA Lobby Mono - Project Instructions

## Project Overview
California lobbying data visualization monorepo with React frontend and Python serverless API.

## Deployment

### Production URL
https://ca-lobbymono.vercel.app

### Deploy to Production
```bash
vercel --prod --yes
```

If Vercel CLI not authenticated, either:
1. Run `vercel login` first
2. Push to `master` branch (auto-deploys if connected)

### Required Environment Variables (Vercel)
Set these in Vercel dashboard or CLI:

| Variable | Description |
|----------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | BigQuery service account JSON (full JSON as string) |
| `BIGQUERY_PROJECT_ID` | `ca-lobby` (use `echo -n` to avoid trailing newlines) |
| `CLERK_*` | Authentication variables |

### Adding Environment Variables
```bash
# IMPORTANT: Use echo -n to avoid trailing newlines
echo -n "ca-lobby" | vercel env add BIGQUERY_PROJECT_ID production

# For JSON credentials
vercel env add GOOGLE_APPLICATION_CREDENTIALS_JSON production
# Then paste the JSON when prompted
```

### Vercel Configuration
The `vercel.json` includes:
- Python 3.12 runtime for `/api/*.py` serverless functions
- Rewrites for API routes and SPA fallback

### Common Deployment Issues

#### 500 Errors on API
1. Check `BIGQUERY_PROJECT_ID` has no trailing newline (`%0A` in URL = newline)
2. Verify `GOOGLE_APPLICATION_CREDENTIALS_JSON` is valid JSON
3. Check Vercel function logs for specific errors

#### API Not Found
Ensure `vercel.json` has `functions` and `rewrites` configured.

## Architecture

### Frontend (`/frontend`)
- React SPA
- Clerk authentication
- Charts: Recharts
- Build: `npm run build`

### API (`/api`)
- Python serverless functions (Vercel)
- BigQuery client for data queries
- Endpoints: `/api/analytics`, `/api/search`, `/api/health`

### Backend (`/backend`)
- Data pipeline scripts (not deployed)
- Documentation

## Local Development
```bash
vercel dev
```
Serves both frontend and API on localhost:3000.

## Testing API Endpoints
```bash
# Health check
curl "https://ca-lobbymono.vercel.app/api/health"

# Analytics
curl "https://ca-lobbymono.vercel.app/api/analytics?type=summary"
curl "https://ca-lobbymono.vercel.app/api/analytics?type=spending"

# Search
curl "https://ca-lobbymono.vercel.app/api/search?q=test"
```

## Git Workflow
- Main branch: `master`
- Push to master triggers Vercel auto-deploy (if connected)

## Reference Documents
- [Session Archive: Production Deployment](Session_Archives/session_2025-10-31_production-deployment.md)
- [Master Files Toolkit](~/.claude/master-files/)
