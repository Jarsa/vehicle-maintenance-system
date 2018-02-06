odoo.define('vms_activity_kiosk.barcode_employee_entry', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var Widget = require('web.Widget');
var Session = require('web.session');
var BarcodeHandlerMixin = require('barcodes.BarcodeHandlerMixin');
var mobile = require('web_mobile.rpc');

var QWeb = core.qweb;
var _t = core._t;

var VmsKioskBarcodeEntry = Widget.extend(BarcodeHandlerMixin, {
    events: {
        "click .o_vms_kiosk_mobile_barcode": 'open_mobile_scanner',
        "click #o_vms_kiosk_select_hr": function(){ this.do_action('vms_activity_kiosk.hr_employee_vms_activity_kiosk_action_kanban'); },
    },
    init: function (parent, action) {
        // Note: BarcodeHandlerMixin.init calls this._super.init, so there's no need to do it here.
        // Yet, "_super" must be present in a function for the class mechanism to replace it with the actual parent method.
        this._super;
        BarcodeHandlerMixin.init.apply(this, arguments);
    },
    start: function () {
        // To remove the top bar.
        this.getParent().getParent().$el.find('div.o_main_navbar').remove();
        //
        var self = this;
        self.session = Session;
        var res_company = new Model('res.company');
        res_company.query(['name'])
            .filter([['id', '=', self.session.company_id]])
            .all().then(function (companies){
                self.company_name = companies[0].name;
                self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: self.session.company_id, field: 'logo',});
                self.$el.html(QWeb.render("VmsKioskSelectMechanic", {widget: self}));
                if(!mobile.methods.scanBarcode){
                    self.$el.find(".o_vms_kiosk_mobile_barcode").remove();
                }
            });
        return self._super.apply(this, arguments);
    },
    open_mobile_scanner: function(){
        var self = this;
        mobile.methods.scanBarcode().then(function(response){
            var barcode = response.data;
            if(barcode){
                self.on_barcode_scanned(barcode);
                mobile.methods.vibrate({'duration': 100});
            }else{
                mobile.methods.showToast({'message': _t('Please, Scan again !!')});
            }
        });
    },
    on_barcode_scanned: function(barcode) {
        var self = this;
        var hremployee_model = new Model('hr.employee');
        hremployee_model.query(['id', 'name'])
            .filter([['vms_barcode', '=', barcode], ['mechanic', '=', 'True']])
            .limit(1).all().then(function(mechanic){
                if(mechanic.length > 0){
                    var action = {
                        type: 'ir.actions.client',
                        name: _t('Tasks'),
                        tag: 'vms_kiosk_task_handler',
                        mechanic_id: mechanic[0].id,
                        mechanic_name: mechanic[0].name,
                    };
                    self.do_action(action);
                }else{
                    self.do_warn('Barcode Error', _t('There is no a mechanic with this barcode.'));
                }
            });
    },
});

core.action_registry.add('vms_kiosk_barcode_employee_entry', VmsKioskBarcodeEntry);

return VmsKioskBarcodeEntry;

});
