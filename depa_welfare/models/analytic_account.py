# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from dateutil import relativedelta

# Fix default fiscal year start month on October
START_MONTH = 10

class fw_pfb_fin_fiscal_year_inherit(models.Model):
    _inherit = 'fw_pfb_fin_system_fiscal_year'
    _order = 'fiscal_year desc'

    def _default_date_start(self):
        today = date.today()
        # Fix default start on 01/10 every year
        default_start_month = START_MONTH
        default_start_date = 1
        # Get current date in array format
        current_date = date.strftime(date.today(), '%Y-%m-%d').split('-')
        if int(current_date[1]) >= default_start_month:
            year = int(current_date[0]) + 1
        else:
            year = int(current_date[0])

        date_start = date(year, default_start_month, default_start_date)
        return date_start

    def _default_date_end(self):
        today = date.today()

        # Fix default end on 30/09 every year
        default_end_month = 9
        default_end_date = 30
        default_start_month = START_MONTH
        # Get current date in array format
        current_date = date.strftime(date.today(), '%Y-%m-%d').split('-')
        if int(current_date[1]) >= default_start_month:
            year = int(current_date[0]) + 2
        else:
            year = int(current_date[0]) + 1

        date_end = date(year, default_end_month, default_end_date)
        return date_end


    date_start = fields.Date(
        default=_default_date_start,
        required=True,
    )
    date_end = fields.Date(
        default=_default_date_end,
        required=True,
    )
