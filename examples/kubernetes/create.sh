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
efs_eks_folder="overlays/eks/efs/"
#GCE
local_gke_folder="overlays/gke/local-storage/"
dynamic_gke_folder="overlays/gke/dynamic-pd/"
static_gke_folder="overlays/gke/static-pd/"
#AZURE
local_azure_folder="overlays/azure/local-storage/"
dynamic_azure_folder="overlays/azure/dynamic-dn/"
static_azure_folder="overlays/azure/static-dn/"

emp_output() {
  >/dev/null 2>&1
  echo "Skipping command..."
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
  if [ -d "gluuminikubeyamls" ];then
    manifestsfolder=gluuminikubeyamls
  elif [ -d "gluueksyamls" ];then
    manifestsfolder=gluueksyamls
  elif [ -d "gluugkeyamls" ];then
    manifestsfolder=gluugkeyamls
  elif [ -d "gluuaksyamls" ];then
    manifestsfolder=gluuaksyamls
  else
    kubectl=microk8s.kubectl
    manifestsfolder=gluumicrok8yamls
    rm -rf /data || emp_output
  fi
  $timeout 10 $kubectl delete deploy,pvc,pv,cm,secrets,svc -l app=casa --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete ClusterRoleBinding,Job,RoleBinding,Role,cm -l app=config-init-load --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete DaemonSet,svc,ClusterRoleBinding,Role,cm -l app=cr-rotate --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete Deployment,svc,cm -l app=key-rotation --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete StatefulSet,svc,cm,StorageClass,PersistentVolume,pvc -l app=opendj --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete deploy,pvc,pv,cm,secrets,svc -l app=oxauth --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete deploy,pvc,pv,cm,secrets,svc -l app=oxd-server --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete deploy,pvc,pv,cm,secrets,svc -l app=oxpassport --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete StatefulSet,pvc,pv,cm,secrets,svc -l app=oxshibboleth --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete StatefulSet,pvc,pv,cm,secrets,svc -l app=oxtrust --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete ClusterRoleBinding,Job,RoleBinding,Role,cm -l app=persistence-load --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete Deployment,svc,cm -l app=radius --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete Deployment,svc,cm -l app=redis --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete pvc,pv,svc,cm -l app=shared-shib --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete Role,RoleBinding,ClusterRole,ClusterRoleBinding,ServiceAccount,StorageClass,PersistentVolumeClaim,Deployment,svc -l app=efs-provisioner --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete pvc,pv,ReplicationController,svc,cm,secrets -l app=nfs-server --force --grace-period=0 --ignore-not-found || emp_output
  $timeout 10 $kubectl delete cm gluu casacm updatelbip --ignore-not-found || emp_output
  $timeout 10 $kubectl delete secret oxdkeystorecm gluu tls-certificate cb-pass cb-crt --ignore-not-found || emp_output
  $timeout 10 $kubectl delete -f nginx/ --ignore-not-found || emp_output
  rm oxd-server.keystore || emp_output
  if [ -d "gluueksyamls" ] \
    || [ -d "gluugkeyamls" ] \
    || [ -d "gluuaksyamls" ]; then
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
  rm -rf old$manifestsfolder || emp_output
  mv -f $manifestsfolder old$manifestsfolder || emp_output
  mv ingress.crt previous-ingress.crt || emp_output
  mv ingress.key previous-ingress.key || emp_output
  delete_cb
}

delete_cb() {
  echo "Deleting Couchbase objects if exist..."
  namespace_template='{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'
  namespaces=$($kubectl get ns -o template --template="$namespace_template" \
    || echo "")
  for ns in $namespaces; do
    $kubectl delete couchbasecluster.couchbase.com/$ns --ignore-not-found -n $ns || emp_output
    $kubectl delete storageclass.storage.k8s.io/couchbase-sc secret/cb-auth \
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
  services="ldap"
  for service in $services; do
    dynamicgkefolder="$service/overlays/gke/dynamic-pd"
    cp -r $service/overlays/eks/dynamic-ebs $dynamicgkefolder
    cat $dynamicgkefolder/storageclasses.yaml \
      | $sed -s "s@kubernetes.io/aws-ebs@kubernetes.io/gce-pd@g" \
      | $sed '/zones/d' | $sed '/encrypted/d' > tmpfile \
      && mv tmpfile $dynamicgkefolder/storageclasses.yaml \
      || emp_output
  done
  #Config
  cat config/base/kustomization.yaml \
    | $sed '/- cluster-role-bindings.yaml/d' \
    | $sed '/^resources:/a \ \ - cluster-role-bindings.yaml' > tmpfile \
    && mv tmpfile config/base/kustomization.yaml \
    || emp_output
}

create_dynamic_azure() {
  services="ldap"
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
  done
}

