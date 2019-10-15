#!/bin/bash
set -e
# version >= V1.14 
#Local Deployments
local_minikube_folder="overlays/minikube/local-storage/"
local_microk8s_folder="overlays/microk8s/local-storage/"
#AWS
local_eks_folder="overlays/eks/local-storage/"
dynamic_eks_folder="overlays/eks/dynamic-ebs/"
static_eks_folder="overlays/eks/static-ebs/"
#GCE
local_gke_folder="overlays/gke/local-storage/"
dynamic_gke_folder="overlays/gke/dynamic-pd/"
static_gke_folder="overlays/gke/static-pd/"
#AZURE
local_azure_folder="overlays/azure/local-storage/"
dynamic_azure_folder="overlays/azure/dynamic-dn/"
static_azure_folder="overlays/azure/static-dn/"

emp_output() {
  echo "" > /dev/null
}

delete_all() {
  find_host
  timeout=timeout
  if [[ $machine == Mac ]]; then
    brew install coreutils
    timeout=gtimeout
  fi
  echo "Deleting Gluu objects. Please wait..."
  kubectl=kubectl
  $timeout 10 $kubectl delete pvc opendj-pvc-opendj-0 --ignore-not-found || emp_output
  if [ -d "localazureyamls" ];then
    $timeout 40 $kubectl delete -f localazureyamls --ignore-not-found || emp_output
  elif [ -d "staticazureyamls" ];then
    $timeout 40 $kubectl delete -f staticazureyamls --ignore-not-found || emp_output
  elif [ -d "localeksyamls" ];then
    $timeout 40 $kubectl delete -f localeksyamls --ignore-not-found || emp_output
  elif [ -d "dynamiceksyamls" ];then
    $timeout 40 $kubectl delete -f dynamiceksyamls --ignore-not-found || emp_output
  elif [ -d "dynamicazureyamls" ];then
    $timeout 40 $kubectl delete -f dynamicazureyamls --ignore-not-found || emp_output
  elif [ -d "localgkeyamls" ];then
    $timeout 40 $kubectl delete -f localgkeyamls --ignore-not-found || emp_output
  elif [ -d "dynamicgkeyamls" ];then
    $timeout 40 $kubectl delete -f dynamicgkeyamls --ignore-not-found || emp_output
  elif [ -d "staticgkeyamls" ];then
    $timeout 40 $kubectl delete -f staticgkeyamls --ignore-not-found || emp_output
  elif [ -d "staticeksyamls" ];then
    $timeout 40 $kubectl delete -f staticeksyamls --ignore-not-found || emp_output
  elif [ -d "localminikubeyamls" ];then
    $timeout 40 $kubectl delete -f localminikubeyamls --ignore-not-found || emp_output
    rm -rf /data
  else
    kubectl=microk8s.kubectl
    $timeout 10 $kubectl delete -f localmicrok8syamls --ignore-not-found || emp_output
    rm -rf /data
  fi
  $timeout 10 $kubectl delete po oxtrust-0 --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete po oxshibboleth-0 --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete cm gluu casacm --ignore-not-found || emp_output
  $timeout 10 $kubectl delete secret gluu tls-certificate cb-pass cb-crt --ignore-not-found || emp_output
  $timeout 10 $kubectl delete -f nginx/ --ignore-not-found || emp_output
  $timeout 10 $kubectl delete secret oxdkeystorecm --ignore-not-found || emp_output
  rm oxd-server.keystore || emp_output
  if [ -d "localazureyamls" ] \
    || [ -d "localeksyamls" ] \
    || [ -d "localgkeyamls" ]; then
    read -rp "Please enter the ssh key path to login
    into the nodes created[~/.ssh/id_rsa ]:                 " sshKey \
     && set_default "$sshKey" "~/.ssh/id_rsa" "sshKey"
    echo "Trying to delete folders created at other nodes."
    ip_template='{{range.items}}{{range.status.addresses}}
      {{if eq .type "ExternalIP"}}{{.address}}{{end}}{{end}} {{end}}'
    node_ips=$($kubectl get nodes -o template --template="$ip_template" \
      || echo "")
    # Loops through the IPs of the nodes and deletes /data
    for node_ip in $node_ips; do
      ssh -oStrictHostKeyChecking=no -i $sshKey \
        ec2-user@"$node_ip" sudo rm -rf /data || emp_output
      ssh -oStrictHostKeyChecking=no -i $sshKey \
        opc@"$node_ip" sudo rm -rf /data || emp_output
    done
  fi
  delete_cb
}

delete_cb() {
  echo "Deleting Couchbase objects if exist..."
  namespace_template='{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'
  namespaces=$($kubectl get ns -o template --template="$namespace_template" \
    || echo "")
  for ns in $namespaces; do
    $kubectl delete couchbasecluster.couchbase.com/cbgluu \
      storageclass.storage.k8s.io/couchbase-sc secret/cb-auth \
      deployment.apps/couchbase-operator \
      rolebinding.rbac.authorization.k8s.io/couchbase-operator \
      serviceaccount/couchbase-operator \
      role.rbac.authorization.k8s.io/couchbase-operator \
      customresourcedefinition.apiextensions.k8s.io/couchbaseclusters.couchbase.com \
      validatingwebhookconfiguration.admissionregistration.k8s.io/couchbase-operator-admission \
      mutatingwebhookconfiguration.admissionregistration.k8s.io/couchbase-operator-admission \
      service/couchbase-operator-admission deployment.apps/couchbase-operator-admission \
      clusterrolebinding.rbac.authorization.k8s.io/couchbase-operator-admission \
      clusterrole.rbac.authorization.k8s.io/couchbase-operator-admission \
      serviceaccount/couchbase-operator-admission secret/couchbase-operator-admission \
      secret/couchbase-operator-tls secret/couchbase-server-tls \
      --ignore-not-found -n $ns || emp_output
  done
  rm -rf easy-rsa pki || emp_output
}

create_dynamic_gke() {
  mkdir dynamicgkeyamls || emp_output
  services="config ldap oxauth casa oxd-server oxtrust radius"
  for service in $services; do
    dynamicgkefolder="$service/overlays/gke/dynamic-pd"
    cp -r $service/overlays/eks/dynamic-ebs $dynamicgkefolder
    cat $dynamicgkefolder/storageclasses.yaml \
      | $$sed -s "s@kubernetes.io/aws-ebs@kubernetes.io/gce-pd@g" \
      | $sed '/zones/d' | $sed '/encrypted/d' > tmpfile \
      && mv tmpfile $dynamicgkefolder/storageclasses.yaml \
      || emp_output
    rm $dynamicgkefolder/deployments.yaml || emp_output 
    if [[ $service == "oxtrust" ]]; then
      rm $dynamicgkefolder/statefulsets.yaml || emp_output
      cat $dynamicgkefolder/kustomization.yaml \
        | $sed '/- statefulsets.yaml/d' \
        | $sed '/patchesStrategicMerge:/d' > tmpfile \
        && mv tmpfile $dynamicgkefolder/kustomization.yaml \
        || emp_output
    fi
    if [[ $service == "oxauth" ]] \
      || [[ $service == "radius" ]] \
      || [[ $service == "casa" ]]; then
    cat $dynamicgkefolder/kustomization.yaml \
      | $sed '/- deployments.yaml/d' \
      | $sed '/patchesStrategicMerge:/d' > tmpfile \
      && mv tmpfile $dynamicgkefolder/kustomization.yaml \
      || emp_output
    fi
  done
  #Config
  cp config/overlays/gke/local-storage/cluster-role-bindings.yaml \
    config/overlays/gke/dynamic-pd
  printf  "\n  - cluster-role-bindings.yaml" \
    >> config/overlays/gke/dynamic-pd/kustomization.yaml
}

