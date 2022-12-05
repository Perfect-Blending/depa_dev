from odoo import models, fields, api, _


class WTCertificates(models.Model):
    _inherit = 'withholding.tax.cert'

    number_wt = fields.Char(string="Number", index=True, copy=False, default=lambda self: _('New'))

    @api.multi
    def write(self, vals):
        if self.state == 'draft':
            if self.number_wt == 'New' or self.number_wt == 'ใหม่':
                if vals.get('number_wt', _('New')) == _('New'):
                    vals['number_wt'] = self.env['ir.sequence'].next_by_code('withholding.tax.cert.sequence') or _('New')
        result = super(WTCertificates, self).write(vals)
        return result




