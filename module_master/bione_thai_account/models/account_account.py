# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    name2 = fields.Char(string=u'Secondary Name', copy=False, track_visibility=True)
    tax_sale_ok = fields.Boolean(string=u'Sale Tax', copy=False, track_visibility=True)
    tax_purchase_ok = fields.Boolean(string=u'Purchase Tax', copy=False, track_visibility=True)
    cheque_in_ok = fields.Boolean(string=u'Cheque In', copy=False, track_visibility=True)
    cheque_out_ok = fields.Boolean(string=u'Cheque Out', copy=False, track_visibility=True)
    deposit_ok = fields.Boolean(string=u'Deposit', copy=False, track_visibility=True)
    wht_purchase_ok = fields.Boolean(string=u'Purchase WHT', copy=False, track_visibility=True)
    wht_sale_ok = fields.Boolean(string=u'Sale WHT', copy=False, track_visibility=True)

