# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import bahttext


class BioneWhtType(models.Model):
    _name = 'bione.wht.type'

    name = fields.Char(string='Description', required=True)
    printed = fields.Char(string='To Print')
    sequence = fields.Integer(string='Sequence')

    _sql_constraints = [
        ('bione_wht_unique', 'unique (sequence)', 'Sequence must be unique!')
    ]


class BioneWhtLine(models.Model):
    _name = 'bione.wht.line'
    _description = 'With Holding Tax Line'

    @api.one
    @api.depends('percent', 'base_amount')
    def _compute_tax(self):
        if self.percent and self.base_amount:
            self.tax = (self.percent / 100) * self.base_amount

    name = fields.Char(string='คำอธิบาย', track_visibility=True)
    wht_type_id = fields.Many2one('bione.wht.type', string='ประเภท', required=True, track_visibility=True)
    date_doc = fields.Date(string='วันที่', required=True, default=fields.Datetime.now(), track_visibility=True)
    percent = fields.Float(string='เปอร์เซ็นต์', digits=(12,2), default=1.0, track_visibility=True)
    wht_id = fields.Many2one('bione.wht', string='With Holding Tax', copy=False, track_visibility=True)
    note = fields.Text(string='หมายเหตุ', track_visibility=True)
    base_amount = fields.Float(string='ฐานภาษี', digits=(12,2), copy=False, track_visibility=True )
    tax = fields.Float(string='ภาษี', digits=(12, 2), compute='_compute_tax' )


