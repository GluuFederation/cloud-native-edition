#!/bin/bash

set -e

get_consul_name() {
    docker ps --filter name=consul --format '{{.Names}}'
}

bootstrap_db() {
    echo "[I] Prepare cluster-wide config and secrets"

    # guess if config already in Consul
    consul_name=$(get_consul_name)
    if [[ ! -z $consul_name ]]; then
        consul_ip=$(docker exec $consul_name ifconfig eth1 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}')
        domain=$(docker-machine ssh manager curl $consul_ip:8500/v1/kv/gluu/config/hostname?raw -s)
    fi

    if [[ -z $domain ]]; then
        echo "[W] Unable to find config in Consul; Make sure config (and secret) already generated; exiting ..."
        exit 1
    fi

    copy_vault_role_secret
    docker run \
        --rm \
        --network container:$consul_name \
        -v /opt/vault/vault_role_id.txt:/etc/certs/vault_role_id \
        -v /opt/vault/vault_secret_id.txt:/etc/certs/vault_secret_id \
        -e GLUU_CONFIG_CONSUL_HOST=consul.server \
        -e GLUU_SECRET_VAULT_HOST=vault.server \
        -e GLUU_PERSISTENCE_TYPE=ldap \
        -e GLUU_PERSISTENCE_LDAP_MAPPING=default \
        -e GLUU_LDAP_URL=ldap.server:1636 \
        gluufederation/persistence:4.0.1_04
}

copy_vault_role_secret() {
    docker-machine scp vault_role_id.txt manager:/opt/vault/vault_role_id.txt
    docker-machine scp vault_secret_id.txt manager:/opt/vault/vault_secret_id.txt
}

bootstrap_db
