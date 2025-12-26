import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.template import Context, Template
from django.template.defaultfilters import linebreaksbr
from django.utils import timezone
from django.views.decorators.http import require_GET

from NEMO.models import Alert, LandingPageChoice, Reservation, Resource, UsageEvent, User
from NEMO.views.alerts import mark_alerts_as_expired
from NEMO.views.area_access import able_to_self_log_in_to_area, able_to_self_log_out_of_area
from NEMO.views.customization import ApplicationCustomization, CustomizationBase, UserCustomization
from NEMO.views.landing import valid_url_for_landing
from NEMO.views.notifications import delete_expired_notifications, get_notification_counts


@login_required
@require_GET
def landing_data(request):
    user: User = request.user
    mark_alerts_as_expired()
    delete_expired_notifications()

    usage_events = UsageEvent.objects.filter(operator=user.id, end=None).prefetch_related("tool", "project")
    tools_in_use = [u.tool.tool_or_parent_id() for u in usage_events]
    fifteen_minutes_from_now = timezone.now() + timedelta(minutes=15)
    landing_page_choices = LandingPageChoice.objects.all()
    if request.device == "desktop":
        landing_page_choices = landing_page_choices.exclude(hide_from_desktop_computers=True)
    if request.device == "mobile":
        landing_page_choices = landing_page_choices.exclude(hide_from_mobile_devices=True)
    landing_page_choices = [
        landing_page_choice for landing_page_choice in landing_page_choices if landing_page_choice.can_user_view(user)
    ]

    if not settings.ALLOW_CONDITIONAL_URLS:
        landing_page_choices = [
            landing_page_choice
            for landing_page_choice in landing_page_choices
            if valid_url_for_landing(landing_page_choice.url)
        ]

    upcoming_reservations = (
        Reservation.objects.filter(user=user.id, end__gt=timezone.now(), cancelled=False, missed=False, shortened=False)
        .exclude(tool_id__in=tools_in_use, start__lte=fifteen_minutes_from_now)
        .exclude(ancestor__shortened=True)
    )
    if user.in_area():
        upcoming_reservations = upcoming_reservations.exclude(
            area=user.area_access_record().area, start__lte=fifteen_minutes_from_now
        )
    upcoming_reservations = upcoming_reservations.order_by("start")[:3]

    show_access_expiration_banner = None
    expiration_warning = UserCustomization.get_int("user_access_expiration_banner_warning")
    expiration_danger = UserCustomization.get_int("user_access_expiration_banner_danger")
    if user.access_expiration and (expiration_warning or expiration_danger):
        access_expiration_datetime = datetime.datetime.combine(user.access_expiration, datetime.time.min).astimezone()
        if access_expiration_datetime >= timezone.now():
            if expiration_warning and access_expiration_datetime < timezone.now() + timedelta(days=expiration_warning):
                show_access_expiration_banner = "warning"
            if expiration_danger and access_expiration_datetime < timezone.now() + timedelta(days=expiration_danger):
                show_access_expiration_banner = "danger"

    notification_counts = get_notification_counts(user)
    customization_values = CustomizationBase.get_all()

    payload = {
        "site_title": customization_values.get("site_title"),
        "facility_name": customization_values.get("facility_name"),
        "access_expiration_banner": show_access_expiration_banner,
        "facility_rules_required_message": Template(
            ApplicationCustomization.get("facility_rules_required_message")
        ).render(Context()),
        "self_log_in": able_to_self_log_in_to_area(request.user),
        "self_log_out": able_to_self_log_out_of_area(request.user),
        "user": {
            "id": user.id,
            "display_name": user.get_full_name() or user.username,
            "training_required": user.training_required,
            "access_expiration": user.access_expiration.isoformat() if user.access_expiration else None,
            "in_area": user.in_area(),
        },
        "alerts": [
            {
                "id": alert.id,
                "title": alert.title,
                "contents": linebreaksbr(alert.contents),
                "dismissible": alert.dismissible,
            }
            for alert in Alert.objects.filter(
                Q(user=None) | Q(user=user),
                debut_time__lte=timezone.now(),
                expired=False,
                deleted=False,
            )
        ],
        "disabled_resources": [
            {
                "id": resource.id,
                "name": str(resource),
                "restriction_message": resource.restriction_message,
            }
            for resource in Resource.objects.filter(available=False)
        ],
        "usage_events": [
            {
                "id": usage.id,
                "tool_name": str(usage.tool),
                "project_name": str(usage.project),
                "start": usage.start.isoformat(),
            }
            for usage in usage_events
        ],
        "upcoming_reservations": [
            {
                "id": reservation.id,
                "title": reservation.title or str(reservation.reservation_item),
                "start": reservation.start.isoformat(),
                "end": reservation.end.isoformat(),
                "resource_name": str(reservation.reservation_item),
            }
            for reservation in upcoming_reservations
        ],
        "landing_page_choices": [
            {
                "id": choice.id,
                "name": choice.name,
                "url": choice.url,
                "open_in_new_tab": choice.open_in_new_tab,
                "image_url": choice.image.url if choice.image else None,
                "notification_count": notification_counts.get(choice.notifications, 0)
                if choice.notifications
                else 0,
            }
            for choice in landing_page_choices
        ],
    }

    return JsonResponse(payload)
