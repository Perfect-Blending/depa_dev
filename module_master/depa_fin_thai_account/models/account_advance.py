# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AccountAdvance(models.Model):
    _inherit = "account.advance"

    title_id = fields.Many2one('fw_pfb_objective', 'วัตถุประสงค์', required=False)