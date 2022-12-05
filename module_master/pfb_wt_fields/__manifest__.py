# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'PFB WT Field',
    'version': '12.0.1.0.1',
    'author': 'PP',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Fields',
    'depends': ['base',
                'web',
                'l10n_th_withholding_tax_cert',
                ],


    'data': [
        'data/sequences.xml',
        'models/wt_fields.xml',

    ],
    'installable': True,
}
