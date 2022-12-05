from odoo import models, fields, api, _


class AccountChequeInherit(models.Model):
    _inherit = 'account.cheque'

    payee_user_id = fields.Many2one('res.partner', string='Payee', domain="[('supplier','=',True),('parent_id','=',"
                                                                         "False)]")
    bank_name = fields.Many2one('res.partner.bank', string='Bank')

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.multi
    def name_get(self):
        res = []
        context = self._context
        if context.get('show_only_bank', True):
            for bank in self:
                name = bank.bank_id.name + (bank.bank_id.branch_bank and (' - ' + bank.bank_id.branch_bank) or '')
                res.append((bank.id, name ))
        else:
            for bank in self:
                name = bank._get_name()
                res.append((bank.id, name ))
        return res