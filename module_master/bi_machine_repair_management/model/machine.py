# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, SUPERUSER_ID,  _

class MachineRepairTeams(models.Model):
    _name = 'machine.repair.team'
    
    name = fields.Char(string="Name")
    leader_id = fields.Many2one('res.users',string='Leader')
    is_default_team = fields.Boolean(string='Is Default Team',default=False)
    team_member_ids = fields.Many2many('res.users','res_user_rel','machine_team_id','user_id',string="Team Member")
    
class MachineServices(models.Model):
    _name = 'machine.services'    
    
    name = fields.Char(string='Machine Service')
    
class MachineServiceType(models.Model):
    _name = 'machine.service.type'

    @api.onchange('product_id')
    def _change_cost(self):
        self.cost = self.product_id.lst_price
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    product_id = fields.Many2one('product.product',string='Product',required=True)
    cost = fields.Float(string='Cost')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'    
    
    is_machine = fields.Boolean(string='Machine',default=False)
    is_machine_parts = fields.Boolean(string='Machine Parts',default=False)  

class ProductTemplate(models.Model):
    _inherit = 'product.template'    
    
    is_machine = fields.Boolean(string='Machine',default=False)
    is_machine_parts = fields.Boolean(string='Machine Parts',default=False)    
    
class MachineRepair(models.Model):      
    _name = 'machine.repair'
    _inherit = ['mail.thread', 'portal.mixin']
    _rec_name = 'sequence'
    
    name = fields.Char(string='Name', required=True)
    sequence = fields.Char(string='Sequence', readonly=True)
    technician_id = fields.Many2one('res.users', string='Technician')
    partner_id = fields.Many2one('res.partner', string='Customer')
    client_email = fields.Char(string='Email')
    client_phone = fields.Char(string='Phone')
    company_id = fields.Many2one('res.company', string='Company')
    project_id = fields.Many2one('project.project', string='Project')
    analytic_account_id = fields.Many2one('account.analytic.line', string='Analytic Account')
    machine_repair_team_id = fields.Many2one('machine.repair.team',string='Machine Repair Team')
    team_leader_id = fields.Many2one('res.users', string='Team Leader')
    #machine_service_type_id = fields.Many2one('machine.service.type',string='Department')
    priority = fields.Selection([('0',False),('1','Low'),('2','Normal'),('3','High')],string='Priority')
    repair_request_date = fields.Datetime(string='Repair Request Date',default=datetime.now())
    close_date = fields.Datetime(string='Close Date')
    is_repaired = fields.Boolean(string='Is Repaired',default=False)
    repairing_duration = fields.Float(string='Repairing Duration',default=0.0)
    # machine_category_id = fields.Many2one('product.category',string='Machine Category')
    is_warranty = fields.Boolean(string='Warranty',default=False)
    product_id = fields.Many2one('product.product',string='Machine')
    brand = fields.Char(string='Brand')
    model = fields.Char(string='Model')
    color = fields.Char(string='Color')
    year = fields.Char(string='Year')
    damage = fields.Text(string='Damage')
    accompanying_item = fields.Text(string='Accompanying Items')
    machine_brand = fields.Char(string='Machine Brand')
    machine_model = fields.Char(string='Machine Model')
    machine_manufacturing_year = fields.Char(string='Machine Manufacturing Year')
    description = fields.Text(string='Description')
    stage = fields.Selection([('new','New'),('assigned','Assigned'),('work_in_progress','Work In Progress'),('needs_reply','Needs Reply'),('reopen','Reopened'),('solution_suggested','Solution Suggested'),('closed','Closed')],string="Stage" ,default="new", index=True)#,('need_more_info','Needs More Info')
    is_ticket_closed = fields.Boolean(string="Is Ticket Closed")
    timesheet_ids = fields.One2many('account.analytic.line','machine_repair_timesheet_id',String="Timesheet")
    machine_services_id = fields.Many2one('machine.services',string="Machine Services")
    machine_service_type_id = fields.Many2many('machine.service.type',string="Repair Type")
    problem = fields.Text(string="Problem")
    # lot_id = fields.Many2one('stock.production.lot',string="Lot")
    machine_consume_ids = fields.One2many('machine.repair.estimate','product_consume_id',string="Product Consume Parts")
    machine_diagnosys_count = fields.Integer('Machine Diagnosis', compute='_get_machine_diagnosys_count')
    machine_workorder_count = fields.Integer('Machine Work Order', compute='_get_machine_workorder_count')
    images_ids = fields.One2many('ir.attachment','machine_repair_id','Images')
    customer_rating = fields.Selection([('0','False'),('1','Poor'), ('2','Average'), ('3','Good'),('4','Excellent')], 'Customer Rating')
    comment = fields.Text(string="Comment")
    attachment_count  =  fields.Integer('Attachments', compute='_get_attachment_count')

    machine_orders_count = fields.Integer('Machine Orders', compute='_get_machine_orders_count')
    machine_orders_ids = fields.One2many('sale.order','machine_repair_id','Quotations')
    
    
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = {}
        if not self.partner_id:
            return res
        self.client_email = self.partner_id.email
        self.client_phone = self.partner_id.phone
        
    
    def _get_machine_diagnosys_count(self):
        for diagnosys in self:
            diagnosys_ids = self.env['machine.diagnosys'].search([('machine_repair_id','=',diagnosys.id)])
            diagnosys.machine_diagnosys_count = len(diagnosys_ids)
            
    
    def machine_diagnosys_button(self):
        self.ensure_one()
        return {
            'name': 'Machine Diagnosis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'machine.diagnosys',
            'domain': [('machine_repair_id', '=', self.id)],
        }

    
    def _get_machine_orders_count(self):
        for order in self:
            order_ids = self.env['sale.order'].search([('machine_repair_id','=',order.id)])
            order.machine_orders_count = len(order_ids)
            
    
    def machine_orders_button(self):
        self.ensure_one()
        return {
            'name': 'Quotaions',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('machine_repair_id', '=', self.id)],
        }
        
    
    def _get_machine_workorder_count(self):
        for workorder in self:
            workorder_ids = self.env['machine.workorder'].search([('machine_repair_id','=',workorder.id)])
            workorder.machine_workorder_count = len(workorder_ids)
            
    
    def machine_workorder_button(self):
        self.ensure_one()
        return {
            'name': 'Machine Workorder',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'machine.workorder',
            'domain': [('machine_repair_id', '=', self.id)],
        }        
        
    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('machine.repair.seq') or 'RO-000'
        result = super(MachineRepair, self).create(vals)
        return result

    
    def set_to_close(self):
        res = self.write({'stage':'closed','is_ticket_closed':True,'close_date':datetime.now(),'is_repaired':True})
        super_user = self.env['res.users'].browse(self.env.uid)
        su_id = self.env['res.users'].browse(self.env.uid).partner_id
        if not self.partner_id.email:
            raise UserError(_('%s customer has no email id please enter email address')
                    % (self.partner_id.name)) 
        else:
            template_id = self.env['ir.model.data'].get_object_reference(
                                                  'bi_machine_repair_management',
                                                  'email_template_machine_repair')[1]
            
            email_template_obj = self.env['mail.template'].browse(template_id)
            
            if template_id:
                values = email_template_obj.generate_email(self.id, fields=None)
                values['email_from'] = super_user.email
                values['email_to'] = self.partner_id.email 
                # values['res_id'] = False
                values['author_id']=su_id.id
                mail_mail_obj = self.env['mail.mail']
                #request.env.uid = 1
                msg_id = mail_mail_obj.sudo().create(values)
                if msg_id:
                    mail_mail_obj.send([msg_id])
        return res 
        
    
    def create_machine_diagnosys(self):
        diagnosis_obj = self.env['machine.diagnosys']
        list_of_timesheet = []
        list_of_consumed_product = []
        machine_repair_obj = self.env['machine.repair'].browse(self.ids[0])
        
        for timesheet in machine_repair_obj.timesheet_ids:
            list_of_timesheet.append(timesheet.id) 
            
        for machine_consume in machine_repair_obj.machine_consume_ids:
            list_of_consumed_product.append(machine_consume.id)             

        diagnosys_name = machine_repair_obj.name + " (" + machine_repair_obj.sequence + ")"
        vals = {
                'name' : diagnosys_name,
                'priority': machine_repair_obj.priority,
                'product_id': machine_repair_obj.product_id.id,
                'project_id' : machine_repair_obj.project_id.id,
                'assigned_to' : machine_repair_obj.technician_id.id,
                'description' : machine_repair_obj.accompanying_item,
                'machine_repair_id' : machine_repair_obj.id,
                'timesheet_ids' : [(6,0,list_of_timesheet)],
                'machine_repair_estimation_ids' : [(6,0,list_of_consumed_product)],
                'partner_id' : machine_repair_obj.partner_id.id,
                # 'type_id' : machine_repair_obj.machine_service_type_id.id or False,
                'initially_planned_hour' : machine_repair_obj.repairing_duration,
        }
        diagnosys_id = self.env['machine.diagnosys'].create(vals)
        return True 

    
    def create_machine_workorder(self):
        workorder_obj = self.env['machine.workorder']
        list_of_timesheet = []
        list_of_consumed_product = []
        machine_repair_obj = self.env['machine.repair'].browse(self.ids[0])
        
        for timesheet in machine_repair_obj.timesheet_ids:
            list_of_timesheet.append(timesheet.id) 
            
        workorder_name = machine_repair_obj.name + " (" + machine_repair_obj.sequence + ")"
        vals = {
                'name' : workorder_name,
                'priority': machine_repair_obj.priority,
                'product_id': machine_repair_obj.product_id.id,
                'project_id' : machine_repair_obj.project_id.id,
                'assigned_to' : machine_repair_obj.technician_id.id,
                'description' : machine_repair_obj.accompanying_item,
                'machine_repair_id' : machine_repair_obj.id,
                'workorder_timesheet_ids' : [(6,0,list_of_timesheet)],
                'partner_id' : machine_repair_obj.partner_id.id,
                # 'type_id' : machine_repair_obj.machine_service_type_id.id or False,
                'initially_planned_hour' : machine_repair_obj.repairing_duration,
        }
        workorder_id = self.env['machine.workorder'].create(vals)
        return True

    
    def _get_attachment_count(self):
        for machine in self:
            attachment_ids = self.env['ir.attachment'].search([('machine_repair_id','=',machine.id)])
            machine.attachment_count = len(attachment_ids)
        
    
    def attachment_on_machine_repair_button(self):
        self.ensure_one()
        return {
            'name': 'Attachment.Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('machine_repair_id', '=', self.id)],
        }

