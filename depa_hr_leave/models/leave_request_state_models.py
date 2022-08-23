# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


class state_colors(models.Model):
    _name = 'leave_request_state'

    state = fields.Char(
        string="state",
        required=True
    )

    name = fields.Char(
        string="สถานะ",
        required=True
    )

    active = fields.Boolean(
        string="active",
        default=True
    )