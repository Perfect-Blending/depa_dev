from odoo import api, fields, models, _
from odoo.exceptions import Warning
import base64,os
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
import xlsxwriter
import time

class StockCard(models.TransientModel):
    _name = 'stock.card'
    _description = 'Stock Card Wizard'

    date_from = fields.Datetime('From')
    date_to = fields.Datetime('To')
    product_ids = fields.Many2many('product.template', 'stock_card_product_rel', 
                                  'stock_card_id', 'product_id', string='Product(s)')
    product_categ_id = fields.Many2one('product.category', 'Internal Category')
    report_type = fields.Selection([('stock_card','Stock Card Report'),
                                    ('stock_card_summary','Stock Card Summary Report')],
                                   string="Report Type", default=lambda *a: 'stock_card')
    move_type = fields.Selection([('1','All Moves'),
                                  ('2','Without Internal Moves')], 
                                 string="Move Type", default=lambda *a:'1')
    excelfile = fields.Binary('Excel File')
    file_name = fields.Char('File Name')
    excel_flag = fields.Boolean('Show Excel File', default=lambda *a: False)

    @api.onchange('product_categ_id')
    def onchange_product_categ_id(self):
        domain = {'product_ids': [('type','=','product')]}
        if self.product_categ_id:
            domain = {'product_ids': [('categ_id', '=', self.product_categ_id.id),
                                      ('type','=','product')]}
        return {'domain': domain}

    @api.multi
    def print_report(self):
        """
        To get the date and print the report
        @return : return report
        """
        datas = {}
        res = self.read(['date_from', 'date_to', 'product_ids', 'report_type', 
                         'product_categ_id', 'move_type'])
        res = res and res[0] or {}
        if res['date_to'] and not res['date_from']:
            raise Warning(_('Since Date To is selected, please select Date From.'))
        res['ids'] = res['product_ids']
        if not res['ids'] and not res['product_categ_id']:
            pids = self.env['product.template'].search([('type','=','product')])
            res['ids'] = [x.id for x in pids]
        if not res['ids'] and res['product_categ_id']:
            pids = self.env['product.template'].search([('type','=','product'),
                                    ('categ_id','=',res['product_categ_id'][0])])
            res['ids'] = [x.id for x in pids]

        datas['form'] = res
        print ("RES: --------> ",res)
        if res['report_type'] == 'stock_card':
            return self.env.ref('rt_stock_card.report_stockcard').report_action([], data=datas)
        if res['report_type'] == 'stock_card_summary':
            return self.env.ref('rt_stock_card.report_stockcard_summary').report_action([], data=datas)

    @api.multi
    def generate_stock_card_summary(self):
        product_template = self.env['product.template']
        res = self.read(['date_from', 'date_to', 'product_ids', 'report_type', 'move_type',
                         'product_categ_id'])
        res = res and res[0] or {}
        if res['date_to'] and not res['date_from']:
            raise Warning(_('Since Date To is selected, please select Date From.'))
        if not res['product_ids'] and not res['product_categ_id']:
            pids = self.env['product.template'].search([('type','=','product')])
            res['product_ids'] = [x.id for x in pids]
        if not res['product_ids'] and res['product_categ_id']:
            pids = self.env['product.template'].search([('type','=','product'),
                                    ('categ_id','=',res['product_categ_id'][0])])
            res['product_ids'] = [x.id for x in pids]

        prod_data = []

        if not self.product_ids:
            domain = [('type','=','product')]
            if self.product_categ_id:
                domain += [('categ_id','=', self.product_categ_id.id)]
            product_ids = self.env['product.template'].search(domain)
        else:
            product_ids = self.product_ids

        for template in product_ids:
            opening_data = template.with_context(res).get_opening_balance()
            all_data = template.with_context(res).generate_stock_card()
            location = ''

            product = template.get_product_id()
            if not product: continue

            inqty = 0.0
            invalue = 0.0
            outqty = 0.0
            outvalue = 0.0
            for x in all_data:
                location = x['location']
                if x['value'] > 0:
                    inqty += x['product_qty']
                    invalue += x['value'] or 0.0
                if x['value'] < 0:
                    outqty += x['product_qty']
                    outvalue += x['value'] or 0.0

            endqty = opening_data[0]['opening_qty'] + inqty - outqty
            endvalue = opening_data[0]['opening_value'] + invalue + outvalue

            data = {'product_id': product.id,
                     'product_name': product.name,
                     'location': location,
                     'beginqty': opening_data[0]['opening_qty'],
                     'beginvalue': opening_data[0]['opening_value'],
                     'inqty': inqty,
                     'invalue': invalue,
                     'outqty': outqty,
                     'outvalue': outvalue,
                     'endqty': endqty,
                     'endvalue': endvalue
                     }
            prod_data.append(data)
        return prod_data

    @api.multi
    def stock_card_excel(self):
        show_value = self.env.user.has_group('rt_stock_card.group_stock_card_qty_values')
        product_template = self.env['product.template']
        res = self.read(['date_from', 'date_to', 'product_ids', 'report_type', 'move_type',
                         'product_categ_id'])
        res = res and res[0] or {}
        if res['date_to'] and not res['date_from']:
            raise Warning(_('Since Date To is selected, please select Date From.'))
        if not res['product_ids'] and not res['product_categ_id']:
            pids = self.env['product.template'].search([('type','=','product')])
            res['product_ids'] = [x.id for x in pids]
        if not res['product_ids'] and res['product_categ_id']:
            pids = self.env['product.template'].search([('type','=','product'),
                                    ('categ_id','=',res['product_categ_id'][0])])
            res['product_ids'] = [x.id for x in pids]

        today = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT).replace(':','').replace(' ','_').replace('-','')
        filename = 'Stock_Card_%s.xlsx' % (today)
        title = 'Stock Card Report'
        if res['date_from'] and res['date_to']:
            title += ' (%s - %s)'%(res['date_from'],res['date_to'])
        if res['date_from'] and not res['date_to']:
            title += ' (%s - Till Date)'%(res['date_from'])

        workbook = xlsxwriter.Workbook('/tmp/%s'%(filename))
        worksheet = workbook.add_worksheet()

        #FORMATING PROPERTIES
        title_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#99ff66',##A9A9A9
        'underline': 2,
        'border': 1,
        'size': 14})
        total_format = workbook.add_format({'bold': 1, 'bg_color': '#ccccff', 'top': 1,
                                            'underline': 2, 'size': 10})
        total_format.set_num_format('0.00')

        dateFormat = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss',
                                      'size': 10,'align': 'left','valign': 'vcenter'})

        td_left_bold = workbook.add_format({'size': 10,'align': 'left','valign': 'vcenter','bold': 1})
        td_left = workbook.add_format({'size': 10,'align': 'left','valign': 'vcenter'})

        float_format = workbook.add_format({'size': 10})
        float_format.set_num_format('0.00')

        greyHeading = workbook.add_format({'bold': 1, 'align': 'left', 'valign': 'vcenter',
            'bg_color': '#A9A9A9', 'border': 1, 'size': 10})
        lightblueHeading = workbook.add_format({'bold': 1, 'align': 'left', 'valign': 'vcenter',
            'bg_color': '#B0C4DE', 'border': 1, 'size': 10})
        topLINE = workbook.add_format({'top': 6})

        if show_value:
            #ADJUST WIDTH OF COLUMNS
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 10)
            worksheet.set_column('D:D', 10)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 10)
            worksheet.set_column('H:H', 10)
            worksheet.set_column('I:I', 10)
            worksheet.set_column('J:J', 10)
            worksheet.set_column('K:K', 10)
    
            worksheet.set_row(0, 30)
    
            #REPORT HEADING
            worksheet.merge_range('A1:K1', title, title_format)
    
            #HEADINGS
            headings = ['Date', 'Reference', 'Origin', 'In-Qty', 'Out-Qty', 
                              'Unit Price', 'Value', 'Remaining Qty', 'Remaining Value',
                              'Balance Qty', 'Balance Value']
    
            row = 3
            col = 0
            for product in product_template.browse(res['product_ids']):
                opening_data = product.with_context(res).get_opening_balance()[0]
                card_data = product.with_context(res).generate_stock_card()
    
                worksheet.write(row, col, 'Product:', lightblueHeading)
                worksheet.write(row, col+1, product.name, lightblueHeading)
                worksheet.write(row+1, col, 'Opening Qty:', td_left_bold)
                worksheet.write(row+1, col+1, opening_data['opening_qty'], float_format)
                worksheet.write(row+2, col, 'Opening Value:', td_left_bold)
                worksheet.write(row+2, col+1, opening_data['opening_value'], float_format)
    
                row += 3
                for h in headings:
                    worksheet.write(row, col, h, greyHeading)
                    col += 1
    
                row += 1
                col = 0
                for element in card_data:
                    worksheet.write(row, col, element['date'], dateFormat)
                    worksheet.write(row, col+1, element['reference'], td_left)
                    worksheet.write(row, col+2, element['origin'], td_left)
                    worksheet.write(row, col+3, element['inqty'], float_format)
                    worksheet.write(row, col+4, element['outqty'], float_format)
                    worksheet.write(row, col+5, element['price_unit'], float_format)
                    worksheet.write(row, col+6, element['value'], float_format)
                    worksheet.write(row, col+7, element['remaining_qty'], float_format)
                    worksheet.write(row, col+8, element['remaining_value'], float_format)
                    worksheet.write(row, col+9, element['balance_qty'], float_format)
                    worksheet.write(row, col+10, element['balance_value'], float_format)
                    row += 1
                    col = 0
                for i in range(0, len(headings)):
                    worksheet.write(row, i, '', topLINE)
    
                row += 3
                col = 0
        else:
            #ADJUST WIDTH OF COLUMNS
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 10)
            worksheet.set_column('D:D', 10)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 10)
    
            worksheet.set_row(0, 30)
    
            #REPORT HEADING
            worksheet.merge_range('A1:G1', title, title_format)
    
            #HEADINGS
            headings = ['Date', 'Reference', 'Origin', 'In-Qty', 'Out-Qty', 
                        'Remaining Qty', 'Balance Qty']

            row = 3
            col = 0
            for product in product_template.browse(res['product_ids']):
                opening_data = product.with_context(res).get_opening_balance()[0]
                card_data = product.with_context(res).generate_stock_card()
    
                worksheet.write(row, col, 'Product:', lightblueHeading)
                worksheet.write(row, col+1, product.name, lightblueHeading)
                worksheet.write(row+1, col, 'Opening Qty:', td_left_bold)
                worksheet.write(row+1, col+1, opening_data['opening_qty'], float_format)
    
                row += 2
                for h in headings:
                    worksheet.write(row, col, h, greyHeading)
                    col += 1
    
                row += 1
                col = 0
                for element in card_data:
                    worksheet.write(row, col, element['date'], dateFormat)
                    worksheet.write(row, col+1, element['reference'], td_left)
                    worksheet.write(row, col+2, element['origin'], td_left)
                    worksheet.write(row, col+3, element['inqty'], float_format)
                    worksheet.write(row, col+4, element['outqty'], float_format)
                    worksheet.write(row, col+5, element['remaining_qty'], float_format)
                    worksheet.write(row, col+6, element['balance_qty'], float_format)
                    row += 1
                    col = 0
                for i in range(0, len(headings)):
                    worksheet.write(row, i, '', topLINE)
    
                row += 3
                col = 0

        workbook.close()

        #FILE UPLOAD
        tf = open('/tmp/%s'%(filename), 'rb')
        buf = tf.read()
        out=base64.encodestring(buf)
        self.write({'excelfile': out, 'file_name': filename, 'excel_flag': True})
        tf.close()
        os.remove('/tmp/%s'%(filename))
        return { 'type': 'ir.actions.act_window', 
                'res_model': 'stock.card', 'view_mode': 'form', 
                'view_type': 'form', 'res_id': self.id, 'target': 'new'}

    @api.multi
    def stock_card_summary_excel(self):
        today = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT).replace(':','').replace(' ','_').replace('-','')
        filename = 'Stock_Card_Summary_%s.xlsx' % (today)
        title = 'Stock Card Summary Report'
        if self.date_from and self.date_to:
            title += ' (%s - %s)'%(self.date_from,self.date_to)
        if self.date_from and not self.date_to:
            title += ' (%s - Till Date)'%(self.date_from)

        workbook = xlsxwriter.Workbook('/tmp/%s'%(filename))
        worksheet = workbook.add_worksheet()

        #FORMATING PROPERTIES
        title_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#99ff66',##A9A9A9
        'underline': 2,
        'border': 1,
        'size': 14})
        total_format = workbook.add_format({'bold': 1, 'bg_color': '#ccccff', 'top': 1,
                                            'underline': 2, 'size': 10})
        total_format.set_num_format('0.00')

        dateFormat = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss',
                                      'size': 10,'align': 'left','valign': 'vcenter'})

        td_left_bold = workbook.add_format({'size': 10,'align': 'left','valign': 'vcenter','bold': 1})
        td_left = workbook.add_format({'size': 10,'align': 'left','valign': 'vcenter'})

        float_format = workbook.add_format({'size': 10})
        float_format.set_num_format('0.00')

        greyHeading = workbook.add_format({'bold': 1, 'align': 'left', 'valign': 'vcenter',
            'bg_color': '#A9A9A9', 'border': 1, 'size': 10})
        lightblueHeading = workbook.add_format({'bold': 1, 'align': 'left', 'valign': 'vcenter',
            'bg_color': '#B0C4DE', 'border': 1, 'size': 10})
        topLINE = workbook.add_format({'top': 6})

        show_value = self.env.user.has_group('rt_stock_card.group_stock_card_qty_values')
        data = self.generate_stock_card_summary()
        if show_value:
            #ADJUST WIDTH OF COLUMNS
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 8)
            worksheet.set_column('D:D', 8)
            worksheet.set_column('E:E', 8)
            worksheet.set_column('F:F', 8)
            worksheet.set_column('G:G', 8)
            worksheet.set_column('H:H', 8)
            worksheet.set_column('I:I', 8)
    
            worksheet.set_row(0, 30)
    
            #REPORT HEADING
            worksheet.merge_range('A1:I1', title, title_format)
    
            #HEADINGS
            headings = ['Product Name', 'Begin-Qty', 'Begin-Value', 
                        'In-Qty', 'In-Value', 'Out-Qty', 'Out-Value', 'End-Qty', 'End-Value']
    
            row = 3
            col = 0
            for h in headings:
                worksheet.write(row, col, h, greyHeading)
                col += 1
    
            row += 1
            col = 0
            for line in data:
                print (line)
                worksheet.write(row, col, line['product_name'], td_left)
                #worksheet.write(row, col+1, line['location'], td_left)
                worksheet.write(row, col+1, line['beginqty'], float_format)
                worksheet.write(row, col+2, line['beginvalue'], float_format)
                worksheet.write(row, col+3, line['inqty'], float_format)
                worksheet.write(row, col+4, line['invalue'], float_format)
                worksheet.write(row, col+5, line['outqty'], float_format)
                worksheet.write(row, col+6, line['outvalue'], float_format)
                worksheet.write(row, col+7, line['endqty'], float_format)
                worksheet.write(row, col+8, line['endvalue'], float_format)
                row += 1
                col = 0
    
            for i in range(0, len(headings)):
                worksheet.write(row, i, '', topLINE)
        else:
            #ADJUST WIDTH OF COLUMNS
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 8)
            worksheet.set_column('D:D', 8)
            worksheet.set_column('E:E', 8)
            worksheet.set_column('F:F', 8)
    
            worksheet.set_row(0, 30)
    
            #REPORT HEADING
            worksheet.merge_range('A1:F1', title, title_format)
    
            #HEADINGS
            headings = ['Product Name', 'Begin-Qty', 'In-Qty', 
                        'Out-Qty', 'End-Qty']
    
            row = 3
            col = 0
            for h in headings:
                worksheet.write(row, col, h, greyHeading)
                col += 1
    
            row += 1
            col = 0
            for line in data:
                worksheet.write(row, col, line['product_name'], td_left)
                #worksheet.write(row, col+1, line['location'], td_left)
                worksheet.write(row, col+1, line['beginqty'], float_format)
                worksheet.write(row, col+2, line['inqty'], float_format)
                worksheet.write(row, col+3, line['outqty'], float_format)
                worksheet.write(row, col+4, line['endqty'], float_format)
                row += 1
                col = 0
    
            for i in range(0, len(headings)):
                worksheet.write(row, i, '', topLINE)

        workbook.close()

        #FILE UPLOAD
        tf = open('/tmp/%s'%(filename), 'rb')
        buf = tf.read()
        out=base64.encodestring(buf)
        self.write({'excelfile': out, 'file_name': filename, 'excel_flag': True})
        tf.close()
        os.remove('/tmp/%s'%(filename))
        return { 'type': 'ir.actions.act_window', 
                'res_model': 'stock.card', 'view_mode': 'form', 
                'view_type': 'form', 'res_id': self.id, 'target': 'new'}
