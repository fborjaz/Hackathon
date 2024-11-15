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
from .models import UserProfile

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scopes necesarios para acceder a Gmail y Google People
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/contacts.readonly"]


# Vista para mostrar la página principal con la información de la huella de carbono
class HomePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'layout/base.html')

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

# Función para obtener el email del perfil de usuario
def get_user_email(service):
    try:
        # Llamada a la API de Gmail para obtener el perfil de usuario
        profile = service.users().getProfile(userId='me').execute()
        # Obtener la dirección de correo electrónico del perfil
        email_address = profile.get('emailAddress')
        return email_address
    except HttpError as error:
        logger.error(f"Error al obtener el perfil de usuario: {error}")
        return None

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
            # Obtener el email del usuario
            user_email = get_user_email(service)
            if not user_email:
                return JsonResponse({'error': 'No se pudo obtener el correo del usuario'}, status=500)

            # Guardar el email en la base de datos si no existe
            user_profile, created = UserProfile.objects.get_or_create(email=user_email)
            if created:
                logger.info(f"Nuevo perfil de usuario creado para {user_email}")
            else:
                logger.info(f"El perfil de usuario para {user_email} ya existe")

            people_service = build("people", "v1", credentials=service._http.credentials)

            message_contents = []
            found_messages = False
            next_page_token = None
            total_messages = 0

            for category in ["promotions", "social"]:
                results = service.users().messages().list(
                    userId="me", 
                    maxResults=10,
                    q=f"category:{category} is:unread older_than:{age}",
                    pageToken=page_token if page_token else None
                ).execute()
                messages = results.get("messages", [])

                if messages:
                    found_messages = True
                    next_page_token = results.get('nextPageToken')
                    total_messages += results.get('resultSizeEstimate', 0)

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

            # Si no se encontraron mensajes en ninguna categoría, devolver mensaje adecuado
            if not found_messages:
                return JsonResponse({'message': 'No tiene correos con la antigüedad especificada.'})

            total_pages = (total_messages + 9) // 10

            return JsonResponse({
                'message_contents': message_contents, 
                'next_page_token': next_page_token, 
                'total_pages': total_pages,
                'user_email': user_email
            })

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
            
            # Obtener el email del usuario
            user_email = get_user_email(service)
            if not user_email:
                return JsonResponse({'error': 'No se pudo obtener el correo del usuario'}, status=500)
            
            # Buscar el perfil del usuario en la base de datos
            user_profile, created = UserProfile.objects.get_or_create(email=user_email)

            # Eliminar los correos electrónicos en lotes
            service.users().messages().batchDelete(
                userId="me",
                body={
                    "ids": message_ids
                }
            ).execute()

            # Actualizar el contador de correos eliminados
            user_profile.deleted_emails_count += len(message_ids)
            user_profile.save()

            logger.info(f"{len(message_ids)} correos eliminados para {user_email}. Total acumulado: {user_profile.deleted_emails_count}")

            return JsonResponse({'success': True, 'deleted_count': user_profile.deleted_emails_count})

        except HttpError as error:
            logger.error(f"Error al eliminar los correos electrónicos: {error.status_code} - {error.content}")
            return JsonResponse({'error': f'Error deleting emails: {error}'}, status=500)
