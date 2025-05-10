# Vercel Deployment Guide for TranscriptHub

This guide contains instructions for deploying TranscriptHub on Vercel.

## Prerequisites

1. A Vercel account (free tier is fine)
2. A PostgreSQL database (options include Supabase, Neon, Railway, etc.)
3. (Optional) A Mistral AI API key

## Setup Steps

### 1. Set up your PostgreSQL Database

1. Create a PostgreSQL database on your preferred provider
2. Get the connection string in the format: `postgresql://username:password@host:port/dbname`

### 2. Deploy to Vercel

1. Connect your GitHub repository to Vercel
2. Set these environment variables in the Vercel dashboard:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A random string for session security  
   - `MISTRAL_API_KEY`: Your Mistral AI API key (optional - a demo key is included)

### 3. Configuration

The repository has already been pre-configured for Vercel deployment with:
- `vercel.json` defining build and routing configuration
- `api/index.py` as the serverless function entrypoint
- Database connection pooling optimized for serverless environments

### 4. Troubleshooting

If you encounter any issues:

1. Check Vercel build logs for errors
2. Verify that your DATABASE_URL environment variable is correct and accessible from Vercel
3. Make sure your database has the necessary tables (they should be created automatically)

### 5. Local Development

To run the application locally:

```bash
cd api
python app.py
```

The app will be available at http://localhost:5000