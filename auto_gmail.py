import base64
import logging

import json
import webbrowser
import csv

import httplib2

from apiclient import discovery
from oauth2client import client
from apiclient.discovery import build

from email.mime.text import MIMEText

SCOPES = [
'https://www.googleapis.com/auth/gmail.send',
'https://www.googleapis.com/auth/gmail.compose',
'https://www.googleapis.com/auth/userinfo.profile'
]

user_credential = ''
	
# Functions taken from https://developers.google.com/gmail/api/guides/sending
def create_message(sender, to, subject, message_text):
	# """Create a message for an email.

	# Args:
	# sender: Email address of the sender.
	# to: Email address of the receiver.
	# subject: The subject of the email message.
	# message_text: The text of the email message.

	# Returns:
	# An object containing a base64url encoded email object.
	# """
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
  # """Send an email message.

  # Args:
    # service: Authorized Gmail API service instance.
    # user_id: User's email address. The special value "me"
    # can be used to indicate the authenticated user.
    # message: Message to be sent.

  # Returns:
    # Sent Message.
  # """
	message = (service.users().messages().send(userId=user_id, body=message)
			   .execute())
	print ('Message Id: %s' % message['id'])
	return message

def build_service(credentials):
  """Build a Gmail service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Gmail service object.
  """
  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('gmail', 'v1', http=http)

def obtain_credentials():  
	flow = client.flow_from_clientsecrets(
		'client_secrets.json',
		scope=SCOPES,
		redirect_uri='urn:ietf:wg:oauth:2.0:oob')
	auth_uri = flow.step1_get_authorize_url()
	webbrowser.open(auth_uri)
	auth_code = input('Enter the auth code: ')

	credentials = flow.step2_exchange(auth_code)
	return credentials

# send_message(build_service(credentials), 'me', create_message('sherman dong', 'shermand@usc.edu', 'hi', 'hi test'))

message_file_name = input('Enter your message file: ')
csv_file_name = input('Enter your csv variable file: ')
user_name = input('Enter the name you want to send the email as: ')
service = build_service(obtain_credentials())
message_string = ''

with open(message_file_name) as message_file:
	message_string = message_file.read()

with open(csv_file_name, newline = '') as csv_file:
	reader = csv.reader(csv_file)
	for line in reader:
		message_version = message_string
		for variable in range (0,len(line)):
			generated_variable = '$(' + str(variable) + ')'
			message_version = message_version.replace(generated_variable, line[variable])
		#print(message_version.split('\n', 1)[0])
		#print(message_version[len(message_version.split('\n', 1)[0]):])
		subject = message_version.split('\n', 1)[0]
		body = message_version[(len(subject) + 1):]
		send_message(service, 'me', create_message(user_name, line[0], subject, body))
		#print(line[0])