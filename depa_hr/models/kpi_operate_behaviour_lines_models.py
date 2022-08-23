from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError

class kpi_operate_behaviour_lines(models.Model):
    _name = 'kpi_operate_behaviour_lines'

    operate_behaviour_setting_lines_id = fields.Many2one(
        'kpi_behaviour_setting_lines',
        required=True
    )
    kpi_id = fields.Char(
        string="KPI ID"
    )
    kpi_name = fields.Text(
        string="KPI NAME",
    )
    kpi_weight = fields.Float(
        string="น้ำหนัก",
        digits=(10, 8)
    )
    kpi_point = fields.Float(
        string="คะแนน",
        digits=(10, 2)
    )
    kpi_earn = fields.Float(
        string="Earn",
        digits=(10, 8),
        compute="_kpi_earn_compute"
    )
    kpi_detail = fields.Text(
        string="รายละเอียด"
    )
    kpi_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year'
    )
    operate_behaviour_lines_id = fields.Many2one(
        'kpi_main',
        string="manage behaviour id",
        required=True,
        ondelete='cascade'
    )
    kpi_operate_behaviour_definition_lines_ids = fields.One2many(
        "kpi_operate_behaviour_definition_lines",
        "kpi_operate_behaviour_definition_lines_id",
        string="คำจำกัดความ",
        copy=True
    )
    operate_behaviour_evaluation_lines_ids = fields.One2many(
        "operate_behaviour_evaluation_lines",
        "operate_behaviour_evaluation_lines_id",
        string="Evaluation Lines"
    )
    kpi_score_total = fields.Integer(
        string="Score Total",
        compute='_kpi_score_total',
        readonly=True,
        store=True
    )
    kpi_earn_total = fields.Float(
        string="Earn Total",
        compute='_kpi_earn_total',
        readonly=True,
        digits=(10, 8),
        store=True
    )
    kpi_show_score_inline = fields.Float(
        string="Score Inline",
        compute='_kpi_show_score_inline',
        digits=(10, 2),
        readonly=True,
        store=False
    )
    kpi_show_earn_inline = fields.Float(
        string="Earn Inline",
        digits=(10, 8),
        compute='_kpi_show_earn_inline',
        readonly=True,
        store=False
    )
    operate_behaviour_attachment_ids = fields.Many2many(
        "ir.attachment",
        "operate_behaviour_lines_attachment_rel",
        "operate_behaviour_attachment_lines_id",
        "ir_attachment_id",
        string='ไฟล์แนบ',
        # required=True
    )
    @api.depends('operate_behaviour_evaluation_lines_ids')
    def _kpi_show_score_inline(self):
        for rec in self:
            for line in rec.operate_behaviour_evaluation_lines_ids:
                if line.is_latest_evaluator:
                    rec.kpi_show_score_inline = line.score

    @api.depends('operate_behaviour_evaluation_lines_ids')
    def _kpi_show_earn_inline(self):
        for rec in self:
            for line in rec.operate_behaviour_evaluation_lines_ids:
                if line.is_latest_evaluator:
                    rec.kpi_show_earn_inline = line.earn

    @api.depends('operate_behaviour_evaluation_lines_ids')
    def _kpi_earn_total(self):
        for rec in self:
            sum = 0
            for line in rec.operate_behaviour_evaluation_lines_ids:
                sum += line.earn

            rec.kpi_earn_total = sum

    @api.depends('operate_behaviour_evaluation_lines_ids')
    def _kpi_score_total(self):
        for rec in self:
            sum = 0
            for line in rec.operate_behaviour_evaluation_lines_ids:
                sum += line.score

            rec.kpi_score_total = sum

    @api.depends('kpi_weight', 'kpi_point')
    def _kpi_earn_compute(self):
        for rec in self:
            rec.kpi_earn = rec.kpi_weight * rec.kpi_point

    @api.onchange('operate_behaviour_setting_lines_id')
    def _behaviour_lines_change(self):
        for rec in self:
            rec.kpi_weight = rec.operate_behaviour_setting_lines_id.behaviour_weight

    @api.onchange('kpi_point')
    def onchange_kpi_point(self):
        for rec in self:
            if len(rec.kpi_operate_behaviour_definition_lines_ids) > 0:
                points = [int(point.level) for point in rec.kpi_operate_behaviour_definition_lines_ids]
                if (rec.kpi_point != 0 and rec.kpi_point < min(points)) or rec.kpi_point > max(points):
                    rec.kpi_point = 0
                    raise ValidationError(_(f"คะแนนต้องอยู่ในช่วงเดียวกับระดับคะแนน คือ {min(points)} - {max(points)}"))
            else:
                raise ValidationError(_(f"ติดต่อ HR เพื่อระบุเกณฑ์คะแนนสำหรับ KPI ของคุณในข้อนี้"))

