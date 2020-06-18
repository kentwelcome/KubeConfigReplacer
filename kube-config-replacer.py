#!/usr/bin/env python3
import os
import sys
import yaml
import pprint

USER_NAME_FORMAT='{}-kube-admin'

def print_usage(argv):
    print('Usage: kube-config-replacer.py <target-name> <target-config>', file=sys.stderr)

def yaml_reader(filename):
    with open(os.path.expanduser(filename), 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def find_obj(type, config, name):
    for i,c in enumerate(config[type]):
        if c.get('name', '') == name:
            return i
    return -1

def replace_cluster(replaced_config, new_config, name):
    cluster_idx = find_obj('clusters', replaced_config, name)
    certificate = new_config['clusters'][0]['cluster']['certificate-authority-data']
    if cluster_idx < 0:
        replaced_config['clusters'].append({
            'cluster': {
                'certificate-authority-data': certificate,
                'server': 'https://127.0.0.1:6443'
            },
            'name': name            
            })
    else:
        replaced_config['clusters'][cluster_idx]['cluster']['certificate-authority-data'] = certificate
    return replaced_config

def replace_context(replaced_config, new_config, name):
    context_idx = find_obj('contexts', replaced_config, name)

    if context_idx < 0:
        replaced_config['contexts'].append({
            'context': {
                'cluster': name,
                'user': USER_NAME_FORMAT.format(name)
            },
            'name': name
        })

    return replaced_config

def replace_user(replaced_config, new_config, name):
    user_idx = find_obj('users', replaced_config, USER_NAME_FORMAT.format(name))

    if new_config['users'][0]['user'].get('client-certificate-data', '') != '':
        client_certificate = new_config['users'][0]['user']['client-certificate-data']
        client_key = new_config['users'][0]['user']['client-key-data']

        if user_idx < 0:
            replaced_config['users'].append({
                'name': USER_NAME_FORMAT.format(name),
                'user': {
                    'client-certificate-data': client_certificate,
                    'client-key-data': client_key
                }
            })
        else:
            replaced_config['users'][user_idx]['user']['client-certificate-data'] = client_certificate
            replaced_config['users'][user_idx]['user']['client-key-data'] = client_key
    else:
        username = new_config['users'][0]['user']['username']
        password = new_config['users'][0]['user']['password']

        if user_idx < 0:
            replaced_config['users'].append({
                'name': USER_NAME_FORMAT.format(name),
                'user': {
                    'username': username,
                    'password': password
                }
            })
        else:
            replaced_config['users'][user_idx]['user']['username'] = username
            replaced_config['users'][user_idx]['user']['password'] = password

    return replaced_config

def replacer(replaced_config, new_config, name):    
    
    replaced_config = replace_cluster(replaced_config, new_config, name)
    replaced_config = replace_context(replaced_config, new_config, name)
    replaced_config = replace_user(replaced_config, new_config, name)
    
    return replaced_config

def main(argv):
    if len(argv) != 3:
        print_usage(argv)
        exit(1)
    
    target_file = os.path.expanduser(argv[2])
    target_name = argv[1]

    target_config = yaml_reader(target_file)
    kube_config = yaml_reader('~/.kube/config')

    kube_config = replacer(kube_config, target_config, target_name)
    
    output = yaml.dump(kube_config, Dumper=yaml.Dumper, default_flow_style=False)
    print(output)
    exit(0)

if __name__ == '__main__':
    main(sys.argv)