class BioneWhtPnd(models.Model):
    _name = 'bione.wht.pnd'
    _description = "WHT PND"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.one
    @api.depends('wht_ids')
    def _attachment_count(self):
        self.attach_count = len(self.wht_ids)
        self.attach_no = len(self.wht_ids) / 6 + 1
        val = val1 = 0.0
        for line in self.wht_ids:
            val1 += line.base_amount
            val += line.tax
        self.total_tax = val
        self.total_amount = val1
        self.total_tax_send = val + self.add_amount or 0.0

    name = fields.Char(string='Description', track_visibility=False)
    date_pnd = fields.Date(string='Date', required=True, track_visibility=False)
    type_normal = fields.Boolean(string='Type Normal', track_visibility=False)
    type_special = fields.Boolean(string='Type Special', track_visibility=False)
    type_no = fields.Boolean(string='Type No', track_visibility=False)
    section_3 = fields.Boolean(string='Section 3', track_visibility=False)
    section_48 = fields.Boolean(string='Section 48', track_visibility=False)
    section_50 = fields.Boolean(string='Section 50', track_visibility=False)
    section_65 = fields.Boolean(string='Section 65', track_visibility=False)
    section_69 = fields.Boolean(string='Section 69', track_visibility=False)
    attach_pnd = fields.Boolean(string='Attach PND', track_visibility=False)
    wht_ids = fields.Many2many('bione.wht', 'bione_wht_pnds', 'pnd_id', 'wht_id', 'With holding tax')
    attach_count = fields.Integer(string='Attach Count', compute='_attachment_count')
    attach_no = fields.Integer(string='Attach No', compute='_attachment_count')
    total_amount = fields.Float(string='Total Amount', digits=(12,2), compute='_attachment_count')
    total_tax = fields.Float(string='Total Tax', digits=(12,2), compute='_attachment_count')
    total_tax_send = fields.Float(string='Tax Send', digits=(12,2), compute='_attachment_count')
    add_amount = fields.Float(string='Add Amount', digits=(12,2), default=0.0, track_visibility=False)
    note = fields.Text(string='Note', track_visibility=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    pnd_type = fields.Selection([('pp4', '(4) PP3'), ('pp7', '(7) PP53')], 'PND Type', required=True,
        select=True, track_visibility=False)
    #'period_tax_id': fields.many2one('account.period', 'Tax Period'),


class BioneWht(models.Model):
    _name = 'bione.wht'
    _description = 'Fiscal Year'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date_doc desc,name desc'

    @api.one
    @api.depends('line_ids')
    def _compute_amount(self):
        val = val1 = 0.0
        for line in self.line_ids:
            val1 += line.base_amount
            val += line.tax
        self.tax = val
        self.base_amount = val1
        self.tax_text = '- '+bahttext.bahttext(val)+' -'

    @api.one
    @api.depends('company_id')
    def _get_company_vat(self):
        if self.company_id:
            self.company_full_address = (self.company_id.partner_id.street or '') + ' ' + \
                                        (self.company_id.partner_id.street2 or '') + ' '+ \
                                        (self.company_id.partner_id.city or '')

    @api.one
    @api.depends('partner_id')
    def _get_supplier_vat(self):
        self.partner_full_address = (self.partner_id.street or '') + ' ' + \
                                    (self.partner_id.street2 or '') + ' '+ \
                                    (self.partner_id.city or '')

    @api.one
    @api.depends()
    def _get_moveline(self):
        sql = 'select id from account_move_line where wht_id = %s' % (self.id)
        self._cr.execute(sql)
        res = self._cr.fetchone()
        self.move_line_id = res and res[0] or False

    @api.one
    @api.depends('line_ids')
    def _get_line_value(self):
        number5_id = 999
        number6_id = 999
        for line in self.line_ids:
            if line.wht_type_id.id == number5_id:
                self.has_number_5 = True
                self.number5_base_amount = line.base_amount
                self.number5_tax = line.tax
            elif line.wht_type_id.id == number6_id :
                self.has_number_6 = True
                self.number6_base_amount = line.base_amount
                self.number6_tax = line.tax
                self.number6_note = line.note

    name = fields.Char(string='เลขที่', required=True, default='/')
    date_doc = fields.Date(string='ลงวันที่', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    company_vat_no = fields.Char(string='Company Vat No', related='company_id.vat', readonly=True)

    company_full_address = fields.Char(string='Company Address',
        store=True, readonly=True, compute='_get_company_vat', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='พาร์ทเนอร์', required=True)
    partner_vat_no = fields.Char(string='Vat No', related='partner_id.vat', readonly=True)
    partner_full_address = fields.Char(string='Partner',
        store=True, readonly=True, compute='_get_supplier_vat', track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account')
    sequence = fields.Integer(string='Sequence', defaults=100)
    wht_type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase')], string='ประเภท')
    wht_kind = fields.Selection([('pp1', '(1) PP1'),
                                  ('pp2', '(2) PP1'),
                                  ('pp3', '(3) PP2'),
                                  ('pp4', '(4) PP3'),
                                  ('pp5', '(5) PP2'),
                                  ('pp6', '(6) PP2'),
                                  ('pp7', '(7) PP53'),
                                  ], string='ภงด.', default='pp7')
    wht_payment = fields.Selection([('pm1', '(1) With holding tax'),
                                     ('pm2', '(2) Forever'),
                                     ('pm3', '(3) Once'),
                                     ('pm4', '(4) Other'),
                                     ], string='การชำระ', default='pm1')
    note = fields.Text(string='หมายเหตุ')
    line_ids = fields.One2many('bione.wht.line', 'wht_id', string='WHT Lines')
    base_amount = fields.Float(string='ยอดเงิน', digits=(12,2), compute='_compute_amount')
    tax = fields.Float(string='ภาษี', digits=(12,2), compute='_compute_amount')
    tax_text = fields.Char(string='Baht Tax', compute='_compute_amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], 'Status', readonly=True, )
    voucher_id = fields.Many2one('account.voucher', string='Voucher')
    move_line_id = fields.Many2one('account.move.line', string='Move Line', compute='_get_moveline')
    has_number_5 = fields.Boolean(string='Is No 5', compute='_get_line_value')
    number5_base_amount = fields.Float(string='Base Amount', compute='_get_line_value', digits=(12,2))
    number5_tax = fields.Float(string='Tax', compute='_get_line_value', digits=(12,2))
    has_number_6 = fields.Boolean(string='Is No 6', compute='_get_line_value')
    number6_base_amount = fields.Float(string='Base Amount', compute='_get_line_value', digits=(12,2))
    number6_tax = fields.Float(string='Tax', compute='_get_line_value', digits=(12,2))
    number6_note = fields.Char(string='Note', compute='_get_line_value',)
    move_line_id = fields.Many2one('account.move.line', string='Move Line', on_delete="restrict")
    customer_payment_id = fields.Many2one('bione.customer.payment', string='Customer Payment', on_delete="restrict")
    customer_deposit_id = fields.Many2one('bione.customer.deposit', string='Customer Deposit', on_delete="restrict")
    customer_receipts_id = fields.Many2one('bione.customer.receipts', string='Customer Receipts', on_delete="restrict")
    supplier_payment_id = fields.Many2one('bione.supplier.payment', string='Supplier Payment', on_delete="restrict")
    supplier_deposit_id = fields.Many2one('bione.supplier.deposit', string='Supplier Deposit', on_delete="restrict")
    supplier_receipts_id = fields.Many2one('bione.supplier.receipts', string='Supplier Receipts', on_delete="restrict")
    advance_clear_id = fields.Many2one('account.advance.clear', string='Advance Clear', ondeleted='cascade',
                                       index=True, )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bione.wht')
        wht_id = super(BioneWht, self.with_context(mail_create_nosubscribe=True)).create(vals)
        return wht_id