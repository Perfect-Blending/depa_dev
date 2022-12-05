odoo.define('bi_dynamic_tree_view.dynamic_tree', function(require) {
	"use strict";

	var BasicView = require('web.BasicView');
	var core = require('web.core');
	var ListRenderer = require('web.ListRenderer');
	var ListController = require('web.ListController');
	var BasicRenderer = require('web.BasicRenderer');
	var config = require('web.config');
	var dom = require('web.dom');
	var field_utils = require('web.field_utils');
	var Pager = require('web.Pager');
	var utils = require('web.utils');
	var qweb = core.qweb;
	var utils = require('web.utils');


	var _t = core._t;

	ListController.include({

		events: _.extend({}, ListController.prototype.events, {
			'click #select_columns': '_manage_columns',
			'click .oe_dropdown_btn': '_hide_columns',
			'click .dropdown-menu': '_stop_event',
		}),

		init: function (parent, model, renderer, params) {
			this._super.apply(this, arguments);
			this.hasSidebar = params.hasSidebar;
			this.toolbarActions = params.toolbarActions || {};
			this.editable = params.editable;
			this.noLeaf = params.noLeaf;
			this.selectedRecords = params.selectedRecords || [];
			this.get_selected_fields = null;
			if(utils.get_cookie('selected_view_fields'))
			{
				this.get_selected_fields = JSON.parse(utils.get_cookie('selected_view_fields'));
			}
		},

		renderButtons: function ($node) {
			var self = this;
			this._super($node);
			this.$buttons.on('click', '#select_columns', this._manage_columns.bind(this));
			this.$buttons.on('click', '.oe_dropdown_btn', this._hide_columns.bind(this));
			this.$buttons.on('click', '.dropdown-menu', this._stop_event.bind(this));
		},

		
		_manage_columns: function (ev) {
			var self = this
			this.trigger_up('hide_cols');
			$("#showfields").toggle();
			var createfields = document.getElementById('showfields');
			var fields_view = this.renderer.arch.children
			_.each(fields_view, function (column) {
				var name = column.attrs.name
				var description = document.createTextNode(column.attrs.string || self.renderer.state.fields[name].string);
				var li= document.createElement("li");
				var checkbox = document.createElement("input");
				checkbox.type = "checkbox";
				checkbox.name = name;
				checkbox.id='inp';
				checkbox.checked = false;
				checkbox.invisible = column.attrs.modifiers.column_invisible || false
				if (self.get_selected_fields != null){
					if(self.modelName in self.get_selected_fields)
					{
						var fields_data = self.get_selected_fields[self.modelName];
						if(name in fields_data)
						{
							checkbox.invisible = !fields_data[name];
						}
					}
				}
				if(checkbox.invisible != true)
				{
					checkbox.checked = true;
				}
				li.appendChild(checkbox);
				li.appendChild(description);
				li.id = 'raghav';
				createfields.appendChild(li);
			});

		},
		_stop_event : function(e)
		  {
			  e.stopPropagation();
		  },

		_hide_columns : function(ev)
		{
			$("#showfields").hide();
			this.hide_columns(ev);
			var state = this.model.get(this.handle);
			this.renderer.updateState(state, {reload: true});
			document.location.reload(true);
		},

		hide_columns: function (ev) {
			var self = this;
			var return_data={};
			$('#raghav input[type="checkbox"]').each(function(){
				var name = $(this).attr('name');
				var selected_items = this;
				var checked  = $(this).is(":checked")
				return_data[name] = checked;

				var field = _.find(self.renderer.arch.children, function(field){
					return field.attrs.name === name
				});				
				if($(this).is(":checked")){
					field.attrs.modifiers.column_invisible = false;
				}
				else {
					field.attrs.modifiers.column_invisible = true;
				}
			
			});
			var get_cookie_data = {};
			if(this.get_selected_fields != null)
			{
				get_cookie_data = this.get_selected_fields;
			}
			get_cookie_data[this.modelName] = return_data;
			utils.set_cookie('selected_view_fields', JSON.stringify(get_cookie_data));

		},
	});

$(document).click(function(){
  $("#showfields").hide();
});


});