create_dynamic_azure() {
  mkdir dynamicazureyamls || emp_output
  services="config ldap oxauth casa oxd-server oxtrust radius"
  for service in $services; do
    dynamicazurefolder="$service/overlays/azure/dynamic-dn"
    mkdir -p $service/overlays/azure \
      && cp -r $service/overlays/eks/dynamic-ebs \
      $service/overlays/azure/dynamic-dn
    cat $dynamicazurefolder/storageclasses.yaml \
      | $sed -s "s@type@storageaccounttype@g" \
      | $sed -s "s@kubernetes.io/aws-ebs@kubernetes.io/azure-disk@g" \
      | $sed '/zones/d' \
      | $sed '/encrypted/d' > tmpfile \
      && mv tmpfile $dynamicazurefolder/storageclasses.yaml \
      || emp_output
    printf  "  kind: Managed" >> $dynamicazurefolder/storageclasses.yaml
    rm $dynamicazurefolder/deployments.yaml || emp_output 
    if [[ $service == "oxtrust" ]]; then
      rm $dynamicazurefolder/statefulsets.yaml || emp_output
      cat $dynamicazurefolder/kustomization.yaml \
        | $sed '/- statefulsets.yaml/d' \
        | $sed '/patchesStrategicMerge:/d' > tmpfile \
        && mv tmpfile $dynamicazurefolder/kustomization.yaml \
        || emp_output
    fi
    if [[ $service == "oxauth" ]] \
      || [[ $service == "radius" ]] \
      || [[ $service == "casa" ]]; then
      cat $dynamicazurefolder/kustomization.yaml \
        | $sed '/- deployments.yaml/d' \
        | $sed '/patchesStrategicMerge:/d' > tmpfile \
        && mv tmpfile $dynamicazurefolder/kustomization.yaml \
        || emp_output
    fi
  done
}

deploy_cb_cluster() {
  if [ -f couchbase-autonomous-operator-kubernetes_*.tar.gz ];then
    delete_cb
    echo "Installing Couchbase. Please follow the prompts.."
    tar xvzf couchbase-autonomous-operator-kubernetes_*.tar.gz --overwrite \
      || emp_output
    cbinstalldir=$(echo couchbase-autonomous-operator-kubernetes_*/)
    $kubectl create namespace $namespace || emp_output
    git clone http://github.com/OpenVPN/easy-rsa
    easyrsa=easy-rsa/easyrsa3
    $easyrsa/easyrsa init-pki
    $easyrsa/easyrsa build-ca
    subject_alt_name="DNS:*.$clustername.$namespace.svc,DNS:*.$namespace.svc,DNS:*.$clustername.$FQDN"
    $easyrsa/easyrsa --subject-alt-name=$subject_alt_name \
      build-server-full couchbase-server nopass
    cp pki/private/couchbase-server.key $easyrsa/pkey.key
    openssl rsa -in $easyrsa/pkey.key -out $easyrsa/pkey.key.der -outform DER
    openssl rsa -in $easyrsa/pkey.key.der -inform DER \
      -out $easyrsa/pkey.key -outform PEM
    cp pki/issued/couchbase-server.crt $easyrsa/chain.pem
    cp $easyrsa/chain.pem $easyrsa/tls-cert-file
    cp $easyrsa/pkey.key $easyrsa/tls-private-key-file
    cp pki/ca.crt couchbase.crt
    $kubectl create secret generic couchbase-server-tls \
      --from-file $easyrsa/chain.pem \
      --from-file $easyrsa/pkey.key --namespace $namespace
    $kubectl create secret generic couchbase-operator-tls \
      --from-file pki/ca.crt --namespace $namespace || emp_output
    $kubectl create secret generic couchbase-operator-admission \
      --from-file $easyrsa/tls-cert-file \
      --from-file $easyrsa/tls-private-key-file --namespace $namespace \
      || emp_output
    tlscertfilebase64=$(base64 -i $easyrsa/tls-cert-file | tr -d '\040\011\012\015')
    $sed -i "$cbinstalldir"admission.yaml -re '49,58d'
    $sed -i '/caBundle/c\    caBundle: TLSCERTFILEBASE64' "$cbinstalldir"admission.yaml
    cat "$cbinstalldir"admission.yaml \
      | $sed -s "s@default@$namespace@g" \
      | $sed -s "s@TLSCERTFILEBASE64@$tlscertfilebase64@g" > tmpfile \
      && mv tmpfile "$cbinstalldir"admission.yaml \
      || emp_output

    $kubectl apply -f "$cbinstalldir"admission.yaml --namespace $namespace
    $kubectl apply -f "$cbinstalldir"crd.yaml --namespace $namespace
    $kubectl apply -f "$cbinstalldir"operator-role.yaml --namespace $namespace
    $kubectl create  serviceaccount couchbase-operator --namespace $namespace
    $kubectl create  rolebinding couchbase-operator --role couchbase-operator \
      --serviceaccount $namespace:couchbase-operator --namespace $namespace
    $kubectl apply -f "$cbinstalldir"operator-deployment.yaml --namespace $namespace
    is_pod_ready "app=couchbase-operator"
    $kubectl create secret generic cb-auth --from-literal=username=$CB_USER \
      --from-literal=password=$CB_PW --namespace $namespace || emp_output
    cat couchbase/storageclasses.yaml \
      | $sed -s "s@VOLUMETYPE@$VOLUME_TYPE@g" > tmpfile \
      && mv tmpfile couchbase/storageclasses.yaml \
      || emp_output
    $kubectl apply -f couchbase/storageclasses.yaml --namespace $namespace
    cat couchbase/couchbase-cluster.yaml \
      | $sed -s "s@CLUSTERNAME@$clustername@g" > tmpfile \
      && mv tmpfile couchbase/couchbase-cluster.yaml \
      || emp_output
    $kubectl apply -f couchbase/couchbase-cluster.yaml --namespace $namespace
    is_pod_ready "couchbase_services=analytics" 
    is_pod_ready "couchbase_services=data"
    is_pod_ready "couchbase_services=index"
    rm -rf $cbinstalldir || emp_output
  else
    echo "Error: Couchbase package not found."
    echo "Please download the couchbase kubernetes package and place it inside
      the same directory containing the create.sh script.
      https://www.couchbase.com/downloads"
    exit 1
  fi

}

create_local_minikube() {
  mkdir localminikubeyamls || emp_output
  services="config ldap oxauth casa oxd-server oxtrust radius"
  for service in $services; do
    localminikubefolder="$service/overlays/minikube"
    mkdir -p $localminikubefolder \
      && cp -r $service/overlays/microk8s/local-storage "$_"
  done
  cp -r oxpassport/overlays/microk8s oxpassport/overlays/minikube
  cp -r oxshibboleth/overlays/microk8s oxshibboleth/overlays/minikube
  #shared-shib
  cp -r shared-shib/microk8s shared-shib/minikube
}

create_local_azure() {
  mkdir localazureyamls || emp_output
  services="config ldap oxauth casa oxd-server oxtrust radius"
  for service in $services; do
    localazurefolder="$service/overlays/azure"
    mkdir -p $localazurefolder \
      && cp -r $service/overlays/gke/local-storage "$_"
  done
  cp -r oxpassport/overlays/gke oxpassport/overlays/azure
  cp -r oxshibboleth/overlays/gke oxshibboleth/overlays/azure
  rm config/overlays/azure/local-storage/cluster-role-bindings.yaml
  cat config/overlays/azure/local-storage/kustomization.yaml \
    | $sed '/- cluster-role-bindings.yaml/d' > tmpfile \
    && mv tmpfile config/overlays/azure/local-storage/kustomization.yaml
}

create_static_gke() {
  mkdir staticgkeyamls || emp_output
  services="config ldap oxauth casa oxd-server oxtrust radius"
  for service in $services; do
    staticgkefolder="$service/overlays/gke/static-pd"
    service_name=$(echo "${service^^}VOLUMEID" | tr -d -)
    cp -r $service/overlays/eks/local-storage $service/overlays/gke/static-pd
    cat $staticgkefolder/persistentvolumes.yaml \
      | $sed '/hostPath/d' \
      | $sed '/path/d' \
      | $sed '/type/d' > tmpfile \
      && mv tmpfile $staticgkefolder/persistentvolumes.yaml \
      || emp_output
    printf  "  gcePersistentDisk:" \
      >> $staticgkefolder/persistentvolumes.yaml
    printf  "\n    pdName: $service_name" \
      >> $staticgkefolder/persistentvolumes.yaml
    printf  "\n    fsType: ext4" \
      >> $staticgkefolder/persistentvolumes.yaml
  done
}

create_static_azure() {
  mkdir staticazureyamls || emp_output
  services="config ldap oxauth casa oxd-server oxtrust radius"
  for service in $services; do
    staticazurefolder="$service/overlays/azure/static-dn"
    service_name=$(echo "${service^^}VOLUMEID" | tr -d -)
    disk_uri=$(echo "${service^^}DISKURI" | tr -d -)
    mkdir -p $service/overlays/azure \
      && cp -r $service/overlays/eks/local-storage \
      $service/overlays/azure/static-dn
    cat $staticazurefolder/persistentvolumes.yaml \
      | $sed '/hostPath/d' \
      | $sed '/path/d' \
      | $sed '/type/d' > tmpfile \
      && mv tmpfile $staticazurefolder/persistentvolumes.yaml \
      || emp_output
    printf  "  azureDisk:" \
      >> $staticazurefolder/persistentvolumes.yaml
    printf  "\n    diskName: $service_name" \
      >> $staticazurefolder/persistentvolumes.yaml
    printf  "\n    diskURI: $disk_uri" \
      >> $staticazurefolder/persistentvolumes.yaml
    printf  "\n    fsType: ext4" \
      >> $staticazurefolder/persistentvolumes.yaml
    printf  "\n    kind: Managed" \
      >> $staticazurefolder/persistentvolumes.yaml
  done
}