class MachineDiagnosys(models.Model):      
    _name = 'machine.diagnosys'
    
    name = fields.Char(string="Name")
    project_id = fields.Many2one('project.project',string="Project")
    assigned_to = fields.Many2one('res.users',string="Assigned To")
    initially_planned_hour = fields.Float(string="Initially Planned Hour",default=0.0)
    deadline_date = fields.Datetime(string="Deadline")
    tag_ids = fields.Many2one('project.tags',string="Tags")
    description = fields.Text(string="Description")
    timesheet_ids = fields.One2many('account.analytic.line','timesheet_id',String="Timesheet")
    machine_repair_estimation_ids = fields.One2many('machine.repair.estimate','diagnosys_id',string="Machine Repair Estimation")
    hours_spent = fields.Float(compute='_get_total_hours',string="Hours Spent",defalut=0.0)
    remaining_hours = fields.Float(compute='_get_total_hours',string="Remaining Hours",defalut=0.0)
    partner_id = fields.Many2one('res.partner',string="Customer")
    machine_repair_id = fields.Many2one('machine.repair',string="Machine Repair")
    type_id = fields.Many2one('machine.service.type',string="Type")
    quotation_count = fields.Float(compute='_get_quotation_count',string="Quotation")
    active = fields.Boolean(default=True)
    priority = fields.Selection([('0',False),('1','Low'),('2','Normal'),('3','High')],string='Priority')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
    product_id = fields.Many2one('product.product',string="Machine")
    picking_count = fields.Float(compute='_get_picking_count',string="Picking")

    
    def picking_button(self):
        self.ensure_one()
        return {
            'name': 'Consume Parts Picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name)],
        }

    
    def _get_picking_count(self):
        for picking in self:
            picking_ids = self.env['stock.picking'].search([('origin', '=', self.name)])
            picking.picking_count = len(picking_ids)

    
    def consume_car_parts(self):
        setting = self.env['res.config.settings'].search([],order="id desc",limit=1)

        if setting.consume_parts:
            picking_type_id = self.env['stock.picking.type'].search([['code','=','internal'],['warehouse_id.company_id','=',self.env.user.company_id.id]],limit=1)
            if not picking_type_id:

                warehouse = self.env['stock.warehouse'].search([('company_id', '=',self.env.user.company_id.id)], limit=1)

                picking_type_id = self.env['stock.picking.type'].create({
                    'name' : 'Consume Parts',
                    'code' : 'internal',
                    'sequence_id' : self.env['ir.sequence'].search([['prefix','like',warehouse.code]],limit=1).id,
                    'warehouse_id' : warehouse.id or False,
                    'company_id' : self.env.user.company_id.id,
                    'default_location_src_id': setting.location_id.id,
                    'default_location_dest_id' : setting.location_dest_id.id,
                    })

            picking = self.env['stock.picking'].create({
                    'partner_id' : self.assigned_to.partner_id.id, 
                    'picking_type_id' : picking_type_id.id,
                    'picking_type_code': 'internal',
                    'location_id' : setting.location_id.id,
                    'location_dest_id' : setting.location_dest_id.id,
                    'origin': self.name,
                    })
            for estitmate in self.machine_repair_estimation_ids:
                move = self.env['stock.move'].create({
                    'picking_id': picking.id,
                    'name': estitmate.product_id.name,
                    'product_uom' : estitmate.product_id.uom_id.id,
                    'product_id': estitmate.product_id.id,
                    'product_uom_qty' : estitmate.quantity,
                    'location_id' : setting.location_id.id,
                    'location_dest_id' : setting.location_dest_id.id,
                    'origin': self.name,
                    })
        else:
            raise Warning(_("Please select the Consume Parts option in Inventory Settings to consume Machine Parts"))


    
    def _get_quotation_count(self):
        for quotation in self:
            quotation_ids = self.env['sale.order'].search([('diagnose_id','=',quotation.id)])
            quotation.quotation_count = len(quotation_ids)
            
    
    def quotation_button(self):
        self.ensure_one()
        return {
            'name': 'Diagnosis Quotataion',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('diagnose_id', '=', self.id)],
        }
        
    
    def _get_total_hours(self):
        spent_hours = 0.0
        rem_hours = 0.0
        
        for hours in self.timesheet_ids:
            spent_hours += hours.unit_amount
            
        rem_hours = self.initially_planned_hour - spent_hours
        
        self.hours_spent = spent_hours
        self.remaining_hours = rem_hours
        
    
    def create_quotation(self):

        diagnose_obj = self.env['machine.diagnosys'].browse(self.ids[0])
        machine_repair_obj = self.env['machine.repair']
        product_obj = self.env['product.product']
        
        sale_order_vals = {
                'partner_id': diagnose_obj.partner_id.id or False,
                'state': 'draft',
                'date_order' : datetime.now(),
                'user_id' : diagnose_obj.assigned_to.id,
                'client_order_ref': diagnose_obj.name,
                'diagnose_id': diagnose_obj.id,
                'machine_repair_id': diagnose_obj.machine_repair_id.id,
                #'state' : 'draft',
                }
        sale_order_id = self.env['sale.order'].create(sale_order_vals)                
        
        for machine_line in diagnose_obj.timesheet_ids:
            sale_order_line_vals = {
                                'product_id':machine_line.machine_service_id.product_id.id,
                                'name': machine_line.name,
                                'price_unit' : machine_line.total_cost,
                                'order_id': sale_order_id.id,                              
                            }
            sale_order_line_id = self.env['sale.order.line'].create(sale_order_line_vals)

        for machine_estimate in diagnose_obj.machine_repair_estimation_ids:
            sale_order_line_estimate = {
                                'product_id': machine_estimate.product_id.id,
                                'name': machine_estimate.product_id.name,
                                'product_uom_qty': machine_estimate.quantity,
                                'product_uom': machine_estimate.product_id.uom_id.id,
                                'price_unit' : machine_estimate.price,
                                'order_id': sale_order_id.id,
                            }
            sale_order_line_ids = self.env['sale.order.line'].create(sale_order_line_estimate)
                      
    
