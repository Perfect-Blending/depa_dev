# -*- coding: utf-8 -*-
from odoo import http

# class DepaHrInherit(http.Controller):
#     @http.route('/depa_hr_inherit/depa_hr_inherit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depa_hr_inherit/depa_hr_inherit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depa_hr_inherit.listing', {
#             'root': '/depa_hr_inherit/depa_hr_inherit',
#             'objects': http.request.env['depa_hr_inherit.depa_hr_inherit'].search([]),
#         })

#     @http.route('/depa_hr_inherit/depa_hr_inherit/objects/<model("depa_hr_inherit.depa_hr_inherit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depa_hr_inherit.object', {
#             'object': obj
#         })