from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-sent_at')

    # Filtre non lues seulement
    unread_only = request.query_params.get('unread')
    if unread_only == 'true':
        notifications = notifications.filter(is_read=False)

    # Pagination
    limit  = min(int(request.query_params.get('limit', 20)), 50)
    offset = int(request.query_params.get('offset', 0))
    total  = notifications.count()
    notifications = notifications[offset:offset + limit]

    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'total':    total,
        'unread':   Notification.objects.filter(user=request.user, is_read=False).count(),
        'results':  serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read(request, pk):
    # Marquer une notification comme lue
    try:
        notif = Notification.objects.get(id=pk, user=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'message': 'Notification marquée comme lue.'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification non trouvée.'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    # Marquer toutes les notifications comme lues
    Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True)
    return Response({'message': 'Toutes les notifications marquées comme lues.'})