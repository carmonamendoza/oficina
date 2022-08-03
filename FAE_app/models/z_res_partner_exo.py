# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.tools import float_compare


import logging
from . import fae_utiles


_logger = logging.getLogger(__name__)

class PartnerExoneration(models.Model):
    _name = "xpartner.exoneration"
    _description = 'Exoneration for partner'

    partner_id = fields.Many2one("res.partner", string="Cliente")
    type_exoneration = fields.Many2one("xexo.authorization", string="Tipo Exoneración" )
    exoneration_number = fields.Char(string="Núm.Exoneración", size=40, required=True, )
    institution_name = fields.Char(string="Nombre Institución", size=160,
                                    help='Nombre de la Institución que emitió la exoneración' )
    date_issue = fields.Datetime(string="Fecha Hora Emisión" )
    date_expiration = fields.Datetime(string="Fecha Expiración" )
    # fiscal_position_id = fields.Many2one("account.fiscal.position", string='Fiscal Position')
    exoneration_rate = fields.Float(string="% Exoneración", digits=(5, 2), )
    account_tax_id = fields.Many2one('account.tax', string='Cód.Impuesto', )
    has_cabys = fields.Boolean(string="Posee CAByS", default=False, )
    cabys_list = fields.Char(string="Lista de CAByS")
    active = fields.Boolean(string="Activo", default=True, required=True)

    @api.onchange('exoneration_number')
    def _onchange_exoneration_number(self):
        res = {}
        if self.exoneration_number:
            res = self.action_get_exoneration_data()
        return res

    @api.onchange('account_tax_id')
    def _onchange_account_tax_id(self):
        if self.account_tax_id:
            if float_compare(self.account_tax_id.x_exoneration_rate, self.exoneration_rate, precision_digits=2) != 0:
                raise ValidationError('El porcentaje de la exoneración %s es diferente al configurado  en el impuesto')

    def action_get_exoneration_data(self):
        if not self.exoneration_number:
            return

        json_response = fae_utiles.get_exoneration_info(self.env, self.exoneration_number)
        if json_response["status"] == 200:
            if json_response['identificacion'] != self.partner_id.vat:
                raise ValidationError('La identificación de la exoneración: %s es diferente a la del contacto' % (json_response['identificacion']))
            if not json_response['poseeCabys']:
                raise ValidationError('La exoneración se trata de una exoneración para todos los productos y servicios')

            self.type_exoneration = json_response['exoAuthorization_id']
            self.institution_name = json_response["nombreInstitucion"]
            self.date_issue = json_response['fechaEmision']
            self.date_expiration = json_response['fechaVencimiento']
            self.exoneration_rate = json_response['porcentajeExoneracion']
            self.account_tax_id = json_response["tax_id"]
            self.has_cabys = json_response["poseeCabys"]
            self.cabys_list = json_response["cabys"]

        else:
            return {'warning': {'title': json_response["status"], 'message': json_response["text"]}}
