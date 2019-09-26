#!/bin/bash

set -e
# version >= V1.14 
#Set folders
local_aws_folder="overlays/aws/local-storage/"
dynamic_aws_folder="overlays/aws/dynamic-ebs/"
dynamic_gke_folder="overlays/gke/dynamic-pd/"
static_aws_folder="overlays/aws/static-ebs/"
local_gke_folder="overlays/gke/local-storage/"
local_minikube_folder="overlays/minikube/local-storage/"
local_microk8s_folder="overlays/microk8s/local-storage/"
static_gke_folder="overlays/gke/static-pd/"

emp_output(){
    echo "" > /dev/null 
}

delete_all(){
    kubectl=kubectl
    $kubectl delete -f localawsyamls || emp_output
	$kubectl delete -f dynamicawsyamls || emp_output
	$kubectl delete -f localgkeyamls || emp_output
    $kubectl delete -f dynamicgkeyamls || emp_output
    $kubectl delete -f staticgkeyamls || emp_output
	$kubectl delete -f staticawsyamls || emp_output
	$kubectl delete -f localminikubeyamls || emp_output
    $kubectl delete -f localmicrok8syamls || emp_output
    $kubectl delete cm gluu || emp_output
	$kubectl delete --namespace default --all pv,pvc,cm || emp_output
    $kubectl delete secret gluu tls-certificate cb-pass cb-crt || emp_output
    $kubectl delete -f nginx/ || emp_output
	echo "Trying to delete folders created at other nodes. This assumes your ssh is ~/.ssh/id_rsa "
	# Loops through the IPs of the nodes and delets /data
	for OUTPUT in $($kubectl get nodes -o template --template='{{range.items}}{{range.status.addresses}}{{if eq .type "ExternalIP"}}{{.address}}{{end}}{{end}} {{end}}' || echo "")
	do
	ssh -oStrictHostKeyChecking=no -i ~/.ssh/id_rsa  ec2-user@"$OUTPUT" sudo rm -rf /data || emp_output
	done
	rm -rf /data || emp_output
}

create_dynamic_gke(){
	mkdir dynamicgkeyamls || emp_output
	for service in "config" "ldap" "oxauth" "oxd-server" "oxtrust" "radius"
	do
	    dynamicgkefolder="$service/overlays/gke/dynamic-pd"
	    cp -r $service/overlays/aws/dynamic-ebs $dynamicgkefolder
	    cat $dynamicgkefolder/storageclasses.yaml | sed -s "s@kubernetes.io/aws-ebs@kubernetes.io/gce-pd@g" | sed '/zones/d' | sed '/encrypted/d' > tmpfile && mv tmpfile $dynamicgkefolder/storageclasses.yaml || emp_output
		rm $dynamicgkefolder/deployments.yaml || emp_output 
		if [[ $service == "oxtrust" ]]; then
		    rm $dynamicgkefolder/statefulsets.yaml || emp_output
	        cat $dynamicgkefolder/kustomization.yaml | sed '/- statefulsets.yaml/d' | sed '/patchesStrategicMerge:/d' > $dynamicgkefolder/kustomization.yaml || emp_output
		fi
        if [[ $service == "oxauth" || $service == "radius"  ]]; then
        cat $dynamicgkefolder/kustomization.yaml | sed '/- deployments.yaml/d' | sed '/patchesStrategicMerge:/d' > $dynamicgkefolder/kustomization.yaml || emp_output
		fi
	done
    #Config
	cp config/overlays/gke/local-storage/cluster-role-bindings.yaml config/overlays/gke/dynamic-pd
    printf  "\n  - cluster-role-bindings.yaml" >> config/overlays/gke/dynamic-pd/kustomization.yaml
}

