Ext.define('devilry_subjectadmin.view.managestudents.ManageTagsOnSingle', {
    extend: 'Ext.container.Container',
    alias: 'widget.managetagsonsingle',
    cls: 'devilry_subjectadmin_managetagsonsingle',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_subjectadmin.view.managestudents.TagsInGroupGrid',
        'devilry_subjectadmin.view.managestudents.TagsHelp',
        'devilry_extjsextras.ContainerWithEditTitle'
    ],

    constructor: function(config) {
        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            /**
             * @event
             * Fired when edit-tags is clicked.
             * @param panel This panel.
             */
            'edit_tags'
        );
        this.callParent([config]);
    },

    initComponent: function() {
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'containerwithedittitle',
                anchor: '100%',
                title: gettext('Tags'),
                listeners: {
                    scope: this,
                    edit: function() {
                        this.fireEvent('edit_tags', this);
                    }
                }
            }, {
                xtype: 'container',
                itemId: 'cardBody',
                layout: 'card',
                deferredRender: true,
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
                        anchor: '100%'
                    }, {
                        xtype: 'moreinfobox',
                        anchor: '100%',
                        moretext: gettext('Tags help ...'),
                        lesstext: gettext('Hide help'),
                        small_morelink: true,
                        moreWidget: {
                            xtype: 'box',
                            html: [
                                '<p>',
                                    devilry_subjectadmin.view.managestudents.TagsHelp.getIntroText(),
                                '</p>',
                                devilry_subjectadmin.view.managestudents.TagsHelp.getDetailsUl(),
                                '<p><small class="muted">', devilry_subjectadmin.view.managestudents.TagsHelp.getPeriodNote(), '</small></p>'
                            ].join('')
                        }
                    }]
                }, {
                    xtype: 'choosetagspanel',
                    itemId: 'setTagsPanel',
                    allowNoTags: true,
                    id: 'single_set_tags_panel',
                    buttonText: gettext('Save tags')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