replace_all() {
  $sed "s/\<PERSISTENCETYPE\>/$PERSISTENCE_TYPE/" \
    | $sed "s/\<LDAPMAPPING\>/$LDAP_MAPPING/" \
    | $sed -s "s@LDAPVOLUMEID@$LDAP_VOLUMEID@g" \
    | $sed -s "s@STORAGELDAP@$STORAGE_LDAP@g" \
    | $sed -s "s@SCLDAPZONE@$SC_LDAP_ZONE@g" \
    | $sed -s "s@LDAPDISKURI@$LDAP_DISKURI@g" \
    | $sed -s "s@STORAGESHAREDSHIB@$STORAGE_SHAREDSHIB@g" \
    | $sed -s "s@CONFIGVOLUMEID@$CONFIG_VOLUMEID@g" \
    | $sed -s "s@STORAGECONFIG@$STORAGE_CONFIG@g" \
    | $sed -s "s@SCCONFIGZONE@$SC_CONFIG_ZONE@g" \
    | $sed -s "s@HOME_DIR@$HOME_DIR@g" \
    | $sed -s "s@OXAUTHVOLUMEID@$OXAUTH_VOLUMEID@g" \
    | $sed -s "s@STORAGEOXAUTH@$STORAGE_OXAUTH@g" \
    | $sed -s "s@SCOXAUTHZONE@$SC_OXAUTH_ZONE@g" \
    | $sed -s "s@OXAUTHDISKURI@$OXAUTH_DISKURI@g" \
    | $sed -s "s@OXTRUSTVOLUMEID@$OXTRUST_VOLUMEID@g" \
    | $sed -s "s@STORAGEOXTRUST@$STORAGE_OXTRUST@g" \
    | $sed -s "s@SCOXTRUSTZONE@$SC_OXTRUST_ZONE@g" \
    | $sed -s "s@OXTRUSTDISKURI@$OXTRUST_DISKURI@g" \
    | $sed -s "s@OXDSERVERVOLUMEID@$OXDSERVER_VOLUMEID@g" \
    | $sed -s "s@STORAGEOXDSERVER@$STORAGE_OXDSERVER@g" \
    | $sed -s "s@SCOXDSERVERZONE@$SC_OXDSERVER_ZONE@g" \
    | $sed -s "s@OXDSERVERDISKURI@$OXDSERVER_DISKURI@g" \
    | $sed -s "s@RADIUSVOLUMEID@$RADIUS_VOLUMEID@g" \
    | $sed -s "s@STORAGERADIUS@$STORAGE_RADIUS@g" \
    | $sed -s "s@SCRADIUSZONE@$SC_RADIUS_ZONE@g" \
    | $sed -s "s@RADIUSDISKURI@$RADIUS_DISKURI@g" \
    | $sed -s "s@CASAVOLUMEID@$CASA_VOLUMEID@g" \
    | $sed -s "s@STORAGECASA@$STORAGE_CASA@g" \
    | $sed -s "s@SCCASAZONE@$SC_CASA_ZONE@g" \
    | $sed -s "s@CASADISKURI@$CASA_DISKURI@g" \
    | $sed "s/\<COUCHBASEURL\>/$COUCHBASE_URL/" \
    | $sed "s/\<CBUSER\>/$CB_USER/" \
    | $sed "s/\<FQDN\>/$FQDN/" \
    | $sed "s#ACCOUNT#$ACCOUNT#g" \
    | $sed "s/\<GLUUCACHETYPE\>/$GLUU_CACHE_TYPE/" \
    | $sed -s "s@VOLUMETYPE@$VOLUME_TYPE@g"
}

setup_tls() {
  sleep 10
  if [ ! -f ingress.crt ] || [ ! -s ingress.crt ]; then
    $kubectl get secret gluu -o json \
      | grep '\"ssl_cert' \
      | awk -F '"' '{print $4}' \
      | base64 --decode > ingress.crt
  fi

  if [ ! -f ingress.key ] || [ ! -s ingress.key ]; then
    $kubectl get secret gluu -o json \
    | grep '\"ssl_key' \
    | awk -F '"' '{print $4}' \
    | base64 --decode > ingress.key
  fi

  $kubectl create secret tls tls-certificate \
    --key ingress.key --cert ingress.crt || true
}

is_pod_ready() {
  pod_status=""
  while true; do 
    echo "[I] Waiting for $1 to finish preperation" && sleep 20
    if [[ "$1" == "app=config-init-load" ]] \
      || [[ "$1" == "app=persistence-load" ]]; then
      pod_status="$($kubectl get pods -l "$1" \
      -o 'jsonpath={..status.conditions[].reason}' || true)"
    elif [[ "$1" == "app=couchbase-operator" ]] \
      || [[ "$1" == "couchbase_services=analytics" ]] \
      || [[ "$1" == "couchbase_services=data" ]] \
      || [[ "$1" == "couchbase_services=index" ]]; then
      pod_status="$($kubectl get pods -l "$1"  \
        -n $namespace \
        -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}'|| true)"
    else
      pod_status="$($kubectl get pods -l "$1" \
        -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}'|| true)"
    fi
    if [[ $pod_status == "PodCompleted" ]] || [[ $pod_status =~ "True" ]]; then
      break
    fi
  done
}

set_default() {
  if [[ ! "$1" ]]; then
    case "$3" in
      "SC_CONFIG_ZONE" ) SC_CONFIG_ZONE="$2"  ;;
      "SC_LDAP_ZONE" ) SC_LDAP_ZONE="$2"  ;;
      "SC_OXAUTH_ZONE" ) SC_OXAUTH_ZONE="$2" ;;
      "SC_OXDSERVER_ZONE" ) SC_OXDSERVER_ZONE="$2"  ;;
      "SC_OXTRUST_ZONE" ) SC_OXTRUST_ZONE="$2"  ;;
      "SC_RADIUS_ZONE" ) SC_RADIUS_ZONE="$2"  ;;
      "SC_CASA_ZONE" ) SC_CASA_ZONE="$2" ;;
      "STORAGE_CONFIG" ) STORAGE_CONFIG="$2"  ;;
      "STORAGE_LDAP" ) STORAGE_LDAP="$2"  ;;
      "STORAGE_OXAUTH" ) STORAGE_OXAUTH="$2" ;;
      "STORAGE_OXTRUST" ) STORAGE_OXTRUST="$2"  ;;
      "STORAGE_RADIUS" ) STORAGE_RADIUS="$2"  ;;
      "STORAGE_SHAREDSHIB" ) STORAGE_SHAREDSHIB="$2"  ;;
      "STORAGE_OXDSERVER" ) STORAGE_OXDSERVER="$2" ;;
      "STORAGE_CASA" ) STORAGE_CASA="$2"  ;;
      "STORAGE_NFS" ) STORAGE_NFS="$2"  ;;
      "EMAIL" ) EMAIL="$2"  ;;
      "ORG_NAME" ) ORG_NAME="$2" ;;
      "sshKey" ) sshKey="$2"  ;;
      "VOLUME_TYPE" ) VOLUME_TYPE="$2"  ;;
      "namespace" ) namespace="$2" ;;
      "clustername" ) clustername="$2"  ;;
      "CB_USER" ) CB_USER="$2"  ;;
      "FQDN" ) FQDN="$2"  ;;
      "COUNTRY_CODE" ) COUNTRY_CODE="$2" ;;
      "STATE" ) STATE="$2"  ;;
      "CITY" ) CITY="$2"  ;;
      "EMAIL" ) EMAIL="$2"  ;;
      "ORG_NAME" ) ORG_NAME="$2" ;;
    esac
  fi
}

check_k8version() {
  kustomize="$kubectl kustomize"
  kubectl_version=$("$kubectl" version -o json | jq -r '.clientVersion.minor')
  kubectl_version=$(echo "$kubectl_version" | tr -d +)
  echo "[I] kubectl detected version 1.$kubectl_version"
  # version < V1.14
  if [[ $kubectl_version -lt 14 ]]; then
    kustomize_install
    kustomize="./kustomize build"
  fi 
}

