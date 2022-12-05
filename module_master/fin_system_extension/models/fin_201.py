# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.fin_system.models.fin_201 as ORIG_FIN201
from random import randrange
from odoo.addons.fin_system.models.fin_middleware import message_log_stamp


class fw_pfb_FS201(models.Model):
    _inherit = 'fw_pfb_fin_system_201'
    _rec_name = 'fin_no'

    price_total = fields.Float(string='Total', compute='_compute_total', store=True) # set store, no need to compute all the time
    trigger = fields.Integer(string="trigger")

    next_approval_id = fields.Many2one('fw_pfb_fin_system_201_approver', string='Next Approval', compute='_compute_next_approval', store=True)
    next_approval_ids = fields.Many2many('fw_pfb_fin_system_201_approver', string='Next Approval IDS',
        relation="fin201_approval_approver_rel", column1='fin201_id', column2='approval_id', compute='_compute_next_approval', store=True)
    next_approval_user_ids = fields.Many2many('res.users', string='Next Approval Users',
        relation="fin201_approval_res_users_rel", column1='fin201_id', column2='user_id', compute='_compute_next_approval', store=True)
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    next_comment_ids = fields.Many2many('fw_pfb_fin_system_201_approver', string='Next Comment',
        relation="fin201_approval_comment_rel", column1='fin201_id', column2='approval_id', compute='_compute_next_comment', store=True)
    next_comment_user_ids = fields.Many2many('res.users', string='Next Comment Users',
        relation="fin201_comment_res_users_rel", column1='fin201_id', column2='user_id', compute='_compute_next_comment', store=True)
    can_comment = fields.Boolean('Can Comment', compute='_compute_can_comment')
    can_complete = fields.Boolean('Can Complete', compute='_compute_can_complete')

    def _compute_can_complete(self):
        print("FIN201._compute_can_complete",self)
        for fin201 in self:
            fin201.can_complete = False
            last_approval = fin201.approver and fin201.approver.sorted(lambda app: app.position_index)[-1] or False
            if last_approval:
                if self.env.user.id in last_approval.employee_user_id.ids:
                    fin201.can_complete = True
                else:
                    fin201.can_complete = False
                # force admin can complete
                if self.env.user.id == 1:
                    fin201.can_complete = True
            if fin201.is_fin_lock:
                fin201.can_complete = False

    @api.multi
    @api.depends('state', 'approver',
        'approver.employee_id', 'approver.employee_id.user_id', 'approver.employee_user_id',
        'approver.action_date', 'approver.state', 'trigger')
    def _compute_next_approval(self):
        print("FIN201._compute_next_approval",self)
        for fin201 in self:
            if fin201.state == 'reject':
                fin201.next_approval_id = False
                return True
            latest_approval_ids = fin201.approver.filtered(lambda app: app.approval_type=='mandatory' and app.state=='approve' and app.approve_active==True)
            latest_approval = latest_approval_ids and latest_approval_ids[-1]
            if latest_approval:
                approval_ids_ready = fin201.approver\
                    .filtered(lambda app: app.approval_type=='mandatory' and app.position_index > latest_approval.position_index and app.state=='pending' and app.approve_active==True)
            else:
                approval_ids_ready = fin201.approver\
                    .filtered(lambda app: app.approval_type=='mandatory' and app.state=='pending' and app.approve_active==True)

            if approval_ids_ready:
                fin201.next_approval_id = approval_ids_ready[0]
                fin201.next_approval_ids = approval_ids_ready
                fin201.next_approval_user_ids = approval_ids_ready[0].mapped('employee_user_id')

            overrule_states = ['DirectorOfFinance','AssistantOfOffice','DeputyOfOffice','SmallNote']
            #overrule_states = []
            #for state in ORIG_FIN201.STATE_SELECTION:
                #if state[0] in ['draft','sent','completed','cancelled', 'reject']:
                    #continue
                #overrule_states.append(state[0])

            if fin201.state in overrule_states:
                #fin201.next_approval_user_ids |= fin201.approver.sorted(lambda app: app.position_index)[-1].mapped('employee_user_id')
                fin201.next_approval_user_ids |= fin201.approver\
                    .filtered(lambda app: app.approve_active==True)\
                    .sorted(lambda app: app.position_index)[-1].mapped('employee_user_id')

    @api.depends('next_approval_id', 'next_approval_user_ids', 'state', 'trigger')
    def _compute_can_approve(self):
        print("FIN201._compute_can_approve",self)
        for fin201 in self:
            #if self.env.user == fin201.next_approval_id.employee_user_id:
            if self.env.user in fin201.next_approval_user_ids:
                fin201.can_approve = True
            else:
                fin201.can_approve = False
            # force admin can approve
            if self.env.user.id == 1 and fin201.next_approval_id:
                fin201.can_approve = True

    @api.multi
    @api.depends('state', 'approver', 'next_approval_id', 'trigger', 'approver.position_index', 'approver.approve_step',
        'approver.employee_id', 'approver.employee_id.user_id', 'approver.employee_user_id',
        'approver.action_date', 'approver.state', 'approver.approval_type')
    def _compute_next_comment(self):
        print("FIN201._compute_next_comment",self)
        for fin201 in self:
            approval_ids = self.env['fw_pfb_fin_system_201_approver']
            approval_ids |= fin201.approver\
                .filtered(lambda app: app.approve_active and app.approval_type=='comment' and app.approve_step <= fin201.next_approval_id.approve_step and (not app.state or app.state=='pending'))
            approval_ids |= fin201.approver.filtered(lambda app: app.approval_type=='comment') and fin201.approver.filtered(lambda app: app.approval_type=='comment')[-1]
            fin201.next_comment_ids = approval_ids.sorted(lambda app: app.position_index)
            if fin201.next_comment_ids:
                fin201.next_comment_user_ids = fin201.next_comment_ids.mapped('employee_user_id')

    @api.depends('next_comment_ids', 'next_comment_user_ids', 'next_comment_ids.employee_user_id', 'state', 'trigger')
    def _compute_can_comment(self):
        print("FIN201._compute_can_comment",self)
        for fin201 in self:
            if self.env.user in fin201.next_comment_user_ids:
                fin201.can_comment = True
            else:
                fin201.can_comment = False
            # force admin can approve
            if self.env.user.id == 1 and fin201.next_comment_ids:
                fin201.can_comment = True

    @api.multi
    @api.depends('fin_lines.price_subtotal', 'trigger')
    def _compute_total(self):
        print("FIN201._compute_total",self)
        for fin in self:
            #fin.objective = False
            fin.approved_amount = 0
            fin.request_amount_total = 0
            fin.load_amount_total = 0
            fin.price_total = 0
            fin.remaining_total = 0

            for line in fin.fin_lines:
                if line.objective and not fin.objective:
                    fin.objective = line.objective
                if line.price_subtotal:
                    fin.approved_amount = fin.approved_amount + line.price_subtotal
                    fin.request_amount_total = fin.approved_amount
                if line.loan_amount:
                    fin.load_amount_total = fin.load_amount_total + line.loan_amount
                if line.payment_amount:
                    fin.price_total = fin.price_total + line.payment_amount
            fin.remaining_total = fin.load_amount_total - fin.spent_amount_total

    @api.multi
    def compute_fin201_line_residual(self):
        print("FIN201.compute_fin201_line_residual",self)
        for fin201 in self:
            if fin201.fin_projects:
                fin201.fin_projects.unlink()
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
    def button_force_compute_fin201_lines(self):
        print("FIN201.button_force_compute_fin201_lines",self)
        for fin201 in self:
            # compute residual in fin100_line._compute_fin100_line_balance()
            if fin201.state in ['cancelled','reject']:
                fin201.fin_lines.write({
                    'fin100_line_residual': 0.0,
                    'fin100_line_residual_amount': 0.0,
                })
                continue
        return True

    @api.multi
    def action_set_draft(self):
        print("FIN201.action_set_draft",self)
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
        print("FIN201.action_set_done",self)
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
        print("FIN201.action_set_cancel",self)
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
        #         "FIN201 Set to Cancel",
        #         str(self.write_date),
        #     ))
        # )
        log_message = message_log_stamp(self, "FIN201 Set to Cancel", self.write_date)
        self.message_post(body=_(log_message))

    @api.multi
    def write(self, vals):
        print("FIN201.write", self, vals)
        approved_amount_total = 0
        for line in self.fin_lines:
            approved_amount_total += line.price_subtotal
        vals['approved_amount'] = approved_amount_total
        res = super(fw_pfb_FS201, self).write(vals)
        if 'fin_lines' in vals or 'state' in vals:
            self.button_force_compute_fin201_lines()
        return res

    @api.onchange('flow_template')
    def _onchange_flow_template(self):
        print("FIN201._onchange_flow_template",self)
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
        print("FIN201.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
            obj.approver.button_trigger()
            obj.fin_lines.button_trigger()
        return True

    @api.multi
    def action_set_approve(self, note=""):
        print("FIN201.action_set_approve",self)
        for fin201 in self:
            approval = fin201.next_approval_id

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin201.next_approval_user_ids:
                    approval = fin201.next_approval_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
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
                latest_approval = fin201.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def action_set_reject(self, note=""):
        print("FIN201.action_set_reject",self)
        for fin201 in self:
            approval = fin201.next_approval_id

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin201.next_approval_user_ids:
                    approval = fin201.next_approval_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
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
                fin201.set_fin201_to_reject()
                fin201.action_generate_mail_to_reject()
            else:
                latest_approval = fin201.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def action_set_comment(self, note=""):
        print("FIN201.action_set_comment",self)
        for fin201 in self:
            approval = fin201.next_comment_ids and fin201.next_comment_ids[0] or False

            if self.env.user != approval.user_id:
                if self.env.user.id == 1:
                    pass
                elif self.env.user in fin201.next_comment_user_ids:
                    approval = fin201.next_comment_ids.filtered(lambda app: app.employee_id.user_id == self.env.user)
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
                latest_approval = fin201.approver.sorted(lambda app: app.position_index)[-1]
                if self.env.user == latest_approval.mapped('employee_user_id') and not latest_approval.approve_active:
                    latest_approval.write({
                        'action_date': fields.Datetime.now(),
                        'user_id': self.env.uid,
                        'memo': note,
                    })
        return True

    @api.multi
    def set_fin201_to_reject(self):
        print("FIN201.set_fin201_to_reject",self)
        for fin201 in self:
            fin201.check_reject = True
            fin201.state = "reject"
        return True

    @api.multi
    def fin_set_to_draft(self):
        if self.fin_lines:
            self.fin_lines.write({'payment_amount': 0.0})
        res = super(fw_pfb_FS201, self).fin_set_to_draft()
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
        #         "FIN201 Set to Draft",
        #         str(self.write_date),
        #     ))
        # )
        log_message = message_log_stamp(self, "FIN201 Set to Draft", self.write_date)
        self.message_post(body=_(log_message))
        
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        env_fin = self.env['fw_pfb_fin_system_201']
        env_fin_approver = self.env['fw_pfb_fin_system_201_approver']
        params = self._context.get('params')
        checkRule = False
        if params:
            if "action" in params:
               if params["action"] == 1131:
                   checkRule = True
        res = super(fw_pfb_FS201, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if checkRule:
            fin201_domain = [
                ('state','not in',['draft','cancelled','reject', 'completed']),
            ]
            fin_list = env_fin.search(fin201_domain)
            to_hide_fin_list = env_fin.search([('id','not in',fin_list.ids)])
            if to_hide_fin_list:
                for todo in to_hide_fin_list:
                    todo.write({'show_fin': False})
                #to_hide_fin_list.write({'show_fin': False})
            print("FOUND-FIN201 >>>>>", len(fin_list))
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
        FIN201 = self.env['fw_pfb_fin_system_201']
        EMAIL = self.env['mail.mail']
        user_to_approve = {}

        mail_server_id = self.env['ir.config_parameter'].sudo().get_param('default_outgoing_mail_server') or False
        if not mail_server_id:
            mail_server_id = self.env['ir.mail_server'].search([], limit=1, order='sequence') and self.env['ir.mail_server'].search([], limit=1, order='sequence').id or False

        email_from = self.env['ir.config_parameter'].sudo().get_param('default_email_from') or False
        email_cc = self.env['ir.config_parameter'].sudo().get_param('default_email_cc') or False

        domain = [
            ('state', 'not in', ['draft','completed','cancelled']),
            ('next_approval_user_ids', '!=', False),
        ]
        fin201_to_approve_ids = FIN201.search(domain)
        print("action_generate_mail_to_approve",fin201_to_approve_ids)

        for fin201 in fin201_to_approve_ids:
            users = fin201.mapped('next_approval_user_ids')
            for user in users:
                user_to_approve.setdefault(user, FIN201)
                user_to_approve[user] |= fin201

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for user, docs in user_to_approve.items():
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN201 ใหม่ที่ต้องอนุมัติ จำนวน "+ str(len(docs)) +u" รายการ"
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
                    'subject': u'FIN201 สรุปรายการที่รออนุมัติ',
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
        FIN201 = self.env['fw_pfb_fin_system_201']
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
        fin201_to_comment_ids = FIN201.search(domain)
        print("action_generate_mail_to_comment",fin201_to_comment_ids)

        for fin201 in fin201_to_comment_ids:
            users = fin201.mapped('next_comment_user_ids')
            for user in users:
                user_to_comment.setdefault(user, FIN201)
                user_to_comment[user] |= fin201

        now = datetime.now()
        date_show = now.date().strftime("%Y-%m-%d")
        time_show = (now + timedelta(hours=7)).strftime("%H:%M")

        for user, docs in user_to_comment.items():
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN201 ใหม่ที่สามารถออกความเห็นได้ จำนวน "+ str(len(docs)) +u" รายการ"
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
                    'subject': u'FIN201 สรุปรายการที่รอความเห็น',
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
        FIN201 = self.env['fw_pfb_fin_system_201']
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

        for fin201 in self:
            message = u"<b>วันที่ "+ date_show +" "+ time_show  +u"</b>"
            message += u"<br/>"
            message += u"<br/>"
            message += u"คุณมี FIN201 ที่ถูกปฏิเสธ จำนวน "+ str('1') +u" รายการ"
            message += u"<br/>"
            message += u""+ fin201.fin_no +"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">โปรดเข้าสู่ระบบเพื่อตรวจสอบ</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">regards</font>"""
            message += u"<br/>"
            message += u"<br/>"
            message += u"""<font style="font-size: 14px;">Administrator</font>"""

            user = fin201.requester.user_id
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
                    'subject': u'FIN201 สรุปรายการที่ถูกปฏิเสธ',
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
    def get_action_fin_201_to_approve(self):
        action = {
            'name': _("FIN201 Pending"),
            'type': "ir.actions.act_window",
            'res_model': "fw_pfb_fin_system_201",
            'view_id': self.env.ref('fin_system.fin_system_201_pending_tree_view').id,
            'view_type': "form",
            'view_mode': "tree,form",
        }
        action['views'] = [
            (self.env.ref('fin_system.fin_system_201_pending_tree_view').id, 'tree'),
            (self.env.ref('fin_system.fin_system_201_request_form_view').id, 'form'),
        ]
        action['domain'] = """[
            ('state','not in',['draft', 'cancelled', 'reject', 'completed']),
            '|', ('next_approval_user_ids', 'in', %s),
                 ('next_comment_user_ids', 'in', %s),
        ]""" %(self.env.user.ids, self.env.user.ids)
        return action

    @api.depends('approver')
    def _get_approver_rights(self):
        rights = ''
        approver_list = []
        for list in self.approver:
            approver_list.append(list.employee_user_id.id)
        if self._uid in approver_list:
            approver = self.env['fw_pfb_fin_system_201_approver'].search(
                [('fin_id', '=', self.id), ('employee_user_id.id', '=', self._uid)])
            if len(approver) > 1:
                for ap in approver:
                    # FIX not found ap.fin_position
                    if ap.fin_position:
                        rights += ap.fin_position + ' , '
            else:
                rights = approver.fin_position

        else:
            rights = 'fin_user'
        self.approver_rights = rights
        if rights == 'director':
            self.is_director = True

class fw_pfb_FS201Lines(models.Model):
    _inherit = 'fw_pfb_fin_system_201_line'

    id = fields.Integer(string='ID')
    fin201_id = fields.Many2one("fw_pfb_fin_system_201", string="FIN201 No.", related="fin_id")

    fin401_id = fields.Many2one(
        'fw_pfb_fin_system_401',
        string='FIN401',
    )

    fin100_line_id = fields.Many2one("fw_pfb_fin_system_100_line", string="FIN100 Line")
    fin100_id = fields.Many2one("fw_pfb_fin_system_100", string="FIN100 No.", related="fin100_line_id.fin_id")

    fin100_line_residual = fields.Float(string='FIN100 Line Residual')
    fin100_line_residual_amount = fields.Float(string='FIN100 Line Residual Amount')
    fin401_current_amount = fields.Float('FIN401 Current Amount')
    fin201_current_amount = fields.Float('FIN201 Current Amount')

    product_id = fields.Many2one('product.product', string="Product") # set string
    fin201_state = fields.Selection(selection=ORIG_FIN201.STATE_SELECTION, string='FIN201 State', related="fin_id.state", index=True)
    trigger = fields.Integer(string="trigger")

    @api.onchange('payment_amount')
    def onchange_payment_amount(self):
        print("FIN201_LINE.onchange_payment_amount",self)
        self.fin100_line_residual_amount = self.price_subtotal - self.payment_amount
        # if self.payment_amount:
        #     #self.fin100_line_residual = self.fin100_line_id.balance + self.payment_amount
        #     #self.fin100_line_residual_amount = self.fin100_line_id.balance
        #     self.fin100_line_residual_amount = self.fin100_line_id.fin201_balance_amount# - self.payment_amount
        # else:
        #     #self.fin100_line_residual = False
        #     self.fin100_line_residual_amount = False

    @api.model
    def create(self, vals):
        print("FIN201_LINE.create",vals)
        return super(fw_pfb_FS201Lines, self).create(vals)

    @api.multi
    def write(self, vals):
        print("FIN201_LINE.write", self, vals)
        return super(fw_pfb_FS201Lines, self).write(vals)

    @api.multi
    def button_trigger(self):
        print("FIN201_LINE.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
        return True

class fw_pfb_FS201Approver(models.Model):
    _inherit = 'fw_pfb_fin_system_201_approver'

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
        print("FIN201_APPROVER._compute_can_reset",self)
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
        print("FIN201_APPROVER.name_get",self)
        res = []
        for obj in self:
            name = obj.employee_id.display_name
            if obj.fin_position:
                fin_position = dict(obj._fields.get('fin_position').selection).get(obj.fin_position)
                name = "%s: %s"%(fin_position, name)
            if obj.approve_step:
                name = "Step %s. %s"%(obj.approve_step, name)
            res.append((obj.id, name))
        return res and res or super(fw_pfb_FS201Approver, self).name_get()

    @api.multi
    def update_fin_status(self):
        print("FIN201_APPROVER.update_fin_status", self)
        for approval_id in self:
            if approval_id.approve_position == 'DirectorOfDepartment':
                if approval_id.state == 'approve':
                    approval_id.fin_id.state = 'DirectorOfDepartment'
                    approval_id.fin_id.target_approver = 'RelatedGroup'
                elif approval_id.state == 'comment':
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfDepartment'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'RelatedGroup'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfFinance'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'AssistantOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DeputyOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'SmallNote'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
                    comment_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
                        ('fin_id', '=', approval_id.fin_id.id),
                        ('approve_position', '=', 'DirectorOfOffice'),
                        ('approval_type', '=', 'comment'),
                        ('approve_active', '=', True)
                    ])
                    commented_approval_obj = self.env['fw_pfb_fin_system_201_approver'].search([
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
        print("FIN201_APPROVER.button_trigger",self)
        for obj in self:
            obj.trigger = randrange(1000001)
        return True

    @api.multi
    def action_reset_approval(self):
        print("FIN201_APPROVER.button_reset_approval",self)
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

class WizardFIN201Approval(models.TransientModel):
    """
    This wizard will Approve/Reject/Comment for FIN201
    """
    _name = "wizard.fin201.approval"
    _description = "FIN201 Approval"

    def _default_next_approval(self):
        print("_default_next_approval",self)
        res = False
        if self._context.get('next_approval_id'):
            res = self.env['fw_pfb_fin_system_201_approver'].browse(self._context.get('next_approval_id'))
        return res
    
    def _default_next_comment(self):
        print("_default_next_comment",self)
        fin201_ids = self.env['fw_pfb_fin_system_201'].browse(self._context.get('active_ids'))
        next_comment_ids = fin201_ids.mapped('next_comment_ids').sorted(lambda x: x.id).ids
        return next_comment_ids
    
    def _default_next_comment_user(self):
        print("_default_next_comment_user",self)
        fin201_ids = self.env['fw_pfb_fin_system_201'].browse(self._context.get('active_ids'))
        next_comment_user_ids = fin201_ids.mapped('next_comment_ids').sorted(lambda x: x.id).mapped('employee_user_id')
        return next_comment_user_ids
    
    next_approval_id = fields.Many2one('fw_pfb_fin_system_201_approver', string='Next Approval', default=_default_next_approval)
    employee_user_id = fields.Many2one('res.users', string='Requested User', related="next_approval_id.employee_user_id")
    
    next_comment_ids = fields.Many2many('fw_pfb_fin_system_201_approver', string='Next Comment', default=_default_next_comment)
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
        print("WIZARD_FIN201_APPROVAL.action_approve",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin201_ids = self.env['fw_pfb_fin_system_201'].browse(active_ids)
        for fin201 in fin201_ids:
            fin201.action_set_approve(note=self.note) 
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reject(self):
        print("WIZARD_FIN201_APPROVAL.action_reject",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin201_ids = self.env['fw_pfb_fin_system_201'].browse(active_ids)
        for fin201 in fin201_ids:
            fin201.action_set_reject(note=self.note)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_comment(self):
        print("WIZARD_FIN201_APPROVAL.action_comment",self)
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        fin201_ids = self.env['fw_pfb_fin_system_201'].browse(active_ids)
        for fin201 in fin201_ids:
            fin201.action_set_comment(note=self.note)
        return {'type': 'ir.actions.act_window_close'}
