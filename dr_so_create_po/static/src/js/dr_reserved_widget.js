odoo.define('dr_so_create_po.ReservedWidget', function (require) {
"use strict";

var Widget = require('web.Widget');
var widget_registry = require('web.widget_registry');
var core = require('web.core');

var QWeb = core.qweb;
var _t = core._t;

var ReservedWidget = Widget.extend({
    template: 'dr_so_create_po.ReservedWidget',
    events: _.extend({}, Widget.prototype.events, {
        'click .fa-info-circle': '_onClickButton',
    }),

    init: function (parent, params) {
        this.data = params.data;
        this._super.apply(this, arguments);
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._setPopOver();
        });
    },

    updateState: function (state) {
        this.$el.popover('dispose');
        var candidate = state.data[this.getParent().currentRow];
        if (candidate) {
            this.data = candidate.data;
            this.renderElement();
            this._setPopOver();
        }
    },

    _setPopOver: function () {
        var $content = $(QWeb.render('dr_so_create_po.ReservedWidgetPopOver', {
            data: this.data,
        }));
        var options = {
            content: $content,
            html: true,
            placement: 'left',
            title: _t('Reserved Availability'),
            trigger: 'focus',
            delay: {'show': 0, 'hide': 100 },
        };
        this.$el.popover(options);
    },

    _onClickButton: function () {
        this.$el.find('.fa-info-circle').prop('special_click', true);
    },
});

widget_registry.add('dr_reserved_widget', ReservedWidget);

return ReservedWidget;

});
