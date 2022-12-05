from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import timedelta, datetime, date
from decimal import *
import re


class receiveDocument(models.Model):
    _name = 'receive.document.main'
    _description = 'หนังสือรับ'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    def _get_manager_name(self):
        director_obj = self.env['fw_pfb_fin_settings2'].sudo().search([])
        for directoroffice in director_obj.directorOfOffice:
            sign_employee = directoroffice
        return sign_employee.job_id.ids
    
    name = fields.Char(
        string='squence',
        required=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True,
        default=lambda self: _('New'),
        track_visibility='onchange'
    )
    name_real = fields.Char(
        string='Real name',
        copy=True,
        track_visibility='onchange'
    )
    tag_ids=fields.Many2many(
        'document.internal.setting.tag',
        string="tag",
        track_visibility='onchange',
        copy=False
    )
    check_real = fields.Char(
        string='Just for check real name',
        copy=False
    )
    date_document_real = fields.Date(
        string='Real Date',
        copy=True,
        track_visibility='onchange',
        default=lambda self: date.today(),
    )
    refer = fields.Char(
        string="Refer",
        track_visibility='onchange',
        copy=False
    )
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
    date_document = fields.Date(
        string='Date',
        readonly=True,
        copy=False,
        track_visibility='onchange',
        default=lambda self: date.today(),
    )
    # department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        default=_default_employee,
        required=True,
        ondelete='cascade',
        index=True,
        copy=False
    )
    department_id = fields.Many2one(
        'hr.department',
        string="Department id",
        related="employee_id.department_id",
        readonly=True,
        copy=False
    )
    department_name = fields.Char(
        string="Department",
        related="employee_id.department_id.name",
        readonly=True,
        copy=False
    )
    date_receive = fields.Date(
        string='Date receive',
        copy=True,
        track_visibility='onchange'
    )
    speed = fields.Selection([('1', 'Normal'),
                              ('2', 'Express'),
                              ('3', 'urgent'),
                              ('4', 'The most urgent'),
                              ],
                             string="Speed ​​class", default='1',
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
        ('job_name', 'Job position')], string="To", default='job_name', required=True)
    job_name = fields.Many2many(
        'hr.job',
        string="Job name",
        # compute='_get_manager_job_name',
        default=_get_manager_name,
        store=True,
    )
    empolyee_name = fields.Many2many('hr.employee', string="Employee name")
    material = fields.Text(
        string='Material',
        copy=False
    )
    # sign=fields.Many2one('hr.job',string="Sign")
    from_document = fields.Char(
        string='From',
        copy=False
    )
    for_document_other = fields.Char(
        string="Other",
        copy=True
    )
    note = fields.Text(
        string="Note",
        copy=True
    )
    routings_internal_id = fields.Many2one(
        'document.external.setting',
        string='Document routing',
        copy=True,
        domain="[('is_active', '=', True)]"
    )
    setting_line_ids = fields.One2many(
        'receive.document.main.setting.lines',
        'setting_id',
        string='Document main line',
        copy=False
    )
    waiting_line_ids = fields.One2many(
        'waiting.receive.document.main.setting.lines',
        'setting_id',
        string='Document wating line',
        copy=True,
        require=True
    )
    approval_count = fields.Integer(
        string="Approval Count",
        default=0,
        copy=False
    )
    check_group_user = fields.Boolean(
        string="Invisible",
        compute="_check_group_user",
        store=False
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Files',
        track_visibility='onchange',
        copy=False
    )
    reference_internal = fields.Many2many(
        'document.internal.main',
        string="reference internal",
        compute="_compute_reference_internal",
        store=False,
        copy=False
    )
    send_with_original_document = fields.Boolean(
        string='Sent with original document',
        default=False,
    )
    approver_name_list = fields.Text(
        string='Approver Name',
        compute='_compute_setting_line',
        store=True
    )
    fin_100_ids = fields.Many2many(
        'fw_pfb_fin_system_100',
        'fin100_receive_document_rel',
        'fin_internal_document_id',
        'fin_id',
        string='FIN100'
    )
    fin_201_ids = fields.Many2many(
        'fw_pfb_fin_system_201',
        'fin201_receive_document_rel',
        'fin_internal_document_id',
        'fin_id',
        string='FIN201'
    )
    fin_401_ids = fields.Many2many(
        'fw_pfb_fin_system_401',
        'fin401_receive_document_rel',
        'fin_internal_document_id',
        'fin_id',
        string='FIN401'
    )
    # show_receive_document = fields.Boolean(
    #     string='show_receive_document',
    # )
    #
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     env_receive_document = self.env['receive.document.main']
    #     env_receive_document_approver = self.env['receive.document.main.setting.lines']
    #     params = self._context.get('params')
    #
    #     res = super(receiveDocument, self).fields_view_get(
    #         view_id=view_id,
    #         view_type=view_type,
    #         toolbar=toolbar,
    #         submenu=submenu
    #     )
    #
    #     receive_document_list = env_receive_document.search([])
    #     for idl in receive_document_list:
    #         receive_document_user = []
    #         receive_document_obj = env_receive_document.search([('id', '=', idl.id)])
    #         if receive_document_obj.state != 'cancel':
    #             receive_document_user_obj = env_receive_document_approver.search([
    #                 ('setting_id', '=', idl.id),
    #                 ('is_active', '=', True)
    #             ])
    #             for rduo in receive_document_user_obj:
    #                 if not rduo.approve_time and rduo.is_active and rduo.status_approve == '0':
    #                     receive_document_user.append(rduo.employee_id.user_id.id)
    #             # receive_document_obj.show_receive_document = True
    #
    #         if self._uid in receive_document_user:
    #             if not receive_document_obj.show_receive_document:
    #                 receive_document_obj.show_receive_document = True
    #         else:
    #             if receive_document_obj.show_receive_document:
    #                 receive_document_obj.show_receive_document = False
    #     self._cr.commit()
    #     return res


    @api.multi
    def _setting_line_approver_set(self):
        internal_obj = self.env['receive.document.main'].search([])
        for rec in internal_obj:
            approver_list = ''
            if rec.setting_line_ids:
                for sti in rec.setting_line_ids:
                    if sti.employee_id.name:
                        approver_list += sti.employee_id.name + ' '
                rec.approver_name_list = approver_list

    @api.multi
    @api.depends('setting_line_ids')
    def _compute_setting_line(self):
        for rec in self:
            approver_list = ''
            if rec.setting_line_ids:
                for sti in rec.setting_line_ids:
                    if sti.employee_id.name:
                        approver_list += sti.employee_id.name + ' '
                rec.approver_name_list = approver_list

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        copy = super(receiveDocument, self).copy(default)
        if 'setting_line_ids' in self:
            if self.setting_line_ids:
                copy.write({
                    'setting_line_ids': [(0, 0, {
                        'setting_id': self.id,
                        'employee_id': self.setting_line_ids[0].employee_id.id,
                        'step': self.setting_line_ids[0].step,
                        'status': self.setting_line_ids[0].status,
                        'dummy': self.setting_line_ids[0].dummy,
                        'approve_type': self.setting_line_ids[0].approve_type,
                        'approve_time': None,
                        'comment': '',
                        'status_approve': None,
                        'is_active': self.setting_line_ids[0].is_active,
                        'sequence': 1,
                    })]
                })
        return copy

    # @api.depends('dear')
    # @api.multi
    # def _get_manager_job_name(self):
    #     director_obj = self.env['fw_pfb_fin_settings2'].sudo().search([])
    #     for directoroffice in director_obj.directorOfOffice:
    #         sign_employee = directoroffice
    #     # if sign_employee:
    #     #     self.job_name = [(4, sign_employee.job_id.id)]


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


    def _check_from_document_name(self, values):
        if values.get('from_document', False) or values.get('refer', False):
            from_document = values.get('from_document', self.from_document)
            refer = values.get('refer', self.refer)
            doc_obj = self.env['receive.document.main'].search([
                ('from_document', '=', from_document),
            ], limit=1)

            if doc_obj:
                for do in doc_obj:
                    if refer == do.refer:
                        # action = self.env.ref('pfb_saraban.receive_document_main_list_action')
                        # msg = _("Refer already used")
                        # raise RedirectWarning(msg, action.id, _("Back to form"))
                        return {"warning": {"title": "Refer used", "message": "Refer already used"}}

    @api.model
    def create(self, vals):
        self._check_from_document_name(vals)
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('saraban.receive') or _('New')
            vals['name_real']= vals['name']
            # vals['date_document']=fields.Date.today()
            # vals['date_document_real']=fields.Date.today()
        result = super(receiveDocument, self).create(vals)
        return result

    @api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""

        self._check_from_document_name(values)

        for line in self.setting_line_ids:
            if not line.status_approve and line.is_active and line.step == '2' and self.state == '2':
                line.status_approve = '0'

        res = super(receiveDocument, self).write(values)
        return res

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

        step_array = []
        for line in self.setting_line_ids:
            if line.is_active:
                step_array.append(line.step)
        initial_step = min(step_array)

        for line in self.setting_line_ids:
            if line.is_active and line.step == initial_step:
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
        # Get receive object to find lastest name on date_document_real day
        # Finding what sequence is the lastest sequence
        # order 'id desc' is the lastest name
        receive_doc_obj = self.env['receive.document.main'].search([
            ('date_document_real', '=', self.date_document_real),
        ], order='id desc', limit=1)

        # if receive_doc_obj already run to get name real
        # It might have '.' in their name_real
        receive_doc_obj_already_run = self.env['receive.document.main'].search([
            ('name_real', 'like', '.'),
            ('date_document_real', '=', self.date_document_real),
        ])
        if receive_doc_obj:
            # Find digit split only number from character
            lastest_number = re.findall(r'\d+', receive_doc_obj.name)[0]
            sequence_prefix = receive_doc_obj.name[:(receive_doc_obj.name).find(str(re.findall(r'\d+', receive_doc_obj.name)[0]))]
            # print((receive_doc_obj.name).rfind('/'))
            # Add '.{receive_doc_obj_already_run+1}' to suffix with lastest_number
            # To transform name into new format like xxx.n and concat it back to sequence prefix
            name_real = ("%s%s" % (sequence_prefix, ('%s.%s' % (lastest_number, str(len(receive_doc_obj_already_run)+1)) )))
            # If sequence have suffix then split suffix to re concat to new name_real character
            if (receive_doc_obj.name).rfind('/') > 0:
                sequence_suffix = receive_doc_obj.name[(receive_doc_obj.name).rfind('/'):]
                name_real += sequence_suffix
            # Set new name_real to self.name_real
            self.name_real = name_real
        else:
            raise ValidationError(_('ไม่มีเอกสารในวันที่ ' + str(self.date_document_real)))




        # Finding which one is already run this function yet
        # That document might be name xxx.1, xxx.2

        # add + .1 to document sequence by counting which one already done this function on the days




    # def real_name_gen(self):
    #     domain=[('date_document_real', '=', self.date_document_real),
    #             ('name','!=',self.name)]
    #     real_name_gen = self.env['receive.document.main'].search(domain) or False
    #     if real_name_gen:
    #         # raise ValidationError(_(list(real_name_gen)))
    #         documents=list(real_name_gen)
    #         hight=0
    #         for document in documents:
    #             print(re.findall(r'\d+', document.name_real[:document.name_real.rfind('/')]))
    #             # name_real=Decimal(r'\d+', document.name_real[:document.name_real.rfind('/')])
    #             name_real = Decimal(re.findall(r'\d+', document.name_real[:document.name_real.rfind('/')])[0])
    #             if hight<name_real:
    #                 count_zero=document.name_real[:document.name_real.rfind('/')]
    #                 zero_count=''
    #                 for zero in count_zero:
    #                     if(zero!='0'):
    #                         break
    #                     zero_count+=zero
    #                 prefix=zero_count
    #                 hight=name_real
    #         self.name_real=prefix+str(hight+Decimal("0.1"))+document.name_real[document.name_real.rfind('/'):]
    #     else:
    #         raise ValidationError(_('ไม่มีเอกสารในวันที่ '+str(self.date_document_real)))
    
    @api.depends('reference_internal')
    def _compute_reference_internal(self):
        for rec in self:
            domain=[('reference_receive_document.name','=',rec.name)]
            document_references=rec.env['document.internal.main'].search(domain) or False
            # raise ValidationError(_([(4,list(document_reference))]))
            if document_references:
                reference_internal=[(4,document_reference.id) for document_reference in list(document_references)]
                rec.reference_internal=reference_internal
        
    
    @api.depends('employee_id')
    def _check_group_user(self):
        for rec in self:
            if rec.env.user.has_group('pfb_saraban.group_super_user_document'):
                rec.check_group_user = True
            else:
                rec.check_group_user = False

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(
                _('You cannot delete an document which is not draft.'))
        return super(receiveDocument, self).unlink()
    