create_minikube(){
	mkdir localminikubeyamls || emp_output
	for service in "config" "ldap" "oxauth" "oxd-server" "oxpassport" "oxshibboleth" "oxtrust" "radius"
	do
	    localminikubefolder="$service/overlays/minikube"
	    cp -r $service/overlays/microk8s $localminikubefolder
	done
    #shared-shib
	cp -r shared-shib/microk8s shared-shib/minikube
}
create_static_gke(){
	mkdir staticgkeyamls || emp_output
	for service in "config" "ldap" "oxauth" "oxd-server" "oxtrust" "radius"
	do
	    staticgkefolder="$service/overlays/gke/static-pd"
		service_name=$(echo "${service^^}VOLUMEID" | tr --delete -)
	    cp -r $service/overlays/aws/local-storage $service/overlays/gke/static-pd
	    cat $staticgkefolder/persistentvolumes.yaml | sed '/hostPath/d' | sed '/path/d' | sed '/type/d' > tmpfile && mv tmpfile $staticgkefolder/persistentvolumes.yaml || emp_output
        printf  "  gcePersistentDisk:" >> $staticgkefolder/persistentvolumes.yaml
        printf  "\n    pdName: $service_name" >> $staticgkefolder/persistentvolumes.yaml
        printf  "\n    fsType: ext4" >> $staticgkefolder/persistentvolumes.yaml
	done
}

replace_all(){
	 sed "s/\<PERSISTENCETYPE\>/$PERSISTENCE_TYPE/" \
	 | sed "s/\<LDAPMAPPING\>/$LDAP_MAPPING/" \
	 | sed "s/\<COUCHBASEURL\>/$COUCHBASE_URL/" \
	 | sed "s/\<CBUSER\>/$CB_USER/" \
	 | sed -s "s@STORAGESHAREDSHIB@$STORAGE_SHAREDSHIB@g" \
	 | sed -s "s@SCSHAREDSHIBZONE@$SC_SHAREDSHIB_ZONE@g" \
	 | sed -s "s@CONFIGVOLUMEID@$CONFIG_VOLUMEID@g" \
	 | sed -s "s@HOME_DIR@$HOME_DIR@g" \
	 | sed -s "s@STORAGECONFIG@$STORAGE_CONFIG@g" \
	 | sed "s#ACCOUNT#$ACCOUNT#g" \
	 | sed -s "s@SCCONFIGZONE@$SC_CONFIG_ZONE@g" \
	 | sed -s "s@LDAPVOLUMEID@$LDAP_VOLUMEID@g" \
	 | sed -s "s@STORAGELDAP@$STORAGE_LDAP@g" \
	 | sed -s "s@SCLDAPZONE@$SC_LDAP_ZONE@g" \
	 | sed "s/\<FQDN\>/$FQDN/" \
	 | sed -s "s@OXAUTHVOLUMEID@$OXAUTH_VOLUMEID@g" \
	 | sed -s "s@STORAGEOXAUTH@$STORAGE_OXAUTH@g" \
	 | sed -s "s@SCOXAUTHZONE@$SC_OXAUTH_ZONE@g" \
	 | sed -s "s@OXTRUSTVOLUMEID@$OXTRUST_VOLUMEID@g" \
	 | sed -s "s@STORAGEOXTRUST@$STORAGE_OXTRUST@g" \
	 | sed -s "s@SCOXTRUSTZONE@$SC_OXTRUST_ZONE@g" \
	 | sed -s "s@OXDSERVERVOLUMEID@$OXDSERVER_VOLUMEID@g" \
	 | sed -s "s@STORAGEOXDSERVER@$STORAGE_OXDSERVER@g" \
	 | sed -s "s@SCOXDSERVERZONE@$SC_OXDSERVER_ZONE@g" \
	 | sed -s "s@RADIUSVOLUMEID@$RADIUS_VOLUMEID@g" \
	 | sed -s "s@STORAGERADIUS@$STORAGE_RADIUS@g" \
	 | sed -s "s@SCRADIUSZONE@$SC_RADIUS_ZONE@g" \
	 | sed -s "s@VOLUMETYPE@$VOLUME_TYPE@g"
}

setup_tls(){
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

    $kubectl create secret tls tls-certificate --key ingress.key --cert ingress.crt
}

