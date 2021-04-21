#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install python3-pip -y
sudo pip3 install pip --upgrade
sudo pip3 install setuptools --upgrade
sudo pip3 install pyOpenSSL --upgrade
sudo apt-get update
sudo apt-get install build-essential unzip -y
sudo pip3 install requests --upgrade
sudo pip3 install shiv
sudo snap install microk8s --classic
sudo microk8s.status --wait-ready
sudo microk8s.enable dns registry ingress
sudo microk8s kubectl get daemonset.apps/nginx-ingress-microk8s-controller -n ingress -o yaml | sed -s "s@ingress-class=public@ingress-class=nginx@g" | microk8s kubectl apply -f -
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install net-tools
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
sudo microk8s config > config
KUBECONFIG="$PWD"/config
sudo microk8s.kubectl create namespace gluu --kubeconfig="$KUBECONFIG" || echo "namespace exists"
sudo helm repo add bitnami https://charts.bitnami.com/bitnami
sudo microk8s.kubectl get po --kubeconfig="$KUBECONFIG"
sudo helm install my-release --set auth.rootPassword=Test1234#,auth.database=jans bitnami/mysql -n gluu --kubeconfig="$KUBECONFIG"
# Create and patch certs and keys. This will also generate the client crt and key to be used to access protected endpoints
mkdir certs
cd certs
wget https://raw.githubusercontent.com/GluuFederation/cloud-native-edition/master/pygluu/kubernetes/pycert.py
wget https://raw.githubusercontent.com/GluuFederation/cloud-native-edition/master/pygluu/kubernetes/helpers.py
sudo sed -i 's/from pygluu.kubernetes.helpers import get_logger/from helpers import get_logger/g' pycert.py
cat << EOF > generate.py
from pycert import setup_crts
setup_crts("Gluu Openbanking CA", "gluu-openbanking", ["demoexample.gluu.org"], key_file="./server.key")
EOF
sudo python3 generate.py
# load the certificate into a variable
sudo sed -ne '
   /-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p
   /-END CERTIFICATE-/q
' $PWD/chain.pem > server.crt
sudo openssl req -new -newkey rsa:4096 -keyout client.key -out client.csr -nodes -subj '/CN=Openbanking'
sudo openssl x509 -req -sha256 -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt
sudo microk8s.kubectl create secret generic cn -n gluu --from-file=ssl_cert=server.crt --from-file=ssl_key=server.key --kubeconfig="$KUBECONFIG"
sudo microk8s kubectl create secret generic ca-secret -n gluu --from-file=tls.crt=server.crt --from-file=tls.key=server.key --from-file=ca.crt=ca.crt --kubeconfig="$KUBECONFIG"
cd ..
# done with cert and key job
sudo helm repo add gluu https://gluufederation.github.io/cloud-native-edition/pygluu/kubernetes/templates/helm
sudo helm repo update
sudo helm install gluu gluu/gluu -n gluu --version=5.0.0 --set config.configmap.cnSqlDbHost="my-release-mysql.gluu.svc" --set global.provisioner="microk8s.io/hostpath" --set config.configmap.cnSqlDbUser="root" --kubeconfig="$KUBECONFIG"

