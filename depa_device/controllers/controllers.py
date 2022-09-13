# -*- coding: utf-8 -*-
from odoo import http

# class DepaHrLeave(http.Controller):
#     @http.route('/depa_hr_leave/depa_hr_leave/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depa_hr_leave/depa_hr_leave/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depa_hr_leave.listing', {
#             'root': '/depa_hr_leave/depa_hr_leave',
#             'objects': http.request.env['depa_hr_leave.depa_hr_leave'].search([]),
#         })

#     @http.route('/depa_hr_leave/depa_hr_leave/objects/<model("depa_hr_leave.depa_hr_leave"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depa_hr_leave.object', {
#             'object': obj
#         })