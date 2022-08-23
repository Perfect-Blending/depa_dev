# -*- coding: utf-8 -*-
from odoo import http

# class DepaSignature(http.Controller):
#     @http.route('/depa_signature/depa_signature/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depa_signature/depa_signature/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depa_signature.listing', {
#             'root': '/depa_signature/depa_signature',
#             'objects': http.request.env['depa_signature.depa_signature'].search([]),
#         })

#     @http.route('/depa_signature/depa_signature/objects/<model("depa_signature.depa_signature"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depa_signature.object', {
#             'object': obj
#         })