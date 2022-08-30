# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
import base64

from odoo import api, fields, models
from odoo import tools, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource


class user_profile(models.Model):
    _name = 'user_profile'

    def _default_employee_id(self):
        employee_obj = self.env['hr.employee'].search([
            ('user_id', '=', self._uid)
        ])
        return employee_obj

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    def _get_my_point(self):
        employee_point = self.env['depa_welfare_hr_lines'].search([
            ('employee_id', '=', self._default_employee_id().id),
            ('hr_employee_id.year', '=', self._default_fiscal_year())
        ], limit=1)

        if employee_point:
            return employee_point.point

    def _get_parent(self, relationship, field):
        parent = self.env['user_relative'].search([
            ('employee_id', '=', self._default_employee_id().id),
            ('relationship', '=', relationship)
        ])
        if parent:
            if field == 'name':
                return parent.name
            elif field == 'birthday':
                return parent.birthday
            elif field == 'age':
                age = relativedelta(date.today(), parent.birthday).years
                return age

    def _get_children(self):
        child = self.env['user_relative'].search([
            ('employee_id', '=', self._default_employee_id().id),
            ('relationship', '=', 'children')
        ])
        if child:
            return child

    # Personal Information
    current_point = fields.Float(
        default=lambda self: self._get_my_point(),
        readonly=True
    )
    current_amount = fields.Float(
        compute="_compute_current_amount",
        store=True,
        readonly=True
    )
    image = fields.Binary(
        default=lambda self: self._default_employee_id().image,
        attachment=True
    )
    name = fields.Char(
        default=lambda self: self._default_employee_id().name,
        readonly=True
    )
    emp_code = fields.Char(
        default=lambda self: self._default_employee_id().emp_code,
        readonly=True
    )
    # Contact Information
    email = fields.Char(
        default=lambda self: self._default_employee_id().work_email,
        readonly=True
    )
    phone = fields.Char(
        default=lambda self: self._default_employee_id().mobile_phone,
        readonly=True
    )
    address_home_id = fields.Many2one(
        'res.partner',
        'Private Address',
        default=lambda self: self._default_employee_id().address_home_id,
        readonly=True)
    emergency_contact = fields.Char(
        "Emergency Contact",
        default=lambda self: self._default_employee_id().emergency_contact,
        readonly=True
    )
    emergency_phone = fields.Char(
        "Emergency Phone",
        default=lambda self: self._default_employee_id().emergency_phone,
        readonly=True
    )
    # Position
    department_id = fields.Many2one(
        'hr.department',
        'Department',
        default=lambda self: self._default_employee_id().department_id,
        readonly=True
    )
    job_id = fields.Many2one(
        'hr.job',
        'Job Position',
        default=lambda self: self._default_employee_id().job_id,
        readonly=True
    )
    job_title = fields.Char(
        "Job Title",
        default=lambda self: self._default_employee_id().job_title,
        readonly=True
    )
    parent_id = fields.Many2one(
        'hr.employee',
        'Manager',
        default=lambda self: self._default_employee_id().parent_id,
        readonly=True
    )
    # Status
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], default=lambda self: self._default_employee_id().gender,
        readonly=True
    )
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], default=lambda self: self._default_employee_id().marital,
        string="Marital Status",
        readonly=True
    )
    spouse_complete_name = fields.Char(
        'Spouse Complete Name',
        default=lambda self: self._default_employee_id().spouse_complete_name,
        readonly=True
    )
    spouse_birthdate = fields.Date(
        'Spouse Birthdate',
        default=lambda self: self._default_employee_id().spouse_birthdate,
        readonly=True
    )
    children = fields.Integer(
        'Number of Children',
        default=lambda self: self._default_employee_id().children,
        readonly=True
    )
    # Birth
    identification_id = fields.Char(
        'เลขประจำตัวประชาชน',
        default=lambda self: self._default_employee_id().identification_id,
        readonly=True
    )
    birthday = fields.Date(
        'วัน/เดือน/ปีเกิด',
        default=lambda self: self._default_employee_id().birthday,
        readonly=True
    )
    age = fields.Char(
        'อายุ',
        compute='_compute_age'
    )
    # Education
    certificate = fields.Selection([
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('other', 'Other'),
    ], 'Certificate Level',
        default=lambda self: self._default_employee_id().certificate,
        readonly=True
    )
    study_field = fields.Char(
        "Field of Study",
        default=lambda self: self._default_employee_id().study_field,
        readonly=True
    )
    study_school = fields.Char(
        "School",
        default=lambda self: self._default_employee_id().study_school,
        readonly=True
    )
    # Parent
    father_name = fields.Char(
        'Father\'s Name',
        default=lambda self: self._get_parent('father', 'name'),
        readonly=True
    )
    father_birthday = fields.Date(
        default=lambda self: self._get_parent('father', 'birthday')
    )
    father_age = fields.Char(
        'Father\'s Age',
        # compute='_compute_father_age'
        default=lambda self: self._get_parent('father', 'age'),
        readonly=True
    )
    mother_name = fields.Char(
        'Mother\'s Name',
        default=lambda self: self._get_parent('mother', 'name'),
        readonly=True
    )
    mother_birthday = fields.Date(
        default=lambda self: self._get_parent('mother', 'birthday')
    )
    mother_age = fields.Char(
        'Mother\'s Age',
        default=lambda self: self._get_parent('mother', 'age'),
        readonly=True
    )

    # Point Usage
    point_history_lines_ids = fields.One2many(
        "point_history_lines",
        "point_history_lines_id",
        string="ประวัติการใช้คะแนน",
        # readonly=True
    )

    employee_relative_lines_ids = fields.One2many(
        "employee_relative_lines",
        "employee_relative_lines_id",
        string="ญาติ"
    )

    hr_relative_lines_ids = fields.Many2many(
        'hr.employee.relative',
        'depa_welfare_basic_hr_relative_lines_rel',
        'depa_welfare_basic_id',
        'hr_relative_lines_id',
        string="ญาติ"
    )

    years = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        string="ปีงบประมาณ",
        default=lambda self: self._default_fiscal_year(),
        # required=True
    )

    @api.depends('current_point')
    def _compute_current_amount(self):
        self.current_amount = round(self.current_point, 2) * 105

    @api.depends('birthday')
    def _compute_age(self):
        try:
            self.age = str(self.get_age_from_dob(self.birthday))
        except:
            self.age = ''

    @api.onchange('years')
    def _onchange_years(self):
        year = self.years.id
        # specific_date = date(year - 1, 12, 31).strftime("%Y-%m-%d %I:%M:%S")
        # fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
        #     ('date_start', '<=', specific_date),
        #     ('date_end', '>=', specific_date),
        #     ('fiscal_year', '=', str(year))
        # ], limit=1)
        # year_model = self.env['depa_welfare_rounds'].search([
        #     (),
        # ], limit=1)
        # start_date = date(year, 1, 1).strftime("%Y-%m-%d %I:%M:%S")
        # end_date = date(year+1, 1, 1).strftime("%Y-%m-%d %I:%M:%S")
        point_history_lines = self.env['point_history_lines'].search([
            ('employee_id', '=', self._default_employee_id().id),
            # ('on_date', '>=', start_date),
            # ('on_date', '<', end_date),
            # ('welfare_fiscal_year', '=', fiscal_year_obj.id),
            ('welfare_fiscal_year', '=', year),
        ])
        history_lines = []
        current_point = 0
        if point_history_lines:
            # current_point = point_history_lines[-1].point_balance
            current_point = point_history_lines[0].point_balance
            for i, rec in enumerate(point_history_lines):  # Add default approval flow
                history_lines.append(
                    (
                        0,
                        0,
                        {
                            'point_history_lines_id': rec.id,
                            'desc': rec.desc,
                            'on_date': rec.on_date,
                            'point_type': rec.point_type,
                            'point_usage': rec.point_usage,
                            'point_balance': rec.point_balance,
                            'depa_welfare_id': rec.depa_welfare_id.id,
                            'wel_doc_no': rec.wel_doc_no
                        }
                    )
                )
        self.update({'point_history_lines_ids': [(5,)]})
        self.update({
            'current_point': current_point,
            'point_history_lines_ids': history_lines
        })

    def get_age_from_dob(self, dob):
        age = relativedelta(date.today(), dob)
        return f"{age.years} ปี {age.months} เดือน {age.days} วัน"

    @api.model
    def default_get(self, fields_list):
        res = super(user_profile, self).default_get(fields_list)
        relative_obj = self.env['hr.employee.relative'].search([
            ('employee_id', '=', self._default_employee_id().id),
        ])
        values = []
        relatives = [(6, 0, relative_obj.ids)]
        for emp in relative_obj:
            values.append([
                0,
                0,
                {
                    'title': emp.title_name.name,
                    'name': emp.name,
                    'relation': emp.relation,
                    'identify_number': emp.identify_number,
                    'date_of_birth': emp.date_of_birth,
                    'age': self.get_age_from_dob(emp.date_of_birth),
                    'gender': emp.gender,
                    'phone_number': emp.phone_number
                }])
        res.update({
            'employee_relative_lines_ids': values,
            'hr_relative_lines_ids': relatives
        })
        return res


class employee_relative_lines(models.Model):
    _name = 'employee_relative_lines'

    title = fields.Char(
        string="คำนำหน้า"
    )
    name = fields.Char(
        string="ชื่อ-สกุล"
    )
    relation = fields.Selection(
        string="ความสัมพันธ์",
        selection=[
            ('MO', 'มารดา'),
            ('FA', 'บิดา'),
            ('SP', 'คู่สมรส'),
            ('CH', 'บุตร'),
        ],
    )
    identify_number = fields.Char(
        string='เลขประจำตัวประชาชน'
    )
    date_of_birth = fields.Date(
        string='วัน/เดือน/ปีเกิด',
    )
    age = fields.Char(
        string="อายุ",
        compute='_compute_age',
    )
    gender = fields.Selection(
        string='เพศ',
        selection=[
            ('male', 'ชาย'),
            ('female', 'หญิง'),
        ]
    )
    phone_number = fields.Char(
        string='เบอร์โทรศัพท์'
    )
    employee_relative_lines_id = fields.Many2one(
        'user_profile'
    )
