# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.

from odoo import api, fields, models, _


class fin_100_request_wiz(models.TransientModel):
    _inherit = 'fin_100_request_wiz'

    @api.multi
    def finish_choose(self):
        fin401_id = False
        if 'active_id' in self._context :
            fin401_id = self._context['active_id']
        elif 'id' in self._context['params'] :
            fin401_id = self._context['params']['id']

        lines = False
        all = False
        if self.filter_prall:
            lines = self.item_fin100_ids_all
            all = True
        else :
            lines = self.item_fin100_ids

        if lines:
            fin401_line_obj = self.env['fw_pfb_fin_system_401_line']

            cloneDatas = False
            objective = False
            fin_objective = False
            other = False
            estimate_output = False
            participantas_quantity = False

            f401 = self.env['fw_pfb_fin_system_401'].browse( fin401_id )

            for each in lines:
                if each.select or all:

                    # never go to this condition!!!
                    if not cloneDatas:
                        cloneDatas = True

                        objective = each.fin100_number.objective
                        if each.fin100_number.fin_objective :
                            fin_objective = each.fin100_number.fin_objective.id
                        other = each.fin100_number.other
                        estimate_output = each.fin100_number.estimate_output
                        participantas_quantity = each.fin100_number.participantas_quantity

                        if f401 :
                            f401.write({
                                "objective": objective,
                                "fin_objective": fin_objective,
                                "other": other,
                                "estimate_output": estimate_output,
                                "participantas_quantity": participantas_quantity,
                            })

                    data = {
                        "fin_id": fin401_id,
                        "description": each.description,
                        "product_uom": each.unit_name.id,
                        "product_uom_qty": each.unit,
                        "price_unit": each.price_unit,
                        "price_subtotal": each.unit * each.price_unit,
                        "product_id": each.product_id.id,
                        "projects_and_plan": False,
                        "fin_line_id": str(each.fin_line_id),
                        "fin_type": each.fin_type,
                        "fin100_line_id": self.env['fw_pfb_fin_system_100_line'].browse(int(each.fin_line_id)).id,
                        "fin100_id": each.fin100_number.id, #related from fin100_line_id.fin_id
                    }
                    fin401_line = fin401_line_obj.create(data)

                    #fin100_line_id = self.env['fw_pfb_fin_system_100_line'].browse( int( each.fin_line_id ) )
                    fin100_line_id = self.env['fw_pfb_fin_system_100_line'].browse( int( each.fin_line_id ) )
                    if fin100_line_id :
                        # for what?
                        data2 = {
                            "wiz_id" : each.fin_line_id,
                            "fin_date" : each.date,
                            "fin401_id" : str(fin401_id),
                            "fin401_line_id" : fin401_line.id,
                            "product_id" : each.product_id.id,
                            "description" : each.description,
                            "status" : "draft"
                        }
                        print(data2)
                        fin100_line_id.item_fin401_ids.create(data2)

                        if f401 :
                            f401.write({"swap" : True})


class fin_100_request_wiz_item(models.TransientModel):
    _inherit = 'fin_100_request_wiz_item'

    fin100_line_id = fields.Many2one('fw_pfb_fin_system_100_line',string='FIN100 Line' )
    fin100_id = fields.Many2one('fw_pfb_fin_system_100',string='FIN100' )
