from odoo import models, fields, api, _


class AccountBillingInherit(models.Model):
    _inherit = 'document.internal.main'

    @api.onchange('reference_line_ids_multi')
    def _onchange_partner_type(self):
        domain = {}
        if self.reference_line_ids_multi:
            doc = self.reference_line_ids_multi
            print(doc)
        print(domain)
        return domain


