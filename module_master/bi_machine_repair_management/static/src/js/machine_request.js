odoo.define('bi_machine_repair_management.machine_request', function (require) {
'use strict';
	var ajax = require('web.ajax');
	var core = require('web.core');
	var Widget = require('web.Widget');
	var qweb = core.qweb;

	var portalchatter = require('portal.chatter');

	portalchatter.PortalChatter.include({
		_loadTemplates: function(){
        	return $.when(this._super(), ajax.loadXML('/bi_machine_repair_management/static/src/xml/chatter.xml', qweb));
    	},
	})

});