from odoo import models, fields, api, _

POSITION_INDEX = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),
                  (11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20)]


class settingInherit(models.Model):
    _inherit = 'document.internal.setting'

    @api.model
    def create(self, vals):
        res = super(settingInherit, self).create(vals)
        res.make_order_setting_line()
        return res

    @api.multi
    def write(self, vals):
        res = super(settingInherit, self).write(vals)
        self.make_order_setting_line()
        return res

       
# class SettingLineInherit(models.Model):
#     _inherit = 'document.internal.setting.lines'
#     _order = 'position_index asc'
#
#     position_index = fields.Selection(POSITION_INDEX, string='Approve Index')
#
#
# class settingExternalInherit(models.Model):
#     _inherit = 'document.external.setting'
#
#     @api.multi
#     def generate_index(self):
#         if self.id:
#             count = 0
#             if self.user_id:
#                 count = len(self.user_id) + 1
#                 for ap in self.user_id:
#                     if ap.id:
#                         count = count - 1
#                         apid = self.env['document.internal.setting.lines'].browse(ap.id)
#                         apid.write({"position_index": int(count)})
#
# class SettingLineExternalInherit(models.Model):
#     _inherit = 'document.external.setting.lines'
#     _order = 'position_index asc'
#
#     position_index = fields.Selection(POSITION_INDEX, string='Approve Index')


