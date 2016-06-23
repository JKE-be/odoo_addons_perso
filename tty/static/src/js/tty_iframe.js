odoo.define('web.form_widget_tty', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var form_common = require('web.form_common');


    var _t = core._t;

    var FieldTty = form_common.AbstractField.extend(form_common.ReinitializeFieldMixin, {
        template: 'FieldTty',
        render_value: function() {
            if (this.get('effective_readonly')) {
                var url = this.get('value');
                this.$el.find('iframe').attr('src', url);
            }
        },
    });

    core.form_widget_registry.add('tty', FieldTty);

    return {
        FieldTty: FieldTty,
    };
});