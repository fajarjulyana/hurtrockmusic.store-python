
#!/bin/bash

# Hurtrock Music Store - Auto Configuration Script
# Mengatur environment variables untuk database PostgreSQL

echo "🎸 Hurtrock Music Store - Auto Configuration"
echo "=============================================="

# PostgreSQL Configuration
export DATABASE_URL="postgresql://hurtrock:strong_db_pass@127.0.0.1:5432/hurtrock_db"

# Security Configuration
export SESSION_SECRET="hurtrock_session_secret_$(date +%s)"
export JWT_SECRET_KEY="hurtrock_jwt_secret_$(date +%s)"

# Flask Configuration
export FLASK_ENV="development"
export FLASK_DEBUG="1"
export IS_PRODUCTION="false"

# Server Configuration
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
export DJANGO_HOST="0.0.0.0"
export DJANGO_PORT="8000"

# Payment Configuration (Development placeholders)
export STRIPE_PUBLISHABLE_KEY="pk_test_placeholder"
export STRIPE_SECRET_KEY="sk_test_placeholder"
export MIDTRANS_SERVER_KEY="midtrans_server_key_placeholder"
export MIDTRANS_CLIENT_KEY="midtrans_client_key_placeholder"

# Email Configuration (Optional)
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="True"

echo "✅ Environment variables configured:"
echo "   DATABASE_URL: $DATABASE_URL"
echo "   FLASK_HOST: $FLASK_HOST"
echo "   FLASK_PORT: $FLASK_PORT"
echo ""
echo "🔧 To use this configuration:"
echo "   source autoconfig.sh"
echo "   python main.py"
echo ""
echo "📝 Note: Update payment gateway keys in production"
echo "=============================================="
