from django.shortcuts import render

# Create your views here.
# views.py

from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from django.conf import settings
from google_auth_oauthlib.flow import Flow

# Replace with your own client_id and client_secret
CLIENT_ID = '1082280473852-3mgm19co549l5reuqpsde1lqri5ltup6.apps.googleusercontent.com'
CLIENT_SECRET = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI = 'http://localhost:8000/rest/v1/calendar/redirect/'


class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET, SCOPES, redirect_uri=REDIRECT_URI)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        state = request.session.pop('state', '')
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET,
            scopes=SCOPES,
            state=state,
            redirect_uri=REDIRECT_URI
        )
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(
            calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        response_data = []
        for event in events:
            response_data.append({
                'summary': event['summary'],
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
            })

        return HttpResponse(response_data)
