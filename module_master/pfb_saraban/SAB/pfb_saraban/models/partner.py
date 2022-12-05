from odoo import fields, models


class user(models.Model):
    _inherit = 'res.users'
    setting = fields.Boolean(
        'Setting',
        default=False
    )
    document_rec = fields.Boolean(
        'สร้างหนังสือรับ',
        default=False
    )
    document_internal = fields.Boolean(
        'แสดงหนังสือภายในทั้งหมด',
        default=False
    )
    document_rec_all = fields.Boolean(
        'แสดงหนังสือรับทั้งหมด',
        default=False
    )
    # super_user=fields.Boolean(
    #     'Super User',
    #     default=False
    # )

    def group_set(self):
        print("")


class hr(models.Model):
    _inherit = 'hr.employee'
    dummy = fields.Boolean(
        'Dummy',
        default=False
    )
