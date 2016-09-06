
# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class VmsBase(models.Model):
    _name = 'tms.base'
    _inherit = 'tms.base'
    _description = 'Base'

    order_sequence_id = fields.Many2one(
        'ir.sequence', string='Order Sequence', required=True)
    report_sequence_id = fields.Many2one(
        'ir.sequence', string='Report Sequence', required=True)
