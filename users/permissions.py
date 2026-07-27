# users/permissions.py  (NOUVEAU FICHIER)
# ⚠️ Nommée IsAdmin (et pas IsAdminUser) pour ne PAS entrer en collision
#    avec rest_framework.permissions.IsAdminUser, qui teste is_staff.
from rest_framework.permissions import BasePermission
 
 
class IsAdmin(BasePermission):
    """Autorise uniquement les comptes dont le rôle est 'admin' (CEO / plateforme)."""
    message = 'Accès réservé aux administrateurs.'
 
    def has_permission(self, request, view):
        u = getattr(request, 'user', None)
        return bool(u and u.is_authenticated and getattr(u, 'role', None) == 'admin')
 