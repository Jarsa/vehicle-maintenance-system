# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _description = "Vehicle"
    _order = 'name asc'

    program_id = fields.Many2one(
        'vms.program',
        string='Maintenance Program')
    last_order_id = fields.Many2one(
        'vms.order',
        string='Last Clycle')
    next_cycle_id = fields.Many2one(
        'vms.cycle',
        string='Next Cycle')
    next_service_date = fields.Datetime()
    next_service_odometer = fields.Float()
    next_service_sequence = fields.Integer()
    cycle_ids = fields.One2many('vms.vehicle.cycle', 'unit_id')
