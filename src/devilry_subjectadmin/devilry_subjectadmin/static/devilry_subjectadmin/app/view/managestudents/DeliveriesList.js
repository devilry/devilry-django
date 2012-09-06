Ext.define('devilry_subjectadmin.view.managestudents.DeliveriesList', {
    extend: 'Ext.Component',
    alias: 'widget.deliverieslist',
    cls: 'devilry_subjectadmin_deliverieslist bootstrap',

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],


    /**
     * @cfg {Array} [deadlines]
     */

    /**
     * @cfg {String} [assignment_id]
     */

    /**
     * @cfg {Ext.data.Model} [groupRecord]
     */

    tpl: [
        '<h3>', gettext('Deliveries'), '</h3>',
        '<tpl if="deliveries">',
            '<tpl if="deliveries.length &gt; 0">',
                '<ul>',
                    '<tpl for="deliveries">',
                        '<li><a class="delivery_link" href="{parent.delivery_link_prefix}{id}" data-deliveryid="{id}">',
                            gettext('Delivery'), ' #{number}',
                        '</a></li>',
                    '</tpl>',
                '</ul>',
            '</tpl>',
        '</tpl>'
    ],

    data: {
        deliveries: undefined
    },

    initComponent: function() {
        this.addListener({
            element: 'el',
            delegate: 'a.delivery_link',
            scope: this,
            click: function(e) {
                e.preventDefault();
                var element = Ext.dom.Element(e.target);
                this.fireEvent('delivery_link_clicked', element.getAttribute('data-deliveryid'));
            }
        });
        this.callParent(arguments);
    },

    _deliveriesAsFlatArray: function(deadlines) {
        var deliveries = [];
        Ext.Array.each(deadlines, function(deadline) {
            deliveries = deliveries.concat(deadline.deliveries);
        }, this);
        return deliveries;
    },

    populate: function(assignment_id, group_id, deadlines) {
        this.update({
            deliveries: this._deliveriesAsFlatArray(deadlines),
            delivery_link_prefix: devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
                assignment_id, group_id)
        });
    }
});
