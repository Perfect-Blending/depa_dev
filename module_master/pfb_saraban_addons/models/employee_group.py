from odoo import models, fields, api, _

class DocumentEmployeeGroups(models.Model):
    _name = "document.employee.groups"

    group_name = fields.Char(required=True)
    active = fields.Boolean(default=True, string="สถานะ")
    flag = fields.Boolean(default=True, string="Public")
    hr_employee_ids = fields.Many2many(
        "hr.employee",
        "document_group_employee_rel",
        "group_id",
        "employee_id"
    )

    @api.multi
    def name_get(self):
        return [(group.id, group.group_name) for i, group in enumerate(self)]

    @api.model
    def name_search(self, name, args=None, operator='like', limit=100):
        if not args:
            args = []
        if name:
            result = self._search(args + [
                ('group_name', operator, name)
            ])
        else:
            result = self._search(args, limit=limit)
        # print(result)
        return self.browse(result).name_get()
