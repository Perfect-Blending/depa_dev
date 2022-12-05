# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.addons.ac_account_thai.models.num2word import num2word
from datetime import *
from odoo.tools.safe_eval import safe_eval

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    cheque_ids = fields.One2many('bione.cheque', 'supplier_payment_id', string=u'เช็คจ่าย')
    vat_ids = fields.One2many('bione.account.vat', 'supplier_payment_id', string=u'ภาษีซื้อ')
    wht_ids = fields.One2many('bione.wht', 'supplier_payment_id', string=u'ภาษีหัก ณ ที่จ่าย')

    move_id = fields.Many2one('account.move', string=u'สมุดรายวัน', index=True)
    move_line_ids = fields.One2many(related="move_id.line_ids", string="Journal Items", readonly=True, copy=False)



