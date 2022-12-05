from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime
from decimal import *

class internalDocument(models.Model):
    _name = 'receive.document.main'
    _description = 'หนังสือรับ'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    
    name = fields.Char(string='squence', required=True, copy=False, readonly=True, states={
                       'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'),track_visibility='onchange')
    name_real = fields.Char(string='Real name',  copy=False, states={
                            'draft': [('readonly', False)]},track_visibility='onchange')
    tag_ids=fields.Many2many('document.internal.setting.tag', string="tag",track_visibility='onchange')
    check_real = fields.Char(string='Just for check real name', copy=False)
    date_document_real = fields.Date(string='Real Date', copy=False,track_visibility='onchange')
    refer = fields.Char(string="Refer",track_visibility='onchange')
    state = fields.Selection([('cancel', 'Reject'),
                              ('draft', 'Draft'),
                              ('sent', 'Sent'),
                              ('1', 'ระดับ1'),
                              ('2', 'กำลังดำเนินการ'),
                              ('done', 'เสร็จสมบูรณ์'),
                              ],
                             readonly=True,
                             default='draft',
                             copy=False,
                             string="Status",
                             required=True,track_visibility='onchange')
    date_document = fields.Date(string='Date', readonly=True, copy=False,track_visibility='onchange')
    # department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee,
                                  required=True, ondelete='cascade', index=True, copy=False)
    department_id = fields.Many2one('hr.department', string="Department id",
                                    related="employee_id.department_id", readonly=True, copy=False)
    department_name = fields.Char(
        string="Department", related="employee_id.department_id.name", readonly=True, copy=False)
    date_receive = fields.Date(string='Date receive', copy=False,track_visibility='onchange')
    speed = fields.Selection([('normal', 'Normal'),
                              ('express', 'Express'),
                              ('urgent', 'urgent'),
                              ('vurgent', 'The most urgent'),
                              ],
                             string="Speed ​​class", default='normal',
                             required=True)
    secret = fields.Selection([('normal', 'Normal'),
                               ('secret', 'Secret'),
                               ('vsecret', 'very secret'),
                               ('vvurgent', 'The most secret'),
                               ],
                              string="Secret ​​class",
                              default='normal',
                              required=True)
    subject = fields.Char(string='Subject', required=True,track_visibility='onchange')
    dear = fields.Selection([
        ('empolyee_name', 'empolyee name'),
        ('job_name', 'Job position')], string="To", default='empolyee_name', required=True)
    job_name = fields.Many2many('hr.job', string="Job name")
    empolyee_name = fields.Many2many('hr.employee', string="Employee name")
    material = fields.Text(string='Material')
    # sign=fields.Many2one('hr.job',string="Sign")
    from_document = fields.Text(string='From')
    for_document_other = fields.Char(string="Other")
    note = fields.Text(string="Note")

    routings_internal_id = fields.Many2one(
        'document.external.setting', string='Document routing', copy=True, domain="[('is_active', '=', True)]")
    setting_line_ids = fields.One2many(
        'receive.document.main.setting.lines', 'setting_id', string='Document main line', copy=True)
    waiting_line_ids = fields.One2many('waiting.receive.document.main.setting.lines',
                                       'setting_id', string='Document wating line', copy=True, require=True)
    approval_count = fields.Integer(
        string="Approval Count", default=0, copy=False)
    check_group_user = fields.Boolean(
        string="Invisible", compute="_check_group_user", store=False)
    attachment_ids = fields.Many2many('ir.attachment', string='Files',track_visibility='onchange')
    reference_internal = fields.Many2many('document.internal.main',
        string="reference internal", compute="_compute_reference_internal", store=False)
    @api.onchange('name_real')
    def onchange_real_name(self):
        try:
            if self.name_real:
                # raise ValidationError(_('Condition not working'))
                if self.name_real:
                    self.check_real = self.department_name+self.name_real
        except Exception as e:
            raise ValidationError(_(e))
    @api.onchange('setting_line_ids')
    def _oncahnge_setting_line_ids(self):
        self.update({
            'waiting_line_ids': False
        })
        main_line_ids = self.setting_line_ids
        values = []
        for line_id in main_line_ids:
            if line_id.is_active and line_id.status_approve=='0':
                values.append([0, 0, {
                    'employee_id': line_id.employee_id.id
                }])
        self.update({
            'waiting_line_ids': values
        })
    @api.onchange('routings_internal_id')
    def onchange_routings_internal_id(self):
        self.ensure_one()
        self.update({
            'setting_line_ids': False
        })
        main_line_ids = self.routings_internal_id.user_id
        values = []
        for line_id in main_line_ids:
            values.append([0, 0, {
                'employee_id': line_id.employee_id.id,
                'job_id_name': line_id.job_id_name,
                'status': line_id.status,
                'step': line_id.step,
                'approve_type': line_id.approve_type,
                'is_active': line_id.is_active,
            }])
        self.update({
            'setting_line_ids': values
        })
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('saraban.receive') or _('New')
            vals['name_real']= vals['name']
            vals['date_document']=fields.Date.today()
            vals['date_document_real']=fields.Date.today()
        result = super(internalDocument, self).create(vals)
        return result
                
                
    def action_make_approval_wizard(self):
        self.ensure_one()
        approve_type = False
        employee_id = False
        setting_line = False
        status = False
        count_nonactive = 0
        for line in self.setting_line_ids:
            if not line.is_active:
                count_nonactive += 1
        if self.setting_line_ids:
            state=0
            if(self.state=='sent'):
                state=1
            else:
                state=int(self.state)
            for line in self.setting_line_ids:
                if not line.approve_time and line.is_active and self.env.uid == line.employee_id.user_id.id and line.status_approve == '0' and line.step == str(state):
                    approve_type = line.approve_type
                    employee_id = line.employee_id
                    setting_line = line.id
                    status = line.status
                    step = line.step
                    return {
                        'name': "Make Approval Wizard",
                        'view_mode': 'form',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'make.approval.wizard.receive',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_approve_type': approve_type,
                            'default_employee_id': employee_id.id,
                            'default_setting_line': setting_line,
                            'default_status': status,
                            'default_total_for_approve': len(self.setting_line_ids)-count_nonactive,
                            'default_setting_id': self.id,
                        }
                    }
            raise ValidationError(_('Not your turn'))
