#!/bin/bash
set -e
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

emp_prompt_vars() {
  read -r NODE_SSH_KEY HOST_EXT_IP VERIFY_EXT_IP DEPLOYMENT_ARCH PERSISTENCE_BACKEND DEPLOY_MULTI_CLUSTER LDAP_VOLUME_TYPE ACCEPT_EFS_NOTES CACHE_TYPE HYBRID_LDAP_HELD_DATA AWS_LB_TYPE USE_ARN ARN_AWS_IAM INSTALL_COUCHBASE VOLUME_TYPE COUCHBASE_NAMESPACE COUCHBASE_CLUSTER_NAME COUCHBASE_FQDN COUCHBASE_URL COUCHBASE_USER ENABLE_CACHE_REFRESH ENABLE_KEY_ROTATE ENABLE_RADIUS ENABLE_OXPASSPORT ENABLE_OXSHIBBOLETH ENABLE_CASA ENABLE_OXTRUST_API ENABLE_OXTRUST_TEST_MODE OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE EFS_FILE_SYSTEM_ID EFS_AWS_REGION EFS_DNS LOAD_PREVIOUS_PARAMS GLUU_FQDN COUNTRY_CODE STATE CITY EMAIL ORG_NAME CONFIRM_PARAMS OXAUTH_REPLICAS OXTRUST_REPLICAS LDAP_REPLICAS OXSHIBBOLETH_REPLICAS OXPASSPORT_REPLICAS OXD_SERVER_REPLICAS CASA_REPLICAS RADIUS_REPLICAS LDAP_STORAGE_SIZE OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE CASA_STORAGE_SIZE GMAIL_ACCOUNT LDAP_STATIC_VOLUME_ID LDAP_STATIC_DISK_URI IS_GLUU_FQDN_REGISTERED DEPLOY_GENERATED_YAMLS <<<$(echo "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "")
}

output_prompt_var_values() {
  prompt_vars="NODE_SSH_KEY HOST_EXT_IP VERIFY_EXT_IP DEPLOYMENT_ARCH PERSISTENCE_BACKEND DEPLOY_MULTI_CLUSTER LDAP_VOLUME_TYPE ACCEPT_EFS_NOTES CACHE_TYPE HYBRID_LDAP_HELD_DATA AWS_LB_TYPE USE_ARN ARN_AWS_IAM INSTALL_COUCHBASE VOLUME_TYPE COUCHBASE_NAMESPACE COUCHBASE_CLUSTER_NAME COUCHBASE_FQDN COUCHBASE_URL COUCHBASE_USER ENABLE_CACHE_REFRESH ENABLE_KEY_ROTATE ENABLE_RADIUS ENABLE_OXPASSPORT ENABLE_OXSHIBBOLETH ENABLE_CASA ENABLE_OXTRUST_API ENABLE_OXTRUST_TEST_MODE OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE EFS_FILE_SYSTEM_ID EFS_AWS_REGION EFS_DNS LOAD_PREVIOUS_PARAMS GLUU_FQDN COUNTRY_CODE STATE CITY EMAIL ORG_NAME CONFIRM_PARAMS OXAUTH_REPLICAS OXTRUST_REPLICAS LDAP_REPLICAS OXSHIBBOLETH_REPLICAS OXPASSPORT_REPLICAS OXD_SERVER_REPLICAS CASA_REPLICAS RADIUS_REPLICAS LDAP_STORAGE_SIZE OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE CASA_STORAGE_SIZE GMAIL_ACCOUNT LDAP_STATIC_VOLUME_ID LDAP_STATIC_DISK_URI IS_GLUU_FQDN_REGISTERED DEPLOY_GENERATED_YAMLS"
  if [ -f installation-variables ] || [ -s installation-variables ]; then
    mv installation-variables previous-installation-variables || emp_output
  fi
  touch installation-variables
  for var in $prompt_vars; do
    if [[ ! ${!var} ]]; then
      read -r $var <<<$(echo '""')
    fi
    echo "$var=${!var}" >> installation-variables
  done
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
  elif [ -d "gluumicrok8yamls" ];then
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
  rm oxd-server.keystore easyrsa_ca_password || emp_output
  if [ -d "gluueksyamls" ] \
    || [ -d "gluugkeyamls" ] \
    || [ -d "gluuaksyamls" ]; then
    if [[ ! "$NODE_SSH_KEY" ]]; then
      read -rp "Please enter the ssh key path to login
      into the nodes created[~/.ssh/id_rsa ]:                 " NODE_SSH_KEY \
       && set_default "$NODE_SSH_KEY" "~/.ssh/id_rsa" "NODE_SSH_KEY"
    fi
    echo "Trying to delete folders created at other nodes."
    ip_template='{{range.items}}{{range.status.addresses}}
      {{if eq .type "ExternalIP"}}{{.address}}{{end}}{{end}} {{end}}'
    node_ips=$($kubectl get nodes -o template --template="$ip_template" \
      || echo "")
    # Loops through the IPs of the nodes and deletes /data
    for node_ip in $node_ips; do
      if [ -d "gluueksyamls" ];then
        ssh -oStrictHostKeyChecking=no -i $NODE_SSH_KEY \
          ec2-user@"$node_ip" sudo rm -rf /data || emp_output
      elif [ -d "gluugkeyamls" ];then
        ssh -oStrictHostKeyChecking=no -i $NODE_SSH_KEY \
          user@"$node_ip" sudo rm -rf /opendj || emp_output
      elif [ -d "gluuaksyamls" ];then
        ssh -oStrictHostKeyChecking=no -i $NODE_SSH_KEY \
          opc@"$node_ip" sudo rm -rf /data || emp_output
      fi
    done
  fi
  rm -rf old$manifestsfolder || emp_output
  mv -f $manifestsfolder old$manifestsfolder || emp_output
  mv ingress.crt previous-ingress.crt || emp_output
  mv ingress.key previous-ingress.key || emp_output
  if [ -f installation-variables ] || [ -s installation-variables ]; then
    mv installation-variables previous-installation-variables || emp_output
  fi
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
  rm -rf easy-rsa pki rm -rf couchbase-autonomous-operator-kubernetes_*/ || emp_output
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
    couchbaseclusterfile="couchbase-cluster.yaml"
    if [[ $DEPLOYMENT_ARCH -eq 4 ]]; then
      cat couchbase/storageclasses.yaml \
        | $sed -s "s@kubernetes.io/aws-ebs@kubernetes.io/gce-pd@g" \
        | $sed '/encrypted:/d' > tmpfile \
        && mv tmpfile couchbase/storageclasses.yaml \
        || emp_output
    elif [[ $DEPLOYMENT_ARCH -eq 1 ]]; then
      couchbaseclusterfile="low-resource-couchbase-cluster.yaml"
      cat couchbase/storageclasses.yaml \
        | $sed -s "s@kubernetes.io/aws-ebs@microk8s.io/hostpath@g" \
        | $sed '/allowVolumeExpansion:/d' \
        | $sed '/parameters:/d' \
        | $sed '/type:/d' \
        | $sed '/encrypted:/d' > tmpfile \
        && mv tmpfile couchbase/storageclasses.yaml \
        || emp_output
    elif [[ $DEPLOYMENT_ARCH -eq 2 ]]; then
      couchbaseclusterfile="low-resource-couchbase-cluster.yaml"
      cat couchbase/storageclasses.yaml \
        | $sed -s "s@kubernetes.io/aws-ebs@k8s.io/minikube-hostpath@g" \
        | $sed '/allowVolumeExpansion:/d' \
        | $sed '/parameters:/d' \
        | $sed '/type:/d' \
        | $sed '/encrypted:/d' > tmpfile \
        && mv tmpfile couchbase/storageclasses.yaml \
        || emp_output
    fi
    delete_cb
    echo "Installing Couchbase. Please follow the prompts.."
    tar xvzf couchbase-autonomous-operator-kubernetes_*.tar.gz || emp_output
    cbinstalldir=$(echo couchbase-autonomous-operator-kubernetes_*/)
    $kubectl create namespace $COUCHBASE_NAMESPACE || emp_output
    wget https://github.com/OpenVPN/easy-rsa/archive/master.zip -O easyrsa.zip
    unzip easyrsa.zip
    mv easy-rsa-master/ easy-rsa
    #git clone http://github.com/OpenVPN/easy-rsa
    easyrsa=easy-rsa/easyrsa3
    $easyrsa/easyrsa init-pki
    if [[ ! "$EASYRSA_COMMON_NAME" ]]; then
      read -rp "Common Name (eg: your user, host, or server name) [CBCA]:" EASYRSA_COMMON_NAME \
        && set_default "$EASYRSA_COMMON_NAME" "CBCA" "EASYRSA_COMMON_NAME"
    fi
    if [[ ! "$EASYRSA_PW" ]]; then
      prompt_password "EASYRSA_PW" "EasyRSA CA"
    fi
    echo "$EASYRSA_PW" > easyrsa_ca_password
    echo "$EASYRSA_PW" >> easyrsa_ca_password
    echo "$EASYRSA_COMMON_NAME" >> easyrsa_ca_password
    $easyrsa/easyrsa build-ca <easyrsa_ca_password
    subject_alt_name="DNS:*.$COUCHBASE_CLUSTER_NAME.$COUCHBASE_NAMESPACE.svc,DNS:*.$COUCHBASE_NAMESPACE.svc,DNS:*.$COUCHBASE_CLUSTER_NAME.$COUCHBASE_FQDN"
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
      --from-file $easyrsa/pkey.key --namespace $COUCHBASE_NAMESPACE
    $kubectl create secret generic couchbase-operator-tls \
      --from-file pki/ca.crt --namespace $COUCHBASE_NAMESPACE || emp_output
    $kubectl create secret generic couchbase-operator-admission \
      --from-file $easyrsa/tls-cert-file \
      --from-file $easyrsa/tls-private-key-file --namespace $COUCHBASE_NAMESPACE \
      || emp_output
    tlscertfilebase64=$(base64 -i $easyrsa/tls-cert-file | tr -d '\040\011\012\015')
    $sed -i "$cbinstalldir"admission.yaml -re '49,58d'
    $sed -i '/caBundle/c\    caBundle: TLSCERTFILEBASE64' "$cbinstalldir"admission.yaml
    cat "$cbinstalldir"admission.yaml \
      | $sed -s "s@default@$COUCHBASE_NAMESPACE@g" \
      | $sed -s "s@TLSCERTFILEBASE64@$tlscertfilebase64@g" > tmpfile \
      && mv tmpfile "$cbinstalldir"admission.yaml \
      || emp_output

    $kubectl apply -f "$cbinstalldir"admission.yaml --namespace $COUCHBASE_NAMESPACE
    $kubectl apply -f "$cbinstalldir"crd.yaml --namespace $COUCHBASE_NAMESPACE
    $kubectl apply -f "$cbinstalldir"operator-role.yaml --namespace $COUCHBASE_NAMESPACE
    $kubectl create  serviceaccount couchbase-operator --namespace $COUCHBASE_NAMESPACE
    $kubectl create  rolebinding couchbase-operator --role couchbase-operator \
      --serviceaccount $COUCHBASE_NAMESPACE:couchbase-operator --namespace $COUCHBASE_NAMESPACE
    $kubectl apply -f "$cbinstalldir"operator-deployment.yaml --namespace $COUCHBASE_NAMESPACE
    is_pod_ready "app=couchbase-operator"
    $kubectl create secret generic cb-auth --from-literal=username=$COUCHBASE_USER \
      --from-literal=password=$CB_PW --namespace $COUCHBASE_NAMESPACE || emp_output
    cat couchbase/storageclasses.yaml \
      | $sed -s "s@VOLUMETYPE@$VOLUME_TYPE@g" > tmpfile \
      && mv tmpfile couchbase/storageclasses.yaml \
      || emp_output
    $kubectl apply -f couchbase/storageclasses.yaml --namespace $COUCHBASE_NAMESPACE
    cat couchbase/$couchbaseclusterfile \
      | $sed -s "s@CLUSTERNAME@$COUCHBASE_CLUSTER_NAME@g" > tmpfile \
      && mv tmpfile couchbase/$couchbaseclusterfile \
      || emp_output
    $kubectl apply -f couchbase/$couchbaseclusterfile --namespace $COUCHBASE_NAMESPACE
    is_pod_ready "couchbase_service_analytics=enabled"
    is_pod_ready "couchbase_service_data=enabled"
    is_pod_ready "couchbase_service_eventing=enabled"
    is_pod_ready "couchbase_service_index=enabled"
    is_pod_ready "couchbase_service_query=enabled"
    is_pod_ready "couchbase_service_search=enabled"
    rm -rf $cbinstalldir || emp_output
    if [[ $DEPLOY_MULTI_CLUSTER == "Y" || $DEPLOY_MULTI_CLUSTER == "y" ]]; then
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
    | $sed -s "s@LDAPVOLUMEID@$LDAP_STATIC_VOLUME_ID@g" \
    | $sed -s "s@STORAGELDAP@$LDAP_STORAGE_SIZE@g" \
    | $sed -s "s@LDAPDISKURI@$LDAP_STATIC_DISK_URI@g" \
    | $sed -s "s@STORAGESHAREDSHIB@$OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE@g" \
    | $sed -s "s@STORAGECASA@$CASA_STORAGE_SIZE@g" \
    | $sed -s "s@HOME_DIR@$HOME_DIR@g" \
    | $sed "s/\<COUCHBASEURL\>/$COUCHBASE_URL/" \
    | $sed "s/\<CBUSER\>/$COUCHBASE_USER/" \
    | $sed "s/\<FQDN\>/$GLUU_FQDN/" \
    | $sed "s#ACCOUNT#$GMAIL_ACCOUNT#g" \
    | $sed "s/\<GLUUCACHETYPE\>/$GLUU_CACHE_TYPE/" \
    | $sed -s "s@VOLUMETYPE@$VOLUME_TYPE@g" \
    | $sed -s "s@FILESYSTEMID@$EFS_FILE_SYSTEM_ID@g" \
    | $sed -s "s@AWSREGION@$EFS_AWS_REGION@g" \
    | $sed -s "s@EFSDNSNAME@$EFS_DNS@g" \
    | $sed -s "s@GLUUOXTRUSTAPIENABLED@$ENABLE_OXTRUST_API_BOOLEAN@g" \
    | $sed -s "s@GLUUOXTRUSTAPITESTMODE@$ENABLE_OXTRUST_TEST_MODE_BOOLEAN@g" \
    | $sed -s "s@GLUUCASAENABBLED@$ENABLE_CASA_BOOLEAN@g" \
    | $sed -s "s@GLUUPASSPORTENABLED@$ENABLE_OXPASSPORT_BOOLEAN@g" \
    | $sed -s "s@GLUURADIUSENABLED@$ENABLE_RADIUS_BOOLEAN@g" \
    | $sed -s "s@GLUUSAMLENABLED@$ENABLE_SAML_BOOLEAN@g" \
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
      || [[ "$1" == "couchbase_service_analytics=enabled" ]] \
      || [[ "$1" == "couchbase_service_data=enabled" ]] \
      || [[ "$1" == "couchbase_service_analytics=enabled" ]] \
      || [[ "$1" == "couchbase_service_eventing=enabled" ]] \
      || [[ "$1" == "couchbase_service_index=enabled" ]] \
      || [[ "$1" == "couchbase_service_query=enabled" ]] \
      || [[ "$1" == "couchbase_service_search=enabled" ]]; then
      pod_status="$($kubectl get pods -l "$1"  \
        -n $COUCHBASE_NAMESPACE \
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
      "LDAP_STORAGE_SIZE" ) LDAP_STORAGE_SIZE="$2"  ;;
      "OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE" ) OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE="$2"  ;;
      "STORAGE_NFS" ) STORAGE_NFS="$2"  ;;
      "EMAIL" ) EMAIL="$2"  ;;
      "ORG_NAME" ) ORG_NAME="$2" ;;
      "NODE_SSH_KEY" ) NODE_SSH_KEY="$2"  ;;
      "VOLUME_TYPE" ) VOLUME_TYPE="$2"  ;;
      "COUCHBASE_NAMESPACE" ) COUCHBASE_NAMESPACE="$2" ;;
      "COUCHBASE_CLUSTER_NAME" ) COUCHBASE_CLUSTER_NAME="$2"  ;;
      "COUCHBASE_USER" ) COUCHBASE_USER="$2"  ;;
      "GLUU_FQDN" ) GLUU_FQDN="$2"  ;;
      "COUNTRY_CODE" ) COUNTRY_CODE="$2" ;;
      "STATE" ) STATE="$2"  ;;
      "CITY" ) CITY="$2"  ;;
      "EMAIL" ) EMAIL="$2"  ;;
      "ORG_NAME" ) ORG_NAME="$2" ;;
      "COUCHBASE_FQDN" ) COUCHBASE_FQDN="$2" ;;
      "OXAUTH_REPLICAS" ) OXAUTH_REPLICAS="$2" ;;
      "OXTRUST_REPLICAS" ) OXTRUST_REPLICAS="$2" ;;
      "LDAP_REPLICAS" ) LDAP_REPLICAS="$2" ;;
      "OXSHIBBOLETH_REPLICAS" ) OXSHIBBOLETH_REPLICAS="$2" ;;
      "OXPASSPORT_REPLICAS" ) OXPASSPORT_REPLICAS="$2" ;;
      "OXD_SERVER_REPLICAS" ) OXD_SERVER_REPLICAS="$2" ;;
      "CASA_REPLICAS" ) CASA_REPLICAS="$2" ;;
      "RADIUS_REPLICAS" ) RADIUS_REPLICAS="$2" ;;
      "CASA_STORAGE_SIZE" ) CASA_STORAGE_SIZE="$2" ;;
      "DEPLOYMENT_ARCH" ) DEPLOYMENT_ARCH="$2" ;;
      "PERSISTENCE_BACKEND" ) PERSISTENCE_BACKEND="$2" ;;
      "DEPLOY_MULTI_CLUSTER" ) DEPLOY_MULTI_CLUSTER="$2" ;;
      "LDAP_VOLUME_TYPE" ) LDAP_VOLUME_TYPE="$2" ;;
      "OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE" ) OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE="$2" ;;
      "ACCEPT_EFS_NOTES" ) ACCEPT_EFS_NOTES="$2" ;;
      "CACHE_TYPE" ) CACHE_TYPE="$2" ;;
      "HYBRID_LDAP_HELD_DATA" ) HYBRID_LDAP_HELD_DATA="$2" ;;
      "USE_ARN" ) USE_ARN="$2" ;;
      "INSTALL_COUCHBASE" ) INSTALL_COUCHBASE="$2" ;;
      "ENABLE_CACHE_REFRESH" ) ENABLE_CACHE_REFRESH="$2" ;;
      "ENABLE_KEY_ROTATE" ) ENABLE_KEY_ROTATE="$2" ;;
      "ENABLE_RADIUS" ) ENABLE_RADIUS="$2" ;;
      "ENABLE_OXPASSPORT" ) ENABLE_OXPASSPORT="$2" ;;
      "ENABLE_OXSHIBBOLETH" ) ENABLE_OXSHIBBOLETH="$2" ;;
      "ENABLE_CASA" ) ENABLE_CASA="$2" ;;
      "ENABLE_OXTRUST_API" ) ENABLE_OXTRUST_API="$2" ;;
      "ENABLE_OXTRUST_TEST_MODE" ) ENABLE_OXTRUST_TEST_MODE="$2" ;;
      "LOAD_PREVIOUS_PARAMS" ) LOAD_PREVIOUS_PARAMS="$2" ;;
      "CONFIRM_PARAMS" ) CONFIRM_PARAMS="$2" ;;
      "IS_GLUU_FQDN_REGISTERED" ) IS_GLUU_FQDN_REGISTERED="$2" ;;
      "EASYRSA_COMMON_NAME" ) EASYRSA_COMMON_NAME="$2" ;;
      "DEPLOY_GENERATED_YAMLS" ) DEPLOY_GENERATED_YAMLS="$2" ;;
      "AWS_LB_TYPE" ) AWS_LB_TYPE="$2" ;;
      "COUCHBASE_NAMESPACE" ) COUCHBASE_NAMESPACE="$2" ;;
    esac
  fi
}

