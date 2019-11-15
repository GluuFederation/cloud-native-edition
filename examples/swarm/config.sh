#!/bin/bash

set -e

saved_config=$PWD/volumes/config.json
saved_secret=$PWD/volumes/secret.json

mask_password(){
    password=''
    while IFS= read -r -s -n1 char; do
        [[ -z $char ]] && { printf '\n'; break; }
        if [[ $char == $'\b' ]]; then
            [[ -n $password ]] && password=${password%?}
            printf '\b \b'
        else
            password+=$char
            printf '*'
        fi
    done
}

get_consul_name() {
    docker ps --filter name=consul --format '{{.Names}}'
}

bootstrap_config() {
    echo "[I] Prepare cluster-wide config and secrets"

    copy_vault_role_secret

    # guess if config already in Consul
    consul_name=$(get_consul_name)
    if [[ ! -z $consul_name ]]; then
        consul_ip=$(docker exec $consul_name ifconfig eth1 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}')
        DOMAIN=$(docker-machine ssh manager curl $consul_ip:8500/v1/kv/gluu/config/hostname?raw -s)
    fi

    if [[ -z $DOMAIN ]]; then
        echo "[W] Unable to find configuration in Consul"

        if [[ -f $saved_config ]]; then
            read -p "[I] Load previously saved config and secrets? [y/n]" load_choice

            if [[ $load_choice != "n" && $load_choice != "N" ]]; then
                DOMAIN=$(cat $saved_config |  awk ' /'hostname'/ {print $2} ' | sed 's/[",]//g')

                if [[ ! -z "$DOMAIN" ]]; then
                    docker-machine scp $saved_config manager:/opt/config-init/db/config.json
                    docker-machine scp $saved_secret manager:/opt/config-init/db/secret.json

                    docker run \
                        --rm \
                        --network container:$consul_name \
                        -v /opt/config-init/db:/opt/config-init/db/ \
                        -v /opt/vault/vault_role_id.txt:/etc/certs/vault_role_id \
                        -v /opt/vault/vault_secret_id.txt:/etc/certs/vault_secret_id \
                        -e GLUU_CONFIG_CONSUL_HOST=consul.server \
                        -e GLUU_SECRET_VAULT_HOST=vault.server \
                        gluufederation/config-init:4.0.1_03 load
                fi
            fi
        fi
    fi

    # config is not loaded from previously saved configuration
    if [[ -z $DOMAIN ]]; then
        if [[ ! -f "$PWD/generate.json" ]]; then
            echo "[I] Creating new configuration, please input the following parameters"
            read -rp "Enter Hostname (demoexample.gluu.org):                 " DOMAIN
            if ! [[ $DOMAIN == *"."*"."* ]]; then
                echo "[E] Hostname provided is invalid. Please enter a FQDN with the format demoexample.gluu.org"
                exit 1
            fi
            read -rp "Enter Country Code:           " COUNTRY_CODE
            read -rp "Enter State:                  " STATE
            read -rp "Enter City:                   " CITY
            read -rp "Enter Email:                  " EMAIL
            read -rp "Enter Organization:           " ORG_NAME
            echo "[I] Password must be at least 6 characters and include one uppercase letter, one lowercase letter, one digit,  and one special chara
cter."
            while true; do
                echo "Enter Admin/LDAP Password:"
                mask_password
                ADMIN_PW=$password
                echo "Confirm Admin/LDAP Password:"
                mask_password
                password2=$password
                [ "$ADMIN_PW" = "$password2" ] && break || echo "Please try again"
            done

            case "$ADMIN_PW" in
                * ) ;;
                "") echo "Password cannot be empty"; exit 1;
            esac

            read -rp "Continue with the above settings? [Y/n]" choiceCont

            case "$choiceCont" in
                y|Y ) ;;
                n|N ) exit 1 ;;
                * )   ;;
            esac

            cat > generate.json <<EOL
{
    "hostname": "$DOMAIN",
    "country_code": "$COUNTRY_CODE",
    "state": "$STATE",
    "city": "$CITY",
    "admin_pw": "$ADMIN_PW",
    "email": "$EMAIL",
    "org_name": "$ORG_NAME"
}
EOL
        fi

        if [ -f generate.json ]; then
            DOMAIN=$(cat generate.json |  awk ' /'hostname'/ {print $2} ' | sed 's/[",]//g')
        fi

        # mount generate.json to mark for new config and secret
        docker-machine scp generate.json manager:/opt/config-init/db/generate.json

        docker run \
            --rm \
            --network container:$consul_name \
            -v /opt/config-init/db:/opt/config-init/db/ \
            -v /opt/vault/vault_role_id.txt:/etc/certs/vault_role_id \
            -v /opt/vault/vault_secret_id.txt:/etc/certs/vault_secret_id \
            -e GLUU_CONFIG_CONSUL_HOST=consul.server \
            -e GLUU_SECRET_VAULT_HOST=vault.server \
            gluufederation/config-init:4.0.1_03 load

        docker-machine scp manager:/opt/config-init/db/config.json $saved_config
        docker-machine scp manager:/opt/config-init/db/secret.json $saved_secret
        rm generate.json
    fi
}

copy_vault_role_secret() {
    docker-machine scp vault_role_id.txt manager:/opt/vault/vault_role_id.txt
    docker-machine scp vault_secret_id.txt manager:/opt/vault/vault_secret_id.txt
}

bootstrap_config
