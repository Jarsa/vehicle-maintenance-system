# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestVmsOrderLine(TransactionCase):

    def setUp(self):
        super(TestVmsOrderLine, self).setUp()
        self.product = self.env.ref('vms.product_product_vms_02')
        self.task = self.env.ref('vms.vms_task_01')
        self.operating_unit = self.env.ref(
            'operating_unit.b2b_operating_unit')
        self.unit_id = self.env.ref('vms.vms_fleet_vehicle_01')

    def create_order(self, order_type):
        order = self.env['vms.order'].create({
            'operating_unit_id': self.operating_unit.id,
            'supervisor_id': self.env.ref('vms.vms_hr_employee_01').id,
            'type': order_type,
            'program_id': self.env.ref('vms.vms_program_01').id,
            'unit_id': self.unit_id.id,
        })
        duration = self.task.duration
        start_date = fields.Datetime.from_string(fields.Datetime.now())
        spares = []
        for spare_part in self.task.spare_part_ids:
            spares.append((0, False, {
                'product_id': spare_part.product_id.id,
                'product_qty': spare_part.product_qty,
                'product_uom_id': (
                    spare_part.product_uom_id.id)
            }))
        order.order_line_ids.create({
            'task_id': self.task.id,
            'start_date': start_date,
            'duration': duration,
            'spare_part_ids': [line for line in spares],
            'order_id': order.id
        })
        return order

    def test_unlink(self):
        order = self.create_order('preventive')
        order.order_line_ids.unlink()
        self.assertFalse(order.order_line_ids)

    def test_onchange_external(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        order_line._onchange_external()
        self.assertTrue(order_line.spare_part_ids)
        order.order_line_ids.write({
            'external': True,
        })
        order_line._onchange_external()
        self.assertFalse(order_line.spare_part_ids)
