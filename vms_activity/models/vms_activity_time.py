# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class VmsActivityTime(models.Model):
    _description = 'VMS Time Activities'
    _name = 'vms.activity.time'
    _order = 'start_date desc'

    activity_id = fields.Many2one(
        'vms.activity', string='Activity', required=True)
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    state = fields.Selection([
        ('process', 'Process'),
        ('end', 'End')], required=True)
