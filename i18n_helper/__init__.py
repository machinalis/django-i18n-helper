from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.encoding import is_protected_type
from django.utils.safestring import SafeUnicode

from django.conf import settings
from wraptools import wraps
import django
import copy
import sys

# Default values
DEFAULT_I18N_CLASS = "i18n-helper"
DEFAULT_I18N_STYLE = "display: inline; background-color: #FAF9A7;"

I18N_HELPER_DEBUG = getattr(settings, 'I18N_HELPER_DEBUG', False)
RUNSERVER = sys.argv[1:2] == ['runserver']
# Omit if not running development server
if I18N_HELPER_DEBUG and RUNSERVER:
    """
    Translation debugging is set, so override django core functions and methods
    as necessary
    """
    i18n_helper_block = getattr(settings, 'I18N_HELPER_HTML', None)
    if i18n_helper_block is None:
        I18N_HELPER_CLASS = getattr(
            settings, 'I18N_HELPER_CLASS', None)
        # Use default style and class if no class is provided.
        if I18N_HELPER_CLASS is None:
            I18N_HELPER_STYLE = getattr(
                settings, 'I18N_HELPER_STYLE', DEFAULT_I18N_STYLE)
            i18n_helper_block = unicode(
                "<div class='%s' style='%s'>{0}</div>" %
                (DEFAULT_I18N_CLASS, I18N_HELPER_STYLE))
        else:
            i18n_helper_block = unicode(
                "<div class='%s'>{0}</div>" % I18N_HELPER_CLASS)
    else:
        i18n_helper_block = unicode(i18n_helper_block)

    # Wrap all the non-lazy translation functions
    @wraps(django.utils.translation.gettext)
    @wraps(django.utils.translation.ugettext)
    @wraps(django.utils.translation.ngettext)
    @wraps(django.utils.translation.ungettext)
    @wraps(django.utils.translation.pgettext)
    @wraps(django.utils.translation.npgettext)
    def wrapper(original_function, *args):
        original_result = original_function(*args)
        return mark_safe(i18n_helper_block.format(original_result))

    # Override all the lazy translation functions
    django.utils.translation.ngettext_lazy = lazy(
        django.utils.translation.ngettext, unicode)
    django.utils.translation.gettext_lazy = lazy(
        django.utils.translation.gettext, unicode)
    django.utils.translation.ungettext_lazy = lazy(
        django.utils.translation.ungettext, unicode)
    django.utils.translation.ugettext_lazy = lazy(
        django.utils.translation.ugettext, unicode)
    django.utils.translation.pgettext_lazy = lazy(
        django.utils.translation.pgettext, unicode)
    django.utils.translation.npgettext_lazy = lazy(
        django.utils.translation.npgettext, unicode)

    # Override the conditional_escape to allow form labels to be marked
    django.utils.html.conditional_escape = lambda html: html

    def custom_resolve(self, context):
        """
        Custom function to resolve variable against a given context as usual,
        but using the overridden transaltion functions.
        """
        if self.lookups is not None:
            # We're dealing with a variable that needs to be resolved
            value = self._resolve_lookup(context)
        else:
            # We're dealing with a literal, so it's already been "resolved"
            value = self.literal
        if self.translate:
            if getattr(self, 'message_context', None):
                return django.utils.translation.pgettext_lazy(
                    self.message_context, value)
            else:
                return django.utils.translation.ugettext_lazy(value)
        return value

    # Set the custom resolve to the Variable class
    django.template.base.Variable.resolve = custom_resolve

    # Make a copy of the function before overridding it
    original_force_unicode = copy.copy(django.utils.encoding.force_unicode)

    def custom_force_unicode(s, encoding='utf-8', strings_only=False,
                             errors='strict'):
        """
        This is a wrapper of django.utils.encoding.force_unicode to
        return SafeUnicode objects instead of unicode, respecting
        protected_types and cases order to keep performance.
         """
        # Handle the common case first, saves 30-40% in performance when s
        # is an instance of unicode. This function gets called often in that
        # setting.
        if isinstance(s, unicode):
            return SafeUnicode(s)
        if strings_only and is_protected_type(s):
            return s
        return SafeUnicode(
            original_force_unicode(s, encoding, strings_only, errors))
    django.utils.encoding.force_unicode = custom_force_unicode
