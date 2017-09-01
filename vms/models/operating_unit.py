
# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    order_sequence_id = fields.Many2one(
        'ir.sequence', string='Order Sequence')
    report_sequence_id = fields.Many2one(
        'ir.sequence', string='Report Sequence')
