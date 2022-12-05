import re

from odoo import _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # @api.onchange("vat")
    # def _preprocess_vat(self):
    #     if "TH" == self.country_id.code and self.vat:
    #         self.identification_id = re.sub("\\D", "", self.identification_id)

    @api.constrains("vat")
    def _check_vat_id(self):
        for record in self:
            # if record.name != "" and record.vat:
            #     _id = record.vat
            if len(record.vat) != 13:
                raise UserError(_("Vat No of Thai must be 13 digits")
                                )
