from odoo import models, fields, api, _


class WorkAcceptanceInherit(models.Model):
    _inherit = 'res.bank'

    branch_bank = fields.Char(string='Branch')

    # cheque_no = fields.Char(string='Cheque No.', states={'draft': [('readonly', False)]}, readonly=True,)
    @api.multi
    def name_get(self):
        result = []
        for bank in self:
            name = bank.name + (bank.branch_bank and (' - ' + bank.branch_bank) or '')
            result.append((bank.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('branch_bank', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        bank_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(bank_ids).name_get()
