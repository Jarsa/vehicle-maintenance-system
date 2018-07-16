# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFleetVehicle(TransactionCase):

    def setUp(self):
        super(TestFleetVehicle, self).setUp()
        self.unit_id = self.env.ref('vms.vms_fleet_vehicle_01')
        self.program = self.env.ref('vms.vms_program_03')
        self.unit_id.program_id = self.program.id
        self.supervisor = self.env.ref('hr.employee_al')
        self.address_home = self.env.ref(
            'base.res_partner_address_3')
        self.supervisor.address_home_id = self.address_home.id
        self.unit_id.supervisor_id = self.supervisor.id
        self.env['fleet.vehicle.odometer'].create({
            'vehicle_id': self.unit_id.id,
            'date': fields.Date.today(),
            'value': 30000,
        })

    def test_compute_distance_averange(self):
        self.unit_id._compute_distance_averange()
        self.assertEqual(self.unit_id.distance, 1000)

    def test_cron_vehicle_maintenance(self):
        self.unit_id._compute_distance_averange()
        self.unit_id.cron_vehicle_maintenance()
        order = self.env['vms.order'].search([])
        self.assertTrue(order)
        security_day = int(self.env['ir.config_parameter'].sudo().get_param(
            'security_days'))
        time = fields.Date
        order.date = time.to_string(
            time.from_string(order.date) + timedelta(days=security_day - 1))
        self.unit_id.cron_vehicle_maintenance()
        mail = self.env['mail.message'].search(
            [('res_id', '=', order.id)])
        self.assertTrue(mail)

    def test_cron_vehicle_maintenance_raise(self):
        self.unit_id._compute_distance_averange()
        self.supervisor.address_home_id = False
        self.unit_id.cron_vehicle_maintenance()
        order = self.env['vms.order'].search([])
        self.assertEqual(len(order.message_ids), 2, 'error in supervisor')
