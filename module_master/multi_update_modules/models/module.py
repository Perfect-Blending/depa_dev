from odoo import api, models


class Module(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def button_update_modules(self):
        return self.button_immediate_upgrade()
