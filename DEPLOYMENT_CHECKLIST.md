# ServiceLink - Deployment Checklist

## Pre-Deployment

- [ ] All tests passing (`pytest`)
- [ ] Environment variables configured
- [ ] Secret key changed from default
- [ ] Database migrations up to date
- [ ] Static files collected/optimized
- [ ] Dependencies updated and reviewed
- [ ] Security headers configured
- [ ] HTTPS certificates obtained
- [ ] Backup strategy in place

## Production Configuration

- [ ] Set `FLASK_ENV=production`
- [ ] Configure PostgreSQL database
- [ ] Set strong `SECRET_KEY`
- [ ] Enable `SESSION_COOKIE_SECURE`
- [ ] Configure email settings (if using)
- [ ] Set up logging (file-based or service)
- [ ] Configure rate limiting
- [ ] Set up monitoring/error tracking

## Server Setup

- [ ] Install Python 3.8+
- [ ] Install PostgreSQL
- [ ] Install and configure Nginx/Apache
- [ ] Install and configure Gunicorn/uWSGI
- [ ] Set up systemd service
- [ ] Configure firewall rules
- [ ] Set up SSL/TLS with Let's Encrypt
- [ ] Configure log rotation

## Database

- [ ] Create production database
- [ ] Run migrations (`flask db upgrade`)
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Test restore procedure

## Security

- [ ] Change all default passwords
- [ ] Review and minimize file permissions
- [ ] Configure fail2ban or similar
- [ ] Set up intrusion detection
- [ ] Enable security headers
- [ ] Test for common vulnerabilities

## Performance

- [ ] Enable caching (Redis/Memcached)
- [ ] Configure CDN for static files
- [ ] Set up database query optimization
- [ ] Enable gzip compression
- [ ] Implement rate limiting

## Monitoring

- [ ] Set up application monitoring (e.g., Sentry)
- [ ] Configure uptime monitoring
- [ ] Set up performance monitoring
- [ ] Enable database monitoring
- [ ] Configure alerting

## Post-Deployment

- [ ] Smoke test all major features
- [ ] Test payment processing (if applicable)
- [ ] Verify email delivery
- [ ] Check all external integrations
- [ ] Review logs for errors
- [ ] Test backup restoration
- [ ] Document deployment process

## Ongoing Maintenance

- [ ] Regular security updates
- [ ] Database optimization
- [ ] Log review and rotation
- [ ] Backup verification
- [ ] Performance monitoring
- [ ] User feedback review
