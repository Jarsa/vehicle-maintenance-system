# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestVmsActivity(TransactionCase):

    def setUp(self):
        super(TestVmsActivity, self).setUp()
        self.task = self.env.ref('vms.vms_task_01')
        self.reponsible = self.env.ref('vms.vms_hr_employee_01')
        self.order = self.env['vms.order'].create({
            'operating_unit_id': self.operating_unit.id,
            'supervisor_id': self.env.ref('vms.vms_hr_employee_01').id,
            'type': 'preventive',
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
        self.order.order_line_ids.create({
            'task_id': self.task.id,
            'start_date': start_date,
            'duration': duration,
            'spare_part_ids': [line for line in spares],
            'order_id': self.order.id
        })

    def create_activity(self):
        return self.env['vms.activity'].create({
            'name': 'Test',
            'order_id': self.order.id,
            'reponsible_id': self.reponsible.id,
            'unit_id': self.order.unit_id.id
        })
