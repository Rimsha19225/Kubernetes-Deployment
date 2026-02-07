# Secret Encoding Helper

To properly encode your secrets for the Kubernetes manifest, run these commands:

## For DATABASE_URL (from backend/.env):
```bash
echo -n 'postgresql://neondb_owner:npg_hAXfM7oN1pqV@ep-empty-recipe-ahl0tehx-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require' | base64
```

## For SECRET_KEY (from backend/.env):
```bash
echo -n 'Lli0kaoi1N2l4UEpTiwK0WauXOvme2IK' | base64
```

## For BETTER_AUTH_SECRET (from backend/.env):
```bash
echo -n 'Lli0kaoi1N2l4UEpTiwK0WauXOvme2IK' | base64
```

## For COHERE_API_KEY (from backend/.env):
```bash
echo -n '738iBMR4YfDZX6ZfioIbPJpkptA3flCd64Rri1bI' | base64
```

Then replace the placeholder values in secrets.yaml with the encoded values.

Note: Both DATABASE_URL and NEON_DATABASE_URL in the .env file have identical values, so encoding either one will work. The application deployment uses the DATABASE_URL secret.