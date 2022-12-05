# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PFB Thai Accounting',
    'version': '12.0.2.1',
    'depends': ["account", "account_voucher", "account_cancel",
                "mail", "portal", "sale", "stock", "sale_stock",
                "purchase",
                "sale_management", "hr",
                "hr_expense",
                "board", "contacts",
                "account_cost_center",
                "account_asset_management",
                "l10n_th_asset_register_report",
                "l10n_th_vat_report",
                "product",
                "hr_expense_petty_cash",
                "account_invoice_refund_link",
                # "fin_system",
                ],
    'author': 'wattanadev',
    'category': 'account',
    'description': """
Feature: 
Thai Accounting on odoo 12
    """,
    'website': 'https://www.perfectblending.com',
    'data': [
        'data/wht_data.xml',
        'data/invoice_order_type.xml',
        'data/sequence.xml',
        'views/account_account_view.xml',
        'views/account_move_view.xml',
        'views/account_wht_view.xml',
        'views/account_cheque_view.xml',
        # 'views/account_billing_view.xml',
        'views/account_customer_payment_view.xml',
        'views/account_journal_view.xml',
        'views/res_config_settings_views.xml',
        'views/account_customer_deposit_view.xml',
        'views/account_invoice_view.xml',
        'views/account_supplier_payment_view.xml',
        'views/account_supplier_deposit_view.xml',
        'views/account_supplier_receipts_view.xml',
        'views/menu_report_acc.xml',
        'views/account_report_view.xml',
        'views/account_customer_receipts_view.xml',

        'views/view_invoice_order_type.xml',
        # 'views/account_voucher_views.xml',

        'views/menuitem.xml',
        'views/petty_cash_fund_view.xml',

        'views/res_partner_view.xml',
        'wizard/sale_make_deposit_view.xml',
        'reports/quotation_layout.xml',
        'security/ir.model.access.csv',
        # 'wizard/product_wizard.xml',
        # 'views/hide_menu_account_view.xml',
        # 'views/res_company_view.xml',
        # 'views/res_config_settings_view.xml',
        # 'views/res_currency_view.xml',

        'views/account_cash_move_view.xml',
        'views/account_advance_request_view.xml',
        'views/account_advance_view.xml',
        'views/account_advance_clear_view.xml',
        'views/account_petty_payment_view.xml',
        'views/account_petty_received_view.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
