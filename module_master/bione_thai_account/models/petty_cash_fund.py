# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class AccountPettyFund(models.Model):
    _name="account.petty.fund"
    _description = "Account Petty Cash Fund"
    _order="name"


    # def _balance(self):
    #     #vals={}
    #     for fund in self:
    #         amt=0.0
    #         fund_move = fund.env["account.cash.move"].search([('fund_id','=',fund.id)])
    #         for move in fund_move:
    #             if move.state!="posted":
    #                 continue
    #             if move.petty_id and move.petty_id.state != 'posted':
    #                 continue
    #             if move.type=='in':
    #                 amt += move.amount
    #             elif move.type=='out':
    #                 amt -= move.amount
    #         fund.balance=amt
    #     return True


    name = fields.Char("Name",required=True)
    code = fields.Char("Code",required=True)
    max_amount = fields.Float("Max Amount",required=True)
    account_id = fields.Many2one("account.account","Account",domain=[('deprecated', '=', False)],required=True,index=True)
    # balance = fields.Float(compute='_balance',string="Current Balance")
    notes = fields.Text("Notes")
    # moves = fields.One2many("account.cash.move","fund_id","Cash Moves")
    active = fields.Boolean('Active',help="You can deactive instead of remove this Petty Cash Fund")
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id,required=True,index=True)


    @api.model
    def create(self, vals):
        pay = super(AccountPettyFund, self).create(vals)
        pay._code()
        pay._maxamount()
        pay.active ='t'
        return pay

    def _maxamount(self):
        for petty in self:
            max_amount = petty.max_amount
            if max_amount > 100000:
                raise UserError(_('Amount Maximum 100,000 Bath.'))

    def unlink(self):
        raise UserError(_('You cannot delete. You must cancel only.'))

    def _code(self):
        code = self.env['account.petty.fund'].search([('code','=',self.code)])
        if code:
            raise UserError(_(' Code was already (%s)'%(self.code)))