is_pod_complete() {
    #TODO: Add logic if its deployed on minikube or microk8s or on cloud then change timeout
   timeout="5 minute"
   endtime=$(date -ud "$timeout" +%s)
   while [[ "$($kubectl get pods -l "$1" -o 'jsonpath={..status.conditions[].reason}')" != "PodCompleted" ]] && [[ $(date -u +%s) -le $endtime ]]; do 
   echo "[I] Waiting for $1 to complete" && sleep 20; done
}
is_pod_ready() {
    #TODO: Add logic if its deployed on minikube or microk8s or on cloud then change timeout
   timeout="5 minute"
   endtime=$(date -ud "$timeout" +%s)
   while [[ "$($kubectl get pods -l "$1" -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}')" != "True" ]] && [[ $(date -u +%s) -le $endtime ]]; do 
   echo "[I] Waiting for $1 to get ready" && sleep 20; done
}
check_k8version() {
    kustomize="$kubectl kustomize"
    kubectl_version=$("$kubectl" version -o json | jq -r '.clientVersion.minor')
	kubectl_version=$(echo "$kubectl_version" | tr --delete +)
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
    curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest |\
      grep browser_download |\
      grep $opsys |\
      cut -d '"' -f 4 |\
      xargs curl -O -L
    mv kustomize_*_${opsys}_amd64 kustomize
    chmod u+x kustomize
}

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
        HOST_IP=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
    elif [[ $machine == Mac ]]; then
        HOST_IP=$(ipconfig getifaddr en0)
    else
        echo "Cannot determine IP address."
        read -rp "Please input the hosts external IP Address: " HOST_IP
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
    read -rp "Is this the correct external IP Address: ${HOST_IP} [Y/n]? " cont
    case "$cont" in
        y|Y)
            return 0
            ;;
        n|N)
            read -rp "Please input the hosts external IP Address: " HOST_IP
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

