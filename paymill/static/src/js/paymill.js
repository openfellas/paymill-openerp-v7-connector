openerp.paymill = function(instance) {
	var _t = instance.web._t, _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	instance.paymill = {}

	instance.paymill.PaymillConnectButton = instance.web.form.WidgetButton.extend({
		get_allowed_permissions: function(fields) {
	    	var allowed_permissions = []
	    	for (var field in fields){
	    	    if ((fields.hasOwnProperty(field)) && (fields[field] == true) && (field.indexOf("_r") > -1 || field.indexOf("_w") > -1 || field.indexOf("_rw") > -1)) {
	    	    	allowed_permissions.push(field);
	    	    }
	    	}

	    	return allowed_permissions.join(' ');

		},

	    on_click: function() {
	        var self = this;
	        
        	fields = this.field_manager.datarecord;
        	
        	var client_id = fields.client_id;

        	var scope = this.get_allowed_permissions(fields);

        	var db = this.session.db;

        	var url = 'https://connect.paymill.com/authorize?client_id='+client_id+'&scope='+scope+'&response_type=code' + '&custom_param='+db+'';

        	window.open(url);
	        
	        this.force_disabled = true;
	        this.check_disable();
	        this.execute_action().always(function() {
	            self.force_disabled = false;
	            self.check_disable();
	        });
    	},

	});

	instance.web.form.tags.add('paymill_button', 'instance.paymill.PaymillConnectButton');

	instance.web.form.widgets.add('PaymillMany2One', 'instance.paymill.FieldMany2One');
	instance.paymill.FieldMany2One = instance.web.form.FieldMany2One.extend({
	    _search_create_popup: function(view, ids, context) {
	        this.no_ed = true;
	        this.ed_def.reject();

	        var self = this;
	        var pop = new instance.paymill.SelectCreatePopup(this);
	        pop.select_element(
	            self.field.relation,
	            {
	                title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
	                initial_ids: ids ? _.map(ids, function(x) {return x[0]}) : undefined,
	                initial_view: view,
	                disable_multiple_selection: true,
	            },
	            self.build_domain(),
	            new instance.web.CompoundContext(self.build_context(), context || {})
	        );
	        pop.on("elements_selected", self, function(element_ids) {
	            self.add_id(element_ids[0]);
	            self.focus();
	        });
	    },
	});
	
	instance.paymill.get_paymill_public_key = function(self, public_key){
		var res = $.Deferred();
		
		self.rpc('/paymill/get_paymill_public_key', {}).done(function(response) {
			res.resolve(response.paymill_public_key);
        });

		return res.promise();
	}

	instance.paymill.handle_paymill = function(self, values){
		var result = $.Deferred();

    	function PaymillResponseHandler(error, res) {
			if (error) {
				alert(error.apierror);
			} else {
				self.rpc('/paymill/get_paymill_payment_object', {token:res.token}).done(function(response) {
					values.payment = response.payment;
					values.type = response.type;
					values.client = response.client;
					values.card_type = response.card_type;
					values.country = response.country;
					values.expire_month = response.expire_month;
					values.expire_year = response.expire_year;
					values.last4 = response.last4;
					values.created_at = response.created_at;
					values.updated_at = response.updated_at;
					values.app_id = response.app_id;
					values.last4 = response.last4;

					result.resolve(values)
	            });
			}
		};

		instance.paymill.get_paymill_public_key(self).done(function(public_key) {
		     paymill.PAYMILL_PUBLIC_KEY = public_key;
				paymill.createToken({
					number : values.card_number_c1.toString() + values.card_number_c2.toString() + values.card_number_c3.toString() + values.card_number_c4.toString(),

					exp_month : values.expiry_month,
					exp_year : values.expiry_year,

					cvc : values.cvc_code.toString(),

					// TODO
					amount_int : 15,

					// TODO
					currency : "EUR",

					cardholder : values.partner_name,

				}, PaymillResponseHandler);
		});

		return result.promise();

	};

	instance.paymill.FormView = instance.web.FormView.extend({
		_process_save: function(save_obj) {
	        var self = this;

	        var prepend_on_create = save_obj.prepend_on_create;
	        try {
	            var form_invalid = false,
	                values = {},
	                first_invalid_field = null,
	                readonly_values = {};
	            for (var f in self.fields) {
	                if (!self.fields.hasOwnProperty(f)) { continue; }
	                f = self.fields[f];
	                if (!f.is_valid()) {
	                    form_invalid = true;
	                    if (!first_invalid_field) {
	                        first_invalid_field = f;
	                    }
	                } else if (f.name !== 'id' && (!self.datarecord.id || f._dirty_flag)) {
	                    // Special case 'id' field, do not save this field
	                    // on 'create' : save all non readonly fields
	                    // on 'edit' : save non readonly modified fields
	                    if (!f.get("readonly")) {
	                        values[f.name] = f.get_value();
	                    } else {
	                        readonly_values[f.name] = f.get_value();
	                    }
	                }
	            }
	            if (form_invalid) {
	                self.set({'display_invalid_fields': true});
	                first_invalid_field.focus();
	                self.on_invalid();
	                return $.Deferred().reject();
	            } else {
	                self.set({'display_invalid_fields': false});
	                var save_deferral;
	                if (!self.datarecord.id) {
	                	
	                	save_deferral = instance.paymill.handle_paymill(self, values).then(function (values){
	                        // Creation save
	                        return self.dataset.create(values, {readonly_fields: readonly_values}).then(function(r) {
	                            return self.record_created(r, prepend_on_create);
	                        }, null);                		
	                	});
	                } else if (_.isEmpty(values)) {
	                    // Not dirty, noop save
	                    save_deferral = $.Deferred().resolve({}).promise();
	                } else {
	                    // Write save
	                    save_deferral = self.dataset.write(self.datarecord.id, values, {readonly_fields: readonly_values}).then(function(r) {
	                        return self.record_saved(r);
	                    }, null);
	                }
	                return save_deferral;
	            }
	        } catch (e) {
	            console.error(e);
	            return $.Deferred().reject();
	        }
	    },

	});

	instance.paymill.SelectCreatePopup = instance.web.form.SelectCreatePopup.extend({
		setup_form_view: function() {
	        var self = this;
	        if (this.row_id) {
	            this.dataset.ids = [this.row_id];
	            this.dataset.index = 0;
	        } else {
	            this.dataset.index = null;
	        }
	        var options = _.clone(self.options.form_view_options) || {};
	        if (this.row_id !== null) {
	            options.initial_mode = this.options.readonly ? "view" : "edit";
	        }
	        _.extend(options, {
	            $buttons: this.$buttonpane,
	        });
	        this.view_form = new instance.paymill.FormView(this, this.dataset, this.options.view_id || false, options);
	        if (this.options.alternative_form_view) {
	            this.view_form.set_embedded_view(this.options.alternative_form_view);
	        }
	        this.view_form.appendTo(this.$el.find(".oe_popup_form"));
	        this.view_form.on("form_view_loaded", self, function() {
	            var multi_select = self.row_id === null && ! self.options.disable_multiple_selection;
	            self.$buttonpane.html(QWeb.render("AbstractFormPopup.buttons", {
	                multi_select: multi_select,
	                readonly: self.row_id !== null && self.options.readonly,
	            }));
	            var $snbutton = self.$buttonpane.find(".oe_abstractformpopup-form-save-new");
	            $snbutton.click(function() {
	                $.when(self.view_form.save()).done(function() {
	                    self.view_form.reload_mutex.exec(function() {
	                        self.view_form.on_button_new();
	                    });
	                });
	            });
	            var $sbutton = self.$buttonpane.find(".oe_abstractformpopup-form-save");
	            $sbutton.click(function() {
	                $.when(self.view_form.save()).done(function() {
	                    self.view_form.reload_mutex.exec(function() {
	                        self.check_exit();
	                    });
	                });
	            });
	            var $cbutton = self.$buttonpane.find(".oe_abstractformpopup-form-close");
	            $cbutton.click(function() {
	                self.view_form.trigger('on_button_cancel');
	                self.check_exit();
	            });
	            self.view_form.do_show();
	        });
	    },
	});

	instance.web.form.widgets.add('PaymillOne2Many', 'instance.paymill.FieldOne2Many');
	instance.paymill.FieldOne2Many = instance.web.form.FieldOne2Many.extend({
		load_views: function() {
	        var self = this;
	
	        var modes = this.node.attrs.mode;
	        modes = !!modes ? modes.split(",") : ["tree"];
	        var views = [];
	        _.each(modes, function(mode) {
	            if (! _.include(["list", "tree", "graph", "kanban"], mode)) {
	                throw new Error(_.str.sprintf(_t("View type '%s' is not supported in One2Many."), mode));
	            }
	            var view = {
	                view_id: false,
	                view_type: mode == "tree" ? "list" : mode,
	                options: {}
	            };
	            if (self.field.views && self.field.views[mode]) {
	                view.embedded_view = self.field.views[mode];
	            }
	            if(view.view_type === "list") {
	                _.extend(view.options, {
	                    addable: null,
	                    selectable: self.multi_selection,
	                    sortable: true,
	                    import_enabled: false,
	                    deletable: true
	                });
	                if (self.get("effective_readonly")) {
	                    _.extend(view.options, {
	                        deletable: null,
	                        reorderable: false,
	                    });
	                }
	            } else if (view.view_type === "form") {
	                if (self.get("effective_readonly")) {
	                    view.view_type = 'form';
	                }
	                _.extend(view.options, {
	                    not_interactible_on_create: true,
	                });
	            } else if (view.view_type === "kanban") {
	                _.extend(view.options, {
	                    confirm_on_delete: false,
	                });
	                if (self.get("effective_readonly")) {
	                    _.extend(view.options, {
	                        action_buttons: false,
	                        quick_creatable: false,
	                        creatable: false,
	                        read_only_mode: true,
	                    });
	                }
	            }
	            views.push(view);
	        });
	        this.views = views;
	
	        this.viewmanager = new instance.paymill.One2ManyViewManager(this, this.dataset, views, {});
	        this.viewmanager.o2m = self;
	        var once = $.Deferred().done(function() {
	            self.init_form_last_update.resolve();
	        });
	        var def = $.Deferred().done(function() {
	            self.initial_is_loaded.resolve();
	        });
	        this.viewmanager.on("controller_inited", self, function(view_type, controller) {
	            controller.o2m = self;
	            if (view_type == "list") {
	                if (self.get("effective_readonly")) {
	                    controller.on('edit:before', self, function (e) {
	                        e.cancel = true;
	                    });
	                    _(controller.columns).find(function (column) {
	                        if (!(column instanceof instance.web.list.Handle)) {
	                            return false;
	                        }
	                        column.modifiers.invisible = true;
	                        return true;
	                    });
	                }
	            } else if (view_type === "form") {
	                if (self.get("effective_readonly")) {
	                    $(".oe_form_buttons", controller.$el).children().remove();
	                }
	                controller.on("load_record", self, function(){
	                     once.resolve();
	                 });
	                controller.on('pager_action_executed',self,self.save_any_view);
	            } else if (view_type == "graph") {
	                self.reload_current_view()
	            }
	            def.resolve();
	        });
	        this.viewmanager.on("switch_mode", self, function(n_mode, b, c, d, e) {
	            $.when(self.save_any_view()).done(function() {
	                if (n_mode === "list") {
	                    $.async_when().done(function() {
	                        self.reload_current_view();
	                    });
	                }
	            });
	        });
	        $.async_when().done(function () {
	            self.viewmanager.appendTo(self.$el);
	        });
	        return def;
	    },
	});
	
	instance.paymill.One2ManyViewManager = instance.web.form.One2ManyViewManager.extend({
		init: function(parent, dataset, views, flags) {
			this._super(parent, dataset, views, _.extend({}, flags, {$sidebar: false}));
			this.registry = this.registry.extend({
	            list: 'instance.paymill.One2ManyListView',
	        });
		}
	});
	
	instance.paymill.One2ManyListView = instance.web.form.One2ManyListView.extend({
	    init: function (parent, dataset, view_id, options) {
	        this._super(parent, dataset, view_id, _.extend(options || {}, {
	            GroupsType: instance.web.form.One2ManyGroups,
	            ListType: instance.web.form.One2ManyList
	        }));
	        this.on('edit:after', this, this.proxy('_after_edit'));
	        this.on('save:before cancel:before', this, this.proxy('_before_unedit'));
	
	        this.records
	            .bind('add', this.proxy("changed_records"))
	            .bind('edit', this.proxy("changed_records"))
	            .bind('remove', this.proxy("changed_records"));
	    },

		do_add_record: function () {
	        if (this.editable()) {
	            this._super.apply(this, arguments);
	        } else {
	            var self = this;
	            var pop = new instance.paymill.SelectCreatePopup(this);
	            pop.select_element(
	                self.o2m.field.relation,
	                {
	                    title: _t("Create: ") + self.o2m.string,
	                    initial_view: "form",
	                    alternative_form_view: self.o2m.field.views ? self.o2m.field.views["form"] : undefined,
	                    create_function: function(data, options) {
                    		return self.o2m.dataset.create(data, options).done(function(r) {
	                            self.o2m.dataset.set_ids(self.o2m.dataset.ids.concat([r]));
	                            self.o2m.dataset.trigger("dataset_changed", r);
	                        });
	                    	
	                    },
	                    read_function: function() {
	                        return self.o2m.dataset.read_ids.apply(self.o2m.dataset, arguments);
	                    },
	                    parent_view: self.o2m.view,
	                    child_name: self.o2m.name,
	                    form_view_options: {'not_interactible_on_create':true}
	                },
	                self.o2m.build_domain(),
	                self.o2m.build_context()
	            );
	            pop.on("elements_selected", self, function() {
	                self.o2m.reload_current_view();
	            });
	        }
	    },
	    
	    // Thid method will handle opening of paymill 
	    do_activate_record: function(index, id) {
	    	return
	    },
	});
}