kustomize_install() {
  echo "[I] Check Kustomize is installed"
  check_kustomize=$(command -v ./kustomize) || emp_output
  if [[ $check_kustomize ]]; then
    echo "Kustomize is installed already."
      return 0
  fi
  echo "[I] Kustomize not found. Installing..."
  if [[ $machine == Linux ]]; then
    opsys=linux
  elif [[ $machine == Mac ]]; then
    opsys=darwin
  else
    echo "Couldn't determine system OS"
  fi
  #Install kustomize
  curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest \
  | grep browser_download \
  | grep $opsys \
  | cut -d '"' -f 4 \
  | xargs curl -O -L
  mv kustomize_*_${opsys}_amd64 kustomize
  chmod u+x kustomize
}

mask_password() {
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

find_host() {
  echo "[I] Determining OS Type "
  unameOut="$(uname -s)"
  case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    *)          machine="UNKNOWN:${unameOut}"
  esac
  echo "Host is detected as ${machine}"
}

gather_ip() {
  echo "Attempting to Gather External IP Address"
  if [[ $machine == Linux ]]; then
    HOST_IP=$(ip route get 8.8.8.8 \
      | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
  elif [[ $machine == Mac ]]; then
    HOST_IP=$(ipconfig getifaddr en0)
    brew install gnu-sed || emp_output
    brew install jq || emp_output
    brew cask install adoptopenjdk8 || emp_output
    sed=gsed || emp_output
  else
    echo "Cannot determine IP address."
    read -rp "Please input the hosts external IP Address:                       " HOST_IP
  fi
}

valid_ip() {
  local ip=${1:-1.2.3.4}
  local IFS=.; local -a a=($ip)
  [[ $ip =~ ^[0-9]+(\.[0-9]+){3}$ ]] || return 1
  local quad
  for quad in {0..3}; do
    [[ "${a[$quad]}" -gt 255 ]] && return 1
  done
  return 0
}

confirm_ip() {
  read -rp "Is this the correct external IP Address: ${HOST_IP} [Y/n]?          " cont
  case "$cont" in
    y|Y)
      return 0
    ;;
    n|N)
      read -rp "Please input the hosts external IP Address:                     " HOST_IP
      if valid_ip "$HOST_IP"; then
        return 0
      else
        echo "Please enter a valid IP Address."
        gather_ip
        return 1
      fi
      return 0
    ;;
    *)
      return 0
    ;;
  esac
}

prompt_cb() {
 if [[ $choicePersistence -ge 1 ]]; then
    if [[ $installCB != "n" || $installCB != "N" ]]; then
      echo "ONLY TESTED ON AWS. Couchbase will begin installation..."
      deploy_cb_cluster
    fi
    if [ ! -f couchbase.crt ] || [ ! -s couchbase.crt ]; then
      echo "There is no crt inside couchbase.crt for couchbase. 
        Please create a file named couchbase.crt and past the certification 
        found in your couchbase UI Security > Root Certificate inside it."
      exit 1
    fi
  fi
}

