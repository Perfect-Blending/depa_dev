from odoo import models, fields, api, _


class MethodRecruitmentInherit(models.Model):
    _inherit = 'purchase.requisition'

    method_of_recruitment = fields.Many2one('method.recruitment', 'Method of recruitment')
