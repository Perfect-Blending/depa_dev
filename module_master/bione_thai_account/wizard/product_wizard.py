from odoo import models, fields, api


# from odoo.addons.bione_thai_account import BioneSupplierReceiptsLine

class ProductWizard(models.TransientModel):
    _name = 'product.multi.receipt.vendor.wizard'
    rc_id = fields.Integer('RC ID')
    product_ids = fields.Many2many('product.template', string='Products')

    def do_confirm_add_product(self):
        rc = self.env['bione.supplier.receipts'].browse([self.rc_id])
        for p in self.product_ids:
            bione.supplier.receipts.line.sudo().create({
                'pr_id': rc.id,
                'product_id': p.id,
                'qty': 1,
                'price': p.list_price,
                'amount': p.list_price,
            })
