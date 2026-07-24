from .models import Notification

def notifications(request):

    if request.user.is_authenticated:

        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        latest_notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")[:5]

    else:

        unread_notifications = 0
        latest_notifications = []

    return {

        "unread_notifications": unread_notifications,

        "latest_notifications": latest_notifications,

    }