# self.env.uid
    def action_sent_to_supervisor(self):
        # if self.employee_id.dummy:
        #     raise ValidationError(_('Dummy not checked'))
        count_active=0
        for line in self.setting_line_ids:
            if line.dummy and line.is_active:
                raise ValidationError(_('Dummy not checked'))
            if line.is_active==True:
                count_active+=1
        if(len(self.setting_line_ids) == 0):
            raise ValidationError(_('Please add the line'))
        if count_active==0:
            raise ValidationError(_('No active user in line'))
        for line in self.setting_line_ids:
            if line.is_active and line.step=='1':
                line.status_approve = '0'
        self.update({
                'waiting_line_ids': False
                })
        main_line_ids = self.setting_line_ids
        values = []
        for line_id in main_line_ids:
            if line_id.is_active and line_id.status_approve=='0':
                values.append([0, 0, {
                    'employee_id': line_id.employee_id.id
                }])
        self.update({
            'waiting_line_ids': values
        })
        self.update({
            'state': 'sent',
            'date_document': fields.Date.today()
        })

    def set_to_draft(self):
        self.update({
            'state': 'draft'
        })
        for line in self.setting_line_ids:
            line.status_approve = ''
            line.comment = ''
            line.approve_time = ''

    def state_done(self):
        self.update({
            'state': 'done'
        })
    def make_order_setting_line(self):
        setting_line_ids = self.setting_line_ids.sorted(lambda x: x.step)
        sequence = 0
        for slid in setting_line_ids:
            slid.update({"sequence":sequence})
            sequence += 1
            
    def real_name_gen(self):
        domain=[('date_document_real', '=', self.date_document_real),
                ('name','!=',self.name)]
        real_name_gen = self.env['receive.document.main'].search(domain) or False
        if real_name_gen:
            # raise ValidationError(_(list(real_name_gen)))
            documents=list(real_name_gen)
            hight=0
            for document in documents:
                name_real=Decimal(document.name_real[:document.name_real.rfind('/')])
                if hight<name_real:
                    count_zero=document.name_real[:document.name_real.rfind('/')]
                    zero_count=''
                    for zero in count_zero:
                        if(zero!='0'):
                            break
                        zero_count+=zero
                    prefix=zero_count
                    hight=name_real
            self.name_real=prefix+str(hight+Decimal("0.1"))+document.name_real[document.name_real.rfind('/'):]
        else:
            raise ValidationError(_('ไม่มีเอกสารในวันที่ '+str(self.date_document_real)))
    
    @api.depends('reference_internal')
    def _compute_reference_internal(self):
        domain=[('reference_receive_document.name','=',self.name)]
        document_references=self.env['document.internal.main'].search(domain) or False
        # raise ValidationError(_([(4,list(document_reference))]))
        if document_references:
            reference_internal=[(4,document_reference.id) for document_reference in list(document_references)]
            self.reference_internal=reference_internal
        
    
    @api.depends('employee_id')
    def _check_group_user(self):
        if self.env.user.has_group('pfb_saraban.group_super_user_document'):
            self.update({
                'check_group_user': True
            })
        else:
            self.update({
                'check_group_user': False
            })

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(
                _('You cannot delete an document which is not draft.'))
        return super(internalDocument, self).unlink()

class SettingLineExternal(models.Model):
    _name = 'receive.document.main.setting.lines'
    _description = 'สารบัญ'
    _order = 'sequence,id'
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    dummy = fields.Boolean(
        string="dummy", related='employee_id.dummy', readonly=True)
    setting_id = fields.Many2one(
        'receive.document.main', string="document main")
    # job_title = fields.Char(string="job title", related='employee_id.job_title', required=True, readonly=True)
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
    approve_time = fields.Datetime(string='approve time', copy=False)
    comment = fields.Char(string='comment', copy=False)
    maker_add=fields.Many2one('hr.employee', string="Employee id", default=_default_employee,
                                  required=True, ondelete='cascade', index=True, copy=False)
    status_approve = fields.Selection(string="status", selection=[
        ('0', 'รออนุมัติ'),
        ('1', 'รับทราบแล้ว')], copy=False)
    document_id = fields.Many2one(
        'receive.document.main',
        string="Document id"
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(string='Sequence', index=True)

    @api.depends('step')
    def set_step(self):
        for record in self:
            if record.step:
                step = record.step
                record.update({'status': step})
    
class WaitingReceiveDocumentSettingLine(models.Model):
    _name = 'waiting.receive.document.main.setting.lines'
    _description = 'สารบรรณ หนังสือภายรับ'

    setting_id = fields.Many2one(
        'receive.document.main', string="document main")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee Name"
    )
    sequence = fields.Integer(string='Sequence', index=True)
