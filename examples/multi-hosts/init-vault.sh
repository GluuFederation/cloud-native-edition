#!/bin/bash

set -e

export VAULT_MANAGER=$(docker ps --filter name=vault --format '{{.Names}}')

init_vault() {
    vault_initialized=$(docker exec $VAULT_MANAGER vault status -format=yaml | grep initialized | awk -F ': ' '{print $2}')

    if [ "${vault_initialized}" = "true" ]; then
        echo "[I] Vault already initialized"
    else
        echo "[W] Vault is not initialized; trying to initialize Vault with 1 recovery key and root token"
        docker exec $VAULT_MANAGER vault operator init \
            -key-shares=1 \
            -key-threshold=1 \
            -recovery-shares=1 \
            -recovery-threshold=1 > "$PWD"/vault_key_token.txt
        echo "[I] Vault recovery key and root token saved to $PWD/vault_key_token.txt"
    fi
}


get_root_token() {
    if [ -f "$PWD"/vault_key_token.txt ]; then
        cat "$PWD"/vault_key_token.txt | grep "Initial Root Token" | awk -F ': ' '{print $2}'
    fi
}

enable_approle() {
    docker exec $VAULT_MANAGER vault login -no-print "$(get_root_token)"

    approle_enabled=$(docker exec $VAULT_MANAGER vault auth list | grep 'approle' || :)

    if [ -z "${approle_enabled}" ]; then
        echo "[W] AppRole is not enabled; trying to enable AppRole"
        docker exec $VAULT_MANAGER vault auth enable approle
        docker exec $VAULT_MANAGER vault write auth/approle/role/gluu policies=gluu
        docker exec $VAULT_MANAGER \
            vault write auth/approle/role/gluu \
                secret_id_ttl=0 \
                token_num_uses=0 \
                token_ttl=20m \
                token_max_ttl=30m \
                secret_id_num_uses=0

        docker exec $VAULT_MANAGER \
            vault read -field=role_id auth/approle/role/gluu/role-id > vault_role_id.txt
        docker exec $VAULT_MANAGER \
            vault write -f -field=secret_id auth/approle/role/gluu/secret-id > vault_secret_id.txt

        docker secret create vault_role_id vault_role_id.txt
        docker secret create vault_secret_id vault_secret_id.txt
    else
        echo "[I] AppRole already enabled"
    fi
}

write_policy() {
    docker exec $VAULT_MANAGER vault login -no-print "$(get_root_token)"

    policy_created=$(docker exec $VAULT_MANAGER vault policy list | grep gluu || :)

    if [ -z "${policy_created}" ]; then
        echo "[W] Gluu policy is not created; trying to create one"
        docker exec $VAULT_MANAGER vault policy write gluu /vault/config/policy.hcl
    else
        echo "[I] Gluu policy already created"
    fi
}

setup_vault() {
    init_vault
    sleep 5
    write_policy
    enable_approle
}

setup_vault
# re-establish Vault cluster by restarting all Vault containers
docker service update --force gluu_vault
