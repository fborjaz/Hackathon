import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

SCOPES = ["https://mail.google.com/"]

@method_decorator(csrf_exempt, name="dispatch")
class NameView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'email/select_email.html')

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        filter_messages = data.get('filter_messages')
        page_token = request.GET.get('pageToken')

        creds = None
        if os.path.exists("delete_email/token.json"):
            creds = Credentials.from_authorized_user_file("delete_email/token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("delete_email/credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("delete_email/token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("gmail", "v1", credentials=creds)
            
            message_contents = []
            for category in ["promotions", "social"]:
                results = service.users().messages().list(
                    userId="me", 
                    maxResults=10,  # Aumentado a 10 resultados por página
                    q=f"category:{category} is:unread older_than:1y",
                    pageToken=page_token if page_token else None
                ).execute()
                messages = results.get("messages", [])

                if not messages:
                    return JsonResponse({'message': 'No messages found.'})

                for message in messages:
                    msg = service.users().messages().get(userId="me", id=message['id']).execute()

                    headers = msg.get("payload", {}).get("headers", [])
                    sender = next((header["value"] for header in headers if header["name"] == "From"), "Remitente desconocido")
                    subject = next((header["value"] for header in headers if header["name"] == "Subject"), "Sin asunto")

                    profile_image_url = f"https://www.gravatar.com/avatar/{hash(sender)}?d=identicon"

                    message_contents.append({
                        'id': message['id'],
                        'sender': sender,
                        'subject': subject,
                        'profileImage': profile_image_url,
                    })

            next_page_token = results.get('nextPageToken')

            return JsonResponse({'message_contents': message_contents, 'nextPageToken': next_page_token})

        except HttpError as error:
            return JsonResponse({'error': str(error)})

class DeleteEmailsView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        message_ids = data.get('message_ids', [])

        if not message_ids:
            return JsonResponse({'error': 'No emails selected for deletion.'}, status=400)

        try:
            creds = Credentials.from_authorized_user_file("delete_email/token.json", SCOPES)
            service = build("gmail", "v1", credentials=creds)

            for msg_id in message_ids:
                service.users().messages().delete(userId="me", id=msg_id).execute()

            return JsonResponse({'success': True})

        except HttpError as error:
            return JsonResponse({'error': f'Error deleting emails: {error}'}, status=500)

class DeleteAllEmailsView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        filter_messages = data.get('filter')
        page_token = data.get('pageToken')
        additional_criteria = data.get('additionalCriteria')
        

        try:
            creds = Credentials.from_authorized_user_file("delete_email/token.json", SCOPES)
            service = build("gmail", "v1", credentials=creds)

            results = service.users().messages().list(
                  userId="me", 
                  q=f"category:{filter_messages} {additional_criteria}",
                  pageToken=page_token if page_token else None
            ).execute()
            messages = results.get("messages", [])
            message_ids = [message['id'] for message in messages]

            for msg_id in message_ids:
                service.users().messages().delete(userId="me", id=msg_id).execute()

            return JsonResponse({'success': True})

        except HttpError as error:
            return JsonResponse({'error': f'Error deleting emails: {error}'}, status=500)