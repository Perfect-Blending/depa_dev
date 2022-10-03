from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
DOC_STATE = (
                ('draft', 'ฉบับร่าง'),
                # ('sent', 'ส่งแล้ว'),
                ('evaluating', 'อยู่ระหว่างประเมิน'),
                ('done', 'เสร็จสมบูรณ์')
            )
MAX_TARGET = 5
class kpi_main(models.Model):
    _name = 'kpi_main'
    _inherit = ['mail.thread', 'mail.activity.mixin']

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
        if fiscal_year_obj:
            return fiscal_year_obj.id

    kpi_no = fields.Char(
        copy=False,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        default=lambda self: self._get_employee_info().id
    )
    emp_code = fields.Char(
        default=lambda self: self._get_employee_info().emp_code
    )
    emp_name = fields.Char(
        default=lambda self: self._get_employee_info().name
    )
    emp_type = fields.Selection(
        [
            ('operation', 'ปฏิบัติการ'),
            ('academic', 'วิชาการ'),
            ('management', 'บริหาร')
        ],
        default=lambda self: self._get_employee_info().employee_types,
        copy=False
    )
    emp_dept_name = fields.Char(
        default=lambda self: self._get_employee_info().department_id.name
    )
    is_emp_gbdi = fields.Boolean(
        default=lambda self: self._get_employee_info().department_id.is_gbdi
    )
    kpi_year = fields.Char(
        compute='_depends_kpi_year',
        store=True,
    )
    kpi_round = fields.Char(
        compute='_depends_kpi_round',
        store=True,
    )
    kpi_round_start = fields.Date(
        # readonly=True,
    )
    kpi_round_end = fields.Date(
        # readonly=True,
    )
    kpi_fiscal_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        # readonly=True,
    )
    corporate_lines_ids = fields.One2many(
        "kpi_corporate_lines",
        "corporate_lines_id",
        # required=True,
        copy=True
    )
    common_lines_ids = fields.One2many(
        "kpi_common_lines",
        "common_lines_id",
        # required=True,
        copy=True
    )
    function_lines_ids = fields.One2many(
        "kpi_function_lines",
        "function_lines_id",
        # required=True,
        copy=True
    )
    org_contribute_lines_ids = fields.One2many(
        "kpi_org_contribute_lines",
        "org_contribute_lines_id",
        copy=True
    )

    group_contribute_lines_ids = fields.One2many(
        "kpi_group_contribute_lines",
        "group_contribute_lines_id",
        copy=True
    )
    operate_behaviour_lines_ids = fields.One2many(
        "kpi_operate_behaviour_lines",
        "operate_behaviour_lines_id",
        copy=True
    )
    manage_behaviour_lines_ids = fields.One2many(
        "kpi_manage_behaviour_lines",
        "manage_behaviour_lines_id",
        copy=True
    )
    evaluate_line_ids = fields.One2many(
        "kpi_evaluate_lines",
        "evaluate_line_id",
        copy=True
    )
    routing_evaluate_id = fields.Many2one(
        'kpi_evaluate_setting',
        string='Evaluate routing',
        copy=True,
        domain="[ ('is_active', '=', True)]"
    )
    evaluate_count = fields.Integer(
        string="Evaluate Count",
        default=0,
        copy=False
    )
    state = fields.Selection(
        DOC_STATE,
        default='draft'
    )
    no_ce = fields.Html(
        string='no_create_edit',
        compute='_compute_no_ce_css',
        sanitize=False,
        store=False,
    )
    is_create = fields.Boolean(
        default=True
    )
    kpi_main_user_evaluating_ids = fields.Many2many(
        'res.users',
        'kpi_main_user_rel',
        'kpi_main_id',
        'user_id',
        string='users_evaluating',
        index=True,
    )
    kpi_evaluating_user = fields.Many2one(
        'res.users'
    )
    is_current_evaluator = fields.Boolean(
        default=False
    )
    total_score_corporate = fields.Float(
        string="Total Score",
        compute="_total_score_corporate",
        store=True,
        readonly=True
    )
    total_earn_corporate = fields.Float(
        string="Total Earn",
        compute="_total_earn_corporate",
        digits=(10, 8),
        store=True,
        readonly=True
    )
    total_weight_corporate = fields.Float(
        string="Total Weight",
        compute="_total_weight_corporate",
        digits=(10, 8),
        store=True,
        readonly=True
    )

    total_score_common = fields.Float(
        string="Total Score",
        compute="_total_score_common",
        store=True,
        readonly=True
    )
    total_earn_common = fields.Float(
        string="Total Earn",
        compute="_total_earn_common",
        digits=(10, 8),
        store=True,
        readonly=True
    )

    total_weight_common = fields.Float(
        string="Total Weight",
        compute="_total_weight_common",
        digits=(10, 8),
        store=True,
        readonly=True
    )

    total_score_function = fields.Float(
        string="Total Score",
        compute="_total_score_function",
        store=True,
        readonly=True
    )
    total_earn_function = fields.Float(
        string="Total Earn",
        compute="_total_earn_function",
        digits=(10, 8),
        store=True,
        readonly=True
    )

    total_weight_function = fields.Float(
        string="Total Weight",
        compute="_total_weight_function",
        digits=(10, 8),
        store=True,
        readonly=True
    )
    total_score_org_contribute = fields.Float(
        string="Total Score",
        compute="_total_score_org_contribute",
        store=True,
        readonly=True
    )
    total_score_group_contribute = fields.Float(
        string="Total Score",
        compute="_total_score_group_contribute",
        store=True,
        readonly=True
    )
    total_score_operate_behaviour = fields.Float(
        string="Total Score",
        compute="_total_score_operate_behaviour",
        store=True,
        readonly=True
    )
    total_earn_operate_behaviour = fields.Float(
        string="Total Earn",
        compute="_total_earn_operate_behaviour",
        digits=(10, 8),
        store=True,
        readonly=True
    )
    total_weight_operate_behaviour = fields.Float(
        string="Total Weight",
        compute="_total_weight_operate_behaviour",
        digits=(10, 8),
        store=True,
        readonly=True
    )

    total_score_manage_behaviour = fields.Float(
        string="Total Score",
        compute="_total_score_manage_behaviour",
        store=True,
        readonly=True
    )
    total_earn_manage_behaviour = fields.Float(
        string="Total Earn",
        compute="_total_earn_manage_behaviour",
        digits=(10, 8),
        store=True,
        readonly=True
    )
    total_weight_manage_behaviour = fields.Float(
        string="Total Weight",
        compute="_total_weight_manage_behaviour",
        digits=(10, 8),
        store=True,
        readonly=True
    )

    total_score_corporate_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_corporate_evaluate",
        store=False,
        readonly=True
    )
    total_earn_corporate_evaluate = fields.Float(
        string="Total Earn",
        compute="_total_earn_corporate_evaluate",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_score_common_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_common_evaluate",
        store=False,
        readonly=True
    )
    total_earn_common_evaluate = fields.Float(
        string="Total Earn",
        compute="_total_earn_common_evaluate",
        digits=(10, 8),
        store=False,
        readonly=True
    )

    total_score_function_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_function_evaluate",
        store=False,
        readonly=True
    )
    total_earn_function_evaluate = fields.Float(
        string="Total Earn",
        compute="_total_earn_function_evaluate",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_score_org_contribute_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_org_contribute_evaluate",
        store=False,
        readonly=True
    )
    total_score_group_contribute_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_group_contribute_evaluate",
        store=False,
        readonly=True
    )
    total_score_operate_behaviour_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_operate_behaviour_evaluate",
        store=True,
        readonly=True
    )
    total_earn_operate_behaviour_evaluate = fields.Float(
        string="Total Earn",
        compute="_total_earn_operate_behaviour_evaluate",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_score_manage_behaviour_evaluate = fields.Float(
        string="Total Score",
        compute="_total_score_manage_behaviour_evaluate",
        store=True,
        readonly=True
    )
    total_earn_manage_behaviour_evaluate = fields.Float(
        string="Total Earn",
        compute="_total_earn_manage_behaviour_evaluate",
        digits=(10, 8),
        store=False,
        readonly=True
    )

    total_earn_corporate_evaluate_all = fields.Float(
        string="Total Earn",
        compute="_total_earn_corporate_evaluate_all",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_earn_common_evaluate_all = fields.Float(
        string="Total Earn",
        compute="_total_earn_common_evaluate_all",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_earn_function_evaluate_all = fields.Float(
        string="Total Earn",
        compute="_total_earn_function_evaluate_all",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_earn_operate_behaviour_evaluate_all = fields.Float(
        string="Total Earn",
        compute="_total_earn_operate_behaviour_evaluate_all",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_earn_manage_behaviour_evaluate_all = fields.Float(
        string="Total Earn",
        compute="_total_earn_manage_behaviour_evaluate_all",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    total_score_org_contribute_evaluate_all = fields.Float(
        string="Total Score",
        compute="_total_score_org_contribute_evaluate_all",
        store=False,
        readonly=True
    )
    total_score_group_contribute_evaluate_all = fields.Float(
        string="Total Score",
        compute="_total_score_group_contribute_evaluate_all",
        store=False,
        readonly=True
    )
    sent_evaluate_at = fields.Datetime(
        string='sent evaluate time',
        copy=False
    )

    show_kpi_sent_button = fields.Boolean(
        string='show_kpi_sent_button',
        compute='_compute_show_kpi_sent_button',
        store=False,
    )
    corporate_summary = fields.Float(
        string="Corporate Summary",
        compute="_corporate_summary_compute",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    common_summary = fields.Float(
        string="Common Summary",
        compute="_common_summary_compute",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    function_summary = fields.Float(
        string="Function Summary",
        compute="_function_summary_compute",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    operate_behaviour_summary = fields.Float(
        string="Operate Summary",
        compute="_operate_behaviour_summary_compute",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    manage_behaviour_summary = fields.Float(
        string="Manage Summary",
        compute="_manage_behaviour_summary_compute",
        digits=(10, 8),
        store=False,
        readonly=True
    )
    kpi_grade = fields.Char(
        string="KPI Grade",
        default="-"
    )
    def name_get(self):
        return [(rec.id, str(rec.kpi_no)) for rec in self]

    @api.depends('total_earn_corporate_evaluate_all', 'total_weight_corporate')
    def _corporate_summary_compute(self):
        for rec in self:
            if MAX_TARGET > 0:
                rec.corporate_summary = rec.total_earn_corporate_evaluate_all / MAX_TARGET

    @api.depends('total_earn_common_evaluate_all', 'total_weight_common')
    def _common_summary_compute(self):
        for rec in self:
            if MAX_TARGET > 0:
                rec.common_summary = rec.total_earn_common_evaluate_all / MAX_TARGET

    @api.depends('total_earn_function_evaluate_all', 'total_weight_function')
    def _function_summary_compute(self):
        for rec in self:
            if MAX_TARGET > 0:
                rec.function_summary = rec.total_earn_function_evaluate_all / MAX_TARGET

    @api.depends('total_earn_operate_behaviour_evaluate_all', 'total_weight_operate_behaviour')
    def _operate_behaviour_summary_compute(self):
        for rec in self:
            if MAX_TARGET > 0:
                rec.operate_behaviour_summary = rec.total_earn_operate_behaviour_evaluate_all / MAX_TARGET

    @api.depends('total_earn_manage_behaviour_evaluate_all', 'total_weight_manage_behaviour')
    def _manage_behaviour_summary_compute(self):
        for rec in self:
            if MAX_TARGET > 0:
                rec.manage_behaviour_summary = rec.total_earn_manage_behaviour_evaluate_all / MAX_TARGET

    @api.depends('kpi_fiscal_year')
    def _depends_kpi_year(self):
        for rec in self:
            if rec.kpi_fiscal_year:
                rec.kpi_year = int(rec.kpi_fiscal_year.fiscal_year)

    @api.depends('kpi_fiscal_year')
    def _depends_kpi_round(self):
        for line in self:
            if line.kpi_fiscal_year:
                kpi_round_line_obj = line.env['kpi_round_setting_lines'].search([
                    ('kpi_round_setting_lines_id.fiscal_year_id', '=', line.kpi_fiscal_year.id),
                    ('kpi_start', '<=', date.today()),
                    ('kpi_end', '>=', date.today())
                ], limit=1)
                if kpi_round_line_obj:
                    line.kpi_round = kpi_round_line_obj.kpi_round
                    line.kpi_round_start = kpi_round_line_obj.kpi_start
                    line.kpi_round_end = kpi_round_line_obj.kpi_end

    @api.depends('corporate_lines_ids.kpi_point')
    def _total_score_corporate(self):
        for score in self:
            score_sum = 0
            for line in score.corporate_lines_ids:
                score_sum += line.kpi_point

            score.total_score_corporate = score_sum

    @api.depends('corporate_lines_ids.kpi_earn')
    def _total_earn_corporate(self):
        for earn in self:
            earn_sum = 0
            for line in earn.corporate_lines_ids:
                earn_sum += line.kpi_earn
            earn.total_earn_corporate = earn_sum

    @api.depends('corporate_lines_ids.kpi_weight')
    def _total_weight_corporate(self):
        for weight in self:
            weight_sum = 0
            for line in weight.corporate_lines_ids:
                weight_sum += line.kpi_weight
            weight.total_weight_corporate = weight_sum

    @api.depends('common_lines_ids.kpi_point')
    def _total_score_common(self):
        for score in self:
            score_sum = 0
            for line in score.common_lines_ids:
                score_sum += line.kpi_point
            score.total_score_common = score_sum

    @api.depends('common_lines_ids.kpi_earn')
    def _total_earn_common(self):
        for earn in self:
            earn_sum = 0
            for line in earn.common_lines_ids:
                earn_sum += line.kpi_earn
            earn.total_earn_common = earn_sum

    @api.depends('common_lines_ids.kpi_weight')
    def _total_weight_common(self):
        for weight in self:
            weight_sum = 0
            for line in weight.common_lines_ids:
                weight_sum += line.kpi_weight
            weight.total_weight_common = weight_sum

    @api.depends('function_lines_ids.kpi_point')
    def _total_score_function(self):
        for score in self:
            score_sum = 0
            for line in score.function_lines_ids:
                score_sum += line.kpi_point
            score.total_score_function = score_sum

    @api.depends('function_lines_ids.kpi_earn')
    def _total_earn_function(self):
        for earn in self:
            earn_sum = 0
            for line in earn.function_lines_ids:
                earn_sum += line.kpi_earn
            earn.total_earn_function = earn_sum

    @api.depends('function_lines_ids.kpi_weight')
    def _total_weight_function(self):
        for weight in self:
            weight_sum = 0
            for line in weight.function_lines_ids:
                weight_sum += line.kpi_weight
            weight.total_weight_function = weight_sum

    @api.depends('org_contribute_lines_ids.contribution_score')
    def _total_score_org_contribute(self):
        for score in self:
            score_sum = 0
            for line in score.org_contribute_lines_ids:
                score_sum += line.contribution_score
            score.total_score_org_contribute = score_sum


    @api.depends('group_contribute_lines_ids.contribution_score')
    def _total_score_group_contribute(self):
        for score in self:
            score_sum = 0
            for line in score.group_contribute_lines_ids:
                score_sum += line.contribution_score
            score.total_score_group_contribute = score_sum

    @api.depends('operate_behaviour_lines_ids.kpi_point')
    def _total_score_operate_behaviour(self):
        for score in self:
            score_sum = 0
            for line in score.operate_behaviour_lines_ids:
                score_sum += line.kpi_point
            score.total_score_operate_behaviour = score_sum

    @api.depends('operate_behaviour_lines_ids.kpi_earn')
    def _total_earn_operate_behaviour(self):
        for earn in self:
            earn_sum = 0
            for line in earn.operate_behaviour_lines_ids:
                earn_sum += line.kpi_earn
            earn.total_earn_operate_behaviour = earn_sum

    @api.depends('operate_behaviour_lines_ids.kpi_weight')
    def _total_weight_operate_behaviour(self):
        for weight in self:
            weight_sum = 0
            for line in weight.operate_behaviour_lines_ids:
                weight_sum += line.kpi_weight
            weight.total_weight_operate_behaviour = weight_sum

    @api.depends('manage_behaviour_lines_ids.kpi_point')
    def _total_score_manage_behaviour(self):
        for score in self:
            score_sum = 0
            for line in score.manage_behaviour_lines_ids:
                score_sum += line.kpi_point
            score.total_score_manage_behaviour = score_sum

    @api.depends('manage_behaviour_lines_ids.kpi_earn')
    def _total_earn_manage_behaviour(self):
        for earn in self:
            earn_sum = 0
            for line in earn.manage_behaviour_lines_ids:
                earn_sum += line.kpi_earn
            earn.total_earn_manage_behaviour = earn_sum

    @api.depends('manage_behaviour_lines_ids.kpi_weight')
    def _total_weight_manage_behaviour(self):
        for weight in self:
            weight_sum = 0
            for line in weight.manage_behaviour_lines_ids:
                weight_sum += line.kpi_weight
            weight.total_weight_manage_behaviour = weight_sum

    @api.depends('corporate_lines_ids.kpi_show_score_inline')
    def _total_score_corporate_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.corporate_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_corporate_evaluate = score_sum

    @api.depends('corporate_lines_ids.kpi_show_earn_inline')
    def _total_earn_corporate_evaluate(self):
        for earn in self:
            earn_sum = 0
            for line in earn.corporate_lines_ids:
                earn_sum += line.kpi_show_earn_inline
            earn.total_earn_corporate_evaluate = earn_sum

    @api.depends('corporate_lines_ids.kpi_show_weight_inline')
    def _total_weight_corporate_evaluate(self):
        for weight in self:
            weight_sum = 0
            for line in weight.corporate_lines_ids:
                weight_sum += line.kpi_show_weight_inline
            weight.total_weight_corporate_evaluate = weight_sum

    @api.depends('common_lines_ids.kpi_show_score_inline')
    def _total_score_common_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.common_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_common_evaluate = score_sum

    @api.depends('common_lines_ids.kpi_show_earn_inline')
    def _total_earn_common_evaluate(self):
        for earn in self:
            earn_sum = 0
            for line in earn.common_lines_ids:
                earn_sum += line.kpi_show_earn_inline
            earn.total_earn_common_evaluate = earn_sum

    @api.depends('function_lines_ids.kpi_show_score_inline')
    def _total_score_function_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.function_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_function_evaluate = score_sum

    @api.depends('function_lines_ids.kpi_show_earn_inline')
    def _total_earn_function_evaluate(self):
        for earn in self:
            earn_sum = 0
            for line in earn.function_lines_ids:
                earn_sum += line.kpi_show_earn_inline
            earn.total_earn_function_evaluate = earn_sum

    @api.depends('org_contribute_lines_ids.kpi_show_score_inline')
    def _total_score_org_contribute_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.org_contribute_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_org_contribute_evaluate = score_sum

    @api.depends('group_contribute_lines_ids.kpi_show_score_inline')
    def _total_score_group_contribute_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.group_contribute_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_group_contribute_evaluate = score_sum

    @api.depends('operate_behaviour_lines_ids.kpi_show_score_inline')
    def _total_score_operate_behaviour_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.operate_behaviour_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_operate_behaviour_evaluate = score_sum

    @api.depends('operate_behaviour_lines_ids.kpi_show_earn_inline')
    def _total_earn_operate_behaviour_evaluate(self):
        for earn in self:
            earn_sum = 0
            for line in earn.operate_behaviour_lines_ids:
                earn_sum += line.kpi_show_earn_inline

            earn.total_earn_operate_behaviour_evaluate = earn_sum

    @api.depends('manage_behaviour_lines_ids.kpi_show_score_inline')
    def _total_score_manage_behaviour_evaluate(self):
        for score in self:
            score_sum = 0
            for line in score.manage_behaviour_lines_ids:
                score_sum += line.kpi_show_score_inline

            score.total_score_manage_behaviour_evaluate = score_sum

    @api.depends('manage_behaviour_lines_ids.kpi_show_earn_inline')
    def _total_earn_manage_behaviour_evaluate(self):
        for earn in self:
            earn_sum = 0
            for line in earn.manage_behaviour_lines_ids:
                earn_sum += line.kpi_show_earn_inline

            earn.total_earn_manage_behaviour_evaluate = earn_sum

    @api.depends('state')
    def _total_earn_corporate_evaluate_all(self):
        for earn in self:
            earn_sum = 0
            for line in earn.corporate_lines_ids:
                earn_sum += line.kpi_earn_total
            earn.total_earn_corporate_evaluate_all = earn_sum

    @api.depends('state')
    def _total_earn_common_evaluate_all(self):
        for earn in self:
            earn_sum = 0
            for line in earn.common_lines_ids:
                earn_sum += line.kpi_earn_total
            earn.total_earn_common_evaluate_all = earn_sum

    @api.depends('state')
    def _total_earn_function_evaluate_all(self):
        for earn in self:
            earn_sum = 0
            for line in earn.function_lines_ids:
                earn_sum += line.kpi_earn_total
            earn.total_earn_function_evaluate_all = earn_sum

    @api.depends('state')
    def _total_earn_operate_behaviour_evaluate_all(self):
        for earn in self:
            earn_sum = 0
            for line in earn.operate_behaviour_lines_ids:
                earn_sum += line.kpi_earn_total
            earn.total_earn_operate_behaviour_evaluate_all = earn_sum

    @api.depends('state')
    def _total_earn_manage_behaviour_evaluate_all(self):
        for earn in self:
            earn_sum = 0
            for line in earn.manage_behaviour_lines_ids:
                earn_sum += line.kpi_earn_total
            earn.total_earn_manage_behaviour_evaluate_all = earn_sum

    @api.depends('state')
    def _total_score_org_contribute_evaluate_all(self):
        for score in self:
            score_sum = 0
            for line in score.org_contribute_lines_ids:
                score_sum += line.kpi_score_total

            score.total_score_org_contribute_evaluate_all = score_sum

    @api.depends('state')
    def _total_score_group_contribute_evaluate_all(self):
        for score in self:
            score_sum = 0
            for line in score.group_contribute_lines_ids:
                score_sum += line.kpi_score_total

            score.total_score_group_contribute_evaluate_all = score_sum

    @api.model
    def default_get(self, fields_list):
        res = super(kpi_main, self).default_get(fields_list)
        behaviour_id = self.env['kpi_behaviour_setting'].search([
            ('behaviour_year', '=', self._default_fiscal_year()),
        ], limit=1)
        if behaviour_id:
            manage_line = []
            operate_line = []
            for line in behaviour_id.behaviour_setting_lines_ids:
                if line.behaviour_type == 'management':
                    definitions = []
                    if line.behaviour_definition_setting_lines_ids:
                        for define in line.behaviour_definition_setting_lines_ids:
                            definitions.append([
                                0,
                                0,
                                {
                                    'level': define.level,
                                    'name': define.name
                                }
                            ])
                    manage_line.append([
                        0,
                        0,
                        {
                            'manage_behaviour_setting_lines_id': line.id,
                            'kpi_weight': line.behaviour_weight,
                            'kpi_point': line.behaviour_score,
                            'kpi_manage_behaviour_definition_lines_ids': definitions,
                        }])
                else:
                    definitions = []
                    if line.behaviour_definition_setting_lines_ids:
                        for define in line.behaviour_definition_setting_lines_ids:
                            definitions.append([
                                0,
                                0,
                                {
                                    'level': define.level,
                                    'name': define.name
                                }
                            ])
                    operate_line.append([
                        0,
                        0,
                        {
                            'operate_behaviour_setting_lines_id': line.id,
                            'kpi_weight': line.behaviour_weight,
                            'kpi_point': line.behaviour_score,
                            'kpi_operate_behaviour_definition_lines_ids': definitions,
                        }])

            res.update({
                'manage_behaviour_lines_ids': manage_line,
                'operate_behaviour_lines_ids': operate_line,
            })

        return res

    @api.onchange('routing_evaluate_id')
    def onchange_routing_evaluate_id(self):
        self.ensure_one()
        self.update({
            'evaluate_line_ids': False
        })
        main_line_ids = self.routing_evaluate_id.user_id
        values = []
        employee_ids = []
        for line_id in main_line_ids:
            employee_ids.append(line_id.employee_id.id)
            # self.empolyee_name = [(4, line_id.employee_id.id)]

            values.append([0, 0, {
                'employee_id': line_id.employee_id.id,
                'job_id_name': line_id.job_id_name,
                'status': line_id.status,
                'step': line_id.step,
                'is_active': line_id.is_active,
                'evaluate_ratio': line_id.evaluate_ratio
            }])
        self.update({
            'evaluate_line_ids': values,
            # 'empolyee_name': [(6, _, employee_ids)],
        })

    @api.depends('state')
    def _compute_no_ce_css(self):
        for application in self:
            # Modify below condition
            if application.state != 'draft':
                if application.state == 'evaluating':
                    if application.kpi_evaluating_user.id == self.env.user.id:
                        # Hide Create Button
                        application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>'

                    else:
                        # Hide Create and Edit Button and Bar button
                        application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>' \
                                            '<style>.o_form_button_edit {display: none !important;}</style>' \
                                            '<style>.o_statusbar_buttons {display: none !important;}</style>'
                else:
                    # Hide Create and Edit Button
                    application.no_ce = '<style>.o_form_button_create {display: none !important;}</style>' \
                                        '<style>.o_form_button_edit {display: none !important;}</style>' \
                                        # '<style>.o_statusbar_buttons {display: none !important;}</style>'

            else:
                application.no_ce = False

    @api.depends('state')
    def _compute_show_kpi_sent_button(self):
        kpi_round_setting = self.env['kpi_round_setting'].search([
            # ('fiscal_year_id', '=', self._default_fiscal_year()),
            ('fiscal_year_id', '=', self.kpi_fiscal_year.id),
            ('active', '=', True)
        ], limit=1)
        if kpi_round_setting:
            for rec in self:
                rec.show_kpi_sent_button = kpi_round_setting.show_sent_button

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(kpi_main, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )

        if view_type == 'form':

            kpi_list = self.env['kpi_main'].search([
                ('state', '=', 'draft'),
                ('employee_id', '=', self._get_employee_info().id)
            ])
            if kpi_list:
                for kpi in kpi_list:
                    kpi_round_line_obj = self.env['kpi_round_setting_lines'].search([
                        ('kpi_round_setting_lines_id.fiscal_year_id', '=', kpi.kpi_fiscal_year.id),
                        ('kpi_start', '<=', date.today()),
                        ('kpi_end', '>=', date.today())
                    ], limit=1)
                    if kpi_round_line_obj:
                        kpi.kpi_round = kpi_round_line_obj.kpi_round

            # Check access right evaluate form
            if res['name'] == 'KPI Evaluate form':
                if not view_id:
                    raise ValidationError(
                        _("คุณไม่สามารถเข้าถึงหน้าแบบประเมินได้ เนื่องจากไม่มีสิทธิ์ในการเข้าถึง KPI นี้\n กรุณาติดต่อฝ่ายบริหารทรัพยากรองค์กรและบุคคล"))

                if 'params' in self.env.context:
                    if 'view_type' in self.env.context['params']:
                        if self.env.context['params']['view_type'] == 'form' and 'id' in self.env.context['params']:
                            kpi_main_id = self.env.context['params']['id']
                            kpi_main_obj = self.env['kpi_main'].search([
                                ('id', '=', kpi_main_id)
                            ], limit=1)
                            if kpi_main_obj:
                                if kpi_main_obj.kpi_evaluating_user.id != self.env.user.id:
                                    raise ValidationError(_("คุณไม่สามารถเข้าถึงหน้าแบบประเมินได้ เนื่องจากไม่มีสิทธิ์ในการประเมิน KPI นี้"))

            # Check access right show all form
            if res['name'] == 'KPI Evaluate form all':
                can_show_all = self.env.user.has_group('depa_hr.group_user_depa_hr_show_kpi_all')
                if not can_show_all:
                    raise ValidationError(
                        _("คุณไม่มีสิทธิ์เข้าถึงการใช้งานนี้ กรุณาติดต่อผู้ดูแลระบบ"))


            # kpi_evaluate_list = self.env['kpi_main'].search([
            #     ('state', '=', 'evaluating'),
            #     ('kpi_evaluating_user.id', '=', self.env.user.id)
            # ])
            # print(kpi_evaluate_list)
            # if kpi_evaluate_list:
            #     for evaluate_line in kpi_evaluate_list:
                    # if evaluate_line.kpi_evaluating_user.id == self.env.user.id:
                    #     evaluate_line.is_current_evaluator = True
                    # else:
                    #     evaluate_line.is_current_evaluator = False
                    #
                    # if evaluate_line.corporate_lines_ids:
                    #     for corporate_line in evaluate_line.corporate_lines_ids:
                    #         if corporate_line.kpi_corporate_evaluation_lines_ids:
                    #             for corp_eval_line in corporate_line.kpi_corporate_evaluation_lines_ids:
                    #                 if corp_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     corp_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     corp_eval_line.is_latest_evaluator = False

                    # if evaluate_line.common_lines_ids:
                    #     for common_line in evaluate_line.common_lines_ids:
                    #         if common_line.kpi_common_evaluation_lines_ids:
                    #             for common_eval_line in common_line.kpi_common_evaluation_lines_ids:
                    #                 if common_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     common_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     common_eval_line.is_latest_evaluator = False
                    #
                    # if evaluate_line.function_lines_ids:
                    #     for function_line in evaluate_line.function_lines_ids:
                    #         if function_line.kpi_function_evaluation_lines_ids:
                    #             for function_eval_line in function_line.kpi_function_evaluation_lines_ids:
                    #                 if function_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     function_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     function_eval_line.is_latest_evaluator = False

                    # if evaluate_line.operate_behaviour_lines_ids:
                    #     for operate_line in evaluate_line.operate_behaviour_lines_ids:
                    #         if operate_line.operate_behaviour_evaluation_lines_ids:
                    #             for operate_eval_line in operate_line.operate_behaviour_evaluation_lines_ids:
                    #                 if operate_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     operate_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     operate_eval_line.is_latest_evaluator = False
                    #
                    # if evaluate_line.manage_behaviour_lines_ids:
                    #     for manage_line in evaluate_line.manage_behaviour_lines_ids:
                    #         if manage_line.manage_behaviour_evaluation_lines_ids:
                    #             for manage_eval_line in manage_line.manage_behaviour_evaluation_lines_ids:
                    #                 if manage_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     manage_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     manage_eval_line.is_latest_evaluator = False
                    #
                    # if evaluate_line.org_contribute_lines_ids:
                    #     for org_line in evaluate_line.org_contribute_lines_ids:
                    #         if org_line.kpi_org_contribute_evaluation_lines_ids:
                    #             for org_eval_line in org_line.kpi_org_contribute_evaluation_lines_ids:
                    #                 if org_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     org_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     org_eval_line.is_latest_evaluator = False
                    #
                    # if evaluate_line.group_contribute_lines_ids:
                    #     for group_line in evaluate_line.group_contribute_lines_ids:
                    #         if group_line.kpi_group_contribute_evaluation_lines_ids:
                    #             for group_eval_line in group_line.kpi_group_contribute_evaluation_lines_ids:
                    #                 if group_eval_line.employee_id.user_id.id == self.env.user.id:
                    #                     group_eval_line.is_latest_evaluator = True
                    #                 else:
                    #                     group_eval_line.is_latest_evaluator = False

        return res

    def make_order_evaluate_line(self):
        evaluate_line_ids = self.evaluate_line_ids.sorted(lambda x: x.step)
        sequence = 0
        for line in evaluate_line_ids:
            line.update({"sequence":sequence})
            sequence += 1

    def sent_to_evaluate(self):

        if self.state == 'draft':

            # check dummy user was selected
            if len(self.evaluate_line_ids) > 0:
                for evaluator in self.evaluate_line_ids:
                    if evaluator.employee_id.is_kpi_dummy or evaluator.employee_id.dummy or evaluator.employee_id.is_dummy:
                        raise ValidationError(_("กรุณาระบุผู้ประเมินของคุณให้ครบถ้วนและถูกต้อง"))

            seq = self.env['ir.sequence'].next_by_code('seq_depa_hr_kpi')
            code_no = "KPI" + str(self.kpi_year)[2:] + '-' + self.kpi_round + '-' + str(seq.zfill(3))

            if self.evaluate_line_ids:
                evaluate_line_ids = self.evaluate_line_ids.sorted(lambda x: x.step)
                self.kpi_evaluating_user =  evaluate_line_ids[0].employee_id.user_id.id
                evaluate_line_ids[0].update({
                    'evaluate_status': '0'
                })
                self.evaluate_count += 1

            if self.corporate_lines_ids:
                for corporate_line in self.corporate_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        for evaluate_line in self.evaluate_line_ids:
                            evaluate_lines.append([0, 0, {
                                'employee_id': evaluate_line.employee_id.id,
                                'job_id_name': evaluate_line.job_id_name,
                                'status': evaluate_line.status,
                                'step': evaluate_line.step,
                                'evaluate_ratio': evaluate_line.evaluate_ratio,
                                'draft_score': corporate_line.kpi_score_draft
                            }])

                    corporate_line.update({
                        'kpi_corporate_evaluation_lines_ids' : evaluate_lines
                    })
            if self.common_lines_ids:
                for common_line in self.common_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        for evaluate_line in self.evaluate_line_ids:
                            evaluate_lines.append([0, 0, {
                                'employee_id': evaluate_line.employee_id.id,
                                'job_id_name': evaluate_line.job_id_name,
                                'status': evaluate_line.status,
                                'step': evaluate_line.step,
                                'evaluate_ratio': evaluate_line.evaluate_ratio,
                                # 'draft_score': common_line.kpi_score_draft
                            }])

                    common_line.update({
                        'kpi_common_evaluation_lines_ids' : evaluate_lines
                    })

            if self.function_lines_ids:
                for function_line in self.function_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        for evaluate_line in self.evaluate_line_ids:
                            evaluate_lines.append([0, 0, {
                                'employee_id': evaluate_line.employee_id.id,
                                'job_id_name': evaluate_line.job_id_name,
                                'status': evaluate_line.status,
                                'step': evaluate_line.step,
                                'evaluate_ratio': evaluate_line.evaluate_ratio,
                                # 'draft_score': function_line.kpi_score_draft
                            }])

                    function_line.update({
                        'kpi_function_evaluation_lines_ids' : evaluate_lines
                    })

            if self.org_contribute_lines_ids:
                for org_contribute_line in self.org_contribute_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        evaluate_line_ids = self.evaluate_line_ids.sorted(lambda x: x.step)
                        evaluate_line = evaluate_line_ids[0]
                        evaluate_lines.append([0, 0, {
                            'employee_id': evaluate_line.employee_id.id,
                            'job_id_name': evaluate_line.job_id_name,
                            'status': evaluate_line.status,
                            'step': evaluate_line.step,
                        }])
                        # for evaluate_line in self.evaluate_line_ids:
                        #     evaluate_line_ids = self.env['kpi_evaluate_lines'].search([
                        #         ('id', '=', evaluate_line.id),
                        #         ('step', '=', 1),
                        #     ], limit=1)
                        #     for evaluate in evaluate_line_ids:
                        #         evaluate_lines.append([0, 0, {
                        #             'employee_id': evaluate.employee_id.id,
                        #             'job_id_name': evaluate.job_id_name,
                        #             'status': evaluate.status,
                        #         }])

                    org_contribute_line.update({
                        'kpi_org_contribute_evaluation_lines_ids': evaluate_lines
                    })

            if self.group_contribute_lines_ids:
                for group_contribute_line in self.group_contribute_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        evaluate_line = evaluate_line_ids[0]
                        evaluate_lines.append([0, 0, {
                            'employee_id': evaluate_line.employee_id.id,
                            'job_id_name': evaluate_line.job_id_name,
                            'status': evaluate_line.status,
                            'step': evaluate_line.step,
                        }])
                        # for evaluate_line in self.evaluate_line_ids:
                        #     evaluate_line_ids = self.env['kpi_evaluate_lines'].search([
                        #         ('id', '=', evaluate_line.id),
                        #         ('step', '=', 1),
                        #     ], limit=1)
                        #     for evaluate in evaluate_line_ids:
                        #         evaluate_lines.append([0, 0, {
                        #             'employee_id': evaluate.employee_id.id,
                        #             'job_id_name': evaluate.job_id_name,
                        #             'status': evaluate.status,
                        #         }])
                    group_contribute_line.update({
                        'kpi_group_contribute_evaluation_lines_ids': evaluate_lines
                    })

            if self.manage_behaviour_lines_ids:
                for manage_behaviour_line in self.manage_behaviour_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        for evaluate_line in self.evaluate_line_ids:
                            evaluate_lines.append([0, 0, {
                                'employee_id': evaluate_line.employee_id.id,
                                'job_id_name': evaluate_line.job_id_name,
                                'status': evaluate_line.status,
                                'step': evaluate_line.step,
                                'evaluate_ratio': evaluate_line.evaluate_ratio,
                            }])

                    manage_behaviour_line.update({
                        'manage_behaviour_evaluation_lines_ids' : evaluate_lines
                    })

            if self.operate_behaviour_lines_ids:
                for operate_behaviour_line in self.operate_behaviour_lines_ids:
                    evaluate_lines = []
                    if self.evaluate_line_ids:
                        for evaluate_line in self.evaluate_line_ids:
                            evaluate_lines.append([0, 0, {
                                'employee_id': evaluate_line.employee_id.id,
                                'job_id_name': evaluate_line.job_id_name,
                                'status': evaluate_line.status,
                                'step': evaluate_line.step,
                                'evaluate_ratio': evaluate_line.evaluate_ratio,
                            }])

                    operate_behaviour_line.update({
                        'operate_behaviour_evaluation_lines_ids' : evaluate_lines
                    })


            self.update({
                'kpi_no': code_no,
                'is_create': False,
                'sent_evaluate_at': datetime.now(),
                'state': 'evaluating'
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def make_evaluate_confirm_action(self):
        return {
            'name': "Evaluate confirmation wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'make_kpi_evaluate_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_kpi_main_id': self.id,
                'default_evaluate_count': self.evaluate_count,
                'default_action_status': 'confirm',
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }

    def make_evaluate_adjust_action(self):
        return {
            'name': "Evaluate adjustment wizard",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'make_kpi_evaluate_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_kpi_main_id': self.id,
                'default_evaluate_count': self.evaluate_count,
                'default_action_status': 'adjust',
                # 'default_employee_id': employee_id.id,
                # 'default_setting_line': setting_line,
                # 'default_status': status,
                # 'default_total_for_approve': len(self.setting_line_ids) - count_nonactive,
                # 'default_setting_id': self.id,
            }
        }

    def summary_action(self):
        print('summary action')

    def make_to_evaluating_action(self):
        # print(self)
        if self.evaluate_line_ids:
            count = self.evaluate_count
            evaluate_user = self.evaluate_line_ids[count - 1]
            evaluate_user.update({
                'comment': False,
                'evaluate_time': False,
                'evaluate_status': '0'
            })
            self.update({
                'kpi_evaluating_user': evaluate_user.employee_id.user_id.id,
                'state': 'evaluating'
            })
            self.message_post(body=str(self.kpi_no) + " ถูกส่งกลับให้ผู้ประเมินลำดับสุดท้ายประเมินอีกครั้ง ")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }