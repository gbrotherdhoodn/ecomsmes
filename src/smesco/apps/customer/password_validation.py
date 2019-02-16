from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AlphabetPasswordValidator:
    def validate(self, password, user=None):
        if password.isalpha():
            raise ValidationError(
                _("The password cannot contain only alphabet characters."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "The password cannot contain only alphabet characters."
        )
