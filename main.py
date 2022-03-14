import json
import os
import requests
import logging


def changePolicyStatusPerSeverity(base_url, token, severity='high', enabled='true'):
    url = "https://%s/v2/policy?policy.severity=%s&policy.policyMode=redlock_default" % (
        base_url, severity)

    logging.debug('Target URL is: {}'.format(url))

    headers = {"content-type": "application/json; charset=UTF-8",
               'Authorization': 'Bearer ' + token}

    response = requests.get(url, headers=headers)
    logging.debug('Rerturn code is: {}'.format(response.status_code))
    policies = response.json()

    for policy in policies:
        patchPolicy(base_url, policy['policyId'], enabled)
        logging.info('Enable policy: {} - {}'.format(
            policy['policyId'], policy['name']))

    logging.info('Number of policies enabled: {}'.format(len(policies)))


def patchPolicy(base_url, policyId, enabled):
    url = "https://%s/policy/%s/status/%s" % (base_url, policyId, enabled)

    headers = {'x-redlock-auth': token}
    response = requests.request("PATCH", url, headers=headers)

    logging.debug('Return code for enable policy {}: {}'.format(
        policyId, response.status_code))


def loginCWP(base_url, access_key, secret_key):
    url = "https://%s/api/v1/authenticate" % (base_url)

    payload = json.dumps({
        "username": access_key,
        "password": secret_key
    })
    headers = {"content-type": "application/json; charset=UTF-8"}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["token"]


def loginCSPM(base_url, access_key, secret_key):
    url = "https://%s/login" % (base_url)

    payload = json.dumps({
        "username": access_key,
        "password": secret_key
    })
    headers = {"content-type": "application/json; charset=UTF-8"}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["token"]


def getParamFromJson(config_file):
    f = open(config_file,)

    params = json.load(f)
    api_endpoint = params["api_endpoint"]
    pcc_api_endpoint = params["pcc_api_endpoint"]
    access_key_id = params["access_key_id"]
    secret_key = params["secret_key"]
    # Closing file
    f.close()
    return api_endpoint, pcc_api_endpoint, access_key_id, secret_key


def connect(type='cspm'):
    global API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY, token
    PRISMA_CLOUD_DIRECTORY = os.environ['HOME'] + "/.prismacloud/"

    if os.path.exists(PRISMA_CLOUD_DIRECTORY):
        CONFIG_FILE = os.environ['HOME'] + "/.prismacloud/credentials.json"
        API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY = getParamFromJson(
            CONFIG_FILE)
        logging.debug("Config loaded from local file.")

    else:
        logging.info(
            'Prisma cloud directory does not exists, let\'s create one in your $HOME/.prismacloud')
        os.makedirs(PRISMA_CLOUD_DIRECTORY)
        CONFIG_FILE = PRISMA_CLOUD_DIRECTORY + "credentials.json"
        API_ENDPOINT = input(
            "Enter CSPM API Endpoint (OPTIONAL if PCCE), eg: api.prismacloud.io: ")
        PCC_API_ENDPOINT = input(
            "Enter CWPP API Endpoint, eg: us-east1.cloud.twistlock.com/<tenant-id>: ")
        ACCESS_KEY_ID = input("Enter the access key ID: ")
        SECRET_KEY = input("Enter the secret key: ")

        API_FILE = {
            "api_endpoint": API_ENDPOINT,
            "pcc_api_endpoint": PCC_API_ENDPOINT,
            "access_key_id": ACCESS_KEY_ID,
            "secret_key": SECRET_KEY
        }

        json_string = json.dumps(API_FILE, sort_keys=True, indent=4)

        with open(CONFIG_FILE, 'w') as outfile:
            outfile.write(json_string)

        API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY = getParamFromJson(
            CONFIG_FILE)

    if type == 'cwpp':
        token = loginCWP(PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY)
    elif type == 'cspm':
        token = loginCSPM(API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY)

    logging.info('Authentication successfull')


def main():
    global API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY, token
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    connect()

    # changePolicyStatusPerSeverity(API_ENDPOINT, token, 'high', 'true')
    changePolicyStatusPerSeverity(API_ENDPOINT, token, 'medium', 'true')
    # changePolicyStatusPerSeverity(API_ENDPOINT, token, 'low', 'true')


if __name__ == "__main__":
    main()
