from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

FH_SELECTION = [("full", "เต็มสิทธิ์"), ("half", "หักแต้มครึ่งหนึ่ง")]
FAMILY_RELATIONS = [
    ('children', 'บุตร'),
    ('father', 'บิดา'),
    ('mother', 'มารดา')
]
class depa_welfare_lines(models.Model):
    _name = 'depa_welfare_lines'

    def _getTypesByDept(self):
        domain = False
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)

        # Check user is gbdi
        if employee.department_id.is_gbdi:
            domain = [('is_depa_only', '!=', True)]
        else:
            domain = []

        return domain

    def _get_employee_info(self):
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ])
        return employee

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        # print(fiscal_year_obj)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    welfare_types_id = fields.Many2one(
        "depa_welfare_types",
        string="รายการสวัสดิการ",
        required=True,
        domain=_getTypesByDept
    )
    actual_amount = fields.Float(
        default=1,
        string="จำนวนเงินที่เบิก",
        required=True
    )
    actual_amount_hidden = fields.Float(
        default=1,
        string="จำนวนเงินที่เบิก hidden",
        required=True
    )
    receipt_amount = fields.Float(
        string="Receipt Amount"
    )
    receipt_date = fields.Date(
        string="วันที่บนใบเสร็จ",
        # default=date.today(),
        required=True
    )
    point_amount = fields.Float(
        string="คะแนนที่ใช้",
        compute="_point_cal",
        store=True,
        readonly=True,
        digits = (10, 2)
    )
    is_full_half = fields.Boolean(
        default=False
    )
    full_half_selection = fields.Selection(
        FH_SELECTION,
        'Full Or Half'
    )
    is_family = fields.Boolean()
    family_name = fields.Char(
        string="Family name"
    )
    family_relation = fields.Selection(
        FAMILY_RELATIONS,
        'Family Relation'
    )
    employee_relation_ids = fields.Many2many(
        "hr.employee.relative",
        "employee_relative_welfare_lines_rel",
        "welfare_lines_id",
        "employee_relative_id",
        string="บุคคลในครอบครัว",
        required=True,
        copy=True
    )
    depa_welfare_lines_id = fields.Many2one(
        'depa_welfare'
    )
    receipt_attachment_ids = fields.Many2many(
        "ir.attachment",
        "depa_welfare_lines_attachment_rel",
        "depa_welfare_lines_id",
        "ir_attachment_id",
        string="แนบใบเสร็จ",
    )
    depa_welfare_type_lines_ids = fields.Many2many(
        "depa_welfare_type_lines",
        "depa_welfare_type_lines_rel",
        "depa_welfare_lines_id",
        "depa_welfare_type_lines_id",
        string="ระบุ (เพิ่มเติม)",
        required=True,
        copy=True
    )
    memo_for_adjustment = fields.Text(
        string="หมายเหตุ (รายการแก้ไข)"
    )
    is_hr_reject = fields.Boolean(
        string="รายการแก้ไข",
        default=False
    )
    show_approve_button = fields.Boolean(
        compute="_get_show_approve_button",
    )
    current_state = fields.Char(
        compute="_get_current_state",
    )

    def setReceiptDate(self, new_date):
        self.receipt_date = new_date

    @api.depends('actual_amount')
    def _point_cal(self):
        for line in self:
            if line.actual_amount > 0 :
                if line.welfare_types_id.is_half_full:
                    line.point_amount = (float(line.actual_amount) / line.welfare_types_id.full_multiply) / 105
                    line.actual_amount_hidden = (float(line.actual_amount) / line.welfare_types_id.full_multiply)
                else:
                    line.point_amount = float(line.actual_amount) / 105
                    line.actual_amount_hidden = float(line.actual_amount)

                # if line.full_half_selection :
                #     if line.full_half_selection == "full" :
                #         line.point_amount = (float(line.actual_amount) / line.welfare_types_id.full_multiply) / 105
                #     else:
                #         line.point_amount = (float(line.actual_amount) / line.welfare_types_id.half_multiply) / 105
                # else:
                #     line.point_amount = float(line.actual_amount) / 105
            else:
                line.point_amount = 0

    @api.depends('depa_welfare_lines_id')
    def _get_current_state(self):
        for rec in self:
            rec.current_state = rec.depa_welfare_lines_id.state

    @api.depends('depa_welfare_lines_id')
    def _get_show_approve_button(self):
        for rec in self:
            rec.show_approve_button = rec.depa_welfare_lines_id.show_button_make_approval

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(depa_welfare_lines, self).default_get(fields_list)
    #     return res

    @api.onchange('actual_amount')
    def _check_actual_amount(self):
        if self.actual_amount <= 0:
            self.actual_amount = 1
            return {
                'warning': {
                    'title': 'แจ้งเตือนผู้ใช้งาน',
                    'message': 'จำเป็นต้องระบุจำนวนเงินลงในแบบฟอร์มการเบิก'}
            }
        # Point Limit
        if self.welfare_types_id.limit_point > 0:
            point_limit = self.welfare_types_id.limit_point
            if self.point_amount > point_limit:
                self.actual_amount = 1
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้คะแนนเกิน ' + str(point_limit) + ' คะแนน'}
                }
            else:
                #check quota limit
                welfares = self.env['depa_welfare'].search([
                    ('employee_id', '=', self._get_employee_info().id),
                    ('welfare_fiscal_year', '=', self._default_fiscal_year()),
                    ('state', '=', 'completed'),
                ])
                if welfares:
                    welfare_lines = self.env['depa_welfare_lines'].search([
                        ('depa_welfare_lines_id', 'in', welfares.ids),
                        ('welfare_types_id', '=', self.welfare_types_id.id)
                    ])
                    if welfare_lines:
                        sum_point = 0
                        for line in welfare_lines:
                            sum_point += line.point_amount

                        if (self.point_amount + sum_point) > point_limit:
                            self.actual_amount = 1
                            return {
                                'warning': {
                                    'title': 'แจ้งเตือนผู้ใช้งาน',
                                    'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้คะแนนเกิน %s คะแนน ซึ่งคุณได้ใช้สวัสดิการนี้ไปแล้ว %s คะแนน สามารถใช้ได้อีกไม่เกิน %s คะแนน' % (str(point_limit), "{:,.2f}".format(sum_point), "{:,.2f}".format((point_limit - sum_point)))
                                }
                            }
        # Amount Limit
        if self.welfare_types_id.limit_amount > 0:
            amount_limit = self.welfare_types_id.limit_amount
            if self.actual_amount > amount_limit:
                self.actual_amount = 1
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้จำนวนเงินเกิน %s บาท' % "{:,.2f}".format(amount_limit)}
                }
            else:
                #check quota limit
                welfares = self.env['depa_welfare'].search([
                    ('employee_id', '=', self._get_employee_info().id),
                    ('welfare_fiscal_year', '=', self._default_fiscal_year()),
                    ('state', '=', 'completed'),
                ])
                if welfares:
                    welfare_lines = self.env['depa_welfare_lines'].search([
                        ('depa_welfare_lines_id', 'in', welfares.ids),
                        ('welfare_types_id', '=', self.welfare_types_id.id)
                    ])
                    if welfare_lines:
                        sum_amount = 0
                        for line in welfare_lines:
                            sum_amount += line.actual_amount

                        if (self.actual_amount + sum_amount) > amount_limit:
                            self.actual_amount = 1
                            return {
                                'warning': {
                                    'title': 'แจ้งเตือนผู้ใช้งาน',
                                    'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้จำนวนเงินเกิน %s บาท ซึ่งคุณได้ใช้สวัสดิการนี้ไปแล้ว %s บาท สามารถใช้ได้อีกไม่เกิน %s บาท' % ("{:,.2f}".format(amount_limit), "{:,.2f}".format(sum_amount), "{:,.2f}".format((amount_limit - sum_amount)))}
                            }
        # check full_multiply
        if self.welfare_types_id.full_multiply > 0:
            full_multiply = self.welfare_types_id.full_multiply
            amount_can_used = self.depa_welfare_lines_id.amount_remain * full_multiply
            if self.actual_amount > amount_can_used:
                self.actual_amount = amount_can_used
                if amount_can_used <= 0:
                    amount_can_used = 0
                    self.actual_amount = False
                    self.welfare_types_id = False
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ สนง. สมทบให้ %s เท่า ซึ่งคุณสามารถระบุจำนวนเงินในรายการนี้ได้ไม่เกิน %s บาท' % (
                        "{:,.2f}".format(full_multiply), "{:,.2f}".format((amount_can_used)))}
                }

    @api.onchange('welfare_types_id')
    def _welfare_types_id_change(self):
        self.is_family = self.welfare_types_id.for_family
        self.is_full_half = self.welfare_types_id.is_half_full
        self.depa_welfare_type_lines_ids = [(5, 0, 0)]
        self.employee_relation_ids = [(5, 0, 0)]

        if self.welfare_types_id.is_half_full:
            self.point_amount = (float(self.actual_amount) / self.welfare_types_id.full_multiply) / 105
            self.actual_amount_hidden = (float(self.actual_amount) / self.welfare_types_id.full_multiply)
        else:
            self.point_amount = float(self.actual_amount) / 105
            self.actual_amount_hidden = float(self.actual_amount)

        # Point Limit
        if self.welfare_types_id.limit_point > 0:
            point_limit = self.welfare_types_id.limit_point
            if self.point_amount > point_limit:
                self.actual_amount = 1
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้คะแนนเกิน '+ str(point_limit) +' คะแนน'}
                }
            else:
                #check quota limit
                welfares = self.env['depa_welfare'].search([
                    ('employee_id', '=', self._get_employee_info().id),
                    ('welfare_fiscal_year', '=', self._default_fiscal_year()),
                    ('state', '=', 'completed'),
                ])
                if welfares:
                    welfare_lines = self.env['depa_welfare_lines'].search([
                        ('depa_welfare_lines_id', 'in', welfares.ids),
                        ('welfare_types_id', '=', self.welfare_types_id.id)
                    ])
                    if welfare_lines:
                        sum_point = 0
                        for line in welfare_lines:
                            sum_point += line.point_amount

                        if (self.point_amount + sum_point) > point_limit:
                            self.actual_amount = 1
                            return {
                                'warning': {
                                    'title': 'แจ้งเตือนผู้ใช้งาน',
                                    'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้คะแนนเกิน %s คะแนน ซึ่งคุณได้ใช้สวัสดิการนี้ไปแล้ว %s คะแนน สามารถใช้ได้อีกไม่เกิน %s คะแนน' % (str(point_limit), "{:,.2f}".format(sum_point), "{:,.2f}".format((point_limit - sum_point)))
                                }
                            }
                        # print(point_amount)

        # Amount Limit
        if self.welfare_types_id.limit_amount > 0:
            amount_limit = self.welfare_types_id.limit_amount
            if self.actual_amount > amount_limit:
                self.actual_amount = 1
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้จำนวนเงินเกิน %s บาท' % "{:,.2f}".format(amount_limit)}
                }
            else:
                #check quota limit
                welfares = self.env['depa_welfare'].search([
                    ('employee_id', '=', self._get_employee_info().id),
                    ('welfare_fiscal_year', '=', self._default_fiscal_year()),
                    ('state', '=', 'completed'),
                ])
                if welfares:
                    welfare_lines = self.env['depa_welfare_lines'].search([
                        ('depa_welfare_lines_id', 'in', welfares.ids),
                        ('welfare_types_id', '=', self.welfare_types_id.id)
                    ])
                    if welfare_lines:
                        sum_amount = 0
                        for line in welfare_lines:
                            sum_amount += line.actual_amount

                        if (self.actual_amount + sum_amount) > amount_limit:
                            self.actual_amount = 1
                            return {
                                'warning': {
                                    'title': 'แจ้งเตือนผู้ใช้งาน',
                                    'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้จำนวนเงินเกิน %s บาท ซึ่งคุณได้ใช้สวัสดิการนี้ไปแล้ว %s บาท สามารถใช้ได้อีกไม่เกิน %s บาท' % ("{:,.2f}".format(amount_limit), "{:,.2f}".format(sum_amount), "{:,.2f}".format((amount_limit - sum_amount)))}
                            }
                        # print(sum_amount)
        # check full_multiply
        if self.welfare_types_id.full_multiply > 0:
            full_multiply = self.welfare_types_id.full_multiply
            amount_can_used = self.depa_welfare_lines_id.amount_remain * full_multiply
            if self.actual_amount > amount_can_used:
                self.actual_amount = amount_can_used
                if amount_can_used <= 0:
                    amount_can_used = 0
                    self.actual_amount = False
                    self.welfare_types_id = False
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ สนง. สมทบให้ %s เท่า ซึ่งคุณสามารถระบุจำนวนเงินในรายการนี้ได้ไม่เกิน %s บาท' % (
                            "{:,.2f}".format(full_multiply), "{:,.2f}".format((amount_can_used)))}
                }

        if self.welfare_types_id.for_family:
            domain = [('employee_id.user_id', '=', self.env.uid)]
            relation = self.welfare_types_id.family_relation
            relate_domain = ('relation', 'in', [relation])
            if relation == 'FA-MO':
                relate_domain = ('relation', 'in', ['FA', 'MO'])
            domain.append(relate_domain)
            if self.welfare_types_id.family_age:
                age_from = self.welfare_types_id.family_age_from
                age_to = self.welfare_types_id.family_age_to
                domain.append(('age_now', '>=', age_from))
                domain.append(('age_now', '<=', age_to))

            emp_relative = self.env['hr.employee.relative'].search(domain)
            if not emp_relative:
                raise ValidationError(_("ไม่พบบุคคลในครอบครัวที่สามารถใช้สวัสดิการนี้ได้"))

            return {'domain': {'employee_relation_ids': domain}}
        # if self.welfare_types_id:
        #     # type_lines = [type_line.id for type_line in self.welfare_types_id.depa_welfare_type_lines_ids]
        #     type_lines = self.welfare_types_id.depa_welfare_type_lines_ids.ids
        #     self.depa_welfare_type_lines_ids = [(6, 0, type_lines)]

    @api.onchange('full_half_selection')
    def _full_half_selection_change(self):
        if self.actual_amount != 0 :
            if self.full_half_selection == "full" :
                self.point_amount = (float(self.actual_amount) / self.welfare_types_id.full_multiply) / 105
            else:
                self.point_amount = (float(self.actual_amount) / self.welfare_types_id.half_multiply) / 105
        else:
            self.point_amount = 0

    @api.constrains('receipt_attachment_ids')
    def _receipt_attachment_ctr(self):
        for line in self:
            if len(line.receipt_attachment_ids) <= 0:
                raise ValidationError(_("กรุณาแนบไฟล์ใบเสร็จรับเงินหรือใบกำกับภาษี"))

    @api.onchange('receipt_date')
    def _receipt_date_change(self):
        if self.receipt_date:
            date_diff = (self.receipt_date - date.today()).days
            print(date_diff)
            if (date_diff < -90):
                self.receipt_date = date.today()
                # raise ValidationError(_("วันที่ในใบเสร็จรับเงินหรือใบกำกับภาษีเกิน 90 วัน"))
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ใบเสร็จรับเงินหรือใบกำกับภาษีมีวันที่เกิน 90 วัน\r\nกรุณาเขียนบันทึกถึงผู้อำนวยการเพื่อขออนุมัติ'}
                }

    @api.onchange('point_amount')
    def _point_amount_change(self):
        # print(self)
        if self.welfare_types_id.limit_point > 0:
            point_limit = self.welfare_types_id.limit_point
            if self.point_amount > point_limit:
                self.actual_amount = 1
                return {
                    'warning': {
                        'title': 'แจ้งเตือนผู้ใช้งาน',
                        'message': 'ประเภทการเบิกสวัสดิการนี้ไม่สามารถใช้คะแนนเกิน '+ str(point_limit) +' คะแนน'}
                }

    def action_make_adjustment_wizard(self):
        # print(self)
        return {
            'name': "Make Adjustment Wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'depa_welfare_make_adjustment_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_welfare_line_id' : self.id,
                'default_current_state': self.current_state,
                # 'default_employee_id': employee_id.id,
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }

    def action_cancel_adjustment(self):
        # print(self)
        self.memo_for_adjustment = ""
        self.is_hr_reject = False

    @api.model
    def create(self, vals):
        res = super(depa_welfare_lines, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(depa_welfare_lines, self).write(vals)
        return res


class depa_welfare_lines_history(models.Model):
    _name = 'depa_welfare_lines_history'

    depa_welfare_lines_id = fields.Many2one(
        "depa_welfare_lines"
    )
    depa_welfare_lines_types_id = fields.Many2one(
        "depa_welfare_types"
    )
    actual_amount_history = fields.Float(
        string="Amount history"
    )
    point_amount_history = fields.Float(
        string="Point amount history"
    )
    receipt_date_history = fields.Date(
        string="Receipt date history"
    )
    state_history = fields.Char(
        string="State history"
    )
