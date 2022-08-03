# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestVmsReport(TransactionCase):
    def setUp(self):
        super().setUp()

        self.report = self.env["vms.report"].create(
            {
                "unit_id": self.env.ref("vms.vms_fleet_vehicle_01").id,
                "employee_id": self.env.ref("hr.employee_al").id,
            }
        )

    def test_create(self):
        report = self.report
        self.assertEqual(report.name, "R-GDL0001")

    def test_action_confirmed(self):
        self.report.action_confirmed()
        self.assertEqual(self.report.state, "closed")

    def test_action_cancel(self):
        self.report.action_cancel()
        self.assertEqual(self.report.state, "cancel")

    def test_action_pending(self):
        self.report.action_pending()
        self.assertEqual(self.report.state, "pending")
