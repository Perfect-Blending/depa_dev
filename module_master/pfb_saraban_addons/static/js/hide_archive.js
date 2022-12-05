odoo.define("disable_action_bar", function(require) {
    "use strict";
    
        var core = require("web.core");
        var Sidebar = require("web.Sidebar");
        var _t = core._t;
        // var session = require("web.session");
    
        Sidebar.include({
            /**
            * @override
            */
            add_items: function(section_code, items) {
                console.log(self);
                var self = this;
                // var _super = this._super;
                // if (!can_export) {
                var export_label = _t("Export");
                var new_items = items;
                if (section_code === "other") {
                    new_items = [];
                    for (var i = 0; i < items.length; i++) {
                        console.log("items[i]: ", items[i]);
                        if (items[i]["label"] !== export_label) {
                            new_items.push(items[i]);
                        }
                    }
                }
                //     if (new_items.length > 0) {
                //         _super.call(self, section_code, new_items);
                //     }
                // } else {
                //     _super.call(self, section_code, items);
                // }
            },
            /**
            * @override
            */
            _addToolbarActions: function (toolbarActions) {
                var self = this;
                console.log(self);
                _.each(['print','action','relate'], function (type) {
                    if (type in toolbarActions) {
                        var actions = toolbarActions[type];
                        if (actions && actions.length) {
                            var items = _.map(actions, function (action) {
                                return {
                                    label: action.name,
                                    action: action,
                                };
                            });
                            self._addItems(type === 'print' ? 'print' : 'other', items);
                        }
                    }
                });
                if ('other' in toolbarActions) {
                    if(self.__parentedParent.modelName == 'document.internal.main' && self.__parentedParent.viewType == 'list' && self.__parentedParent.displayName == 'หนังสือภายใน/รอดำเนินการ'){
                        return;
                    } else {
                        this._addItems('other', toolbarActions.other);
                    }
                }
            },
        });
    });

    
// odoo.define('pfb_saraban_addons.BasicView', function (require) {
// "use strict";

// // var session = require('web.session');
// // var BasicView = require('web.BasicView');
// // BasicView.include({
// //         init: function(viewInfo, params) {
// //             var self = this;
// //             this._super.apply(this, arguments);
// //             var model = self.controllerParams.modelName;
// //             if(model == 'document.internal.main') {
// //                 self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
// // //                console.log(self);
// // ////                console.log(self.controllerParams.toolbarActions.action);
// // ////                self.controllerParams.toolbarActions['action'] = 'False';
// // //                self.controllerParams.archiveEnabled = 'False';
// //             }
// //         },
// // });

//     var core = require("web.core");
//     var Sidebar = require("web.Sidebar");
//     // var _t = core._t;
//     // var Model = require("web.Model");
//     var session = require("web.session");

//     Sidebar.include({
// //         init: function(viewInfo, params) {
// //             var self = this;
// //             this._super.apply(this, arguments);
// //             var model = self.controllerParams.modelName;
// //             if(model == 'document.internal.main') {
// //                 self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
// // //                console.log(self);
// // ////                console.log(self.controllerParams.toolbarActions.action);
// // ////                self.controllerParams.toolbarActions['action'] = 'False';
// // //                self.controllerParams.archiveEnabled = 'False';
// //             }
// //         },
//         add_items: function(section_code, items) {
//             var self = this;
//             var model = self.controllerParams.modelName;
//             if(model == 'document.internal.main') {
//                 var _super = this._super;
//                 // var export_label = _t("Export");
//                 // var new_items = items;
//                 if (section_code === "other") {
//                     // new_items = [];
//                     // for (var i = 0; i < items.length; i++) {
//                     //     console.log("items[i]: ", items[i]);
//                     //     if (items[i]["label"] !== export_label) {
//                     //         new_items.push(items[i]);
//                     //     }
//                     // }
//                     return true;
//                 }
//                 // if (new_items.length > 0) {
//                 //     _super.call(self, section_code, new_items);
//                 // }
//             }
//         }
//     });


// });