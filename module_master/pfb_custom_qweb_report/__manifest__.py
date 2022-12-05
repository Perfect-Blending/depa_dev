# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "PFB Custom Qweb Report",
    'summary': "Custom Qweb Report",
    'author': 'PP',
    'website': "",
    'category': 'Base',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base', 'web',
    ],
    'data': [
        'views/assets.xml',
        'views/purchase_order_report_template.xml',
    ],
    'css': [
        'static/css/font_style.css',
    ],
    'installable': True,
}
