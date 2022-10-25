# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVmsWizardMaintenanceOrder(TransactionCase):
    def setUp(self):
        super(TestVmsWizardMaintenanceOrder, self).setUp()
        self.vehicle_id1 = self.env.ref("vms.vms_fleet_vehicle_01")
        self.vehicle_id2 = self.env.ref("vms.vms_fleet_vehicle_02")

    def create_report(self, unit):
        return self.env["vms.report"].create(
            {
                "vehicle_id": unit.id,
                "employee_id": self.env.ref("hr.employee_al").id,
            }
        )

    def test_validate_order(self):
        report1 = self.create_report(self.vehicle_id1)
        context = {"active_model": "vms.report", "active_ids": [report1.id]}
        wizard = (
            self.env["vms.wizard.maintenance.order"].with_context(**context).create({})
        )
        wizard.make_orders()
        report2 = self.create_report(self.vehicle_id1)
        with self.assertRaisesRegexp(
            ValidationError, "All least one record has an order assigned"
        ):
            context = {
                "active_model": "vms.report",
                "active_ids": [report1.id, report2.id],
            }
            self.env["vms.wizard.maintenance.order"].with_context(**context).create({})