prepare_config() {
    choiceDeploy=6
	echo "[0] Exit"
	echo "[1] AWS      | Volumes on host"
	echo "[2] AWS      | EBS volumes dynamically provisioned"
	echo "[3] GKE      | Volumes on host"
	echo "[4] AWS      | EBS volumes statically provisioned"
	echo "[5] Minikube | Volumes on host"
	echo "[6] Microk8s | Volumes on host"
	echo "[7] GKE      | Persistent Disk volumes dynamically provisioned"
	echo "[8] GKE      | Persistent Disk volumes statically provisioned"
	echo  "Any other option will default to choice 6 "
	choiceCR="N"
	choiceKeyRotate="N"
	choiceOXD="N"
	choiceRadius="N"
	choicePassport="N"
	
	read -rp "What type of deployment " choiceDeploy
	echo "[0] WrenDS [default]"
	echo "[1] Couchbase [Testing Phase]"
	echo "[2] Hybrid(WrenDS + Couchbase)[Testing Phase]"
	read -rp "Persistence type? " choicePersistence
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
		echo "[0] Default" 
	    echo "[1] User" 
	    echo "[2] Site"
	    echo "[3] Cache"
	    echo "[4] Token"
	    read -rp "Persistence type? " choiceHybrid
        case "$choiceHybrid" in
            1 ) LDAP_MAPPING="user"  ;;
            2 ) LDAP_MAPPING="site"  ;;
            3 ) LDAP_MAPPING="cache" ;;
            4 ) LDAP_MAPPING="token"  ;;
            * ) LDAP_MAPPING="default"  ;;
        esac
	fi
    if [[ $choicePersistence -ge 1 ]]; then
	    if [ ! -f couchbase.crt ] || [ ! -s couchbase.crt ]; then
            echo "There is no crt inside couchbase.crt for couchbase. Please create a file named couchbase.crt and past the certification found in your couchbase UI Security > Root Certificate inside it."
			exit 1
        fi
	    read -rp "Please enter remote couchbase username                           " CB_USER
	    read -rp "Please enter remote couchbase URL base name, couchbase.gluu.org  " COUCHBASE_URL
		#TODO: Add test CB connection
		while true; do
            echo "Enter remote couchbase Password:"
            mask_password
            CB_PW=$password
            echo "Confirm remote couchbase Password:"
            mask_password
            CB_PW_CM=$password
            [ "$CB_PW" = "$CB_PW_CM" ] && break || echo "Please try again"
        done

        case "$CB_PW" in
            * ) ;;
            "") echo "Password cannot be empty"; exit 1;
        esac
		echo "$CB_PW" > couchbase_password
	fi
	if [[ $choiceDeploy -eq 6 ]]; then
	kubectl=microk8s.kubectl
	else
	    kubectl=kubectl
	fi
	check_k8version
	if [[ $choiceDeploy -eq 5 ]] || [[ $choiceDeploy -eq 6 ]]; then
	    gather_ip
		until confirm_ip; do : ; done
	    ip=$HOST_IP	    
	else
	    # Assign random IP. IP will be changed by either the update ip script or by GKE external ip
		ip=22.22.22.22
	fi
	read -rp "Deploy Cr-Rotate[N]?[Y/N]      " choiceCR
	read -rp "Deploy Key-Rotation{N]?[Y/N]   " choiceKeyRotate
	read -rp "Deploy Radius[N]?[Y/N]         " choiceRadius
	read -rp "Deploy Passport[N]?[Y/N]       " choicePassport
	read -rp "Deploy OXD-Server[N]?[Y/N]     " choiceOXD
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
	    read -rp "[I] Use pervious params? [Y/n]" param_choice
        if [[ $param_choice != "y" && $param_choice != "Y" ]]; then
            generate=1			
        fi
    fi
    # config is not loaded from previously saved configuration
    if [[ $generate -eq 1 ]]; then
	    echo "[I] Removing all previous gluu services if found"
		#delete_all
        echo "[I] Creating new configuration, please input the following parameters"
        read -rp "Enter Hostname (demoexample.gluu.org):           " FQDN
        if ! [[ $FQDN == *"."*"."* ]]; then
            echo "[E] Hostname provided is invalid. Please enter a FQDN with the format demoexample.gluu.org"
            exit 1
        fi
        read -rp "Enter Country Code:                              " COUNTRY_CODE
        read -rp "Enter State:                                     " STATE
        read -rp "Enter City:                                      " CITY
        read -rp "Enter Email:                                     " EMAIL
        read -rp "Enter Organization:                              " ORG_NAME
		while true; do
			echo "Enter Gluu Admin/LDAP Password:"
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
	    read -rp "Please confirm your FQDN        " FQDN
    fi
}

prompt_zones(){
    #output the zones out to the user
    echo "You will be asked to enter a zone for each service. Please confine the zones to where your nodes zones are which are the following: "
    $kubectl get nodes -o json | jq '.items[] | .metadata .labels["failure-domain.beta.kubernetes.io/zone"]'		
	read -rp "Config storage class zone:                               " SC_CONFIG_ZONE
	if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
		 read -rp "Ldap storage class zone:                                " SC_LDAP_ZONE
	fi
	read -rp "oxAuth storage class zone:                               " SC_OXAUTH_ZONE
	if [[ $choiceOXD != "n" && $choiceOXD != "N" ]]; then
	# OXD server
	read -rp "oxdServer storage class zone:                            " SC_OXDSERVER_ZONE
	fi
	read -rp "oxTrust storage class zone:                              " SC_OXTRUST_ZONE
	if [[ $choiceRadius != "n" && $choiceRadius != "N" ]]; then
	# Radius server
	read -rp "Radius storage class zone:                               " SC_RADIUS_ZONE
	fi
	if [[ $choiceDeploy -ne 3 && $choiceDeploy -ne 7  ]]; then
	    read -rp "Shared-Shib storage class zone:                          " SC_SHAREDSHIB_ZONE
    fi
}

