odoo.define('bi_dynamic_tree_view.list_renderer_extend', function(require) {
	"use strict";
	var core = require('web.core');
	var dom = require('web.dom');
	var ListController = require('web.ListController');
	var ListRenderer = require('web.ListRenderer');
	var utils = require('web.utils');

	var _t = core._t;
	ListRenderer.include({
		init: function (parent, state, params) {
			this._super.apply(this, arguments);
			this.get_selected_fields = null;	
			if(utils.get_cookie('selected_view_fields'))
			{
				this.get_selected_fields = JSON.parse(utils.get_cookie('selected_view_fields'));
			}
		},

		_processColumns: function (columnInvisibleFields) {
			var self = this;
			self.handleField = null;
			this.get_selected_fields = null;
			if(utils.get_cookie('selected_view_fields'))
			{
				this.get_selected_fields = JSON.parse(utils.get_cookie('selected_view_fields'));
			}

			if (this.get_selected_fields != null){
				if(this.state.model in this.get_selected_fields)
				{
					var fields_data = this.get_selected_fields[this.state.model];

					this.columns = _.reject(this.arch.children, function (c) {
						if (c.tag === 'control') {
							return true;
						}
						var reject;
						var name = c.attrs.name;
						if(name in fields_data)
						{
							if(fields_data[name] == false){
								reject = c.attrs.modifiers.column_invisible;
							}
						}
						if (!reject && c.attrs.widget === 'handle') {
							self.handleField = c.attrs.name;
						}
						return reject;
					});
				}
				else{
					this.columns = _.reject(this.arch.children, function (c) {
						if (c.tag === 'control') {
							return true;
						}
						var reject = c.attrs.modifiers.column_invisible;
						if (c.attrs.name in columnInvisibleFields) {
							reject = columnInvisibleFields[c.attrs.name];
						}
						if (!reject && c.attrs.widget === 'handle') {
							self.handleField = c.attrs.name;
						}
						return reject;
					});
				}
			}
			else{
					this.columns = _.reject(this.arch.children, function (c) {
						if (c.tag === 'control') {
							return true;
						}
						var reject = c.attrs.modifiers.column_invisible;
						// If there is an evaluated domain for the field we override the node
						// attribute to have the evaluated modifier value.
						if (c.attrs.name in columnInvisibleFields) {
							reject = columnInvisibleFields[c.attrs.name];
						}
						if (!reject && c.attrs.widget === 'handle') {
							self.handleField = c.attrs.name;
						}
						return reject;
					});
			}
			
		},

	});

});