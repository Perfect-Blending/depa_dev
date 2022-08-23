# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from pytz import timezone
import smtplib
from odoo.http import request
from requests import get

class leave_request(models.Model):
    _name = 'leave_request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_info(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ], limit=1)
        return employee

    def _get_employee_id(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ], limit=1)
        return employee.id

    def _get_employee_quota(self):
        quota_year = self.env['leave_setting_employee'].search([
            ('year', '=', self._default_fiscal_year())
        ], limit=1)
        if quota_year:
            employee_quota = self.env['leave_setting_employee_lines'].search([
                ('hr_employee_id', '=', quota_year['id']),
                ('employee_id', '=', self._get_employee_id())
            ], limit=1)
            if employee_quota:
                return employee_quota
        return False

    def _get_employee_quota_for_approver(self):
        quota_year = self.env['leave_setting_employee'].search([
            ('year', '=', self._default_fiscal_year())
        ], limit=1)
        if quota_year:
            employee_quota = self.env['leave_setting_employee_lines'].search([
                ('hr_employee_id', '=', quota_year['id']),
                ('employee_id', '=', self.requester_id.id)
            ], limit=1)
            if employee_quota:
                return employee_quota
        return False

    def _get_all_state(self):
        states = self.env['leave_request_state'].search([
            ('active', '=', True)
        ])
        data = []
        for state in states:
            data.append((state.state, state.name))
        return data

    def _get_state_id(self, state):
        state_record = self.env['leave_request_state'].search([
            ('state', '=', state)
        ], limit=1)
        if state_record:
            return state_record.id

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)

        if fiscal_year_obj:
            return fiscal_year_obj.id


    def _get_public_holidays(self):
        this_year_holidays = self.env['leave_request_public_holidays'].search([
            ('fiscal_year_id', '=', self._default_fiscal_year())
        ], limit=1)

        if this_year_holidays:
            public_holidays = self.env['leave_request_public_holidays_lines'].search([
                ('leave_request_public_holidays_lines_id', '=', this_year_holidays.id)
            ])
            if public_holidays:
                data = []
                for holiday in public_holidays:
                    holiday_detail = self.env['leave_request_public_holidays_lines'].search([
                        ('id', '=', holiday['id'])
                    ])
                    if holiday_detail:
                        data.append(holiday_detail['date'])
                return data

    def _check_quota_sending(self):
        quota = self._get_employee_quota()
        request_days = self.request_days
        type_en_name = self.request_type_id.en_name
        # กรณีเลือกประเภทการลาเป็น วันลาพักผ่อน
        if type_en_name == "vacation":
            quota_days = quota['vacation']
            # กรณีมีวันลาพักผ่อนยกยอด มากกว่า 0 วัน
            if quota_days > 0:
                # กรณีขอลามากกว่าจำนวนวันลาพักผ่อนยกยอดที่เหลือ
                # จะทำการหักวันลาพักผ่อนยกยอดจนเหลือ 0 และนำส่วนต่างไปหักจากโควต้าวันลาพักผ่อน
                if request_days > quota_days:
                    delta_days = request_days - quota_days
                    vacation_days = quota['vacation_remaining']
                    remaining_days = vacation_days - delta_days
                    if remaining_days < 0:
                        raise ValidationError(_("จำนวนวันที่ขอลามากกว่าจำนวนโควต้าที่มี (ขอลา " + str(request_days) + \
                                                " วัน | โควต้า " + str(quota_days) + " + " + str(
                            vacation_days) + " = " + \
                                                str(quota_days + vacation_days) + " วัน)"))
                # กรณีที่มีวันลาพักผ่อนยกยอดเพียงพอ จะหักจากวันลาพักผ่อนยกยอดอย่างเดียว
            # กรณีไม่เหลือวันลาพักผ่อนยกยอด
            else:
                quota_days = quota['vacation_remaining']
                if request_days > quota_days:
                    raise ValidationError(
                        _("จำนวนวันที่ขอลามากกว่าจำนวนโควต้าที่มี (ขอลา " + str(request_days) + " วัน | โควต้า " + str(
                            quota_days) + " วัน)"))
        # กรณีเลือกประเภทการลาแบบอื่น
        else:
            quota_days = quota[type_en_name]
            if request_days > quota_days:
                raise ValidationError(
                    _("จำนวนวันที่ขอลามากกว่าจำนวนโควต้าที่มี (ขอลา " + str(request_days) + " วัน | โควต้า " + str(
                        quota_days) + " วัน)"))

    def _subtract_quota_approving(self):
        quota = self._get_employee_quota_for_approver()
        request_days = self.request_days
        type_en_name = self.request_type_id.en_name
        # กรณีเลือกประเภทการลาเป็น วันลาพักผ่อน
        if type_en_name == "vacation":
            quota_days = quota['vacation']
            # กรณีมีวันลาพักผ่อนยกยอด มากกว่า 0 วัน
            if quota_days > 0:
                # กรณีขอลามากกว่าจำนวนวันลาพักผ่อนยกยอดที่เหลือ
                # จะทำการหักวันลาพักผ่อนยกยอดจนเหลือ 0 และนำส่วนต่างไปหักจากโควต้าวันลาพักผ่อน
                if request_days > quota_days:
                    delta_days = request_days - quota_days
                    vacation_days = quota['vacation_remaining']
                    remaining_days = vacation_days - delta_days
                    if remaining_days < 0:
                        raise ValidationError(_("จำนวนวันที่ขอลามากกว่าจำนวนโควต้าที่มี (ขอลา "+str(request_days)+ \
                                                " วัน | โควต้า "+str(quota_days)+" + "+str(vacation_days)+" = "+ \
                                                str(quota_days+vacation_days)+" วัน)"))
                    else:
                        quota.update({
                            'vacation': 0,
                            'vacation_remaining': remaining_days
                        })
                # กรณีที่มีวันลาพักผ่อนเพียงพอ จะหักจากวันลาพักผ่อนอย่างเดียว
                else:
                    remaining_days = quota_days - request_days
                    quota.update({
                        'vacation': remaining_days
                    })
            # กรณีไม่เหลือวันลาพักผ่อน
            else:
                quota_days = quota['vacation_remaining']
                if request_days > quota_days:
                    raise ValidationError(_("จำนวนวันที่ขอลามากกว่าจำนวนโควต้าที่มี (ขอลา "+str(request_days)+" วัน | โควต้า "+str(quota_days)+" วัน)"))
                else:
                    remaining_days = quota_days - request_days
                    quota.update({
                        'vacation_remaining': remaining_days
                    })
        # กรณีเลือกประเภทการลาแบบอื่น
        else:
            quota_days = quota[type_en_name]
            if request_days > quota_days:
                raise ValidationError(_("จำนวนวันที่ขอลามากกว่าจำนวนโควต้าที่มี (ขอลา "+str(request_days)+" วัน | โควต้า "+str(quota_days)+" วัน)"))
            else:
                remaining_days = quota_days - request_days
                quota.update({
                    type_en_name: remaining_days
                })

    @api.depends('request_approval_id')
    def _get_request_approval_userid(self):
        for rec in self:
            approval = self.env['hr.employee'].search([
                ('id', '=', rec.request_approval_id.id)
            ], limit=1)
            if approval:
                rec.request_approval_user_id = approval.user_id.id


    requester_id = fields.Many2one(
        "hr.employee",
        string="ผู้ขออนุมัติ",
        default= lambda self: self._get_employee_id()
    )
    requester_department_id = fields.Many2one(
        "hr.department",
        string="สังกัด",
        default= lambda self: self._get_employee_info().department_id
    )
    request_type_id = fields.Many2one(
        "leave_request_types",
        string="ประเภทการลา",
        required=True,
        default=False
    )
    date_from = fields.Datetime(
        'จากวันที่',
        readonly=True,
        copy=False,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    date_to = fields.Datetime(
        'ถึงวันที่',
        readonly=True,
        copy=False,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    request_date_from = fields.Date(
        string="จากวันที่",
        track_visibility='onchange'
        # default=lambda self: date.today()
    )
    request_date_to = fields.Date(
        string="ถึงวันที่",
        track_visibility='onchange'
        # default=lambda self: date.today()
    )
    request_desc = fields.Text(
        string="รายละเอียด",
        track_visibility='onchange',
        required=True
    )
    is_not_full_day = fields.Boolean(
        string="ลาครึ่งวัน",
        default=False
    )
    request_days = fields.Float(
        string="ระยะเวลา (วัน)",
        compute='_compute_request_days',
        store=True
    )
    request_approval_id = fields.Many2one(
        "hr.employee",
        string="ผู้อนุมัติการลา",
        required=True,
        default=False
    )
    # request_approval_user_id = fields.Integer(
    #     compute='_get_request_approval_userid',
    #     store=True
    # )

    request_attachment_id = fields.Many2one(
        'leave_request'
    )
    request_attachment_ids = fields.Many2many(
        "ir.attachment",
        "request_attachment_rel",
        "request_attachment_id",
        "ir_attachment_id",
        string='เอกสารแนบ',
        # required=True
    )
    state = fields.Selection(
        # STATES
        lambda self: self._get_all_state(),
        string="สถานะ",
        default="draft",
        copy=False
    )
    state_id = fields.Many2one(
        'leave_request_state',
        string="สถานะ",
        default=lambda self: self._get_state_id(state='draft')
    )
    half_day_selection = fields.Selection(
        [
            ('morning', 'ครึ่งวันเช้า'),
            ('afternoon', 'ครึ่งวันบ่าย')
        ],
        track_visibility='onchange',
        string="เลือกช่วงเวลาครึ่งวัน",
        default=False
    )

    show_approval_button = fields.Boolean(
        string='แสดงปุ่มอนุมัติ',
        compute='_check_approval_id',
        default=False,
        store=True
    )
    show_in_overview_calendar = fields.Boolean(
        string='แสดงในปฏิทินการลา',
        compute='_check_in_overview_calendar',
        default=False,
        store=True
    )
    show_cancel_button = fields.Boolean(
        string='แสดงปุ่มยกเลิก',
        compute='_check_requester_id',
        default=False,
        store=True
    )
    show_half_day_selection = fields.Boolean(
        string='แสดงตัวเลือกครึ่งวัน',
        default=False,
        store=True
    )

    employee_quota = fields.One2many(
        "leave_setting_employee_lines",
        "hr_employee_id",
        default= lambda self: self._get_employee_quota(),
        store=False
    )

    @api.onchange('request_type_id', 'request_approval_id')
    def _change_approver(self):
        for rec in self:
            request_type = self.env['leave_request_types'].browse(rec.request_type_id.id)
            if request_type['is_primary_approval']:
                employee = self.env['hr.employee'].browse(self._get_employee_id())
                parent = self.env['hr.employee'].browse(employee['parent_id'])
                if parent:
                    self._get_all_state()
                    rec.request_approval_id = parent['id']
            else:
                if request_type['request_type_approval_id']:
                    rec.request_approval_id = request_type['request_type_approval_id']

    @api.depends('request_approval_id')
    def _check_approval_id(self):
        for rec in self:
            if rec.request_approval_id.user_id.id == self._uid:
                rec.show_approval_button = True

    @api.depends('requester_id')
    def _check_requester_id(self):
        for rec in self:
            if rec.requester_id.user_id.id == self._uid \
            or (self.env.user.has_group('depa_hr_leave.group_user_depa_leave_setting') and rec.request_approval_id.user_id.id != self._uid):
                rec.show_cancel_button = True

    @api.depends('requester_department_id')
    def _check_in_overview_calendar(self):
        for rec in self:
            if rec.requester_department_id == rec._get_employee_info().department_id:
                rec.show_in_overview_calendar = True

    def _calculate_leave_days(self, date_from, date_to):
        for rec in self:
            if rec.is_not_full_day:
                return 0.5
            else:
                holidays = self._get_public_holidays()
                if (date_from.date() == date_to.date() and date_from.date().weekday() in [5,6])\
                or (relativedelta(date_to.date(), date_from.date()) == 1 and date_from.date().weekday() in [5,6] and date_to.date().weekday() in [5,6]):
                    if holidays:
                        if date_from.date() in holidays:
                            return 0
                    return 0
                elif relativedelta(date_to.date(), date_from.date()).days <= 0:
                    rec.request_date_to = rec.request_date_from
                    rec.date_to = rec.date_from = datetime.combine(rec.request_date_from, datetime.min.time())
                    return 1
                employee = self.env['hr.employee'].browse(self._get_employee_id())
                # date_from_calculate = datetime.combine(date_from, datetime.min.time())
                # date_to_calculate = datetime.combine(date_to, datetime.max.time())
                delta = employee.get_work_days_data(date_from, date_to)['days']
                if holidays:
                    for holiday in holidays:
                        if date_from.date() <= holiday <= date_to.date() and delta > 0:
                            delta = delta - 1
                if date_to.date().weekday() in [5,6]:
                    return delta
                return delta + 1

    @api.onchange('is_not_full_day','request_date_from','request_date_to')
    def _date_change_listener(self):
        for rec in self:
            if rec.is_not_full_day:
                rec.show_half_day_selection = True
                rec.request_date_to = rec.request_date_from
            else:
                rec.show_half_day_selection = False
                rec.half_day_selection = False
            rec.date_from = datetime.combine(rec.request_date_from, datetime.min.time())
            rec.date_to = datetime.combine(rec.request_date_to, datetime.min.time())

    @api.depends('date_from','date_to')
    def _compute_request_days(self):
        for rec in self:
            rec.request_date_from = rec.date_from.date()
            rec.request_date_to = rec.date_to.date()
            # self.request_days = self._calculate_leave_days(date_from=self.request_date_from, date_to=self.request_date_to)
            rec.request_days = self._calculate_leave_days(date_from=rec.date_from, date_to=rec.date_to)

    @api.multi
    def unlink(self):
        for leave in self.filtered(lambda self: self.state not in ['draft', 'reject', 'cancel']):
            if not self.env.user.has_group('depa_hr_leave.delete_leave_request_depa_leave_setting'):
                raise UserError(_('ไม่สามารถลบคำขออนุมัติการลาที่อยู่ในสถานะ %s ได้') % (leave.state_id.name,))
        return super(leave_request, self).unlink()

    def send_email(self, id, action):
        web_base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = str(self.env.ref('depa_hr_leave.leave_request_approve_action_window').id)
        
        if action == "send":
            email_to = self.request_approval_id.user_id.partner_id.email
            message_body =  '<p> เรียน ' + self.request_approval_id.name + '</p>' + \
                            '<p> ได้รับคำขออนุมัติการลาจาก ' + self.requester_id.name + '</p>' + \
                            '<p> ประเภทการลา : ' + self.request_type_id.name + '</p>' + \
                            '<p> จากวันที่ : ' + str(self.request_date_from) + '</p>' + \
                            '<p> ถึงวันที่  : ' + str(self.request_date_to) + '</p>' + \
                            '<p> เป็นระยะเวลา : ' + str(self.request_days) + ' วัน </p>' + \
                            '<p> รายละเอียด : ' + self.request_desc + '</p><br/><br/>' + \
                            '<a href='+ web_base +'web#id='+ str(id)+'&model=leave_request&action='+ action_id +'&view_type=form>คำขออนุมัติ</a>'
            subject = 'ได้รับคำขออนุมัติการลา (odoo)'
        elif action == "approve":
            email_to = self.requester_id.user_id.partner_id.email
            message_body =  '<p> เรียน ' + self.requester_id.name + '</p>' + \
                            '<p> คำขอการลาของคุณได้รับการอนุมัติแล้ว </p><br/><br/>' + \
                            '<p> ประเภทการลา : ' + self.request_type_id.name + '</p>' + \
                            '<p> จากวันที่ : ' + str(self.request_date_from) + '</p>' + \
                            '<p> ถึงวันที่  : ' + str(self.request_date_to) + '</p>' + \
                            '<p> ตรวจสอบได้ที่ <a href='+ web_base +'web#id='+ str(id)+'&model=leave_request&action='+ action_id +'&view_type=form>คำขออนุมัติ</a> </p>'
            subject = 'คำขอการลาได้รับการอนุมัติแล้ว'
        elif action == "reject":
            email_to = self.requester_id.user_id.partner_id.email
            message_body =  '<p> เรียน ' + self.requester_id.name + '</p>' + \
                            '<p> คำขอการลาของคุณถูกปฏิเสธ </p><br/><br/>' + \
                            '<p> ประเภทการลา : ' + self.request_type_id.name + '</p>' + \
                            '<p> จากวันที่ : ' + str(self.request_date_from) + '</p>' + \
                            '<p> ถึงวันที่  : ' + str(self.request_date_to) + '</p>' + \
                            '<p> ตรวจสอบได้ที่ <a href='+ web_base +'web#id='+ str(id)+'&model=leave_request&action='+ action_id +'&view_type=form>คำขออนุมัติ</a> </p>'
            subject = 'คำขอการลาถูกปฏิเสธ'
        template_obj = request.env['mail.mail']
        template_data = {
            'subject': subject,
            'body_html': message_body,
            'email_from': request.env.user.company_id.email,
            'email_to': email_to
        }
        template_id = template_obj.create(template_data)
        template_id.send()

    # button functions
    def send_leave_request(self):
        if self.state == 'draft':
            if self.request_days <= 0:
                raise ValidationError(_("จำนวนวันลาต้องมากกว่าหรือเท่ากับ 0.5 วัน"))
            # check both request_type and approver are selected
            if self.request_type_id and self.request_approval_id:
                self.ensure_one()
                self._check_quota_sending()
                self.update({
                    'state': 'sent',
                    'state_id': self._get_state_id(state='sent')
                })
                self.send_email(id=self.id, action="send")
                self.message_post(
                    body="ส่งคำขออนุมัติการลาไปยัง "+ self.request_approval_id.name
                )
            else:
                raise ValidationError(_("กรุณาเลือกประเภทการลาและผู้อนุมัติการลาให้ครบถ้วนและถูกต้อง"))

    def approve_leave_request(self):
        if self.request_approval_id.id == self._get_employee_id():
            self._subtract_quota_approving()
            self.update({
                'state': 'done',
                'state_id': self._get_state_id(state='done')
            })
            self.send_email(id=self.id, action="approve")
            self.message_post(
                body="อนุมัติคำขอโดย " + self.request_approval_id.name
            )
        else:
            raise ValidationError(_("ต้องเป็นผู้อนุมัติเท่านั้น"))

    def reject_leave_request(self):
        if self.request_approval_id.id == self._get_employee_id():
            self.update({
                'state': 'reject',
                'state_id': self._get_state_id(state='reject')
            })
            self.send_email(id=self.id, action="reject")
            self.message_post(
                body="ปฏิเสธคำขอโดย " + self.request_approval_id.name
            )
        else:
            raise ValidationError(_("ต้องเป็นผู้อนุมัติเท่านั้น"))


    def cancel_leave_request(self):
        if self.env.user.has_group('depa_hr_leave.group_user_depa_leave_setting') or self.requester_id.user_id.id == self._uid:
            self.update({
                'state': 'cancel',
                'state_id': self._get_state_id(state='cancel')
            })
            self.message_post(
                body="ยกเลิกคำขอโดย " + self._get_employee_info().name
            )
        else:
            raise ValidationError(_("ต้องมีสิทธิ์ในการตั้งค่าการลาเท่านั้น หรือเป็นผู้ขออนุมัติเท่านั้น"))

    def cancel_approved_leave_request(self):
        if self.env.user.has_group('depa_hr_leave.group_user_depa_leave_setting'):
            quota = self._get_employee_quota_for_approver()
            request_days = self.request_days
            type_en_name = self.request_type_id.en_name
            quota_days = quota[type_en_name]
            return_days = int(quota_days)+int(request_days)

            quota.update({
                type_en_name: return_days
            })

            self.update({
                'state': 'cancel',
                'state_id': self._get_state_id(state='cancel')
            })
            self.message_post(
                body="ยกเลิกคำขอที่อนุมัติแล้วโดย " + self._get_employee_info().name
            )
        else:
            raise ValidationError(_("ต้องมีสิทธิ์ในการตั้งค่าการลาเท่านั้น หรือเป็นผู้ขออนุมัติเท่านั้น"))

