from odoo import models, fields, api


class life_insurance_lines(models.Model):
    _name = 'life_insurance_lines'

    life_insurance_name = fields.Text(
        string='ชื่อ'
    )


    life_insurance_amount = fields.Float(
        string='ราคา'
    )

    life_insurance_point = fields.Float(
        string='Point',
        compute="_depends_amount",
    )
    life_from_ages = fields.Integer(
        string="ตั้งแต่อายุ (ปี)",
        default=0,
        required=True
    )
    life_to_ages = fields.Integer(
        string="ถึงอายุ (ปี)",
        default=0,
        required=True
    )
    life_insurance_lines_id = fields.Many2one(
        'depa_welfare_basic_setting',
        string="Life Insurance id",
        required=True,
    )

    life_insurance_desc_lines_ids = fields.One2many(
        "life_insurance_desc_lines",
        "life_insurance_desc_lines_id",
        required=True,
        copy=True
    )
    sequence = fields.Integer(
        string='Sequence',
        index=True
    )

    @api.depends('life_insurance_amount')
    def _depends_amount(self):
        for rec in self:
            rec.life_insurance_point = rec.life_insurance_amount / 105

    @api.multi
    def name_get(self):
        res = []
        for obj in self:
            name = obj.life_insurance_name
            res.append((obj.id, name))
        return res



class life_insurance_desc_lines(models.Model):
    _name = 'life_insurance_desc_lines'

    life_insurance_desc = fields.Text(
        string='รายละเอียด'
    )
    life_insurance_package = fields.Float(
        string='ความคุ้มครอง'
    )
    life_insurance_desc_lines_id = fields.Many2one(
        'life_insurance_lines',
        string="Life Insurance Desc id",
        required=True,
    )





