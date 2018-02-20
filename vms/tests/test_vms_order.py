# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVmsOrder(TransactionCase):

    def setUp(self):
        super(TestVmsOrder, self).setUp()
        self.operating_unit = self.env.ref(
            'operating_unit.b2b_operating_unit')
        self.unit_id = self.env.ref('vms.vms_fleet_vehicle_01')
        self.program = self.env.ref('vms.vms_program_03')
        self.task = self.env.ref('vms.vms_task_01')
        self.report = self.env['vms.report'].create({
            'operating_unit_id': self.operating_unit.id,
            'unit_id': self.unit_id.id,
            'employee_id': self.env.ref('hr.employee_al').id
        })
        self.service_product = self.env.ref(
            'product.service_delivery_product_template')

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

    def order_with_reports(self):
        wizard = self.env['vms.wizard.maintenance.order'].with_context({
            'active_model': 'vms.report',
            'active_ids': [self.report.id]}).create({})
        wizard.make_orders()
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
        self.report.order_id.order_line_ids.create({
            'task_id': self.task.id,
            'start_date': start_date,
            'duration': duration,
            'spare_part_ids': [line for line in spares],
            'order_id': self.report.order_id.id
        })
        return self.report.order_id

    def test_create(self):
        order = self.create_order('preventive')
        self.assertEqual(order.name, 'O-GDL0001')
        with self.assertRaisesRegexp(
            ValidationError,
                'Verify that the sequences in the base are assigned'):
            self.operating_unit.order_sequence_id = False
            order = self.create_order('preventive')

    def test_default_warehouse_id(self):
        order = self.create_order('preventive')
        self.assertTrue(order.warehouse_id)

    def test_onchange_type(self):
        order = self.create_order('preventive')
        order.type = 'corrective'
        order._onchange_type()
        self.assertFalse(order.program_id)
        self.assertFalse(order.current_odometer)
        self.assertFalse(order.order_line_ids)
        self.unit_id.program_id = self.program.id
        self.unit_id.odometer = 100
        order.type = 'preventive'
        order._onchange_type()
        self.assertEqual(order.program_id, self.program)
        self.assertEqual(order.current_odometer, 100)
        self.assertTrue(order.order_line_ids)

    def test_compute_end_date(self):
        order = self.create_order('preventive')
        order._compute_end_date()
        end_date = fields.Datetime.to_string(
            fields.Datetime.from_string(
                order.start_date) + timedelta(hours=self.task.duration))
        self.assertEqual(order.end_date, end_date)

    def test_compute_end_date_real(self):
        order = self.create_order('preventive')
        order.action_open()
        order.order_line_ids.action_done()
        order._compute_end_date_real()
        end_date_real = fields.Datetime.to_string(
            fields.Datetime.from_string(
                order.start_date_real) + timedelta(
                hours=order.order_line_ids.real_duration))
        self.assertEqual(order.end_date_real, end_date_real)

    def test_action_open(self):
        order_one = self.create_order('preventive')
        with self.assertRaisesRegexp(
            ValidationError,
                'Unit not available for maintenance because it has more '
                'open order.'):
            order_one.action_open()
            order_two = self.create_order('preventive')
            order_two.action_open()
        with self.assertRaisesRegexp(
            ValidationError,
                'The order must have at least one task.'):
            order_one.order_line_ids = False
            order_one.action_open()

    def test_action_open_report(self):
        order_report = self.order_with_reports()
        order_report.order_line_ids.spare_part_ids.create({
            'product_id': self.service_product.id,
            'product_qty': 2.0,
            'product_uom_id': self.service_product.uom_id.id,
            'order_line_id': order_report.order_line_ids.id,
        })
        order_report.action_open()
        self.assertEqual(order_report.report_ids.state, 'pending')

    def test_action_cancel(self):
        order = self.order_with_reports()
        order.action_open()
        order.action_cancel()
        self.assertEqual(order.report_ids.state, 'pending')
        self.assertEqual(order.state, 'cancel')

    def test_action_cancel_draft(self):
        order = self.order_with_reports()
        order.action_open()
        order.action_cancel()
        order.action_cancel_draft()
        self.assertEqual(order.report_ids.state, 'pending')
        self.assertEqual(order.state, 'draft')

    def test_action_released(self):
        order = self.order_with_reports()
        order.action_released()
        self.assertEqual(order.report_ids.state, 'closed')
        self.assertEqual(order.state, 'released')

    def test_order_pickings(self):
        order = self.create_order('preventive')
        order.action_open()
        order._compute_picking_ids()
        self.assertTrue(order.picking_ids)
        order._compute_pickings_count()
        self.assertEqual(order.pickings_count, 1)
        picking_action = order.action_view_pickings()
        self.assertTrue(picking_action)
        order.action_cancel()
        order.action_cancel_draft()
        order.action_open()
        picking_action = order.action_view_pickings()
        self.assertTrue(picking_action)
