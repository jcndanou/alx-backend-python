import logging
from datetime import datetime, time, timedelta
from django.http import HttpResponseForbidden

# ... autres classes de middleware ...

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        # Définissez les heures d'accès autorisées (9h00 à 18h00)
        open_time = time(9, 0)
        close_time = time(18, 0)

        # Vérifiez si l'heure actuelle est en dehors de la plage
        if not (open_time <= current_time <= close_time):
            return HttpResponseForbidden("Access to the chat is restricted outside of operating hours (9 AM to 6 PM).")

        response = self.get_response(request)
        return response

# Je configure un logger pour écrire dans le fichier requests.log
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        # Je Definie les heures d'accès autorisées (9h00 à 18h00)
        open_time = time(9, 0)
        close_time = time(18, 0)

        # Je verifie si l'heure actuelle est en dehors de la plage
        if not (open_time <= current_time <= close_time):
            return HttpResponseForbidden("Access to the chat is restricted outside of operating hours (9 AM to 6 PM).")

        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionnaire pour stocker les requêtes par IP et leur timestamp
        self.requests_per_ip = {}
        self.max_requests = 5 # Limite de 5 messages
        self.time_window = timedelta(minutes=1) # Par minute

    def __call__(self, request):
        if request.method == 'POST':
            client_ip = request.META.get('REMOTE_ADDR')
            now = datetime.now()

            # Je nettoye l'historique des requêtes trop vieilles
            if client_ip in self.requests_per_ip:
                # Garde seulement les requêtes dans la fenêtre de temps
                self.requests_per_ip[client_ip] = [
                    ts for ts in self.requests_per_ip[client_ip] if now - ts < self.time_window
                ]
            else:
                self.requests_per_ip[client_ip] = []

            # Je vérifie si l'utilisateur a dépassé la limite
            if len(self.requests_per_ip[client_ip]) >= self.max_requests:
                return HttpResponseForbidden("You have exceeded the message sending limit. Please try again later.")

            # J'ajoute la requête actuelle à l'historique
            self.requests_per_ip[client_ip].append(now)

        response = self.get_response(request)
        return response

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Je défini les chemins qui nécessitent des privilèges d'admin
        self.admin_paths = ['/admin/', '/api/admin_actions/']

    def __call__(self, request):
        if request.path_info.startswith('/admin/') or request.path_info.startswith('/api/admin_actions/'):
            # Je m'assure que l'utilisateur est authentifié et est un admin
            if not request.user.is_authenticated or not request.user.is_staff:
                return HttpResponseForbidden("You do not have the required permissions to access this resource.")

        response = self.get_response(request)
        return response