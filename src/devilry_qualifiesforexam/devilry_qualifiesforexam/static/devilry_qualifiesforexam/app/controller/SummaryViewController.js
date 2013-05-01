Ext.define('devilry_qualifiesforexam.controller.SummaryViewController', {
    extend: 'Ext.app.Controller',

    views: [
        'summaryview.SummaryView'
    ],

    models: [
        'NodeDetail'
    ],
    stores: [
        'Statuses'
    ],

    refs: [{
        ref: 'summaryView',
        selector: 'summaryview'
    }],

    init: function() {
        this.control({
            'viewport summaryview summaryviewgrid': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        this.getSummaryView().setLoading();
        this.application.breadcrumbs.set([], gettext('Loading') + ' ...');
        this.node_id = this.getSummaryView().node_id;
        this.application.setTitle(gettext('Summary - Qualifies for final exams'));
        this.getStatusesStore().loadWithinNode(this.node_id, {
            scope: this,
            callback: function(records, op) {
                if(op.success) {
                    this._onLoadSuccess(records);
                } else {
                    this._onLoadError( op );
                }
            }
        });
    },

    _onLoadSuccess: function(records) {
        this.getSummaryView().setLoading(false);
        this._loadNodeDetails();
    },


    _loadNodeDetails: function() {
        this.getNodeDetailModel().load(this.node_id, {
            scope: this,
            callback: function ( records, op ) {
                if( op.success ) {
                    this._onLoadNodeDetailsSuccess(records);
                } else {
                    this._onLoadError(op);
                }
            }
        });
    },

    _onLoadNodeDetailsSuccess:function ( record ) {
        var path = record.get('path');
        var breadcrumb = [];
        for (var i = 0; i < path.length; i++) {
            var element = path[i];
            breadcrumb.push({
                text: element.short_name,
                url: devilry_qualifiesforexam.utils.UrlLookup.nodeadmin_node_details(element.id)
            });
        }
        this.application.breadcrumbs.set( breadcrumb, gettext('Summary - Qualifies for final exams'));
    },

    _onLoadError:function (op) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrorsFromOperation(op);
        this.application.getAlertmessagelist().addMany(
            errorhandler.errormessages, 'error', true );
    }
});
