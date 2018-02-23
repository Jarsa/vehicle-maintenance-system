# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVmsActivity(TransactionCase):

    def setUp(self):
        super(TestVmsActivity, self).setUp()
        self.operating_unit = self.env.ref(
            'operating_unit.b2b_operating_unit')
        self.unit_id = self.env.ref('vms.vms_fleet_vehicle_01')
        self.program = self.env.ref('vms.vms_program_01')
        self.task = self.env.ref('vms.vms_task_01')
        self.supervisor = self.env.ref('vms.vms_hr_employee_01')
        self.mechanic = self.env.ref('vms.vms_hr_employee_02')

    def create_order(self):
        order = self.env['vms.order'].create({
            'operating_unit_id': self.operating_unit.id,
            'supervisor_id': self.supervisor.id,
            'type': 'preventive',
            'program_id': self.program.id,
            'unit_id': self.unit_id.id,
        })
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
            'start_date': fields.Datetime.from_string(fields.Datetime.now()),
            'duration': self.task.duration,
            'spare_part_ids': [line for line in spares],
            'order_id': order.id
        })
        return order

    def activity(self):
        order = self.create_order()
        order.order_line_ids.responsible_ids += self.mechanic
        order.action_open()
        task = order.activity_ids
        return task

    def test_action_start(self):
        activity = self.activity()
        activity.action_start()
        self.assertEqual(activity.state, 'process')
        self.assertTrue(activity.start_date)

    def test_action_pause(self):
        activity = self.activity()
        activity.action_start()
        activity.action_pause()
        self.assertEqual(activity.state, 'pause')

    def test_action_resume(self):
        activity = self.activity()
        activity.action_start()
        activity.action_pause()
        activity.action_resume()
        self.assertEqual(activity.state, 'process')

    def test_action_end(self):
        activity = self.activity()
        activity.action_start()
        activity.action_pause()
        activity.action_resume()
        activity.action_end()
        self.assertEqual(activity.state, 'end')
        self.assertTrue(activity.end_date)

    def test_action_cancel(self):
        activity = self.activity()
        activity.action_start()
        activity.action_cancel()
        self.assertEqual(activity.state, 'cancel')

    def test_action_draft(self):
        activity = self.activity()
        activity.action_start()
        activity.action_cancel()
        activity.action_draft()
        self.assertEqual(activity.state, 'draft')

    def test_start_resume_activity_time(self):
        activity = self.activity()
        activity.action_start()
        with self.assertRaisesRegexp(
            ValidationError,
                'The activity must be in Pending, Process or Pause'):
            activity.action_cancel()
            activity.start_resume_activity_time()
        with self.assertRaisesRegexp(
            ValidationError,
                'The order line task must be open.'):
            activity.order_line_id.action_cancel()
            activity.start_resume_activity_time()

    def test_compute_total_hours(self):
        activity = self.activity()
        activity.action_start()
        activity.action_pause()
        activity.action_resume()
        activity.action_pause()
        activity.action_resume()
        activity.action_end()
        for act in activity.activity_time_ids:
            act.end_date = fields.Datetime.from_string(
                act.end_date) + timedelta(hours=.5)
        activity._compute_total_hours()
        self.assertEqual(activity.total_hours, 1.5)
