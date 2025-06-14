#!/bin/sh

set -e

host="$1"
shift
cmd="$@"

# Wait for Docker DNS to resolve host
until getent hosts "$host" > /dev/null; do
  echo "DNS for $host not available yet..."
  sleep 1
done

# Wait for Postgres to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "postgres" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable at $host - sleeping"
  sleep 1
done

echo "PostgreSQL is up at $host - executing command"
exec $cmd
