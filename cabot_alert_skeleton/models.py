from django.db import models
from cabot.cabotapp.alert import AlertPluginUserData, AlertPlugin
from os import environ as env
from django.template import Context, Template
from django.conf import settings

from logging import getLogger
logger = getLogger(__name__)

cachet_template = """
Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}*is back to normal*{% else %}reporting *{{ service.overall_status }}* status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %} \
{% if alert %}{% for alias in users %} @{{ alias }}{% endfor %}{% endif %}\
{% if service.overall_status != service.PASSING_STATUS %}Checks failing:\
{% for check in service.all_failing_checks %}\
    {% if check.check_category == 'Jenkins check' %}\
        {% if check.last_result.error %}\
            - {{ check.name }} ({{ check.last_result.error|safe }}) {{check.jenkins_config.jenkins_api}}job/{{ check.name }}/{{ check.last_result.job_number }}/console
        {% else %}\
            - {{ check.name }} {{check.jenkins_config.jenkins_api}}/job/{{ check.name }}/{{check.last_result.job_number}}/console
        {% endif %}\
    {% else %}
        - {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}
    {% endif %}\
{% endfor %}\
{% endif %}\
"""

class SkeletonAlertUserData(AlertPluginUserData):
    name = "Cachet Plugin"
    favorite_bone = models.CharField(max_length=50, blank=True)

class SkeletonAlert(AlertPlugin):
    name = "Skeleton"
    author = "Jack Skellington"

    def send_alert(self, service, users, duty_officers):
        alert = True
        users = list(users) + list(duty_officers)
        if service.overall_status == service.WARNING_STATUS:
            alert = False  # Don't alert at all for WARNING
        if service.overall_status == service.ERROR_STATUS:
            if service.old_overall_status in (service.ERROR_STATUS, service.ERROR_STATUS):
                alert = False  # Don't alert repeatedly for ERROR
        if service.overall_status == service.PASSING_STATUS:
            color = 'good'
            if service.old_overall_status == service.WARNING_STATUS:
                alert = False  # Don't alert for recovery from WARNING status
        else:
            color = 'danger'

        c = Context({
            'service': service,
            'users': users,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME,
            'alert': alert,
        })
        message = Template(slack_template).render(c)
        if alert:
            self._send_cabot_alert(message, service, color=color, sender='Cabot')

        return True
    def _send_cabot_alert(message, service,color, sender):
        logger.info(message)
