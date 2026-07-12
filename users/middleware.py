# users/middleware.py
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class LastSeenMiddleware(MiddlewareMixin):
    """
    Met à jour le champ last_seen de l'utilisateur authentifié
    à chaque requête API.
    
    Utilise un cache pour ne pas écrire trop souvent en DB
    (max 1 fois par minute par user).
    """
    
    # Cache en mémoire : {user_id: last_updated_timestamp}
    _last_update_cache = {}
    UPDATE_INTERVAL_SEC = 60  # Update DB max 1 fois par minute
    
    def process_request(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        user_id = str(request.user.id)
        now = timezone.now()
        last_db_update = self._last_update_cache.get(user_id)
        
        # Update DB seulement si > 60s depuis le dernier update
        if (last_db_update is None or
            (now - last_db_update).total_seconds() > self.UPDATE_INTERVAL_SEC):
            
            # Update direct sans charger l'instance (plus rapide)
            type(request.user).objects.filter(id=request.user.id).update(
                last_seen=now)
            self._last_update_cache[user_id] = now
        
        return None