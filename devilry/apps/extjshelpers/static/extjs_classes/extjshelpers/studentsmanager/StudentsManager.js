Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    cls: 'studentsmanager',

    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid',
        'devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow',
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.SetListOfUsers',
        'devilry.gradeeditors.EditManyDraftEditorWindow',
        'devilry.extjshelpers.studentsmanager.MultiResultWindow',
        'devilry.extjshelpers.MenuHeader',
        'devilry.extjshelpers.HelpWindow',
        'Ext.ux.grid.Printer',
        'devilry.extjshelpers.GridPrintButton'
    ],

    mixins: {
        createFeedback: 'devilry.extjshelpers.studentsmanager.StudentsManagerCreateFeedback',
        manageDeadlines: 'devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines',
        closeOpen: 'devilry.extjshelpers.studentsmanager.StudentsManagerCloseOpen',
        addDeliveries: 'devilry.administrator.studentsmanager.AddDeliveriesMixin'
    },

    /**
    * @cfg
    * Use the administrator RESTful interface to store drafts? If this is
    * ``false``, we use the examiner RESTful interface.
    */
    isAdministrator: false,

    /**
     * @cfg
     */
    gradeeditor_config_model: undefined,

    /**
     * @cfg
     */
    deadlinemodel: undefined,

    /**
     * @cfg
     */
    assignmentid: undefined,

    /**
     * @cfg
     */
    assignmentrecord: undefined,

    /**
     * @cfg
     */
    periodid: undefined,


    feedbackTooltip: Ext.create('Ext.XTemplate',
        'Select one or more students/groups and click this button to give them feedback.',
        '<tpl if="delivery_types == 0">',
        '   You should only use this in simple cases.',
        '   <tpl if="isAdministrator">',
        '       We reccommend that you set yourself, or someone else, as examiner, and use the examiner interface.',
        '   </tpl>',
        '   <tpl if="!isAdministrator">',
        '       We reccommend that you use the Todo-list unless you need to give feedback to many students in bulk.',
        '   </tpl>',
        '</tpl>'
    ),

    _createAssignmentgroupStore: function() {
        var model = Ext.ModelManager.getModel(this.assignmentgroupmodelname);
        this.assignmentgroupstore = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
    },

    initComponent: function() {
        this.defaultPageSize = 30;
        this.role = this.isAdministrator? 'administrator': 'examiner';
        this.assignmentgroupmodelname = Ext.String.format('devilry.apps.{0}.simplified.SimplifiedAssignmentGroup', this.role);
        this._createAssignmentgroupStore();
        this.gradeeditor_config_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer.addListener('setRecord', this.onLoadRegistryItem, this);

        this.progressWindow = Ext.create('devilry.extjshelpers.studentsmanager.MultiResultWindow', {
            isAdministrator: this.isAdministrator
        });

        this.giveFeedbackToSelectedArgs = {
            text: '<i class="icon-pencil"></i> ' + gettext('Give feedback to selected'),
            cls: 'bootstrap',
            listeners: {
                scope: this,
                click: this.onGiveFeedbackToSelected,
                render: function(button) {
                    if(!this.registryitem_recordcontainer.record) {
                        button.getEl().mask('Loading'); // TODO: Only mask the affected buttons
                    }
                    var tip = Ext.create('Ext.tip.ToolTip', {
                        target: button.getEl(),
                        title: gettext('Give feedback to selected'),
                        html: this.feedbackTooltip.apply({
                            delivery_types: this.assignmentrecord.get('delivery_types'),
                            isAdministrator: this.isAdministrator
                        }),
                        width: 350,
                        anchor: 'top',
                        dismissDelay: 30000 // Hide after 30 seconds hover
                    });
                }
            }
        };
        this.giveFeedbackButton = Ext.widget('button', Ext.Object.merge({
            scale: 'medium'
        }, this.giveFeedbackToSelectedArgs));

        var me = this;

        var topBarItems = [{
            xtype: 'searchfield',
            width: 400,
            emptyText: gettext('Search') + ' ...'
        }, {
            xtype: 'button',
            text: 'x',
            handler: function() { me.setFilter(''); }
        }, {
            xtype: 'button',
            text: '<i class="icon-filter"></i> ' + gettext('Filter'),
            cls: 'bootstrap',
            menu: {
                xtype: 'menu',
                plain: true,
                items: this.getFilters()
            }
        }, {
            xtype: 'button',
            text: gettext('All on one page'),
            enableToggle: true,
            listeners: {
                scope: this,
                toggle: function(btn, pressed) {
                    this.assignmentgroupstore.pageSize = pressed? 100000: this.defaultPageSize;
                    if(pressed) {
                        this.assignmentgroupstore.currentPage = 1;
                    }
                    this.assignmentgroupstore.load();
                }
            }
        }, '->'
        //{
            //xtype: 'gridprintbutton',
            //listeners: {
                //scope: this,
                //print: this._onPrint,
                //printformat: this._onPrintFormat
            //}
        //}
        ];


        if(this.assignmentrecord.get('delivery_types') === 0) {
            topBarItems.push({
                xtype: 'button',
                text: '<i class="icon-download"></i> ' + gettext('Download all deliveries'),
                cls: 'bootstrap',
                listeners: {
                    scope: this,
                    click: this._onDownload
                }
            });
        }

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'panel',
                flex: 1,
                layout: 'fit',
                frame: true,
                border: false,
                items: [{
                    xtype: 'studentsmanager_studentsgrid',
                    store: this.assignmentgroupstore,
                    assignmentid: this.assignmentid,
                    assignmentrecord: this.assignmentrecord,
                    isAdministrator: this.isAdministrator,
                    isAnonymous: this.assignmentrecord.data.anonymous,
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'top',
                        items: topBarItems
                    }]
                }],

                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'bottom',
                    ui: 'footer',
                    items: this.getToolbarItems()
                }]
            }]
        });
        this.callParent(arguments);
        this.setSearchfieldAttributes();

        this.addListener('render', function() {
            //this.up('window').addListener('show', this.onManuallyCreateUsers, this);
            //this.up('window').addListener('show', function() {
                //Ext.defer(this.onReplaceExaminers, 1000, this);
                //Ext.defer(this.onRandomDistributeExaminers, 1000, this);
                //Ext.defer(this.onImportExaminersFromAnotherAssignmentInCurrentPeriod, 1000, this);
            //}, this);
            this.down('studentsmanager_studentsgrid').on('itemcontextmenu', this.onGridContexMenu, this);
        }, this);
        this.loadGradeEditorConfigModel();

        this.loadFirstPage();
    },

    _onDownload: function() {
        window.location.href = Ext.String.format('compressedfiledownload/{0}', this.assignmentid);
    },

    _onPrint: function() {
        Ext.ux.grid.Printer.print(this.down('studentsmanager_studentsgrid'), true);
    },

    _onPrintFormat: function() {
        Ext.ux.grid.Printer.print(this.down('studentsmanager_studentsgrid'), false);
    },

    getFilters: function() {
        var me = this;
        var filters = [{xtype: 'menuheader', html: 'Open/closed'}, {
            text: gettext('Open'),
            handler: function() { me.setFilter('is_open:yes'); }
        }, {
            text: gettext('Closed'),
            handler: function() { me.setFilter('is_open:no'); }
        }, {xtype: 'menuheader', html: gettext('Grade')}, {
            text: gettext('Passed'),
            handler: function() { me.setFilter('feedback__is_passing_grade:yes'); }
        }, {
            text: gettext('Failed'),
            handler: function() { me.setFilter('feedback__is_passing_grade:no'); }
        }, {xtype: 'menuheader', html: gettext('Deliveries')}, {
            text: interpolate(gettext('Has %(deliveries_term)s'), {deliveries_term: gettext('deliveries')}, true),
            handler: function() { me.setFilter('number_of_deliveries:>:0'); }
        }, {
            text: interpolate(gettext('No %(deliveries_term)s'), {deliveries_term: gettext('deliveries')}, true),
            handler: function() { me.setFilter('number_of_deliveries:0'); }
        }, {xtype: 'menuheader', html: gettext('Feedback')}, {
            text: interpolate(gettext('Has %(feedback_term)s'), {feedback_term: gettext('feedback')}, true),
            handler: function() { me.setFilter('feedback:>=:0'); }
        }, {
            text: interpolate(gettext('No %(feedback_term)s'), {feedback_term: gettext('feedback')}, true),
            handler: function() { me.setFilter('feedback:none'); }
        }, {xtype: 'menuheader', html: gettext('Delivery type')}, {
            text: gettext('Electronic'),
            handler: function() { me.setFilter('feedback__delivery__delivery_type:0'); }
        }, {
            text: gettext('Non-electronic'),
            handler: function() { me.setFilter('feedback__delivery__delivery_type:1'); }
        }, {
            text: interpolate(gettext('From previous %(period_term)s'), {period_term: gettext('period')}, true),
            handler: function() { me.setFilter('feedback__delivery__delivery_type:2'); }
        }];
        if(this.assignmentrecord.data.anonymous) {
            filters.push({
                xtype: 'menuheader', html: gettext('Candidate ID')
            });
            filters.push({
                text: gettext('Missing candidate ID'),
                handler: function() { me.setFilter('candidates__identifier:none'); }
            });
        }
        return filters;
    },

    getToolbarItems: function() {
        var advanced = Ext.Array.merge(
            [{xtype: 'menuheader', html: gettext('On single group')}], this.getOnSingleMenuItems(),
            [{xtype: 'box', height: 12}],
            [{xtype: 'menuheader', html: gettext('On one or more group')}], this.getOnManyMenuItems()
        );

        return [{
            text: '<i class="icon-question-sign"></i> ' + gettext('Help'),
            cls: 'bootstrap',
            scale: 'medium',
            listeners: {
                scope: this,
                click: this.onHelp
            }
        }, '->', {
            xtype: 'button',
            text: gettext('Advanced'),
            scale: 'medium',
            menu: {
                xtype: 'menu',
                plain: true,
                items: advanced 
            }
        }, this.giveFeedbackButton];
    },

    getOnSingleMenuItems: function() {
        var menu = [{
            text: gettext('Open in examiner interface'),
            listeners: {
                scope: this,
                click: this.onOpenExaminerInterface
            }
        }];

        if(this.assignmentrecord.data.delivery_types === this.deliveryTypes.TYPE_ELECTRONIC) {
            menu.push({
                text: gettext('Add non-electronic delivery'),
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this.onAddNonElectronicDelivery
                }
            });
        }

        return menu;
    },

    getOnManyMenuItems: function() {
        var items = [{
            text: gettext('Close/open selected'),
            menu: [{
                text: gettext('Close selected'),
                listeners: {
                    scope: this,
                    click: this.onCloseGroups
                }
            }, {
                text: gettext('Open selected'),
                listeners: {
                    scope: this,
                    click: this.onOpenGroups
                }
            }]
        }];
        if(this.assignmentrecord.get('delivery_types') !== this.deliveryTypes.TYPE_NON_ELECTRONIC) {
            items.push({
                text: interpolate(gettext('Add %(deadline_term)s'), {
                    deadline_term: gettext('deadline')
                }, true),
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this.onAddDeadline
                }
            });
        }
        return items;
    },

    onHelp: function() {
        Ext.widget('helpwindow', {
            title: gettext('Help'),
//            maximizable: true,
//            maximized: true,
            helptpl: Ext.create('Ext.XTemplate',
                '<div class="section helpsection">',
                '   <h1>Guides</h1>',
                '   <p>This is a complex view that supports a huge amount of different workflows. Please visit the <a href="{DevilrySettings.DEVILRY_HELP_URL}" target="_blank">primary help section</a> for guides and more help.</p>',
                '   <h1>Search</h1>',
                '   <p>Use the search box to search for more or less anything. Examples are candidate IDs and usernames of students and examiners.</p>',
                '   <h1>About each column</h1>',
                '   <h2>The first column (with no header)</h2>',
                '       <p>Contains notifications. Unless something is wrong, you will see <em>open</em> or <em>close</em>. When a group is open, students can add more deliveries. When a group is closed, it is not possible to add more deliveries.</p>',
                '   <h2>Students</h2>',
                '       <p>Usernames of all students on each group. If the assignment is <em>anonymous</em>, this column shows the <em>cadidate ID</em> instead of the username.</p>',
                '   <h2>Deliveries</h2>',
                '       <p>Number of deliveries</p>',
                '   <h2>Latest feedback</h2>',
                '       <h3>Points</h3>',
                '       <p>Number of points achieved by the group on this assignment. Points are used for statistics, and they are not available to students.</p>',
                '       <h3>Grade</h3>',
                '       <p>The grade achieved by the group on this assignment. A grade columns cell has 3 parts:</p><ul>',
                '           <li>It is either passed or failed. If the status of this has any consequence for the students, depends on if the assignment must be passed or not.</li>',
                '           <li>A textual representation of the points. The format of this text depends on the <em>grade editor</em> used on this assignment.</li>',
                '           <li>Type of delivery. This may be <em>electronic</em>, <em>non-electronic</em> or <em>From previous period</em>. The last is for groups marked as delivered in a previous period.</li>',
                '   <h2>Examiners</h2>',
                '       <p>Usernames of examiners.</p>',
                '   <h2>Active deadline</h2>',
                '       <p>The deadline that students deliver on. Always the <em>latest</em> deadline.</p>',
                '   <h2>Group name</h2>',
                '       <p>The name of the group. Group names are usually used for project assignments where each project has a specific name.</p>',
                '</div>'
            ),
            helpdata: {DevilrySettings: DevilrySettings}
        }).show();
    },

    /**
     * @private
     */
    onSelectNone: function() {
        Ext.MessageBox.alert('No element(s) selected', 'You must select at least one group to use the selected action.');
    },

    /**
     * @private
     */
    noneSelected: function() {
        return this.getSelection().length === 0;
    },

    /**
     * @private
     */
    onNotSingleSelected: function() {
        Ext.MessageBox.alert('Invalid selection', 'You must select exactly one group to use the selected action.');
    },

    /**
     * @private
     */
    singleSelected: function() {
        return this.getSelection().length === 1;
    },

    /**
     * @private
     */
    getSelection: function() {
        //if(this.contexSelectedItem) {
            //return [this.contexSelectedItem];
        //}
        return this.down('studentsmanager_studentsgrid').selModel.getSelection();
    },

    /**
     * @private
     */
    loadFirstPage: function() {
        this.assignmentgroupstore.currentPage = 1;
        this.refreshStore();
    },

    /**
     * @private
     */
    createRecordFromStoreRecord: function(record) {
        var modelname = Ext.String.format('devilry.apps.{0}.simplified.SimplifiedAssignmentGroup', this.role);
        var editRecord = Ext.create(modelname, {
            // NOTE: Very important that this is all the editablefields, since any missing fields will be None!
            id: record.data.id,
            name: record.data.name,
            is_open: record.data.is_open,
            parentnode: record.data.parentnode
        });
        return editRecord;
    },


    /**
     * @private
     */
    onOpenExaminerInterface: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }
        var record = this.getSelection()[0];
        window.open(Ext.String.format('../assignmentgroup/{0}', record.data.id), '_blank');
    },

    /**
     * @private
     */
    onGridContexMenu: function(grid, record, index, item, ev) {
        var items;
        if(this.noneSelected()) {
            //items = [{xtype: 'menuheader', html: 'Select at least one group'}];
            return;
        } else {
            items = this.getGridContextMenuItems();
        }
        ev.stopEvent();
        var gridContextMenu = new Ext.menu.Menu({
            plain: true,
            items: items
            //listeners: {
                //scope: this,
                //hide: this.onGridContexMenuHide
                //}
        });
        gridContextMenu.showAt(ev.xy);
    },

    /**
     * @private
     */
    getGridContextMenuItems: function() {
        if(this.singleSelected()) {
            return this.getContexMenuSingleSelectItems();
        } else {
            return this.getContexMenuManySelectItems();
        }
    },

    getContexMenuManySelectItems: function() {
        return Ext.Array.merge([this.giveFeedbackToSelectedArgs], this.getOnManyMenuItems());
    },

    getContexMenuSingleSelectItems: function() {
        return Ext.Array.merge(
            [{xtype: 'menuheader', html: 'On single group'}], this.getOnSingleMenuItems(),
            [{xtype: 'box', height: 12}],
            [{xtype: 'menuheader', html: 'On one or more group'}], this.getContexMenuManySelectItems()
        );
    },

    /**
     * @private
     */
    //onGridContexMenuHide: function(grid, record, index, item, ev) {
        //this.contexSelectedItem = undefined;
    //},

    
    /**
     * @private
     */
    setSearchfieldAttributes: function() {
        var searchfield = this.down('searchfield');
        searchfield.addListener('newSearchValue', this.search, this);
        searchfield.addListener('emptyInput', function() {
            this.search("");
        }, this);
    },
    
    /**
     * @private
     */
    search: function(searchstring) {
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: searchstring,
            alwaysAppliedFilters: [{
                field: 'parentnode',
                comp: 'exact',
                value: this.assignmentid
            }]
        });
        var extraParams = this.assignmentgroupstore.proxy.extraParams;
        this.assignmentgroupstore.proxy.extraParams = parsedSearch.applyToExtraParams(extraParams, []);
        this.assignmentgroupstore.proxy.extraParams.orderby = Ext.JSON.encode([]);
        this.assignmentgroupstore.loadPage(1, {
            scope: this,
            callback: function(records, operation, success) {
            }
        });
    },

    /**
     * @private
     */
    setFilter: function(filterstr) {
        var searchfield = this.down('searchfield');
        searchfield.setValue(filterstr);
    },

    /**
     * @private
     * Reftesh store by re-searching for the current value.
     */
    refreshStore: function() {
        var searchfield = this.down('searchfield');
        this.search(searchfield.getValue());
    }
});
