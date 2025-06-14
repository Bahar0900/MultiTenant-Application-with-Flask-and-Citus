#!/bin/bash
set -e

# Wait for master to be ready
until pg_isready -h citus-master -U postgres; do
  echo "Waiting for citus-master..."
  sleep 2
done

# Wait for worker to be ready
until pg_isready -h citus-worker -U postgres; do
  echo "Waiting for citus-worker..."
  sleep 2
done

echo "Verifying Citus extension on master..."
psql -h citus-master -U postgres -c "SELECT citus_version();"

echo "Verifying Citus extension on worker..."
psql -h citus-worker -U postgres -c "SELECT citus_version();"

echo "Setting up Citus cluster..."
psql -v ON_ERROR_STOP=1 --username postgres --host citus-master <<-EOSQL
  SELECT citus_set_coordinator_host('citus-master');
  SELECT citus_add_node('citus-worker', 5432);
  SELECT * FROM citus_get_active_worker_nodes();
EOSQL

echo "Cluster setup complete!"