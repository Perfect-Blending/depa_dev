# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WizardFinRecomputeBudget(models.TransientModel):
    _name = 'wizard.fin.recompute.budget'

    def action_recompute_budget(self):
        fin100_obj = self.env['fw_pfb_fin_system_100'].search([])
        for obj in fin100_obj:
            if obj.fin_projects:
                obj.fin_projects.unlink()
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
        return True