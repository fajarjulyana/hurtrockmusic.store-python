# Panduan Maintainer Hurtrock Music Store

## Daftar Isi
- [Pendahuluan](#pendahuluan)
- [Server Management](#server-management)
- [Database Maintenance](#database-maintenance)
- [Backup & Recovery](#backup--recovery)
- [Performance Monitoring](#performance-monitoring)
- [Security Maintenance](#security-maintenance)
- [Log Management](#log-management)
- [Updates & Patches](#updates--patches)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Alerting](#monitoring--alerting)
- [Disaster Recovery](#disaster-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [Documentation Updates](#documentation-updates)

## Pendahuluan

Sebagai maintainer untuk Hurtrock Music Store, tanggung jawab utama meliputi memastikan aplikasi berjalan dengan optimal, aman, dan stabil. Panduan ini mencakup semua aspek maintenance operasional dari infrastruktur hingga aplikasi level.

### Responsibility Overview

**Daily Tasks**:
- ✅ Monitor sistem health dan performance
- ✅ Check error logs dan resolve issues
- ✅ Verify backup completion
- ✅ Monitor disk space dan resource usage
- ✅ Check security alerts

**Weekly Tasks**:
- 📊 Performance analysis dan optimization
- 🔄 Update sistem dan dependencies
- 🗄️ Database maintenance dan optimization
- 📋 Review monitoring metrics
- 🔒 Security audit dan updates

**Monthly Tasks**:
- 📈 Capacity planning review
- 💾 Backup retention management
- 📊 Generate performance reports
- 🔄 Major updates planning
- 📝 Documentation updates

## Server Management

### Server Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                    (Nginx/HAProxy)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐      ┌────▼────┐      ┌────▼────┐
│ Web    │      │ Web     │      │ Web     │
│ Server │      │ Server  │      │ Server  │
│ Node 1 │      │ Node 2  │      │ Node 3  │
└───┬────┘      └────┬────┘      └────┬────┘
    │                │                │
    └─────────────────┼─────────────────┘
                      │
              ┌───────▼───────┐
              │   Database    │
              │  (PostgreSQL) │
              └───────────────┘
```

### System Requirements

**Minimum Requirements**:
- **CPU**: 2 vCPU cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **Network**: 100Mbps

**Recommended Production**:
- **CPU**: 4 vCPU cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 1Gbps

### Server Health Monitoring

**System Metrics to Monitor**:
```bash
# CPU Usage
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'

# Memory Usage
free -m | awk 'NR==2{printf "%.2f%%\n", $3*100/$2 }'

# Disk Usage
df -h | awk '$NF=="/"{printf "%s\n", $5}'

# Network Connections
netstat -an | grep :5000 | wc -l

# Process Status
ps aux | grep python | grep -v grep
```

**Automated Health Check Script**:
```bash
#!/bin/bash
# health_check.sh

LOG_FILE="/var/log/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log with timestamp
log_message() {
    echo "[$DATE] $1" >> $LOG_FILE
}

# Check if application is running
if pgrep -f "python main.py" > /dev/null; then
    log_message "✅ Application is running"
else
    log_message "❌ Application is NOT running"
    # Restart application
    systemctl restart hurtrock-app
    log_message "🔄 Application restarted"
fi

# Check database connection
if pg_isready -h localhost -p 5432 > /dev/null; then
    log_message "✅ Database is accessible"
else
    log_message "❌ Database connection failed"
    # Alert mechanism
    echo "Database down!" | mail -s "ALERT: Database Down" admin@hurtrock.com
fi

# Check disk space (alert if > 80%)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log_message "⚠️ Disk usage high: ${DISK_USAGE}%"
    echo "Disk usage: ${DISK_USAGE}%" | mail -s "WARNING: High Disk Usage" admin@hurtrock.com
else
    log_message "✅ Disk usage normal: ${DISK_USAGE}%"
fi

# Check memory usage (alert if > 90%)
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEM_USAGE -gt 90 ]; then
    log_message "⚠️ Memory usage high: ${MEM_USAGE}%"
else
    log_message "✅ Memory usage normal: ${MEM_USAGE}%"
fi

log_message "Health check completed"
```

### Process Management

**Systemd Service Configuration**:
```ini
# /etc/systemd/system/hurtrock-app.service
[Unit]
Description=Hurtrock Music Store Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/hurtrock
Environment=PATH=/var/www/hurtrock/venv/bin
Environment=FLASK_ENV=production
EnvironmentFile=/var/www/hurtrock/.env
ExecStart=/var/www/hurtrock/venv/bin/gunicorn --workers 4 --bind unix:/var/run/hurtrock.sock --pid /var/run/hurtrock.pid --daemon main:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PIDFile=/var/run/hurtrock.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Service Management Commands**:
```bash
# Start service
sudo systemctl start hurtrock-app

# Stop service
sudo systemctl stop hurtrock-app

# Restart service
sudo systemctl restart hurtrock-app

# Enable auto-start
sudo systemctl enable hurtrock-app

# Check status
sudo systemctl status hurtrock-app

# View logs
sudo journalctl -u hurtrock-app -f
```

## Database Maintenance

### PostgreSQL Maintenance Tasks

**Daily Maintenance**:
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('hurtrock_music_store'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Check long running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

**Weekly Maintenance**:
```sql
-- Vacuum and analyze all tables
VACUUM ANALYZE;

-- Update table statistics
ANALYZE;

-- Check for bloated tables
SELECT 
    schemaname, 
    tablename, 
    attname, 
    n_distinct, 
    correlation 
FROM pg_stats 
WHERE schemaname = 'public';

-- Reindex if needed
REINDEX INDEX CONCURRENTLY idx_products_name;
REINDEX INDEX CONCURRENTLY idx_products_category_id;
```

**Performance Tuning**:
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public';

-- Add indexes for performance
CREATE INDEX CONCURRENTLY idx_orders_created_at ON orders(created_at);
CREATE INDEX CONCURRENTLY idx_chat_messages_room_id ON chat_messages(chat_room_id);
CREATE INDEX CONCURRENTLY idx_products_is_active ON products(is_active) WHERE is_active = true;
```

### Database Monitoring Script

```bash
#!/bin/bash
# db_monitoring.sh

DB_NAME="hurtrock_music_store"
LOG_FILE="/var/log/db_monitoring.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check database connections
CONNECTIONS=$(psql -d $DB_NAME -t -c "SELECT count(*) FROM pg_stat_activity;")
echo "[$DATE] Active connections: $CONNECTIONS" >> $LOG_FILE

# Check database size
DB_SIZE=$(psql -d $DB_NAME -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
echo "[$DATE] Database size: $DB_SIZE" >> $LOG_FILE

# Check for locks
LOCKS=$(psql -d $DB_NAME -t -c "SELECT count(*) FROM pg_locks WHERE granted = false;")
if [ $LOCKS -gt 0 ]; then
    echo "[$DATE] WARNING: $LOCKS ungranted locks found" >> $LOG_FILE
fi

# Check for long-running queries
LONG_QUERIES=$(psql -d $DB_NAME -t -c "SELECT count(*) FROM pg_stat_activity WHERE (now() - query_start) > interval '5 minutes' AND state = 'active';")
if [ $LONG_QUERIES -gt 0 ]; then
    echo "[$DATE] WARNING: $LONG_QUERIES long-running queries found" >> $LOG_FILE
fi
```

## Backup & Recovery

### Automated Backup Strategy

**Backup Types**:
1. **Daily**: Incremental database backup
2. **Weekly**: Full database backup + application files
3. **Monthly**: Complete system backup

**Database Backup Script**:
```bash
#!/bin/bash
# backup_database.sh

DB_NAME="hurtrock_music_store"
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/hurtrock_db_$DATE.sql"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Log backup completion
echo "$(date): Database backup completed: ${BACKUP_FILE}.gz" >> /var/log/backup.log

# Verify backup integrity
if gunzip -t "${BACKUP_FILE}.gz"; then
    echo "$(date): Backup verification successful" >> /var/log/backup.log
else
    echo "$(date): ERROR: Backup verification failed!" >> /var/log/backup.log
    # Send alert email
    echo "Database backup verification failed!" | mail -s "BACKUP ERROR" admin@hurtrock.com
fi
```

**Application Files Backup**:
```bash
#!/bin/bash
# backup_application.sh

APP_DIR="/var/www/hurtrock"
BACKUP_DIR="/backups/application"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/hurtrock_app_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create application backup (exclude venv and logs)
tar -czf $BACKUP_FILE -C $APP_DIR \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='.git' \
    .

# Remove backups older than 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "$(date): Application backup completed: $BACKUP_FILE" >> /var/log/backup.log
```

**Crontab Configuration**:
```bash
# Daily database backup at 2 AM
0 2 * * * /usr/local/bin/backup_database.sh

# Weekly application backup on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/backup_application.sh

# Daily health check every hour
0 * * * * /usr/local/bin/health_check.sh
```

### Recovery Procedures

**Database Recovery**:
```bash
# Stop application
sudo systemctl stop hurtrock-app

# Drop existing database (CAUTION!)
dropdb hurtrock_music_store

# Create new database
createdb hurtrock_music_store

# Restore from backup
gunzip -c /backups/database/hurtrock_db_20231215_020001.sql.gz | psql hurtrock_music_store

# Restart application
sudo systemctl start hurtrock-app

# Verify recovery
psql hurtrock_music_store -c "SELECT count(*) FROM users;"
```

**Application Recovery**:
```bash
# Stop application
sudo systemctl stop hurtrock-app

# Backup current (corrupted) version
mv /var/www/hurtrock /var/www/hurtrock_corrupted_$(date +%Y%m%d)

# Restore from backup
cd /var/www
tar -xzf /backups/application/hurtrock_app_20231215_030001.tar.gz
mv hurtrock_restored hurtrock

# Restore virtual environment
cd /var/www/hurtrock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Restore environment file
cp /backups/config/.env /var/www/hurtrock/

# Set permissions
chown -R www-data:www-data /var/www/hurtrock

# Start application
sudo systemctl start hurtrock-app
```

## Performance Monitoring

### Application Performance Metrics

**Key Metrics to Monitor**:
- Response time (avg, p95, p99)
- Throughput (requests per second)
- Error rate (4xx, 5xx responses)
- Database query time
- Memory usage
- CPU utilization
- Disk I/O

**Performance Monitoring Script**:
```bash
#!/bin/bash
# performance_monitor.sh

LOG_FILE="/var/log/performance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Function to get response time
check_response_time() {
    local url=$1
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' $url)
    echo $response_time
}

# Check homepage response time
HOMEPAGE_TIME=$(check_response_time "http://localhost:5000/")
echo "[$DATE] Homepage response time: ${HOMEPAGE_TIME}s" >> $LOG_FILE

# Check admin dashboard response time
ADMIN_TIME=$(check_response_time "http://localhost:5000/admin/dashboard")
echo "[$DATE] Admin dashboard response time: ${ADMIN_TIME}s" >> $LOG_FILE

# Check database query performance
DB_QUERY_TIME=$(psql -d hurtrock_music_store -t -c "
    SELECT extract(epoch from now() - query_start) 
    FROM pg_stat_activity 
    WHERE state = 'active' AND query != '<IDLE>' 
    ORDER BY query_start 
    LIMIT 1;
")
echo "[$DATE] Longest running query: ${DB_QUERY_TIME}s" >> $LOG_FILE

# Memory usage
MEM_USAGE=$(ps aux | grep '[p]ython main.py' | awk '{sum+=$6} END {print sum/1024 " MB"}')
echo "[$DATE] Application memory usage: $MEM_USAGE" >> $LOG_FILE
```

### Performance Optimization

**Database Optimization**:
```sql
-- Enable query timing
\timing on

-- Check query performance
EXPLAIN ANALYZE SELECT * FROM products WHERE category_id = 1 AND is_active = true;

-- Optimize frequent queries
CREATE INDEX CONCURRENTLY idx_products_category_active ON products(category_id, is_active);

-- Update table statistics
ANALYZE products;

-- Check for unused indexes
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
WHERE idx_tup_read = 0;
```

**Application Optimization**:
```python
# Implement caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def get_category_products(category_id):
    return Product.query.filter_by(category_id=category_id, is_active=True).all()

# Use database session efficiently
def bulk_update_products(product_updates):
    try:
        for product_id, data in product_updates.items():
            db.session.execute(
                update(Product).where(Product.id == product_id).values(**data)
            )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
```

## Security Maintenance

### Security Monitoring

**Daily Security Checks**:
```bash
#!/bin/bash
# security_check.sh

LOG_FILE="/var/log/security.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check for failed login attempts
FAILED_LOGINS=$(grep "Failed login" /var/log/nginx/access.log | wc -l)
echo "[$DATE] Failed login attempts: $FAILED_LOGINS" >> $LOG_FILE

# Check for suspicious URLs
SUSPICIOUS=$(grep -E "(\.\.\/|<script|DROP TABLE)" /var/log/nginx/access.log | wc -l)
if [ $SUSPICIOUS -gt 0 ]; then
    echo "[$DATE] WARNING: $SUSPICIOUS suspicious requests found" >> $LOG_FILE
fi

# Check open ports
OPEN_PORTS=$(nmap -sT localhost | grep "open" | wc -l)
echo "[$DATE] Open ports: $OPEN_PORTS" >> $LOG_FILE

# Check SSL certificate expiry
SSL_EXPIRY=$(openssl x509 -in /etc/ssl/certs/hurtrock.crt -noout -dates | grep "notAfter" | cut -d= -f2)
echo "[$DATE] SSL certificate expires: $SSL_EXPIRY" >> $LOG_FILE
```

**Security Updates**:
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip list --outdated
pip install --upgrade package_name

# Check for security vulnerabilities
pip-audit

# Update SSL certificates (Let's Encrypt)
sudo certbot renew --dry-run
```

### Access Control

**File Permissions**:
```bash
# Set proper file permissions
chmod 755 /var/www/hurtrock
chmod 644 /var/www/hurtrock/*.py
chmod 600 /var/www/hurtrock/.env
chown -R www-data:www-data /var/www/hurtrock
```

**Firewall Configuration**:
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Log Management

### Log Configuration

**Application Logging**:
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/hurtrock.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Hurtrock Music Store startup')
```

**Log Rotation**:
```bash
# /etc/logrotate.d/hurtrock
/var/log/hurtrock/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload hurtrock-app
    endscript
}
```

### Log Analysis

**Daily Log Analysis Script**:
```bash
#!/bin/bash
# analyze_logs.sh

LOG_DIR="/var/log/hurtrock"
REPORT_FILE="/var/log/daily_report_$(date +%Y%m%d).txt"
DATE=$(date '+%Y-%m-%d')

echo "Daily Log Analysis Report - $DATE" > $REPORT_FILE
echo "===========================================" >> $REPORT_FILE

# Error count
ERROR_COUNT=$(grep -c "ERROR" $LOG_DIR/hurtrock.log)
echo "Total Errors: $ERROR_COUNT" >> $REPORT_FILE

# Warning count
WARNING_COUNT=$(grep -c "WARNING" $LOG_DIR/hurtrock.log)
echo "Total Warnings: $WARNING_COUNT" >> $REPORT_FILE

# Top error messages
echo -e "\nTop Error Messages:" >> $REPORT_FILE
grep "ERROR" $LOG_DIR/hurtrock.log | awk -F'ERROR: ' '{print $2}' | sort | uniq -c | sort -nr | head -5 >> $REPORT_FILE

# Request statistics from nginx logs
echo -e "\nRequest Statistics:" >> $REPORT_FILE
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -nr >> $REPORT_FILE

# Database connection errors
DB_ERRORS=$(grep -c "database.*error" $LOG_DIR/hurtrock.log)
echo -e "\nDatabase Errors: $DB_ERRORS" >> $REPORT_FILE

# Send report via email
mail -s "Daily Log Report - $DATE" admin@hurtrock.com < $REPORT_FILE
```

## Updates & Patches

### Update Procedure

**Security Updates (Priority: High)**:
```bash
# 1. Create backup
/usr/local/bin/backup_database.sh
/usr/local/bin/backup_application.sh

# 2. Update system packages
sudo apt update
sudo apt list --upgradable
sudo apt upgrade -y

# 3. Update Python dependencies
source /var/www/hurtrock/venv/bin/activate
pip list --outdated
pip install --upgrade package_name

# 4. Test application
python -m pytest tests/

# 5. Restart services
sudo systemctl restart hurtrock-app
sudo systemctl restart nginx

# 6. Verify functionality
curl -f http://localhost:5000/
```

**Application Updates**:
```bash
# 1. Backup current version
cp -r /var/www/hurtrock /var/www/hurtrock_backup_$(date +%Y%m%d)

# 2. Pull latest code
cd /var/www/hurtrock
git fetch origin
git checkout main
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run database migrations
flask db upgrade

# 5. Restart application
sudo systemctl restart hurtrock-app

# 6. Monitor logs
tail -f /var/log/hurtrock/hurtrock.log
```

### Testing Updates

**Pre-deployment Testing**:
```bash
# Create staging environment
cp -r /var/www/hurtrock /var/www/hurtrock_staging

# Test database migration
cd /var/www/hurtrock_staging
flask db upgrade

# Run automated tests
python -m pytest tests/ -v

# Performance test
ab -n 100 -c 10 http://localhost:5001/

# Security scan
nmap -sV localhost
```

## Troubleshooting

### Common Issues

**Application Won't Start**:
```bash
# Check service status
sudo systemctl status hurtrock-app

# Check logs
sudo journalctl -u hurtrock-app -f

# Check if port is available
sudo lsof -i :5000

# Check dependencies
source /var/www/hurtrock/venv/bin/activate
pip check

# Test application manually
cd /var/www/hurtrock
python main.py
```

**Database Connection Issues**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -d hurtrock_music_store -c "SELECT 1;"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log

# Check connection limits
psql -d postgres -c "SELECT setting FROM pg_settings WHERE name='max_connections';"
```

**High Memory Usage**:
```bash
# Check memory usage by process
ps aux --sort=-%mem | head

# Check for memory leaks
top -p $(pgrep -f "python main.py")

# Check swap usage
cat /proc/swaps
free -h

# Restart application if needed
sudo systemctl restart hurtrock-app
```

**Slow Performance**:
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check for blocking queries
SELECT blocked_locks.pid     AS blocked_pid,
       blocked_activity.usename  AS blocked_user,
       blocking_locks.pid     AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query    AS blocked_statement,
       blocking_activity.query   AS current_statement_in_blocking_process
FROM  pg_catalog.pg_locks         blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity  ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks         blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.GRANTED;
```

## Monitoring & Alerting

### Monitoring Setup

**Metrics Collection**:
```bash
#!/bin/bash
# collect_metrics.sh

METRICS_FILE="/var/log/metrics_$(date +%Y%m%d_%H%M).json"

# Collect system metrics
cat << EOF > $METRICS_FILE
{
    "timestamp": "$(date -Iseconds)",
    "cpu_usage": $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'),
    "memory_usage": $(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}'),
    "disk_usage": $(df / | tail -1 | awk '{print $5}' | sed 's/%//'),
    "active_connections": $(netstat -an | grep :5000 | wc -l),
    "database_size": "$(psql -d hurtrock_music_store -t -c "SELECT pg_size_pretty(pg_database_size('hurtrock_music_store'));" | xargs)",
    "error_count": $(grep -c "ERROR" /var/log/hurtrock/hurtrock.log),
    "response_time": $(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/)
}
EOF

# Send metrics to monitoring system
# curl -X POST -H "Content-Type: application/json" -d @$METRICS_FILE http://monitoring-server/api/metrics
```

**Alert Configuration**:
```bash
#!/bin/bash
# check_alerts.sh

# CPU usage > 80%
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "High CPU usage: $CPU_USAGE%" | mail -s "ALERT: High CPU Usage" admin@hurtrock.com
fi

# Memory usage > 85%
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEM_USAGE -gt 85 ]; then
    echo "High memory usage: $MEM_USAGE%" | mail -s "ALERT: High Memory Usage" admin@hurtrock.com
fi

# Disk usage > 85%
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "High disk usage: $DISK_USAGE%" | mail -s "ALERT: High Disk Usage" admin@hurtrock.com
fi

# Response time > 5 seconds
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/)
if (( $(echo "$RESPONSE_TIME > 5" | bc -l) )); then
    echo "Slow response time: $RESPONSE_TIME seconds" | mail -s "ALERT: Slow Response Time" admin@hurtrock.com
fi
```

## Disaster Recovery

### Disaster Recovery Plan

**RTO (Recovery Time Objective)**: 4 hours
**RPO (Recovery Point Objective)**: 24 hours

**Recovery Scenarios**:

1. **Database Corruption**:
   - Restore from latest backup
   - Rebuild from transaction logs
   - Estimated downtime: 2-4 hours

2. **Server Hardware Failure**:
   - Migrate to backup server
   - Restore application and data
   - Estimated downtime: 4-6 hours

3. **Data Center Outage**:
   - Failover to secondary data center
   - DNS update for traffic routing
   - Estimated downtime: 6-8 hours

**Recovery Procedures**:

```bash
#!/bin/bash
# disaster_recovery.sh

SCENARIO=$1
BACKUP_DATE=$2

case $SCENARIO in
    "database")
        echo "Starting database recovery..."
        # Stop application
        sudo systemctl stop hurtrock-app
        
        # Restore database
        dropdb hurtrock_music_store
        createdb hurtrock_music_store
        gunzip -c /backups/database/hurtrock_db_$BACKUP_DATE.sql.gz | psql hurtrock_music_store
        
        # Start application
        sudo systemctl start hurtrock-app
        echo "Database recovery completed"
        ;;
        
    "full")
        echo "Starting full system recovery..."
        # Restore application files
        tar -xzf /backups/application/hurtrock_app_$BACKUP_DATE.tar.gz -C /var/www/
        
        # Restore database
        dropdb hurtrock_music_store
        createdb hurtrock_music_store
        gunzip -c /backups/database/hurtrock_db_$BACKUP_DATE.sql.gz | psql hurtrock_music_store
        
        # Restart services
        sudo systemctl restart hurtrock-app
        sudo systemctl restart nginx
        echo "Full recovery completed"
        ;;
        
    *)
        echo "Usage: $0 [database|full] [backup_date]"
        echo "Example: $0 database 20231215_020001"
        ;;
esac
```

## Maintenance Procedures

### Planned Maintenance

**Monthly Maintenance Checklist**:

- [ ] Update system packages
- [ ] Update Python dependencies
- [ ] Database maintenance (vacuum, analyze)
- [ ] Log rotation and cleanup
- [ ] Backup verification
- [ ] Security patches
- [ ] Performance review
- [ ] Disk cleanup
- [ ] SSL certificate renewal
- [ ] Monitoring system check

**Maintenance Window Protocol**:

1. **Pre-maintenance**:
   - Schedule maintenance window
   - Notify stakeholders
   - Create full backup
   - Prepare rollback plan

2. **During maintenance**:
   - Enable maintenance mode
   - Perform updates
   - Test functionality
   - Monitor system health

3. **Post-maintenance**:
   - Verify all services
   - Performance testing
   - Update documentation
   - Maintenance report

### Emergency Maintenance

```bash
#!/bin/bash
# emergency_maintenance.sh

echo "Starting emergency maintenance..."

# 1. Enable maintenance mode
echo "Maintenance in progress..." > /var/www/hurtrock/templates/maintenance.html

# 2. Stop application gracefully
sudo systemctl stop hurtrock-app

# 3. Create emergency backup
pg_dump hurtrock_music_store > /tmp/emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# 4. Perform emergency fixes
# (Emergency fixes would go here)

# 5. Start application
sudo systemctl start hurtrock-app

# 6. Disable maintenance mode
rm /var/www/hurtrock/templates/maintenance.html

# 7. Verify functionality
curl -f http://localhost:5000/

echo "Emergency maintenance completed"
```

## Documentation Updates

### Maintenance Documentation

**Daily Reports**:
- System health status
- Performance metrics
- Error summary
- Backup status

**Weekly Reports**:
- Performance trends
- Capacity planning
- Security incidents
- Update log

**Monthly Reports**:
- System utilization
- Cost analysis
- Maintenance summary
- Improvement recommendations

**Documentation Template**:
```markdown
# Maintenance Report - [Date]

## System Status
- **Uptime**: 99.9%
- **Average Response Time**: 250ms
- **Error Rate**: 0.1%

## Maintenance Activities
- [ ] System updates applied
- [ ] Database maintenance completed
- [ ] Backup verification passed
- [ ] Security scan completed

## Issues Resolved
1. Issue description
   - Root cause
   - Resolution
   - Prevention measures

## Performance Metrics
- CPU usage: avg 45%, peak 78%
- Memory usage: avg 60%, peak 85%
- Disk usage: 65%

## Recommendations
1. Upgrade memory to handle peak loads
2. Implement additional monitoring
3. Schedule database optimization

## Next Maintenance Window
- **Date**: [Next maintenance date]
- **Duration**: 2 hours
- **Scope**: Security updates and performance optimization
```

---

## Emergency Contacts

**Technical Team**:
- **Lead Developer**: [Contact info]
- **System Administrator**: [Contact info]
- **Database Administrator**: [Contact info]

**Vendors**:
- **Hosting Provider**: [Contact info]
- **Payment Gateway**: [Contact info]
- **SSL Certificate**: [Contact info]

**Escalation Matrix**:
1. **Level 1**: Technical team (0-2 hours)
2. **Level 2**: Senior management (2-4 hours)
3. **Level 3**: External vendors (4+ hours)

---

*Panduan ini harus direvisi setiap 6 bulan atau setelah perubahan sistem yang signifikan. Untuk informasi teknis tambahan, hubungi tim development.*