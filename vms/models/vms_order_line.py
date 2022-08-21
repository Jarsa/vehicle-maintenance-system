# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrderLine(models.Model):
    _name = "vms.order.line"
    _description = "VMS Order Line"

    task_id = fields.Many2one("vms.task", string="Task", required=True)
    start_date = fields.Datetime(
        default=fields.Datetime.now(), string="Schedule start", required=True
    )
    end_date = fields.Datetime(string="Schedule end", store=True, readonly=True)
    start_date_real = fields.Datetime(string="Real start date", readonly=True)
    end_date_real = fields.Datetime(string="Real Finishing", readonly=True)
    duration = fields.Float(store=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("process", "Process"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ]
    )
    real_duration = fields.Float(readonly=True)
    spare_part_ids = fields.One2many(
        "vms.product.line",
        "order_line_id",
        string="Spare Parts",
        help="You must save the order to select the mechanic(s).",
    )
    order_id = fields.Many2one("vms.order", readonly=True, ondelete="cascade")
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    real_time_total = fields.Integer()

    def _prepare_spare_part_ids(self, spare_part):
        return {
            "product_id": spare_part.product_id.id,
            "product_qty": spare_part.product_qty,
            "product_uom_id": spare_part.product_uom_id.id,
        }

    @api.onchange("task_id")
    def _onchange_task_id(self):
        duration = self.task_id.duration
        end_date = (
            self.start_date + timedelta(hours=self.duration)
            if self.start_date
            else False
        )
        spare_part_ids = []
        for spare_part in self.task_id.spare_part_ids:
            spare_part_ids.append((0, 0, self._prepare_spare_part_ids(spare_part)))
        self.update(
            {
                "duration": duration,
                "end_date": end_date,
                "spare_part_ids": spare_part_ids,
            }
        )

    @api.onchange("duration")
    def _onchange_duration(self):
        if self.start_date and self.duration:
            self.end_date = self.start_date + timedelta(hours=self.duration)

    @api.depends("start_date_real", "end_date_real")
    def _compute_real_time_total(self):
        for rec in self:
            start_date = fields.Datetime.from_string(rec.start_date_real)
            end_date = fields.Datetime.from_string(rec.end_date_real)
            total_days = end_date - start_date
            rec.real_time_total = total_days.days

    def action_process(self):
        for rec in self:
            if rec.order_id.state != "open":
                raise ValidationError(_("The order must be open."))
            rec.spare_part_ids._action_launch_stock_rule()
            rec.write(
                {
                    "state": "process",
                    "start_date_real": fields.Datetime.now(),
                }
            )

    def action_done(self):
        for rec in self:
            rec.write(
                {
                    "state": "done",
                    "end_date_real": fields.Datetime.now(),
                    "real_duration": rec.task_id.duration,
                }
            )

    def action_cancel(self):
        for rec in self:
            self.mapped("spare_part_ids.procurement_ids").cancel()
            rec.write(
                {
                    "state": "cancel",
                    "start_date_real": False,
                }
            )

    def action_cancel_draft(self):
        for rec in self:
            rec.state = "draft"
