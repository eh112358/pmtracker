#!/bin/bash

echo "========================================="
echo "  PM Tracker - Remove Secrets from Git"
echo "========================================="
echo ""
echo "WARNING: This will rewrite Git history to remove .env file"
echo "This is necessary because the .env file contains an exposed API key."
echo ""
echo "After running this script, you MUST:"
echo "  1. Force push to remote: git push origin --force --all"
echo "  2. Rotate your API key at https://www.goldapi.io/"
echo "  3. Update your local .env with the new key"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Removing .env from Git history..."

    # Remove .env from all commits
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch .env" \
        --prune-empty --tag-name-filter cat -- --all

    if [ $? -eq 0 ]; then
        # Clean up refs
        rm -rf .git/refs/original/
        git reflog expire --expire=now --all
        git gc --prune=now --aggressive

        echo ""
        echo "✓ .env removed from Git history successfully!"
        echo ""
        echo "NEXT STEPS (IMPORTANT):"
        echo "  1. Force push to remote:"
        echo "     git push origin --force --all"
        echo ""
        echo "  2. Rotate your API key immediately:"
        echo "     Visit: https://www.goldapi.io/"
        echo "     Generate a new API key"
        echo ""
        echo "  3. Update your local .env file with the new key"
        echo "     (This file is not tracked by Git)"
        echo ""
        echo "  4. Verify .env is not in Git:"
        echo "     git ls-files | grep '\\.env$'"
        echo "     (Should return nothing)"
        echo ""
    else
        echo ""
        echo "✗ Error occurred during Git history rewrite"
        echo "Please check the error messages above"
        exit 1
    fi
else
    echo ""
    echo "Operation cancelled"
    exit 0
fi
