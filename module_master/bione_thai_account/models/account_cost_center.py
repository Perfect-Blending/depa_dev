from odoo import fields, models, api


class AccountCostCenter(models.Model):
    _inherit = 'account.cost.center'

    @api.multi
    def name_get(self):
        res = []
        for cost in self:
            name = cost.name
            if cost.code:
                name = '[' + cost.code + '] ' + name
            # if cost.partner_id:
            #     name = name + ' - ' + cost.partner_id.commercial_partner_id.name
            res.append((cost.id, name))
        return res
