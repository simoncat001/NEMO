from NEMO.views.api_render import render_api as render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from NEMO.models import ContactInformation, ContactInformationCategory


@login_required
@require_GET
def contact_staff(request):
    dictionary = {
        "categories": ContactInformationCategory.objects.all(),
        "people": ContactInformation.objects.all(),
    }
    return render(request, "contact/contact_staff.html", dictionary)
