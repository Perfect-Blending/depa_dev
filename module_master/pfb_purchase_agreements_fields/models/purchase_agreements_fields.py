from odoo import models, fields, api, _


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    contract_number = fields.Char(string='Contract Number', required=True)
    line_agreement = fields.One2many('purchase.requisition.test', 'test_id')


class PurchaseRequisitionTest(models.Model):
    _name = 'purchase.requisition.test'

    @api.onchange('test_one')
    def set_position(self):
        for rec in self:
            if rec.test_one:
                rec.test_three = rec.test_one.department_id.name

    test_one = fields.Many2one('hr.employee', string='Employees')
    test_two = fields.Many2one('jop.position.work', string='Position')
    test_three = fields.Char(string='Department', readonly=True, related='test_one.department_id.name')
    test_id = fields.Many2one('purchase.requisition', string='Test_ID')


