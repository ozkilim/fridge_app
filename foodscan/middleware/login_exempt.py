from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


def login_exempt(view):
    view.login_exempt = True
    return view


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_attr_list = [a for a in dir(view_func) if not a.startswith('__')]
        if 'view_class' in view_attr_list:
            if view_func.view_class == auth_views.LoginView or view_func.view_class == auth_views.LogoutView:
                return

        if getattr(view_func, 'login_exempt', False):
            return

        if request.user.is_authenticated:
            return

        # You probably want to exclude the login/logout views, etc.

        return login_required(view_func)(request, *view_args, **view_kwargs)