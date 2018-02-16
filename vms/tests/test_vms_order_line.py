# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from .test_vms_order import TestVmsOrder


class TestVmsOrderLine(TestVmsOrder):

    def setUp(self):
        super(TestVmsOrderLine, self).setUp()
        self.external_service = self.env.ref('vms.product_product_vms_04')
        self.supplier = self.env.ref('base.res_partner_address_3')

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

    def test_onchange_task(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        order_line._onchange_task()
        self.assertEqual(order_line.duration, .5)
        self.assertTrue(order_line.spare_part_ids)

    def test_onchange_duration(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        order_line._onchange_duration()
        end_date = fields.Datetime.to_string(
            fields.Datetime.from_string(
                order_line.start_date) + timedelta(hours=self.task.duration))
        self.assertEqual(order_line.end_date, end_date)

    def test_compute_real_time_total(self):
        order = self.create_order('preventive')
        order.action_open()
        order_line = order.order_line_ids
        order_line.action_done()
        order_line.end_date_real = fields.Datetime.to_string(
            fields.Datetime.from_string(order_line.end_date_real) +
            timedelta(days=2))
        order_line._compute_real_time_total()
        self.assertEqual(order_line.real_time_total, 2)

    def test_create_po(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        order_line.write({
            'product_id': self.external_service.id,
            'external': True,
            'supplier_id': self.supplier.id,
        })
        order_line.spare_part_ids.write({
            'external_spare_parts': True,
        })
        order.action_open()
        order_line.create_po()
        self.assertTrue(order_line.purchase_order_id)
        order_line._compute_purchase_state()
        self.assertFalse(order_line.purchase_state)

    def test_action_process_raise(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        with self.assertRaisesRegexp(
                ValidationError, 'The order must be open.'):
            order_line.action_process()
        order_line.spare_part_ids.unlink()
        order.action_open()
        self.assertFalse(order_line.spare_part_ids)

    def test_action_done_raise(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        order_line.write({
            'product_id': self.external_service.id,
            'external': True,
            'supplier_id': self.supplier.id,
        })
        order.action_open()
        order_line.create_po()
        with self.assertRaisesRegexp(
                ValidationError,
                'Verify that purchase order are in done state to continue'):
            order_line.action_done()

    def test_action_cancel_draft(self):
        order = self.create_order('preventive')
        order_line = order.order_line_ids
        order_line.action_cancel()
        order_line.action_cancel_draft()
        self.assertEqual(order_line.state, 'draft')