prompt_storage(){
	read -rp "Size of config volume storage [Cloud min 1Gi]:             " STORAGE_CONFIG
	if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
	    read -rp "Size of ldap volume storage [Cloud min 1Gi]:               " STORAGE_LDAP
    fi
	read -rp "Size of oxAuth volume storage [Cloud min 1Gi]:             " STORAGE_OXAUTH
    read -rp "Size of oxTrust volume storage [Cloud min 1Gi]:            " STORAGE_OXTRUST
	if [[ $choiceRadius != "n" && $choiceRadius != "N" ]]; then
	# Radius Volume storage
    read -rp "Size of Radius volume storage [Cloud min 1Gi]:             " STORAGE_RADIUS
	fi
	if [[ $choiceDeploy -ne 3 && $choiceDeploy -ne 7 && $choiceDeploy -ne 8 ]]; then
	    read -p "Size of Shared-Shib volume storage [Cloud min 1Gi]:        " STORAGE_SHAREDSHIB
	fi
	if [[ $choiceOXD != "n" && $choiceOXD != "N" ]]; then
	    # OXD server
        read -rp "Size of oxdServer volume storage [Cloud min 1Gi]:      " STORAGE_OXDSERVER
	fi
}

gke_prompts() {
    oxpassport_oxshibboleth_folder="overlays/gke"
	read -rp "Please enter valid email for Google Cloud account:             " ACCOUNT
	read -rp "Please enter valid Zone name used when creating the cluster:   " ZONE
	SC_LDAP_ZONE=$ZONE
	echo "Trying to login user"
	NODE=$(kubectl get no -o go-template='{{range .items}}{{.metadata.name}} {{end}}' | awk -F " " '{print $1}')
	
	HOME_DIR=$(gcloud compute ssh root@$NODE --zone $ZONE --command='echo $HOME' || echo "Permission denied")
	if [[ $HOME_DIR =~ "Permission denied" ]];then
		echo "This occurs when your compute instance has PermitRootLogin set to  no in it's SSHD config. Trying to login using user"
		HOME_DIR=$(gcloud compute ssh user@$NODE --zone $ZONE --command='echo $HOME')
	fi
	$kustomize nfs/base/ > $output_yamls/nfs.yaml
	read -rp "NFS storage volume:           " STORAGE_NFS
}