class MachineRepairEstimate(models.Model):      
    _name = 'machine.repair.estimate'    

    diagnosys_id = fields.Many2one('machine.diagnosys',string="Machine Repair Estimate") 
    product_consume_id = fields.Many2one('machine.repair',string="Product Consume")       
    product_id = fields.Many2one('product.product',string="Product")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom',string="Unit Of Measure")
    price = fields.Float(string="Price")
    notes = fields.Char(string="Notes")
    
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        self.price = self.product_id.list_price
        self.uom_id =self.product_id.uom_id

class MachineWorkOrder(models.Model):      
    _name = 'machine.workorder'
    
    name = fields.Char(string="Name")
    project_id = fields.Many2one('project.project',string="Project")
    assigned_to = fields.Many2one('res.users',string="Assigned To")
    initially_planned_hour = fields.Float(string="Initially Planned Hour",default=0.0)
    deadline_date = fields.Datetime(string="Deadline")
    tag_ids = fields.Many2one('project.tags',string="Tags")
    description = fields.Text(string="Description")
    workorder_timesheet_ids = fields.One2many('account.analytic.line','timesheet_workorder_id',String="Timesheet")
    machine_repair_estimation_ids = fields.One2many('machine.repair.estimate','diagnosys_id',string="Machine Repair Estimation")
    hours_spent = fields.Float(compute='_get_total_hours',string="Hours Spent",defalut=0.0)
    remaining_hours = fields.Float(compute='_get_total_hours',string="Remaining Hours",defalut=0.0)
    partner_id = fields.Many2one('res.partner',string="Customer")
    machine_repair_id = fields.Many2one('machine.repair',string="Machine Repair")
    type_id = fields.Many2one('machine.service.type',string="Type")
    active = fields.Boolean(default=True)
    priority = fields.Selection([('0',False),('1','Low'),('2','Normal'),('3','High')],string='Priority')
    product_id = fields.Many2one('product.product',string="Machine")
    
    
    def _get_total_hours(self):
        spent_hours = 0.0
        rem_hours = 0.0
        
        for hours in self.workorder_timesheet_ids:
            spent_hours += hours.unit_amount
            
        rem_hours = self.initially_planned_hour - spent_hours
        
        self.hours_spent = spent_hours
        self.remaining_hours = rem_hours
        return True 
        
