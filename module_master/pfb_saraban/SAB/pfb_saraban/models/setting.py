from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
import requests as r
def send(msg):
    token = 'GB3DOAbe7Eu5vvVUQ3UFMMcNE8No1YqwR7zj3Rp9hDE'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    url = 'https://notify-api.line.me/api/notify'
    r.post(url, headers=headers, data={'message': msg})

class setting(models.Model):
    _name = 'document.internal.setting'
    _description = 'สารบรรณ'

    name = fields.Char(
        string='ชื่อ',
        required=True,
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    user_id = fields.One2many(
        'document.internal.setting.lines',
        'document_id',
        string='Approval',
        required=True,
        copy=True
    )
    

    def make_order_setting_line(self):
        user_id = self.user_id.sorted(lambda x: x.step)
        sequence = 0
        for slid in user_id:
            slid.update({"sequence":sequence})
            sequence += 1
       
class SettingLine(models.Model):
    _name = 'document.internal.setting.lines'
    _description = 'สารบัญ'
    # _order = 'step,sequence'
    _order='step asc'
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    job_id_name = fields.Many2one('hr.job', string="Job name")
    step = fields.Selection(string="Step", selection=[
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6')
    ], default='1',index=True)
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผอ.ฝ่าย'),
        ('2', 'ฝ่ายที่เกี่ยวข้อง-1'),
        ('3', 'ชสศด.'),
        ('4', 'รสศด.'),
        ('5', 'ฝ่ายที่เกี่ยวข้อง-2'),
        ('6', 'ผสศด.')
    ], default='1', readonly=True, compute='set_step')

    approve_type = fields.Selection(string="Approve type", selection=[
        ('require', 'Is require to approve'),
        ('comments', 'Comments only')],
        default='require')
    document_id = fields.Many2one(
        'document.internal.setting',
        string="Document id"
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(string='Sequence', index=True,default=10)

    @api.depends('step')
    # @api.onchange('step')
    def set_step(self):
        # self.ensure_one()
        for record in self:
            if record.step:
                step = record.step
                # record.update({'status':step})
                record.status = step
        # document_id=self.document_id.user_id
        # for i in document_id:
        #     print(i)
        # self.document_id.user_id=False
        # print(document_id)
        # self.document_id.user_id=document_id


class settingExternal(models.Model):
    _name = 'document.external.setting'
    _description = 'สารบรรณ'

    name = fields.Char(
        string='ชื่อ',
        required=True,
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    user_id = fields.One2many(
        'document.external.setting.lines',
        'document_id',
        string='Approval',
        required=True,
        copy=True
    )
    def make_order_setting_line(self):
        user_id = self.user_id.sorted(lambda x: x.step)
        sequence = 0
        for slid in user_id:
            slid.update({"sequence":sequence})
            sequence += 1

class SettingLineExternal(models.Model):
    _name = 'document.external.setting.lines'
    _description = 'สารบัญ'
    _order = 'step,sequence,id'
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    # job_title = fields.Char(string="job title", related='employee_id.job_title', required=True, readonly=True)
    active = fields.Boolean(default=True, help="Set active to false to hide without removing it.")
    job_id_name = fields.Many2one('hr.job', string="Job name")
    step = fields.Selection(string="Step", selection=[
        ('1', '1'),
        ('2', '2')
    ], default='1')
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผอ.ฝ่าย'),
        ('2', 'ฝ่ายที่เกี่ยวข้อง')
    ], default='1', readonly=True, compute='set_step')
    approve_type = fields.Selection(string="Approve type", selection=[
        ('comments', 'Comments only')], default='comments')
    document_id = fields.Many2one(
        'document.external.setting',
        string="Document id"
    )
    is_active = fields.Boolean(
        string='Active ',
        default=True,
    )
    sequence = fields.Integer(string='Sequence', index=True,default=10)

    @api.depends('step')
    def set_step(self):
        for record in self:
            if record.step:
                step = record.step
                record.update({'status': step})
                
                
class DocumentTag(models.Model):
    _name = "document.internal.setting.tag"
    _description = "Document tag"

    name = fields.Char(string="Document Tag", required=True, copy=False)
    color = fields.Integer(string='Color Index')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    
    
class DocumentTemplateSetting(models.Model):
    _name = "document.template.setting"
    _description = "Document Template"

    name = fields.Char(string="Name", required=True)
    document_type = fields.Selection([('บันทึกข้อความ', 'บันทึกข้อความ'),
                                      ('คำสั่ง ก', 'คำสั่ง ก'),
                                      ('คำสั่ง ข', 'คำสั่ง ข'),
                                      ('คำสั่ง ค', 'คำสั่ง ค'),
                                      ('คำสั่ง พ', 'คำสั่ง พ'),
                                      ('ประกาศ', 'ประกาศ'),
                                      ('ข้อบังคับ', 'ข้อบังคับ'),
                                      ('หนังสือภายนอก+หนังสือรับรอง',
                                       'หนังสือภายนอก+หนังสือรับรอง'),
                                      ('ระเบียบ', 'ระเบียบ'),
                                      ], string='Document type',default='บันทึกข้อความ')
    is_active = fields.Boolean(
        string='Active ',
        default=True,
    )
    material = fields.Text(string='Material')
