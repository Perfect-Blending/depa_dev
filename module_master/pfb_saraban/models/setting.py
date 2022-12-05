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
    _description = 'สารบัญ internal setting line'
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
        ('6', '6'),
        ('7', '7'),
    ], default='1',index=True)
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผอ.ฝ่าย'),
        ('2', 'ฝ่ายที่เกี่ยวข้อง-1'),
        ('3', 'เลขา ชสศด./รสศด.'),
        ('4', 'ชสศด.'),
        ('5', 'รสศด.'),
        ('6', 'ฝ่ายที่เกี่ยวข้อง-2'),
        ('7', 'ผสศด.')
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

    def _comment_moved_stamp_to_comment_internal(self):
        # This function used for stamp old comment box (fields.Char)
        # to a new comment box (fields.Html)
        # only for comment before 01/06
        self._cr.execute('''
            SELECT * FROM document_internal_main_setting_line
            WHERE create_date < '2021-06-01' AND comment_moved0 is not null AND comment is null
        ''')
        internal_obj = self._cr.dictfetchall()
        for io in internal_obj:
            if io['comment_moved0'] is not None:
                self._cr.execute('''
                    UPDATE document_internal_main_setting_line
                    SET comment = '%s'
                    WHERE id = '%s'
                ''' % (io['comment_moved0'].replace("'", ''), str(io['id'])))

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

    @api.multi
    def update_line_status(self):
        line_obj = self.env['document.internal.setting.lines'].search([])
        for line in line_obj:
            if line.step == '3':
                line.step = '4'
                line.status = '4'
            elif line.step == '4':
                line.step = '5'
                line.status = '5'
            elif line.step == '5':
                line.step = '6'
                line.status = '6'
            elif line.step == '6':
                line.step = '7'
                line.status = '7'


    @api.multi
    def update_internal_main(self):
        internal_obj = self.env['document.internal.main'].search([])
        for line in internal_obj:
            if line.state == '3':
                line.state = '4'
            elif line.state == '4':
                line.state = '5'
            elif line.state == '5':
                line.state = '6'
            elif line.state == '6':
                line.state = '7'

    @api.multi
    def backup_step_and_status_to_backup_field(self):
        setting_line_obj = self.env['document.internal.main.setting.line'].search([])
        for line in setting_line_obj:
            line.step_before_change = line.step

    @api.multi
    def update_main_line_status(self):
        new_internal_main = self.env['document.internal.main.setting.line'].search([
            ('step', '=', '7'),
        ])
        new_internal_list = []
        for nim in new_internal_main:
            if nim.setting_id.id not in new_internal_list:
                new_internal_list.append(nim.setting_id.id)
        setting_line_obj = self.env['document.internal.main.setting.line'].search([
            ('setting_id', 'not in', new_internal_list),
        ])
        
        for line in setting_line_obj:
            if line.step == '3':
                line.step = '4'
                line.status = '4'
            elif line.step == '4':
                line.step = '5'
                line.status = '5'
            elif line.step == '5':
                line.step = '6'
                line.status = '6'
            elif line.step == '6':
                line.step = '7'
                line.status = '7'


    @api.multi
    def restore_step_before_change(self):
        setting_line_obj = self.env['document.internal.main.setting.line'].search([])
        for line in setting_line_obj:
            if line.step_before_change != '':
                line.step = line.step_before_change

    @api.multi
    def update_document_internal_main_status(self):
        # For filter document.main.setting.line that no waiting status (maybe approve or reject actually)
        setting_main_line_obj = self.env['document.internal.main.setting.line'].search([
            '|',
            ('status_approve', '!=', '0'),
            ('status_approve', '!=', False),
            ('setting_id.state', 'not in', ['draft', 'cancel', 'done'])
        ])
        sml_array = []
        # For set and id of setting.main.line to get specific on document_id (setting_id.id) : Main document
        for sml in setting_main_line_obj:
            if sml.setting_id.id not in sml_array:
                sml_array.append(sml.setting_id.id)

        # Loop for get only main.setting.line line in the same setting_id
        for sa in sml_array:
            setting_main_line_obj = self.env['document.internal.main.setting.line'].search([
                ('status_approve', '!=', '0'),
                ('is_active', '=', True),
                ('setting_id', '=', sa),
                ('setting_id.state', '!=', 'done'),
            ], order='step desc')
            if setting_main_line_obj:
                if len(setting_main_line_obj) >= 1:
                    obj_check_status_approve_is_zero = self.env['document.internal.main.setting.line'].search([
                        ('step', '=', setting_main_line_obj[0].step),
                        ('status_approve', '=', '0'),
                        ('is_active', '=', True),
                        ('setting_id', '=', setting_main_line_obj[0].setting_id.id),
                        ('setting_id.state', '!=', 'done'),
                    ])
                    # print('@@@@@@@')
                    # print(setting_main_line_obj[0].setting_id)
                    # print(setting_main_line_obj[0])
                    # print(setting_main_line_obj[0].step)
                    # print('STATUS APPROVE')
                    # print(obj_check_status_approve_is_zero)
                    # print('-----')
                    if obj_check_status_approve_is_zero:
                        if setting_main_line_obj[0].step == '1':
                            setting_main_line_obj[0].setting_id.state = 'sent'
                        else:
                            setting_main_line_obj[0].setting_id.state = setting_main_line_obj[0].step
                    else:
                        setting_main_line_obj[0].setting_id.state = setting_main_line_obj[0].step
                #elif len(setting_main_line_obj) == 1:
                #    if setting_main_line_obj[0].step == '1':
                #        setting_main_line_obj[0].setting_id.state = 'sent'
                #    printj[0].step)


        # for sml in setting_main_line_obj:
        #     print(sml)
        #     if sml.setting_id:
        #         if sml.status == '1':
        #             sml.setting_id.state = 'sent'
        #         else:
        #             sml.setting_id.state = str(int(sml.status) - 1)



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


class InternalDocumentTag(models.Model):
    _name = "document.internal.document.setting.tag"
    _description = "Internal Document tag"

    name = fields.Char(string="Internal Document Tag", required=True, copy=False)
    color = fields.Integer(string='Color Index')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
