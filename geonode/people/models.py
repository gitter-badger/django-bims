# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from uuid import uuid4
import logging

from allauth.account.adapter import get_adapter
from django.conf import settings

from django.db import models
from django.db.models import signals

from django.urls import reverse
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager

from taggit.managers import TaggableManager

from geonode.base.enumerations import COUNTRIES

from allauth.account.signals import user_signed_up

from .signals import (
    profile_post_save,
    notify_admins_new_signup)
from .languages import LANGUAGES
from .timezones import TIMEZONES

logger = logging.getLogger(__name__)


class ProfileUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)


class Profile(AbstractUser):
    """Fully featured Geonode user"""

    organization = models.CharField(
        _('Organization Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('name of the responsible organization'))
    profile = models.TextField(
        _('Profile'),
        null=True,
        blank=True,
        help_text=_('introduce yourself'))
    position = models.CharField(
        _('Position Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('role or position of the responsible person'))
    voice = models.CharField(_('Voice'), max_length=255, blank=True, null=True, help_text=_(
        'telephone number by which individuals can speak to the responsible organization or individual'))
    fax = models.CharField(_('Facsimile'), max_length=255, blank=True, null=True, help_text=_(
        'telephone number of a facsimile machine for the responsible organization or individual'))
    delivery = models.CharField(
        _('Delivery Point'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('physical and email address at which the organization or individual may be contacted'))
    city = models.CharField(
        _('City'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('city of the location'))
    area = models.CharField(
        _('Administrative Area'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('state, province of the location'))
    zipcode = models.CharField(
        _('Postal Code'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('ZIP or other postal code'))
    country = models.CharField(
        _('Country'),
        choices=COUNTRIES,
        max_length=3,
        blank=True,
        null=True,
        help_text=_('country of the physical address'))
    keywords = TaggableManager(_('keywords'), blank=True, help_text=_(
        'commonly used word(s) or formalised word(s) or phrase(s) used to describe the subject \
            (space or comma-separated'))
    language = models.CharField(
        _("language"),
        max_length=10,
        choices=LANGUAGES,
        default=settings.LANGUAGE_CODE
    )
    timezone = models.CharField(
        _('Timezone'),
        max_length=100,
        default="",
        choices=TIMEZONES,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self._previous_active_state = self.is_active

    def get_absolute_url(self):
        return reverse('profile_detail', args=[self.username, ])

    def __str__(self):
        return "{0}".format(self.username)

    @staticmethod
    def class_name(value):
        return value.__class__.__name__

    objects = ProfileUserManager()
    USERNAME_FIELD = 'username'

    def is_member_of_group(self, group_slug):
        """
        Returns if the Profile belongs to a group of a given slug.
        """
        return self.groups.filter(name=group_slug).exists()

    def keyword_list(self):
        """
        Returns a list of the Profile's keywords.
        """
        return [kw.name for kw in self.keywords.all()]

    @property
    def name_long(self):
        if self.first_name and self.last_name:
            return '%s %s (%s)' % (self.first_name,
                                   self.last_name, self.username)
        elif (not self.first_name) and self.last_name:
            return '%s (%s)' % (self.last_name, self.username)
        elif self.first_name and (not self.last_name):
            return '%s (%s)' % (self.first_name, self.username)
        else:
            return self.username

    @property
    def full_name_or_nick(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name,
                              self.last_name)
        else:
            return self.username

    @property
    def first_name_or_nick(self):
        return self.first_name if self.first_name else self.username

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        self._notify_account_activated()
        self._previous_active_state = self.is_active

    def _notify_account_activated(self):
        """Notify user that its account has been activated by a staff member"""
        became_active = self.is_active and not self._previous_active_state
        if became_active and self.last_login is None:
            try:
                # send_notification(users=(self,), label="account_active")

                from invitations.adapters import get_invitations_adapter
                current_site = Site.objects.get_current()
                ctx = {
                    'username': self.username,
                    'current_site': current_site,
                    'site_name': current_site.name,
                    'email': self.email,
                    'inviter': self,
                }

                email_template = 'pinax/notifications/account_active/account_active'
                adapter = get_invitations_adapter()
                adapter.send_invitation_email(email_template, self.email, ctx)
            except Exception:
                import traceback
                traceback.print_exc()

    def send_mail(self, template_prefix, context):
        if self.email:
            get_adapter().send_mail(template_prefix, self.email, context)


def get_anonymous_user_instance(user_model):
    return user_model(pk=-1, username='AnonymousUser')


""" Connect relevant signals to their corresponding handlers. """
user_signed_up.connect(
    notify_admins_new_signup,
    dispatch_uid=str(uuid4()),
    weak=False
)
signals.post_save.connect(
    profile_post_save,
    sender=settings.AUTH_USER_MODEL
)