prepare_config() {
  sed=sed || emp_output
  choiceDeploy=1
  echo "|-----------------------------------------------------------------|"
  echo "|                     Local Deployments                           |"
  echo "|-----------------------------------------------------------------|"
  echo "| [1]  Microk8s | Volumes on host                                 |"
  echo "| [2]  Minikube | Volumes on host                                 |"
  echo "|-----------------------------------------------------------------|"
  echo "|                     Cloud Deployments                           |"
  echo "|-----------------------------------------------------------------|"
  echo "|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)    |"
  echo "|-----------------------------------------------------------------|"
  echo "| [3]  EKS      | Volumes on host                                 |"
  echo "| [4]  EKS      | EBS volumes dynamically provisioned             |"
  echo "| [5]  EKS      | EBS volumes statically provisioned              |"
  echo "|-----------------------------------------------------------------|"
  echo "|Google Cloud Engine - Google Kubernetes Engine                   |"
  echo "|-----------------------------------------------------------------|"
  echo "| [6]  GKE      | Volumes on host                                 |"
  echo "| [7]  GKE      | Persistent Disk volumes dynamically provisioned |"
  echo "| [8]  GKE      | Persistent Disk volumes statically provisioned  |"
  echo "|-----------------------------------------------------------------|"
  echo "|Microsoft Azure                                                  |"
  echo "|-----------------------------------------------------------------|"
  echo "| [9]  Azure    | Volumes on host                                 |"
  echo "| [10] Azure    | Persistent Disk volumes dynamically provisioned |"
  echo "| [11] Azure    | Persistent Disk volumes statically provisioned  |"
  echo "|-----------------------------------------------------------------|"
  echo "|                            Notes                                |"
  echo "|-----------------------------------------------------------------|"
  echo "|- Any other option will default to choice 1                      |"
  echo "|-----------------------------------------------------------------|"
  read -rp "What type of deployment?                                            " choiceDeploy
  echo "|-----------------------------------------------------------------|"
  echo "|                     Cache layer                                 |"
  echo "|-----------------------------------------------------------------|"
  echo "| [0] NATIVE_PERSISTENCE [default]                                |"
  echo "| [1] IN_MEMORY                                                   |"
  echo "| [2] REDIS                                                       |"
  echo "|-----------------------------------------------------------------|"
  read -rp "Cache layer?                                                        " choiceCache
  case "$choiceCache" in
    1 ) GLUU_CACHE_TYPE="IN_MEMORY"  ;;
    2 ) GLUU_CACHE_TYPE="REDIS" ;;
    * ) GLUU_CACHE_TYPE="NATIVE_PERSISTENCE"  ;;
  esac  
  GLUU_CACHE_TYPE="'${GLUU_CACHE_TYPE}'"
  echo "|-----------------------------------------------------------------|"
  echo "|                     Persistence layer                           |"
  echo "|-----------------------------------------------------------------|"
  echo "| [0] WrenDS [default]                                            |"
  echo "| [1] Couchbase [Testing Phase]                                   |"
  echo "| [2] Hybrid(WrenDS + Couchbase)[Testing Phase]                   |"
  echo "|-----------------------------------------------------------------|"
  read -rp "Persistence layer?                                                  " choicePersistence
  case "$choicePersistence" in
    1 ) PERSISTENCE_TYPE="couchbase"  ;;
    2 ) PERSISTENCE_TYPE="hybrid"  ;;
    * ) PERSISTENCE_TYPE="ldap"  ;;
  esac
  #COUCHBASE
  CB_PW=""
  CB_USER="admin"
  COUCHBASE_URL="couchbase"
  LDAP_MAPPING="default"
  if [[ $choicePersistence -eq 2 ]]; then
    echo "|-----------------------------------------------------------------|"
    echo "|                     Hybrid [WrendDS + Couchbase]                |"
    echo "|-----------------------------------------------------------------|"
    echo "| [0] Default                                                     |"
    echo "| [1] User                                                        |"
    echo "| [2] Site                                                        |"
    echo "| [3] Cache                                                       |"
    echo "| [4] Token                                                       |"
    echo "|-----------------------------------------------------------------|"
    read -rp "Persistence type?                                                 " choiceHybrid
    case "$choiceHybrid" in
      1 ) LDAP_MAPPING="user"  ;;
      2 ) LDAP_MAPPING="site"  ;;
      3 ) LDAP_MAPPING="cache" ;;
      4 ) LDAP_MAPPING="token"  ;;
      * ) LDAP_MAPPING="default"  ;;
    esac
  fi
  if [[ $choiceDeploy -eq 1 ]]; then
    kubectl=microk8s.kubectl || emp_output
  else
    kubectl=kubectl || emp_output
  fi
  check_k8version
  if [[ $choiceDeploy -eq 2 ]] || [[ $choiceDeploy -eq 1 ]]; then
    gather_ip
    until confirm_ip; do : ; done
    ip=$HOST_IP	    
  else
    # Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
    ip=22.22.22.22
  fi
  if [[ $choiceDeploy -eq 3 ]] \
    || [[ $choiceDeploy -eq 4 ]] \
    || [[ $choiceDeploy -eq 5 ]]; then
    echo "|-----------------------------------------------------------------|"
    echo "|                     AWS Loadbalancer type                       |"
    echo "|-----------------------------------------------------------------|"
    echo "| [0] Classic Load Balancer (CLB) [default]                       |"
    echo "| [1] Network Load Balancer (NLB) -- Static IP                    |"
    echo "|-----------------------------------------------------------------|"
    read -rp "Loadbalancer type ?                                               " lbChoicenumber
    case "$lbChoicenumber" in
      0 ) lbChoice="clb"  ;;
      1 ) lbChoice="nlb"  ;;
      * ) lbChoice="clb"  ;;
    esac
  fi
  if [[ $choicePersistence -ge 1 ]]; then
    COUCHBASE_URL=""
    echo "For the following prompt  if placed [N] the couchbase 
      is assumed to be installed or remotely provisioned"
    read -rp "Install Couchbase[Y][Y/N] ?                                       " installCB
    if [[ $installCB != "n" || $installCB != "N" ]]; then
      if [ -f couchbase-autonomous-operator-kubernetes_*.tar.gz ];then
        read -rp "Please enter the volume type for EBS.[io1]    :           \
          " VOLUME_TYPE && set_default "$VOLUME_TYPE" "io1" "VOLUME_TYPE"
        read -rp "Please enter a namespace for CB objects. \
          Confine to 4 lowercase letters only.[cbns] \
          " namespace && set_default "$namespace" "cbns" "namespace"
        read -rp "Please enter a cluster name. \
          Confine to 6 lowercase letter only.[cbgluu] \
          " clustername && set_default "$clustername" "cbgluu" "clustername"
        COUCHBASE_URL="$clustername.$namespace.svc.cluster.local"
      else
        echo "Error: Couchbase package not found."
        echo "Please download the couchbase kubernetes package and place it inside
          the same directory containing the create.sh script.
          https://www.couchbase.com/downloads"
    exit 1
  fi

    fi
    if [ -z "$COUCHBASE_URL" ];then
      read -rp "Please enter remote couchbase URL base name, 
        couchbase.gluu.org       " COUCHBASE_URL
    fi
    read -rp "Please enter couchbase username [admin]                          " CB_USER \
      && set_default "$CB_USER" "admin" "CB_USER"
    #TODO: Add test CB connection
    while true; do
      CB_PW_RAND="$(cat /dev/urandom \
        | env LC_CTYPE=C tr -dc 'a-zA-Z0-9A-Za-z0-9!"#$' \
        | fold -w 6 | head -c 6)"GlU4%
      CB_PW_RAND_OUT=${CB_PW_RAND::3}
      CB_PW_RAND_OUT="$CB_PW_RAND_OUT***"
      echo "Enter couchbase password.Min 6 letters [$CB_PW_RAND_OUT]:"
      mask_password
      if [[ ! "$password" ]]; then
        CB_PW=$CB_PW_RAND
        break
      else
        CB_PW=$password 
        echo "Confirm couchbase password. Min 6 letters:"
        mask_password
        CB_PW_CM=$password
        [ "$CB_PW" = "$CB_PW_CM" ] && break || echo "Please try again"
      fi
    done
    echo "$CB_PW" > couchbase_password
    echo "Password is located in couchbase_password.
      Please save your password securely and delete file couchbase_password"
  fi
  read -rp "Deploy Cr-Rotate[N]?[Y/N]                                          " choiceCR
  read -rp "Deploy Key-Rotation[N]?[Y/N]                                       " choiceKeyRotate
  read -rp "Deploy Radius[N]?[Y/N]                                             " choiceRadius
  read -rp "Deploy Passport[N]?[Y/N]                                           " choicePassport
  read -rp "[Testing Phase] Deploy Casa[N]?[Y/N]                               " choiceCasa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    choiceOXD="Y"
  else
    read -rp "Deploy OXD-Server[N]?[Y/N]                                       " choiceOXD
  fi
  if [[ $choiceOXD == "Y" || $choiceOXD == "y" ]]; then
    if [[ $machine == Linux ]]; then
      apt-get update -y
      apt-get install openjdk-8-jdk -y
    fi
    keytool -genkey -noprompt \
      -alias oxd-server \
      -dname "CN=oxd-server, OU=ID, O=Gluu, L=Gluu, S=TX, C=US" \
      -keystore oxd-server.keystore \
      -storepass example \
      -keypass example \
      -deststoretype pkcs12 \
      -keysize 2048 || emp_output
  fi
  generate=0
  echo "[I] Preparing cluster-wide config and secrets"
  echo "[I] Checking existing config parameters configmap"
  paramcheck=$($kubectl get cm -l app=config-init-load || emp_output)
  if [[ $paramcheck -eq 0 ]]; then
    generate=1
    echo "No config parameters found"
  else
    echo "[I] Found existing parametes configmap"
    $kubectl get cm config-generate-params -o yaml | cat -
    read -rp "[I] Use pervious params? [Y/n]                                   " param_choice
    if [[ $param_choice != "y" && $param_choice != "Y" ]]; then
      generate=1
    fi
  fi
  # config is not loaded from previously saved configuration
  if [[ $generate -eq 1 ]]; then
    echo "[I] Removing all previous gluu services if found"
    #delete_all
    echo "[I] Creating new configuration, please input the following parameters"
    read -rp "Enter Hostname [demoexample.gluu.org]:                           " FQDN \
      && set_default "$FQDN" "demoexample.gluu.org" "FQDN"
    if ! [[ $FQDN == *"."*"."* ]]; then
      echo "[E] Hostname provided is invalid. 
        Please enter a FQDN with the format demoexample.gluu.org"
      exit 1
    fi
    read -rp "Enter Country Code [US]:                                         " COUNTRY_CODE \
      && set_default "$COUNTRY_CODE" "US" "COUNTRY_CODE"
    read -rp "Enter State [TX]:                                                " STATE \
      && set_default "$STATE" "TX" "STATE"
    read -rp "Enter City [Austin]:                                             " CITY \
      && set_default "$CITY" "Austin" "CITY"
    read -rp "Enter Email [support@gluu.org]:                                  " EMAIL \
      && set_default "$EMAIL" "support@gluu.org" "EMAIL"
    read -rp "Enter Organization [Gluu]:                                       " ORG_NAME \
      && set_default "$ORG_NAME" "Gluu" "ORG_NAME"
    echo "$CB_PW" > couchbase_password
    while true; do
      ADMIN_PW_RAND="$(cat /dev/urandom \
       | env LC_CTYPE=C tr -dc 'a-zA-Z0-9A-Za-z0-9!"#$' \
       | fold -w 6 | head -c 6)"GlU4%
      ADMIN_PW_RAND_OUT=${ADMIN_PW_RAND::3}
      ADMIN_PW_RAND_OUT="$ADMIN_PW_RAND_OUT***"
      echo "Password will be located in gluu_admin_password.
Please save your password securely and delete file gluu_admin_password"
      echo "Enter Gluu Admin/LDAP Password [$ADMIN_PW_RAND_OUT]:"
      mask_password
      if [[ ! "$password" ]]; then
        ADMIN_PW=$ADMIN_PW_RAND
        break
      else
        ADMIN_PW=$password
        echo "Confirm Admin/LDAP Password: "
        mask_password
        password2=$password
        [ "$ADMIN_PW" = "$password2" ] && break || echo "Please try again"
      fi
    done
    echo "$ADMIN_PW" > gluu_admin_password
    read -rp "Continue with the above settings? [Y/n]                          " choiceCont
    case "$choiceCont" in
      y|Y ) ;;
      n|N ) exit 1 ;;
      * )   ;;
    esac
    echo "{" > config/base/generate.json
    echo '"hostname"': \"$FQDN\", >> config/base/generate.json
    echo '"country_code"': \"$COUNTRY_CODE\", >> config/base/generate.json
    echo '"state"': \"$STATE\", >> config/base/generate.json
    echo '"city"': \"$CITY\", >> config/base/generate.json
    echo '"admin_pw"': \"$ADMIN_PW\", >> config/base/generate.json
    echo '"email"': \"$EMAIL\", >> config/base/generate.json
    echo '"org_name"': \"$ORG_NAME\" >> config/base/generate.json
    echo "}" >> config/base/generate.json
  else
    read -rp "Please confirm your FQDN                                         " FQDN
  fi
}

