# -*- coding: utf-8 -*-
# ProThai Technology Co., Ltd.

from odoo import api, fields, models, _


class fin_201_request_101_wiz(models.TransientModel):
    _inherit = 'fin_201_request_101_wiz'

    @api.multi
    def finish_choose(self):
        fin201_id = False
        if 'active_id' in self._context :
            fin201_id = self._context['active_id']
        elif 'id' in self._context['params'] :
            fin201_id = self._context['params']['id']

        lines = False
        all = False
        if self.filter_prall:
            lines = self.item_fin100_ids_all
            all = True
        else :
            lines = self.item_fin100_ids

        if lines:
            fin201_line_obj = self.env['fw_pfb_fin_system_201_line']
            fid = False
            ob = False
            total = 0
            loan_amount = 0
            payment_amount = 0

            for each in lines :
                if each.select or all:

                    fid = each.fin100_number.id
                    ob = each.objective
                    total = total + ( each.unit * each.price_unit )
                    data = {
                        "fin_id": fin201_id,
                        "description": each.description,
                        "product_uom": each.unit_name.id,
                        "product_uom_qty": each.unit,
                        "price_unit": each.price_unit,
                        "price_subtotal": each.unit * each.price_unit,
                        "product_id": each.product_id.id,
                        "projects_and_plan": False,
                        "fin_line_id": str(each.fin_line_id),
                        "loan_amount": self.default_loan_amount(str(each.fin_line_id)),
                        "fin100_number": each.fin100_number.id,
                        "fin_type": each.fin_type,
                        "objective": each.objective,
                        "fin100_line_id": self.env['fw_pfb_fin_system_100_line'].browse(int(each.fin_line_id)).id,
                        #"fin100_id": each.fin100_number.id, #related from fin100_line_id.fin_id
                    }
                    fin201_line = fin201_line_obj.create(data)

                    fin100_line_id = self.env['fw_pfb_fin_system_100_line'].browse(int(each.fin_line_id))
                    if fin100_line_id :
                        # why do we need this?
                        data2 = {
                            "wiz_id": each.fin_line_id,
                            "fin_date": each.date,
                            "fin201_id": str(fin201_id),
                            "fin201_line_id": fin201_line.id,
                            "product_id": each.product_id.id,
                            "description": each.description,
                            "status": "draft"
                        }
                        #print(data2)
                        fin100_line_id.item_fin201_ids.create(data2)

            request_amount_total = 0
            load_amount_total = 0
            price_total = 0
            allfinline = fin201_line_obj.search([('fin_id','=',fin201_id)])
            if allfinline :
                for i in allfinline:
                    if i.price_subtotal :
                        request_amount_total += i.price_subtotal
                    if i.loan_amount :
                        load_amount_total += i.loan_amount
                    if i.payment_amount :
                        price_total += i.payment_amount


            fin201 = self.env['fw_pfb_fin_system_201'].browse(fin201_id)
            if fin201 :
                fin201.write({
                    #"objective": ob,
                    "request_amount_total": total,
                    "approved_amount": total,
                    "request_amount_total": request_amount_total,
                    "load_amount_total": load_amount_total,
                    "price_total": price_total,
                    "spent_amount_total": 0,
                    "remaining_total": price_total,
                })


class fin_201_request_101_wiz_item(models.TransientModel):
    _inherit = 'fin_201_request_101_wiz_item'

    fin100_line_id = fields.Many2one('fw_pfb_fin_system_100_line', string='FIN100 Line')
    fin100_id = fields.Many2one('fw_pfb_fin_system_100', string='FIN100')
