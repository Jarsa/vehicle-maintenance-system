# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsOrder(models.Model):
    _inherit = 'vms.order'

    activity_ids = fields.One2many(
        'vms.activity', 'order_id', string='Activities', ondelete='cascade')
