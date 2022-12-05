from odoo import models, fields, api, _


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement	')

    @api.model
    def _prepare_order_from_rfq(self):
        return {
            "name": self.env["ir.sequence"].next_by_code("purchase.order") or "/",
            "order_sequence": True,
            "quote_id": self.id,
            "partner_ref": self.partner_ref,
            "requisition_id": self.requisition_id.id,
        }


class RequisitionTestInherit(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def name_get(self):
        res = []
        context = self._context
        print(context)
        if context.get('show_only_requisition', True):
            for number in self:
                if number.contract_number:
                    name = number.contract_number
                else:
                    name = ''
                res.append((number.id, name))
        else:
            for number in self:
                name = number._get_name()
                res.append((number.id, name))
        return res