class SettingLineExternal(models.Model):
    _name = 'receive.document.main.setting.lines'
    _description = 'สารบัญ receive setting line'
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
    job_id_name = fields.Many2one(
        'hr.job',
        string="Job name"
    )
    step = fields.Selection(
        string="Step",
        selection=[
            ('1', '1'),
            ('2', '2')
        ],
        default='1'
    )
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผอ.ฝ่าย'),
        ('2', 'ฝ่ายที่เกี่ยวข้อง')
    ], default='1', readonly=True, compute='set_step')
    approve_type = fields.Selection(string="Approve type", selection=[
        ('comments', 'Comments only')], default='comments')
    approve_time = fields.Datetime(
        string='approve time',
        copy=False
    )
    comment = fields.Html(
        string='comment',
        copy=False
    )
    maker_add=fields.Many2one(
        'hr.employee',
        string="Employee id",
        default=_default_employee,
        required=True,
        ondelete='cascade',
        index=True,
        copy=False
    )
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
    sequence = fields.Integer(
        string='Sequence',
        index=True
    )
    to_or_cc = fields.Selection(
        string='To/CC',
        selection=[
            ('', ''),
            ('to', 'To'),
            ('cc', 'CC'),
        ],
        default='',
    )
    sender = fields.Many2one(
        'hr.employee',
        string='Sender'
    )
    # order_choice = fields.Many2many(
    #     'order.choices',
    #     string='Order',
    # )

    def _comment_moved_stamp_to_comment_receive(self):
        # This function used for stamp old comment box (fields.Char)
        # to a new comment box (fields.Html)
        # only for comment before 01/06
        self._cr.execute('''
            SELECT * FROM receive_document_main_setting_lines
            WHERE create_date < '2021-06-01' AND comment_moved0 is not null AND comment is null
        ''')
        receive_obj = self._cr.dictfetchall()
        for ro in receive_obj:
            if ro['comment_moved0'] is not None:
                self._cr.execute('''
                    UPDATE receive_document_main_setting_lines
                    SET comment = '%s'
                    WHERE id = '%s'
                ''' % (ro['comment_moved0'].replace("'", ''), str(ro['id'])))

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
