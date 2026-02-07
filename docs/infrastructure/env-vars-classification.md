# Environment Variables Classification for Kubernetes Secrets

## Frontend Environment Variables (.env)
- NEXT_PUBLIC_API_BASE_URL: Non-sensitive, can be in ConfigMap
- NEXT_PUBLIC_APP_URL: Non-sensitive, can be in ConfigMap

## Backend Environment Variables (.env)
### Non-sensitive variables (ConfigMap):
- APP_NAME
- DEBUG
- ENVIRONMENT
- DB_ECHO
- ACCESS_TOKEN_EXPIRE_MINUTES
- ALGORITHM
- BETTER_AUTH_URL
- LOG_LEVEL
- LOG_FILE
- ALLOWED_ORIGINS
- BACKEND_URL
- FRONTEND_URL

### Sensitive variables (Secrets):
- DATABASE_URL: Database connection string with credentials
- NEON_DATABASE_URL: Neon database URL with credentials
- SECRET_KEY: JWT secret key
- BETTER_AUTH_SECRET: Better Auth secret
- COHERE_API_KEY: API key for Cohere AI service