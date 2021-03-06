"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

# Standard imports
from re import compile as re_compile

# Third-party imports
from constance import config

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.db.models import signals
from django.http import HttpResponseNotAllowed, HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry

# Project imports
from allauth.account.models import EmailAddress
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.9/LICENSE"
__version__ = "1.0.9"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


EXEMPT_URLS = [re_compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re_compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other than LOGIN_URL.
    Exemptions to this requirement can optionally be specified in settings
    via a list of regular expressions in LOGIN_EXEMPT_URLS (which you can copy from your urls.py).

    MIDDLEWARE_CLASSES should have 'django.contrib.auth.middleware.AuthenticationMiddleware'.
    TEMPLATE_CONTEXT_PROCESSORS setting should include'django.core.context_processors.auth'.
    """
    def process_view(self, request, view_func, args, kwargs):
        assert hasattr(request, 'user')
        if not request.user.is_authenticated() and not config.auto_login:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)


class AutoLoginMiddleware(MiddlewareMixin):
    """
    Auto login test user.
    Create test user if needed.
    settings should have AUTOLOGIN_TEST_USER_FORBIDDEN_URLS
    and AUTOLOGIN_ALWAYS_OPEN_URLS
    MIDDLEWARE_CLASSES should have 'django.contrib.auth.middleware.AuthenticationMiddleware'.
    TEMPLATE_CONTEXT_PROCESSORS setting should include 'django.core.context_processors.auth'.
    """
    TEST_USER_FORBIDDEN_URLS = [
        re_compile(str(expr)) for expr in settings.AUTOLOGIN_TEST_USER_FORBIDDEN_URLS]

    def process_view(self, request, view_func, args, kwargs):

        if config.auto_login:

            path = request.path_info
            if path in settings.AUTOLOGIN_ALWAYS_OPEN_URLS:
                return

            if not request.user.is_authenticated():
                test_user, created = User.objects.update_or_create(
                    username='test_user',
                    defaults=dict(
                        first_name='Test',
                        last_name='User',
                        name='Test User',
                        email='test@user.com',
                        role='manager',
                        is_active=True))
                if created:
                    test_user.set_password('test_user')
                    test_user.save()
                    EmailAddress.objects.create(
                        user=test_user,
                        email=test_user.email,
                        verified=True,
                        primary=True)

                user = authenticate(username='test_user', password='test_user')
                request.user = user
                login(request, user)

            if request.user.username == 'test_user':
                if any(m.search(path) for m in self.TEST_USER_FORBIDDEN_URLS):
                    return redirect(reverse_lazy('home'))


class HttpResponseNotAllowedMiddleware(MiddlewareMixin):
    """
    Custom page for HTTP method Not Allowed error 405.
    """
    def process_response(self, request, response):
        if isinstance(response, HttpResponseNotAllowed):
            response.content = render(request, '405.html')
        return response


class Response5xxErrorMiddleware(MiddlewareMixin):
    """
    Custom page for 5xx errors (502 Bad Gateway).
    """
    def process_response(self, request, response):
        if str(response.status_code).startswith('5'):
            response.status_code = 500
            response.content = render(request, '500.html')
        return response


class RequestUserMiddleware(MiddlewareMixin):
    """
    Provide access to request user in models
    """
    def process_request(self, request):
        if request.method not in ('HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
            update_save_info = curry(self.insert_user, user)
            signals.pre_save.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.post_save.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)
            signals.m2m_changed.connect(
                update_save_info, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def process_exception(self, request, exception):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid=(self.__class__, request,))
        signals.m2m_changed.disconnect(dispatch_uid=(self.__class__, request,))
        return None

    def insert_user(self, user, sender, instance, **kwargs):
        instance.request_user = user


class AppEnabledRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires to enable certain kind of application enabled.
    in "application settings"
    """
    def process_view(self, request, view_func, args, kwargs):
        if hasattr(view_func, 'view_class') and hasattr(view_func.view_class, 'sub_app'):
            current_sub_app = view_func.view_class.sub_app
            available_locators = list(settings.REQUIRED_LOCATORS) + list(config.standard_optional_locators)
            if current_sub_app not in available_locators:
                messages.error(request, 'This locator is not enabled.')
                if request.is_ajax() or request.META['CONTENT_TYPE'] == 'application/json':
                    return HttpResponseForbidden('Standard sub-application "%s" is not enabled.'
                                                 % current_sub_app)
                return redirect(reverse_lazy('common:application-settings'))


class CookieMiddleware(MiddlewareMixin):
    """
    Set cookie.
    """
    def process_response(self, request, response):
        auth_token = request.COOKIES.get('auth_token', request.META.get('HTTP_AUTHORIZATION'))
        if request.META['PATH_INFO'] == reverse('rest_login') \
                and hasattr(response, 'data') \
                and response.data and response.data.get('key'):
            response.set_cookie('auth_token', 'Token %s' % response.data['key'])
        elif auth_token:
            response.set_cookie('auth_token', auth_token)
        return response
