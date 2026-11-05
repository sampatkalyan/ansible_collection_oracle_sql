# Linux development container for Ansible Collection development & Oracle tools
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed by Ansible and Oracle Instant Client
RUN apt-get update && apt-get install -y --no-install-recommends \
    libaio1 \
    libaio-dev \
    unzip \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client (Basic Lite + SQL*Plus + Tools/sqlldr)
# Note: In production or full container testing, install instantclient from Oracle.
# python-oracledb is installed below and can run in thin mode (no client needed)
# or thick mode with the Instant Client.
ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient:$LD_LIBRARY_PATH
ENV PATH=$ORACLE_HOME:$PATH

# Install Ansible collection development and testing dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    ansible-core>=2.15 \
    pytest>=8.0 \
    oracledb>=2.0 \
    pyyaml>=6.0 \
    cryptography \
    jinja2

# Set ANSIBLE_COLLECTIONS_PATH so ansible tools discover the collection natively
ENV ANSIBLE_COLLECTIONS_PATH=/workspaces
ENV PYTHONPATH=/workspaces:$PYTHONPATH