prompt_zones() {
  #output the zones out to the user
  zones=$($kubectl get nodes -o json | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]')
  arrzones=($zones)
  numberofzones="${#arrzones[@]}"
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  echo "You will be asked to enter a zone for each service.
    Please confine the zones to where your nodes zones are which are the following: "
  echo $zones
  read -rp "Config storage class zone [Auto-Assign]:                           " SC_CONFIG_ZONE \
    && set_default "$SC_CONFIG_ZONE" "${arrzones[$arrspot]}" "SC_CONFIG_ZONE" 
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Ldap storage class zone [Auto-Assign]:                           " SC_LDAP_ZONE \
      && set_default "$SC_LDAP_ZONE" "${arrzones[$arrspot]}" "SC_LDAP_ZONE"
  fi
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  read -rp "oxAuth storage class zone [Auto-Assign]:                           " SC_OXAUTH_ZONE \
    && set_default "$SC_OXAUTH_ZONE" "${arrzones[$arrspot]}" "SC_OXAUTH_ZONE"
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  # OXD server (activate below line if volumes are added)
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    read -rp "oxdServer storage class zone [Auto-Assign]:                      " SC_OXDSERVER_ZONE \
      && set_default "$SC_OXDSERVER_ZONE" "${arrzones[$arrspot]}" "SC_OXDSERVER_ZONE"
  fi
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  read -rp "oxTrust storage class zone: [Auto-Assign]                          " SC_OXTRUST_ZONE \
    && set_default "$SC_OXTRUST_ZONE" "${arrzones[$arrspot]}" "SC_OXTRUST_ZONE"
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    read -rp "Radius storage class zone: [Auto-Assign]                         " SC_RADIUS_ZONE \
      && set_default "$SC_RADIUS_ZONE" "${arrzones[$arrspot]}" "SC_RADIUS_ZONE"
  fi
  arrspot="$(echo $RANDOM % $numberofzones + 0 | bc)"
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    read -rp "Casa storage class zone:  [Auto-Assign]                          " SC_CASA_ZONE \
      && set_default "$SC_CASA_ZONE" "${arrzones[$arrspot]}" "SC_CASA_ZONE"
  fi
}

prompt_storage() {
  read -rp "Size of config volume storage [4Gi]:                               " STORAGE_CONFIG \
    && set_default "$STORAGE_CONFIG" "4Gi" "STORAGE_CONFIG"
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Size of ldap volume storage [4Gi]:                               " STORAGE_LDAP \
      && set_default "$STORAGE_LDAP" "4Gi" "STORAGE_LDAP"
  fi
  read -rp "Size of oxAuth volume storage [4Gi]:                               " STORAGE_OXAUTH \
    && set_default "$STORAGE_OXAUTH" "4Gi" "STORAGE_OXAUTH"
  read -rp "Size of oxTrust volume storage [4Gi]:                              " STORAGE_OXTRUST \
    && set_default "$STORAGE_OXTRUST" "4Gi" "STORAGE_OXTRUST"
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius Volume storage
    read -rp "Size of Radius volume storage [4Gi]:                             " STORAGE_RADIUS \
      && set_default "$STORAGE_RADIUS" "4Gi" "STORAGE_RADIUS"
  fi
  if [[ $choiceDeploy -ne 6 ]] \
    && [[ $choiceDeploy -ne 7 ]] \
    && [[ $choiceDeploy -ne 8 ]] \
    && [[ $choiceDeploy -ne 9 ]] \
    && [[ $choiceDeploy -ne 10 ]] \
    && [[ $choiceDeploy -ne 11 ]]; then
    read -p "Size of Shared-Shib volume storage [4Gi]:                         " STORAGE_SHAREDSHIB \
      && set_default "$STORAGE_SHAREDSHIB" "4Gi" "STORAGE_SHAREDSHIB"
  fi
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    # OXD server
    read -rp "Size of oxdServer volume storage [4Gi]:                          " STORAGE_OXDSERVER \
      && set_default "$STORAGE_OXDSERVER" "4Gi" "STORAGE_OXDSERVER"
  fi
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    read -rp "Size of Casa      volume storage [4Gi]:                          " STORAGE_CASA \
      && set_default "$STORAGE_CASA" "4Gi" "STORAGE_CASA"
  fi
}

gke_prompts() {
  oxpassport_oxshibboleth_folder="overlays/gke"
  read -rp "Please enter valid email for Google Cloud account:                 " ACCOUNT
  read -rp "Please enter valid Zone name used when creating the cluster:       " ZONE
  SC_LDAP_ZONE=$ZONE
  echo "Trying to login user"
  NODE=$(kubectl get no \
    -o go-template='{{range .items}}{{.metadata.name}} {{end}}' \
    | awk -F " " '{print $1}')
  HOME_DIR=$(gcloud compute ssh root@$NODE --zone $ZONE --command='echo $HOME' \
    || echo "Permission denied")
  if [[ $HOME_DIR =~ "Permission denied" ]];then
    echo "This occurs when your compute instance has 
      PermitRootLogin set to  no in it's SSHD config.
      Trying to login using user"
    HOME_DIR=$(gcloud compute ssh user@$NODE --zone $ZONE --command='echo $HOME')
  fi
  prompt_nfs
}

prompt_nfs() {
  $kustomize nfs/base/ > $output_yamls/nfs.yaml
   read -rp "NFS storage volume [4Gi]:                                         " STORAGE_NFS \
     && set_default "$STORAGE_NFS" "4Gi" "STORAGE_NFS"
}

prompt_volumes_identitfier() {
  read -rp "Please enter $static_volume_prompt for Config:                     " CONFIG_VOLUMEID
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Please enter $static_volume_prompt for LDAP:                     " LDAP_VOLUMEID
  fi
  read -rp "Please enter $static_volume_prompt for oxAuth:                     " OXAUTH_VOLUMEID
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    # OXD server
    read -rp "Please enter $static_volume_prompt for OXD-server                " OXDSERVER_VOLUMEID
  fi
  read -rp "Please enter $static_volume_prompt for oxTrust:                    " OXTRUST_VOLUMEID
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    read -rp "Please enter $static_volume_prompt for Radius:                   " RADIUS_VOLUMEID
  fi
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    # Radius server
    read -rp "Please enter $static_volume_prompt for Casa:                     " CASA_VOLUMEID
  fi  
}

prompt_disk_uris() {
  read -rp "Please enter the disk uri for Config:                              " CONFIG_DISKURI
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Please enter the disk uri for LDAP:                              " LDAP_DISKURI
  fi
  read -rp "Please enter the disk uri for oxAuth:                              " OXAUTH_DISKURI
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    # OXD server
    read -rp "Please enter the disk uri for OXD-server:                        " OXDSERVER_DISKURI
  fi
  read -rp "Please enter the disk uri for oxTrust:                             " OXTRUST_DISKURI
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    read -rp "Please enter the disk uri for Radius:                            " RADIUS_DISKURI
  fi
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    read -rp "Please enter the disk uri for Casa:                              " CASA_DISKURI
  fi  
}

