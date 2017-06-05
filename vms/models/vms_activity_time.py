# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class VmsActivityTime(models.Model):
    _description = 'VMS Time Activities'
    _name = 'vms.activity.time'

    status = fields.Selection(
        [('process', 'Process'),
         ('pause', 'Pause'),
         ('end', 'End')],
        required=True)
    date = fields.Datetime()
    activity_id = fields.Many2one('vms.activity', string='Activity')
