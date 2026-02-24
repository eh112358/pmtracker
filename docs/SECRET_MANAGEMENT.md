# Secret Management Guide

This guide explains how to properly manage secrets (API keys, tokens, credentials) in the PM Tracker application.

## Table of Contents
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Security Best Practices](#security-best-practices)
- [API Key Rotation](#api-key-rotation)
- [Troubleshooting](#troubleshooting)

---

## Development Setup

### Initial Setup

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Get your API key**:
   - Visit [GoldAPI.io](https://www.goldapi.io/)
   - Sign up for free account (300 requests/month)
   - Copy your API key

3. **Add your API key to `.env`**:
   ```bash
   GOLDAPI_KEY=your-actual-key-here
   ```

4. **Verify `.env` is in `.gitignore`**:
   ```bash
   # This should return nothing (file is not tracked)
   git ls-files | grep "\.env$"
   ```

### Important Warnings

⚠️ **NEVER commit `.env` file to Git!**

The `.env` file contains sensitive credentials that should NEVER be committed to version control:
- ❌ Do NOT add `.env` to Git
- ❌ Do NOT share `.env` file publicly
- ❌ Do NOT include real keys in screenshots or documentation
- ✅ DO keep `.env` local only
- ✅ DO use `.env.example` as a template

---

## Production Deployment

### Option 1: Server Environment Variables (Recommended)

Set secrets directly on your production server:

```bash
# On your server
export GOLDAPI_KEY='your-production-key-here'
export ALLOWED_ORIGINS='https://pmtracker.yourdomain.com'

# Start application
docker-compose -f docker-compose.prod.yml up -d
```

**Pros**: Simple, no files to manage
**Cons**: Secrets visible in process list

### Option 2: Docker Compose `.env` File

1. Create `.env` on production server (NOT in Git):
   ```bash
   # On production server only
   nano .env
   ```

2. Add your production configuration:
   ```bash
   GOLDAPI_KEY=your-production-key-here
   ALLOWED_ORIGINS=https://pmtracker.yourdomain.com
   DOMAIN=pmtracker.yourdomain.com
   SSL_EMAIL=your@email.com
   ```

3. Secure the file:
   ```bash
   chmod 600 .env
   chown root:root .env
   ```

4. Verify file permissions:
   ```bash
   ls -la .env
   # Should show: -rw------- (only owner can read/write)
   ```

### Option 3: Docker Secrets

For Docker Swarm deployments:

1. Create secrets directory:
   ```bash
   mkdir -p secrets
   chmod 700 secrets
   ```

2. Create secret file:
   ```bash
   echo "your-production-key-here" > secrets/goldapi_key.txt
   chmod 600 secrets/goldapi_key.txt
   ```

3. Update `docker-compose.yml`:
   ```yaml
   services:
     backend:
       secrets:
         - goldapi_key
       environment:
         - GOLDAPI_KEY_FILE=/run/secrets/goldapi_key

   secrets:
     goldapi_key:
       file: ./secrets/goldapi_key.txt
   ```

### Option 4: Secret Management Service (Advanced)

For team or enterprise deployments:

- **HashiCorp Vault**: Enterprise-grade secret management
- **AWS Secrets Manager**: If hosting on AWS
- **Azure Key Vault**: If hosting on Azure
- **Google Secret Manager**: If hosting on GCP

See `.env.example` for Vault configuration options.

---

## Security Best Practices

### 1. Never Commit Secrets to Git

✅ **DO**:
- Use `.env.example` as a template
- Keep `.env` in `.gitignore`
- Use environment variables or secret files
- Document required secrets without exposing values

❌ **DON'T**:
- Commit `.env` file
- Hardcode API keys in source code
- Share secrets in chat/email/Slack
- Include secrets in screenshots

### 2. Use Different Keys for Dev/Prod

- **Development**: Use free tier API key for testing
- **Production**: Use separate API key for production
- **Benefits**: Isolate quota, easier to rotate, better security

### 3. Rotate API Keys Regularly

- Rotate keys every **90 days** minimum
- Set calendar reminder for rotation
- Keep old key active during rotation period
- Test new key before revoking old one

### 4. Restrict API Key Permissions

If your API provider supports it:
- Limit key to specific IP addresses
- Set rate limits
- Enable read-only access where possible
- Monitor usage for anomalies

### 5. Monitor API Usage

Regularly check:
- API quota usage (avoid exhaustion)
- Unexpected spikes in requests
- Failed authentication attempts
- Geographic anomalies

### 6. Secure Production Secrets

```bash
# Set restrictive file permissions
chmod 600 .env

# Ensure ownership
chown root:root .env

# Never store in web-accessible directories
# Store outside of application root if possible
```

---

## API Key Rotation

### When to Rotate

Rotate your API key if:
- ✅ Every 90 days (routine maintenance)
- ⚠️ Key was accidentally committed to Git
- ⚠️ Key was shared in insecure channel
- ⚠️ Unusual API usage detected
- ⚠️ Team member with access left
- ⚠️ Security breach suspected

### How to Rotate

1. **Generate new key** at provider (GoldAPI.io):
   - Log in to your account
   - Navigate to API keys section
   - Generate new API key
   - Copy new key

2. **Update production environment**:
   ```bash
   # Update .env file or environment variable
   GOLDAPI_KEY=new-key-here

   # Restart application
   docker-compose restart backend
   ```

3. **Verify new key works**:
   ```bash
   # Test API endpoint
   curl http://localhost:8000/api/portfolio/prices

   # Check logs for errors
   docker-compose logs backend | grep -i "api\|error"
   ```

4. **Revoke old key** at provider:
   - Only after confirming new key works
   - Wait 24-48 hours to ensure no issues

### Emergency Rotation (Key Compromised)

If your API key is exposed:

1. **Immediately** generate new key at provider
2. **Update all environments** (dev, staging, prod)
3. **Revoke compromised key** right away
4. **Review API logs** for suspicious activity
5. **Monitor usage** for next 48 hours

---

## Troubleshooting

### "API key not found" Error

**Symptom**: Application logs show "GoldAPI key not found" or similar

**Solutions**:
1. Verify `.env` file exists and contains `GOLDAPI_KEY`
2. Check file permissions: `ls -la .env`
3. Restart application: `docker-compose restart backend`
4. Check environment variable: `docker-compose exec backend env | grep GOLDAPI_KEY`

### "401 Unauthorized" from API

**Symptom**: API returns 401 error

**Solutions**:
1. Verify API key is correct (copy-paste from provider)
2. Check for extra whitespace in `.env` file
3. Ensure key hasn't expired
4. Check API provider dashboard for key status

### "API quota exceeded"

**Symptom**: 429 Too Many Requests or quota error

**Solutions**:
1. Check current usage at API provider dashboard
2. Wait for quota reset (monthly for free tier)
3. Upgrade to paid tier if needed
4. Verify rate limiting is working (see `backend/app/services/price_service.py`)

### Environment Variables Not Loading

**Symptom**: Application can't read environment variables

**Solutions**:
1. Verify `docker-compose.yml` includes environment section
2. Check `.env` file syntax (no quotes around values)
3. Restart Docker Compose: `docker-compose down && docker-compose up -d`
4. Check Docker Compose logs: `docker-compose logs backend`

### File-Based Secrets Not Working

**Symptom**: Docker secrets not loading

**Solutions**:
1. Verify secret file exists: `ls -la secrets/`
2. Check file permissions: `chmod 600 secrets/goldapi_key.txt`
3. Ensure `_FILE` suffix in environment variable name
4. Check Docker Compose secrets configuration

---

## Quick Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOLDAPI_KEY` | Yes | API key for GoldAPI.io |
| `GOLDAPI_KEY_FILE` | No | Path to file containing API key (Docker secrets) |
| `METALS_API_KEY` | No | Alternative API key for Metals-API.com |
| `ALLOWED_ORIGINS` | No | CORS allowed origins (prod) |
| `DATABASE_URL` | No | Database connection string |

### File Locations

| File | Purpose | Tracked in Git? |
|------|---------|-----------------|
| `.env` | Local secrets | ❌ NO |
| `.env.example` | Template | ✅ Yes |
| `secrets/` | Docker secrets | ❌ NO |
| `docs/SECRET_MANAGEMENT.md` | This guide | ✅ Yes |

### Commands

```bash
# Development
cp .env.example .env              # Create local config
docker-compose up                 # Start with .env

# Production
export GOLDAPI_KEY='...'          # Set environment variable
docker-compose -f docker-compose.prod.yml up -d  # Start production

# Security
chmod 600 .env                    # Secure file permissions
git ls-files | grep "\.env$"      # Verify not tracked
```

---

## Support

If you need help with secret management:

1. Check this guide first
2. Review [Troubleshooting](#troubleshooting) section
3. Check API provider documentation
4. Review application logs: `docker-compose logs backend`

**Remember**: Never share your actual API keys when asking for help!