generate_yamls() {
  read -rp "Are you using a globally resolvable FQDN [N] [Y/N]:                " FQDN_CHOICE
  if [[ $FQDN_CHOICE == "y" || $FQDN_CHOICE == "Y" ]]; then
  echo "Please place your FQDN certification and key inside 
    ingress.crt and ingress.key respectivley."
    if [ ! -f ingress.crt ] \
      || [ ! -s ingress.crt ] \
      || [ ! -f ingress.key ] \
      || [ ! -s ingress.key ]; then
      echo "Check that  ingress.crt and ingress.key are not empty 
        and contain the right information for your FQDN. "
      exit 1
    fi
  fi  
  oxpassport_oxshibboleth_folder="overlays/eks"
  
  if [[ $choiceDeploy -eq 0 ]]; then
    exit 1

  elif [[ $choiceDeploy -eq 3 ]]; then
    mkdir localeksyamls || emp_output
    output_yamls=localeksyamls
    yaml_folder=$local_eks_folder
    # Shared-Shib
    shared_shib_child_folder="eks"

  elif [[ $choiceDeploy -eq 4 ]]; then
    echo "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html"
    echo "Follow the doc above to help you choose 
      which volume type to use.Options are [gp2,io1,st1,and sc1]"
    read -rp "Please enter the volume type for EBS[io1]:                       " VOLUME_TYPE \
      && set_default "$VOLUME_TYPE" "io1" "VOLUME_TYPE"
    mkdir dynamiceksyamls || emp_output
    output_yamls=dynamiceksyamls
    yaml_folder=$dynamic_eks_folder
    prompt_zones
    shared_shib_child_folder="eks"

  elif [[ $choiceDeploy -eq 6 ]]; then
    mkdir localgkeyamls || emp_output
    output_yamls=localgkeyamls
    yaml_folder=$local_gke_folder
    gke_prompts

  elif [[ $choiceDeploy -eq 5 ]]; then
    mkdir staticeksyamls || emp_output
    output_yamls=staticeksyamls
    yaml_folder=$static_eks_folder
    echo "Zones of your volumes are required to match the deployments to the volume zone"
    prompt_zones
    static_volume_prompt="EBS Volume ID"
    prompt_volumes_identitfier
    shared_shib_child_folder="eks"

  elif [[ $choiceDeploy -eq 2 ]]; then
    create_local_minikube
    output_yamls=localminikubeyamls
    yaml_folder=$local_minikube_folder
    shared_shib_child_folder="minikube"

  elif [[ $choiceDeploy -eq 7 ]]; then
    echo "Please enter the volume type for the persistent disk."
    read -rp "Options are (pd-standard, pd-ssd). [pd-ssd] :                    " VOLUME_TYPE \
      && set_default "$VOLUME_TYPE" "pd-ssd" "VOLUME_TYPE"
    create_dynamic_gke
    output_yamls=dynamicgkeyamls
    yaml_folder=$dynamic_gke_folder
    gke_prompts

  elif [[ $choiceDeploy -eq 8 ]]; then
    create_static_gke
    output_yamls=staticgkeyamls
    static_volume_prompt="Persistent Disk Name"
    echo 'Place the name of your persistent disks between two quotes as such 
      "gke-testinggluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd"'
    prompt_volumes_identitfier
    yaml_folder=$static_gke_folder
    gke_prompts

  elif [[ $choiceDeploy -eq 9 ]]; then
    create_local_azure
    output_yamls=localazureyamls
    yaml_folder=$local_azure_folder
    prompt_nfs

  elif [[ $choiceDeploy -eq 10 ]]; then
    echo "https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-types"
    echo "Please enter the volume type for the persistent disk. Example:UltraSSD_LRS,"
    echo "Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')"
    read -rp "[Premium_LRS] :                                                  " VOLUME_TYPE \
      && set_default "$VOLUME_TYPE" "Premium_LRS" "VOLUME_TYPE"
    echo "Outputing available zones used : "
    $kubectl get nodes -o json \
      | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]'
    read -rp "Please enter a valid Zone name used this might be set to 0:      " ZONE \
      && set_default "$ZONE" "0" "ZONE"
    SC_LDAP_ZONE=$ZONE
    create_dynamic_azure
    output_yamls=dynamicazureyamls
    yaml_folder=$dynamic_azure_folder
    prompt_nfs

  elif [[ $choiceDeploy -eq 11 ]]; then
    echo "https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-types"
    echo "Please enter the volume type for the persistent disk. Example:UltraSSD_LRS,"
    echo "Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')"
    read -rp "[Premium_LRS] :                                                  " VOLUME_TYPE \
      && set_default "$VOLUME_TYPE" "Premium_LRS" "VOLUME_TYPE"
    echo "Outputing available zones used : "
    $kubectl get nodes -o json | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]'
    read -rp "Please enter a valid Zone name used this might be set to 0:      " ZONE \
      && set_default "$ZONE" "0" "ZONE"
    SC_LDAP_ZONE=$ZONE
    create_static_azure
    static_volume_prompt="Persistent Disk Name"
    prompt_volumes_identitfier
    prompt_disk_uris
    output_yamls=staticazureyamls
    yaml_folder=$static_azure_folder
    prompt_nfs

  else
    mkdir localmicrok8syamls || emp_output
    output_yamls=localmicrok8syamls
    yaml_folder=$local_microk8s_folder
    shared_shib_child_folder="microk8s"
  fi
  # Get prams for the yamls
  prompt_storage
  if [[ $choiceDeploy -ne 6 ]] \
    && [[ $choiceDeploy -ne 7 ]] \
    && [[ $choiceDeploy -ne 8 ]] \
    && [[ $choiceDeploy -ne 9 ]] \
    && [[ $choiceDeploy -ne 10 ]] \
    && [[ $choiceDeploy -ne 11 ]]; then
    $kustomize shared-shib/$shared_shib_child_folder/ \
      | replace_all  > $output_yamls/shared-shib.yaml
  fi
  # Config
  $kustomize config/$yaml_folder | replace_all > $output_yamls/config.yaml
  # WrenDS
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    $kustomize ldap/$yaml_folder | replace_all > $output_yamls/ldap.yaml
  fi
  # Persistence
  $kustomize persistence/base | replace_all > $output_yamls/persistence.yaml
  # oxAuth
  $kustomize oxauth/$yaml_folder | replace_all > $output_yamls/oxauth.yaml
  # oxTrust
  $kustomize oxtrust/$yaml_folder | replace_all > $output_yamls/oxtrust.yaml
  # oxShibboleth
  $kustomize oxshibboleth/$oxpassport_oxshibboleth_folder \
    | replace_all  > $output_yamls/oxshibboleth.yaml
  if [[ $choicePassport == "y" || $choicePassport == "Y" ]]; then
    # oxPassport
    $kustomize oxpassport/$oxpassport_oxshibboleth_folder \
      | replace_all  > $output_yamls/oxpassport.yaml
  fi
  if [[ $choiceRotate == "y" || $choiceRotate == "Y" ]]; then
    # Key Rotationls
    $kustomize key-rotation/base | replace_all > $output_yamls/key-rotation.yaml
  fi
  if [[ $choiceCR == "y" || $choiceCR == "Y" ]]; then
    # Cache Refresh rotating IP registry
    $kustomize cr-rotate/base | replace_all > $output_yamls/cr-rotate.yaml
  fi
    # OXD-Server
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    $kustomize oxd-server/novolume | replace_all > $output_yamls/oxd-server.yaml
  fi
    # Casa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    $kustomize casa/$yaml_folder | replace_all > $output_yamls/casa.yaml
  fi  
  # Radius
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    $kustomize radius/$yaml_folder | replace_all > $output_yamls/radius.yaml
  fi
  if [[ $choiceCache == 2 ]];then
    $kustomize redis/base/ | replace_all > $output_yamls/redis.yaml
  fi  
  if [[ $FQDN_CHOICE != "y" || $FQDN_CHOICE != "Y" ]]; then
    $kustomize update-lb-ip/base > $output_yamls/updatelbip.yaml
  else
    # Remove hostAliases object from yamls
    cat $output_yamls/oxauth.yaml \
      | $sed '/LB_ADDR: LBADDR/d' \
      | $sed '/hostAliases:/d' \
      | $sed '/- hostnames:/d' \
      | $sed "/$FQDN/d" \
      | $sed '/ip: NGINX_IP/d' > tmpfile \
      && mv tmpfile $output_yamls/oxauth.yaml \
      || emp_output
    cat $output_yamls/oxpassport.yaml \
      | $sed '/LB_ADDR: LBADDR/d' \
      | $sed '/hostAliases:/d' \
      | $sed '/- hostnames:/d' \
      | $sed "/$FQDN/d" \
      | $sed '/ip: NGINX_IP/d' > tmpfile \
      && mv tmpfile $output_yamls/oxpassport.yaml \
      || emp_output
    cat $output_yamls/oxshibboleth.yaml \
      | $sed '/LB_ADDR: LBADDR/d' \
      | $sed '/hostAliases:/d' \
      | $sed '/- hostnames:/d' \
      | $sed "/$FQDN/d" \
      | $sed '/ip: NGINX_IP/d' > tmpfile \
      && mv tmpfile $output_yamls/oxshibboleth.yaml \
      || emp_output
    cat $output_yamls/oxtrust.yaml \
      | $sed '/LB_ADDR: LBADDR/d' \
      | $sed '/hostAliases:/d' \
      | $sed '/- hostnames:/d' \
      | $sed "/$FQDN/d" \
      | $sed '/ip: NGINX_IP/d' > tmpfile \
      && mv tmpfile $output_yamls/oxtrust.yaml \
      || emp_output
    cat $output_yamls/radius.yaml \
      | $sed '/LB_ADDR: LBADDR/d' \
      | $sed '/hostAliases:/d' \
      | $sed '/- hostnames:/d' \
      | $sed "/$FQDN/d" \
      | $sed '/ip: NGINX_IP/d' > tmpfile \
      && mv tmpfile $output_yamls/radius.yaml \
      || emp_output
    cat $output_yamls/casa.yaml \
      | $sed '/LB_ADDR: LBADDR/d' \
      | $sed '/hostAliases:/d' \
      | $sed '/- hostnames:/d' \
      | $sed "/$FQDN/d" \
      | $sed '/ip: NGINX_IP/d' > tmpfile \
      && mv tmpfile $output_yamls/casa.yaml \
      || emp_output
  fi
    echo " all yamls have been generated in $output_yamls folder"
}

