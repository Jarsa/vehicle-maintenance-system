odoo.define('vms_activity_kiosk.employee_kanban_view_handler', function(require) {
"use strict";

var core = require('web.core');
var KanbanRecord = require('web_kanban.Record');
var KanbanView = require('web_kanban.KanbanView');
var Widget = require('web.Widget');
var QWeb = core.qweb;

var _t = core._t;


KanbanView.include({
    start: function(){
        var sup = this._super();
        var self = this;
        // Waits to render all dom and then removes the top bar of tasks kiosk mode.
        $.when( sup ).then(function(sup){
            if(sup.el.classList.value.includes('o_hr_employee_vms_activity_kiosk_kanban')){
                sup.getParent().getParent().getParent().$el.find('div.o_main_navbar').remove();
            }
        });
    },
});

KanbanRecord.include({
    on_card_clicked: function() {
        if (this.model === 'hr.employee' && this.$el.parents('.o_hr_employee_vms_activity_kiosk_kanban').length) {
            // needed to diffentiate : register activities kanban view of mechanics <-> standard employee kanban view
            var action = {
                type: 'ir.actions.client',
                name: _t('Tasks'),
                tag: 'vms_kiosk_task_handler',
                mechanic_id: this.record.id.raw_value,
                mechanic_name: this.record.name.raw_value,
            };
            this.do_action(action);
        } else {
            this._super.apply(this, arguments);
        }
    }
});

});
