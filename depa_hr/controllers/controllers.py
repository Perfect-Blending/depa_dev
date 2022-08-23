# -*- coding: utf-8 -*-
from odoo import http

# class DepaHr(http.Controller):
#     @http.route('/depa_hr/depa_hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depa_hr/depa_hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depa_hr.listing', {
#             'root': '/depa_hr/depa_hr',
#             'objects': http.request.env['depa_hr.depa_hr'].search([]),
#         })

#     @http.route('/depa_hr/depa_hr/objects/<model("depa_hr.depa_hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depa_hr.object', {
#             'object': obj
#         })