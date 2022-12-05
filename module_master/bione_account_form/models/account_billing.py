from odoo import models, api


class AccountBilling(models.Model):
    _inherit = 'account.billing'

    @api.multi
    def remove_menu_print(self, res, reports):
        # Remove reports menu
        for report in reports:
            reports = self.env.ref(report, raise_if_not_found=False)
            for rec in res.get('toolbar', {}).get('print', []):
                if rec.get('id', False) in reports.ids:
                    del res['toolbar']['print'][
                        res.get('toolbar', {}).get('print').index(rec)]
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        hide_reports_base = [
            'account_billing.report_account_billing',
        ]
        hide_reports_vendor = [
            'bione_account_form.bione_billing_form_pdf_report',
        ]
        hide_reports_customer = [
            'bione_account_form.bione_payment_request_form_pdf_report',
        ]
        type = self._context.get('bill_type')
        res = super(AccountBilling, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if res and view_type in ['tree', 'form']:
            # del menu report customer and vendor
            self.remove_menu_print(res, hide_reports_base)
            # del menu report vendor
            if type and type not in ['out_invoice']:
                self.remove_menu_print(res, hide_reports_vendor)
            # del menu report customer
            if type and type not in ['in_invoice']:
                self.remove_menu_print(res, hide_reports_customer)
        return res
