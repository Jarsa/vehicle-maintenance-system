# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from .test_vms_activity import TestVmsActivity


class TestVmsOrderLine(TestVmsActivity):

    def test_action_process(self):
        order = self.create_order()
        with self.assertRaisesRegexp(
                ValidationError, 'The tasks must have almost one mechanic.'):
            order.action_open()

    def test_action_process_task(self):
        order = self.create_order()
        order.order_line_ids.responsible_ids += self.mechanic
        task = self.env['vms.activity'].create({
            'name': self.task.name,
            'order_id': order.id,
            'order_line_id': order.order_line_ids.id,
            'task_id': self.task.id,
            'responsible_id': self.mechanic.id,
            'unit_id': self.unit_id.id,
            'state': 'draft',
            'priority': order.order_line_ids.priority,
        })
        order.action_open()
        self.assertEqual(task.state, 'pending')

    def test_get_real_duration(self):
        order = self.create_order()
        order.order_line_ids.responsible_ids += self.mechanic
        order.action_open()
        with self.assertRaisesRegexp(
                ValidationError, 'All the activities must be finished.'):
            order.action_released()
        order.order_line_ids.activity_ids.action_start()
        order.order_line_ids.activity_ids.action_end()
        order.action_released()

    def test_get_real_duration_not(self):
        order = self.create_order()
        order.order_line_ids.responsible_ids += self.mechanic
        order.action_open()
        order.order_line_ids.activity_ids.unlink()
        order.action_released()
        self.assertEqual(
            order.order_line_ids.real_duration,
            sum(order.mapped('order_line_ids.task_id.duration')))
