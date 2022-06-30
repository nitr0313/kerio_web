from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

from django.db.models import QuerySet
from django.views import View
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IPAddressForm
from .models import IPAddress
from .service import KerioService
from .tasks import sync_with_kerio_control


class Profile(LoginRequiredMixin, View):
    model = IPAddress
    template_name = "accounts/account.html"

    def get(self, request):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        context = self.get_context_data()

        bounded_form = IPAddressForm(request.POST, initial={'user': request.user})
        context['form'] = bounded_form
        if bounded_form.is_valid():
            kerio = KerioService(user=request.user)
            context['object'] = kerio.change_object_in_db(
                new_ip=bounded_form.cleaned_data.get('ipaddress'),
                is_active=bounded_form.cleaned_data.get('is_active')
            )
        return render(request, self.template_name, context)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(user=self.request.user).first()

    def get_context_data(self) -> dict:
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            current_ip = x_forwarded_for.split(',')[0]
        else:
            current_ip = self.request.META.get('REMOTE_ADDR')
        instance = self.get_queryset()
        form = IPAddressForm(instance=instance)
        context = dict(
            form=form,
            object=instance,
            current_ip=current_ip
        )
        return context


@require_GET
@login_required
def get_status_ip(request, pk):
    object = get_object_or_404(IPAddress, id=pk)
    return render(request, "accounts/includes/rounded_bage.html", {'object': object})


class Login(LoginView):
    ...


class Logout(LogoutView):
    ...


def sync_db(request):
    sync_with_kerio_control()
    return redirect('profile')