create_efs_aws() {
  services="ldap"
  for service in $services; do
    efseksyamls="$service/overlays/eks/efs"
    mkdir -p $service/overlays/eks/efs \
      && cp -r $service/overlays/eks/dynamic-ebs/* \
      $service/overlays/eks/efs
    rm -rf $efseksyamls/storageclasses.yaml \
      || emp_output
    cat $efseksyamls/kustomization.yaml \
        | $sed '/- storageclasses.yaml/d' > tmpfile \
        && mv tmpfile $efseksyamls/kustomization.yaml \
        || emp_output
    cat $efseksyamls/statefulsets.yaml \
      | $sed -n '/template/q;p' \
      | $sed '/storageClassName/d' \
      | $sed -s "s@ReadWriteOnce@ReadWriteMany@g" \
      | $sed '/^\   \ - metadata:/a \       \ annotations:' \
      | $sed '/^\       \ annotations:/a \         \ volume.beta.kubernetes.io/storage-class: "aws-efs"' > tmpfile \
      && mv tmpfile $efseksyamls/statefulsets.yaml \
      || emp_output
  done
}

create_local_minikube() {
  services="ldap"
  for service in $services; do
    localminikubefolder="$service/overlays/minikube"
    mkdir -p $localminikubefolder \
      && cp -r $service/overlays/microk8s/local-storage "$_"
  done
}

create_local_azure() {
  services="ldap"
  for service in $services; do
    localazurefolder="$service/overlays/azure"
    mkdir -p $localazurefolder \
      && cp -r $service/overlays/gke/local-storage "$_"
  done
  cat config/base/kustomization.yaml \
    | $sed '/- cluster-role-bindings.yaml/d' > tmpfile \
    && mv tmpfile config/base/kustomization.yaml
}

create_static_gke() {
  services="ldap"
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
  services="ldap"
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

deploy_cb_cluster() {
  if [ -f couchbase-autonomous-operator-kubernetes_*.tar.gz ];then
    if [[ $choiceDeploy -eq 4 ]]; then
      cat couchbase/storageclasses.yaml \
        | $sed -s "s@kubernetes.io/aws-ebs@kubernetes.io/gce-pd@g" \
        | $sed -s "s@io1@pd-ssd@g" \
        | $sed '/encrypted:/d' > tmpfile \
        && mv tmpfile couchbase/storageclasses.yaml \
        || emp_output
    fi
    delete_cb
    echo "Installing Couchbase. Please follow the prompts.."
    tar xvzf couchbase-autonomous-operator-kubernetes_*.tar.gz --overwrite \
      || emp_output
    cbinstalldir=$(echo couchbase-autonomous-operator-kubernetes_*/)
    $kubectl create namespace $namespace || emp_output
    wget https://github.com/OpenVPN/easy-rsa/archive/master.zip -O easyrsa.zip
    unzip easyrsa.zip
    mv easy-rsa-master/ easy-rsa
    #git clone http://github.com/OpenVPN/easy-rsa
    easyrsa=easy-rsa/easyrsa3
    $easyrsa/easyrsa init-pki
    $easyrsa/easyrsa build-ca
    subject_alt_name="DNS:*.$clustername.$namespace.svc,DNS:*.$namespace.svc,DNS:*.$clustername.$CB_FQDN"
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
	if [[ $multiCluster == "Y" || $multiCluster == "y" ]]; then
	  echo "Setup XDCR between the running gluu couchbase cluster and this one"
      read -rp "Press enter  when XDCR is ready?                               "
    fi
  else
    echo "Error: Couchbase package not found."
    echo "Please download the couchbase kubernetes package and place it inside
      the same directory containing the create.sh script.
      https://www.couchbase.com/downloads"
    exit 1
  fi

}

replace_all() {
  $sed "s/\<PERSISTENCETYPE\>/$PERSISTENCE_TYPE/" \
    | $sed "s/\<LDAPMAPPING\>/$LDAP_MAPPING/" \
    | $sed -s "s@LDAPVOLUMEID@$LDAP_VOLUMEID@g" \
    | $sed -s "s@STORAGELDAP@$STORAGE_LDAP@g" \
    | $sed -s "s@LDAPDISKURI@$LDAP_DISKURI@g" \
    | $sed -s "s@STORAGESHAREDSHIB@$STORAGE_SHAREDSHIB@g" \
    | $sed -s "s@STORAGECASA@$STORAGE_CASA@g" \
    | $sed -s "s@HOME_DIR@$HOME_DIR@g" \
    | $sed "s/\<COUCHBASEURL\>/$COUCHBASE_URL/" \
    | $sed "s/\<CBUSER\>/$CB_USER/" \
    | $sed "s/\<FQDN\>/$FQDN/" \
    | $sed "s#ACCOUNT#$ACCOUNT#g" \
    | $sed "s/\<GLUUCACHETYPE\>/$GLUU_CACHE_TYPE/" \
    | $sed -s "s@VOLUMETYPE@$VOLUME_TYPE@g" \
    | $sed -s "s@FILESYSTEMID@$fileSystemID@g" \
    | $sed -s "s@AWSREGION@$awsRegion@g" \
    | $sed -s "s@EFSDNSNAME@$efsDNS@g" \
    | $sed -s "s@NFSIP@$NFS_IP@g" 
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
      "STORAGE_LDAP" ) STORAGE_LDAP="$2"  ;;
      "STORAGE_SHAREDSHIB" ) STORAGE_SHAREDSHIB="$2"  ;;
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
      "CB_FQDN" ) CB_FQDN="$2" ;;
      "REPLICA_OXAUTH" ) REPLICA_OXAUTH="$2" ;;
      "REPLICA_OXTRUST" ) REPLICA_OXTRUST="$2" ;;
      "REPLICA_LDAP" ) REPLICA_LDAP="$2" ;;
      "REPLICA_SHIB" ) REPLICA_SHIB="$2" ;;
      "REPLICA_PASSPORT" ) REPLICA_PASSPORT="$2" ;;
      "REPLICA_OXD" ) REPLICA_OXD="$2" ;;
      "REPLICA_CASA" ) REPLICA_CASA="$2" ;;
      "REPLICA_RADIUS" ) REPLICA_RADIUS="$2" ;;
      "STORAGE_CASA" ) STORAGE_CASA="$2" ;;
      "ZONE" ) ZONE="$2" ;;
    esac
  fi
}

