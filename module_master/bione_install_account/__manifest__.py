# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Accounting Library',
    'category': 'Generic Modules',
    'summary': 'Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'account_billing',
        'account_debitnote',
        'account_cash_invoice',
        'account_credit_control',
        'account_document_reversal',
        'account_due_list',
        'account_due_list_days_overdue',
        'account_export_csv',
        'account_financial_report',
        'account_fiscal_month',
        'account_fiscal_year',
        'account_invoice_refund_link',
        'account_lock_date_update',
        'account_menu_invoice_refund',
        'account_reconcile_rule',
        'account_set_reconcilable',
        'account_cutoff_prepaid',
        'show_invoice_journal_items',
        'float_number_discount',
        # 'cheque_management',
        'account_move_template',
        'account_invoice_view_payment',
        'account_payment_multi_deduction',
        'account_payment_netting',
        'account_payment_show_invoice',
        'account_payment_widget_amount',
        'gts_multiple_invoice_payment',
        'bione_account_payment',
        'currency_rate_inverted',
        'currency_manual_exchange_rate',
        'account_type_menu',
        # 'account_fiscal_year_closing',
        'bi_account_cheque',
        #'fiscal_year_sync_app',
        'multi_write_off_advanced',
        'bi_import_chart_of_accounts',
        'bi_print_journal_entries',

                ],
    'data': [
        # 'views/bo_ir_seq.xml',
    ],
    'installable': True,
    "active": False,
    "description": """

BiOne Library modules
====================================

Contain libary shared for BiOne modules

Change logs:
------------------------------------

* 2020-01-05(1) BO add running seq

""",
}