prompt_volumes_identitfier() {
	read -rp "Please enter $static_volume_prompt for Config:                             " CONFIG_VOLUMEID
	if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
		read -rp "Please enter $static_volume_prompt for LDAP:                               " LDAP_VOLUMEID
	fi		
	read -rp "Please enter $static_volume_prompt for oxAuth:                             " OXAUTH_VOLUMEID
	if [[ $choiceOXD != "n" && $choiceOXD != "N" ]]; then
		# OXD server
		read -rp "Please enter $static_volume_prompt for OXD-server:                     " OXDSERVER_VOLUMEID
	fi
	read -rp "Please enter $static_volume_prompt for oxTrust:                            " OXTRUST_VOLUMEID
	if [[ $choiceRadius != "n" && $choiceRadius != "N" ]]; then
		# Radius server
		read -rp "Please enter $static_volume_prompt for Radius:                             " RADIUS_VOLUMEID
	fi
}
generate_yamls() {
    FQDN_CHOICE="Y"
	read -rp "Are you using a globally resolvable FQDN [Y] [Y/N]:       " FQDN_CHOICE
	if [[ $FQDN_CHOICE != "n" && $FQDN_CHOICE != "N" ]]; then
		echo "Please place your FQDN certification and key inside ingress.crt and ingress.key respectivley."
		if [ ! -f ingress.crt ] || [ ! -s ingress.crt ] || [ ! -f ingress.key ] || [ ! -s ingress.key ]; then
			echo "Check that  ingress.crt and ingress.key are not empty and contain the right information for your FQDN. "
			exit 1
		fi		
	fi	
    oxpassport_oxshibboleth_folder="overlays/aws"
    if [[ $choiceDeploy -eq 0 ]]; then
	    exit 1
	elif [[ $choiceDeploy -eq 1 ]]; then
	    mkdir localawsyamls || emp_output
		output_yamls=localawsyamls
	    yaml_folder=$local_aws_folder
        # Shared-Shib
		shared_shib_child_folder="aws"
    elif [[ $choiceDeploy -eq 2 ]]; then
	    echo "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html"
		echo "Follow the doc above to help you choose which volume type to use.Options are [gp2,io1,st1,and sc1]"
		read -rp "Please enter the volume type for EBS.Example:gp2    : " VOLUME_TYPE
	    mkdir dynamicawsyamls || emp_output
	    output_yamls=dynamicawsyamls
	    yaml_folder=$dynamic_aws_folder
        prompt_zones
		shared_shib_child_folder="aws"
    elif [[ $choiceDeploy -eq 3 ]]; then
	    mkdir localgkeyamls || emp_output
		output_yamls=localgkeyamls
	    yaml_folder=$local_gke_folder
		gke_prompts

    elif [[ $choiceDeploy -eq 4 ]]; then
		mkdir staticawsyamls || emp_output
	    output_yamls=staticawsyamls
	    yaml_folder=$static_aws_folder
		echo "Zones of your volumes are required to match the deployments to the volume zone"
		prompt_zones
		static_volume_prompt="AWS Volume ID"
		prompt_volumes_identitfier
		shared_shib_child_folder="aws"
    elif [[ $choiceDeploy -eq 5 ]]; then
	    create_minikube
	    output_yamls=localminikubeyamls
	    yaml_folder=$local_minikube_folder
		shared_shib_child_folder="minikube"
	elif [[ $choiceDeploy -eq 7 ]]; then
        read -rp "Please enter the volume type for the persistent disk Options are [pd-standard, pd-ssd]. Example:pd-standard,    : " VOLUME_TYPE
	    create_dynamic_gke
		output_yamls=dynamicgkeyamls
	    yaml_folder=$dynamic_gke_folder
		gke_prompts
	elif [[ $choiceDeploy -eq 8 ]]; then
	    create_static_gke
		output_yamls=staticgkeyamls
		static_volume_prompt="Persistent Disk Name"
		echo 'Place the name of your persistent disks between two quotes as such "gke-testinggluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd"'
		prompt_volumes_identitfier
	    yaml_folder=$static_gke_folder
		gke_prompts
    else
	    mkdir localmicrok8syamls || emp_output
	    output_yamls=localmicrok8syamls
        yaml_folder=$local_microk8s_folder
		shared_shib_child_folder="microk8s"
	fi
    # Get prams for the yamls
    prompt_storage
	if [[ $choiceDeploy -ne 3 && $choiceDeploy -ne 7 && $choiceDeploy -ne 8 ]]; then
	    $kustomize shared-shib/$shared_shib_child_folder/ | replace_all  > $output_yamls/shared-shib.yaml
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
    $kustomize oxshibboleth/$oxpassport_oxshibboleth_folder | replace_all  > $output_yamls/oxshibboleth.yaml
	if [[ $choicePassport != "n" && $choicePassport != "N" ]]; then
	# oxPassport
    $kustomize oxpassport/$oxpassport_oxshibboleth_folder | replace_all  > $output_yamls/oxpassport.yaml
	fi
	if [[ $choiceCR != "n" && $choiceCR != "N" ]]; then
	# Key Rotationls
    $kustomize key-rotation/base | replace_all > $output_yamls/key-rotation.yaml
	fi
	if [[ $choiceRotate != "n" && $choiceRotate != "N" ]]; then
	# Cache Refresh rotating IP registry
    $kustomize cr-rotate/base | replace_all > $output_yamls/cr-rotate.yaml
	fi
    # OXD-Server
	if [[ $choiceOXD != "n" && $choiceOXD != "N" ]]; then
	    $kustomize oxd-server/$yaml_folder | replace_all > $output_yamls/oxd-server.yaml
	fi
	# Radius
	if [[ $choiceRadius != "n" && $choiceRadius != "N" ]]; then
		# Radius server
	    $kustomize radius/$yaml_folder | replace_all > $output_yamls/radius.yaml
	fi	
	if [[ $FQDN_CHOICE != "y" && $FQDN_CHOICE != "Y" ]]; then
	    $kustomize update-lb-ip/base > $output_yamls/updatelbip.yaml
	else
		# Remove hostAliases object from yamls
	    cat $output_yamls/oxauth.yaml | sed '/LB_ADDR: LBADDR/d' | sed '/hostAliases:/d' | sed '/- hostnames:/d' | sed "/$FQDN/d" | sed '/ip: NGINX_IP/d' > tmpfile && mv tmpfile $output_yamls/oxauth.yaml || emp_output
		cat $output_yamls/oxpassport.yaml | sed '/LB_ADDR: LBADDR/d' | sed '/hostAliases:/d' | sed '/- hostnames:/d' | sed "/$FQDN/d" | sed '/ip: NGINX_IP/d' > tmpfile && mv tmpfile $output_yamls/oxpassport.yaml || emp_output
		cat $output_yamls/oxshibboleth.yaml | sed '/LB_ADDR: LBADDR/d' | sed '/hostAliases:/d' | sed '/- hostnames:/d' | sed "/$FQDN/d" | sed '/ip: NGINX_IP/d' > tmpfile && mv tmpfile $output_yamls/oxshibboleth.yaml || emp_output
		cat $output_yamls/oxtrust.yaml | sed '/LB_ADDR: LBADDR/d' | sed '/hostAliases:/d' | sed '/- hostnames:/d' | sed "/$FQDN/d" | sed '/ip: NGINX_IP/d' > tmpfile && mv tmpfile $output_yamls/oxtrust.yaml || emp_output
		cat $output_yamls/radius.yaml | sed '/LB_ADDR: LBADDR/d' | sed '/hostAliases:/d' | sed '/- hostnames:/d' | sed "/$FQDN/d" | sed '/ip: NGINX_IP/d' > tmpfile && mv tmpfile $output_yamls/radius.yaml || emp_output
    fi 	
	echo " all yamls have been generated in $output_yamls folder"
}

