# PostgreSQL Backups

Use managed PostgreSQL automated backups for production whenever possible, with retention and restore testing enabled. Keep database credentials outside the repository.

## Manual dump

```bash
pg_dump "$DATABASE_URL" --format=custom --file=homehealth-$(date +%Y%m%d-%H%M%S).dump
```

## Restore

```bash
createdb homehealth_restore
pg_restore --dbname=homehealth_restore --clean --if-exists homehealth-YYYYMMDD-HHMMSS.dump
```

Before restoring production data, verify BAAs, encryption, access approvals, and audit requirements.
