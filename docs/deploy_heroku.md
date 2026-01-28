# Deploying Homeschool Hub to Heroku

This guide covers deploying the Django application to Heroku with Cloudflare R2 for media storage.

## Prerequisites

- Heroku CLI installed and authenticated (`heroku login`)
- Cloudflare R2 bucket created with API credentials
- Git repository with latest code pushed

## 1. Create Heroku App

```powershell
heroku apps:create steadfast-scholars
```

> Replace `steadfast-scholars` with your preferred app name. The app URL will be `https://<appname>.herokuapp.com`.

## 2. Add PostgreSQL Database

```powershell
heroku addons:create heroku-postgresql:essential-0
```

This automatically sets the `DATABASE_URL` config var.

## 3. Set Environment Variables

### Required Core Settings

```powershell
# Generate a secure secret key (use Python or a password generator)
heroku config:set SECRET_KEY="your-secure-random-secret-key-here"

# IMPORTANT: Set DEBUG to false in production
heroku config:set DEBUG="false"

# IMPORTANT: Use exact hostname(s), NOT wildcards like ".herokuapp.com"
# For single domain:
heroku config:set ALLOWED_HOSTS="steadfast-scholars.herokuapp.com"

# For multiple domains (comma-separated, no spaces around commas):
heroku config:set ALLOWED_HOSTS="steadfast-scholars.herokuapp.com,www.yourdomain.com"
```

### Cloudflare R2 Storage Settings

```powershell
# Enable R2 storage for media files
heroku config:set USE_R2="true"

# R2 credentials (from Cloudflare dashboard > R2 > Manage R2 API Tokens)
heroku config:set R2_ACCESS_KEY_ID="your-r2-access-key-id"
heroku config:set R2_SECRET_ACCESS_KEY="your-r2-secret-access-key"

# R2 bucket configuration
heroku config:set R2_BUCKET_NAME="steadfast-scholars-media"
heroku config:set R2_ENDPOINT_URL="https://your-account-id.r2.cloudflarestorage.com"
heroku config:set R2_REGION="auto"
```

> **Finding your R2 endpoint URL**: In Cloudflare dashboard, go to R2 > your bucket > Settings. The endpoint format is `https://<account-id>.r2.cloudflarestorage.com`.

## 4. Deploy

```powershell
git push heroku main
```

## 5. Run Migrations

```powershell
heroku run python manage.py migrate
```

## 6. Collect Static Files

```powershell
heroku run python manage.py collectstatic --noinput
```

## 7. Create Superuser (Optional)

```powershell
heroku run python manage.py createsuperuser
```

## Verify Deployment

```powershell
# Check app status
heroku ps

# View logs
heroku logs --tail

# Open the app in browser
heroku open
```

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | `unsafe-secret-for-dev-only` | Django secret key (generate a secure random string) |
| `DEBUG` | Yes | `true` | Set to `false` in production |
| `ALLOWED_HOSTS` | Yes | localhost (dev only) | Comma-separated list of exact hostnames |
| `DATABASE_URL` | Yes | (set by Heroku) | PostgreSQL connection URL |
| `USE_R2` | No | `false` | Enable Cloudflare R2 for media storage |
| `R2_ACCESS_KEY_ID` | If USE_R2 | - | R2 API access key |
| `R2_SECRET_ACCESS_KEY` | If USE_R2 | - | R2 API secret key |
| `R2_BUCKET_NAME` | If USE_R2 | `steadfast-scholars-media` | R2 bucket name |
| `R2_ENDPOINT_URL` | If USE_R2 | - | R2 S3-compatible endpoint |
| `R2_REGION` | No | `auto` | R2 region (usually "auto") |

## Troubleshooting

### "Invalid HTTP_HOST header" error

This means `ALLOWED_HOSTS` doesn't include the hostname you're accessing. Fix:

```powershell
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
```

### Static files not loading

Run collectstatic again:

```powershell
heroku run python manage.py collectstatic --noinput --clear
```

### Media uploads failing

1. Verify R2 credentials are correct
2. Check R2 bucket permissions allow write access
3. View logs: `heroku logs --tail`

## Local Development vs Production

| Setting | Local (default) | Production |
|---------|-----------------|------------|
| `DEBUG` | `true` | `false` |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Your domain(s) |
| `USE_R2` | `false` (local media/) | `true` |
| Static files | Django dev server | WhiteNoise |
| Media files | Local `media/` folder | Cloudflare R2 |
