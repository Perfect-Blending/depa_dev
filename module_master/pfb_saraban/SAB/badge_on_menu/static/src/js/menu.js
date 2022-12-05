odoo.define('badge_on_menu', function(require) {
    'use strict';

    var Menu = require('web.Menu');
    var core = require('web.core');
    var QWeb = core.qweb;
    var session = require('web.session');

    // Attachment Logic Implemented
    var AttachmentBox = require('mail.AttachmentBox');
    AttachmentBox.include({
        _onDeleteAttachment: function(ev) {
            var self = this;
            ev.stopPropagation();
            var $target = $(ev.currentTarget);
            this.trigger_up('delete_attachment', {
                attachmentId: $target.data('id'),
                attachmentName: $target.data('name')
            });
            var data = {
                // author_id: [5],
                subject: false,
                body: _t("Deleted " + $target.data('name')),
                // model: 'document.internal.main',
                res_id: this.currentResID,

            };
            self._rpc({
                model: self.currentResModel,
                method: 'message_post',
                args: [self.currentResID],
                kwargs: data,
            });
        },

        Update_msg: function(data) {
            var self = this;
            var i;
            for (i in data) {
                console.log(i + ":" + data[i])
            }
            console.log(self.currentResModel)
            self._rpc({
                model: self.currentResModel,
                method: 'message_post',
                args: [self.currentResID],
                kwargs: data,
            });
            self.trigger_up('reload_attachment_box');
            self.trigger_up('reload_mail_fields');
            // self.trigger_up('reload');

        },

        _onAddAttachment: function(ev) {
            var self = this;
            var $input = $(ev.currentTarget).find('input.o_input_file');
            if ($input.val() !== '') {
                //var filename = $input.val().match(/^.?([^\\/.])[^\\/]*$/);
                var test = $input.val().split(':')[1];
                // alert(test);
                var filename = test.substring(test.lastIndexOf("\\") + 1, test.length);
                var $binaryForm = this.$('form.o_form_binary_form');
                $binaryForm.submit().then(function(id) {
                    var data = {
                        // author_id: [5],
                        subject: false,
                        body: _t("Attachment created " + filename),
                        // attachment_ids: [1],
                        // model: 'document.internal.main',
                        res_id: this.currentResID,

                    };
                    var postData = new FormData();
                    var att_id = id["attach"];
                    // alert(id["attach"]);
                    if (att_id != false) {
                        // data.attachment_ids = [id["attach"]];
                        // alert(data);
                        self.Update_msg(data);
                    } else {
                        var def = setTimeout(function() {
                            $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: '/get_data',
                                cache: false,
                                contentType: false,
                                processData: false,
                                data: postData,
                            }).then(function(id) {
                                // data.attachment_ids = [id["attach"]];
                                self.Update_msg(data);
                                // });
                            }, 1000);
                        });
                    }
                });

                // var activeAttachmentID = $(ev.currentTarget).data('id');
                var data = {
                    // author_id: [5],
                    subject: false,
                    body: _t("Attachment created " + filename),
                    // attachment_ids: [1],
                    // model: 'document.internal.main',
                    res_id: this.currentResID,

                };
                var postData = new FormData();
                /*
                var values = {
                			file_name : filename,
                		};
                		ajax.jsonRpc('/get_data', 'call', values).then(function(data) {
                			var att_id = data["attach"];
                		    	console.log(att_id);
                		});
                */
                // postData.append('file_name', filename);
                // // alert(filename);
                // var def = $.ajax({
                //     type: "POST",
                //     dataType: 'json',
                //     url: '/get_data',
                //     cache: false,
                //     contentType: false,
                //     processData: false,
                //     data: postData,
                // }).then(function(id) {
                //     var att_id = id["attach"];
                //     // alert(id["attach"]);
                //     if (att_id != false) {
                //         // data.attachment_ids = [id["attach"]];
                //         // alert(data);
                //         self.Update_msg(data);
                //     } else {
                //         // var def = setTimeout(function() {
                //             $.ajax({
                //                 type: "POST",
                //                 dataType: 'json',
                //                 url: '/get_data',
                //                 cache: false,
                //                 contentType: false,
                //                 processData: false,
                //                 data: postData,
                //             }).then(function(id) {
                //                 // data.attachment_ids = [id["attach"]];
                //                 self.Update_msg(data);
                //             // });
                //         }, 1000);
                // }

                // });

            }
        },
    });

    Menu.include({
        events: {
            'click .o_menu_sections ': '_onAppNameClickedStataic',
        },

        _onAppNameClickedStataic: function(ev) {
            var self = this;
            _.each($(".o_menu_sections").find('.o_menu_entry_lvl_3'), function($item) {
                // console.log($item.href.indexOf($item.href.split('&')[1]))
                var act_vals = $item.href.indexOf($item.href.split('&')[1])
                if (act_vals > -1 || act_vals > -1) {
                    var postData = new FormData();
                    if (core.csrf_token) {
                        postData.append('csrf_token', core.csrf_token);
                    }
                    postData.append('href_link', $item.href)
                    var def = $.ajax({
                        type: "POST",
                        dataType: 'json',
                        url: '/get_badge_count_test',
                        cache: false,
                        contentType: false,
                        processData: false,
                        data: postData,
                    }).then(function(count) {
                        if (count["count"] == 0) {
                            $item.text = count["menu_label"]
                        } else {
                            $item.text = count["menu_label"]
                            var html_to_insert = "<span class='dd'> " + count["count"] + "</span>";
                            $item.innerHTML += html_to_insert;
                        }
                    });
                }
            });

            _.each($(".o_menu_sections").find('.o_menu_entry_lvl_2'), function($item) {
                var act_vals = $item.href.indexOf($item.href.split('&')[1])
                if (act_vals > -1 || act_vals > -1) {
                    var postData = new FormData();
                    if (core.csrf_token) {
                        postData.append('csrf_token', core.csrf_token);
                    }
                    postData.append('href_link', $item.href)
                    var def = $.ajax({
                        type: "POST",
                        dataType: 'json',
                        url: '/get_badge_count_test',
                        cache: false,
                        contentType: false,
                        processData: false,
                        data: postData,
                    }).then(function(count) {
                        if (count["count"] == 0) {
                            $item.text = count["menu_label"]
                        } else {
                            $item.text = count["menu_label"]
                            var html_to_insert = "<span class='dd'> " + count["count"] + "</span>";
                            $item.innerHTML += html_to_insert;
                        }
                    });

                }
            });
            // _.each($(".o_menu_sections").find('.o_menu_header_lvl_1'), function($item) {
            //     var act_vals = $item.text;
            //     if (act_vals) {
            //         var postData = new FormData();
            //         if (core.csrf_token) {
            //             postData.append('csrf_token', core.csrf_token);
            //         }
            //         postData.append('text', $item.text)
            //         var def = $.ajax({
            //             type: "POST",
            //             dataType: 'json',
            //             url: '/get_badge_count_head',
            //             cache: false,
            //             contentType: false,
            //             processData: false,
            //             data: postData,
            //         }).then(function(count) {
            //             if (count["count"] == 0) {
            //                 $item.text = count["menu_label"]
            //             } else {
            //                 $item.text = count["menu_label"]
            //                 var html_to_insert = "<span class='dd'>" + count["count"] + "</span>";
            //                 $item.innerHTML += html_to_insert;
            //             }
            //         });
            //     }
            // });
        },

        start: function() {
            var self = this;
            var def = this._super.apply(this, arguments);
            $('ul.o_menu_apps > li > a.full').bind('click', function(ev) {
                ev.preventDefault();
                var $target = $('.o_menu_apps .dropdown .show');
                if ($target.length == 0) {
                    self.on_load_badge();
                }
            });
            return def
        },
        on_load_badge: function() {
            var self = this;
            var badge_count = $('[id=menu_counter]')
            if (badge_count.length > 0) {
                $('[id=menu_counter]').remove();

            }
            _.each(this.menu_data.children, function(item) {
                var isEnterprise = odoo.session_info.server_version_info[5] === 'e';
                if (isEnterprise) {
                    var $menu_item = $('.o_apps').find('a[data-menu-id="' + item['id'] + '"]')
                } else {
                    var $menu_item = $('.dropdown-menu').find('a[data-menu-id="' + item['id'] + '"]')
                }
                var postData = new FormData();
                postData.append("menu_id", item['id']);
                if (core.csrf_token) {
                    postData.append('csrf_token', core.csrf_token);
                }
                var def = $.ajax({
                    type: "POST",
                    dataType: 'json',
                    url: '/get_badge_count',
                    cache: false,
                    contentType: false,
                    processData: false,
                    data: postData,
                }).then(function(count) {
                    $menu_item.append(QWeb.render("badge_on_menu_counter", {
                        widget: count
                    }));
                });
            })
            _.each($(".o_menu_sections").find('.o_menu_header_lvl_1'), function($item) {
                var act_vals = $item.text;
                if (act_vals) {
                    var postData = new FormData();
                    if (core.csrf_token) {
                        postData.append('csrf_token', core.csrf_token);
                    }
                    postData.append('text', $item.text)
                    var def = $.ajax({
                        type: "POST",
                        dataType: 'json',
                        url: '/get_badge_count_head',
                        cache: false,
                        contentType: false,
                        processData: false,
                        data: postData,
                    }).then(function(count) {
                        if (count["count"] == 0) {
                            $item.text = count["menu_label"]
                                // var html_to_insert = "<span class='dd'> " + $item.text + "</span>";
                                // $item.innerHTML += html_to_insert;
                        } else {
                            $item.text = count["menu_label"]
                            var html_to_insert = "<span class='dd'>" + count["count"] + "</span>";
                            $item.innerHTML += html_to_insert;
                        }
                    });
                }
            });
        },

    });
    return {
        'Menu': Menu,
    };


});