check_k8version() {
  kustomize="$kubectl kustomize"
  linux_flavor=$(cat /etc/*-release) || emp_output
  if [[ $linux_flavor =~ "CentOS" ]] || [[ $linux_flavor =~ "Amazon Linux" ]]; then
    yum update -y || emp_output
    yum install epel-release -y
    yum install jq -y
    yum install java-1.8.0-openjdk-devel -y
    yum install bind-utils -y
  elif [[ $linux_flavor =~ "Ubuntu" ]]; then
    apt-get update -y
    apt-get install jq -y
    apt-get install openjdk-8-jdk -y
    apt-get install dnsutils -y
  else
    echo "Please install the follwing packages before you continue"
    echo "jq, openjdk 8, unzip, bc, and wget."
    echo "Exit immediatly if these packages are not installed. Otherwise, setup will continue"
    sleep 10
  fi
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
  curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases \
  | grep browser_download \
  | grep $opsys \
  | cut -d '"' -f 4 \
  | grep /kustomize/v \
  | sort | tail -n 1 \
  | xargs curl -O -L
  tar xzf ./kustomize_v*_${opsys}_amd64.tar.gz
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
    read -rp "Please input the hosts external IP Address:                      " HOST_IP
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
  read -rp "Is this the correct external IP Address: ${HOST_IP} [Y/n]?         " cont
  case "$cont" in
    y|Y)
      return 0
    ;;
    n|N)
      read -rp "Please input the hosts external IP Address:                    " HOST_IP
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
    if [[ $installCB != "n" ]] && [[ $installCB != "N" ]]; then
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
  echo "|---------------------------------------------------------------- -|"
  echo "|                     Local Deployments                            |"
  echo "|---------------------------------------------------------------- -|"
  echo "| [1]  Microk8s [default]                                          |"
  echo "| [2]  Minikube                                                    |"
  echo "|---------------------------------------------------------------- -|"
  echo "|                     Cloud Deployments                            |"
  echo "|----------------------------------------------------------------- |"
  echo "| [3] Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)|"
  echo "| [4] Google Cloud Engine - Google Kubernetes Engine (GKE)         |"
  echo "| [5] Microsoft Azure (AKS)                                        |"
  echo "|------------------------------------------------------------------|"
  read -rp "Deploy using?                                                      " choiceDeploy
  echo "|------------------------------------------------------------------|"
  echo "|                     Persistence layer                            |"
  echo "|------------------------------------------------------------------|"
  echo "| [0] WrenDS [default]                                             |"
  echo "| [1] Couchbase [Testing Phase]                                    |"
  echo "| [2] Hybrid(WrenDS + Couchbase)[Testing Phase]                    |"
  echo "|------------------------------------------------------------------|"
  read -rp "Persistence layer?                                                 " choicePersistence
  case "$choicePersistence" in
    1 ) PERSISTENCE_TYPE="couchbase"  ;;
    2 ) PERSISTENCE_TYPE="hybrid"  ;;
    * ) PERSISTENCE_TYPE="ldap"  ;;
  esac
  echo "|------------------------------------------------------------------|"
  echo "|            Is this a multi-cloud/region setup[N] ?[Y/N]          |"
  echo "|------------------------------------------------------------------|"
  echo "|                            Notes                                 |"
  echo "|------------------------------------------------------------------|"
  echo "|- If you are planning for a multi-cloud/region setup and this     |"
  echo "|  is the first cluster answer N or leave blank. You will answer Y |"
  echo "|  for the second and more cluster setup                           |"
  echo "|------------------------------------------------------------------|"
  read -rp "Is this a multi-cloud/region setup[N]                              " multiCluster
  if [[ $choicePersistence -ne 1 ]]; then
    echo "|------------------------------------------------------------------|"
    echo "|                     Local Deployments                            |"
    echo "|------------------------------------------------------------------|"
    echo "| [1]  Microk8s | LDAP volumes on host                             |"
    echo "| [2]  Minikube | LDAP volumes on host                             |"
    echo "|------------------------------------------------------------------|"
    echo "|                     Cloud Deployments                            |"
    echo "|------------------------------------------------------------------|"
    echo "|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)     |"
    echo "|                    MultiAZ - Supported                           |"
    echo "|------------------------------------------------------------------|"
    echo "| [6]  EKS      | LDAP volumes on host                             |"
    echo "| [7]  EKS      | LDAP EBS volumes dynamically provisioned         |"
    echo "| [8]  EKS      | LDAP EBS volumes statically provisioned          |"
    echo "| [9]  EKS      | LDAP EFS volume                                  |"
    echo "|------------------------------------------------------------------|"
    echo "|Google Cloud Engine - Google Kubernetes Engine                    |"
    echo "|------------------------------------------------------------------|"
    echo "| [11]  GKE     | LDAP volumes on host                             |"
    echo "| [12]  GKE     | LDAP Persistent Disk  dynamically provisioned    |"
    echo "| [13]  GKE     | LDAP Persistent Disk  statically provisioned     |"
    echo "|------------------------------------------------------------------|"
    echo "|Microsoft Azure                                                   |"
    echo "|------------------------------------------------------------------|"
    echo "| [16] Azure    | LDAP volumes on host                             |"
    echo "| [17] Azure    | LDAP Persistent Disk  dynamically provisioned    |"
    echo "| [18] Azure    | LDAP Persistent Disk  statically provisioned     |"
    echo "|------------------------------------------------------------------|"
    echo "|                            Notes                                 |"
    echo "|------------------------------------------------------------------|"
    echo "|- Any other option will default to choice 1                       |"
    echo "|------------------------------------------------------------------|"
    read -rp "What type of deployment?                                         " choiceLDAPDeploy
    if [[ $choiceLDAPDeploy -eq 9 ]];then
      read -rp "EFS created [Y]" efsNote
      read -rp "EFS must be inside the same region as the EKS cluster [Y]" efsNote
      read -rp "VPC of EKS and EFS are the same [Y]" efsNote
      read -rp "Security group of EFS allows all connections from EKS nodes [Y]" efsNote
      if [[ efsNote == "n" ]] || [[ efsNote == "N" ]]; then
        exit 1
      fi
    fi
  fi
  echo "|------------------------------------------------------------------|"
  echo "|                     Cache layer                                  |"
  echo "|------------------------------------------------------------------|"
  echo "| [0] NATIVE_PERSISTENCE [default]                                 |"
  echo "| [1] IN_MEMORY                                                    |"
  echo "| [2] REDIS                                                        |"
  echo "|------------------------------------------------------------------|"
  read -rp "Cache layer?                                                       " choiceCache
  case "$choiceCache" in
    1 ) GLUU_CACHE_TYPE="IN_MEMORY"  ;;
    2 ) GLUU_CACHE_TYPE="REDIS" ;;
    * ) GLUU_CACHE_TYPE="NATIVE_PERSISTENCE"  ;;
  esac  
  LDAP_MAPPING="default"
  GLUU_CACHE_TYPE="'${GLUU_CACHE_TYPE}'"
  #COUCHBASE
  COUCHBASE_URL="couchbase"
  CB_USER="admin"
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
    read -rp "Persistence type?                                                " choiceHybrid
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
  if [[ $choiceDeploy -eq 3 ]]; then
    echo "|-----------------------------------------------------------------|"
    echo "|                     AWS Loadbalancer type                       |"
    echo "|-----------------------------------------------------------------|"
    echo "| [0] Classic Load Balancer (CLB) [default]                       |"
    echo "| [1] Network Load Balancer (NLB - Alpha) -- Static IP            |"
    echo "|-----------------------------------------------------------------|"
    read -rp "Loadbalancer type ?                                              " lbChoicenumber
    case "$lbChoicenumber" in
      0 ) lbChoice="clb"  ;;
      1 ) lbChoice="nlb"  ;;
      * ) lbChoice="clb"  ;;
    esac
    read -rp "Are you terminating SSL traffic at LB and using certificate from 
       AWS [N][Y/N]   : " UseARN
    if [[ $UseARN == "Y" || $UseARN == "y" ]]; then
      read -rp 'Enter aws-load-balancer-ssl-cert arn quoted \
        ("arn:aws:acm:us-west-2:XXXXXXXX:certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX"): ' ARN
    fi
  fi
  if [[ $choicePersistence -ge 1 ]]; then
    COUCHBASE_URL=""
    echo "For the following prompt  if placed [N] the couchbase 
      is assumed to be installed or remotely provisioned"
    read -rp "Install Couchbase[Y][Y/N] ?                                      " installCB
    if [[ $installCB != "n" ]] && [[ $installCB != "N" ]]; then
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
        read -rp "Please enter a couchbase domain for SAN. \
          " CB_FQDN && set_default "$CB_FQDN" "cb.gluu.org" "CB_FQDN"
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
  read -rp "Deploy Shibboleth SAML IDP[N]?[Y/N]                                " choiceShibboleth
  read -rp "[Testing Phase] Deploy Casa[N]?[Y/N]                               " choiceCasa
  if [[ $choiceShibboleth == "y" || $choiceShibboleth == "Y" ]]; then
    if [[ $choiceDeploy  -eq 3 ]];then
      echo "|-----------------------------------------------------------------|"
      echo "|                     Shared Shibboleth Volume                    |"
      echo "|-----------------------------------------------------------------|"
      echo "| [0] local storage [default]                                     |"
      echo "| [1] EFS - Required for production                               |"
      echo "|-----------------------------------------------------------------|"
      read -rp "Type of Shibboleth volume                                      " choiceVolumeShibboleth
      if [[ choiceVolumeShibboleth -eq 1 ]]; then
        read -rp "EFS created [Y]" efsNote
        read -rp "EFS must be inside the same region as the EKS cluster [Y]" efsNote
        read -rp "VPC of EKS and EFS are the same [Y]" efsNote
        read -rp "Security group of EFS allows all connections from EKS nodes [Y]" efsNote
        read -rp "Enter FileSystemID (fs-xxx):                                     " fileSystemID
        read -rp "Enter AWS region (us-west-2):                                    " awsRegion
        read -rp "Enter EFS dns name (fs-xxx.us-west-2.amazonaws.com):             " efsDNS
        if [[ efsNote == "n" ]] || [[ efsNote == "N" ]]; then
          exit 1
        fi
      fi
    fi
  fi
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    choiceOXD="Y"
  #else
  #  read -rp "Deploy OXD-Server[N]?[Y/N]                                       " choiceOXD
  fi
  if [[ $choiceOXD == "Y" || $choiceOXD == "y" ]]; then
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
       | env LC_CTYPE=C tr -dc 'a-zA-Z0-9A-Za-z0-9!#$' \
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
  google_azure_zone=""
  #output the zones out to the user
  zones=$($kubectl get nodes -o json | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]')
  arrzones=($zones)
  numberofzones="${#arrzones[@]}"
  echo "There are $numberofzones nodes deployed in these zones:"
  zones=$(echo "${zones[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' ' | tr -d '\"')
  echo $zones
  arrzones=($zones)
  numberofzones="${#arrzones[@]}"
  num=$numberofzones
  if [[ $choiceLDAPDeploy -eq 7 ]] \
    || [[ $choiceLDAPDeploy -eq 12 ]] \
    || [[ $choiceLDAPDeploy -eq 17 ]]; then
    if [[ -f ldap/$yaml_folder/storageclasses_copy.yaml ]]; then
      cp ldap/$yaml_folder/storageclasses_copy.yaml ldap/$yaml_folder/storageclasses.yaml
    fi
    cp ldap/$yaml_folder/storageclasses.yaml ldap/$yaml_folder/storageclasses_copy.yaml
  fi
  while true;do
    num=$(($num - 1))
    google_azure_zone="${arrzones[$num]}"
    singlezone="${arrzones[$num]}"
    if [[ $choiceLDAPDeploy -eq 7 ]] \
      || [[ $choiceLDAPDeploy -eq 12 ]] \
      || [[ $choiceLDAPDeploy -eq 17 ]]; then	
      printf  "\n    - $singlezone" \
        >> ldap/$yaml_folder/storageclasses.yaml
    fi
    if [[ $num -eq 0 ]];then
      break
    fi
  done
}

prompt_replicas() {
  read -rp "Number of oxAuth replicas [1]:                                     " REPLICA_OXAUTH \
    && set_default "$REPLICA_OXAUTH" "1" "REPLICA_OXAUTH"

  read -rp "Number of oxTrust replicas [1]:                                    " REPLICA_OXTRUST \
    && set_default "$REPLICA_OXTRUST" "1" "REPLICA_OXTRUST"

  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Number of LDAP replicas [1]:                                     " REPLICA_LDAP \
      && set_default "$REPLICA_LDAP" "1" "REPLICA_LDAP"
  fi
  
  if [[ $choiceShibboleth == "y" || $choiceShibboleth == "Y" ]]; then
    # oxShibboleth
    read -rp "Number of oxShibboleth replicas [1]:                             " REPLICA_SHIB \
      && set_default "$REPLICA_SHIB" "1" "REPLICA_SHIB"
  fi

  if [[ $choicePassport == "y" || $choicePassport == "Y" ]]; then
    # oxPassport
    read -rp "Number of oxPassport replicas [1]:                               " REPLICA_PASSPORT \
      && set_default "$REPLICA_PASSPORT" "1" "REPLICA_PASSPORT"
  fi
    # OXD-Server
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    read -rp "Number of oxd-server replicas [1]:                               " REPLICA_OXD \
      && set_default "$REPLICA_OXD" "1" "REPLICA_OXD"
  fi
    # Casa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    read -rp "Number of casa replicas [1]:                                     " REPLICA_CASA \
      && set_default "$REPLICA_CASA" "1" "REPLICA_CASA"
  fi  
  # Radius
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    read -rp "Number of Radius replicas [1]:                                   " REPLICA_RADIUS \
      && set_default "$REPLICA_RADIUS" "1" "REPLICA_RADIUS"
  fi
}

prompt_storage() {
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Size of ldap volume storage [4Gi]:                               " STORAGE_LDAP \
      && set_default "$STORAGE_LDAP" "4Gi" "STORAGE_LDAP"
  fi
  if [[ $choiceShibboleth == "y" || $choiceShibboleth == "Y" ]]; then
    read -p "Size of Shared-Shib volume storage [4Gi]:                         " STORAGE_SHAREDSHIB \
      && set_default "$STORAGE_SHAREDSHIB" "4Gi" "STORAGE_SHAREDSHIB"
  fi
  STORAGE_CASA=$STORAGE_SHAREDSHIB
      # Casa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    read -p "Size of Casa volume storage [4Gi]:                                " STORAGE_CASA \
      && set_default "$STORAGE_CASA" "4Gi" "STORAGE_CASA"
  fi
}

gke_prompts() {
  read -rp "Please enter valid email for Google Cloud account:                 " ACCOUNT
  read -rp "Please enter valid Zone name used when creating the cluster:[$google_azure_zone]" ZONE \
      && set_default "$ZONE" "$google_azure_zone" "ZONE"
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
  generate_nfs
}

generate_nfs() {
  $kustomize shared-shib/nfs > $output_yamls/nfs.yaml
  STORAGE_NFS=$STORAGE_SHAREDSHIB
}

prompt_volumes_identitfier() {
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Please enter $static_volume_prompt for LDAP:                     " LDAP_VOLUMEID
  fi  
}

prompt_disk_uris() {
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    read -rp "Please enter the disk uri for LDAP:                              " LDAP_DISKURI
  fi
}
output_inital_yamls() {
  if [[ $choiceShibboleth == "y" || $choiceShibboleth == "Y" ]]; then
    if [[ $choiceDeploy -eq 3 ]] \
      && [[ $choiceVolumeShibboleth -eq 1 ]]; then
      $kustomize shared-shib/efs \
        | replace_all  > $output_yamls/shared-shib.yaml
    elif [[ $choiceDeploy -eq 4 ]] || [[ $choiceDeploy -eq 5 ]]; then
      $kustomize shared-shib/nfs \
        | replace_all  > $output_yamls/shared-shib.yaml
    else
      $kustomize shared-shib/localstorage \
        | replace_all  > $output_yamls/shared-shib.yaml
    fi
  fi
  # Config
  $kustomize config/base | replace_all > $output_yamls/config.yaml
  # WrenDS
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    $kustomize ldap/$yaml_folder | replace_all > $output_yamls/ldap.yaml
  fi
  # Persistence
  $kustomize persistence/base | replace_all > $output_yamls/persistence.yaml
  # oxAuth
  $kustomize oxauth/base | replace_all > $output_yamls/oxauth.yaml
  # oxTrust
  $kustomize oxtrust/base | replace_all > $output_yamls/oxtrust.yaml
  if [[ $choiceShibboleth == "y" || $choiceShibboleth == "Y" ]]; then
    # oxShibboleth
    $kustomize oxshibboleth/base \
      | replace_all  > $output_yamls/oxshibboleth.yaml
  fi

  if [[ $choicePassport == "y" || $choicePassport == "Y" ]]; then
    # oxPassport
    $kustomize oxpassport/base \
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
    $kustomize oxd-server/base | replace_all > $output_yamls/oxd-server.yaml
  fi
    # Casa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    $kustomize casa/base | replace_all > $output_yamls/casa.yaml
  fi  
  # Radius
  if [[ $choiceRadius == "y" || $choiceRadius == "Y" ]]; then
    # Radius server
    $kustomize radius/base | replace_all > $output_yamls/radius.yaml
  fi
  if [[ $choiceCache == 2 ]];then
    $kustomize redis/base/ | replace_all > $output_yamls/redis.yaml
  fi 
}

generate_yamls() {
  read -rp "Are you using a globally resolvable FQDN [N] [Y/N]:                " FQDN_CHOICE
  if [[ $FQDN_CHOICE == "y" || $FQDN_CHOICE == "Y" ]]; then
  echo "You can mount your FQDN certification and key by placing them inside 
    ingress.crt and ingress.key respectivley "
    if [ ! -f ingress.crt ] \
      || [ ! -s ingress.crt ] \
      || [ ! -f ingress.key ] \
      || [ ! -s ingress.key ]; then
      echo "Check that  ingress.crt and ingress.key are not empty 
        and contain the right information for your FQDN. "
    fi
  fi
  if [[ $choiceDeploy -eq 2 ]]; then
    mkdir gluuminikubeyamls || emp_output
    output_yamls=gluuminikubeyamls
  elif [[ $choiceDeploy -eq 3 ]]; then
    mkdir gluueksyamls || emp_output
    output_yamls=gluueksyamls
  elif [[ $choiceDeploy -eq 4 ]]; then
    mkdir gluugkeyamls || emp_output
    output_yamls=gluugkeyamls
  elif [[ $choiceDeploy -eq 5 ]]; then
    mkdir gluuaksyamls || emp_output
    output_yamls=gluuaksyamls
  else
    mkdir gluumicrok8yamls || emp_output
    output_yamls=gluumicrok8yamls
  fi
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    if [[ $choiceLDAPDeploy -eq 2 ]]; then
      create_local_minikube
      yaml_folder=$local_minikube_folder

    elif [[ $choiceLDAPDeploy -eq 6 ]]; then
      yaml_folder=$local_eks_folder

    elif [[ $choiceLDAPDeploy -eq 7 ]]; then
      echo "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html"
      echo "Follow the doc above to help you choose 
        which volume type to use.Options are [gp2,io1,st1,and sc1]"
      read -rp "Please enter the volume type for EBS[io1]:                       " VOLUME_TYPE \
        && set_default "$VOLUME_TYPE" "io1" "VOLUME_TYPE"
      yaml_folder=$dynamic_eks_folder
      prompt_zones

    elif [[ $choiceLDAPDeploy -eq 8 ]]; then
      yaml_folder=$static_eks_folder
      echo "Zones of your volumes are required to match the deployments to the volume zone"
      prompt_zones
      static_volume_prompt="EBS Volume ID"
      prompt_volumes_identitfier

    elif [[ $choiceLDAPDeploy -eq 9 ]]; then
      create_efs_aws
      yaml_folder=$efs_eks_folder
      read -rp "Enter FileSystemID (fs-xxx):                                     " fileSystemID
      read -rp "Enter AWS region (us-west-2):                                    " awsRegion
      read -rp "Enter EFS dns name (fs-xxx.us-west-2.amazonaws.com):             " efsDNS

    elif [[ $choiceLDAPDeploy -eq 11 ]]; then
      yaml_folder=$local_gke_folder
      prompt_zones
      gke_prompts

    elif [[ $choiceLDAPDeploy -eq 12 ]]; then
      echo "Please enter the volume type for the persistent disk."
      read -rp "Options are (pd-standard, pd-ssd). [pd-ssd] :                    " VOLUME_TYPE \
        && set_default "$VOLUME_TYPE" "pd-ssd" "VOLUME_TYPE"
      create_dynamic_gke
      yaml_folder=$dynamic_gke_folder
      prompt_zones
      gke_prompts

    elif [[ $choiceLDAPDeploy -eq 13 ]]; then
      create_static_gke
      static_volume_prompt="Persistent Disk Name"
      echo 'Place the name of your persistent disks between two quotes as such 
        "gke-testinggluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd"'
      prompt_volumes_identitfier
      yaml_folder=$static_gke_folder
      prompt_zones
      gke_prompts

    elif [[ $choiceLDAPDeploy -eq 16 ]]; then
      create_local_azure
      yaml_folder=$local_azure_folder
      generate_nfs

    elif [[ $choiceLDAPDeploy -eq 17 ]]; then
      echo "https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-types"
      echo "Please enter the volume type for the persistent disk. Example:UltraSSD_LRS,"
      echo "Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')"
      prompt_zones
      read -rp "[Premium_LRS] :                                                  " VOLUME_TYPE \
        && set_default "$VOLUME_TYPE" "Premium_LRS" "VOLUME_TYPE"
      echo "Outputing available zones used : "
      $kubectl get nodes -o json \
        | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]'
      read -rp "Please enter a valid Zone name used this might be set to 0:[$google_azure_zone]" ZONE \
        && set_default "$ZONE" "$google_azure_zone" "ZONE"
      create_dynamic_azure
      yaml_folder=$dynamic_azure_folder
      generate_nfs

    elif [[ $choiceLDAPDeploy -eq 18 ]]; then
      echo "https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-types"
      echo "Please enter the volume type for the persistent disk. Example:UltraSSD_LRS,"
      echo "Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')"
      prompt_zones
      read -rp "[Premium_LRS] :                                                  " VOLUME_TYPE \
        && set_default "$VOLUME_TYPE" "Premium_LRS" "VOLUME_TYPE"
      echo "Outputing available zones used : "
      $kubectl get nodes -o json | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]'
      read -rp "Please enter a valid Zone name used this might be set to 0:[$google_azure_zone]" ZONE \
        && set_default "$ZONE" "$google_azure_zone" "ZONE"
      create_static_azure
      static_volume_prompt="Persistent Disk Name"
      prompt_volumes_identitfier
      prompt_disk_uris
      yaml_folder=$static_azure_folder
      generate_nfs

    else
      mkdir localmicrok8syamls || emp_output
      yaml_folder=$local_microk8s_folder
    fi
  fi
  # Get prams for the yamls
  prompt_storage
  prompt_replicas
  if [[ $FQDN_CHOICE == "y" ]] \
    || [[ $FQDN_CHOICE == "Y" ]]; then
    services="casa oxauth oxd-server oxpassport radius oxshibboleth oxtrust"
    for service in $services; do
      # Incase user has used updatelbip and switched kustmization source file
      cat $service/base/kustomization.yaml \
        | $sed -s "s@deployments-patch.yaml@deployments.yaml@g" \
        | $sed -s "s@statefulsets-patch.yaml@statefulsets.yaml@g" > tmpfile \
        && mv tmpfile $service/base/kustomization.yaml \
        || emp_output
    done
  else
    services="casa oxauth oxd-server oxpassport radius oxshibboleth oxtrust"
    for service in $services; do
      cat $service/base/kustomization.yaml \
        | $sed -s "s@deployments.yaml@deployments-patch.yaml@g" \
        | $sed -s "s@statefulsets.yaml@statefulsets-patch.yaml@g" > tmpfile \
        && mv tmpfile $service/base/kustomization.yaml \
        || emp_output
    done
  fi
  output_inital_yamls
  if [[ $FQDN_CHOICE == "y" ]] \
    || [[ $FQDN_CHOICE == "Y" ]]; then
    services="casa oxauth oxd-server oxpassport radius oxshibboleth oxtrust"
    for service in $services; do
      # Remove hostAliases object from yamls
      cat $output_yamls/$service.yaml \
        | $sed '/LB_ADDR: LBADDR/d' \
        | $sed '/hostAliases:/d' \
        | $sed '/- hostnames:/d' \
        | $sed "/$FQDN/d" \
        | $sed '/- command:/,/entrypoint.sh/d' \
        | $sed -s "s@  envFrom@- envFrom@g" \
        | $sed '/ip: NGINX_IP/d'> tmpfile \
        && mv tmpfile $output_yamls/$service.yaml \
        || emp_output
    done
    # Create dummy updatelbip
    $kubectl create configmap updatelbip --from-literal=demo=empty || emp_output
  else
    services="casa oxauth oxd-server oxpassport radius oxshibboleth oxtrust"
    for service in $services; do
      if [[ choiceDeploy -eq 4 ]] || [[ choiceDeploy -eq 5 ]]; then
        cat $output_yamls/$service.yaml \
          | $sed '/LB_ADDR: LBADDR/d' \
          | $sed '/- command:/,/entrypoint.sh/d' \
          | $sed -s "s@  envFrom@- envFrom@g" > tmpfile \
          && mv tmpfile $output_yamls/$service.yaml \
          || emp_output
      fi
    done
    $kustomize update-lb-ip/base > $output_yamls/updatelbip.yaml
  fi
  echo " all yamls have been generated in $output_yamls folder"
}

deploy_nginx() {
  cp -rf nginx $output_yamls
  if [[ $choiceDeploy -eq 1 ]]; then
    # If microk8s ingress
    microk8s.enable ingress dns || emp_output
  fi
  if [[ $choiceDeploy -eq 2 ]]; then
    # If minikube ingress
    minikube addons enable ingress || emp_output
  fi
  # Nginx
  $kubectl apply -f $output_yamls/nginx/mandatory.yaml
  if [[ $choiceDeploy -eq 3 ]]; then
    lbhostname=""
    if [[ $lbChoice == "nlb" ]];then
      $kubectl apply -f $output_yamls/nginx/nlb-service.yaml
      while true; do
        lbhostname=$($kubectl -n ingress-nginx get svc ingress-nginx \
          --output jsonpath='{.status.loadBalancer.ingress[0].hostname}' || echo "")
        hostname="'${lbhostname}'" || emp_output 
        ip_static=$(dig +short "$lbhostname" || echo "")
        echo "Waiting for LB to recieve an ip assignment from AWS"
        if [[ $ip_static ]]; then
          break
        fi
        sleep 20
      done
    else
      if [[ $UseARN == "Y" || $UseARN == "y" ]]; then
        cat $output_yamls/nginx/service-l7.yaml \
          | $sed -s "s@ARN@$ARN@g" > tmpfile \
          && mv tmpfile $output_yamls/nginx/service-l7.yaml \
          || emp_output
        $kubectl apply -f $output_yamls/nginx/service-l7.yaml
        $kubectl apply -f $output_yamls/nginx/patch-configmap-l7.yaml
      else
        $kubectl apply -f $output_yamls/nginx/service-l4.yaml 
        $kubectl apply -f $output_yamls/nginx/patch-configmap-l4.yaml
      fi
    fi
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

  if [[ $choiceDeploy -eq 4 ]] || [[ $choiceDeploy -eq 5 ]]; then
    $kubectl apply -f $output_yamls/nginx/cloud-generic.yaml
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
  cat $output_yamls/nginx/nginx.yaml | $sed "s/\<FQDN\>/$FQDN/" > tmpfile \
    && mv tmpfile $output_yamls/nginx/nginx.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/nginx/nginx.yaml
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
  
  echo "[I] Deploying LDAP.Please wait.."
  sleep 40
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
  if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
    $kubectl scale statefulset opendj --replicas=$REPLICA_LDAP
    is_pod_ready "app=opendj"
  fi

}

deploy_shared_shib() {
  if [[ $choiceDeploy -eq 4 ]] || [[ $choiceDeploy -eq 5 ]]; then
    $kubectl apply -f shared-shib/nfs/services.yaml
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
      | replace_all > tmpfile \
      && mv tmpfile $output_yamls/nfs.yaml \
      || emp_output
    $kubectl apply -f $output_yamls/nfs.yaml
    is_pod_ready "app=nfs-server"
    $kubectl exec -ti $($kubectl get pods -l app=nfs-server \
      -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}') \
      -- mkdir -p /exports/opt/shared-shibboleth-idp
    $kubectl exec -ti $($kubectl get pods -l app=nfs-server \
      -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}') \
      -- mkdir -p /exports/data/casa
  elif [[ $choiceDeploy -eq 3 ]] \
    && [[ $choiceVolumeShibboleth -eq 1 ]]; then
    cat $output_yamls/shared-shib.yaml \
      | replace_all > tmpfile \
      && mv tmpfile $output_yamls/shared-shib.yaml \
      || emp_output
    $kubectl apply -f $output_yamls/shared-shib.yaml
    is_pod_ready "app=efs-provisioner"
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
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxauth.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxauth.yaml
  is_pod_ready "app=oxauth"
  $kubectl scale deployment oxauth --replicas=$REPLICA_OXAUTH
  is_pod_ready "app=oxauth"
}

deploy_oxd() {
  # OXD server
  $kubectl create secret generic oxdkeystorecm --from-file=oxd-server.keystore
  cat $output_yamls/oxd-server.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxd-server.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxd-server.yaml
  is_pod_ready "app=oxd-server"
  $kubectl scale deployment oxd-server --replicas=$REPLICA_OXD
  is_pod_ready "app=oxd-server"

}

deploy_casa() {
  # Casa
  cat $output_yamls/casa.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/casa.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/casa.yaml
  is_pod_ready "app=casa"
  #Wait some time for casa.json to be created in casa app correctly
  sleep 15
  podname_template='{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'
  casapodname=$($kubectl get pod -l=app=casa -o template --template="$podname_template" \
    || echo "")
  $kubectl cp $casapodname:etc/gluu/conf/casa.json ./casa.json
  rm casacm.yaml
  $kubectl create configmap casacm --from-file=casa.json -o yaml --dry-run > casacm.yaml
  $kubectl apply -f casacm.yaml || emp_output
  rm casacm.yaml
  # restart oxauth 
  $kubectl scale deployment oxauth --replicas=0
  sleep 5
  $kubectl scale deployment oxauth --replicas=$REPLICA_OXAUTH
}

deploy_oxtrust() {
  cat $output_yamls/oxtrust.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxtrust.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxtrust.yaml || emp_output
  is_pod_ready "app=oxtrust"
  $kubectl scale statefulset oxtrust --replicas=$REPLICA_OXTRUST
}

deploy_oxshibboleth() {
  cat $output_yamls/oxshibboleth.yaml \
    | $sed -s "s@NGINX_IP@$ip@g"  \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxshibboleth.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxshibboleth.yaml || emp_output
  is_pod_ready "app=oxshibboleth"
  $kubectl scale statefulset oxshibboleth --replicas=$REPLICA_SHIB
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
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxpassport.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxpassport.yaml || emp_output
  is_pod_ready "app=oxpassport"
  $kubectl scale deployment oxpassport --replicas=$REPLICA_PASSPORT
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
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/radius.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/radius.yaml || emp_output
  is_pod_ready "app=radius"
  $kubectl scale deployment radius --replicas=$REPLICA_RADIUS

}

deploy_cr_rotate() {
  $kubectl apply -f  $output_yamls/cr-rotate.yaml || emp_output
}

deploy() {
  ls $output_yamls || true
  read -rp "Deploy the generated yamls? [Y][Y/n]                                " choiceContDeploy
  case "$choiceContDeploy" in
    y|Y ) ;;
    n|N ) exit 1 ;;
    * )   ;;
  esac
  prompt_cb
  deploy_shared_shib
  $kubectl create secret generic cb-pass --from-file=couchbase_password || true
  $kubectl create secret generic cb-crt --from-file=couchbase.crt || true
  if [[ $multiCluster != "Y" && $multiCluster != "y" ]]; then
    deploy_config
  fi
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
  if [[ $FQDN_CHOICE != "y" ]] && [[ $FQDN_CHOICE != "Y" ]]; then
    deploy_update_lb_ip
  fi
  deploy_oxauth
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    deploy_oxd
  fi
    # Casa
  if [[ $choiceCasa == "y" || $choiceCasa == "Y" ]]; then
    deploy_casa
  else
    $timeout 10 $kubectl delete pvc -l type=casa --ignore-not-found || emp_output
    $timeout 10 $kubectl delete pv -l type=casa --ignore-not-found || emp_output
  fi
  deploy_oxtrust
  if [[ $choiceShibboleth == "y" || $choiceShibboleth == "Y" ]]; then
    # oxShibboleth
    deploy_oxshibboleth
  fi
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