from pprint import pprint
from kubernetes import config, client
import logging

#use the serviceAccount k8s gives to pods
config.load_incluster_config() 
v1 = client.CoreV1Api()

#global vars
name = "tls-certificate"
namespace = "default"

# check if gluu secret exists
def get_certs():
    if ( v1.read_namespaced_secret( 'gluu', 'default' ) ):
        ssl_cert = v1.read_namespaced_secret( 'gluu', 'default' ).data['ssl_cert']
        ssl_key = v1.read_namespaced_secret( "gluu", "default" ).data['ssl_key']
        
        print('ssl_cert / {} \n ssl_key: {}'.format(ssl_cert, ssl_key) )

    return ssl_cert, ssl_key


def create_tls(cert, key):

    v1 = client.CoreV1Api()
    try:
        secret = v1.read_namespaced_secret(name, namespace)
    except client.rest.ApiException as e:
        if e.status == 404:
            print('secret/{} in ns/{} does not exist. Creating...'.format(
                name, namespace))
            metadata = {
                'name': name,
                'namespace': namespace
            }
            data = {
                'tls.crt': cert,
                'tls.key' : key,
            }
            api_version = 'v1'
            kind = 'Secret'
            body = client.V1Secret(api_version, data , kind, metadata, 
                type='kubernetes.io/tls')
            api_response = v1.create_namespaced_secret(namespace, body )
            pprint(api_response)
        else:
            logging.exception(e)
        return False
    else:
        print('tls-certificate already exists as /{}'. format(
            secret
        ))

        
def main():
    cert, key = get_certs()
    create_tls(cert, key)

if __name__ == "__main__":
    main()