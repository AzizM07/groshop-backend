from django.db import models
import uuid


class DeviceToken(models.Model):
    PLATFORMS = (('web', 'Web'), ('android', 'Android'), ('ios', 'iOS'))

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                    null=True, blank=True, related_name='device_tokens')
    token      = models.TextField(unique=True)
    platform   = models.CharField(max_length=10, choices=PLATFORMS, default='web')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'device_tokens'
        indexes = [models.Index(fields=['user']), models.Index(fields=['is_active'])]

    def __str__(self):
        return f'{self.platform} · {self.token[:16]}…'


class PushNotification(models.Model):
    AUDIENCES = (
        ('all', 'Tous'),
        ('buyers', 'Acheteurs'),
        ('suppliers', 'Fournisseurs'),
        ('user', 'Un utilisateur'),
    )

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=200)
    body        = models.TextField()
    image_url   = models.TextField(blank=True, default='')
    link        = models.CharField(max_length=500, blank=True, default='')
    audience    = models.CharField(max_length=12, choices=AUDIENCES, default='all')
    target_user = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='+')
    sent_count  = models.IntegerField(default=0)
    fail_count  = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'push_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title