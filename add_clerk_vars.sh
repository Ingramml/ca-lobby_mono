#!/bin/bash
# Script to add Clerk environment variables to Vercel
# This will prompt you for the values and add them to all environments

echo "=========================================="
echo "Adding Clerk Variables to Vercel"
echo "=========================================="
echo ""

# Read values from your .env file
source .env

# Check if variables are set
if [ -z "$REACT_APP_CLERK_PUBLISHABLE_KEY" ] || [ -z "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" ] || [ -z "$CLERK_SECRET_KEY" ]; then
    echo "ERROR: One or more Clerk variables not found in .env file"
    echo "Please ensure these variables are set in .env:"
    echo "  - REACT_APP_CLERK_PUBLISHABLE_KEY"
    echo "  - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"
    echo "  - CLERK_SECRET_KEY"
    exit 1
fi

echo "Found Clerk variables in .env"
echo ""

# Add REACT_APP_CLERK_PUBLISHABLE_KEY
echo "Adding REACT_APP_CLERK_PUBLISHABLE_KEY..."
echo "$REACT_APP_CLERK_PUBLISHABLE_KEY" | vercel env add REACT_APP_CLERK_PUBLISHABLE_KEY production
echo "$REACT_APP_CLERK_PUBLISHABLE_KEY" | vercel env add REACT_APP_CLERK_PUBLISHABLE_KEY preview
echo "$REACT_APP_CLERK_PUBLISHABLE_KEY" | vercel env add REACT_APP_CLERK_PUBLISHABLE_KEY development

# Add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
echo ""
echo "Adding NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY..."
echo "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" | vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production
echo "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" | vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY preview
echo "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" | vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY development

# Add CLERK_SECRET_KEY (sensitive - only for server-side)
echo ""
echo "Adding CLERK_SECRET_KEY (sensitive)..."
echo "$CLERK_SECRET_KEY" | vercel env add CLERK_SECRET_KEY production
echo "$CLERK_SECRET_KEY" | vercel env add CLERK_SECRET_KEY preview
echo "$CLERK_SECRET_KEY" | vercel env add CLERK_SECRET_KEY development

echo ""
echo "=========================================="
echo "✅ All Clerk variables added successfully!"
echo "=========================================="
echo ""
echo "Total environment variables added: 9 (3 variables × 3 environments)"
echo ""
echo "Next step: Restart vercel dev server to pick up new variables"
echo "  1. Stop current server (Ctrl+C or kill process)"
echo "  2. Run: vercel dev --yes"
