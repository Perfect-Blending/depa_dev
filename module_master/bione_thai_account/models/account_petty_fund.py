# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.osv import expression


class AccountPettyFund(models.Model):
    _name="account.petty.fund"
    _order="name"

    @api.depends('partner_id', 'account_id')
    def _balance(self):
        aml_env = self.env['account.move.line']
        for rec in self:
            # aml = aml_env.search([('partner_id', '=', rec.partner_id.id),
            #                       ('account_id', '=', rec.account_id.id)])
            aml = aml_env.search([('account_id', '=', rec.account_id.id)])
            # print(aml)
            balance = sum([line.debit - line.credit for line in aml])
            # print(balance)
            rec.balance = balance

    name = fields.Char("Name",required=True)
    code = fields.Char("Code",required=True)
    max_amount = fields.Float("Max Amount",required=True)
    account_id = fields.Many2one("account.account","Account",domain=[('deprecated', '=', False)],required=True,index=True)
    balance = fields.Float(compute='_balance',string="Current Balance")
    notes = fields.Text("Notes")
    moves = fields.One2many("account.cash.move","fund_id","Cash Moves")
    active = fields.Boolean('Active',help="You can deactive instead of remove this Petty Cash Fund")
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id,required=True,index=True)
    partner_id = fields.Many2one('res.partner', 'Petty Cash Holder', domain="[('supplier','=',True)]")

    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)',
         'Petty Cash Holder must be unique!'),
    ]

    @api.model
    def create(self, vals):
        pay = super(AccountPettyFund, self).create(vals)
        pay._code()
        pay._maxamount()
        pay.active ='t'
        return pay

    @api.multi
    def _maxamount(self):
        for petty in self:
            max_amount = petty.max_amount
            if max_amount > 100000:
                raise UserError(_('Amount Maximum 100,000 Bath.'))

    @api.multi
    def unlink(self):
        raise UserError(_('You cannot delete. You must cancel only.'))

    def _code(self):
        code = self.env['account.petty.fund'].search([('code','=',self.code)])
        if code:
            raise UserError(_(' Code was already (%s)'%(self.code)))

