# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    def _prepare_order(self, program):
        res = super()._prepare_order(program)
        res["operating_unit_id"] = self.operating_unit_id.id
        return res
