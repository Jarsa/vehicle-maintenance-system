odoo.define('vms_activity_kiosk.task_view_handler', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var activity_model = new Model('vms.activity');
var activity_fields = ['id', 'name', 'total_hours', 'state', 'priority', 'unit_id', 'activity_time_ids'];
var activity_time_model = new Model('vms.activity.time');

var VmsKioskTaskHandler = Widget.extend({
    events: {
        "click .vms-activity-row": 'on_select_activity',
        "click a#start_task": 'on_start_task',
        "click a#pause_task": 'on_pause_task',
        "click a#stop_task": 'on_stop_task',
        "click div#return_tasks": 'on_return',
        "click div#return_home": 'go_home',
        // inactivity
        "mousemove .o_vms_kiosk_mode_container": 'restart_inactivity_detection',
        "click .o_vms_kiosk_mode_container": 'restart_inactivity_detection',
    },
    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.mechanic_id = action.mechanic_id;
        this.mechanic_name = action.mechanic_name;
    },
    start: function () {
        // To remove the top bar.
        this.getParent().getParent().$el.find('div.o_main_navbar').remove();

        // Check if there is a mechanic selected.
        if(this.mechanic_id && this.mechanic_name){
            var self = this;
            activity_model.query(activity_fields)
                .filter([['responsible_id', '=', self.mechanic_id], ['state', '=', 'process']])
                .limit(1).all().then(function(current_activity){
                    // Starts the inactivity
                    self.restart_inactivity_detection();
                    // Check if there is a task in process.
                    if(current_activity.length > 0){
                        self.activity_selected = current_activity[0];
                        self.render_task();
                    }else{
                        self.get_activities();
                    }
                });
        }else{ this.go_home(); }
        return this._super.apply(this, arguments);
    },
    go_home: function(){
        var action = {
            type: 'ir.actions.client',
            name: _t('Mechanic Tasks Kiosk Mode'),
            tag: 'vms_kiosk_barcode_employee_entry',
        };
        var options = {
            clear_breadcrumbs: true,
        }
        this.stop_clock();
        this.stop_inactivity_detection();
        this.do_action(action, options);
    },
    render_task: function() {
        this.$el.html(QWeb.render("VmsKioskTaskHandler", {
            activity: this.activity_selected, mechanic: this.mechanic_name}));
        this.get_state_buttons();
        if(this.activity_selected.state === 'process'){
            this.start_clock();
        }
    },
    get_activities: function() {
        // Get and render mechanic's activity list
        var self = this;
        activity_model.query(activity_fields)
           .filter([['responsible_id', '=', self.mechanic_id], ['state', 'not in', ['end', 'cancel', 'draft']]])
           .all().then(function(activities){
                self.activities = activities;
                self.$el.html(QWeb.render("VmsKioskSelectTask", {widget: self}));
            });
    },
    on_select_activity: function(e) {
        var activity_id = parseInt(e.currentTarget.attributes.index.value);
        this.activity_selected = $.grep(this.activities ,function(dict, index){
            return dict.id === activity_id;
        })[0];
        this.render_task();
    },
    get_state_buttons: function() {
        var start_btn = this.$el.find('a#start_task').attr('disabled', true);
        var pause_btn = this.$el.find('a#pause_task').attr('disabled', true);
        var stop_btn = this.$el.find('a#stop_task').attr('disabled', true);
        if(['pending', 'pause'].indexOf(this.activity_selected.state) >= 0){
            start_btn.attr('disabled', false);
        }
        if(['process'].indexOf(this.activity_selected.state) >= 0){
            pause_btn.attr('disabled', false);
        }
        if(['process', 'pause'].indexOf(this.activity_selected.state) >= 0){
            stop_btn.attr('disabled', false);
        }
    },
    change_state: function(method, callback=false) {
        var self = this;
        return activity_model.call(method, [this.activity_selected.id]).then(function (state) {
            self.activity_selected.state = state;
            self.$el.find('td#activity_state').html(state);
            self.get_state_buttons();
        });
    },
    on_start_task: function(e) {
        if(!e.currentTarget.attributes.disabled){
            var method = '';
            if(this.activity_selected.state === 'pending'){
                method = 'action_start';
            }else if(this.activity_selected.state === 'pause'){
                method = 'action_resume';
            }
            var self = this;
            // Wait the delay to start the clock
            this.change_state(method).then(function(){
                self.start_clock();
            });
        }
    },
    on_pause_task: function(e) {
        if(!e.currentTarget.attributes.disabled){
            this.change_state('action_pause');
            this.stop_clock();
        }
    },
    on_stop_task: function(e) {
        if(!e.currentTarget.attributes.disabled){
            this.change_state('action_end');
            this.stop_clock();
        }
    },
    on_return: function() {
        this.get_activities();
        this.stop_clock();
    },

    get_time_activity: function() {
        // Current elapsed time of activity, in format 0000:00:00
        var total_seconds = Math.round(Math.abs(this.activity_process_time - new Date)/1000) + this.total_time;
        var total_minutes = total_seconds/60;
        var total_hours = total_seconds/60/60;

        var seconds = String(total_seconds % 60);
        var minutes = String(Math.floor(total_minutes % 60));
        var hours = String(Math.floor(total_hours));
        return ("000" + hours).slice(-4) + ':' + ("0" + minutes).slice(-2) + ':' + ("0" + seconds).slice(-2); 
    },
    get_total_time: function(times) {
        // Total raw seconds of all activity times
        var self = this;
        var time_sec = 0; 
        $.each(times, function(i, val){
            if(val.state === 'end'){
                var start_date = moment(val.start_date + ' 0000', 'YYYY-MM-DD HH:mm:ss ZZ').toDate();
                var end_date = moment(val.end_date + ' 0000', 'YYYY-MM-DD HH:mm:ss ZZ').toDate();
                time_sec += Math.round(Math.abs(start_date - end_date)/1000);
            }
        });
        return time_sec;
    },
    start_clock: function() {
        var self = this;
        activity_time_model.query(['start_date', 'end_date', 'state'])
           .filter([['activity_id', '=', self.activity_selected.id]])
           .all().then(function(times){
                $.when(
                    $.grep(times ,function(dict, index){
                        return dict.state === 'process';
                    })[0]
                ).done(function(current_activity){
                    self.activity_process_time = moment(current_activity.start_date + ' 0000', 'YYYY-MM-DD HH:mm:ss ZZ').toDate();

                    $.when(
                        self.get_total_time(times)
                    ).done(function(total_time){
                        self.total_time = total_time;
                        self.clock_start = setInterval(function () {self.$(".o_vms_kiosk_clock").text(self.get_time_activity());}, 500);
                        // To avoid the setInterval delay
                        self.$(".o_vms_kiosk_clock").text(self.get_time_activity());
                        self.$el.find('.o_vms_kiosk_clock_content').show();
                    });  

                });              
            });
    },
    stop_clock: function () {
        clearInterval(this.clock_start);
        this.$el.find('.o_vms_kiosk_clock_content').hide();
    },
    destroy: function () {
        this.stop_clock();
        this.stop_inactivity_detection();
        this._super.apply(this, arguments);
    },

    restart_inactivity_detection: function(e) {
        // Avoid go home after press go home by inactivity
        var homeid = ((e || {}).target || {}).id === 'return_home';
        var homeparentid = (((e || {}).target || {}).parentElement || {}).id === 'return_home';
        if( (e || {}).type === 'mousemove' || !(homeid || homeparentid)){
            var self = this;
            clearTimeout(this.inactivity_notice);
            this.$el.find('.vms-alert').slideUp(500, function(){
                $(this).remove();
            });
            // Show and alert after 15 second of inactivity
            this.inactivity_notice = setTimeout( function(){
                var message = _t('Inactivity was detected, the session will be closed in 5 seconds.');
                var notice = $('<div class="vms-alert alert-warning">\
                        <i class="fa fa-exclamation-triangle"></i> '+ message +'\
                    </div>').hide();
                self.$el.find('.o_vms_kiosk_mode').before(notice);
                notice.slideDown(500);
            }, 15000 );
            clearTimeout(this.inactivity);
            // Go home after 5 seconds the alert was shown
            this.inactivity = setTimeout( function(){ self.go_home(); }, 20000 );
        }
    },
    stop_inactivity_detection: function() {
        clearTimeout(this.inactivity_notice);
        clearTimeout(this.inactivity);
    },
});

core.action_registry.add('vms_kiosk_task_handler', VmsKioskTaskHandler);

return VmsKioskTaskHandler;

});
