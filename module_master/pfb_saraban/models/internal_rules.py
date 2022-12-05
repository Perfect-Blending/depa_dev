from odoo import models, fields, api, _
from datetime import timedelta

class internalDocumentRules(models.Model):
    _name = 'document.internal.rules'
    _description = 'สารบรรณ หนังสือภายใน ข้อบังคับ'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
     
    name=fields.Char(
        string='name'
    )
    issue = fields.Char(
        string='Issue',
        
    )
    year=fields.Char(
        string='year'
    )
    circular_letter = fields.Boolean(
        string='หนังสือเวียน',
        default=False,
        required=True
    )
    state = fields.Selection([('draft', 'Draft'),
                               ('sent', 'Sent'),
                                ('1', 'ผอ.ฝ่าย'),
                                ('2', 'ฝ่ายที่เกี่ยวข้อง-1'),
                                ('3', 'ชสศด.'),
                                ('4', 'รสศด.'),
                                ('5', 'ฝ่ายที่เกี่ยวข้อง-2'),
                                ('6', 'ผสศด.'),
                                ('done','เสร็จสมบูรณ์')
                                ], 
                             readonly=True, 
                             default='draft', 
                             copy=False, 
                             string="Status",
                             required=True)
    date_document=fields.Date(string='Date',readonly=True,default=fields.Date.context_today)
    # department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",readonly=True)
    speed = fields.Selection([('normal', 'Normal'),
                               ('express', 'Express'),
                                ('urgent', 'urgent'),
                                ('vurgent', 'The most urgent'),
                                ],
                             string="Speed ​​class"
                             ,default='normal',
                             required=True)
    secret= fields.Selection([('normal', 'Normal'),
                               ('secret', 'Secret'),
                                ('vsecret', 'very secret'),
                                ('vvurgent', 'The most secret'),
                                ],
                             string="Secret ​​class",
                             default='normal',
                             required=True)
    job_name=fields.Many2many('hr.job',string="Job name")
    empolyee_name=fields.Many2many('hr.employee',string="Employee name")
    subject=fields.Text(string='Subject',required=True)
    sign=fields.Many2one('hr.job',string="Sign",required=True)
    material=fields.Text(string='Material',required=True)
    for_document= fields.Selection([('1', 'เพื่อดำเนินการ'),
                               ('2', 'เพื่อโปรเจคพิจารณา'),
                                ('3', 'เพื่อโปรดทราบ'),
                                ('4', 'อื่นๆ'),
                                ],required=True)
    note=fields.Text(string="Note")
    
    routings_internal_id = fields.Many2one('document.internal.setting',string='Document routing')
    setting_line_ids = fields.One2many('document.internal.rules.setting.line','setting_id', string='Document main line')

    @api.onchange('routings_internal_id')
    def onchange_routings_internal_id(self):
        self.update({
            'setting_line_ids' : False
        })    
        main_line_ids = self.routings_internal_id.user_id
        values = []
        for line_id in main_line_ids:
            if line_id.is_active==True:
                values.append([0, 0, {
                    'employee_id' : line_id.employee_id.id,
                    'job_id_name' : line_id.job_id_name,
                    'status' : line_id.status,
                    'approve_type' : line_id.approve_type,
                    'is_active' : line_id.is_active,
                }])
        self.update({
            'setting_line_ids' : values
        })
        
class  InternalDocumentrulesSettingLine(models.Model):
    _name = 'document.internal.rules.setting.line'
    _order='status,sequence,id'

    setting_id = fields.Many2one('document.internal.rules', string="document rules")
    employee_id= fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    job_id_name = fields.Char(string="job id", related='employee_id.job_id.name', readonly=True)
    
    status = fields.Selection(string="Status",selection=[
        (1, 'ผอ.ฝ่าย'),
        (2, 'ฝ่ายที่เกี่ยวข้อง-1'),
        (3, 'ชสศด.'),
        (4, 'รสศด.'),
        (5, 'ฝ่ายที่เกี่ยวข้อง-2'),
        (6, 'ผสศด.')
        ],default=1)
    step=fields.Integer(string="step",compute='set_step')
    approve_type=fields.Selection(string="Approve type",selection=[
        ('require', 'Is require to approve'),
        ('comments', 'Comments only')])
    approve_time=fields.Datetime(string='approve time')
    comment=fields.Char(string='comment')
    document_id= fields.Many2one(
        'document.internal.setting',
        string="Document id"
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(string='Sequence',index=True)
    
    @api.depends('status')
    # @api.onchange('status')
    def set_step(self):
        for record in self:
            if record.status:
                status=record.status
                record.update({'step':int(status)})
