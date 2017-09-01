# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from datetime import datetime, timedelta

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    program_id = fields.Many2one(
        'vms.program',
        string='Maintenance Program')
    last_order_id = fields.Many2one(
        'vms.order',
        string='Last Order')
    last_cycle_id = fields.Many2one(
        'vms.vehicle.cycle',
        string='Last Cycle')
    next_cycle_id = fields.Many2one(
        'vms.vehicle.cycle',
        string='Next Cycle')
    next_service_date = fields.Datetime(
        compute='_compute_next_service_date'
    )
    next_service_odometer = fields.Float()
    next_service_sequence = fields.Integer()
    cycle_ids = fields.One2many(
        'vms.vehicle.cycle', 'unit_id', string="Cycles")
    sequence = fields.Integer()
    distance = fields.Float(
        'Distance Average', required=True
    )

    @api.multi
    def program_mtto(self):
        for vehicle in self:
            prog_ids = vehicle.cycle_ids.search([('unit_id', '=', vehicle.id)])
            if len(prog_ids):
                prog_ids.unlink()
            seq = 1
            for cycle in vehicle.program_id.cycle_ids:
                for rec in range(cycle.frequency, (
                        4000000 + cycle.frequency), cycle.frequency):
                    vehicle.cycle_ids.create({
                        'cycle_id': cycle.id,
                        'schedule': rec,
                        'sequence': seq,
                        'unit_id': vehicle.id,
                    })
                    seq += 1
            last_schedule = 0.00
            for cycles in vehicle.cycle_ids:
                if last_schedule <= vehicle.odometer <= cycles.schedule:
                    vehicle.sequence = cycles.sequence
                    vehicle.last_cycle_id = cycles.id
                    next_cycle = cycles.search([
                        ('sequence', '=', (cycles.sequence)),
                        ('unit_id', '=', vehicle.id)])
                    vehicle.next_cycle_id = next_cycle.id
                    vehicle.next_service_odometer = next_cycle.schedule
                    return True
                else:
                    last_schedule = cycles.schedule
                    cycles.unlink()

    @api.depends('distance', 'last_cycle_id')
    def _compute_next_service_date(self):
        for vehicle in self:
            if vehicle.last_order_id.id:
                date = datetime.strptime(
                    vehicle.last_cycle_id.date, "%Y-%m-%d %H:%M:%S")
                days = []
                for cycle in vehicle.program_id.cycle_ids:
                    day = (cycle.frequency / vehicle.distance) * 24
                    days.append(day)
                vehicle.next_service_date = (
                    date + timedelta(hours=min(days)))
            else:
                vehicle.next_service_date = False
