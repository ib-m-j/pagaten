import gflags
import httplib2
import json
import datetime

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from tools import run_flow

#FLAGS = gflags.FLAGS


def initOAuth():
  # Set up a Flow object to be used if we need to authenticate. This
  # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
  # the information it needs to authenticate. Note that it is called
  # the Web Server Flow, but it can also handle the flow for native
  # applications
  # The client_id and client_secret can be found in Google Developers Console
  FLOW = OAuth2WebServerFlow(
      client_id='970138854411-mk87k9e904ddjm7ciia1aqampcr7fsjo.apps.googleusercontent.com',
      client_secret='xurJvS1YPsDju_0Gv5eO8dUN',
      scope='https://www.googleapis.com/auth/calendar',
      user_agent='pagaten/1',
      redirect_uri='http://localhost')

  # To disable the local server feature, uncomment the following line:
  #FLAGS.auth_local_webserver = False

  # If the Credentials don't exist or are invalid, run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage('calendar.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    credentials = run_flow(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Build a service object for interacting with the API. Visit
  # the Google Developers Console
  # to get a developerKey for your own application.

  service = build(serviceName='calendar', version='v3', http=http,
                  developerKey='AIzaSyBFOFZ4hR2yv88EcvQl8aUfJG784KDnPYk'.encode('utf-8'))
  return service

newEvent = {
  'summary':'Pagaten Guddie, Philippe, Einar, Bente',
  'location':'Ib',
  'start':{'dateTime':'2015-05-02T19:30:00','timeZone':'Europe/Paris'},
  'end': {'dateTime':'2015-05-02T23:30:00','timeZone':'Europe/Paris'},
  'attendees':[{'email':'ib.m.jorgensen@gmail.com','displayName':'Ib'}]}


def createEvent(service, date, attendees, arranger, emails):
  title = 'Pagaten '
  for n in attendees:
    title = title + n + ' '
  title = title[:-1]
  dateBase = date.__format__('%Y-%m-%d')
  attList = [{'email':b,'displayName':a} for (a,b) in zip(attendees, emails)]
  newEvent = {
    'summary':title,
    'location':arranger,
    'start':{'dateTime':dateBase+'T19:30:00','timeZone':'Europe/Paris'},
    'end': {'dateTime':dateBase+'T23:30:00','timeZone':'Europe/Paris'},
    'attendees': attList}
  print(newEvent)
  create = service.events().insert(calendarId='slro83h5fnso74be0uerav2jmo@group.calendar.google.com',body=newEvent).execute()
  print('created event: ' + dateBase)
  id = create['id']
  print(id)
  return id

  
