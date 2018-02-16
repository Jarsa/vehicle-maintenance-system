# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVmsWizardMaintenanceOrder(TransactionCase):

    def setUp(self):
        super(TestVmsWizardMaintenanceOrder, self).setUp()
        self.operating_unit1 = self.env.ref(
            'operating_unit.b2b_operating_unit')
        self.operating_unit2 = self.env.ref(
            'operating_unit.b2c_operating_unit')
        self.unit_id1 = self.env.ref('vms.vms_fleet_vehicle_01')
        self.unit_id2 = self.env.ref('vms.vms_fleet_vehicle_02')

    def create_report(self, operating, unit):
        return self.env['vms.report'].create({
            'operating_unit_id': operating.id,
            'unit_id': unit.id,
            'employee_id': self.env.ref('hr.employee_al').id,
        })

    def test_validate_operating(self):
        report1 = self.create_report(self.operating_unit1, self.unit_id1)
        report2 = self.create_report(self.operating_unit2, self.unit_id1)
        with self.assertRaisesRegexp(
            ValidationError,
                'All reports must be in the same Operating Unit'):
            self.env['vms.wizard.maintenance.order'].with_context({
                'active_model': 'vms.report',
                'active_ids': [report1.id, report2.id]}).create({})

    def test_validate_unit(self):
        report1 = self.create_report(self.operating_unit1, self.unit_id1)
        report2 = self.create_report(self.operating_unit1, self.unit_id2)
        with self.assertRaisesRegexp(
            ValidationError,
                'All record must be of the same Unit'):
            self.env['vms.wizard.maintenance.order'].with_context({
                'active_model': 'vms.report',
                'active_ids': [report1.id, report2.id]}).create({})

    def test_validate_order(self):
        report1 = self.create_report(self.operating_unit1, self.unit_id1)
        wizard = self.env['vms.wizard.maintenance.order'].with_context({
            'active_model': 'vms.report',
            'active_ids': [report1.id]}).create({})
        wizard.make_orders()
        report2 = self.create_report(self.operating_unit1, self.unit_id1)
        with self.assertRaisesRegexp(
            ValidationError,
                'All least one record has an order assigned'):
            self.env['vms.wizard.maintenance.order'].with_context({
                'active_model': 'vms.report',
                'active_ids': [report1.id, report2.id]}).create({})
