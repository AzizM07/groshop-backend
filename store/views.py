from django.http import JsonResponse

# Vos fonctions de vue doivent être ici, sans 'path()'
def recent_searches(request):
    # Logique pour récupérer les recherches récentes
    return JsonResponse({"status": "recent_searches view"})

def clear_recent_searches(request):
    # Logique pour effacer les recherches
    return JsonResponse({"status": "clear_recent_searches view"})