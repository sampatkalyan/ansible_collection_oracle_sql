#!/usr/bin/env bash
# Script to build and publish collection to Ansible Galaxy
set -e

if [ -z "$GALAXY_API_KEY" ]; then
    echo "ERROR: GALAXY_API_KEY environment variable is not set."
    echo "Usage: GALAXY_API_KEY='your_token' ./publish.sh"
    exit 1
fi

echo "Building collection..."
ansible-galaxy collection build --force

TARBALL=$(ls sampatkalyan-oracle_sql-*.tar.gz | head -n 1)
echo "Publishing $TARBALL to Ansible Galaxy..."
ansible-galaxy collection publish "$TARBALL" --api-key "$GALAXY_API_KEY"
echo "Published successfully!"