class kpi_operate_behaviour_definition_lines(models.Model):
    _name = 'kpi_operate_behaviour_definition_lines'

    kpi_operate_behaviour_definition_lines_id = fields.Many2one(
        'kpi_operate_behaviour_lines',
        required=True,
        ondelete='cascade'
    )

    level = fields.Selection(
        [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
        ],
        string="ระดับคะแนน",
        required=True
    )
    name = fields.Char(
        string="คำจำกัดความ",
        required=True
    )
    active = fields.Boolean(
        default=True
    )

class operate_behaviour_evaluation_lines(models.Model):
    _name = 'operate_behaviour_evaluation_lines'

    operate_behaviour_evaluation_lines_id = fields.Many2one(
        "kpi_operate_behaviour_lines",
        string="Evaluate line id",
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string="ชื่อผู้ประเมิน",
        readonly=True
    )
    job_id_name = fields.Many2one(
        'hr.job',
        string="ตำแหน่ง",
        readonly=True
    )
    step = fields.Selection(
        string="Step",
        selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8')
        ],
        readonly=True
    )
    status = fields.Selection(
        string="สถานะ",
        selection=[
            ('1', 'ผู้บังคับบัญชาขั้นต้น'),
            ('2', 'ผอ.ฝ่าย'),
            ('3', 'ฝ่ายที่เกี่ยวข้อง-1'),
            ('4', 'เลขา ชสศด./รสศด.'),
            ('5', 'ชสศด.'),
            ('6', 'รสศด.'),
            ('7', 'ฝ่ายที่เกี่ยวข้อง-2'),
            ('8', 'ผสศด.')
        ],
        readonly=True
    )

    score = fields.Float(
        string="คะแนน",
        digits=(10, 2)
    )
    earn = fields.Float(
        string="Earn",
        compute='_kpi_earn_lines_total',
        readonly=True,
        digits=(10, 8),
        store=True
    )
    evaluate_ratio = fields.Float(
        string="สัดส่วน",
        digits=(10, 4)
    )
    is_latest_evaluator = fields.Boolean(
        string='is_latest_evaluator',
        compute='_compute_is_latest_evaluator',
        store=False,
        # default=False
    )

    @api.depends('operate_behaviour_evaluation_lines_id.operate_behaviour_lines_id.state')
    def _compute_is_latest_evaluator(self):
        for rec in self:
            state = rec.operate_behaviour_evaluation_lines_id.operate_behaviour_lines_id.state
            if state == 'evaluating':
                if rec.employee_id.user_id.id == self.env.user.id:
                    rec.is_latest_evaluator = True
                else:
                    rec.is_latest_evaluator = False

    @api.depends('score')
    def _kpi_earn_lines_total(self):
        for rec in self:
            rec.earn = (rec.score * rec.evaluate_ratio) * rec.operate_behaviour_evaluation_lines_id.kpi_weight

    @api.onchange('score')
    def onchange_score(self):
        for rec in self:
            definition_line_ids = rec.operate_behaviour_evaluation_lines_id.kpi_operate_behaviour_definition_lines_ids
            if len(definition_line_ids) > 0:
                points = [int(point.level) for point in definition_line_ids]
                if (rec.score != 0 and rec.score < min(points)) or rec.score > max(points):
                    rec.score = 0
                    raise ValidationError(_(f"คะแนนต้องอยู่ในช่วงเดียวกับระดับคะแนน คือ {min(points)} - {max(points)}"))
            else:
                raise ValidationError(_(f"ติดต่อ HR เพื่อระบุเกณฑ์คะแนนสำหรับ KPI ของคุณในข้อนี้"))