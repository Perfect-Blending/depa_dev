from odoo import models, fields, api, _


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one('res.partner', string='Vendors', domain="[('supplier','=',True),('parent_id','=',"
                                                                         "False)]")
    contact_person = fields.Many2one('res.partner', string='Contact')


class ResPartnerPartnerChildName(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        res = []
        context = self._context
        if context.get('show_only_child', True):
            for partner in self:
                name = partner.name
                res.append((partner.id, name))
        else:
            for partner in self:
                name = partner._get_name()
                res.append((partner.id, name))
        return res
