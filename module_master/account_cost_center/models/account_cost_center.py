# Copyright 2015-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountCostCenter(models.Model):
    _name = 'account.cost.center'
    _description = 'Account Cost Center'

    name = fields.Char(string='Title', required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for cost in self:
    #         name = cost.name
    #         if cost.code:
    #             name = '[' + cost.code + '] ' + name
    #         # if cost.partner_id:
    #         #     name = name + ' - ' + cost.partner_id.commercial_partner_id.name
    #         res.append((cost.id, name))
    #     return res

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     if not args:
    #         args = []
    #     if name:
    #         args += ['|', ('name', operator, '%' + name + '%'), ()]

    # @api.model
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = '[ID=' + str(record.id) + ']' + '' + record.name
    #         result.append((record.id, name))
    #     return result