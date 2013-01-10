Ext.define('devilry_subjectadmin.view.detailedperiodoverview.ExportPeriodOverviewMenu', {
    extend: 'Ext.menu.Menu',
    alias: 'widget.exportperiodoverviewmenu',
    cls: 'devilry_subjectadmin',

    /**
     * @cfg {int} [period_id]
     */

    bodyTpl: [
        '<h4 style="margin-top: 0;">', gettext('MS Excel (Office Open XML)'), '</h4>',
        '<a href="{download_url}?format=xslx&download=1" class="btn btn-small btn-success"><i class="icon-download icon-white"></i> All data</a> ',
        '<a href="{download_url}?format=xslx&download=1&grade=grade" class="btn btn-small btn-inverse">',
            '<i class="icon-download icon-white"></i> Grades</a> ',
        '<a href="{download_url}?format=xslx&download=1&grade=points" class="btn btn-small btn-inverse">',
            '<i class="icon-download icon-white"></i> Points</a> ',
        '<a href="{download_url}?format=xslx&download=1&grade=is_passing_grade" class="btn btn-small btn-inverse">',
            '<i class="icon-download icon-white"></i> Passed/failed</a> ',

        '<h4 style="margin-top: 20px;">', gettext('Comma-separated values (CSV)'), '</h4>',
        '<a href="{download_url}?format=csv&download=1" class="btn btn-small btn-success"><i class="icon-download icon-white"></i> All data</a> ',
        '<a href="{download_url}?format=csv&download=1&grade=grade" class="btn btn-small btn-inverse">',
        '<i class="icon-download icon-white"></i> Grades</a> ',
        '<a href="{download_url}?format=csv&download=1&grade=points" class="btn btn-small btn-inverse">',
        '<i class="icon-download icon-white"></i> Points</a> ',
        '<a href="{download_url}?format=csv&download=1&grade=is_passing_grade" class="btn btn-small btn-inverse">',
        '<i class="icon-download icon-white"></i> Passed/failed</a> ',

        '<h4 style="margin-top: 20px;">', gettext('Other formats'), '</h4>',
        '<p class="muted">',
            gettext('These formats are mostly useful for programmers that need formats that are easy to parse. Refer to the Devilry website and Wiki for how to use the REST API.'),
        '</p>',
        '<a href="{restapi_url}?format=json" target="_blank" class="btn btn-small">JSON</a> ',
        '<a href="{restapi_url}?format=yaml" target="_blank" class="btn btn-small">YAML</a> ',
        '<a href="{restapi_url}?format=xml" target="_blank" class="btn btn-small">XML</a> ',
        '<a href="{restapi_url}" target="_blank" class="btn btn-small">REST API</a> '
    ],

    
    initComponent: function() {
        Ext.apply(this, {
            plain: true,
            maxWidth: 500,
            layout: 'fit',
            items: {
                xtype: 'box',
                cls: 'bootstrap',
                padding: 10,
                itemId: 'body',
                tpl: this.bodyTpl,
                style: 'white-space: normal !important;',
                data: {
                    period_id: this.period_id,
                    restapi_url: Ext.String.format(
                        '{0}/devilry_subjectadmin/rest/detailedperiodoverview/{1}',
                        DevilrySettings.DEVILRY_URLPATH_PREFIX, this.period_id),
                    download_url: Ext.String.format(
                        '{0}/devilry_subjectadmin/export/periodoverview/{1}',
                        DevilrySettings.DEVILRY_URLPATH_PREFIX, this.period_id)
                }
            }
        });
        this.callParent(arguments);
    }
});
