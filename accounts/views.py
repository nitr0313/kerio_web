from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

from django.db.models import QuerySet
from django.views import View
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, redirect, render

from action_logger.service import ActionLoggerService
from .forms import IPAddressForm
from .models import IPAddress
from .service import IPService
from .tasks import sync_in_from_kerio_control


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
            kerio = IPService(user=request.user)
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
        logs = ActionLoggerService(self.request.user)
        context = dict(
            form=form,
            object=instance,
            current_ip=current_ip,
            logs=logs.get_logs(2)
        )
        if self.request.user.is_staff:
            context.update({
                'users_ip': IPAddress.objects.all()
            })
        return context


@require_GET
@login_required
def get_status_ip(request, pk):
    """
    You can respond with the HTTP response code 286
    and the element will cancel the polling.
    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(IPAddress, id=pk)
    return render(
        request=request,
        template_name="accounts/includes/rounded_bage.html",
        context={'object': obj},
        status=286 if obj.in_router else None
    )


class Login(LoginView):
    ...


class Logout(LogoutView):
    ...


def sync_db(request):
    action = ActionLoggerService(request.user)
    action.add_task_sync_db()
    sync_in_from_kerio_control.delay()
    return redirect('profile')


def get_logs(request, count=None):
    action = ActionLoggerService(request.user)
    return render(request, "accounts/includes/logs.html", {"logs": action.get_logs(count)})