deploy_nginx() {
  if [[ $choiceDeploy -eq 1 ]]; then
    # If microk8s ingress
    microk8s.enable ingress dns || emp_output
  fi
  if [[ $choiceDeploy -eq 2 ]]; then
    # If minikube ingress
    minikube addons enable ingress || emp_output
  fi
  # Nginx
  $kubectl apply -f nginx/mandatory.yaml
  if [[ $choiceDeploy -eq 3 ]] \
    || [[ $choiceDeploy -eq 4 ]] \
    || [[ $choiceDeploy -eq 5 ]]; then
    if [[ $lbChoice == "nlb" ]];then
      $kubectl apply -f nginx/nlb-service.yaml
    else
      $kubectl apply -f nginx/service-l4.yaml 
      $kubectl apply -f nginx/patch-configmap-l4.yaml
    fi
    lbhostname=""
    while true; do
      echo "Waiting for loadbalancer address.."
      if [[ $lbhostname ]]; then
        break
      fi
      lbhostname=$($kubectl -n ingress-nginx get svc ingress-nginx \
        --output jsonpath='{.status.loadBalancer.ingress[0].hostname}' || echo "")
      hostname="'${lbhostname}'" || emp_output 
      sleep 20	  
      done
  fi

  if [[ $choiceDeploy -eq 6 ]] \
    || [[ $choiceDeploy -eq 7 ]] \
    || [[ $choiceDeploy -eq 8 ]] \
    || [[ $choiceDeploy -eq 9 ]] \
    || [[ $choiceDeploy -eq 10 ]] \
    || [[ $choiceDeploy -eq 11 ]]; then
    $kubectl apply -f nginx/cloud-generic.yaml
    $kubectl apply -f nfs/base/services.yaml
    ip=""
    echo "Waiting for the ip of the Loadbalancer"
    while true; do
      if [[ $ip ]]; then
        break
      fi
      #GKE and Azure get external IP
      ip=$($kubectl -n ingress-nginx get svc ingress-nginx \
        --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
      sleep 20
      done
      echo "IP: $ip"
  fi
  cat nginx/nginx.yaml | $sed "s/\<FQDN\>/$FQDN/" | $kubectl apply -f -
}

deploy_redis() {
  # Redis
  cat $output_yamls/redis.yaml | $kubectl apply -f -
  is_pod_ready "app=redis"
}

deploy_config() {
  # Config
  cat $output_yamls/config.yaml | $kubectl apply -f -
  is_pod_ready "app=config-init-load"
}

deploy_ldap() {
  # LDAP
  cat $output_yamls/ldap.yaml | $kubectl apply -f -
  is_pod_ready "app=opendj"
  echo "[I] Deploying LDAP ..."
  while true; do
    ldaplog=$($kubectl logs -l app=opendj || emp_output)
    if [[ $ldaplog =~ "The Directory Server has started successfully" ]]; then
      break
    fi
    sleep 20
  done
}

deploy_persistence() {
  # Persistence
  cat $output_yamls/persistence.yaml | $kubectl apply -f -
  echo "Trying to import ldifs..."
  is_pod_ready "app=persistence-load"
  while true; do
    persistencelog=$($kubectl logs -l app=persistence-load || emp_output)
    if [[ $persistencelog =~ "Importing o_metric.ldif file" ]]; then
      break
    fi
    sleep 30
  done
}

deploy_shared_shib() {
  if [[ $choiceDeploy -eq 6 ]] \
    || [[ $choiceDeploy -eq 7 ]] \
    || [[ $choiceDeploy -eq 8 ]] \
    || [[ $choiceDeploy -eq 9 ]] \
    || [[ $choiceDeploy -eq 10 ]] \
    || [[ $choiceDeploy -eq 11 ]]; then
    NFS_IP=""
    while true; do
      if [[ $NFS_IP ]] ; then
        break
      fi
      NFS_IP=$($kubectl get svc nfs-server --output jsonpath='{.spec.clusterIP}')
      sleep 30
    done
    # setup NFS
    cat $output_yamls/nfs.yaml \
      | $sed -s "s@STORAGENFS@$STORAGE_NFS@g" \
      | $sed -s "s@NFSIP@$NFS_IP@g" \
      | $kubectl apply -f -
    is_pod_ready "role=nfs-server"
    $kubectl exec -ti $($kubectl get pods -l role=nfs-server \
      -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}') \
      -- mkdir -p /exports/opt/shared-shibboleth-idp
  else
    cat $output_yamls/shared-shib.yaml  | $kubectl apply -f - || emp_output
  fi
}

deploy_update_lb_ip() {
  # Update LB 
  $kubectl apply -f $output_yamls/updatelbip.yaml || emp_output
}

deploy_oxauth() {
  $kubectl create configmap casacm --from-file=casa.json -o yaml --dry-run > casacm.yaml
  $kubectl apply -f casacm.yaml
  cat $output_yamls/oxauth.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f -
  is_pod_ready "app=oxauth"
}

deploy_oxd() {
  # OXD server
  $kubectl create secret generic oxdkeystorecm --from-file=oxd-server.keystore
  cat $output_yamls/oxd-server.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f -
  is_pod_ready "app=oxd-server"
}

deploy_casa() {
  # Casa
  cat $output_yamls/casa.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f -
  is_pod_ready "app=casa"
  podname_template='{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'
  casapodname=$($kubectl get pod -l=app=casa -o template --template="$podname_template" \
    || echo "")
  $kubectl cp $casapodname:etc/gluu/conf/casa.json ./casa.json
  rm casacm.yaml
  $kubectl create configmap casacm --from-file=casa.json -o yaml --dry-run > casacm.yaml
  $kubectl apply -f casacm.yaml
  rm casacm.yaml
  # restart oxauth 
  $kubectl scale deployment oxauth --replicas=0
  sleep 5
  $kubectl scale deployment oxauth --replicas=1
}

deploy_oxtrust() {
  cat $output_yamls/oxtrust.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f -
  is_pod_ready "app=oxtrust"
}

deploy_oxshibboleth() {
  cat $output_yamls/oxshibboleth.yaml \
    | $sed -s "s@NGINX_IP@$ip@g"  \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f -
  is_pod_ready "app=oxshibboleth"
}

deploy_oxpassport() {
  echo "---------------------------------------------------------------------------------------------------------------"
  echo "Please enable Passport in the Gluu GUI in order for oxpassport pod to run."
  echo "Configuration > Organization configuration > System Configuration > Check Passport Support and press update" 
  echo "Please enable the following scripts in the Gluu GUI"
  echo "Configuration > Manage Custom Scripts > Person Authentication > passport_social > Check Enabled and press update"
  echo "Configuration > Manage Custom Scripts > UMA RPT Policies > scim_access_policy > Check Enabled and press update"
  echo "---------------------------------------------------------------------------------------------------------------"

  cat $output_yamls/oxpassport.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f -
  is_pod_ready "app=oxpassport"
}

deploy_key_rotation() {
  $kubectl apply -f $output_yamls/key-rotation.yaml || emp_output
  is_pod_ready "app=key-rotation"
}

deploy_radius() {
  echo "---------------------------------------------------------------------------------------------------------------"
  echo "Please enable Radius in the Gluu GUI."
  echo "Configuration > Organization configuration > System Configuration > Check Gluu Radius Support and press update" 
  echo "---------------------------------------------------------------------------------------------------------------"
  cat $output_yamls/radius.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" \
    | $kubectl apply -f - \
    || emp_output
  is_pod_ready "app=radius"
}

deploy_cr_rotate() {
  $kubectl apply -f  $output_yamls/cr-rotate.yaml || emp_output
}

deploy() {
  ls $output_yamls || true
  read -rp "Deploy the generated yamls? [Y/n]                                  " choiceContDeploy
  case "$choiceContDeploy" in
    y|Y ) ;;
    n|N ) exit 1 ;;
    * )   ;;
  esac
  prompt_cb
  $kubectl create secret generic cb-pass --from-file=couchbase_password || true
  $kubectl create secret generic cb-crt --from-file=couchbase.crt || true
  deploy_config
  setup_tls
  if [[ $choiceCache == 2 ]];then
    deploy_redis
  fi 
  # If hybrid or just ldap
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    deploy_ldap
  fi
  deploy_nginx
  deploy_persistence
  deploy_update_lb_ip
  deploy_oxauth
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    deploy_oxd
  fi
    # Casa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    deploy_casa
  fi
  deploy_shared_shib
  deploy_oxtrust
  deploy_oxshibboleth
  if [[ $choicePassport == "y" || $choicePassport == "Y" ]]; then
    deploy_oxpassport
  fi
  if [[ $choiceCR == "y" || $choiceCR == "Y" ]]; then
    deploy_cr_rotate
  fi
  if [[ $choiceRotate == "y" || $choiceRotate == "Y" ]]; then
    deploy_key_rotation
  fi
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    deploy_radius
  fi
}

# ==========
# entrypoint
# ==========

case $1 in
  "install"|"")
    touch couchbase.crt
    touch couchbase_password
    touch casa.json
    find_host
    prepare_config
    generate_yamls
    deploy
    ;;
  delete)
    delete_all
    ;;
  *)
    echo "[E] Unsupported command; please choose 'install', or  'delete'"
    exit 1
    ;;
esac