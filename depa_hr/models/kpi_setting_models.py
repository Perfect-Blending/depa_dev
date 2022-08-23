from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class kpi_setting(models.Model):
    _name = 'kpi_setting'

    def _default_fiscal_year(self):
        fiscal_year_obj = self.env['fw_pfb_fin_system_fiscal_year'].search([
            ('date_start', '<=', date.today()),
            ('date_end', '>=', date.today()),
        ], limit=1)
        if fiscal_year_obj:
            return fiscal_year_obj.id

    kpi_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year',
        default=_default_fiscal_year,
        required=True
    )
    kpi_setting_lines_ids = fields.One2many(
        'kpi_setting_lines',
        'kpi_setting_lines_id',
        required=True,
        copy=True
    )

class kpi_setting_lines(models.Model):
    _name = 'kpi_setting_lines'

    kpi_id = fields.Char(string="รหัส KPI")
    kpi_name = fields.Text(string='ชื่อ KPI')
    kpi_type = fields.Char(string="ประเภท")
    kpi_source = fields.Char(string="ที่มา")
    kpi_unit = fields.Many2one(
        'uom.uom',
        'หน่วย'
    )
    kpi_target = fields.Char(string='เป้าหมาย')
    kpi_setting_lines_id = fields.Many2one(
        'kpi_setting'
    )
    kpi_setting_group_lines_ids = fields.One2many(
        'kpi_setting_group_lines',
        'kpi_setting_group_lines_id',
        required=True,
        copy=True
    )
    active = fields.Boolean(
        default=True
    )

    @api.multi
    def name_get(self):
        return [(line.id, str(line.kpi_id) +" "+ str(line.kpi_name)) for i, line in enumerate(self)]

    @api.model
    def name_search(self, name, args=None, operator='like', limit=100):
        if not args:
            args = []
        if name:
            result = self._search(args + [
                '|',
                ('kpi_id', operator, name),
                ('kpi_name', operator, name),

            ])
        else:
            result = self._search(args, limit=limit)
        return self.browse(result).name_get()

class kpi_setting_group_lines(models.Model):
    _name = 'kpi_setting_group_lines'


    kpi_group = fields.Selection(
        string="กลุ่มงาน",
        selection=[
            ('ศด', 'กลุ่มงานเศรษฐกิจดิจิทัล'),
            ('สก', 'กลุ่มงานสังคมและกำลังคนดิจิทัล'),
            ('คพ', 'กลุ่มงานโครงการพิเศษ'),
            ('ยศ', 'กลุ่มงานยุทธศาสตร์และบริหาร'),
            ('บห', 'กลุ่มงานบริหารสำนักงาน'),
            ('กส', 'กลุ่มงานกิจการสาขา'),
            ('GBDi', 'GBDi')
        ]
    )

    kpi_weight = fields.Float(
        string='น้ำหนัก'
    )
    level = fields.Integer(
        string='ระดับ '
    )
    kpi_unit =fields.Many2one(
        'uom.uom',
        'หน่วย'
    )


    kpi_setting_group_lines_id = fields.Many2one(
        'kpi_setting_lines'
    )

class kpi_evaluate_setting(models.Model):
    _name = 'kpi_evaluate_setting'
    _description = 'ลำดับการประเมิน'

    name = fields.Char(
            string='ชื่อ',
            required=True,
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    user_id = fields.One2many(
        'kpi_evaluate_setting_lines',
        'evaluate_setting_id',
        string='Approval',
        required=True,
        copy=True
    )
    evaluate_ratio_total = fields.Float(
        string='รวมสัดส่วนการประเมิน',
        digits=(10, 2),
        compute='_evaluate_ratio_total',
        store=True
    )

    @api.depends('user_id')
    def _evaluate_ratio_total(self):
        for record in self:
            ratio_sum = 0
            if record.user_id:
                for line in record.user_id:
                    ratio_sum += line.evaluate_ratio
            record.evaluate_ratio_total = ratio_sum

    @api.constrains('evaluate_ratio_total')
    def _evaluate_ratio_total_ctr(self):
        for line in self:
            # if line.evaluate_ratio_total not in range(2):
            #     raise ValidationError(_("ผลรวมของสัดส่วนการประเมินต้องมีค่าเท่ากับ 0-1"))

            if len(line.user_id) > 0 and line.evaluate_ratio_total != 1:
                raise ValidationError(_("ผลรวมของสัดส่วนการประเมินต้องมีค่าเท่ากับ 1"))

class kpi_evaluate_setting_lines(models.Model):
    _name = 'kpi_evaluate_setting_lines'
    _description = 'ลำดับการประเมิน'
    _order = 'step asc'

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
        ('8', '8'),
    ], default='1', index=True)
    status = fields.Selection(string="Status", selection=[
        ('1', 'ผู้บังคับบัญชาขั้นต้น'),
        ('2', 'ผอ.ฝ่าย'),
        ('3', 'ฝ่ายที่เกี่ยวข้อง-1'),
        ('4', 'เลขา ชสศด./รสศด.'),
        ('5', 'ชสศด.'),
        ('6', 'รสศด.'),
        ('7', 'ฝ่ายที่เกี่ยวข้อง-2'),
        ('8', 'ผสศด.')
    ], default='1', readonly=True, compute='set_step')

    # approve_type = fields.Selection(string="Approve type", selection=[
    #     ('require', 'Is require to approve'),
    #     ('comments', 'Comments only')],
    #                                 default='require')

    evaluate_setting_id = fields.Many2one(
        'kpi_evaluate_setting',
        string="Evaluate setting id"
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    evaluate_ratio = fields.Float(
        string='สัดส่วนการประเมิน',
        digits=(10, 4),
        required=True
    )
    sequence = fields.Integer(string='Sequence', index=True, default=10)

    @api.depends('step')
    # @api.onchange('step')
    def set_step(self):
        # self.ensure_one()
        for record in self:
            if record.step:
                step = record.step
                # record.update({'status':step})
                record.status = step

    @api.onchange('employee_id')
    def employee_id_changed(self):
        self.job_id_name = self.employee_id.job_id


