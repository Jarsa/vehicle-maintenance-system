# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    program_id = fields.Many2one("vms.program", string="Maintenance Program")
