from odoo import models, fields, api, _


class MethodOfRecruitment(models.Model):
    _name = 'method.recruitment'
    _description = 'Method Of Recruitment'
    _parent_name = "partner_id"
    _order = 'complete_name'
    _rec_name = 'complete_name'

    name = fields.Char(string='Method of recruitment', required=True)
    complete_name = fields.Char("Full Location Name", compute='_compute_complete_name', store=True)
    partner_id = fields.Many2one('method.recruitment', 'Parent', index=True, ondelete='cascade')
    active = fields.Boolean(default=True)

    @api.one
    @api.depends('name', 'partner_id.complete_name')
    def _compute_complete_name(self):
        if self.partner_id.complete_name:
            self.complete_name = '%s/%s' % (self.partner_id.complete_name, self.name)
        else:
            self.complete_name = self.name






