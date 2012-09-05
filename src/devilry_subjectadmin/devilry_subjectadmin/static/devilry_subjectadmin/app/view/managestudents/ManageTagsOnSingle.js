Ext.define('devilry_subjectadmin.view.managestudents.ManageTagsOnSingle', {
    extend: 'Ext.container.Container',
    alias: 'widget.managetagsonsingle',
    cls: 'devilry_subjectadmin_managetagsonsingle',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_subjectadmin.view.managestudents.TagsInGroupGrid'
    ],

    /**
     * @cfg {Ext.data.Store} tagsStore (required)
     */

    more_text: gettext('TODO'),

    initComponent: function() {
        var tags = [];
        this.tagsStore.each(function(tagRecord) {
            tags.push(tagRecord.get('tag'));
        }, this);
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'box',
                anchor: '100%',
                tpl: [
                    '<h4>',
                        '{heading}',
                    '</h4>'
                ],
                data: {
                    heading: gettext('Tags'),
                }
            }, {
                xtype: 'container',
                itemId: 'cardBody',
                layout: 'card',
                anchor: '100%',
                items: [{
                    xtype: 'panel',
                    itemId: 'helpAndButtonsContainer',
                    id: 'single_tags_help_and_buttons_container',
                    border: false,
                    frame: false,
                    layout: 'anchor',
                    items: [{
                        xtype: 'tagsingroupgrid',
                        store: this.tagsStore,
                        anchor: '100%'
                    }, {
                        xtype: 'moreinfobox',
                        anchor: '100%',
                        moretext: gettext('Tags help ...'),
                        lesstext: gettext('Hide help'),
                        introtext: '',
                        small_morelink: true,
                        moreWidget: {
                            xtype: 'box',
                            html: this.more_text
                        }
                    }],
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        ui: 'footer',
                        padding: 0,
                        defaults: {
                            xtype: 'button',
                            scale: 'medium',
                            minWidth: 100
                        },
                        items: [{
                            text: gettext('Edit tag(s)'),
                            itemId: 'setTagButton',
                            id: 'single_set_tags_button',
                            tooltip: gettext('Edit tag(s) on this group.')
                        }]
                    }],
                }, {
                    xtype: 'choosetagspanel',
                    itemId: 'setTagsPanel',
                    initialValue: tags.join(','),
                    allowNoTags: true,
                    id: 'single_set_tags_panel',
                    buttonText: gettext('Save tags')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
