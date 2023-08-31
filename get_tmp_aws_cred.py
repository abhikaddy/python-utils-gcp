#!/usr/bin/env python3
import json
import requests
import sys

import boto3

def get_metadata(path: str, parameter: str):
    metadata_url = 'http://metadata.google.internal/computeMetadata/v1/{}/{}'.format(path, parameter)
    headers = {'Metadata-Flavor': 'Google'}
    try:
        meta_request = requests.get(metadata_url, headers=headers)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if meta_request.ok:
        return meta_request.text
    else:
        raise SystemExit('Compute Engine meta data error')


if __name__ == '__main__':
    # Get aws arn from command line argument
    # get_tmp_aws_cred rolearn
    try:
        aws_role_arn = sys.argv[1]
    except IndexError:
        print('Please specify AWS arn role:\n{} arn:aws:iam::account-id:role/role-name'.format(sys.argv[0]))
        exit(0)

    # Get variables from the metadata server
    instance_name = get_metadata('instance', 'name') # use 'id' instead of 'name' for GKE PODs
    project_id = get_metadata('project', 'project-id')
    project_and_instance_name = '{}.{}'.format(project_id, instance_name)
    token = get_metadata('instance', 'service-accounts/default/identity?format=standard&audience=gcp')

    # Assume role using gcp service account token
    sts = boto3.client('sts', aws_access_key_id='', aws_secret_access_key='')

    res = sts.assume_role_with_web_identity(
        RoleArn=aws_role_arn,
        WebIdentityToken=token,
        RoleSessionName=project_and_instance_name)

    aws_temporary_credentials = {
        'Version': 1,
        'AccessKeyId': res['Credentials']['AccessKeyId'],
        'SecretAccessKey': res['Credentials']['SecretAccessKey'],
        'SessionToken': res['Credentials']['SessionToken'],
        'Expiration': res['Credentials']['Expiration'].isoformat()
    }

    print(json.dumps(aws_temporary_credentials))