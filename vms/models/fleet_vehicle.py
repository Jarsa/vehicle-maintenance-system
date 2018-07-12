# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from datetime import timedelta
from odoo import _, api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    program_id = fields.Many2one(
        'vms.program',
        string='Maintenance Program')
    distance = fields.Float(
        'Distance Average', required=True,
        compute="_compute_distance_averange",
    )
    supervisor_id = fields.Many2one(
        'hr.employee', 'Supervisor', domain=[('mechanic', '=', True)],)

    @api.model
    def cron_vehicle_maintenance(self):
        order_obj = self.env['vms.order']
        time = fields.Date
        follower = self.env['mail.wizard.invite']
        security_day = int(self.env['ir.config_parameter'].sudo().get_param(
            'security_days'))
        for vehicle in self.search([]):
            if vehicle.program_id:
                for cycle in vehicle.program_id.cycle_ids:
                    days = round((cycle.frequency / vehicle.distance))
                    order = order_obj.search([
                        ('unit_id', '=', vehicle.id),
                        ('state', '=', 'draft')])
                    if not order:
                        new_order = order_obj.create({
                            'operating_unit_id': 1,
                            'unit_id': vehicle.id,
                            'type': 'preventive',
                            'date': time.to_string(
                                time.from_string(time.today()) +
                                timedelta(days=days)),
                            'supervisor_id': vehicle.supervisor_id.id,
                            'state': 'draft',
                            'program_id': vehicle.program_id.id,

                        })
                        new_order.get_tasks_from_cycle(cycle, new_order)
                        if vehicle.supervisor_id.address_home_id.id:
                            mail_invite = follower.with_context({
                                'default_res_model': 'vms.order',
                                'default_res_id': new_order.id
                            }).create({
                                'partner_ids': [(
                                    4, vehicle.supervisor_id.address_home_id.id
                                    )],
                                'send_mail': True,
                            })
                            mail_invite.add_followers()
                        else:
                            msg = (_('The supervisor was not added as '
                                     'a document follower because does '
                                     'not have a home_address assigned'))
                            new_order.message_post(body=msg)
                    else:
                        order_date = (
                            time.from_string(order.date) -
                            time.from_string(time.today()))
                        if security_day == order_date.days:
                            self.env['mail.message'].create({
                                'date': time.today(),
                                'email_from': '',
                                'author_id': self.env.user.id,
                                'record_name': order.name,
                                'model': 'vms.order',
                                'res_id': order.id,
                                'message_type': 'email',
                                'body': 'Mantenimiento pendiente en',
                            })

    @api.multi
    def _compute_distance_averange(self):
        for vehicle in self:
            frequency = int(self.env['ir.config_parameter'].sudo().get_param(
                'day_distance_averange'))
            time = fields.Date
            date_end = time.from_string(time.today())
            date_start = date_end - timedelta(days=frequency)
            odometer = self.env['fleet.vehicle.odometer']
            odometers = odometer.search([
                ('vehicle_id', '=', vehicle.id),
                ('date', '>=', time.to_string(date_start)),
                ('date', '<=', time.to_string(date_end))])
            if odometers:
                distance = sum([x.value for x in odometers]) / frequency
                vehicle.distance = distance
