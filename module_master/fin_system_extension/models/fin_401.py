# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.


from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.fin_system.models.fin_401 as ORIG_FIN401
from random import randrange
from odoo.addons.fin_system.models.fin_middleware import message_log_stamp

ALLOW_DIRECTOR_STATE = [
    'RelatedGroup',
    'AssistantOfOffice',
    'DeputyOfOffice',
    'SmallNote',
]

class fw_pfb_FS401(models.Model):
    _inherit = 'fw_pfb_fin_system_401'
    _rec_name = 'fin_no'

    price_total = fields.Float(string='Total', compute='_compute_total', store=True)
    trigger = fields.Integer(string="trigger")

    next_approval_id = fields.Many2one('fw_pfb_fin_system_401_approver', string='Next Approval', compute='_compute_next_approval', store=True)
    next_approval_ids = fields.Many2many('fw_pfb_fin_system_401_approver', string='Next Approval IDS',
        relation="fin401_approval_approver_rel", column1='fin401_id', column2='approval_id', compute='_compute_next_approval', store=True)
    next_approval_user_ids = fields.Many2many('res.users', string='Next Approval Users',
        relation="fin401_approval_res_users_rel", column1='fin401_id', column2='user_id', compute='_compute_next_approval', store=True)
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    next_comment_ids = fields.Many2many('fw_pfb_fin_system_401_approver', string='Next Comment',
        relation="fin401_approval_comment_rel", column1='fin401_id', column2='approval_id', compute='_compute_next_comment', store=True)
    next_comment_user_ids = fields.Many2many('res.users', string='Next Comment Users',
        relation="fin401_comment_res_users_rel", column1='fin401_id', column2='user_id', compute='_compute_next_comment', store=True)
    can_comment = fields.Boolean('Can Comment', compute='_compute_can_comment')
    can_complete = fields.Boolean('Can Complete', compute='_compute_can_complete')

    def _compute_can_complete(self):
        print("FIN401._compute_can_complete",self)
        for fin401 in self:
            fin401.can_complete = False
            last_approval = fin401.approver and fin401.approver.sorted(lambda app: app.position_index)[-1] or False
            if last_approval:
                if self.env.user.id in last_approval.employee_user_id.ids:
                    fin401.can_complete = True
                else:
                    fin401.can_complete = False
                # force admin can complete
                if self.env.user.id == 1:
                    fin401.can_complete = True
            if fin401.is_fin_lock:
                fin401.can_complete = False

    @api.multi
    @api.depends('state', 'approver',
        'approver.employee_id', 'approver.employee_id.user_id', 'approver.employee_user_id',
        'approver.action_date', 'approver.state', 'trigger')
    def _compute_next_approval(self):
        print("FIN401._compute_next_approval",self)
        for fin401 in self:
            if fin401.state == 'reject':
                fin401.next_approval_id = False
                return True
            latest_approval_ids = fin401.approver.filtered(lambda app: app.approval_type=='mandatory' and app.state=='approve' and app.approve_active==True)
            latest_approval = latest_approval_ids and latest_approval_ids[-1]
            if latest_approval:
                approval_ids_ready = fin401.approver\
                    .filtered(lambda app: app.approval_type=='mandatory' and app.position_index > latest_approval.position_index and app.state=='pending' and app.approve_active==True)
            else:
                approval_ids_ready = fin401.approver\
                    .filtered(lambda app: app.approval_type=='mandatory' and app.state=='pending' and app.approve_active==True)

            if approval_ids_ready:
                fin401.next_approval_id = approval_ids_ready[0]
                fin401.next_approval_ids = approval_ids_ready
                fin401.next_approval_user_ids = approval_ids_ready[0].mapped('employee_user_id')

            overrule_states = ['DirectorOfFinance','AssistantOfOffice','DeputyOfOffice','SmallNote']
            #overrule_states = []
            #for state in ORIG_FIN401.STATE_SELECTION:
                #if state[0] in ['draft','sent','completed','cancelled', 'reject']:
                    #continue
                #overrule_states.append(state[0])

            if fin401.state in overrule_states:
                #fin401.next_approval_user_ids |= fin401.approver.sorted(lambda app: app.position_index)[-1].mapped('employee_user_id')
                fin401.next_approval_user_ids |= fin401.approver\
                    .filtered(lambda app: app.approve_active==True)\
                    .sorted(lambda app: app.position_index)[-1].mapped('employee_user_id')

    @api.depends('next_approval_id', 'next_approval_user_ids', 'state', 'trigger')
    def _compute_can_approve(self):
        print("FIN401._compute_can_approve",self)
        for fin401 in self:
            #if self.env.user == fin401.next_approval_id.employee_user_id:
            if self.env.user in fin401.next_approval_user_ids:
                fin401.can_approve = True
            else:
                fin401.can_approve = False
            # force admin can approve
            if self.env.user.id == 1 and fin401.next_approval_id:
                fin401.can_approve = True

    @api.multi
    @api.depends('state', 'approver', 'next_approval_id', 'trigger', 'approver.position_index', 'approver.approve_step',
        'approver.employee_id', 'approver.employee_id.user_id', 'approver.employee_user_id',
        'approver.action_date', 'approver.state', 'approver.approval_type')
    def _compute_next_comment(self):
        print("FIN401._compute_next_comment",self)
        for fin401 in self:
            approval_ids = self.env['fw_pfb_fin_system_401_approver']
            approval_ids |= fin401.approver\
                .filtered(lambda app: app.approve_active and app.approval_type=='comment' and app.approve_step <= fin401.next_approval_id.approve_step and (not app.state or app.state=='pending'))
            approval_ids |= fin401.approver.filtered(lambda app: app.approval_type=='comment') and fin401.approver.filtered(lambda app: app.approval_type=='comment')[-1]
            fin401.next_comment_ids = approval_ids.sorted(lambda app: app.position_index)
            if fin401.next_comment_ids:
                fin401.next_comment_user_ids = fin401.next_comment_ids.mapped('employee_user_id')

    @api.depends('next_comment_ids', 'next_comment_user_ids', 'next_comment_ids.employee_user_id', 'state', 'trigger')
    def _compute_can_comment(self):
        print("FIN401._compute_can_comment",self)
        for fin401 in self:
            if self.env.user in fin401.next_comment_user_ids:
                fin401.can_comment = True
            else:
                fin401.can_comment = False
            # force admin can approve
            if self.env.user.id == 1 and fin401.next_comment_ids:
                fin401.can_comment = True

    @api.multi
    @api.depends('fin_lines.price_subtotal', 'trigger')
    def _compute_total(self):
        print("FIN401._compute_total",self)
        for fin in self:
            total = sum([line.lend or 0.0 for line in fin.fin_lines])
            fin.price_total = total

    @api.multi
    def compute_fin401_line_residual(self):
        print("FIN401.compute_fin401_line_residual",self)
        for fin401 in self:
            if fin401.fin_projects:
                fin401.fin_projects.unlink()
            groups = {}
            for fin_line in obj.fin_lines:
                key = fin_line.fin_id, fin_line.projects_and_plan
                groups.setdefault(key, self.env['fw_pfb_fin_system_100_line'])
                groups[key] |= fin_line
            if groups:
                for (fin, project), fin_lines in groups.items():
                    amount_to_reserve = sum(fin_lines.mapped('price_subtotal')) or 0.0
                    vals = {
                        'fin_id': fin.id,
                        'projects_and_plan': project.id,
                        'projects_reserve': amount_to_reserve,
                        'projects_residual': project.budget_balance,
                    }
                    line_proj = self.env['fw_pfb_fin_system_100_projects'].create(vals)
        return

    @api.multi
    def button_force_compute_fin401_lines(self):
        print("FIN401.button_force_compute_fin401_lines",self)
        for fin401 in self:
            # compute residual in fin100_line._compute_fin100_line_balance()
            if fin401.state in ['cancelled','reject']:
                fin401.fin_lines.write({
                    'fin100_line_residual': 0.0,
                    'fin100_line_residual_amount': 0.0,
                })
                continue
        return True

    @api.multi
    def action_set_draft(self):
        print("FIN401.action_set_draft",self)
        self.write({'state':'draft'})
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Set to Draft",
        #         str(self.write_date),
        #     ))
        # )
        log_message = message_log_stamp(self, "Set to Draft", self.write_date)
        self.message_post(body=_(log_message))

    @api.multi
    def action_set_done(self):
        print("FIN401.action_set_done",self)
        self.write({'state':'completed'})
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "Set To Complete",
        #         str(self.write_date),
        #     ))
        # )
        log_message = message_log_stamp(self, "Set To Complete", self.write_date)
        self.message_post(body=_(log_message))

    @api.multi
    def action_set_cancel(self):
        print("FIN401.action_set_cancel",self)
        self.write({'state':'cancelled'})
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "FIN401 Set to Cancel",
        #         str(self.write_date),
        #     ))
        # )
        log_message = message_log_stamp(self, "FIN401 Set to Cancel", self.write_date)
        self.message_post(body=_(log_message))

    @api.multi
    def write(self, vals):
        print("FIN401.write", self, vals)
        res = super(fw_pfb_FS401, self).write(vals)
        if 'fin_lines' in vals or 'state' in vals:
            self.button_force_compute_fin401_lines()
        return res

    @api.onchange('flow_template')
    def _onchange_flow_template(self):
        print("FIN401._onchange_flow_template",self)
        self.approver = False
        template_id = False
        if self.flow_template:
            template_id = self.flow_template.id
        template = self.env['fw_pfb_flow_template'].browse(template_id)
        if template and template.approve_line:
            for line in template.approve_line:
                data = {
                    "employee_id" : line.emp_name.id,
                    "fin_position" : line.position,
                    "approve_active" : line.data_activate,
                    "approve_position" : line.approve_position,
                    "position_index" : line.position_index,
                    "approval_type" : line.approval_type,
                    "approve_step" : line.approve_step,
                }
                if line.data_activate :
                    data["state"] = "pending"
                self.approver += self.approver.new(data)

    @api.multi
    def button_trigger(self):
        print("FIN401.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
            obj.approver.button_trigger()
            obj.fin_lines.button_trigger()
        return True

    @api.multi
    def action_set_approve(self, note=""):
        print("FIN401.action_set_approve", self)
        for fin401 in self:
            approval = fin401.next_approval_id
            # If state in ALLOW_DIRECTOR_STATE
            # Director can visible a record and allow to approve also
            is_director = False
            if fin401.state in ALLOW_DIRECTOR_STATE:
                director_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                    ('fin_id', '=', fin401.id),
                    ('approve_active', '=', True),
                    ('employee_user_id', '=', self._uid),
                    ('position_index', '=', fin401.next_approval_id.position_index)
                ], limit=1)
                if director_obj:
                    approval = director_obj
                    is_director = True
            if self.env.user != approval.user_id and not is_director:

                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin401.next_approval_user_ids:
                    approval = fin401.next_approval_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
                else:
                    raise UserError(_('Only authorized person to approve or action'))
            if approval:
                if len(approval) > 1:
                    approval = approval[0]
                if approval.approval_type == 'mandatory':
                    pass
                if approval.approval_type == 'optional':
                    pass
                if approval.approval_type == 'comment':
                    raise UserError(_('Need to Comment'))
                approval.write({
                    'state': 'approve',
                    'action_date': fields.Datetime.now(),
                    'user_id': self.env.uid,
                    'memo': note,
                })
                approval.update_fin_status()
            else:
                latest_approval = fin401.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def action_set_reject(self, note=""):
        print("FIN401.action_set_reject",self)
        for fin401 in self:
            approval = fin401.next_approval_id

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin401.next_approval_user_ids:
                    approval = fin401.next_approval_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
                else:
                    raise UserError(_('Only authorized person to approve or action'))

            if approval:
                if len(approval) > 1:
                    approval = approval[0]
                if approval.approval_type == 'mandatory':
                    pass
                if approval.approval_type == 'optional':
                    pass
                if approval.approval_type == 'comment':
                    raise UserError(_('Need to Comment'))
                if not note:
                    raise UserError(_('Please input reason for reject'))
                approval.write({
                    'state': 'reject',
                    'action_date': fields.Datetime.now(),
                    'user_id': self.env.uid,
                    'memo': note,
                })
                fin401.set_fin401_to_reject()
                fin401.action_generate_mail_to_reject()
            else:
                latest_approval = fin401.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def action_set_comment(self, note=""):
        print("FIN401.action_set_comment",self)
        for fin401 in self:
            approval = fin401.next_comment_ids and fin401.next_comment_ids[0] or False

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin401.next_comment_user_ids:
                    approval = fin401.next_comment_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
                else:
                    raise UserError(_('Only authorized person to comment or action'))

            if approval:
                if len(approval) > 1:
                    approval = approval[0]
                if approval.approval_type == 'mandatory':
                    raise UserError(_('Need to Approve / Reject'))
                if approval.approval_type == 'optional':
                    pass
                if approval.approval_type == 'comment':
                    pass
                if not note:
                    raise UserError(_('Please input Note/Comment'))
                approval.write({
                    'state': 'comment',
                    'action_date': fields.Datetime.now(),
                    'user_id': self.env.uid,
                    'memo': note,
                })
                approval.update_fin_status()
            else:
                latest_approval = fin401.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def set_fin401_to_reject(self):
        print("FIN401.set_fin401_to_reject",self)
        for fin401 in self:
            fin401.check_reject = True
            fin401.state = "reject"
        return True

    @api.multi
    def fin_set_to_draft(self):
        res = super(fw_pfb_FS401, self).fin_set_to_draft()
        if self.approver:
            self.approver.write({'user_id': ''})
        # Stamp Log
        # employee_obj = self.env['hr.employee'].search([
        #     ('user_id', '=', self._uid),
        # ])
        # if employee_obj:
        #     user_name = _("%s" % employee_obj.name)
        # else:
        #     user_obj = self.env['res.users'].search([
        #         ('id', '=', self._uid),
        #     ])
        #     user_name = _("%s" % user_obj.name)
        # self.message_post(
        #     body=_("<b><u>%s</u></b><br />%s : <b>%s</b><br />Action : %s <br />Date/Time : %s" % (
        #         "SYSTEM LOG",
        #         "Employee" if employee_obj else "User",
        #         str(user_name),
        #         "FIN401 Set to Draft",
        #         str(self.write_date),
        #     ))
        # )
        log_message = message_log_stamp(self, "FIN401 Set to Draft", self.write_date)
        self.message_post(body=_(log_message))
        
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_fin = self.env['fw_pfb_fin_system_401']
        env_fin_approver = self.env['fw_pfb_fin_system_401_approver']
        params = self._context.get('params')
        checkRule = False
        if params:
            if "action" in params:
               if params["action"] == 1125:
                   checkRule = True
        res = super(fw_pfb_FS401, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if checkRule:
            fin401_domain = [
                ('state','not in',['draft','cancelled','reject', 'completed']),
            ]
            fin_list = env_fin.search(fin401_domain)
            to_hide_fin_list = env_fin.search([('id','not in',fin_list.ids)])
            if to_hide_fin_list:
                to_hide_fin_list.write({'show_fin': False})
            print("FOUND-FIN401 >>>>>", len(fin_list))
            for fin in fin_list:
                fin_user = []

                if fin.check_reject != True :
                    if fin.next_approval_user_ids:
                        fin_user += fin.next_approval_user_ids.ids
                    if fin.next_comment_user_ids:
                        fin_user += fin.next_comment_user_ids.ids

                if self._uid in fin_user:
                    if not fin.show_fin : # if show_fin is False
                        fin.show_fin = True
                else:
                    if fin.show_fin : # if show_fin is True
                        fin.show_fin = False
        return res

    @api.model
    def cron_action_generate_mail_to_approve(self):
        return self.action_generate_mail_to_approve()

    @api.multi
    def action_generate_mail_to_approve(self):
        # schedule on 10:00 and 14:00
        FIN401 = self.env['fw_pfb_fin_system_401']
        EMAIL = self.env['mail.mail']
        user_to_approve = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        domain = [
            ('state', 'not in', ['draft','completed','cancelled','reject']),
            ('next_approval_user_ids', '!=', False),
        ]
        fin401_to_approve_ids = FIN401.search(domain)
        print("action_generate_mail_to_approve",fin401_to_approve_ids)

        for fin401 in fin401_to_approve_ids:
            users = fin401.mapped('next_approval_user_ids')
            for user in users:
                user_to_approve.setdefault(user, FIN401)
                user_to_approve[user] |= fin401

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for user, docs in user_to_approve.items():
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN401 ใหม่ที่ต้องอนุมัติ จำนวน "+ str(len(docs)) +u" รายการ"
            message += u"<br/>"
            for doc_name in docs.sorted(lambda d: d.fin_no).mapped('fin_no'):
                message += u""+ doc_name +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">ระบบจะส่ง e-mail อัตโนมัติ ในเวลา 10:00 น. ของทุกวัน และจะส่งอีกครั้งในเวลา 14:00 น. หากมีรายการใหม่เพิ่ม</font>"""

            email_to = user.partner_id.email or (user.employee_ids and user.employee_ids[0].es_email or False) or False
            if email_to and 'frontware' in email_to:
                email_to = False

            if email_to:
                values = {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_cc': email_cc or '',
                    'message_type': 'email',
                    'auto_delete': False,
                    'mail_server_id': mail_server_id,
                    'subject': u'FIN401 สรุปรายการที่รออนุมัติ',
                    'body_html': message,
                    'state': 'outgoing',
                }
                email = EMAIL.sudo().create(values)
                EMAIL |= email

        # email send now
        db_name = self.env['ir.config_parameter'].sudo().get_param('database.name') or ''
        if self.env.cr.dbname == db_name:
            if EMAIL:
                EMAIL.send()

        return True

    @api.model
    def cron_action_generate_mail_to_comment(self):
        return self.action_generate_mail_to_comment()

    @api.multi
    def action_generate_mail_to_comment(self):
        # schedule on 10:00 and 14:00
        FIN401 = self.env['fw_pfb_fin_system_401']
        EMAIL = self.env['mail.mail']
        user_to_comment = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        domain = [
            ('state', 'not in', ['draft','completed','cancelled','reject']),
            ('next_comment_user_ids', '!=', False),
        ]
        fin401_to_comment_ids = FIN401.search(domain)
        print("action_generate_mail_to_comment",fin401_to_comment_ids)

        for fin401 in fin401_to_comment_ids:
            users = fin401.mapped('next_comment_user_ids')
            for user in users:
                user_to_comment.setdefault(user, FIN401)
                user_to_comment[user] |= fin401

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for user, docs in user_to_comment.items():
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN401 ใหม่ที่สามารถออกความเห็นได้ จำนวน "+ str(len(docs)) +u" รายการ"
            message += u"<br/>"
            for doc_name in docs.sorted(lambda d: d.fin_no).mapped('fin_no'):
                message += u""+ doc_name +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">ระบบจะส่ง e-mail อัตโนมัติ ในเวลา 10:00 น. ของทุกวัน และจะส่งอีกครั้งในเวลา 14:00 น. หากมีรายการใหม่เพิ่ม</font>"""

            email_to = user.partner_id.email or (user.employee_ids and user.employee_ids[0].es_email or False) or False
            if email_to and 'frontware' in email_to:
                email_to = False

            if email_to:
                values = {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_cc': email_cc or '',
                    'message_type': 'email',
                    'auto_delete': False,
                    'mail_server_id': mail_server_id,
                    'subject': u'FIN401 สรุปรายการที่รอความเห็น',
                    'body_html': message,
                    'state': 'outgoing',
                }
                email = EMAIL.sudo().create(values)
                EMAIL |= email

        # email send now
        db_name = self.env['ir.config_parameter'].sudo().get_param('database.name') or ''
        if self.env.cr.dbname == db_name:
            if EMAIL:
                EMAIL.send()

        return True

    @api.multi
    def action_generate_mail_to_reject(self):
        # schedule now when rejected
        print("action_generate_mail_to_reject",self)
        FIN401 = self.env['fw_pfb_fin_system_401']
        EMAIL = self.env['mail.mail']
        user_to_comment = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for fin401 in self:
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN401 ที่ถูกปฏิเสธ จำนวน "+ str('1') +u" รายการ"
            message += u"<br/>"
            message += u""+ fin401.fin_no +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">regards</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">Administrator</font>"""

            user = fin401.requester.user_id
            email_to = user.partner_id.email or (user.employee_ids and user.employee_ids[0].es_email or False) or False
            if email_to and 'frontware' in email_to:
                email_to = False

            if email_to:
                values = {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_cc': email_cc or '',
                    'message_type': 'email',
                    'auto_delete': False,
                    'mail_server_id': mail_server_id,
                    'subject': u'FIN401 สรุปรายการที่ถูกปฏิเสธ',
                    'body_html': message,
                    'state': 'outgoing',
                }
                email = EMAIL.sudo().create(values)
                EMAIL |= email

        # email send now
        db_name = self.env['ir.config_parameter'].sudo().get_param('database.name') or ''
        if self.env.cr.dbname == db_name:
            if EMAIL:
                EMAIL.send()

        return True

    @api.multi
    def get_action_fin_401_to_approve(self):
        action = {
            'name': _("FIN401 Pending"),
            'type': "ir.actions.act_window",
            'res_model': "fw_pfb_fin_system_401",
            'view_id': self.env.ref('fin_system.fin_system_401_pending_tree_view').id,
            'view_type': "form",
            'view_mode': "tree,form",
        }
        action['views'] = [
            (self.env.ref('fin_system.fin_system_401_pending_tree_view').id, 'tree'),
            (self.env.ref('fin_system.fin_system_401_request_form_view').id, 'form'),
        ]
        action['domain'] = """[
            ('state','not in',['draft', 'cancelled', 'reject', 'completed']),
            '|', ('next_approval_user_ids', 'in', %s),
                 ('next_comment_user_ids', 'in', %s),
        ]""" %(self.env.user.ids, self.env.user.ids)
        return action

class fw_pfb_FS401Lines(models.Model):
    _inherit = 'fw_pfb_fin_system_401_line'

    id = fields.Integer(string='ID')
    fin401_id = fields.Many2one("fw_pfb_fin_system_401", string="FIN401 No.", related="fin_id")

    fin100_line_id = fields.Many2one("fw_pfb_fin_system_100_line", string="FIN100 Line")
    fin100_id = fields.Many2one("fw_pfb_fin_system_100", string="FIN100 No.", related="fin100_line_id.fin_id")

    fin100_line_residual = fields.Float(string='FIN100 Line Residual')
    fin100_line_residual_amount = fields.Float(string='FIN100 Line Residual Amount')
    fin401_current_amount = fields.Float('FIN401 Current Amount')
    fin201_current_amount = fields.Float('FIN201 Current Amount')

    product_id = fields.Many2one('product.product', string="Product") # set string
    fin401_state = fields.Selection(selection=ORIG_FIN401.STATE_SELECTION, string='FIN401 State', related="fin_id.state", index=True)
    trigger = fields.Integer(string="trigger")

    @api.onchange('lend')
    def onchange_lend(self):
        print("FIN401_LINE.onchange_lend",self)
        if self.lend:
            self.fin100_line_residual_amount = self.fin100_line_residual - self.lend
        else:
            self.fin100_line_residual_amount = False

    @api.constrains('fin100_line_residual_amount')
    def _check_amount(self):
        print("FIN401_LINE._check_amount",self)
        for fin401_line in self:
            if fin401_line.fin100_line_residual_amount < 0.0:
                raise ValidationError(_('Budget is not enough for this request'))

    @api.multi
    def button_trigger(self):
        print("FIN401_LINE.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
        return True

class fw_pfb_FS401Approver(models.Model):
    _inherit = 'fw_pfb_fin_system_401_approver'

    approval_type = fields.Selection([
        #('optional', 'Approves, but the approval is optional'),
        ('mandatory', 'Is required to approve'),
        ('comment', 'Comments only'),
        ], 'Approval Type',
        default='mandatory', required=True)
    approve_step = fields.Integer(string='Step', default=0, required=True)
    trigger = fields.Integer(string="trigger")
    user_id = fields.Many2one('res.users', string="Approved by", copy=False)
    state = fields.Selection(selection_add=[('comment', 'Comment')])
    can_reset = fields.Boolean('Can Reset', compute='_compute_can_reset')

    def _compute_can_reset(self):
        print("FIN401_APPROVER._compute_can_reset",self)
        for approval in self:
            approval.can_reset = False
            last_approval = approval.fin_id.approver.filtered(lambda app: app.approval_type=='mandatory' and app.approve_active==True).sorted(lambda app: app.position_index)
            if last_approval:
                last_approval = last_approval[-1]
                if last_approval == approval and last_approval.state != 'pending':
                    if self.env.user.id in last_approval.employee_user_id.ids:
                        approval.can_reset = True
                    else:
                        approval.can_reset = False
            # force admin can reset for all
            if self.env.user.id == 2:
                approval.can_reset = True

    @api.multi
    @api.depends('employee_id','fin_position', 'approve_step')
    def name_get(self):
        print("FIN401_APPROVER.name_get",self)
        res = []
        for obj in self:
            name = obj.employee_id.display_name
            if obj.fin_position:
                fin_position = dict(obj._fields.get('fin_position').selection).get(obj.fin_position)
                name = "%s: %s"%(fin_position, name)
            if obj.approve_step:
                name = "Step %s. %s"%(obj.approve_step, name)
            res.append((obj.id, name))
        return res and res or super(fw_pfb_FS401Approver, self).name_get()

    @api.multi
    def update_fin_status(self):
        print("FIN401_APPROVER.update_fin_status", self)
        for approval_id in self:
            if approval_id.approve_position == 'DirectorOfDepartment':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DirectorOfDepartment'
                    approval_id.fin_id.target_approver = 'RelatedGroup'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfDepartment'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfDepartment'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'DirectorOfDepartment'
                        approval_id.fin_id.target_approver = 'RelatedGroup'
            elif approval_id.approve_position == 'RelatedGroup':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'RelatedGroup'
                    approval_id.fin_id.target_approver = 'DirectorOfFinance'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'RelatedGroup'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'RelatedGroup'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'RelatedGroup'
                        approval_id.fin_id.target_approver = 'DirectorOfFinance'
            elif approval_id.approve_position == 'DirectorOfFinance':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DirectorOfFinance'
                    approval_id.fin_id.target_approver = 'AssistantOfOffice'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfFinance'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfFinance'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'DirectorOfFinance'
                        approval_id.fin_id.target_approver = 'AssistantOfOffice'
            elif approval_id.approve_position == 'AssistantOfOffice':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'AssistantOfOffice'
                    approval_id.fin_id.target_approver = 'DeputyOfOffice'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'AssistantOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'AssistantOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'AssistantOfOffice'
                        approval_id.fin_id.target_approver = 'DeputyOfOffice'
            elif approval_id.approve_position == 'DeputyOfOffice':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DeputyOfOffice'
                    approval_id.fin_id.target_approver = 'SmallNote'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DeputyOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DeputyOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'DeputyOfOffice'
                        approval_id.fin_id.target_approver = 'SmallNote'
            elif approval_id.approve_position == 'SmallNote':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'SmallNote'
                    approval_id.fin_id.target_approver = 'DirectorOfOffice'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'SmallNote'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'SmallNote'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'SmallNote'
                        approval_id.fin_id.target_approver = 'DirectorOfOffice'
            elif approval_id.approve_position == 'DirectorOfOffice':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DirectorOfOffice'
                    approval_id.fin_id.target_approver = 'DirectorOfOffice'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_401_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('state', '=', 'comment'),
                    ])
                    comment_all = len(comment_approval_obj)
                    commented_count = len(commented_approval_obj)
                    if comment_all == commented_count:
                        approval_id.fin_id.state = 'DirectorOfOffice'
                        approval_id.fin_id.target_approver = 'DirectorOfOffice'
        return True

    @api.multi
    def button_trigger(self):
        print("FIN401_APPROVER.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
        return True

    @api.multi
    def action_reset_approval(self):
        print("FIN401_APPROVER.button_reset_approval",self)
        for approval in self:
            approval.write({
                'memo': '',
                'action_date': False,
                'state': 'pending',
                'user_id': False,
            })
            lastest_approval_id = approval.fin_id.approver.filtered(lambda app: app.approval_type=='mandatory' and app.state=='approve' and app.approve_active==True)
            lastest_approval_id.update_fin_status()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

class WizardFIN401Approval(models.TransientModel):
    """
    This wizard will Approve/Reject/Comment for FIN401
    """
    _name = "wizard.fin401.approval"
    _description = "FIN401 Approval"

    def _default_next_approval(self):
        print("_default_next_approval",self)
        res = False
        if self._context.get('next_approval_id'):
            res = self.env['fw_pfb_fin_system_401_approver'].browse(self._context.get('next_approval_id'))
        return res

    def _default_next_comment(self):
        print("_default_next_comment",self)
        fin401_ids = self.env['fw_pfb_fin_system_401'].browse(self._context.get('active_ids'))
        next_comment_ids = fin401_ids.mapped('next_comment_ids').sorted(lambda x: x.id).ids
        return next_comment_ids

    def _default_next_comment_user(self):
        print("_default_next_comment_user",self)
        fin401_ids = self.env['fw_pfb_fin_system_401'].browse(self._context.get('active_ids'))
        next_comment_user_ids = fin401_ids.mapped('next_comment_ids').sorted(lambda x: x.id).mapped('employee_user_id')
        return next_comment_user_ids

    next_approval_id = fields.Many2one('fw_pfb_fin_system_401_approver', string='Next Approval', default=_default_next_approval)
    employee_user_id = fields.Many2one('res.users', string='Requested User', related="next_approval_id.employee_user_id")

    next_comment_ids = fields.Many2many('fw_pfb_fin_system_401_approver', string='Next Comment', default=_default_next_comment)
    next_comment_user_ids = fields.Many2many('res.users', string='Next Comment Users', default=_default_next_comment_user)

    approval_type = fields.Selection([
        #('optional', 'Approves, but the approval is optional'),
        ('mandatory', 'Is required to approve'),
        ('comment', 'Comments only'),
        ], 'Approval Type',
        related="next_approval_id.approval_type")
    note = fields.Text(string="Memo", required=True)

    @api.multi
    def action_approve(self):
        print("WIZARD_FIN401_APPROVAL.action_approve",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin401_ids = self.env['fw_pfb_fin_system_401'].browse(active_ids)
        for fin401 in fin401_ids:
            fin401.action_set_approve(note=self.note)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reject(self):
        print("WIZARD_FIN401_APPROVAL.action_reject",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin401_ids = self.env['fw_pfb_fin_system_401'].browse(active_ids)
        for fin401 in fin401_ids:
            fin401.action_set_reject(note=self.note)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_comment(self):
        print("WIZARD_FIN401_APPROVAL.action_comment",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin401_ids = self.env['fw_pfb_fin_system_401'].browse(active_ids)
        for fin401 in fin401_ids:
            fin401.action_set_comment(note=self.note)
        return {'type': 'ir.actions.act_window_close'}
