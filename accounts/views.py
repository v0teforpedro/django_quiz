from django.contrib.auth import get_user_model
from django.core.signing import BadSignature
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import TemplateView

from .forms import AccountRegisterForm
from .utils import signer


class AccountRegisterView(CreateView):
    model = get_user_model()
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:register_done')
    form_class = AccountRegisterForm


class AccountRegisterDoneView(TemplateView):
    template_name = 'accounts/register_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'accounts/bad_signature.html')

    user = get_object_or_404(get_user_model(), username=username)
    if user.is_activated:
        template = 'accounts/user_is_activated.html'
    else:
        template = 'accounts/activation_done.html'
        user.is_activated = True
        user.is_active = True
        user.save()

    return render(request, template)
