# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVmsOrder(TransactionCase):

    def setUp(self):
        super(TestVmsOrder, self).setUp()
        self.operating_unit = self.env.ref(
            'operating_unit.b2b_operating_unit')

    def create_order(self, order_type):
        return self.env['vms.order'].create({
            'operating_unit_id': self.operating_unit.id,
            'supervisor_id': self.env.ref('vms.vms_hr_employee_01').id,
            'type': order_type,
            'program_id': self.env.ref('vms.vms_program_01').id,
            'unit_id': self.env.ref('vms.vms_fleet_vehicle_01').id,
        })

    def test_create(self):
        order = self.create_order('preventive')
        self.assertEqual(order.name, 'O-MTY0001')
        with self.assertRaisesRegexp(
            ValidationError,
                'Verify that the sequences in the base are assigned'):
            self.operating_unit.order_sequence_id = False
            order = self.create_order('preventive')

    def test_default_warehouse_id(self):
        order = self.create_order('preventive')
        self.assertTrue(order.warehouse_id)
