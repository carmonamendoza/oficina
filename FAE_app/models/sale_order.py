
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import pytz

import logging


_logger = logging.getLogger(__name__)


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    x_economic_activity_id = fields.Many2one("xeconomic.activity", string="Actividad Económica", required=False,
                                             context={'active_test': True}, )

    def _prepare_invoice(self):
        vals = super(SaleOrderInherit, self)._prepare_invoice()
        if vals:
            if self.partner_id.x_foreign_partner:
                document_type = 'FEE'
            elif self.partner_id.vat:
                if ((self.partner_id.country_id and self.partner_id.country_id.code != 'CR')
                    or (self.partner_id.x_identification_type_id and self.partner_id.x_identification_type_id.code == '05')):
                    document_type = 'TE'
                else:
                    document_type = 'FE'
            else:
                document_type = 'TE'
            vals['x_economic_activity_id'] = self.x_economic_activity_id
            vals['x_document_type'] = document_type
        return vals 

    @api.onchange('partner_id', 'company_id')
    def _get_economic_activities(self):
        for rec in self:
            rec.x_economic_activity_id = rec.company_id.x_economic_activity_id

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_exoneration_id = fields.Many2one("xpartner.exoneration", string="Exoneración", required=False, )

    def _compute_tax_id(self):
        res = super(SaleOrderLine, self)._compute_tax_id()
        order = self.order_id
        if order.partner_id.x_special_tax_type == 'E' and order.partner_id.x_exo_modality == 'M':
            for line in self:
                if line.product_id.x_cabys_code_id:
                    cabys_code = line.product_id.x_cabys_code_id.code
                    for exo_line in order.partner_id.x_exoneration_lines:
                        if exo_line.active and exo_line.date_expiration and \
                                exo_line.date_expiration > line.order_id.date_order and exo_line.account_tax_id:
                            cabys_list = exo_line.cabys_list
                            if cabys_code in cabys_list:
                                line.tax_id = exo_line.account_tax_id
                                line.x_exoneration_id = exo_line.id
        return res