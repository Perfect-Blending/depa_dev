from odoo import models, fields, api, _
from odoo.osv import expression


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"

    job_organization = fields.Many2one(
        'hr.job',
        string='Job Organization',
    )

    @api.onchange('job_id')
    @api.multi
    def _onchange_job_id(self):
        for rec in self:
            rec.job_organization = rec.job_id.id
            rec.job_title = rec.job_id.name

    @api.multi
    def name_get(self):
        res = []
        for line in self:
            if self.env.context.get('job_id_searchable', False):
                if line.job_title:
                    name = "[%s] %s" % (line.job_id.name, line.name)
                else:
                    name = "%s" % (line.name)
            elif self.env.context.get('job_title_searchable', False):
                if line.job_title:
                    name = "[%s] %s" % (line.job_title, line.name)
                else:
                    name = "%s" % (line.name)
            else:
                name = "%s" % (line.name)
            res.append((line.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('job_id_searchable', False):
            employee_ids = self.search(['|', ('name', operator, name), ('job_id.name', operator, name)])
        elif self.env.context.get('job_title_searchable', False):
            employee_ids = self.search(['|', ('name', operator, name), ('job_title', operator, name)])
        else:
            employee_ids = self.search([('name', operator, name)])
        return employee_ids.name_get()
