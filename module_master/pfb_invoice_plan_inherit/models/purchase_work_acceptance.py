from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math


class PurchaseWorkAcceptanceInherit(models.Model):
    _inherit = 'work.acceptance'

    @api.multi
    def button_accept(self, vals, force=False):
        instalment_wa = self.instalment_wa
        installment_pl = 0
        for inv in self.purchase_id.invoice_plan_ids:
            if inv.to_invoice == True:
                installment_pl = inv.installment
                amount_pl = inv.amount_invoice_plan
        sum_amount = 0
        for wa in self.wa_line_ids:
            sum_amount += wa.price_subtotal
        if self.purchase_id.invoice_plan_ids:
            for rec in self:
                if instalment_wa != installment_pl:
                    raise ValidationError(_("จำนวนงวดที่ไม่ตรงกับงวดในแผนใบแจ้งหนี้"))

                if math.ceil(sum_amount) != math.ceil(amount_pl):
                    raise ValidationError(_("จำนวนยอดเงินไม่ตรงกับจำนวนยอดเงินในแผนใบแจ้งหนี้"))

        self._unlink_zero_quantity()
        po_lines = self.purchase_id.order_line
        for po_line in po_lines:
            if po_line.product_id.type not in ['product', 'consu']:
                po_line.qty_received = self.wa_line_ids.filtered(
                    lambda l: l.purchase_line_id == po_line).product_qty
        self.write({'state': 'accept', 'date_accept': fields.Datetime.now()})

    # @api.depends('price_unit')
    # def _compute_set_installment(self):
    #     for rec in self.wa_line_ids:
    #         if rec.price_subtotal != 0:
    #             rec.price_subtotal = rec.price_unit * rec.product_qty
    #             print(rec.price_subtotal)

