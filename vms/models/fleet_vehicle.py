# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    program_id = fields.Many2one("vms.program", string="Maintenance Program")
    distance = fields.Float(
        "Distance Average",
        required=True,
        compute="_compute_distance_averange",
    )
    supervisor_id = fields.Many2one(
        "hr.employee",
        "Supervisor",
        domain=[("mechanic", "=", True)],
    )

    def _prepare_order(self, cycle):
        self.ensure_one()
        return {
            "unit_id": self.id,
            "type": "preventive",
            "date": fields.Date.today()
            + timedelta(days=round(cycle.frequency / self.distance)),
            "supervisor_id": self.supervisor_id.id,
            "state": "draft",
            "program_id": self.program_id.id,
        }

    @api.model
    def cron_vehicle_maintenance(self):
        order_obj = self.env["vms.order"]
        follower = self.env["mail.wizard.invite"]
        security_day = int(
            self.env["ir.config_parameter"].sudo().get_param("security_days")
        )
        for rec in self.search([]):
            if not rec.program_id:
                continue
            for cycle in rec.program_id.cycle_ids:
                order = order_obj.search(
                    [("unit_id", "=", rec.id), ("state", "=", "draft")]
                )
                if not order:
                    new_order = order_obj.create(self._prepare_order(cycle))
                    new_order.get_tasks_from_cycle(cycle, new_order)
                    if rec.supervisor_id.address_home_id.id:
                        context = {
                            "default_res_model": "vms.order",
                            "default_res_id": new_order.id,
                        }
                        mail_invite = follower.with_context(**context).create(
                            {
                                "partner_ids": [
                                    (4, rec.supervisor_id.address_home_id.id)
                                ],
                                "send_mail": True,
                            }
                        )
                        mail_invite.add_followers()
                    else:
                        msg = _(
                            "The supervisor was not added as "
                            "a document follower because does "
                            "not have a home_address assigned"
                        )
                        new_order.message_post(body=msg)
                else:
                    order_date = order.date - fields.Datetime.now()
                    if security_day == order_date.days:
                        self.env["mail.message"].create(
                            {
                                "date": fields.Date.today(),
                                "email_from": "",
                                "author_id": self.env.user.id,
                                "record_name": order.name,
                                "model": "vms.order",
                                "res_id": order.id,
                                "message_type": "email",
                                "body": "Mantenimiento pendiente en",
                            }
                        )

    def _compute_distance_averange(self):
        for rec in self:
            frequency = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("day_distance_averange")
            )
            time = fields.Date
            date_end = time.from_string(time.today())
            date_start = date_end - timedelta(days=frequency)
            odometer = self.env["fleet.vehicle.odometer"]
            odometers = odometer.search(
                [
                    ("vehicle_id", "=", rec.id),
                    ("date", ">=", time.to_string(date_start)),
                    ("date", "<=", time.to_string(date_end)),
                ]
            )
            if odometers:
                distance = sum(x.value for x in odometers) / frequency
                rec.distance = distance
