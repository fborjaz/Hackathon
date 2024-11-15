import json
import logging
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

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scopes necesarios para acceder a Gmail y Google People
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/contacts.readonly"]


# Función para autenticar y construir el servicio de Gmail
def get_gmail_service():
    creds = None
    if os.path.exists("delete_email/token.json"):
        creds = Credentials.from_authorized_user_file("delete_email/token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("delete_email/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent', authorization_prompt_message='', success_message="Authentication successful! Redirecting...")  
        with open("delete_email/token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

@method_decorator(csrf_exempt, name="dispatch")
class EmailSelectionView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'email/select_email.html')

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        page_token = request.GET.get('pageToken')
        age = data.get('age', '1y')

        try:
            service = get_gmail_service()
            people_service = build("people", "v1", credentials=service._http.credentials)

            message_contents = []
            for category in ["promotions", "social"]:
                results = service.users().messages().list(
                    userId="me", 
                    maxResults=10,
                    q=f"category:{category} is:unread older_than:{age}",
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

                    sender_email = sender.split('<')[-1].split('>')[0] if '<' in sender else sender
                    profile_image_url = self.get_profile_image(people_service, sender_email)

                    message_contents.append({
                        'id': message['id'],
                        'sender': sender,
                        'subject': subject,
                        'profileImage': profile_image_url,
                    })

            next_page_token = results.get('nextPageToken')
            total_messages = results.get('resultSizeEstimate', 0)
            total_pages = (total_messages + 9) // 10  # Redondear hacia arriba

            return JsonResponse({'message_contents': message_contents, 'next_page_token': next_page_token, 'total_pages': total_pages})

        except HttpError as error:
            logger.error(f"Error al obtener los correos electrónicos: {error.status_code} - {error.content}")
            return JsonResponse({'error': str(error)}, status=error.status_code)

    def get_profile_image(self, people_service, email):
        try:
            # Consultar la API de Google People para obtener la foto de perfil
            profile = people_service.people().get(
                resourceName=f'people/{email}',
                personFields='photos'
            ).execute()

            # Extraer la URL de la foto de perfil si existe
            if 'photos' in profile:
                return profile['photos'][0]['url']
            return "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon"  # Imagen por defecto si no tiene foto
        except HttpError:
            return "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon"  # Imagen por defecto en caso de error

@method_decorator(csrf_exempt, name="dispatch")
class DeleteEmailsView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        message_ids = data.get('message_ids', [])

        if not message_ids:
            return JsonResponse({'error': 'No emails selected for deletion.'}, status=400)

        try:
            service = get_gmail_service()

            # Eliminar los correos electrónicos en lotes
            service.users().messages().batchDelete(
                userId="me",
                body={
                    "ids": message_ids
                }
            ).execute()

            return JsonResponse({'success': True})

        except HttpError as error:
            logger.error(f"Error al eliminar los correos electrónicos: {error.status_code} - {error.content}")
            return JsonResponse({'error': f'Error deleting emails: {error}'}, status=500)