class AccountAnalyticLine(models.Model):      
    _inherit = 'account.analytic.line'
    
    timesheet_id = fields.Many2one('machine.diagnosys',string="Machine Timesheet")
    machine_repair_timesheet_id = fields.Many2one('machine.repair',string="Machine Repair Timesheet")
    project_id = fields.Many2one('project.project', string='Project',domain=[('allow_timesheets','=',True)])
    machine_service_id = fields.Many2one('machine.service.type', string="Service Type")
    total_cost = fields.Float('Cost',compute='_change_total_cost')
    timesheet_workorder_id = fields.Many2one('machine.workorder')

    @api.model
    def create(self,values):
        result = super(AccountAnalyticLine, self).create(values)
        machine_repair_id = values.get('machine_repair_timesheet_id')
        timesheet_id = values.get('timesheet_id') or self.env['machine.diagnosys'].search([['machine_repair_id','=',machine_repair_id]],limit=1).id
        machine_workorder_id = values.get('timesheet_workorder_id') or self.env['machine.workorder'].search([['machine_repair_id','=',machine_repair_id]],limit=1).id

        if machine_repair_id:
            timesheets = self.env['account.analytic.line'].search([['machine_repair_timesheet_id','=',values.get('machine_repair_timesheet_id')]])
            if timesheet_id:
                timesheets.write({'timesheet_id':timesheet_id})
            if machine_workorder_id:
                timesheets.write({'timesheet_workorder_id':machine_workorder_id})
        return result

    def _change_total_cost(self):
        for order in self:
            order.total_cost = order.unit_amount*order.machine_service_id.cost

    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    diagnose_id = fields.Many2one('machine.diagnose', string='Machine Diagnosis')

    machine_repair_count = fields.Integer('Machine Repair', compute='_get_machine_repair_count')
    machine_repair_id = fields.Many2one('machine.repair', string='Machine Repair')

    
    def _get_machine_repair_count(self):
        for repair in self:
            repair_ids = self.env['machine.repair'].search([('id','=',self.machine_repair_id.id)])
            repair.machine_repair_count = len(repair_ids)

    
    def machine_repair_button(self):
        self.ensure_one()
        return {
            'name': 'Machine Repair',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'machine.repair',
            'domain': [('id', '=', self.machine_repair_id.id)],
        }


class ir_attachment(models.Model):
    _inherit='ir.attachment'

    machine_repair_id  =  fields.Many2one('machine.repair', 'Machine Repair')    

class Website(models.Model):

    _inherit = "website"
    
    def get_machine_repair_services_list(self):            
        machine_services_ids=self.env['machine.services'].sudo().search([])
        return machine_services_ids

    def get_machine_list(self):            
        machine_ids=self.env['product.product'].sudo().search([('is_machine', '=', 1)])
        return machine_ids
        

