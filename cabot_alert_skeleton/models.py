from django.db import models
from cabot.cabotapp.alert import AlertPluginUserData, AlertPlugin
from os import environ as env

from logging import getLogger
logger = getLogger(__name__)

class SkeletonAlertUserData(AlertPluginUserData):
    name = "Skeleton Plugin"
    favorite_bone = models.CharField(max_length=50, blank=True)

class SkeletonAlert(AlertPlugin):
    name = "Skeleton"
    author = "Jack Skellington"

    def send_alert(self, service, users, duty_officers):
        calcium_level = env.get('CALCIUM_LEVEL')
        message = service.get_status_message()
        for u in users:
            logger.info('{} - This is bad for your {}.'.format(
                message,
                u.cabot_alert_skeleton_settings.favorite_bone))

        return True