check_k8version() {
  kustomize="$kubectl kustomize"
  linux_flavor=""
  if [[ $machine != Mac ]]; then
    linux_flavor=$(cat /etc/*-release) || emp_output
  fi
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
  elif [[ $machine == Mac ]]; then
    HOST_EXT_IP=$(ipconfig getifaddr en0)
    brew install gnu-sed || emp_output
    brew tap AdoptOpenJDK/openjdk || emp_output
    brew install jq || emp_output
    brew cask install adoptopenjdk8 || emp_output
    sed=gsed || emp_output
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

prompt_password() {
  while true; do
    TEMP_PW_RAND="$(cat /dev/urandom \
      | env LC_CTYPE=C tr -dc 'a-zA-Z0-9A-Za-z0-9!@^%_+#$' \
      | fold -w 6 | head -c 6)"GlU4%
    TEMP_PW_OUT=${TEMP_PW_RAND::3}
    TEMP_PW_RAND_OUT="$TEMP_PW_OUT***"
    echo "Passwords requires the following structure :"
    echo "One upper case, one lower case, one number, one of the following symbols @#%^&*_+ and a total of 6 characters"
    echo "Enter $2 password.[$TEMP_PW_RAND_OUT]:"
    mask_password
    if [[ ! "$password" ]]; then
      TEMP_PW=$TEMP_PW_RAND
      break
    else
      TEMP_PW=$password
      if [[ ${#TEMP_PW} -ge 6 && "$TEMP_PW" == *[[:lower:]]* && "$TEMP_PW" == *[[:upper:]]* && "$TEMP_PW" == *[0-9]* && "$TEMP_PW" == *['!'@#\$%^\&*_+]* ]]; then
        echo "Confirm password :"
        mask_password
        TEMP_PW_VERIFY=$password
        [ "$TEMP_PW" = "$TEMP_PW_VERIFY" ] && break || echo "Please try again"
      else
        echo "Password does not meet requirments."
      fi
    fi
  done
  if [[ "$1" == "ADMIN_PW" ]]; then
    ADMIN_PW="$TEMP_PW"
    echo "$TEMP_PW" > gluu_admin_password
  elif [[ "$1" == "CB_PW" ]]; then
    CB_PW="$TEMP_PW"
    echo "$TEMP_PW" > couchbase_password
  elif [[ "$1" == "EASYRSA_PW" ]]; then
    EASYRSA_PW="$TEMP_PW"
    echo "$TEMP_PW" > easyrsa_ca_password
  fi
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
    if [[ ! $HOST_EXT_IP ]]; then
      HOST_EXT_IP=$(ip route get 8.8.8.8 \
        | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
    fi
  elif [[ $machine == Mac ]]; then
    if [[ ! $HOST_EXT_IP ]]; then
      HOST_EXT_IP=$(ipconfig getifaddr en0)
    fi
  else
    if [[ ! $HOST_EXT_IP ]]; then
      echo "Cannot determine IP address."
      read -rp "Please input the hosts external IP Address:                      " HOST_EXT_IP
    fi
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
  if [[ ! $VERIFY_EXT_IP ]]; then
    read -rp "Is this the correct external IP Address: ${HOST_EXT_IP} [Y/n]?         " VERIFY_EXT_IP
  fi
  case "$VERIFY_EXT_IP" in
    y|Y)
      return 0
    ;;
    n|N)
      read -rp "Please input the hosts external IP Address:                    " HOST_EXT_IP
      if valid_ip "$HOST_EXT_IP"; then
        return 0
      else
        echo "Please enter a valid IP Address."
        gather_ip
        return 1
      fi
      return 0
    ;;
    *)
      VERIFY_EXT_IP="Y"
      return 0
    ;;
  esac
}

prompt_cb() {
 if [[ $PERSISTENCE_BACKEND -ge 1 ]]; then
    if [[ $INSTALL_COUCHBASE != "n" ]] && [[ $INSTALL_COUCHBASE != "N" ]]; then
      echo "Couchbase will begin installation..."
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
  echo "|------------------------------------------------------------------|"
  echo "|                     Local Deployments                            |"
  echo "|------------------------------------------------------------------|"
  echo "| [1]  Microk8s [default]                                          |"
  echo "| [2]  Minikube                                                    |"
  echo "|------------------------------------------------------------------|"
  echo "|                     Cloud Deployments                            |"
  echo "|------------------------------------------------------------------|"
  echo "| [3] Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)|"
  echo "| [4] Google Cloud Engine - Google Kubernetes Engine (GKE)         |"
  echo "| [5] Microsoft Azure (AKS)                                        |"
  echo "|------------------------------------------------------------------|"
  if [[ ! "$DEPLOYMENT_ARCH" ]]; then
    read -rp "Deploy using?                                                      " DEPLOYMENT_ARCH \
      && set_default "$DEPLOYMENT_ARCH" "1" "DEPLOYMENT_ARCH"
    if [[ ! "$DEPLOYMENT_ARCH" ]]; then
      DEPLOYMENT_ARCH=1
    fi
  fi
  echo "|------------------------------------------------------------------|"
  echo "|                     Persistence layer                            |"
  echo "|------------------------------------------------------------------|"
  echo "| [0] WrenDS [default]                                             |"
  echo "| [1] Couchbase [Testing Phase]                                    |"
  echo "| [2] Hybrid(WrenDS + Couchbase)[Testing Phase]                    |"
  echo "|------------------------------------------------------------------|"
  if [[ ! "$PERSISTENCE_BACKEND" ]]; then
    read -rp "Persistence layer?                                                 " PERSISTENCE_BACKEND \
      && set_default "$PERSISTENCE_BACKEND" "0" "PERSISTENCE_BACKEND"
  fi
  case "$PERSISTENCE_BACKEND" in
    1 ) PERSISTENCE_TYPE="couchbase";;
    2 ) PERSISTENCE_TYPE="hybrid"  ;;
    * ) PERSISTENCE_TYPE="ldap" ;;
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
  if [[ ! "$DEPLOY_MULTI_CLUSTER" ]]; then
    read -rp "Is this a multi-cloud/region setup[N]                              " DEPLOY_MULTI_CLUSTER \
      && set_default "$DEPLOY_MULTI_CLUSTER" "N" "DEPLOY_MULTI_CLUSTER"
  fi
  if [[ $PERSISTENCE_BACKEND -ne 1 ]]; then
    echo "|------------------------------------------------------------------|"
    echo "|                     Local Deployments                            |"
    echo "|------------------------------------------------------------------|"
    echo "| [1]  Microk8s | LDAP volumes on host [default]                   |"
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
    if [[ ! "$LDAP_VOLUME_TYPE" ]]; then
      read -rp "What type of deployment?                                         " LDAP_VOLUME_TYPE \
        && set_default "$LDAP_VOLUME_TYPE" "1" "LDAP_VOLUME_TYPE"
    fi
    if [[ $LDAP_VOLUME_TYPE -eq 9 ]];then
      if [[ ! "$ACCEPT_EFS_NOTES" ]]; then
        read -rp "EFS created [Y]" ACCEPT_EFS_NOTES
        read -rp "EFS must be inside the same region as the EKS cluster [Y]" ACCEPT_EFS_NOTES
        read -rp "VPC of EKS and EFS are the same [Y]" ACCEPT_EFS_NOTES
        read -rp "Security group of EFS allows all connections from EKS nodes [Y]" ACCEPT_EFS_NOTES \
          && set_default "$ACCEPT_EFS_NOTES" "Y" "ACCEPT_EFS_NOTES"
      fi
      if [[ ACCEPT_EFS_NOTES == "n" ]] || [[ ACCEPT_EFS_NOTES == "N" ]]; then
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
  if [[ ! "$CACHE_TYPE" ]]; then
    read -rp "Cache layer?                                                       " CACHE_TYPE \
      && set_default "$CACHE_TYPE" "0" "CACHE_TYPE"
  fi
  case "$CACHE_TYPE" in
    1 ) GLUU_CACHE_TYPE="IN_MEMORY"  ;;
    2 ) GLUU_CACHE_TYPE="REDIS" ;;
    * ) GLUU_CACHE_TYPE="NATIVE_PERSISTENCE"  ;;
  esac
  LDAP_MAPPING="default"
  GLUU_CACHE_TYPE="'${GLUU_CACHE_TYPE}'"
  #COUCHBASE
  COUCHBASE_URL="couchbase"
  COUCHBASE_USER="admin"
  if [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
    echo "|-----------------------------------------------------------------|"
    echo "|                     Hybrid [WrendDS + Couchbase]                |"
    echo "|-----------------------------------------------------------------|"
    echo "| [0] Default                                                     |"
    echo "| [1] User                                                        |"
    echo "| [2] Site                                                        |"
    echo "| [3] Cache                                                       |"
    echo "| [4] Token                                                       |"
    echo "|-----------------------------------------------------------------|"
    if [[ ! "$HYBRID_LDAP_HELD_DATA" ]]; then
      read -rp "Persistence type?                                                " HYBRID_LDAP_HELD_DATA \
        && set_default "$HYBRID_LDAP_HELD_DATA" "0" "HYBRID_LDAP_HELD_DATA"
    fi
    case "$HYBRID_LDAP_HELD_DATA" in
      1 ) LDAP_MAPPING="user"  ;;
      2 ) LDAP_MAPPING="site"  ;;
      3 ) LDAP_MAPPING="cache" ;;
      4 ) LDAP_MAPPING="token"  ;;
      * ) LDAP_MAPPING="default"  ;;
    esac
  fi
  if [[ $DEPLOYMENT_ARCH -eq 1 ]]; then
    kubectl=microk8s.kubectl || emp_output
    microk8s.enable dns ingress storage || emp_output
  else
    kubectl=kubectl || emp_output
  fi
  check_k8version
  if [[ $DEPLOYMENT_ARCH -eq 2 ]] || [[ $DEPLOYMENT_ARCH -eq 1 ]]; then
    gather_ip
    until confirm_ip; do : ; done
    ip=$HOST_EXT_IP
  else
    # Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
    ip=22.22.22.22
  fi
  if [[ $DEPLOYMENT_ARCH -eq 3 ]]; then
    echo "|-----------------------------------------------------------------|"
    echo "|                     AWS Loadbalancer type                       |"
    echo "|-----------------------------------------------------------------|"
    echo "| [0] Classic Load Balancer (CLB) [default]                       |"
    echo "| [1] Network Load Balancer (NLB - Alpha) -- Static IP            |"
    echo "|-----------------------------------------------------------------|"
    if [[ ! "$AWS_LB_TYPE" ]]; then
      read -rp "Loadbalancer type ?                                              " AWS_LB_TYPE \
        && set_default "$AWS_LB_TYPE" "0" "AWS_LB_TYPE"
    fi
    case "$AWS_LB_TYPE" in
      0 ) lbChoice="clb"  ;;
      1 ) lbChoice="nlb"  ;;
      * ) lbChoice="clb"  ;;
    esac
    if [[ ! "$USE_ARN" ]]; then
      read -rp "Are you terminating SSL traffic at LB and using certificate from
         AWS [N][Y/N]   : " USE_ARN \
         && set_default "$USE_ARN" "N" "USE_ARN"
    fi
    if [[ $USE_ARN == "Y" || $USE_ARN == "y" ]]; then
      if [[ ! "$ARN_AWS_IAM" ]]; then
        read -rp 'Enter aws-load-balancer-ssl-cert arn quoted \
          ("arn:aws:acm:us-west-2:XXXXXXXX:certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX"): ' ARN_AWS_IAM
      fi
    fi
  fi
  if [[ $PERSISTENCE_BACKEND -ge 1 ]]; then
    COUCHBASE_URL=""
    echo "For the following prompt  if placed [N] the couchbase
      is assumed to be installed or remotely provisioned"
    if [[ ! "$INSTALL_COUCHBASE" ]]; then
      read -rp "Install Couchbase[Y][Y/N] ?                                      " INSTALL_COUCHBASE \
        && set_default "$INSTALL_COUCHBASE" "Y" "INSTALL_COUCHBASE"
    fi
    if [[ $INSTALL_COUCHBASE != "n" ]] && [[ $INSTALL_COUCHBASE != "N" ]]; then
      if [ -f couchbase-autonomous-operator-kubernetes_*.tar.gz ];then
        if [[ ! "$VOLUME_TYPE" ]]; then
          read -rp "Please enter the volume type for EBS.[io1]    :           \
            " VOLUME_TYPE && set_default "$VOLUME_TYPE" "io1" "VOLUME_TYPE"
        fi
        if [[ ! "$COUCHBASE_NAMESPACE" ]]; then
          read -rp "Please enter a namespace for CB objects.[cbns] \
            " COUCHBASE_NAMESPACE && set_default "$COUCHBASE_NAMESPACE" "cbns" "COUCHBASE_NAMESPACE"
        fi
        if [[ ! "$COUCHBASE_NAMESPACE" ]]; then
          read -rp "Please enter a namespace for CB objects.[cbns] \
            " COUCHBASE_NAMESPACE && set_default "$COUCHBASE_NAMESPACE" "cbns" "COUCHBASE_NAMESPACE"
        fi
        if [[ ! "$COUCHBASE_CLUSTER_NAME" ]]; then
          read -rp "Please enter a cluster name.[cbgluu] \
            " COUCHBASE_CLUSTER_NAME && set_default "$COUCHBASE_CLUSTER_NAME" "cbgluu" "COUCHBASE_CLUSTER_NAME"
        fi
        COUCHBASE_URL="$COUCHBASE_CLUSTER_NAME.$COUCHBASE_NAMESPACE.svc.cluster.local"
        if [[ ! "$COUCHBASE_FQDN" ]]; then
          read -rp "Please enter a couchbase domain for SAN. \
            " COUCHBASE_FQDN && set_default "$COUCHBASE_FQDN" "cb.gluu.org" "COUCHBASE_FQDN"
        fi
      else
        echo "Error: Couchbase package not found."
        echo "Please download the couchbase kubernetes package and place it inside
          the same directory containing the create.sh script.
          https://www.couchbase.com/downloads"
        exit 1
      fi
    fi
    if [ -z "$COUCHBASE_URL" ];then
      read -rp "Please enter remote couchbase URL base name couchbase.gluu.org  " COUCHBASE_URL
    fi
    if [[ ! "$COUCHBASE_USER" ]]; then
      read -rp "Please enter couchbase username [admin]                         " COUCHBASE_USER \
        && set_default "$COUCHBASE_USER" "admin" "COUCHBASE_USER"
    fi
    #TODO: Add test CB connection
    if [[ ! "$CB_PW" ]]; then
      prompt_password "CB_PW" "Couchbase"
    fi
    echo "Password is located in couchbase_password.
      Please save your password securely and delete file couchbase_password"
  fi
  if [[ ! "$ENABLE_CACHE_REFRESH" ]]; then
    read -rp "Deploy Cr-Rotate[N]?[Y/N]                                          " ENABLE_CACHE_REFRESH \
      && set_default "$ENABLE_CACHE_REFRESH" "N" "ENABLE_CACHE_REFRESH"
  fi
  if [[ ! "$ENABLE_KEY_ROTATE" ]]; then
    read -rp "Deploy Key-Rotation[N]?[Y/N]                                       " ENABLE_KEY_ROTATE \
      && set_default "$ENABLE_KEY_ROTATE" "N" "ENABLE_KEY_ROTATE"
  fi
  if [[ ! "$ENABLE_RADIUS" ]]; then
    read -rp "Deploy Radius[N]?[Y/N]                                             " ENABLE_RADIUS \
      && set_default "$ENABLE_RADIUS" "N" "ENABLE_RADIUS"
  fi
  if [[ ! "$ENABLE_OXPASSPORT" ]]; then
    read -rp "Deploy Passport[N]?[Y/N]                                           " ENABLE_OXPASSPORT \
      && set_default "$ENABLE_OXPASSPORT" "N" "ENABLE_OXPASSPORT"
  fi
  if [[ ! "$ENABLE_OXSHIBBOLETH" ]]; then
    read -rp "Deploy Shibboleth SAML IDP[N]?[Y/N]                                " ENABLE_OXSHIBBOLETH \
      && set_default "$ENABLE_OXSHIBBOLETH" "N" "ENABLE_OXSHIBBOLETH"
  fi
  if [[ ! "$ENABLE_CASA" ]]; then
    read -rp "[Testing Phase] Deploy Casa[N]?[Y/N]                               " ENABLE_CASA \
      && set_default "$ENABLE_CASA" "N" "ENABLE_CASA"
  fi
  if [[ ! "$ENABLE_OXTRUST_API" ]]; then
    read -rp "Enable oxTrust Api         [N]?[Y/N]                               " ENABLE_OXTRUST_API \
      && set_default "$ENABLE_OXTRUST_API" "N" "ENABLE_OXTRUST_API"
  fi
  ENABLE_OXTRUST_API_BOOLEAN="'false'"
  ENABLE_OXTRUST_TEST_MODE_BOOLEAN="'false'"
  if [[ $ENABLE_OXTRUST_API == "y" || $ENABLE_OXTRUST_API == "Y" ]]; then
    ENABLE_OXTRUST_API_BOOLEAN="'true'"
    if [[ ! "$ENABLE_OXTRUST_TEST_MODE" ]]; then
      read -rp "Enable oxTrust Test Mode [N]?[Y/N]                               " ENABLE_OXTRUST_TEST_MODE \
        && set_default "$ENABLE_OXTRUST_TEST_MODE" "N" "ENABLE_OXTRUST_TEST_MODE"
    fi
    if [[ $ENABLE_OXTRUST_TEST_MODE == "y" || $ENABLE_OXTRUST_TEST_MODE == "Y" ]]; then
      ENABLE_OXTRUST_TEST_MODE_BOOLEAN="'true'"
    fi
  fi
  ENABLE_RADIUS_BOOLEAN="'false'"
  ENABLE_OXPASSPORT_BOOLEAN="'false'"
  ENABLE_CASA_BOOLEAN="'false'"
  ENABLE_SAML_BOOLEAN="'false'"
  if [[ $ENABLE_RADIUS == "y" || $ENABLE_RADIUS == "Y" ]]; then
    ENABLE_RADIUS_BOOLEAN="'true'"
  fi
  if [[ $ENABLE_OXPASSPORT == "y" || $ENABLE_OXPASSPORT == "Y" ]]; then
    ENABLE_OXPASSPORT_BOOLEAN="'true'"
  fi
  if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
    ENABLE_CASA_BOOLEAN="'true'"
  fi
  if [[ $ENABLE_OXSHIBBOLETH == "y" || $ENABLE_OXSHIBBOLETH == "Y" ]]; then
    ENABLE_SAML_BOOLEAN="'true'"
  fi
    if [[ $DEPLOYMENT_ARCH  -eq 3 ]];then
      echo "|-----------------------------------------------------------------|"
      echo "|                     Shared Shibboleth Volume                    |"
      echo "|-----------------------------------------------------------------|"
      echo "| [0] local storage [default]                                     |"
      echo "| [1] EFS - Required for production                               |"
      echo "|-----------------------------------------------------------------|"
      if [[ ! "$OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE" ]]; then
        read -rp "Type of Shibboleth volume                                      " OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE \
          && set_default "$OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE" "0" "OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE"
      fi
      if [[ OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE -eq 1 ]]; then
        if [[ ! "$OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE" ]]; then
          read -rp "EFS created [Y]" ACCEPT_EFS_NOTES
          read -rp "EFS must be inside the same region as the EKS cluster [Y]" ACCEPT_EFS_NOTES
          read -rp "VPC of EKS and EFS are the same [Y]" ACCEPT_EFS_NOTES
          read -rp "Security group of EFS allows all connections from EKS nodes [Y]" ACCEPT_EFS_NOTES \
            && set_default "$ACCEPT_EFS_NOTES" "Y" "ACCEPT_EFS_NOTES"
        fi
        if [[ ! "$EFS_FILE_SYSTEM_ID" ]]; then
          read -rp "Enter FileSystemID (fs-xxx):                                     " EFS_FILE_SYSTEM_ID
        fi
        if [[ ! "$EFS_AWS_REGION" ]]; then
          read -rp "Enter AWS region (us-west-2):                                    " EFS_AWS_REGION
        fi
        if [[ ! "$EFS_DNS" ]]; then
          read -rp "Enter EFS dns name (fs-xxx.us-west-2.amazonaws.com):             " EFS_DNS
        fi
        if [[ ACCEPT_EFS_NOTES == "n" ]] || [[ ACCEPT_EFS_NOTES == "N" ]]; then
          exit 1
        fi
      fi
    fi
  if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
    choiceOXD="Y"
  #else
  #  read -rp "Deploy OXD-Server[N]?[Y/N]                                       " choiceOXD
  fi
  #TODO: Allow user inputs here and eliminate duplication below
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
    $kubectl get cm gluu -o yaml > gluu-cm.yaml
    $kubectl get secret gluu -o yaml > gluu-secret.yaml
    if [[ ! "$LOAD_PREVIOUS_PARAMS" ]]; then
      read -rp "[I] Use pervious params? [Y/n]                                   " LOAD_PREVIOUS_PARAMS \
        && set_default "$LOAD_PREVIOUS_PARAMS" "N" "LOAD_PREVIOUS_PARAMS"
    fi
    if [[ $LOAD_PREVIOUS_PARAMS != "y" && $LOAD_PREVIOUS_PARAMS != "Y" ]]; then
      generate=1
    fi
  fi
  # config is not loaded from previously saved configuration
  if [[ $generate -eq 1 ]]; then
    echo "[I] Removing all previous gluu services if found"
    delete_all
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
    echo "[I] Creating new configuration, please input the following parameters"
    if [[ ! "$GLUU_FQDN" ]]; then
      read -rp "Enter Hostname [demoexample.gluu.org]:                           " GLUU_FQDN \
        && set_default "$GLUU_FQDN" "demoexample.gluu.org" "GLUU_FQDN"
    fi
    if ! [[ $GLUU_FQDN == *"."*"."* ]]; then
      echo "[E] Hostname provided is invalid.
        Please enter a FQDN with the format demoexample.gluu.org"
      exit 1
    fi
    if [[ ! "$COUNTRY_CODE" ]]; then
      read -rp "Enter Country Code [US]:                                         " COUNTRY_CODE \
        && set_default "$COUNTRY_CODE" "US" "COUNTRY_CODE"
    fi
    if [[ ! "$STATE" ]]; then
      read -rp "Enter State [TX]:                                                " STATE \
        && set_default "$STATE" "TX" "STATE"
    fi
    if [[ ! "$CITY" ]]; then
      read -rp "Enter City [Austin]:                                             " CITY \
        && set_default "$CITY" "Austin" "CITY"
    fi
    if [[ ! "$EMAIL" ]]; then
      read -rp "Enter Email [support@gluu.org]:                                  " EMAIL \
        && set_default "$EMAIL" "support@gluu.org" "EMAIL"
    fi
    if [[ ! "$ORG_NAME" ]]; then
      read -rp "Enter Organization [Gluu]:                                       " ORG_NAME \
        && set_default "$ORG_NAME" "Gluu" "ORG_NAME"
    fi
    if [[ ! "$ADMIN_PW" ]]; then
      prompt_password "ADMIN_PW" "Gluu"
    fi
    if [[ ! "$CONFIRM_PARAMS" ]]; then
      read -rp "Continue with the above settings? [Y/n]                          " CONFIRM_PARAMS \
        && set_default "$CONFIRM_PARAMS" "Y" "CONFIRM_PARAMS"
    fi
    case "$CONFIRM_PARAMS" in
      y|Y ) ;;
      n|N ) exit 1 ;;
      * )   ;;
    esac
    echo "{" > config/base/generate.json
    echo '"hostname"': \"$GLUU_FQDN\", >> config/base/generate.json
    echo '"country_code"': \"$COUNTRY_CODE\", >> config/base/generate.json
    echo '"state"': \"$STATE\", >> config/base/generate.json
    echo '"city"': \"$CITY\", >> config/base/generate.json
    echo '"admin_pw"': \"$ADMIN_PW\", >> config/base/generate.json
    echo '"email"': \"$EMAIL\", >> config/base/generate.json
    echo '"org_name"': \"$ORG_NAME\" >> config/base/generate.json
    echo "}" >> config/base/generate.json
  else
    $kubectl apply -f gluu-cm.yaml || emp_output
    $kubebctl apply -f gluu-secret.yaml || emp_output
    GLUU_FQDN="$kubectl get cm gluu --output jsonpath='{.data.hostname}'"
    deployConfig="N"
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
  if [[ $LDAP_VOLUME_TYPE -eq 7 ]] \
    || [[ $LDAP_VOLUME_TYPE -eq 12 ]] \
    || [[ $LDAP_VOLUME_TYPE -eq 17 ]]; then
    if [[ -f ldap/$yaml_folder/storageclasses_copy.yaml ]]; then
      cp ldap/$yaml_folder/storageclasses_copy.yaml ldap/$yaml_folder/storageclasses.yaml
    fi
    cp ldap/$yaml_folder/storageclasses.yaml ldap/$yaml_folder/storageclasses_copy.yaml
  fi
  while true;do
    num=$(($num - 1))
    google_azure_zone="${arrzones[$num]}"
    singlezone="${arrzones[$num]}"
    if [[ $LDAP_VOLUME_TYPE -eq 7 ]] \
      || [[ $LDAP_VOLUME_TYPE -eq 12 ]] \
      || [[ $LDAP_VOLUME_TYPE -eq 17 ]]; then
      printf  "\n    - $singlezone" \
        >> ldap/$yaml_folder/storageclasses.yaml
    fi
    if [[ $num -eq 0 ]];then
      break
    fi
  done
}

prompt_replicas() {
  if [[ ! "$OXAUTH_REPLICAS" ]]; then
    read -rp "Number of oxAuth replicas [1]:                                     " OXAUTH_REPLICAS \
      && set_default "$OXAUTH_REPLICAS" "1" "OXAUTH_REPLICAS"
  fi

  if [[ ! "$OXTRUST_REPLICAS" ]]; then
    read -rp "Number of oxTrust replicas [1]:                                    " OXTRUST_REPLICAS \
      && set_default "$OXTRUST_REPLICAS" "1" "OXTRUST_REPLICAS"
  fi

  if [[ ! "$LDAP_REPLICAS" ]]; then
    if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
      read -rp "Number of LDAP replicas [1]:                                     " LDAP_REPLICAS \
        && set_default "$LDAP_REPLICAS" "1" "LDAP_REPLICAS"
    fi
  fi

  if [[ ! "$OXSHIBBOLETH_REPLICAS" ]]; then
    if [[ $ENABLE_OXSHIBBOLETH == "y" || $ENABLE_OXSHIBBOLETH == "Y" ]]; then
      # oxShibboleth
      read -rp "Number of oxShibboleth replicas [1]:                             " OXSHIBBOLETH_REPLICAS \
        && set_default "$OXSHIBBOLETH_REPLICAS" "1" "OXSHIBBOLETH_REPLICAS"
    fi
  fi

  if [[ ! "$OXPASSPORT_REPLICAS" ]]; then
    if [[ $ENABLE_OXPASSPORT == "y" || $ENABLE_OXPASSPORT == "Y" ]]; then
      # oxPassport
      read -rp "Number of oxPassport replicas [1]:                               " OXPASSPORT_REPLICAS \
        && set_default "$OXPASSPORT_REPLICAS" "1" "OXPASSPORT_REPLICAS"
    fi
  fi

  if [[ ! "$OXD_SERVER_REPLICAS" ]]; then
    if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
      read -rp "Number of oxd-server replicas [1]:                               " OXD_SERVER_REPLICAS \
        && set_default "$OXD_SERVER_REPLICAS" "1" "OXD_SERVER_REPLICAS"
    fi
  fi

  if [[ ! "$CASA_REPLICAS" ]]; then
    if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
      read -rp "Number of casa replicas [1]:                                     " CASA_REPLICAS \
        && set_default "$CASA_REPLICAS" "1" "CASA_REPLICAS"
    fi
  fi

  if [[ ! "$RADIUS_REPLICAS" ]]; then
    if [[ $ENABLE_RADIUS == "y" || $ENABLE_RADIUS == "Y" ]]; then
      # Radius server
      read -rp "Number of Radius replicas [1]:                                   " RADIUS_REPLICAS \
        && set_default "$RADIUS_REPLICAS" "1" "RADIUS_REPLICAS"
    fi
  fi
}

prompt_storage() {
  OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE="4Gi"
  CASA_STORAGE_SIZE=$OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE
  if [[ ! "$LDAP_STORAGE_SIZE" ]]; then
    if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
      read -rp "Size of ldap volume storage [4Gi]:                               " LDAP_STORAGE_SIZE \
        && set_default "$LDAP_STORAGE_SIZE" "4Gi" "LDAP_STORAGE_SIZE"
    fi
  fi

  if [[ ! "$OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE" ]]; then
    if [[ $ENABLE_OXSHIBBOLETH == "y" || $ENABLE_OXSHIBBOLETH == "Y" ]]; then
      read -p "Size of Shared-Shib volume storage [4Gi]:                         " OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE \
        && set_default "$OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE" "4Gi" "OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"
    fi
  fi

  if [[ ! "$CASA_STORAGE_SIZE" ]]; then
    if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
      read -p "Size of Casa volume storage [4Gi]:                                " CASA_STORAGE_SIZE \
        && set_default "$CASA_STORAGE_SIZE" "4Gi" "CASA_STORAGE_SIZE"
    fi
  fi
}

gke_prompts() {
  if [[ ! "$GMAIL_ACCOUNT" ]]; then
    read -rp "Please enter valid email for Google Cloud account:                 " GMAIL_ACCOUNT
  fi
  echo "Trying to login user: root..."
  NODE=$(kubectl get no \
    -o go-template='{{range .items}}{{.metadata.name}} {{end}}' \
    | awk -F " " '{print $1}')
  HOME_DIR=$(gcloud compute ssh root@$NODE --zone=${arrzones[0]} --command='echo $HOME' \
             || gcloud compute ssh root@$NODE --zone=${arrzones[1]} --command='echo $HOME' \
             || gcloud compute ssh root@$NODE --zone=${arrzones[2]} --command='echo $HOME' \
             || echo "Permission denied")
  if [[ $HOME_DIR =~ "Permission denied" ]];then
    echo "This occurs when your compute instance has PermitRootLogin set to  no in it's SSHD config."
    echo "Trying to login using user: user"
    HOME_DIR=$(gcloud compute ssh user@$NODE --zone=${arrzones[0]} --command='echo $HOME' \
               || gcloud compute ssh user@$NODE --zone=${arrzones[1]} --command='echo $HOME' \
               || gcloud compute ssh user@$NODE --zone=${arrzones[2]} --command='echo $HOME' \
               || emp_output)
  fi
  generate_nfs
}

generate_nfs() {
  $kustomize shared-shib/nfs > $output_yamls/nfs.yaml
  STORAGE_NFS=$OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE
}

prompt_volumes_identitfier() {
  if [[ ! "$LDAP_STATIC_VOLUME_ID" ]]; then
    if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
      read -rp "Please enter $static_volume_prompt for LDAP:                     " LDAP_STATIC_VOLUME_ID
    fi
  fi
}

prompt_disk_uris() {
  if [[ ! "$LDAP_STATIC_DISK_URI" ]]; then
    if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
      read -rp "Please enter the disk uri for LDAP:                              " LDAP_STATIC_DISK_URI
    fi
  fi

}
output_inital_yamls() {
  if [[ $DEPLOYMENT_ARCH -eq 3 ]] \
    && [[ $OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE -eq 1 ]]; then
    $kustomize shared-shib/efs \
      | replace_all  > $output_yamls/shared-shib.yaml
  elif [[ $DEPLOYMENT_ARCH -eq 4 ]] || [[ $DEPLOYMENT_ARCH -eq 5 ]]; then
    $kustomize shared-shib/nfs \
      | replace_all  > $output_yamls/shared-shib.yaml
  else
    $kustomize shared-shib/localstorage \
      | replace_all  > $output_yamls/shared-shib.yaml
  fi
  # Config
  $kustomize config/base | replace_all > $output_yamls/config.yaml
  # WrenDS
  if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
    $kustomize ldap/$yaml_folder | replace_all > $output_yamls/ldap.yaml
  fi
  # Persistence
  $kustomize persistence/base | replace_all > $output_yamls/persistence.yaml
  # oxAuth
  $kustomize oxauth/base | replace_all > $output_yamls/oxauth.yaml
  # oxTrust
  $kustomize oxtrust/base | replace_all > $output_yamls/oxtrust.yaml
  if [[ $ENABLE_OXSHIBBOLETH == "y" || $ENABLE_OXSHIBBOLETH == "Y" ]]; then
    # oxShibboleth
    $kustomize oxshibboleth/base \
      | replace_all  > $output_yamls/oxshibboleth.yaml
  fi

  if [[ $ENABLE_OXPASSPORT == "y" || $ENABLE_OXPASSPORT == "Y" ]]; then
    # oxPassport
    $kustomize oxpassport/base \
      | replace_all  > $output_yamls/oxpassport.yaml
  fi
  if [[ $ENABLE_KEY_ROTATE == "y" || $ENABLE_KEY_ROTATE == "Y" ]]; then
    # Key Rotationls
    $kustomize key-rotation/base | replace_all > $output_yamls/key-rotation.yaml
  fi
  if [[ $ENABLE_CACHE_REFRESH == "y" || $ENABLE_CACHE_REFRESH == "Y" ]]; then
    # Cache Refresh rotating IP registry
    $kustomize cr-rotate/base | replace_all > $output_yamls/cr-rotate.yaml
  fi
    # OXD-Server
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    $kustomize oxd-server/base | replace_all > $output_yamls/oxd-server.yaml
  fi
    # Casa
  if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
    $kustomize casa/base | replace_all > $output_yamls/casa.yaml
  fi
  # Radius
  if [[ $ENABLE_RADIUS == "y" || $ENABLE_RADIUS == "Y" ]]; then
    # Radius server
    $kustomize radius/base | replace_all > $output_yamls/radius.yaml
  fi
  if [[ $CACHE_TYPE == 2 ]];then
    $kustomize redis/base/ | replace_all > $output_yamls/redis.yaml
  fi
}

generate_yamls() {
  if [[ ! "$IS_GLUU_FQDN_REGISTERED" ]]; then
    read -rp "Are you using a globally resolvable FQDN [N] [Y/N]:                " IS_GLUU_FQDN_REGISTERED \
      && set_default "$IS_GLUU_FQDN_REGISTERED" "N" "IS_GLUU_FQDN_REGISTERED"
  fi
  if [[ $IS_GLUU_FQDN_REGISTERED == "y" || $IS_GLUU_FQDN_REGISTERED == "Y" ]]; then
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
  if [[ $DEPLOYMENT_ARCH -eq 2 ]]; then
    mkdir gluuminikubeyamls || emp_output
    create_local_minikube
    yaml_folder=$local_minikube_folder
    output_yamls=gluuminikubeyamls
  elif [[ $DEPLOYMENT_ARCH -eq 3 ]]; then
    mkdir gluueksyamls || emp_output
    output_yamls=gluueksyamls
    if [[ $LDAP_VOLUME_TYPE -eq 6 ]]; then
      yaml_folder=$local_eks_folder

    elif [[ $LDAP_VOLUME_TYPE -eq 7 ]]; then
      echo "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html"
      echo "Follow the doc above to help you choose
        which volume type to use.Options are [gp2,io1,st1,and sc1]"
      if [[ ! "$VOLUME_TYPE" ]]; then
        read -rp "Please enter the volume type for EBS[io1]:                       " VOLUME_TYPE \
          && set_default "$VOLUME_TYPE" "io1" "VOLUME_TYPE"
      fi
      yaml_folder=$dynamic_eks_folder

    elif [[ $LDAP_VOLUME_TYPE -eq 8 ]]; then
      yaml_folder=$static_eks_folder
      echo "Zones of your volumes are required to match the deployments to the volume zone"
      static_volume_prompt="EBS Volume ID"
      prompt_volumes_identitfier

    elif [[ $LDAP_VOLUME_TYPE -eq 9 ]]; then
      create_efs_aws
      yaml_folder=$efs_eks_folder
      if [[ ! "$EFS_FILE_SYSTEM_ID" ]]; then
        read -rp "Enter FileSystemID (fs-xxx):                                     " EFS_FILE_SYSTEM_ID
      fi

      if [[ ! "$EFS_AWS_REGION" ]]; then
        read -rp "Enter AWS region (us-west-2):                                    " EFS_AWS_REGION
      fi

      if [[ ! "$EFS_DNS" ]]; then
        read -rp "Enter EFS dns name (fs-xxx.us-west-2.amazonaws.com):             " EFS_DNS
      fi
    fi
    prompt_zones
  elif [[ $DEPLOYMENT_ARCH -eq 4 ]]; then
    mkdir gluugkeyamls || emp_output
    output_yamls=gluugkeyamls
    if [[ $LDAP_VOLUME_TYPE -eq 11 ]]; then
      yaml_folder=$local_gke_folder

    elif [[ $LDAP_VOLUME_TYPE -eq 12 ]]; then
      if [[ ! "$VOLUME_TYPE" ]]; then
        echo "Please enter the volume type for the persistent disk."
        read -rp "Options are (pd-standard, pd-ssd). [pd-ssd] :                    " VOLUME_TYPE \
          && set_default "$VOLUME_TYPE" "pd-ssd" "VOLUME_TYPE"
      fi
      create_dynamic_gke
      yaml_folder=$dynamic_gke_folder

    elif [[ $LDAP_VOLUME_TYPE -eq 13 ]]; then
      create_static_gke
      static_volume_prompt="Persistent Disk Name"
      echo 'Place the name of your persistent disks between two quotes as such
        "gke-testinggluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd"'
      prompt_volumes_identitfier
      yaml_folder=$static_gke_folder
    fi
    prompt_zones
    gke_prompts
  elif [[ $DEPLOYMENT_ARCH -eq 5 ]]; then
    mkdir gluuaksyamls || emp_output
    output_yamls=gluuaksyamls
    if [[ $LDAP_VOLUME_TYPE -eq 16 ]]; then
      create_local_azure
      yaml_folder=$local_azure_folder
      generate_nfs

    elif [[ $LDAP_VOLUME_TYPE -eq 17 ]]; then
      if [[ ! "$VOLUME_TYPE" ]]; then
        echo "https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-types"
        echo "Please enter the volume type for the persistent disk. Example:UltraSSD_LRS,"
        echo "Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')"
        read -rp "[Premium_LRS] :                                                  " VOLUME_TYPE \
          && set_default "$VOLUME_TYPE" "Premium_LRS" "VOLUME_TYPE"
      fi
      create_dynamic_azure
      yaml_folder=$dynamic_azure_folder
      generate_nfs

    elif [[ $LDAP_VOLUME_TYPE -eq 18 ]]; then
      if [[ ! "$VOLUME_TYPE" ]]; then
        echo "https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-types"
        echo "Please enter the volume type for the persistent disk. Example:UltraSSD_LRS,"
        echo "Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')"
        read -rp "[Premium_LRS] :                                                  " VOLUME_TYPE \
          && set_default "$VOLUME_TYPE" "Premium_LRS" "VOLUME_TYPE"
      fi
      echo "Outputing available zones used : "
      create_static_azure
      static_volume_prompt="Persistent Disk Name"
      prompt_volumes_identitfier
      prompt_disk_uris
      yaml_folder=$static_azure_folder
      generate_nfs
    fi
    prompt_zones
  else
    mkdir gluumicrok8yamls || emp_output
    output_yamls=gluumicrok8yamls
    yaml_folder=$local_microk8s_folder
  fi
  # Get prams for the yamls
  prompt_storage
  prompt_replicas
  service_oxshibboleth=""
  service_passport=""
  service_oxd=""
  service_casa=""
  service_radius=""
  # Determine enabled services
  if [[ $ENABLE_OXSHIBBOLETH == "y" || $ENABLE_OXSHIBBOLETH == "Y" ]]; then
    service_oxshibboleth=" oxshibboleth"
  fi
  if [[ $ENABLE_OXPASSPORT == "y" || $ENABLE_OXPASSPORT == "Y" ]]; then
    service_passport=" oxpassport"
  fi
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    service_oxd=" oxd-server"
  fi
  if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
    service_casa=" casa"
  fi
  if [[ $ENABLE_RADIUS == "y" || $ENABLE_RADIUS == "Y" ]]; then
    service_radius=" radius"
  fi
  services="${service_oxshibboleth}${service_passport}${service_oxd}${service_casa}${service_radius} oxauth oxtrust"
  # Determine if FQDN status: If non registered patch, if registered unpatch
  if [[ $IS_GLUU_FQDN_REGISTERED == "y" ]] \
    || [[ $IS_GLUU_FQDN_REGISTERED == "Y" ]]; then
    for service in $services; do
      # Incase user has used updatelbip and switched kustmization source file
      cat $service/base/kustomization.yaml \
        | $sed -s "s@deployments-patch.yaml@deployments.yaml@g" \
        | $sed -s "s@statefulsets-patch.yaml@statefulsets.yaml@g" > tmpfile \
        && mv tmpfile $service/base/kustomization.yaml \
        || emp_output
    done
  else
    for service in $services; do
      cat $service/base/kustomization.yaml \
        | $sed -s "s@deployments.yaml@deployments-patch.yaml@g" \
        | $sed -s "s@statefulsets.yaml@statefulsets-patch.yaml@g" > tmpfile \
        && mv tmpfile $service/base/kustomization.yaml \
        || emp_output
    done
  fi
# Generate the yamls
  output_inital_yamls
  if [[ $IS_GLUU_FQDN_REGISTERED == "y" ]] \
    || [[ $IS_GLUU_FQDN_REGISTERED == "Y" ]]; then
    for service in $services; do
      # Remove hostAliases object from yamls
      cat $output_yamls/$service.yaml \
        | $sed '/LB_ADDR: LBADDR/d' \
        | $sed '/hostAliases:/d' \
        | $sed '/- hostnames:/d' \
        | $sed "/$GLUU_FQDN/d" \
        | $sed '/- command:/,/entrypoint.sh/d' \
        | $sed -s "s@  envFrom@- envFrom@g" \
        | $sed '/ip: NGINX_IP/d'> tmpfile \
        && mv tmpfile $output_yamls/$service.yaml \
        || emp_output
    done
    # Create dummy updatelbip
    $kubectl create configmap updatelbip --from-literal=demo=empty || emp_output
  else
    for service in $services; do
      if [[ DEPLOYMENT_ARCH -eq 1 ]] || \
         [[ DEPLOYMENT_ARCH -eq 2 ]] || \
         [[ DEPLOYMENT_ARCH -eq 4 ]] || \
         [[ DEPLOYMENT_ARCH -eq 5 ]]; then
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
  if [[ $DEPLOYMENT_ARCH -eq 2 ]]; then
    # If minikube ingress
    minikube addons enable ingress || emp_output
  fi
  # Nginx
  $kubectl apply -f $output_yamls/nginx/mandatory.yaml
  if [[ $DEPLOYMENT_ARCH -eq 3 ]]; then
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
      if [[ $USE_ARN == "Y" || $USE_ARN == "y" ]]; then
        cat $output_yamls/nginx/service-l7.yaml \
          | $sed -s "s@ARN_AWS_IAM@$ARN_AWS_IAM@g" > tmpfile \
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

  if [[ $DEPLOYMENT_ARCH -eq 4 ]] || [[ $DEPLOYMENT_ARCH -eq 5 ]]; then
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
  cat $output_yamls/nginx/nginx.yaml | $sed "s/\<FQDN\>/$GLUU_FQDN/" > tmpfile \
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
  if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
    $kubectl scale statefulset opendj --replicas=$LDAP_REPLICAS
    is_pod_ready "app=opendj"
  fi

}

deploy_shared_shib() {
  if [[ $DEPLOYMENT_ARCH -eq 4 ]] || [[ $DEPLOYMENT_ARCH -eq 5 ]]; then
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
  elif [[ $DEPLOYMENT_ARCH -eq 3 ]] \
    && [[ $OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE -eq 1 ]]; then
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
  $kubectl scale deployment oxauth --replicas=$OXAUTH_REPLICAS
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
  $kubectl scale deployment oxd-server --replicas=$OXD_SERVER_REPLICAS
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
  $kubectl scale deployment oxauth --replicas=$OXAUTH_REPLICAS
}

deploy_oxtrust() {
  cat $output_yamls/oxtrust.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxtrust.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxtrust.yaml || emp_output
  is_pod_ready "app=oxtrust"
  $kubectl scale statefulset oxtrust --replicas=$OXTRUST_REPLICAS
}

deploy_oxshibboleth() {
  cat $output_yamls/oxshibboleth.yaml \
    | $sed -s "s@NGINX_IP@$ip@g"  \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxshibboleth.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxshibboleth.yaml || emp_output
  is_pod_ready "app=oxshibboleth"
  $kubectl scale statefulset oxshibboleth --replicas=$OXSHIBBOLETH_REPLICAS
}

deploy_oxpassport() {
  cat $output_yamls/oxpassport.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/oxpassport.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/oxpassport.yaml || emp_output
  is_pod_ready "app=oxpassport"
  $kubectl scale deployment oxpassport --replicas=$OXPASSPORT_REPLICAS
}

deploy_key_rotation() {
  $kubectl apply -f $output_yamls/key-rotation.yaml || emp_output
  is_pod_ready "app=key-rotation"
}

deploy_radius() {
  cat $output_yamls/radius.yaml \
    | $sed -s "s@NGINX_IP@$ip@g" \
    | $sed "s/\<LBADDR\>/$hostname/" > tmpfile \
    && mv tmpfile $output_yamls/radius.yaml \
    || emp_output
  $kubectl apply -f $output_yamls/radius.yaml || emp_output
  is_pod_ready "app=radius"
  $kubectl scale deployment radius --replicas=$RADIUS_REPLICAS

}

deploy_cr_rotate() {
  $kubectl apply -f  $output_yamls/cr-rotate.yaml || emp_output
}

deploy() {
  ls $output_yamls || true
  if [[ ! "$DEPLOY_GENERATED_YAMLS" ]]; then
    read -rp "Deploy the generated yamls? [Y][Y/n]                                " DEPLOY_GENERATED_YAMLS \
      && set_default "$DEPLOY_GENERATED_YAMLS" "Y" "DEPLOY_GENERATED_YAMLS"
  fi
  case "$DEPLOY_GENERATED_YAMLS" in
    y|Y ) ;;
    n|N ) exit 1 ;;
    * )   ;;
  esac
  prompt_cb
  # Writing all vars and vlaues to installation-variables
  output_prompt_var_values
  deploy_shared_shib
  $kubectl create secret generic cb-pass --from-file=couchbase_password || true
  $kubectl create secret generic cb-crt --from-file=couchbase.crt || true
  if [[ $DEPLOY_MULTI_CLUSTER != "Y" && $DEPLOY_MULTI_CLUSTER != "y" && $deployConfig != "N" ]]; then
    deploy_config
  fi
  setup_tls
  if [[ $CACHE_TYPE == 2 ]];then
    deploy_redis
  fi
  # If hybrid or just ldap
  if [[ $PERSISTENCE_BACKEND -eq 0 ]] || [[ $PERSISTENCE_BACKEND -eq 2 ]]; then
    deploy_ldap
  fi
  deploy_nginx
  deploy_persistence
  if [[ $IS_GLUU_FQDN_REGISTERED != "y" ]] && [[ $IS_GLUU_FQDN_REGISTERED != "Y" ]]; then
    deploy_update_lb_ip
  fi
  deploy_oxauth
  if [[ $choiceOXD == "y" || $choiceOXD == "Y" ]]; then
    deploy_oxd
  fi
    # Casa
  if [[ $ENABLE_CASA == "y" || $ENABLE_CASA == "Y" ]]; then
    deploy_casa
  else
    $kubectl delete pvc -l app=casa --ignore-not-found || emp_output
    $kubectl delete pv -l app=casa --ignore-not-found || emp_output
  fi
  deploy_oxtrust
  if [[ $ENABLE_OXSHIBBOLETH == "y" || $ENABLE_OXSHIBBOLETH == "Y" ]]; then
    # oxShibboleth
    deploy_oxshibboleth
  fi
  if [[ $ENABLE_OXPASSPORT == "y" || $ENABLE_OXPASSPORT == "Y" ]]; then
    deploy_oxpassport
  fi
  if [[ $ENABLE_CACHE_REFRESH == "y" || $ENABLE_CACHE_REFRESH == "Y" ]]; then
    deploy_cr_rotate
  fi
  if [[ $ENABLE_KEY_ROTATE == "y" || $ENABLE_KEY_ROTATE == "Y" ]]; then
    deploy_key_rotation
  fi
  if [[ $ENABLE_RADIUS == "y" || $ENABLE_RADIUS == "Y" ]]; then
    # Radius server
    deploy_radius
  fi
}

# ==========
# entrypoint
# ==========

case $1 in
  "install"|"")
    emp_prompt_vars
    if [ -f installation-variables ] || [ -s installation-variables ]; then
      read -rp "Installation settings have been found. Would you like to use it? [N][Y/n]                                " USE_INSTALLATION_VARIABLES
      case "$USE_INSTALLATION_VARIABLES" in
        y|Y ) source installation-variables ;;
        * ) ;;
      esac
    fi
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
