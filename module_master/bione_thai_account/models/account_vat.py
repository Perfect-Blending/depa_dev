# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
# from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

class BioneAccountVat(models.Model):
    _name = "bione.account.vat"
    _description = "Vat"

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.taxid = self.partner_id.vat or ''
            self.depcod = self.partner_id.branch or self.partner_id.branch_no

    @api.onchange('docdat')
    def change_docdat(self):
        self.vatprd = self.docdat

    @api.onchange('vatprd')
    def change_vat_date(self):
        self.vat_period = self.calc_vat_date(self.vatprd)

    def calc_vat_date(self, vatprd):
        if vatprd:
            dtdt = (self.vatprd).strftime('%Y-%m')
            return dtdt
            # print(dtdt.strftime('%m'))  # ได้ 06

        # return datetime.datetime.strptime(vatprd, '%Y-%m-%d').strftime('%m/%Y')
        else:
            return False



    # receivable_id = fields.Many2one('bione.account.receivable', string='เอกสาร')
    # receivable_date = fields.Date(string='ลงวันที่', related='receivable_id.docdat')

    move_line_id = fields.Many2one('account.move.line', string='Move Line', on_delete="restrict")
    customer_payment_id = fields.Many2one('bione.customer.payment', string='Customer Payment', on_delete="restrict")
    customer_deposit_id = fields.Many2one('bione.customer.deposit', string='Customer Deposit', on_delete="restrict")
    customer_receipts_id = fields.Many2one('bione.customer.receipts', string='Customer Receipts', on_delete="restrict")
    supplier_payment_id = fields.Many2one('bione.supplier.payment', string='Supplier Payment', on_delete="restrict")
    supplier_deposit_id = fields.Many2one('bione.supplier.deposit', string='Supplier Deposit', on_delete="restrict")
    supplier_receipts_id = fields.Many2one('bione.supplier.receipts', string='Supplier Receipts', on_delete="restrict")

    invoice_id = fields.Many2one('account.invoice', string='Invoice', on_delete="restrict")

    name = fields.Char(string='เลขที่ใบกำกับภาษี', required=True, copy=False, track_visibility='onchange', default='New')
    docdat = fields.Date(string='ลงวันที่', required=True, track_visibility='onchange', default=lambda self: fields.Date.today())
    vatprd = fields.Date(string='วันที่ยื่น')
    vat_period = fields.Char(string='งวดที่')
    partner_id = fields.Many2one('res.partner', 'พาร์ทเนอร์', required=True)
    taxid = fields.Char(string='เลขประจำตัวผู้เสียภาษี', required=True, copy=True)
    depcod = fields.Char(string='รหัสสาขา', size=5, required=True, copy=True)
    amount_untaxed = fields.Float(string='ยอดก่อนภาษี')
    amount_tax = fields.Float(string='ภาษี')
    amount_total = fields.Float(string='ยอดเงินรวม')
    late = fields.Boolean(string='ยื่นล่าช้า')
    remark = fields.Char(string='หมายเหตุ', size=30)
    vat_type = fields.Selection([('sale', u'ภาษีขาย'), ('purchase', u'ภาษีซื้อ')], string=u'ประเภทภาษี',
                                track_visibility='onchange')
    # vat_inv = fields.Selection([('cash', u'ขายสด'), ('service', u'บริการ')], string=u'ประเภทเอกสาร',
    #                             track_visibility='onchange')

    # order_type = fields.Many2one(comodel_name='invoice.order.type',
    #                              readonly=False,
    #                              string='Type',
    #                              ondelete='restrict')
    order_type = fields.Many2one(
        comodel_name='invoice.order.type',
        string='ประเภทใบกำกับ',
        required=False)


    vatrec = fields.Char(string='vatrec', size=1)
    vattyp = fields.Char(string='vattyp', size=1)
    rectyp = fields.Char(string='rectyp', size=1)
    # period_id = fields.Many2one('bione.account.period', string='งวดภาษี', required=True)
    refnum = fields.Char(string='refnum', size=15)
    newnum = fields.Char(string='newnum', size=10)
    descrp = fields.Char(string='descrp', size=60)
    amt01 = fields.Float(string='amt01', digits=(8, 2))
    vat01 = fields.Float(string='vat01', digits=(8, 2))
    amt02 = fields.Float(string='รายได้จากการขาย', digits=(8, 2))
    vat02 = fields.Float(string='จำนวนภาษีมูลค่าเพิ่ม', digits=(8, 2))
    amtrat0 = fields.Float(string='amtrat0', digits=(8, 2))
    self_added = fields.Char(string='self_added', size=1)
    had_modify = fields.Char(string='had_modify', size=1)
    docstat = fields.Char(string='docstat', size=1)
    orgnum = fields.Integer(string='orgnum')
    prenam = fields.Char(string='prenam', size=15)
    advance_clear_id = fields.Many2one('account.advance.clear', string='Advance Clear', ondeleted='cascade',
                                       index=True, )

    def get_by_date(self):
        return datetime.now().date

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' and vals.get('order_type'):
            invoice_type = self.env['invoice.order.type'].browse(
                vals['order_type'])
            if invoice_type.sequence_id:
                vals['name'] = invoice_type.sequence_id.next_by_id()
        return super().create(vals)


    # @api.model
    # def create(self, vals):
    #     # if self.vat_inv == 'cash' :
    #     #     vals['name'] = self.env['ir.sequence'].next_by_code('bione.customer.receipts.inv.cash')
    #     #     receipt1_id = super(BioneAccountVat, self.with_context(mail_create_nosubscribe=True)).create(vals)
    #     #     return receipt1_id
    #     # if self.vat_inv == 'service' :
    #         vals['name'] = self.env['ir.sequence'].next_by_code('bione.customer.receipts.inv.service')
    #         receipt2_id = super(BioneAccountVat, self.with_context(mail_create_nosubscribe=True)).create(vals)
    #         return receipt2_id
    #
    # @api.model
    # def create(self, vals):
    #     if vals.get('name', '/') == '/' and vals.get('vat_inv'):
    #         purchase_type = self.env['purchase.order.type'].browse(
    #             vals['vat_inv'])
    #         if purchase_type.sequence_id:
    #             vals['name'] = purchase_type.sequence_id.next_by_id()
    #     return super().create(vals)
    #

    # move_id = fields.Many2one('account.move', string=u'สมุดรายวัน', index=True)

    # @api.onchange('vatprd')
    # def change_vat_date(self):
    #     self.vat_period = self.vatprd
    #     # print(date_time_object.strfrtime('%m%d%y'))

    # self.vat_period = self.calc_vat_date(self.vatprd)

    # def calc_vat_date(self, vatprd):
    #     if vatprd:
    #         return datetime.date.strptime(vatprd,'%m/%Y')
    #     else:
    #         return False

    # print(date_time_object.strfrtime('%m%d%y'))
    # return datetime.datetime.strptime(vat_date, '%Y-%m-%d').strftime('%m/%Y')