from urllib2 import urlopen, Request
import boto3
import os
import json

from base64 import b64decode

#parse environment variables
ENCRYPTED = os.environ['auth']
USER = os.environ['user']
DECRYPTED = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED))['Plaintext']
EMAIL_CLIENT = boto3.client('ses')

def lambda_handler(event, context):
    """main lambda function to be executed"""

    #url defines the type of information that will be returned by the request
    jsonRes = getData(
        'https://api.github.com/user/repos',
        USER,
        DECRYPTED
    )

    emailText = ''

    for elem in jsonRes:
        #get the repo name from each individual entry
        name = elem['full_name']

        #get more information from each repo
        created = elem['created_at']

        #add to the text of the email
        emailText += 'repo: {}, created at {} \n'.format(name, created)

    #send myself an email about the results of the api call
    status = sendEmail(
        'example@gmail.com',
        emailText
    )

    #print the status of the email
    print(status)

def getData(gitUrl, user, authToken):
    """make github api call and return json object"""

    #create new request
    request = Request(gitUrl)

    #add auth header: github api token
    request.add_header('Authorization', 'token %s' % authToken)

    #get response, return object
    response = urlopen(request)

    #return data as an index-able json object
    return json.loads(response.read())

def sendEmail(address, body):
    """sends email to ses verified address with the contents of the body"""

    #using boto3 ses client, create a formatted email with the necessary params
    response = EMAIL_CLIENT.send_email(
        Destination={
            'ToAddresses': [
                address,
            ]
        },
        Message={
            'Subject': {
                'Data': 'Github repo update',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        },
        Source='example@gmail.com'
    )
    #get status for logs
    return response
