{
    'name': 'BiOne_Purchase_Form_tt',
    'version': '12.0.1.0.0',
    'author': 'BiOne',
    'license': 'AGPL-3',
    'website': 'https://bione.co.th',
    'category': 'Report',
    'depends': [
        'web',
        'purchase',
        'bione_purchase',
    ],
    'data': [
        'data/paper_format.xml',
        'data/report_data.xml',
        'reports/purchase_order_form.xml',
        'reports/purchase_style.xml',
    ],
    'installable': True,
}
