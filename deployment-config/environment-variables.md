# Environment Variables Configuration

## Required Environment Variables for Deployment

### Vercel Dashboard Configuration
Set these in Vercel Dashboard → Project Settings → Environment Variables:

```bash
# Clerk Authentication (REQUIRED)
REACT_APP_CLERK_PUBLISHABLE_KEY = pk_test_c3RyaWtpbmctaWd1YW5hLTgxLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY = sk_test_X3r9ydct9z3cCMj1ozWzCtXvHeOYI4HmWuojIQyTaC
```

### Environment Settings
- **Target:** Production, Preview, Development (select all)
- **Source:** Manual entry (not Git branch specific)

### Local Development .env
For local development, create `.env` file in project root:
```bash
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_c3RyaWtpbmctaWd1YW5hLTgxLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_X3r9ydct9z3cCMj1ozWzCtXvHeOYI4HmWuojIQyTaC
```

### Variable Naming Important Notes
- **Frontend variables** must start with `REACT_APP_` prefix
- **Backend variables** (like CLERK_SECRET_KEY) are server-side only
- Never commit `.env` files to Git (already in .gitignore)

### Verification Commands
```bash
# Check if environment variables are accessible:
npm start
# Look for console logs: "Clerk Key Available: true"
```