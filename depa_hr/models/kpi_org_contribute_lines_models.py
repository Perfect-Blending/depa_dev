from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError
class kpi_org_contribute_lines(models.Model):
    _name = 'kpi_org_contribute_lines'

    contribution_lines_id = fields.Many2one(
        'kpi_contribution_setting_lines',
        string = 'Contribution',
        required=True
    )
    contribution_score = fields.Float(
        string='คะแนน',
        readonly=True,
        digits=(10, 2)
    )
    contribution_date = fields.Date(
        string='วันที่',
        required=True
    )
    contribution_detail = fields.Text(
        string='รายละเอียด'
    )
    org_contribute_lines_id = fields.Many2one(
        'kpi_main',
        string="org contribute id",
        required=True,
        ondelete='cascade'
    )
    kpi_org_contribute_evaluation_lines_ids = fields.One2many(
        "kpi_org_contribute_evaluation_lines",
        "kpi_org_contribute_evaluation_lines_id",
        string="Evaluation Lines"
    )
    kpi_year = fields.Many2one(
        'fw_pfb_fin_system_fiscal_year'
    )
    kpi_score_total = fields.Float(
        string="Score Total",
        compute='_kpi_score_total',
        digits=(10, 8),
        readonly=True,
        store=True
    )
    kpi_show_score_inline = fields.Float(
        string="Score Inline",
        compute='_kpi_show_score_inline',
        digits=(10, 2),
        readonly=True,
        store=False
    )
    org_contribute_attachment_ids = fields.Many2many(
        "ir.attachment",
        "org_contribute_lines_attachment_rel",
        "org_contribute_attachment_lines_id",
        "ir_attachment_id",
        string='ไฟล์แนบ',
        # required=True
    )

    @api.depends('kpi_org_contribute_evaluation_lines_ids')
    def _kpi_show_score_inline(self):
        for rec in self:
            for line in rec.kpi_org_contribute_evaluation_lines_ids:
                if line.is_latest_evaluator:
                    rec.kpi_show_score_inline = line.score

    @api.depends('kpi_org_contribute_evaluation_lines_ids')
    def _kpi_score_total(self):
        for rec in self:
            sum = 0
            for line in rec.kpi_org_contribute_evaluation_lines_ids:
                sum += line.score

            rec.kpi_score_total = sum

    @api.onchange('contribution_lines_id')
    def _contribution_lines_change(self):
        for rec in self:
            rec.contribution_score = rec.contribution_lines_id.contribution_score

class kpi_org_contribute_evaluation_lines(models.Model):
    _name = 'kpi_org_contribute_evaluation_lines'

    kpi_org_contribute_evaluation_lines_id = fields.Many2one(
        "kpi_org_contribute_lines",
        string="Evaluate line id",
        required=True,
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="ชื่อผู้ประเมิน",
        readonly=True
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
    is_latest_evaluator = fields.Boolean(
        string='is_latest_evaluator',
        compute='_compute_is_latest_evaluator',
        store=False,
        # default=False
    )

    @api.depends('kpi_org_contribute_evaluation_lines_id.org_contribute_lines_id.state')
    def _compute_is_latest_evaluator(self):
        for rec in self:
            state = rec.kpi_org_contribute_evaluation_lines_id.org_contribute_lines_id.state
            if state == 'evaluating':
                if rec.employee_id.user_id.id == self.env.user.id:
                    rec.is_latest_evaluator = True
                else:
                    rec.is_latest_evaluator = False

    @api.onchange('score')
    def onchange_score(self):
        for rec in self:
            total_score = rec.kpi_org_contribute_evaluation_lines_id.contribution_score
            if rec.score < 0 or rec.score > total_score:
                    raise ValidationError(_(f"คะแนนต้องอยู่ในช่วงเดียวกับระดับคะแนน คือ 1 - {total_score}"))



