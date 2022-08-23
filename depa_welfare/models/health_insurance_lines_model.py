from odoo import models, fields, api


class health_insurance_lines(models.Model):
    _name = 'health_insurance_lines'

    health_insurance_name = fields.Text(
        string='ชื่อ'
    )

    health_insurance_amount = fields.Float(
        string='ราคา'
    )

    health_insurance_point = fields.Float(
        string='Point',
        compute="_depends_amount",
    )
    health_from_ages = fields.Integer(
        string="ตั้งแต่อายุ (ปี)",
        default=0,
        required=True
    )
    health_to_ages = fields.Integer(
        string="ถึงอายุ (ปี)",
        default=0,
        required=True
    )
    health_insurance_lines_id = fields.Many2one(
        'depa_welfare_basic_setting',
        string="Health Insurance id",
        required=True,
    )

    health_insurance_desc_lines_ids = fields.One2many(
        "health_insurance_desc_lines",
        "health_insurance_desc_lines_id",
        required=True,
        copy=True
    )
    sequence = fields.Integer(
        string='Sequence',
        index=True
    )

    disable_employee = fields.Boolean(
        string='พนักงานไม่สามารถเลือกได้',
        default=False,
    )

    @api.depends('health_insurance_amount')
    def _depends_amount(self):
        for rec in self:
            rec.health_insurance_point = rec.health_insurance_amount / 105

    @api.multi
    def name_get(self):
        res = []
        for obj in self:
            name = obj.health_insurance_name
            res.append((obj.id, name))
        return res



class health_insurance_desc_lines(models.Model):
    _name = 'health_insurance_desc_lines'

    health_insurance_desc = fields.Text(
        string='รายละเอียด'
    )
    health_insurance_package = fields.Float(
        string='ความคุ้มครอง'
    )
    health_insurance_desc_lines_id = fields.Many2one(
        'health_insurance_lines',
        string="health Insurance Desc id",
        required=True,
    )



