#!/bin/bash
set -e

install_easyrsa() {
    easyrsa=easy-rsa-master/easyrsa3
    chmod +x $easyrsa/easyrsa
    $easyrsa/easyrsa init-pki
    $easyrsa/easyrsa build-ca
    subject_alt_name=$SUBJECT_ALT_NAME
    $easyrsa/easyrsa --subject-alt-name="$subject_alt_name" \
      build-server-full couchbase-server nopass
    cp pki/private/couchbase-server.key $easyrsa/pkey.key
    openssl rsa -in $easyrsa/pkey.key -out $easyrsa/pkey.key.der -outform DER
    openssl rsa -in $easyrsa/pkey.key.der -inform DER \
      -out $easyrsa/pkey.key -outform PEM
}

# ==========
# entrypoint
# ==========

case $1 in
  "install"|"")
    SUBJECT_ALT_NAME=$2
    install_easyrsa
    ;;
  *)
    echo "[E] Unsupported command; please enter 'install <SUBJECT_ALT_NAME>'"
    exit 1
    ;;
esac