deploy_nginx(){
    # If microk8s ingress
	microk8s.enable ingress dns || emp_output
	# If minikube ingress
	minikube addons enable ingress || emp_output
    # Nginx	
	$kubectl apply -f nginx/mandatory.yaml
	if [[ $choiceDeploy -eq 1 ]] || [[ $choiceDeploy -eq 2 ]] || [[ $choiceDeploy -eq 4 ]]; then
		$kubectl apply -f nginx/service-l4.yaml 
	    $kubectl apply -f nginx/patch-configmap-l4.yaml
		#AWS
		echo "Waiting for loadbalancer address.."
	    sleep 30
	fi
    #AWS
	lbhostname=$($kubectl -n ingress-nginx get svc ingress-nginx --output jsonpath='{.status.loadBalancer.ingress[0].hostname}' || echo "")
	hostname="'${lbhostname}'" || emp_output 
	if [[ $choiceDeploy -eq 3  || $choiceDeploy -eq 7 || $choiceDeploy -eq 8 ]]; then
	    $kubectl apply -f nginx/cloud-generic.yaml
		$kubectl apply -f nfs/base/services.yaml
	    ip=""
        echo "Waiting for the ip of the Loadbalancer"
	    while true; do
	    if [[ $ip ]]; then
		    break
	    fi
		#GKE get external IP
	    ip=$($kubectl -n ingress-nginx get svc ingress-nginx --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
	    sleep 20
	    done
		echo "IP: $ip"
	fi
	cat nginx/nginx.yaml | sed "s/\<FQDN\>/$FQDN/" | $kubectl apply -f -    
}
deploy_config(){
    # Config
    cat $output_yamls/config.yaml | $kubectl apply -f -
    is_pod_complete "app=config-init-load"
}
deploy_ldap(){
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
deploy_persistence(){
	# Persistence
	cat $output_yamls/persistence.yaml | $kubectl apply -f -
	echo "Trying to import ldifs..."
	is_pod_complete "app=persistence-load"
	while true; do
	  persistencelog=$($kubectl logs -l app=persistence-load || emp_output)
	  # Use the below when you want the output not to contain some string
	  if [[ $persistencelog =~ "Importing o_metric.ldif file" ]]; then
		break
	  fi
	  sleep 30
	done
}
deploy_shared_shib(){
	if [[ $choiceDeploy -eq 3 || $choiceDeploy -eq 7 || $choiceDeploy -eq 8 ]]; then
		NFS_IP=""
	    while true; do
	    if [[ $NFS_IP ]] ; then
		    break
	    fi
		NFS_IP=$($kubectl get svc nfs-server --output jsonpath='{.spec.clusterIP}')
		#AWS
	    #ip=$(dig +short "$lbhostname" || true)
	    sleep 30
	    done
		# setup NFS
		cat $output_yamls/nfs.yaml | sed -s "s@STORAGENFS@$STORAGE_NFS@g" | sed -s "s@NFSIP@$NFS_IP@g" | $kubectl apply -f -
        is_pod_ready "role=nfs-server"
		$kubectl exec -ti $($kubectl get pods -l role=nfs-server -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}') -- mkdir -p /exports/opt/shared-shibboleth-idp
	else
	    cat $output_yamls/shared-shib.yaml  | $kubectl apply -f - || emp_output
	fi
}
deploy_update_lb_ip(){
	# Update LB 
	$kubectl apply -f $output_yamls/updatelbip.yaml || emp_output
}
deploy_oxauth(){
	cat $output_yamls/oxauth.yaml | sed -s "s@NGINX_IP@$ip@g" | sed "s/\<LBADDR\>/$hostname/" | $kubectl apply -f -
	is_pod_ready "app=oxauth"
}
deploy_oxd(){
	# OXD server
	cat $output_yamls/oxd-server.yaml | $kubectl apply -f - || emp_output
	is_pod_ready "app=oxd-server"
}
deploy_oxtrust(){
	cat $output_yamls/oxtrust.yaml | sed -s "s@NGINX_IP@$ip@g" | sed "s/\<LBADDR\>/$hostname/" | $kubectl apply -f -
	is_pod_ready "app=oxtrust"
}
deploy_oxshibboleth(){
	cat $output_yamls/oxshibboleth.yaml | sed -s "s@NGINX_IP@$ip@g"  | sed "s/\<LBADDR\>/$hostname/" | $kubectl apply -f -
	is_pod_ready "app=oxshibboleth"
}
deploy_oxpassport(){
	cat $output_yamls/oxpassport.yaml | sed -s "s@NGINX_IP@$ip@g" | sed "s/\<LBADDR\>/$hostname/" | $kubectl apply -f -
	is_pod_ready "app=oxpassport"
}
deploy_key_rotation(){
	$kubectl apply -f $output_yamls/key-rotation.yaml || emp_output
	is_pod_ready "app=key-rotation"
}
deploy_radius(){
    cat $output_yamls/radius.yaml | sed -s "s@NGINX_IP@$ip@g" | sed "s/\<LBADDR\>/$hostname/" | $kubectl apply -f - || emp_output
    is_pod_ready "app=radius"
}
deploy_cr_rotate(){
	$kubectl apply -f  $output_yamls/cr-rotate.yaml || emp_output
}
deploy() {
    ls $output_yamls || true
    read -rp "Deploy the generated yamls? [Y/n]" choiceContDeploy
	case "$choiceContDeploy" in
		y|Y ) ;;
		n|N ) exit 1 ;;
		* )   ;;
    esac
	$kubectl create secret generic cb-pass --from-file=couchbase_password || true
	$kubectl create secret generic cb-crt --from-file=couchbase.crt || true
    deploy_config
	setup_tls
	# If hybrid or just ldap
	if [[ $choicePersistence -eq 0 ]] || [[ $choicePersistence -eq 2 ]]; then
	    deploy_ldap
    fi
	deploy_nginx
	deploy_persistence
    deploy_update_lb_ip
	deploy_oxauth
	if [[ $choiceOXD != "n" && $choiceOXD != "N" ]]; then
	    deploy_oxd
    fi
	deploy_shared_shib
    deploy_oxtrust
    deploy_oxshibboleth
    deploy_oxpassport
	deploy_key_rotation
    deploy_cr_rotate
	deploy_radius
}
# ==========
# entrypoint
# ==========
case $1 in
    "install"|"")
	    touch couchbase.crt
		touch couchbase_password
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