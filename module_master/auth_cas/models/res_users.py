# -*- coding: utf-8 -*-



from odoo import api, fields, models
from odoo.exceptions import AccessDenied

import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    """The field declared here is used
    in order to check autenticity of logins
    """

    _inherit = 'res.users'

    cas_key = fields.Char('CAS Key', size=16, readonly=True)

    @api.model
    def check_credentials(self, password):
        """Check Authenticy of logins"""
        # We try to connect the user with his password by the standard way
        try:
            return super(ResUsers, self).check_credentials(password)
        # If it failed, we try to do it thanks to
        # the cas key created by the Controller
        except AccessDenied:
            if not password:
                raise AccessDenied()
            self._cr.execute("""SELECT COUNT(1)
                                FROM res_users
                               WHERE id=%s
                                 AND cas_key=%s""",
                             (int(self._uid), password))
            if not self._cr.fetchone()[0]:
                raise AccessDenied()
