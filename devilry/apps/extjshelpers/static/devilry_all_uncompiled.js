/**
 * Base class for proxy error handling.
 */
Ext.define('devilry_extjsextras.ProxyErrorHandler', {
    constructor: function() {
        this.errormessages = [];
        this.fielderrors = {};
    },

    /** Check if the list of errormessages and fielderrors are empty, and
     * return ``true`` if one of them contains at least one error message. */
    hasErrors: function() {
        return this.errormessages.length > 0 || Ext.Object.getSize(this.fielderrors) > 0;
    },

    /**
     * Add error from an ``Ext.data.Operation`` object. Uses
     * {@link #getErrorMessageFromOperation} to find the error message.
     *
     * @return The number of errors added.
     */
    addErrorsFromOperation: function(operation) {
        var httpError = this.getErrorMessageFromOperation(operation);
        if(!Ext.isEmpty(httpError)) {
            this.errormessages.push(httpError);
        }
    },

    _formatTpl: function(tpl, data) {
        return Ext.create('Ext.XTemplate', tpl).apply(data);
    },

    _formatUrl: function(url) {
        return Ext.String.format('<a href="{0}" target="_blank">{0}</a>', url);
    },

    parseHttpError: function(error, request) {
        var message;
        if(error.status === 0) {
            message = this._formatTpl(gettext('Could not connect to server at URL "{url}".'), {
                url: this._formatUrl(request.url)
            });
        } else {
            message = this._formatTpl('The server responded with error message <em>{status}: {statusText}</em> when we made a {method}-request to URL {url}.', {
                status: error.status,
                statusText: error.statusText,
                method: request.method,
                url: this._formatUrl(request.url)
            });
        }
        return message;
    },

    /** Formats the error object returned by ``Ext.data.Operation.getError(). as
     * a string that can be displayed to users.
     * 
     * @return The formatted string.
     * */
    getErrorMessageFromOperation: function(operation) {
        var error = operation.getError();
        if(error === undefined) {
            return null;
        }
        return this.parseHttpError(error, operation.request);
    },

    /**
     * Copy errormessages and fielderrors into a single array, and return the array.
     * Each item in the array is a string. Fielderrors are formatted as
     * ``"{fieldname}: {message}"``.
     */
    asArrayOfStrings: function() {
        var messages = Ext.clone(this.errormessages);
        Ext.Object.each(this.fielderrors, function(message, fieldname) {
            messages.push(Ext.String.format('{0}: {1}', fieldname, message));
        }, this);
        return messages;
    },

    /**
     * Uses #asArrayOfStrings to flatten the error messages, then put these
     * messages in a HTML unordered list.
     * */
    asHtmlList: function() {
        return Ext.create('Ext.XTemplate',
            '<ul>',
            '<tpl for="messages">',
                '<li>{.}</li>',
            '</tpl>',
            '</ul>'
        ).apply({
            messages: this.asArrayOfStrings()
        });
    }
});


/** A textfield for searching.
 *
 * */
Ext.define('devilry.extjshelpers.SearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.searchfield',
    fieldCls: 'widget-searchfield',

    config: {
        /**
         * @cfg
         * Delay before a search is performed in milliseconds. Defaults to 500.
         * The search is not performed if the user changes the input text before
         * ``searchdelay`` is over.
         */
        searchdelay: 500
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.addEvents('emptyInput');
        this.addEvents('newSearchValue');
    },

    initComponent: function() {
        this.on('specialKey', function(field, e) {
            this.handleSpecialKey(e);
        }, this);
        this.on('change', function(field, newValue, oldValue) {
            this.handleChange(newValue);
        }, this);
        this.callParent(arguments);
    },

    triggerSearch: function(value) {
        var currentValue = this.getValue();
        var noNewInput = value == currentValue;
        if(noNewInput) {
            this.fireEvent('newSearchValue', value);
        }
    },

    handleSpecialKey: function(e) {
        if(e.getKey() == e.ENTER) {
            this.fireEvent('newSearchValue', this.getValue());
        } else if(e.getKey() == e.ESC) {
            this.fireEvent('emptyInput');
        }
    },

    handleChange: function(newValue) {
        var me = this;
        if(Ext.String.trim(newValue) == "") {
            this.fireEvent('emptyInput');
        } else {
            Ext.Function.defer(function() {
                me.triggerSearch(newValue);
            }, this.searchdelay);
        }
    }
});


Ext.define('devilry.statistics.LabelManager', {
    extend: 'Ext.util.Observable',
    
    config: {
        loader: undefined
    },
    application_id: 'devilry.statistics.Labels',

    constructor: function(config) {
        this.initConfig(config);
        this.addEvents({
            "changedMany": true
        });
        this.callParent(arguments);
    },

    _onError: function(what, response) {
        Ext.getBody().unmask();
        var httperror = 'Lost connection with server';
        if(response.status !== 0) {
            httperror = Ext.String.format('{0} {1}', response.status, response.statusText);
        }
        Ext.MessageBox.show({
            title: Ext.String.format('Failed to {0} labels', what),
            msg: '<p>This is usually caused by an unstable server connection. <strong>Please re-try saving labels</strong>.</p>' +
                Ext.String.format('<p>Error details: {0}</p>', httperror),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    },

    _onFinished: function() {
        Ext.getBody().unmask();
        window.location.search = 'open_students=yes';
    },
    
    _changeRequired: function(student, match, label) {
        var has_label = student.hasLabel(label);
        if(match && !has_label) {
            return 'create';
        } else if(!match && has_label) {
            return 'delete';
        } else {
            return false;
        }
    },

    _sendRestRequest: function(args) {
        Ext.apply(args, {
            url: Ext.String.format('{0}/administrator/restfulsimplifiedrelatedstudentkeyvalue/', DevilrySettings.DEVILRY_URLPATH_PREFIX)
        });
        Ext.Ajax.request(args);
    },

    _create: function(toBeCreated) {
        if(toBeCreated.length === 0) {
            this._onFinished();
            return;
        }
        Ext.getBody().mask('Creating labels', 'page-load-mask');
        this._sendRestRequest({
            params: Ext.JSON.encode(toBeCreated),
            method: 'POST',
            scope: this,
            callback: function(op, success, response) {
                if(success) {
                    this._onFinished();
                } else {
                    this._onError('create', response);
                }
            }
        });
    },

    _delete: function(toBeDeleted, toBeCreated) {
        if(toBeDeleted.length === 0) {
            this._create(toBeCreated);
            return;
        }
        Ext.getBody().mask('Deleting current labels', 'page-load-mask');
        this._sendRestRequest({
            params: Ext.JSON.encode(toBeDeleted),
            method: 'DELETE',
            scope: this,
            callback: function(op, success, response) {
                if(success) {
                    this._create(toBeCreated);
                } else {
                    this._onError('delete', response);
                }
            }
        });
    },

    _createLabelObj: function(student, label, student_can_read) {
        return {
            relatedstudent: student.get('relatedstudent_id'),
            application: this.application_id,
            key: label,
            student_can_read: (student_can_read === true)
        };
    },

    _addToAppropriateChagelist: function(toBeCreated, toBeDeleted, match, student, label, student_can_read) {
        var changeRequired = this._changeRequired(student, match, label);
        if(changeRequired === 'create') {
            toBeCreated.push(this._createLabelObj(student, label, student_can_read));
        } else if(changeRequired === 'delete') {
            var labelId = student.getLabelId(label);
            if(labelId === -1) {
                throw "Label not found";
            }
            toBeDeleted.push(labelId);
        }
    },

    setLabels: function(options) {
        var labelRecords = [];
        Ext.getBody().mask('Updating labels', 'page-load-mask');
        this.loader.clearFilter();

        var toBeCreated = [];
        var toBeDeleted = [];
        Ext.each(this.loader.store.data.items, function(student) {
            var match = Ext.bind(options.filter, options.scope)(student);
            this._addToAppropriateChagelist(toBeCreated, toBeDeleted, match, student, options.label, options.student_can_read);
            this._addToAppropriateChagelist(toBeCreated, toBeDeleted, !match, student, options.negative_label, options.student_can_read);
        }, this);
        this._delete(toBeDeleted, toBeCreated);
    }
});


/** Singleton class with methods for form error handling. No state is stored in
 * the singleton. */
Ext.define('devilry_extjsextras.form.ErrorUtils', {
    singleton: true,

    _getFieldByName: function(formpanel, fieldname) {
        var fieldComponentQuery = Ext.String.format('[name={0}]', fieldname);
        var match = formpanel.query(fieldComponentQuery);
        if(match.length > 0) {
            return match[0];
        } else {
            return null;
        }
    },

    /**
     * Mark all fields that are both in ``formpanel`` and ``fielderrors`` with
     * using ``field.markInvalid(fielderrors[fieldname])``.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
     * */
    markFieldErrorsAsInvalid: function(formpanel, fielderrors) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var field = this._getFieldByName(formpanel, fieldname);
            if(field) {
                field.markInvalid(fielderrors);
            }
        }, this);
    },

    _getFieldLabel: function(field, fieldname) {
        var displayName = field.fieldLabel;

        // Support label defined in radiogroup
        if(typeof displayName == 'undefined') {
            if(field.getXType() == 'radiofield') {
                var group = field.up('radiogroup');
                displayName = group.fieldLabel;
            }
        }

        // Fall back on the fieldname (the one in the error response object)
        if(typeof displayName == 'undefined') {
            displayName = fieldname;
        }

        return displayName;
    },

    /**
     * Add field errors to ``AlertMessageList``.
     *
     * Locates form field labels using the key in fielderrors, and prefixes all
     * error messages with the field label.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
     * @param alertmessagelist A ``devilry_extjsextras.AlertMessageList`` object.
     * */
    addFieldErrorsToAlertMessageList: function(formpanel, fielderrors, alertmessagelist) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var fielderror = fielderrors.join('. ');
            var field = this._getFieldByName(formpanel, fieldname);
            if(field) {
                var displayName = this._getFieldLabel(field, fieldname);
                var message = Ext.String.format('<strong>{0}:</strong> {1}', displayName, fielderror)
                alertmessagelist.add({
                    message: message,
                    type: 'error'
                });
            } else {
                console.error(Ext.String.format(
                    "Field error in field that is not in the form. Field name: {0}. Error: {1}.",
                    fieldname, fielderror));
            }
        }, this);
    }
});


/** 
 * Defaults for {@link devilry.extjshelpers.searchwidget.SearchResults#filterconfig}
 * for student, administrator and examiner.
 */
Ext.define('devilry.extjshelpers.searchwidget.FilterConfigDefaults', {
    statics: {
        assignment: {
            type: 'assignment'
        },
        assignmentgroup: {
            type: 'group',
            shortcuts: {
                assignment: 'parentnode'
            }
        },
        deadline: {
            type: 'deadline',
            shortcuts: {
                assignment: 'assignment_group__parentnode',
                group: 'assignment_group',
            }
        },
        delivery: {
            type: 'delivery',
            shortcuts: {
                assignment: 'deadline__assignment_group__parentnode',
                group: 'deadline__assignment_group'
            }
        }
    }
});


Ext.define('devilry.extjshelpers.GridSelectionModel', {
    extend: 'Ext.selection.CheckboxModel',

    onRowMouseDown: function(view, record, item, index, e) {
        view.el.focus();
        var me = this;

        // checkOnly set, but we didn't click on a checker.
        if (me.checkOnly && !checker) {
            return;
        }

        // Only check with left mouse button
        if(e.button !== 0) {
            return;
        }

        var mode = me.getSelectionMode();
        // dont change the mode if its single otherwise
        // we would get multiple selection
        if (mode !== 'SINGLE') {
            me.setSelectionMode('SIMPLE');
        }
        me.selectWithEvent(record, e);
        me.setSelectionMode(mode);
    }
});


Ext.define('devilry_header.model.StudentSearchResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'path', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'name',  type: 'string'},
        {name: 'students',  type: 'auto'},
        {name: 'type',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_search/rest/studentcontent',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json',
            root: 'matches',
            totalProperty: 'total'
        }
    }
});


Ext.define('devilry.extjshelpers.DateTime', {
    statics: {
        restfulNow: function() {
            return devilry.extjshelpers.DateTime.restfulFormat(new Date(Ext.Date.now()));
        },

        restfulFormat: function(dateobj) {
            return Ext.Date.format(dateobj, Ext.Date.patterns.RestfulDateTime);
        }
    }
});


/**
 * Based on http://www.sencha.com/forum/showthread.php?134345-Ext.ux.form.field.DateTime
 */
Ext.define('devilry_extjsextras.form.DateTimeField', {
    extend: 'Ext.form.FieldContainer',
    mixins:{    
        field:'Ext.form.field.Field'
    },
    alias: 'widget.devilry_extjsextras-datetimefield',

    requires: [
        'Ext.util.DelayedTask'
    ],
        
    //configurables
    
    combineErrors: true,
    msgTarget: 'under',    
    readOnly: false,
    allowBlank: true,

    /**
     * @cfg {Object} dateConfig
     * Additional config options for the date field.
     */
    dateConfig:{},

    /**
     * @cfg {Object} timeConfig
     * Additional config options for the time field.
     */
    timeConfig:{},

    /**
     * @cfg {string} dateFieldEmptyText ``emptyText`` attribute for the date field.
     */
    dateFieldEmptyText: pgettext('extjs date emptytext', 'YYYY-MM-DD'),

    /**
     * @cfg {string} dateFieldEmptyText ``emptyText`` attribute for the time field.
     */
    timeFieldEmptyText: pgettext('extjs time emptytext', 'hh:mm'),
    

    initComponent: function(){
        this.childrenRendered = 0;
        this.currentValue = null;
        this.currentIsValid = false;
        Ext.apply(this, {
            layout: 'column',
            items: [Ext.Object.merge({
                xtype: 'devilry_extjsextras_datefield',
                columnWidth: 0.5,
                isFormField: false, //exclude from field query's
                emptyText: this.dateFieldEmptyText,
                submitValue: false,
                allowBlank: this.allowBlank,
                listeners: {
                    scope: this,
                    render: this._onChildRender,
                    blur: this._onItemBlur,
                    change: this._onFieldChange,
                    focus: this._onItemFocus
                }
            }, this.dateConfig), Ext.Object.merge({
                xtype: 'devilry_extjsextras_timefield',
                columnWidth: 0.5,
                isFormField: false, //exclude from field query's
                emptyText: this.timeFieldEmptyText,
                submitValue: false,
                allowBlank: this.allowBlank,
                listeners: {
                    scope: this,
                    render: this._onChildRender,
                    blur: this._onItemBlur,
                    change: this._onFieldChange,
                    focus: this._onItemFocus
                }
            }, this.timeConfig)]
        });

        
        //for (var i=0; i < this.items.length; i++) {
            //this.items[i].on('specialkey', function(field, event){
                //var key = event.getKey();
                //var tab = key == event.TAB;
                
                //if (tab && this.focussedItem == this.getDateField()) {
                    //event.stopEvent();
                    //this.getTimeField().focus();
                    //return;
                //}
                
                //this.fireEvent('specialkey', field, event);
            //});
        //}

        this.callParent(arguments);
        
        // this dummy is necessary because Ext.Editor will not check whether an inputEl is present or not
        this.inputEl = {
            dom:{},
            swallowEvent:function(){}
        };

        this.initField();
    },

    getDateField: function() {
        return this.down('devilry_extjsextras_datefield');
    },
    getTimeField: function() {
        return this.down('devilry_extjsextras_timefield');
    },

    _onFieldChange: function(timefield, newValue, oldValue) {
        var oldFullValue = this.currentValue;
        var newFullValue = this.getValue();
        if(this.newFullValue !== null) {
            this.currentValue = newFullValue;
            this.fireEvent('change', this, newFullValue, oldFullValue);
            var isValid = this.isValid();
            if(isValid !== this.currentIsValid) {
                this.currentIsValid = isValid;
                this.fireEvent('validitychange', this, isValid);
            }
        }
    },

    _onChildRender: function() {
        this.childrenRendered ++;
        if(this.childrenRendered == 2) {
            if(!Ext.isEmpty(this.value)) {
                this.setValue(this.value);
            }
            this.fireEvent('allRendered', this);
        }
    },

    focus:function(){
        this.callParent();
        this.getDateField().focus();
    },

    _onItemFocus: function(item){
        if (this.blurTask){
            this.blurTask.cancel();
        }
        this.focussedItem = item;
    },
    
    _onItemBlur: function(item){
        if (item != this.focussedItem) {
            return;
        }
        // 100ms to focus a new item that belongs to us, otherwise we will assume the user left the field
        this.blurTask = new Ext.util.DelayedTask(function(){
            this.fireEvent('blur', this);
        }, this);
        this.blurTask.delay(100);
    },
    
    getValue: function(){
        var value = null;
        var date = this.getDateField().getSubmitValue()
        if (date){
            var time = this.getTimeField().getSubmitValue()
            if (time){
                var format = this.getFormat();
                value = Ext.Date.parse(date + ' ' + time, format);
            } else {   
                value = this.getDateField().getValue();
            }
        }
        return value;
    },
    
    getSubmitValue: function(){   
        var format = this.getFormat()
        var value = this.getValue();
        return value ? Ext.Date.format(value, format) : null;        
    },
 
    setValue: function(value){    
        if (Ext.isString(value)){
            value = Ext.Date.parse(value, this.getFormat());
        }
        this.getDateField().setValue(value);
        this.getTimeField().setValue(value);
    },
    
    getFormat: function(){
        return (this.getDateField().submitFormat || this.getDateField().format) + " " + (this.getTimeField().submitFormat || this.getTimeField().format);
    },
    
    // Bug? A field-mixin submits the data from getValue, not getSubmitValue
    getSubmitData: function(){
        var data = null;
        if (!this.disabled && this.submitValue && !this.isFileUpload()) {
            data = {};
            data[this.getName()] = '' + this.getSubmitValue();
        }
        return data;
    },

    isValid: function() {
        return this.getDateField().isValid() && this.getTimeField().isValid();
    }
});


Ext.define('devilry_extjsextras.DatetimeHelpers', {
    singleton: true,
    requires: [
        'Ext.Date'
    ],

    /**
     * Format the given Date object in a human readable string suitable for places where
     * space is an issue.
     *
     * @param dateobj A Date object.
     */
    formatDateTimeShort: function(dateobj) {
        return Ext.Date.format(dateobj, pgettext('extjs short datetime', 'Y-m-d H:i'));
    },

    /**
     * Format the given Date object in a human readable string suitable for places where
     * space is not an issue.
     *
     * @param dateobj A Date object.
     */
    formatDateTimeLong: function(dateobj) {
        return Ext.Date.format(dateobj, pgettext('extjs long datetime', 'Y-m-d H:i'));
    },

    parseRestformattedDatetime: function (datetimeString) {
//        return Ext.Date.parse(datetimeString, 'Y-m-dTH:i:s.u');
        return Ext.Date.parse(datetimeString, 'c');
    },

    /**
     * Format a time ``delta`` as a human readable string.
     *
     * @param delta An object with the following attributes ``days``, ``hours``, ``minutes`` and ``seconds``
     */
    formatTimedeltaShort: function(delta) {
        if(delta.days > 0) {
            return interpolate(gettext('%s days'), [delta.days]);
        } else if(delta.hours > 0) {
            return interpolate(gettext('%s hours'), [delta.hours]);
        } else if(delta.minutes > 0) {
            return interpolate(gettext('%s minutes'), [delta.minutes]);
        } else {
            return interpolate(gettext('%s seconds'), [delta.seconds]);
        }
    },

    /**
     * Format a time ``delta`` as a human readable string relative to *now*.
     *
     * @param delta An object with the following attributes ``days``, ``hours``, ``minutes`` and ``seconds``
     * @param in_the_future Is the delta positive? Defaults to ``false``, which means that we
     *      the result is a string that indicates past tense.
     */
    formatTimedeltaRelative: function(delta, in_the_future) {
        if(in_the_future) {
            return interpolate(gettext('In %(delta)s'), {
                delta: this.formatTimedeltaShort(delta)
            }, true);
        } else {
            return interpolate(gettext('%(delta)s ago'), {
                delta: this.formatTimedeltaShort(delta)
            }, true);
        }
    }
});


/** Parses values from a string into plain values and filters which is
 * compatible with our RESTful filters.
 * */
Ext.define('devilry.extjshelpers.SearchStringParser', {
    filterToStringTpl: Ext.create('Ext.XTemplate', '{field}:{comp}:{value}'),
    toStringTpl: Ext.create('Ext.XTemplate',
        '<tpl if="type">type:{type} </tpl>',
        '<tpl if="filters">{filters} </tpl>',
        '{query}'),
    config: {
        searchstring: undefined,
        pageSizeWithType: 10,
        pageSizeWithoutType: 3,
        alwaysAppliedFilters: [],
    },

    constructor: function(config) {
        this.initConfig(config);
        this.query = "";
        this.filters = [];
        this.type = undefined;
        this.parseSearchString();
        return this;
    },

    toString: function() {
        return Ext.String.trim(this.toStringTpl.apply({
            query: this.query,
            filters: this.filtersToString(),
            type: this.type
        }));
    },

    filtersToString: function() {
        var filterstring = "";
        var me = this;
        Ext.each(this.filters, function(filter) {
            filterstring += me.filterToString(filter) + ' ';
        });
        return Ext.String.trim(filterstring);
    },

    filterToString: function(filter) {
        return this.filterToStringTpl.apply(filter);
    },

    isInt: function(value) {
        return !isNaN(parseInt(value));
    },

    parseFilter: function(filtersplit) {
        var filter = new Object();
        filter.field = filtersplit[0];
        if(filtersplit.length === 2) {
            filter.comp = 'exact';
            filter.value = filtersplit[1];
        } else {
            filter.comp = filtersplit[1];
            filter.value = filtersplit[2];
        }
        if(this.isInt(filter.value)) {
            filter.value = parseInt(filter.value);
        }
        if(!Ext.Array.contains(this.illegalFilters, filter.field)) {
            this.filters.push(filter);
        }
    },

    parseFilterIsh: function(filterstring) {
        var split = filterstring.split(':');
        var first = split[0].toLowerCase();
        if(first === 'type') {
            this.type = split[1];
        } else {
            this.parseFilter(split);
        }
    },

    /**
     * @private
     * Parse ``this.searchstring`` into:
     *
     *  ``this.filters``
     *      A filter list on the format used by Devilry.
     *      This goes into the ``filters`` parameter of
     *      a Devilry search. Set to ``undefined`` if no
     *      filters are found.
     *
     * ``this.query``
     *      Other values (all words not containing :). This goes
     *      into the ``query`` parameter of a Devilry search.
     *      Set to ``undefined if no query is found.
     *
     *  ``this.type``
     *      A special *filter* (type:mytype) which specifies that a search should
     *      be done for a specific type instead of on multiple types. Set to
     *      ``undefined`` if not found.
     */
    parseSearchString: function() {
        this.illegalFilters = [];
        Ext.each(this.alwaysAppliedFilters, function(filter, index) {
            this.illegalFilters.push(filter.field);
        }, this);

        var split = this.searchstring.split(' ');
        var query = "";
        var me = this;
        Ext.each(split, function(word) {
            if(word.indexOf(':') === -1) {
                query += word + ' ';
            } else {
                me.parseFilterIsh(word);
            }
        });
        this.query = query;
        //console.log(this.query);
        //console.log(this.filters);
    },

    applyPageSizeToStore: function(store) {
        if(this.type) {
            store.pageSize = this.pageSizeWithType;
        } else {
            store.pageSize = this.pageSizeWithoutType;
        }
    },

    applyToExtraParams: function(extraParams, shortcuts) {
        if(!extraParams) {
            extraParams = new Object();
        }
        if(this.query) {
            extraParams.query = this.query;
        }

        var localfilters = [];
        if(this.filters) {
            if(shortcuts) {
                localfilters = this.applyShortcuts(shortcuts);
            } else {
                localfilters = this.filters;
            }
        }
        if(this.alwaysAppliedFilters) {
            Ext.Array.insert(localfilters, 0, this.alwaysAppliedFilters);
        }

        extraParams.filters = Ext.JSON.encode(localfilters);
        return extraParams;
    },

    /**
     * @private
     */
    applyShortcuts: function(shortcuts) {
        var localfilters = Ext.clone(this.filters);
        var me = this;
        Ext.each(this.filters, function(filter, index) {
            var fieldnameFromFilter = me.applyFirstMatchingShortcut(shortcuts, filter.field);
            if(fieldnameFromFilter) {
                localfilters[index].field = fieldnameFromFilter;
            }
            //console.log(localfilters[index].field);
        });
        return localfilters;
    },

    /**
     * @private
     */
    applyFirstMatchingShortcut: function(shortcuts, fieldname) {
        var realFieldname = undefined;
        Ext.Object.each(shortcuts, function(shortcut, replacement) {
            var startswithShortcut = new RegExp("^" + shortcut);
            if(fieldname.match(startswithShortcut)) {
                realFieldname = fieldname.replace(startswithShortcut, replacement);
                return false;
            }
        });
        return realFieldname;
    }
});


Ext.define('devilry.statistics.dataview.SelectViewCombo', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.statistics-dataview-selectviewcombo',
    valueField: 'clsname',
    displayField: 'label',
    forceSelection: true,
    editable: false,
    
    config: {
        availableViews: [],
        defaultViewClsname: undefined
    },
    
    constructor: function(config) {
        this.addEvents('selectView');
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var selectViewStore = Ext.create('Ext.data.Store', {
            fields: ['clsname', 'label'],
            data: this.availableViews,
            proxy: 'memory'
        });
        Ext.apply(this, {
            store: selectViewStore,
            emptyText: this._findDefaultViewInAvailableViews().label
        });
        this.on('select', this._onSelectView, this);
        this.callParent(arguments);
    },

    _findDefaultViewInAvailableViews: function() {
        var view;
        Ext.each(this.availableViews, function(availableView, index) {
            if(availableView.clsname === this.defaultViewClsname) {
                view = availableView;
                return false; // break
            }
        }, this);
        return view;
    },

    _onSelectView: function(combo, records) {
        var record = records[0];
        this.fireEvent('selectView', record.get('clsname'));
    }
});


Ext.define('devilry_i18n.LanguageSelectModel', {
    extend: 'Ext.data.Model',
    idProperty: 'preferred',
    fields: [
        {name: 'preferred',  type: 'string'},
        {name: 'selected',  type: 'auto'},
        {name: 'available',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_i18n/rest/languageselect',
        appendId: false,
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});


/**
 * Adds utilites for ``djangorestframework`` errors,
 */
Ext.define('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', {
    extend: 'devilry_extjsextras.ProxyErrorHandler',

    _decodeResponseTextJSON: function(response) {
        try {
            return Ext.JSON.decode(response.responseText);
        } catch(e) {
            return null;
        }
    },

    _addFieldErrors: function(responseData) {
        if(!Ext.isEmpty(responseData.field_errors)) {
            this.fielderrors = responseData.field_errors;
        }
    },

    _addMessages: function(responseData) {
        if(responseData.detail) {
            this.errormessages.push(responseData.detail);
        }
        if(responseData.errors) {
            this.errormessages = this.errormessages.concat(responseData.errors);
        }
    },

    /**
     * Add errors from an extjs response object (such as the one given to proxy
     * exception events).
     */
    addRestErrorsFromResponse: function(response) {
        var responseData = this._decodeResponseTextJSON(response);
        if(responseData) {
            this._addMessages(responseData);
            this._addFieldErrors(responseData);
        }
    },

    addErrors: function(response, operation) {
        if(response) {
            this.addRestErrorsFromResponse(response);
        }
        if(!this.hasErrors()) {
            this.addErrorsFromOperation(operation);
        }
    },

    addBatchErrors: function(batch) {
        Ext.Array.each(batch.exceptions, function(exception) {
            var message = this.parseHttpError(exception.error, exception.request);
            this.errormessages.push(message);
        }, this);
    }
});


/** A search result item (a single row in the search result).
 *
 * @xtype searchresultitem
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResultItem', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchresultitem',
    cls: 'searchresultitem',
    frame: false,
    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` formatting template for the text content. _Required_.
         */
        tpl: undefined,

        recorddata: undefined,
        recordindex: undefined,
        defaultbutton: undefined,
        menuitems: undefined
    },
    layout: {
        type: 'hbox',
        align: 'top'
    },


    initComponent: function() {
        if(this.recordindex % 2 != 0) {
            this.addCls('searchresultitem-even');
        }

        var template = Ext.create('Ext.XTemplate', this.tpl);
        var items = [{
            xtype: 'component',
            flex: 4,
            html: template.apply(this.recorddata)
        }];

        var button = this.defaultbutton;
        if(this.defaultbutton) {
            if(this.menuitems) {
                this.configureClickable(button, 'splitbutton');
                button.menu = {
                    items: this.configureMenuItems()
                }
            } else {
                this.configureClickable(button, 'button');
            }

            Ext.apply(button, {
                minWidth: 100,
                margin: '0 0 0 10 0'
            });
            items.push(button);
        }

        Ext.apply(this, {items: items});
        this.callParent(arguments);
    },


    configureMenuItems: function() {
        var me = this;
        Ext.each(this.menuitems, function(menuitem) {
            me.configureClickable(menuitem);
        });
        return this.menuitems;
    },

    configureClickable: function(config, xtype) {
        Ext.apply(config, {
            xtype: xtype,
            scale: 'medium'
        });
        if(config.clickLinkTpl) {
            this.applyClickLinkButton(config);
        } else if(config.clickFilter) {
            this.applyClickFilterButton(config);
        }
        return config;
    },

    applyClickLinkButton: function(config) {
        var tpl = Ext.create('Ext.XTemplate', config.clickLinkTpl);
        var url = tpl.apply(this.recorddata);
        Ext.apply(config, {
            listeners: {
                click: function() {
                    window.location = url;
                }
            }
        });
    },

    applyClickFilterButton: function(config) {
        var tpl = Ext.create('Ext.XTemplate', config.clickFilter);
        var filter = tpl.apply(this.recorddata);
        var me = this;
        Ext.apply(config, {
            listeners: {
                click: function() {
                    var searchwidget = me.getSearchWidget();
                    searchwidget.setSearchValue(filter);
                }
            }
        });
    },

    getSearchWidget: function() {
        return this.up('multisearchresults').getSearchWidget();
    }
});


Ext.define('devilry_extjsextras.UnfocusedContainer', {
    extend: 'Ext.container.Container',
    alias: 'widget.unfocusedcontainer',
    cls: 'devilry_extjsextras_unfocusedcontainer',

    defaultOpacity: 0.6,
    hoverOpacity: 1.0,

    initComponent: function() {
        this.on('render', this._onRender, this);
        this.callParent(arguments);
    },
    _onRender: function() {
        this.getEl().setOpacity(this.defaultOpacity);
        this.getEl().on({
            scope: this,
            mouseenter: this._onMouseEnter,
            mouseleave: this._onMouseLeave
        });
    },
    _onMouseEnter: function() {
        this.getEl().setOpacity(this.hoverOpacity);
        this.mouseEnterExtras();
    },
    _onMouseLeave: function() {
        this.getEl().setOpacity(this.defaultOpacity);
        this.mouseLeaveExtras();
    },

    mouseEnterExtras: function() {
        
    },
    mouseLeaveExtras: function() {

    }
});


Ext.define('devilry.extjshelpers.page.Header', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.pageheader',
    bodyStyle: 'background-color: transparent !important',
    border: false,
    margins: '0 0 0 0',
    height: 90,
    //autoHeight: true,

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="header">',
        '    <div id="heading">',
        '        <h1>Devilry</h1>',
        '        <div id="authenticated-user-bar">',
        '            <tpl if="DevilryUser.is_authenticated">',
        '                <span id="authenticated-user-info">',
        '                    {DevilryUser.username}',
        '                </span>',
        '                | <a class="loginout-link" href="{DevilrySettings.DEVILRY_LOGOUT_URL}">Log out</a>',
        '            </tpl>',
        '            <tpl if="!DevilryUser.is_authenticated">',
        '                <a class="loginout-link" href="{DevilrySettings.DEVILRY_LOGIN_URL}">Log in</a>',
        '            </tpl>',
        '        </div>',
        '    </div>',
        '    <div class="nav {navclass}">',
        '        <ul>',
        '            <li class="student-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/student/">Student</a></li>',
        '            <li class="examiner-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/examiner/">Examiner</a></li>',
        '            <li class="administrator-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/administrator/">Administrator</a></li>',
        '            <li class="externallink-navitem"><a href="{DevilrySettings.DEVILRY_HELP_URL}" target="_blank">Help</a></li>',
        '        </ul>',
        '    </div>',
        '</div>'
    ),

    config: {
        navclass: ''
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.html = this.bodyTpl.apply({
            navclass: this.navclass,
            DevilrySettings: DevilrySettings,
            DevilryUser: DevilryUser
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.extjshelpers.EvenRandomSelection', {
    config: {
        selection: []
    },

    constructor: function(config) {
        this.pool = []; // Currently available subset of the selection. When this is empty, it is re-cloned from selection
        this.initConfig(config);
        this.callParent([config]);
    },

    getRandomItem: function() {
        if(this.pool.length === 0) {
            this.pool = Ext.Array.clone(this.selection);
        }
        var randomIndex = Math.floor(Math.random() * (this.pool.length));
        var next = this.pool[randomIndex];
        Ext.Array.remove(this.pool, next);
        return next;
    },
});


Ext.define('devilry_i18n.LanguageSelectWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilry_i18n_languageselect',
    cls: 'devilry_i18n_languageselect',


    /**
     * @cfg {bool} [hideLabel]
     * Forwarded to the interal combobox.
     */

    /**
     * @cfg {bool} [fieldLabel]
     * Forwarded to the interal combobox.
     */

    requires: [
        'Ext.window.MessageBox',
        'Ext.data.Store',
        'devilry_i18n.LanguageSelectModel'
    ],

    initComponent: function() {
        devilry_i18n.LanguageSelectModel.load(null, {
            scope: this,
            success: this._onLoadSuccess,
            failure: this._onLoadFailure
        });
        Ext.apply(this, {
            layout: 'fit',
            items: [{
                xtype: 'box',
                html: gettext('Loading') + ' ...'
            }]
        });
        this.callParent(arguments);
    },

    _createAvailableLanguagesStore: function(availableLanguages) {
        var data = [];
        Ext.Array.each(availableLanguages, function(language) {
            data.push({
                languagecode: language.languagecode,
                name: language.name
            });
        }, this);
        return Ext.create('Ext.data.Store', {
            fields: ['languagecode', 'name'],
            data: data
        });
    },

    _onLoadSuccess: function(languageRecord) {
        this.languageRecord = languageRecord;
        var store = this._createAvailableLanguagesStore(languageRecord.get('available'));
        this._addCombobox(store, languageRecord.get('selected'));
    },

    _showError: function(msg) {
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: msg,
            icon: Ext.MessageBox.ERROR
        });
    },

    _onLoadFailure: function(unused, operation) {
        this._showError(gettext('Failed to load languages. Try to reload the page.'));
    },

    _addCombobox: function(store, selected) {
        this.removeAll();
        this.add({
            xtype: 'combobox',
            queryMode: 'local',
            displayField: 'name',
            valueField: 'languagecode',
            forceSelection: true,
            editable: false,
            value: selected.languagecode,
            store: store,
            hideLabel: this.hideLabel,
            fieldLabel: this.fieldLabel,
            listeners: {
                scope: this,
                select: this._onSelect
            }
        });
    },

    _onSelect: function(combo, records) {
        var languagecode = records[0].get('languagecode');
        this.languageRecord.set('preferred', languagecode);
        Ext.getBody().mask(gettext('Saving') + '...');
        this.languageRecord.save({
            scope: this,
            success: this._onSaveSuccess,
            failure: this._onSaveFailure
        });
    },

    _onSaveFailure: function(unused, operation) {
        Ext.getBody().unmask();
        this._showError(gettext('Failed to save language choice.'));
    },

    _onSaveSuccess: function(languageRecord) {
        Ext.getBody().unmask();
        window.location.reload();
    }
});


Ext.define('devilry.statistics.OverviewOfSingleStudentRecord', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: ['id', 'assignment__long_name', 'assignmentid', 'assignment__short_name', 'is_open', 'feedback__points', 'feedback']
});


/**
 * Mixin that can be used to automatically adjust the size of a component when the size
 * of the window changes.
 *
 * Example:
 *
 *      Ext.define('MyPanel', {
 *          constructor: function () {
 *              extends: 'Ext.panel.Panel',
 *              mixins: ['devilry_extjsextras.AutoHeightComponentMixin'],
 *              this.callParent(arguments);
 *              this.setupAutoHeightSizing();
 *          }
 *      });
 */
Ext.define('devilry_extjsextras.AutoHeightComponentMixin', {

    /**
     * @cfg {int} [autoHeightMargin=60]
     * The number of pixels to retract from the window height.
     */
    autoHeightMargin: 60,

    setupAutoHeightSizing: function() {
        Ext.fly(window).on('resize', function() {
            if(this.isVisible()) {
                this.setHeightAutomatically();
            }
        }, this);
        this.on('render', function() {
            this.setHeightAutomatically();
        }, this);
    },

    setHeightAutomatically: function() {
        var bodysize = Ext.getBody().getViewSize();
        var height = bodysize.height - this.autoHeightMargin;
        this.setHeight(height);
    }
});


Ext.define('devilry.extjshelpers.PermissionChecker', {
    extend: 'Ext.Component',
    hidden: true,
    config: {
        stores: [],
        emptyHtml: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.loadedItems = 0;
        this.loadedWithRecords = 0;

        Ext.each(this.stores, function(store, index) {
            store.on('load', this.onLoadStore, this);
        }, this);
    },

    onLoadStore: function(store) {
        this.loadedItems ++;
        if(store.totalCount > 0) {
            this.loadedWithRecords ++;
        }
        if(this.loadedItems === this.stores.length) {
            this.fireEvent('allLoaded', this.loadedItems, this.loadedWithRecords);
            if(this.loadedWithRecords === 0) {
                this.fireEvent('noPermission', this.loadedItems, this.loadedWithRecords);
                this.update(this.emptyHtml);
                this.show();
            } else {
                this.fireEvent('hasPermission', this.loadedItems, this.loadedWithRecords);
            }
        }
    }
});


/**
 * Selection model that checks the clicked row without deselecting the previous
 * selection.
 * */
Ext.define('devilry_extjsextras.GridMultiSelectModel', {
    extend: 'Ext.selection.CheckboxModel',

    onRowMouseDown: function(view, record, item, index, e) {
        view.el.focus();
        var me = this;

        // checkOnly set, but we didn't click on a checker.
        if (me.checkOnly && !checker) {
            return;
        }

        // Only check with left mouse button
        if(e.button !== 0) {
            return;
        }

        var mode = me.getSelectionMode();
        // dont change the mode if its single otherwise
        // we would get multiple selection
        if (mode !== 'SINGLE') {
            me.setSelectionMode('SIMPLE');
        }
        me.selectWithEvent(record, e);
        me.setSelectionMode(mode);
    }
});


Ext.define('devilry_extjsextras.RouteNotFound', {
    extend: 'Ext.Component',
    alias: 'widget.routenotfound',
    cls: 'bootstrap',
    
    tpl: [
        '<div class="alert alert-block error">',
        '  <h1 class="alert-heading">{title}</h1>',
        '  <p>{route}</p>',
        '  <div class="alert-actions">',
        '    <a class="btn" href="#">{gotodashboard}</a>',
        '  </div>',
        '</div>'
    ],

    data: {
        title: gettext('Route not found'),
        gotodashboard: gettext('Return to dashboard')
    },

    /**
     * @cfg
     * The missed route.
     */
    route: undefined,

    initComponent: function() {
        this.data.route = this.route;
        this.callParent(arguments);
    }
});


Ext.define('devilry.extjshelpers.MenuHeader', {
    extend: 'Ext.Component',
    plain: true,
    alias: 'widget.menuheader',
    cls: 'widget-menuheader'
});


Ext.define('devilry.statistics.SingleStudentPeriodChart', {
    extend: 'Ext.chart.Chart',
    alias: 'widget.statistics-singlestudentperiodchart',
    cls: 'widget-statistics-singlestudentperiodchart',

    groupTpl: Ext.create('Ext.XTemplate',
        '<tpl for="candidates">',
        '   {.}<tpl if="xindex != xcount">, </tpl>',
        '</tpl>'
    ),

    hoverTpl: Ext.create('Ext.XTemplate',
        'Points: {feedback__points}'
    ),

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            style: 'background:#fff',
            animate: true,
            shadow: true,
            axes: [{
                type: 'Numeric',
                position: 'left',
                fields: ['feedback__points'],
                label: {
                    renderer: Ext.util.Format.numberRenderer('0,0')
                },
                title: 'Points',
                grid: true,
                minimum: 0
            }, {
                type: 'Category',
                position: 'bottom',
                fields: ['assignment__short_name'],
                title: 'Assignment',

                label: {
                    renderer: function(data) {
                        return me.groupTpl.apply({candidates: data});
                    }
                }
            }],
            series: [{
                type: 'column',
                axis: 'left',
                highlight: true,
                tips: {
                    trackMouse: true,
                    width: 140,
                    height: 28,
                    renderer: function(storeItem, item) {
                        this.setTitle(me.hoverTpl.apply(storeItem.data));
                    }
                },
                label: {
                    display: 'insideEnd',
                    'text-anchor': 'middle',
                    field: 'feedback__grade',
                    //orientation: 'vertical',
                    color: '#333'
                },
                xField: 'id',
                yField: 'feedback__points',

                renderer: function(sprite, record, attr, index, store) {
                    var color = record.get('feedback__is_passing_grade')? '#77B300': '#CC4400';
                    return Ext.apply(attr, {
                        fill: color
                    });
                }
            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.extjshelpers.ComboboxTemplatesMixin', {
    assignmentRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">{parentnode__parentnode__short_name}.{parentnode__short_name}</p>',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    assignmentgroupRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{parentnode__parentnode__parentnode__short_name:ellipsis(60)}.',
        '{parentnode__parentnode__short_name:ellipsis(60)}.',
        '{parentnode__short_name:ellipsis(60)}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <h1><ul class="useridlist"><tpl for="candidates__identifier"><li>{.}</li></tpl></ul></h1>',
        '   </tpl>',
        '   <tpl if="is_student">',
        '       <h1>{parentnode__long_name:ellipsis(40)}</h1>',
        '   </tpl>',
        '   <p><tpl if="name">{name}</tpl><p>',
        '</div>'
    ],

    deliveryRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__short_name}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>',
        '   </tpl>',
        '   <tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>',
        '   <div class="section dl_valueimportant">',
        '      <div class="section">',
        '          <h1>Delivery number</h1>',
        '          {number}',
        '      </div>',
        '   </div>',
        '</div>'
    ]
});


Ext.define('devilry_header.UserInfoBox', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_userinfobox',
    cls: 'devilryheader_userinfobox',

    tpl: [
        '<h2>',
            gettext('About you'),
        '</h2>',
        '<tpl if="loading">',
            '<p>', gettext('Loading'), ' ...</p>',
        '<tpl else>',
            '<p class="discreet">',
                gettext('The table below shows the personal information registered about you in Devilry. <a href="{wrong_userinfo_url}">Click here</a> if any information is incorrect.'),
            '</p>',
            '<table class="userinfotable">',
                '<tbody>',
                    '<tr>',
                        '<th>', gettext('Name'), ':</th>',
                        '<td>{userInfo.full_name}</td>',
                    '</tr>',
                    '<tr>',
                        '<th>', gettext('Email'), ':</th>',
                        '<td>{userInfo.email}</td>',
                    '</tr>',
                    '<tr>',
                        '<th>', gettext('Username'), ':</th>',
                        '<td>{userInfo.username}</td>',
                    '</tr>',
                '</tbody>',
            '</table>',
            '<div class="logout_para bootstrap"><a href="{logout_url}" class="logout_button btn btn-primary btn-large">',
                gettext('Log out'),
            '</a></div>',
        '</tpl>'
    ],

    data: {
        loading: true
    },


    /**
     * Set UserInfo record and update view.
     */
    setUserInfoRecord: function(userInfoRecord) {
        this.update({
            userInfo: userInfoRecord.data,
            wrong_userinfo_url: DevilrySettings.DEVILRY_WRONG_USERINFO_URL,
            logout_url: DevilrySettings.DEVILRY_LOGOUT_URL
        });
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.IsOpen', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroup_isopen',
    cls: 'widget-assignmentgroup_isopen',
    config: {
        assignmentgroup_recordcontainer: undefined,
        canExamine: undefined
    },

    tooltips: {
        canExamine: gettext('Click to toggle open/closed. A group should remain open until you have finished grading them. Devilry normally opens and closes groups for you automatically. You may want to manually close a group if you want to make the current grade their final grade on this assignment. A closed group can be re-opened at any time.'),
        student: 'As long as the assignment is open for more deliveries, you can add as many deliveries as you like, and your examiner(s) will normally correct your latest delivery. When an assignment is closed, the latest feedback is your final grade on this assignment. If you have not been given feedback, and you think this is wrong, you should contact your examiner or course administrator.'
    },
    layout: 'fit',
    //style: 'border: none',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        if(this.assignmentgroup_recordcontainer.record) {
            this.onSetRecord();
        } else {
            this.assignmentgroup_recordcontainer.on('setRecord', this.onSetRecord, this);
        }
        this.callParent(arguments);
    },

    /**
     * @private
     */
    onSetRecord: function() {
        this.removeAll();
        var buttonText;
        if(this.assignmentgroup_recordcontainer.record.get('is_open')) {
            buttonText = '<i class="icon-folder-open"></i> ' + gettext('Open - click to close');
        } else {
            buttonText = '<i class="icon-folder-close"></i> ' + gettext('Closed - click to open');
        }
        if(this.canExamine) {
            this.add({
                xtype: 'button',
                scale: 'medium',
                cls: 'bootstrap',
                text: buttonText,
//                ui: 'inverse',
                listeners: {
                    scope: this,
                    click: this.onStatusButtonClick,
                    render: function(button) {
                        Ext.tip.QuickTipManager.register({
                            target: button.getEl(),
                            title: gettext('How open/closed works'),
                            text: this.tooltips.canExamine,
                            width: 350,
                            dismissDelay: 30000 // Hide after 30 seconds hover
                        });
                    }
                }
            });
        } else {
            this.add({
                xtype: 'box',
                cls: 'text_with_tooltip',
                html: this.assignmentgroup_recordcontainer.record.data.is_open? 'Open - more deliveries allowed': 'Closed - final grade given',
                listeners: {
                    scope: this,
                    render: function(button) {
                        Ext.tip.QuickTipManager.register({
                            target: button.getEl(),
                            title: 'How open/closed works',
                            text: this.tooltips.student,
                            width: 300,
                            dismissDelay: 30000 // Hide after 30 seconds hover
                        });
                    }
                }
            });
        }
    },


    /**
     * @private
     */
    onStatusButtonClick: function() {
        //console.log(this.id);
        if(this.assignmentgroup_recordcontainer.record.data.is_open) {
            this.onCloseGroup();
        } else {
            this.onOpenGroup();
        }
    },


    /**
     * @private
     */
    onOpenGroup: function() {
        var win = Ext.MessageBox.show({
            title: 'Are you sure you want to open this group?',
            msg: '<p>This will <strong>allow</strong> students to add more deliveries. ' +
                'Normally Devilry will close groups automatically when:</p>'+
                '<ul>' +
                '   <li>you have given a passing grade.</li>' +
                '   <li>students have failed to get a passing grade more than the configured maximum number of times.</li>' +
                '</ul>' +
                '<p>And you normally do not open it again unless you want students to add a new delivery.</p>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId === 'yes') {
                    this.assignmentgroup_recordcontainer.record.data.is_open = true;
                    this.assignmentgroup_recordcontainer.record.save({
                        scope: this,
                        success: function(record) {
//                            this.assignmentgroup_recordcontainer.fireSetRecordEvent();
                            window.location.reload();
                        },
                        failure: function() {
                            throw "Failed to open group.";
                        }
                    });
                }
            }
        });
    },

    /**
     * @private
     */
    onCloseGroup: function() {
        var statics = this.statics();
        var win = Ext.MessageBox.show({
            title: 'Are you sure you want to close this group?',
            msg: '<p>This will <strong>prevent</strong> students from adding more deliveries. ' +
                'Normally Devilry will close groups automatically when:</p>'+
                '<ul>' +
                '   <li>you have given a passing grade.</li>' +
                '   <li>students have failed to get a passing grade more than the configured maximum number of times.</li>' +
                '</ul>' +
                '<p>However you may have to close a group manually if no maximum number of tries have been configured, or if you want the current feedback to be stored as the final feedback for this group.</p>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId === 'yes') {
                    statics.closeGroup(this.assignmentgroup_recordcontainer, function() {
                        window.location.reload();
                    });
                }
            }
        });
    },

    statics: {
        closeGroup: function(assignmentgroup_recordcontainer, callbackFn, callbackScope) {
            assignmentgroup_recordcontainer.record.data.is_open = false;
            assignmentgroup_recordcontainer.record.save({
                success: function(record) {
                    assignmentgroup_recordcontainer.fireSetRecordEvent();
                    Ext.callback(callbackFn, callbackScope);
                },
                failure: function() {
                    throw "Failed to close group.";
                }
            });
        }
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesPanel', {
    extend: 'Ext.container.Container',
    alias: 'widget.deliveriespanel',
    requires: [
        'devilry.extjshelpers.assignmentgroup.IsOpen',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    assignmentgroup_recordcontainer: undefined,
    delivery_recordcontainer: undefined,
    deadlineRecord: undefined,
    deliveriesStore: undefined,
    activeFeedback: undefined,

    titleTpl: [
        '<div class="deadline_title bootstrap">',
            '<p style="padding: 5px; margin: 0;">',
                '<tpl if="assignmentgroup.parentnode__delivery_types !== 1">',
                    '<small class="muted" style="line-height: 14px;">', gettext('Deadline'), ':</small> ',
                    '<strong style="font-size: 16px;">{[this.formatDatetime(values.deadline.deadline)]}</strong>',
                '</tpl>',
                '<tpl if="assignmentgroup.parentnode__delivery_types === 1">',
                    gettext('Non-electronic delivery'),
                '</tpl>',
            '</p>',
        '</div>', {
            formatDatetime:function (dt) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
            }
        }
    ],


    initComponent: function() {
        Ext.apply(this, {
            border: false,
            margin: '0 0 20 0'
        });

        this.items = [{
            xtype: 'box',
            tpl: this.titleTpl,
            data: {
                deadline: this.deadlineRecord.data,
                assignmentgroup: this.assignmentgroup_recordcontainer.record.data
            }
        }];
        if(this.deliveriesStore.count() === 0) {
            this.items.push({
                xtype: 'box',
                cls: 'bootstrap',
                html: [
                    '<p class="muted" style="margin: 0 0 0 5px; padding: 0;">',
                        gettext('No deliveries on this deadline'),
                    '</p>'
                ]
            });
        } else {
            this.items.push({
                xtype: 'deliveriesgrid',
//                margin: '0 0 0 20',
                delivery_recordcontainer: this.delivery_recordcontainer,
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                deadlineRecord: this.deadlineRecord,
                store: this.deliveriesStore
            });
        }

        this.callParent(arguments);
    },

    _onCollapse: function() {
        //var allGrids = this.up('assignmentgroupoverview').feedbackPanel.hide();
    }
});


Ext.define('devilry.extjshelpers.SetListOfUsers', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.setlistofusers',
    frame: false,
    border: false,

    config: {
        /**
         * @cfg
         * Usernames to fill in on load.
         */
        usernames: [],

        /**
         * @cfg
         * The label of the box/field.
         */
        fieldLabel: 'Usernames',

        buttonLabel: 'Save',

        example: 'bob\nalice\neve\ndave',
        helptext: '<p>One username on each line. Example:</p>',

        helptpl: Ext.create('Ext.XTemplate',
            '<div class="section helpsection">',
            '   {helptext}',
            '   <pre style="padding: 5px;">{example}</pre>',
            '</div>'
        )
    },


    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when the save button is clicked.
             *
             * @param setlistofusersobj This object.
             * @param usernames Array of usernames.
             */
            'saveClicked');
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.userinput = Ext.widget('textareafield', {
            fieldLabel: this.fieldLabel,
            flex: 12, // Take up all remaining vertical space
            margin: 10,
            labelAlign: 'top',
            labelWidth: 100,
            labelStyle: 'font-weight:bold'
        });
        this.setValueFromArray(this.usernames);

        var toolbarItems = ['->', {
            xtype: 'button',
            iconCls: 'icon-save-32',
            scale: 'large',
            text: this.buttonLabel,
            listeners: {
                scope: this,
                click: this.onSave
            }
        }];

        if(this.extraToolbarButtons) {
            Ext.Array.insert(toolbarItems, 0, this.extraToolbarButtons);
        }

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [this.userinput, {
                flex: 10,
                xtype: 'box',
                padding: 10,
                autoScroll: true,
                html: this.helptpl.apply(this)
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: toolbarItems
            }]
        });
        this.callParent(arguments);
    },

    parseInput: function(rawValue) {
        var asArray = rawValue.split('\n');
        var usernames = [];
        Ext.Array.each(asArray, function(username) {
            username = Ext.String.trim(username);
            if(username != "") {
                usernames.push(username);
            }
        });
        return Ext.Array.unique(usernames);
    },

    setValueFromArray: function(arrayOfUsernames) {
        var currentValue = "";
        Ext.each(arrayOfUsernames, function(username, index) {
            currentValue += Ext.String.format('{0}\n', username);
        });
        this.userinput.setValue(currentValue);
    },

    /**
     * @private
     */
    onSave: function() {
        var usernames = this.parseInput(this.userinput.getValue());
        this.fireEvent('saveClicked', this, usernames);
    }
});


Ext.define('devilry.extjshelpers.models.StaticFeedback', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "auto", "name": "grade"},
        {"type": "bool", "name": "is_passing_grade"},
        {"type": "auto", "name": "saved_by"},
        {"type": "date", "name": "save_timestamp", "dateFormat": "Y-m-d\\TH:i:s"},
        {"type": "int", "name": "delivery"},
        {"type": "auto", "name": "rendered_view"}
    ],
});


/** Mixin class for grids that can add a pager if needed. */
Ext.define('devilry.extjshelpers.AddPagerIfNeeded', {
    
    /**
     * @private
     * Make sure we show pager if needed.
     */
    addPagerIfNeeded: function() {
        if(this._hasPager) {
            return;
        }
        var totalCount = this.store.getTotalCount();
        if(totalCount == undefined) {
            this.store.on('load', this.addPagerIfNeeded, this, {single: true});
            return;
        }
        this._hasPager = true;
        if(this.store.count() < this.store.getTotalCount()) {
            this._addPager();
        };
    },

    _addPager: function() {
        try {
            this.addDocked({
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: false
            });
        } catch(e) {
            Ext.defer(function() {
                this._addPager();
            }, 250, this);
        }
    },
});


/** 
 * REST proxy subclass which handles errors from {@link devilry.extjshelpers.RestSubmit}. 
 *
 * Since ExtJS for some reason goes into panic mode for any HTTP status
 * code except 200 (and ignores the response text), we need to override
 * setException in the REST proxy and manually decode the responseText.
 * ([see this forum thread](http://www.sencha.com/forum/showthread.php?135143-RESTful-Model-How-to-indicate-that-the-PUT-operation-failed&highlight=store+failure))
 *
 * However how do we get this into the form when we do not have any link to the form?
 *
 *  - We add the response and the the decoded responsedata to the operation
 *    object, which is available to onFailure in Submit.
 *
 * # Usage
 * 
 * First we need to use the proxy, for example in a ``Ext.data.Model``:
 *
 *     Ext.define('MyModel', {{
 *               extend: 'Ext.data.Model',
 *               requires: ['devilry.extjshelpers.RestProxy'],
 *               fields: [...],
                 proxy: Ext.create('devilry.extjshelpers.RestProxy', {
 *                   ...
 *               }
 *     });
 *
 * Then we can handle errors and access the error data as plain text or JSON.
 * See {@link #setException} for more details):
 *
 *     myform.getForm().doAction('devilryrestsubmit', {
 *         submitEmptyText: true,
 *         waitMsg: 'Saving item...',
 *         success: function(form, action) {...},
 *         failure: function(form, action) {
 *             var errorraw = action.operation.responseText;
 *             console.log(errorraw);
 *             var errorjson = action.operation.responseData;
 *             console.log(errorjson);
 *         }
 *     });
 *
 *
 * # See also
 * This should be used with {@link devilry.extjshelpers.RestSubmit}.
 * */
Ext.define('devilry.extjshelpers.RestProxy', {
    extend: 'Ext.data.proxy.Rest',
    alias: 'proxy.devilryrestproxy',

    /**
     * @cfg
     * Forwarded to {@link #setDevilryResultFieldgroups}.
     */
    result_fieldgroups: undefined,

    /**
     * @cfg
     * Forwarded to {@link #setDevilryOrderby}.
     */
    orderby: undefined,

    /**
     * @cfg
     * Forwarded to {@link #setDevilryOrderby}.
     */
    filters: undefined,

    constructor: function(config) {
        Ext.apply(this, {
            reader: {
                type: 'json',
                root: 'items',
                totalProperty: 'total'
            },
            writer: {
                type: 'json'
           }
        });

        this.callParent([config]);

        if(!this.extraParams) {
            this.extraParams = {};
        }
        this.extraParams.getdata_in_qrystring = true;

        if(this.result_fieldgroups) {
            this.setDevilryResultFieldgroups(this.result_fieldgroups);
        }
        if(this.orderby) {
            this.setDevilryOrderby(this.orderby);
        }
        if(this.filters) {
            this.setDevilryFilters(this.filters);
        }
    },


    /**
     * Copy the extraParams and url of this proxy into a config object. Apply
     * the given options to the config, and create a new proxy object.
     */
    copy: function(options) {
        var config = {
            extraParams: this.extraParams,
            url: this.url
        };
        if(options) {
            Ext.apply(config, options);
        }
        var newproxy = Ext.create('devilry.extjshelpers.RestProxy', config);
        return newproxy;
    },
    

    /**
     * Overrides error handling. Adds error information to the ``operation`` parameter.
     *
     * The error data is added to:
     *
     * - ``operation.responseText``: The data in the body of the HTTP response.
     * - ``operation.responseData``: If ``responseText`` can be decoded as JSON,
     *   this contains the decoded JSON object.
     */
    setException: function(operation, response){
        operation.response = response;
        operation.responseText = response.responseText;
        try {
            operation.responseData = Ext.JSON.decode(operation.responseText); // May want to use a Reader
        } catch(e) {
            // No operation.responseData if it can not be decoded as JSON.
        }
        operation.setException({
            status: response.status,
            statusText: response.statusText
        });
    },

    /** Set the ``result_fieldgroups`` parameter for the devilry restful API.
     *
     * @param {[String]} [fieldgroups] Restful result_fieldgroups.
     *
     * Example:
     *
     *      setDevilryResultFieldgroups(['everything', 'evenmore']);
     */
    setDevilryResultFieldgroups: function(fieldgroups) {
        if(Ext.typeOf(fieldgroups) !== 'array') {
            throw "setDevilryResultFieldgroups(): fieldgroups must be an array";
        }
        this.extraParams.result_fieldgroups = Ext.JSON.encode(fieldgroups);
    },

    /**
     * Set filters on the devilry restful format
     *
     * @param {[Object]} [filters] Restful filters.
     *
     * Example:
     *
     *      setDevilryFilters([
     *          {field:"long_name", comp:"<", value:"My example value"},
     *          {field:"parentnode", comp:"iexact", value:15}
     *      ]);
     * */
    setDevilryFilters: function(filters) {
        if(Ext.typeOf(filters) !== 'array') {
            throw "setDevilryFilters(): filters must be an array";
        }
        this.extraParams.filters = Ext.JSON.encode(filters);
    },

    /**
     * Set the orderby paramaeter to the devilry restful API.
     *
     * @param {[String]} [fieldgroups] Array of field names.
     *
     * Example:
     *
     *      setDevilryOrderby(['-short_name', 'long_name']);
     */
    setDevilryOrderby: function(orderby) {
        if(Ext.typeOf(orderby) !== 'array') {
            throw "setDevilryOrderby(): orderby must be an array";
        }
        this.extraParams.orderby = Ext.JSON.encode(orderby);
    },

    statics: {
        formatHtmlErrorMessage: function(operation, message) {
            var tpl = Ext.create('Ext.XTemplate', 
                '<div class="section errormessages">',
                '<tpl if="message"><p>{message}</p></tpl>',
                '<tpl if="httperror"><p>{httperror.status} {httperror.statusText}</p></tpl>',
                '<tpl for="errormessages">',
                '   <p>{.}</p>',
                '</tpl>',
                '</div>'
            );
            var tpldata = {message: message};
            if(operation.responseData && operation.responseData.errormessages) {
                tpldata.errormessages = operation.responseData.errormessages;
            } else if(operation.error.status === 0) {
                tpldata.httperror = {'status': 'Lost connection with server.'};
            } else {
                tpldata.httperror = operation.error;
            }
            return tpl.apply(tpldata);
        },

        showErrorMessagePopup: function(operation, title, message) {
            Ext.MessageBox.show({
                title: title,
                msg: devilry.extjshelpers.RestProxy.formatHtmlErrorMessage(operation),
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR
            });
        }
    }
});


Ext.define('devilry.extjshelpers.AutoSizedWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.devilry_autosizedwindow',
    windowPadding: 20,

    initComponent: function() {
        this._preferredWidth = this.width;
        this._preferredHeight = this.height;
        this._setupAutosizing();
        this.maximizable = false;
        this.callParent(arguments);
    },

    _setupAutosizing: function() {
        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShowWindow, this);
    },
    _onShowWindow: function() {
        this.setSizeAndPosition();
    },
    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this.setSizeAndPosition();
        }
    },
    setSizeAndPosition: function() {
        if(this.isFloating()) {
            var padding = this.windowPadding;
            var bodysize = Ext.getBody().getViewSize();
            var bodyWidth = bodysize.width - padding;
            var bodyHeight = bodysize.height - padding;
            var height = bodyHeight;
            var width = bodyWidth;
            if(this._preferredHeight) {
                height = bodyHeight < this._preferredHeight? bodyHeight: this._preferredHeight;
            }
            if(this._preferredWidth) {
                width = bodyWidth < this._preferredWidth? bodyWidth: this._preferredWidth;
            }
            this.setSize({
                width: width,
                height: height
            });
            this.center();
        }
    },

    getPreferredHeight: function() {
        return this._preferredHeight;
    },
    getPreferredWidth: function() {
        return this._preferredWidth;
    }
});


Ext.define('devilry.examiner.models.StaticFeedback', {
    extend: 'devilry.extjshelpers.models.StaticFeedback',
    belongsTo: 'devilry.examiner.models.Delivery',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/examiner/restfulsimplifiedstaticfeedback/'
    })
});


Ext.define('devilry.extjshelpers.page.Footer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.pagefooter',
    border: false,
    margin: '0 0 0 0',
    height: 30,

    html: Ext.create('Ext.XTemplate',
        '<div class="footer">',
        '   <a href="http://devilry.org">Devilry</a> is an open source general purpose delivery system. Visit <a class="projectlink" href="http://devilry.org">http://devilry.org</a> and help us make it better.',
        '</div>'
    ).apply({})
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedFileMeta', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "filename"
        }, 
        {
            "type": "int", 
            "name": "size"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedfilemeta/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.MaximizableWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.maximizablewindow',

    constructor: function(config) {
        this.callParent([config]);

        this.on('maximize', function() {
            window.scrollTo(0, 0);
        }, this);
    }
});


/**
 * Container of a single ``Ext.data.Model`` record, with event listener which
 * fires then the contained record changes.
 */
Ext.define('devilry.extjshelpers.SingleRecordContainer', {
    extend: 'Ext.util.Observable',

    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when setRecord is called.
             * @param singlerecordontainer The SingleRecordContainer that fired the event.
             */
            'setRecord');
        this.callParent([config]);
    },

    /**
     * Set the record and fire the _setRecord_ event.
     */
    setRecord: function(record) {
        this.record = record;
        this.fireEvent('setRecord', this);
    },

    /**
     * Fire the setRecord event to with the current record (used to refresh
     * views after changing the current record).
     */
    fireSetRecordEvent: function() {
        this.fireEvent('setRecord', this);
    }
});


/**
Delete button
*/ 
Ext.define('devilry_extjsextras.DeleteButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.deletebutton',
    ui: 'danger',
    scale: 'large',
    cls: 'devilry_deletebutton',
    text: pgettext('uibutton', 'Delete')
});


Ext.define('devilry_extjsextras.Router', {
    mixins: {
        observable: 'Ext.util.Observable'
    },
    requires: [
        'Ext.util.History'
    ],

    namedParam: /:\w+/g,
    splatParam: /\*\w+/g,
    escapeRegExp: /[-[\]{}()+?.,\\^$|#\s]/g,

    constructor: function(handler, config) {
        this.handler = handler;
        this.routes = [];
        this.started = false;
        this.eventsSuspended = false;

        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            /**
             * @event
             * Fired before a successful route.
             * @param route The Route object.
             * @param routeInfo The route info object (the same that is sent to the handlers).
             */
            'beforeroute',

            /**
             * @event
             * Fired after a successful route.
             * @param route The Route object.
             * @param routeInfo The route info object (the same that is sent to the handlers).
             */
            'afterroute'
        );
    },

    add: function(pattern, action) {
        var regex;
        if(Ext.typeOf(pattern) == 'regexp') {
            regex = pattern;
        } else if(Ext.typeOf(pattern) == 'string') {
            regex = this._patternToRegExp(pattern);
        } else {
            throw 'pattern must be regex.';
        }
        this.routes.push({
            regex: regex,
            action: action
        });
    },

    start: function() {
        if(this.started) {
            throw "Can only start() once!";
        }
        this.started = true;
        this._initHistory();
    },

    _trigger: function(token) {
        if(this.eventsSuspended) {
            this.eventsSuspended = false;
            return;
        }
        if(token == null) {
            token = '';
        }
        var routeInfo = {
            token: token,
            url: '#' + token
        };
        for(var index in this.routes) {
            var route = this.routes[index];
            var match = token.match(route.regex);
            if(match) {
                var args = match.slice(1);
                this.fireEvent('beforeroute', this, routeInfo);
                Ext.bind(this.handler[route.action], this.handler, args, true)(Ext.apply(routeInfo, {
                    action: route.action
                }));
                this.fireEvent('afterroute', this, routeInfo);
                return;
            }
        }
        Ext.bind(this.handler['routeNotFound'], this.handler)(Ext.apply(routeInfo, {
            action: 'routeNotFound'
        }));
    },

    _initHistory: function() {
		Ext.util.History.init(this._onHistoryReady, this);
    },

    _onHistoryReady: function(history) {
        this.resume();
        var token = history.getToken();
        if(token == null) {
            token = '';
        }
        this._trigger(token);
    },

    _onHistoryChange: function(token) {
        this._trigger(token);
    },

    suspend: function() {
        this.mun(Ext.util.History, 'change', this._onHistoryChange, this);
    },

    resume: function() {
        this.mon(Ext.util.History, 'change', this._onHistoryChange, this);
    },
    startOrResume: function() {
        if(this.started) {
            this.resume();
        } else {
            this.start();
        }
    },

    /**
     * @private
     * Convert a route string into a regular expression, suitable for matching
     * against the current location hash.
     */
    _patternToRegExp: function(pattern) {
        var regex = pattern.replace(this.escapeRegExp, '\\$&');
        regex = regex.replace(this.namedParam, '([^\/]*)');
        regex = regex.replace(this.splatParam, '(.*?)');
        return new RegExp('^' + regex + '$');
    },

    /**
     * Remove a prefixed ``#`` from ``token`` if present, or just return the unchanged token.
     */
    normalizeToken: function(token) {
        if(token.length > 0 && token.charAt(0) == '#') {
            return token.substring(1);
        } else {
            return token;
        }
    },

    _navigate: function(token, ignoreDuplicate, suspendEvents) {
        token = this.normalizeToken(token);
        if(ignoreDuplicate && token == Ext.util.History.getToken()) {
            return;
        }
        if(suspendEvents) {
            this.eventsSuspended = true;
        }
        Ext.util.History.add(token);
    },

    /**
     * @param token The token to navigate to. ``token`` is filtered through #normalizeToken.
     * @param ignoreDuplicate Do nothing if the normalized token matches the current token.
     */
    navigate: function(token, ignoreDuplicate) {
        this._navigate(token, ignoreDuplicate);
    },

    /**
     * Set token without triggering the routing events.
     * Use this if you just want to update the URL, but not navigate to the
     * updated URL.
     */
    setHashWithoutEvent: function(token) {
        this._navigate(token, true, true);
    }
});


Ext.define('devilry_header.store.BaseSearchResults', {
    extend: 'Ext.data.Store',

    search: function (params, loadConfig) {
        Ext.apply(this.proxy.extraParams, params);
        this.load(loadConfig);
    }
});

Ext.define('devilry.extjshelpers.SortByLastnameColumn', {
    extend: 'Ext.grid.column.Column',
    alias: 'widget.sortbylastnamecolumn',

    doSort: function(direction) {
        var store = this.up('tablepanel').store;
        store.sort(Ext.create('Ext.util.Sorter', {
            direction: direction,
            sorterFn: Ext.bind(this._sorter, this)
        }));
    },

    _getLastName: function(fullname) {
        var sp = fullname.split(' ');
        return sp[sp.length - 1];
    },

    compare: function(afull, bfull) {
        var alast = this._getLastName(afull);
        var blast = this._getLastName(bfull);
        return alast.localeCompare(blast);
    },

    _sorter: function(a, b) {
        afull = a.get(this.dataIndex);
        bfull = b.get(this.dataIndex);
        if(Ext.typeOf(afull) != 'string') {
            return 1;
        } else if(Ext.typeOf(bfull) != 'string') {
            return -1;
        } else {
            return this.compare(afull, bfull);
        }
    }
});


Ext.define('devilry.statistics.OverviewOfSingleStudent', {
    extend: 'Ext.Component',
    alias: 'widget.statistics-overviewofsinglestudent',
    requires: [
        'devilry.statistics.OverviewOfSingleStudentRecord'
    ],
    
    /**
     * @cfg {Object} [groupInfos]
     */

    /**
     * @cfg {Object} [assignment_store]
     */

    /**
     * @cfg {Object} [labels]
     */

    tpl: [
        '<div style="margin-bottom: 5px">',
        '   <ul class="labels-list">',
        '       <tpl for="labels">',
        '          <li class="label-{label}">{label}</li>',
        '       </tpl>',
        '   </ul>',
        '</div>',
        '<table class="horizontalinfotable">',
        '   <thead><tr>',
        '       <th>Assignment</th>',
        '       <th>Points (no scaling)</th>',
        '       <th>Grade</th>',
        '       <th>Passing grade?</th>',
        '       <th>Open?</th>',
        '   </tr></thead>',
        '   <tbody>',
        '      <tpl for="items">',
        '         <tr>',
        '             <td><a href="{parent.DEVILRY_URLPATH_PREFIX}/administrator/assignmentgroup/{data.id}" target="_blank">{data.assignment__long_name}</a></td>',
        '             <td><tpl if="data.feedback !== null">',
        '                {data.feedback.points}',
        '             </tpl></td>',
        '             <td><tpl if="data.feedback !== null">',
        '                {data.feedback.grade}',
        '             </tpl></td>',
        '             <td>',
        '                 <tpl if="data.feedback === null">',
        '                    <span class="nofeedback">No feedback</span>',
        '                 <tpl else>',
        '                    <tpl if="data.feedback.is_passing_grade">Yes</tpl>',
        '                    <tpl if="!data.feedback.is_passing_grade">No</tpl>',
        '                 </tpl>',
        '             </td>',
        '             <td>',
        '                <tpl if="data.is_open">Yes</tpl>',
        '                <tpl if="!data.is_open">No</tpl>',
        '             </td>',
        '         </tr>',
        '      </tpl>',
        '   </tbody>',
        '   <tfoot>',
        '      <tr>',
        '          <td>Total points</td>',
        '          <td>{total_points}</td>',
        '      </tr>',
        '   </tfoot>',
        '</table>'
    ],

    padding: 10,
    
    initComponent: function() {
        this.total_points = 0;
        var storeData = [];
        Ext.each(this.groupInfos, function(groupInfo, index) {
            var assignmentRecord = this.assignment_store.getById(groupInfo.assignment_id);
            this.total_points += groupInfo.feedback === null? 0: groupInfo.feedback.points;
            var data = {
                id: groupInfo.id,
                is_open: groupInfo.is_open,
                feedback: groupInfo.feedback,
                assignmentid: assignmentRecord.get('id'),
                assignment__short_name: assignmentRecord.get('short_name'),
                assignment__long_name: assignmentRecord.get('long_name')
            };
            storeData.push(data);
        }, this);
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.OverviewOfSingleStudentRecord',
            autoSync: false,
            proxy: 'memory',
            data: storeData
        });

        this.DEVILRY_URLPATH_PREFIX = DevilrySettings.DEVILRY_URLPATH_PREFIX;
        Ext.apply(this, {
            data: {
                items: this.store.data.items,
                labels: this.labels,
                total_points: this.total_points
            }
        });
        this.callParent(arguments);
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedStaticFeedback', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "grade"
        }, 
        {
            "type": "bool", 
            "name": "is_passing_grade"
        }, 
        {
            "type": "auto", 
            "name": "saved_by"
        }, 
        {
            "type": "date", 
            "name": "save_timestamp", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "auto", 
            "name": "rendered_view"
        }, 
        {
            "type": "int", 
            "name": "points"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "date", 
            "name": "delivery__time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "delivery__number"
        }, 
        {
            "type": "auto", 
            "name": "delivery__delivered_by"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifiedstaticfeedback/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "period", "delivery", "candidates", "assignment_group", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedDelivery', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "int", 
            "name": "number"
        }, 
        {
            "type": "date", 
            "name": "time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline"
        }, 
        {
            "type": "bool", 
            "name": "successful"
        }, 
        {
            "type": "int", 
            "name": "delivery_type"
        }, 
        {
            "type": "auto", 
            "name": "alias_delivery"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode"
        }, 
        {
            "type": "int", 
            "name": "deadline__assignment_group__parentnode__delivery_types"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode"
        }, 
        {
            "type": "date", 
            "name": "deadline__assignment_group__parentnode__parentnode__start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "deadline__assignment_group__parentnode__parentnode__end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "delivered_by__identifier"
        }, 
        {
            "type": "date", 
            "name": "deadline__deadline", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifieddelivery/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment_group_users", "assignment", "period", "delivered_by", "deadline", "assignment_group", "candidates", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedFileMeta', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "filename"
        }, 
        {
            "type": "int", 
            "name": "size"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifiedfilemeta/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.Notification', {
    extend: 'Ext.window.Window',
    alias: 'widget.notification',

    initComponent: function() {
        Ext.apply(this, {
            iconCls: this.iconCls,
            cls: 'x-notification',
            width: 200,
            autoHeight: true,
            plain: true,
            border: false,
            draggable: false,
            shadow: true,
            //bodyStyle: 'text-align:center'
        });
        if (this.autoDestroy) {
            this.task = new Ext.util.DelayedTask(this.hide, this);
        } else {
            this.closable = true;
        }

        this.callParent(arguments);
    },


    setMessage: function(msg) {
        this.update(msg);
    },

    setTitle: function(title, iconCls) {
        devilry.extjshelpers.Notification.superclass.setTitle.call(this, title, iconCls || this.iconCls);
    },

    onDestroy: function() {
        devilry.extjshelpers.Notification.superclass.onDestroy.call(this);
    },

    cancelHiding: function() {
        this.addClass('fixed');
        if (this.autoDestroy) {
            this.task.cancel();
        }
    },

    afterShow: function() {
        devilry.extjshelpers.Notification.superclass.afterShow.call(this);
        Ext.fly(this.body.dom).on('click', this.cancelHiding, this);
        if (this.autoDestroy) {
            this.task.delay(this.hideDelay || 5000);
        }
    },

    beforeShow: function() {
        this.el.hide();
    },

    onShow: function() {
        var me = this;

        var pos = devilry.extjshelpers.NotificationManager.height + 10;
        this.el.alignTo(document, "tr-tr", [-20, 10 + pos]);
        devilry.extjshelpers.NotificationManager.height = pos + this.getHeight();

        this.el.slideIn('t', {
            duration: 500,
            listeners: {
                afteranimate: {
                    fn: function() {
                        me.el.show();
                    }
                }
            }
        });
    },

    onHide: function() {
        this.el.disableShadow();
        this.el.ghost("t", {
            duration: 500,
            remove: true
        });
        devilry.extjshelpers.NotificationManager.height -= this.getHeight() - 10;
    },

    focus: Ext.emptyFn
});


Ext.define('devilry.administrator.models.StaticFeedback', {
    extend: 'devilry.extjshelpers.models.StaticFeedback',
    belongsTo: 'devilry.administrator.models.Delivery',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifiedstaticfeedback/'
    })
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedDeadline', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "text"
        }, 
        {
            "type": "date", 
            "name": "deadline", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "number_of_deliveries"
        }, 
        {
            "type": "bool", 
            "name": "feedbacks_published"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__id"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__delivery_types"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__name"
        }, 
        {
            "type": "bool", 
            "name": "assignment_group__is_open"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__candidates__identifier"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifieddeadline/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "assignment_group", "assignment_group_users", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "name"
        }, 
        {
            "type": "bool", 
            "name": "is_open"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "feedback"
        }, 
        {
            "type": "auto", 
            "name": "latest_delivery_id"
        }, 
        {
            "type": "auto", 
            "name": "latest_deadline_id"
        }, 
        {
            "type": "auto", 
            "name": "latest_deadline_deadline"
        }, 
        {
            "type": "auto", 
            "name": "number_of_deliveries"
        }, 
        {
            "type": "int", 
            "name": "feedback__points"
        }, 
        {
            "type": "auto", 
            "name": "feedback__grade"
        }, 
        {
            "type": "bool", 
            "name": "feedback__is_passing_grade"
        }, 
        {
            "type": "auto", 
            "name": "tags__tag"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "bool", 
            "name": "parentnode__anonymous"
        }, 
        {
            "type": "int", 
            "name": "parentnode__delivery_types"
        }, 
        {
            "type": "date", 
            "name": "parentnode__publishing_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "feedback__delivery__number"
        }, 
        {
            "type": "date", 
            "name": "feedback__delivery__time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "feedback__delivery__delivery_type"
        }, 
        {
            "type": "auto", 
            "name": "feedback__delivery__deadline"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "candidates"
        }, 
        {
            "type": "auto", 
            "name": "candidates__student__username"
        }, 
        {
            "type": "auto", 
            "name": "candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "examiners__user__username"
        }, 
        {
            "type": "auto", 
            "name": "feedback__rendered_view"
        }, 
        {
            "type": "auto", 
            "name": "candidates__student__devilryuserprofile__full_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "fake_examiners"
        }, 
        {
            "type": "auto", 
            "name": "fake_candidates"
        }, 
        {
            "type": "auto", 
            "name": "fake_tags"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedassignmentgroup/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["feedback", "tags", "assignment", "feedbackdelivery", "period", "candidates", "users", "feedback_rendered_view", "students_full_name", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.statistics.activeperiods.AggregatedPeriodModel', {
    extend: 'Ext.data.Model',
    fields: ['period_id', 'subject_long_name', 'period_long_name', 'qualifies_for_exam_ready_for_export'],
    idProperty: 'period_id'
});


Ext.define('devilry.gradeeditors.FailureHandler', {
    statics: {
        onFailure: function(operation) {
            var title = 'Failed to save!';
            var msg = 'Please try again';
            var icon = Ext.Msg.ERROR;
            if(operation.error.status === 0) {
                title = 'Server error';
                msg = 'Could not contact the server. Please try again.';
            } else if(operation.error.status === 400) {
                title = 'Failed to save!';
                msg = operation.responseData.items.errormessages[0];
                icon = Ext.Msg.WARNING;
            }
            Ext.MessageBox.show({
                title: title,
                msg: msg,
                buttons: Ext.Msg.OK,
                icon: icon,
                closable: false
            });
        }
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "period"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "application"
        }, 
        {
            "type": "auto", 
            "name": "key"
        }, 
        {
            "type": "auto", 
            "name": "value"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedperiodapplicationkeyvalue/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.gradeeditors.simplified.administrator.SimplifiedFeedbackDraft', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "auto", 
            "name": "saved_by"
        }, 
        {
            "type": "date", 
            "name": "save_timestamp", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "draft"
        }, 
        {
            "type": "bool", 
            "name": "published"
        }, 
        {
            "type": "auto", 
            "name": "staticfeedback"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/gradeeditors/administrator/restfulsimplifiedfeedbackdraft/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

/**
 * */
Ext.define('devilry_extjsextras.GridBigButtonCheckboxModel', {
    extend: 'Ext.selection.CheckboxModel',

    headerWidth: 50, // The width of the checkbox column

    /**
     * Configuration for the header cell (the cell where you can select/deselect all)
     */
    getHeaderConfig: function() {
        var config = this.callParent(arguments);
        if(config.cls !== '') { // If we do not have a header, cls will be empty, and we should keep it that way
            config.cls += ' ' + 'devilry-column-header-checkbox-bigbutton';
        }
        return config;
    },
    
    /**
     * Called to render the cells containing the checkbox for each row.
     * The same as the superclass, but we add our own css class.
     */
    renderer: function(value, metaData, record, rowIndex, colIndex, store, view) {
        var baseCSSPrefix = Ext.baseCSSPrefix;
        metaData.tdCls = baseCSSPrefix + 'grid-cell-special ' + baseCSSPrefix + 'grid-cell-row-checker devilry-grid-cell-row-checker-bigbutton';
        return '<div class="' + baseCSSPrefix + 'grid-row-checker">&#160;</div>';
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedRelatedExaminer', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "period"
        }, 
        {
            "type": "auto", 
            "name": "user"
        }, 
        {
            "type": "auto", 
            "name": "tags"
        }, 
        {
            "type": "auto", 
            "name": "user__username"
        }, 
        {
            "type": "auto", 
            "name": "user__devilryuserprofile__full_name"
        }, 
        {
            "type": "auto", 
            "name": "user__email"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedrelatedexaminer/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.SortFullNameByGlobalPolicyColumn', {
    extend: 'devilry.extjshelpers.SortByLastnameColumn',
    alias: 'widget.sortfullnamebyglobalpolicycolumn',

    compare: function(afull, bfull) {
        if(DevilrySettings.DEVILRY_SORT_FULL_NAME_BY_LASTNAME) {
            return this.callParent(arguments);
        } else {
            return afull.localeCompare(bfull);
        }
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedCandidate', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "student"
        }, 
        {
            "type": "auto", 
            "name": "candidate_id"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "identifier"
        }, 
        {
            "type": "auto", 
            "name": "full_name"
        }, 
        {
            "type": "auto", 
            "name": "email"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedcandidate/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.RangeSelect', {
    extend: 'Ext.form.Panel',
    alias: 'widget.statistics-rangeselect',

    config: {
        initialMin: undefined,
        initialMax: undefined
    },
    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },

            fieldDefaults: {
                labelAlign: 'top',
                labelWidth: 100,
                labelStyle: 'font-weight:bold'
            },
            items: [{
                name: "min",
                fieldLabel: "Minimum",
                xtype: 'numberfield',
                value: this.initialMin,
                emptyText: 'Example: 0. Not checked if not specified.'
            }, {
                name: "max",
                fieldLabel: "Maximum",
                xtype: 'numberfield',
                value: this.initialMax,
                emptyText: 'Example: 1000. Not checked if not specified.'
            }]
        });
        this.callParent(arguments);
    }
});


/**
 * @class Ext.ux.grid.Printer
 * @author Ed Spencer (edward@domine.co.uk)
 * Helper class to easily print the contents of a grid. Will open a new window with a table where the first row
 * contains the headings from your column model, and with a row for each item in your grid's store. When formatted
 * with appropriate CSS it should look very similar to a default grid. If renderers are specified in your column
 * model, they will be used in creating the table. Override headerTpl and bodyTpl to change how the markup is generated
 * 
 * Usage:
 * 
 * 1 - Add Ext.Require Before the Grid code
 * Ext.require([
 *   'Ext.ux.grid.GridPrinter',
 * ]);
 * 
 * 2 - Declare the Grid 
 * var grid = Ext.create('Ext.grid.Panel', {
 *   columns: //some column model,
 *   store   : //some store
 * });
 * 
 * 3 - Print!
 * Ext.ux.grid.Printer.print(grid);
 * 
 * Original url: http://edspencer.net/2009/07/printing-grids-with-ext-js.html
 * 
 * Modified by Loiane Groner (me@loiane.com) - September 2011 - Ported to Ext JS 4
 * http://loianegroner.com (English)
 * http://loiane.com (Portuguese)
 */
Ext.define("Ext.ux.grid.Printer", {
	
	requires: 'Ext.XTemplate',

	statics: {
		/**
		 * Prints the passed grid. Reflects on the grid's column model to build a table, and fills it using the store
		 * @param {Ext.grid.Panel} grid The grid to print
         *
         * @param {Boolean} printAutomatically True to open the print dialog
         *      automatically and close the window after printing. False to simply
         *      open the print version of the grid (defaults to true)
		 */
		print: function(grid, printAutomatically) {
			//We generate an XTemplate here by using 2 intermediary XTemplates - one to create the header,
			//the other to create the body (see the escaped {} below)
			var columns = grid.columns;

			//build a useable array of store data for the XTemplate
			var data = [];
			grid.store.data.each(function(item) {
				//var convertedData = [];

                var rowData = [];
                Ext.each(columns, function(column) {
                    var cellValue = item.data[column.dataIndex];
                    var renderedCell = column.renderer? column.renderer(cellValue, undefined, item): cellValue;
                    rowData.push({renderedCell: renderedCell});
                }, this);
                data.push(rowData);
			});

			//use the headerTpl and bodyTpl markups to create the main XTemplate below
			var headings = Ext.create('Ext.XTemplate', this.headerTpl).apply(columns);
			var body     = Ext.create('Ext.XTemplate', this.bodyTpl).apply(data);
			
            var title = grid.title;
            if(Ext.isEmpty(title)) {
                title = 'Print';
            }
			var htmlMarkup = [
				'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
				'<html>',
				  '<head>',
				    '<meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />',
                    '<link href="' + this.stylesheetPath + '" rel="stylesheet" type="text/css" media="screen,print" />',
				    '<title>' + title + '</title>',
				  '</head>',
				  '<body>',
				    '<table>',
				      headings,
				      '<tpl for=".">',
                        '<tr>',
                            '<tpl for=".">',
                                '<td>{renderedCell}</td>',
                            '</tpl>',
                        '</tr>',
				      '</tpl>',
				    '</table>',
				  '</body>',
				'</html>'           
			];

			var html = Ext.create('Ext.XTemplate', htmlMarkup).apply(data); 

			//open up a new printing window, write to it, print it and close
			var win = window.open('', 'printgrid');

			win.document.write(html);
            win.document.close();
            win.focus();

			if (printAutomatically){
                Ext.defer(function() {
                    win.print();
                    win.close();
                }, 200);
			}
		},

		/**
		 * @property stylesheetPath
		 * @type String
		 * The path at which the print stylesheet can be found (defaults to 'ux/grid/gridPrinterCss/print.css')
		 */
		stylesheetPath: DevilrySettings.DEVILRY_STATIC_URL + '/extjsux/ux/grid/print.css',
		
		/**
		 * @property headerTpl
		 * @type {Object/Array} values
		 * The markup used to create the headings row. By default this just uses <th> elements, override to provide your own
		 */
		headerTpl: [ 
			'<tr>',
				'<tpl for=".">',
					'<th>{header}</th>',
				'</tpl>',
			'</tr>'
		]
	}
});


Ext.define('devilry.extjshelpers.AsyncActionPool', {
    singleton: true,
    config: {
        size: 20
    },

    constructor: function(config) {
        this.initConfig(config);
        this._occupants = 0;
    },

    add: function(options) {
        this._run(options);
    },

    _run: function(options) {
        if(this._occupants > this.size) {
            Ext.defer(function() {
                this._run(options);
            }, 250, this);
            return;
        }
        //console.log('Running', this._occupants);
        this._occupants ++;
        Ext.bind(options.callback, options.scope, options.args, true)(this);
    },

    notifyTaskCompleted: function() {
        this._occupants --;
        //console.log('completed', this._occupants);
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedAssignmentGroup', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "name"
        }, 
        {
            "type": "bool", 
            "name": "is_open"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "feedback"
        }, 
        {
            "type": "auto", 
            "name": "latest_delivery_id"
        }, 
        {
            "type": "auto", 
            "name": "latest_deadline_id"
        }, 
        {
            "type": "auto", 
            "name": "latest_deadline_deadline"
        }, 
        {
            "type": "auto", 
            "name": "number_of_deliveries"
        }, 
        {
            "type": "auto", 
            "name": "candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "bool", 
            "name": "parentnode__anonymous"
        }, 
        {
            "type": "int", 
            "name": "parentnode__delivery_types"
        }, 
        {
            "type": "date", 
            "name": "parentnode__publishing_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "feedback__points"
        }, 
        {
            "type": "auto", 
            "name": "feedback__grade"
        }, 
        {
            "type": "bool", 
            "name": "feedback__is_passing_grade"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__short_name"
        }, 
        {
            "type": "int", 
            "name": "feedback__delivery__number"
        }, 
        {
            "type": "date", 
            "name": "feedback__delivery__time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "feedback__delivery__delivery_type"
        }, 
        {
            "type": "auto", 
            "name": "feedback__delivery__deadline"
        }, 
        {
            "type": "auto", 
            "name": "candidates"
        }, 
        {
            "type": "auto", 
            "name": "feedback__rendered_view"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode__short_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifiedassignmentgroup/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["users", "assignment", "feedback", "period", "feedbackdelivery", "candidates", "feedback_rendered_view", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry_extjsextras.ContainerWithEditTitle', {
    extend: 'Ext.container.Container',
    alias: 'widget.containerwithedittitle',

    /**
     * @cfg {String} [cls="containerwithedittitle"]
     * Defaults to ``containerwithedittitle``.
     */
    cls: 'containerwithedittitle',

    /**
     * @cfg {String} title
     */

    /**
     * @cfg {Array|Ext.XTemplate} [titleTag="h4"]
     */
    titleTag: 'h4',

    /**
     * @cfg {String} [titleCls='editablesidebarbox_title bootstrap']
     * The css class of the title box.
     */
    titleCls: 'titlebox bootstrap',

    /**
     * @cfg {String} buttontext (optional)
     * Button text. Defaults to "Edit" (translated).
     */
    buttonText: pgettext('uibutton', 'edit'),

    /**
     * @cfg {String} [buttonSuffix]
     * HTML to suffix to the ``buttonText``. Typicallu used to add an icon after the text.
     */
    //buttonSuffix: '<i class="icon-edit"></i>',
    buttonSuffix: '',

    /**
     * @cfg {String} [title]
     * The title text.
     */

    /**
     * @cfg {Object} [body]
     * The config for the body element. The container
     * uses anchor layout to lay out the title and the body.
     */

    constructor: function(config) {
        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            /**
             * @event
             * Fired when the edit-button is clicked.
             * @param box This ContainerWithEditTitle.
             */
            'edit'
        );
        this.callParent([config]);
    },

    initComponent: function() {
        var titleInnerTpl = [
            '{title}',
            '&nbsp;',
            '<a class="edit_link btn btn-mini" style="margin-top: -6px;" href="{editurl}">',
                this.buttonText,
                this.buttonSuffix,
            '</a>'
        ];
        var titletpl = Ext.String.format('<{0}>{1}</{2}>',
            this.titleTag, titleInnerTpl.join(''), this.titleTag);
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'box',
                itemId: 'title',
                anchor: '100%',
                cls: this.titleCls,
                tpl: titletpl,
                data: {
                    title: this.title,
                    editurl: '#'
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a.edit_link',
                    click: function(e) {
                        e.preventDefault();
                        this.fireEvent('edit', this);
                    }
                }
            }, this.body]
        });
        this.callParent(arguments);
    },

    updateTitle: function(title, editurl) {
        if(typeof editurl === 'undefined') {
            editurl = '#';
        }
        this.down('#title').update({
            title: title,
            editurl: editurl
        });
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedDeadline', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "text"
        }, 
        {
            "type": "date", 
            "name": "deadline", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "number_of_deliveries"
        }, 
        {
            "type": "bool", 
            "name": "feedbacks_published"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__id"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__delivery_types"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__name"
        }, 
        {
            "type": "bool", 
            "name": "assignment_group__is_open"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__candidates__identifier"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifieddeadline/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "assignment_group", "assignment_group_users", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry_extjsextras.EvenRandomSelection', {
    config: {
        /**
        * @cfg {Object[]} [selection]
        * The items in the selection pool.
        */
        selection: []
    },

    constructor: function(config) {
        this.pool = []; // Currently available subset of the selection. When this is empty, it is re-cloned from selection
        this.initConfig(config);
    },

    /** Get random item from the selection pool.
     *
     * The pool is filled with ``selection``, re-filled each time the pool is
     * empty. This method picks a random item from the pool. This means that
     * we always pick every item in the pool before we re-start picking items. */
    getRandomItem: function() {
        if(this.pool.length === 0) {
            this.pool = Ext.Array.clone(this.selection);
        }
        var randomIndex = Math.floor(Math.random() * (this.pool.length));
        var next = this.pool[randomIndex];
        Ext.Array.remove(this.pool, next);
        return next;
    }
});


Ext.define('devilry.statistics.ChooseAssignmentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-chooseassignmentsgrid',
    hideHeaders: true,
    title: 'Choose assignments',

    requires: [
        'devilry.extjshelpers.GridSelectionModel'
    ],

    /**
     * @cfg {int[]} [selectedAssignmentIds=undefined]
     */
    
    
    initComponent: function() {
        this.selModel = Ext.create('devilry.extjshelpers.GridSelectionModel', {
            checkOnly: false
        });
        Ext.apply(this, {
            columns: [{
                header: 'Long name',  dataIndex: 'long_name', flex: 1
            }]
        });
        this.on('render', function() {
            if(this.selectedAssignmentIds) {
                this._selectByIds(this.selectedAssignmentIds);
            }
        }, this);
        this.callParent(arguments);
    },

    _selectByIds: function(assignmentIds) {
        this.setLoading(true);
        var records = [];
        Ext.each(assignmentIds, function(assignmentId, index) {
            var record = this.store.getById(assignmentId);
            records.push(record);
        }, this);
        this._selectRecords(records);
    },

    _selectRecords: function(records) {
        Ext.defer(function() { // NOTE: Defer to work around ExtJS rendering order issues.
            this.getSelectionModel().select(records);
            this.setLoading(false);
        }, 500, this);
    },

    getIdOfSelected: function() {
        var assignment_ids = [];
        Ext.each(this.getSelectionModel().getSelection(), function(assignmentRecord, index) {
            assignment_ids.push(assignmentRecord.get('id'));
        }, this);
        return assignment_ids;
    },


    checkAtLeastOneSelected: function() {
        var assignment_ids = this.getIdOfSelected();
        if(assignment_ids.length === 0) {
            Ext.MessageBox.alert('Invalid input', 'Please select at least one assignment');
            return false;
        }
        return true;
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedPeriod', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "date", 
            "name": "start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifiedperiod/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

/** A button in a {@link devilry.extjshelpers.ButtonBar}. */
Ext.define('devilry.extjshelpers.ButtonBarButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.buttonbarbutton',
    scale: 'large',
    hidden: true,

    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` for tooltip. (Optional).
         */
        tooltipTpl: Ext.create('Ext.XTemplate',
            '<div class="tooltip-title">{title}</div><p>{body}</p>'
        ),

        /**
         * @cfg
         * Tooltip config. Should be an Object with title and body attributes. (Required).
         */
        tooltipCfg: undefined,

        /**
         * @cfg
         * If defined, the handler is set to open this url.
         */
        clickurl: undefined,

        /**
         * @cfg
         * The store to use to check if this button should be visible. The store will have it pageSize set to 1.
         */
        store: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var me = this;
        this._loadStore();
        if(this.clickurl) {
            this.handler = function() {
                window.location = me.clickurl;
            }
        }
        Ext.apply(this, {
            listeners: {
                render: function() {
                    Ext.create('Ext.tip.ToolTip', {
                        target: me.id,
                        anchor: 'top',
                        dismissDelay: 30000,
                        html: me.tooltipTpl.apply(me.tooltipCfg)
                    });
                }
            },
        });
        this.callParent(arguments);
    },

    _loadStore: function() {
        this.store.load();
        this.store.on('load', function(store, records) {
            if(this.store.totalCount || this.is_superuser) {
                this.show();
            }
            hasRecords = (this.store.totalCount > 0 || this.is_superuser);
            this.up('buttonbar').notifyStoreLoad(hasRecords);
            //this.up('buttonbar').notifyStoreLoad(false);
        }, this);
    }
});


Ext.define('devilry.extjshelpers.ErrorList', {
    extend: 'Ext.panel.Panel',
    title: 'Errors',
    cls: 'errorlist',
    bodyCls: 'errorlist-body',
    hidden: true,
    margin: {
        bottom: 15
    },

    addError: function(error) {
        this.add({
            xtype: 'component',
            html: Ext.String.format('<p class="errorlist-item">{0}</p>', error)
        });
        this.show();
    },

    clearErrors: function() {
        this.removeAll();
        this.hide();
    }
});


/**
 * Search results for many results, each result shown in a
 * {@link devilry.extjshelpers.searchwidget.SearchResults}.
 * */
Ext.define('devilry.extjshelpers.searchwidget.MultiSearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.multisearchresults',
    cls: 'multisearchresults',
    autoScroll: true,
    
    config: {
        searchWidget: undefined
    }
});


/**
Cancel button
*/ 
Ext.define('devilry_extjsextras.CancelButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.cancelbutton',
    scale: 'medium',
    cls: 'devilry_extjsextras_cancelbutton',
    text: pgettext('uibutton', 'Cancel')
});


Ext.define('devilry.statistics.activeperiods.Overview', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.activeperiods-overview',
    frame: false,
    border: false,
    autoScroll: true,
    //cls: 'selectable-grid',

    requires: [
        'devilry.extjshelpers.DateTime',
        'devilry.statistics.activeperiods.AggregatedPeriodModel',
        'devilry.extjshelpers.RestProxy',
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.GridSelectionModel'
    ],
    
    /**
     * @cfg
     */
    nodeRecord: undefined,


    linkTpl: Ext.create('Ext.XTemplate',
        '<a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/administrator/period/{data.period_id}?open_students=yes&students_hidesidebar=yes">',
        '{data.subject_long_name} ({data.period_long_name})',
        '</a>'
    ),

    readyForExportTpl: Ext.create('Ext.XTemplate',
        '<tpl if="qualifies_for_exam_ready_for_export"><span class="goodInlineItem">yes</span></tpl>',
        '<tpl if="!qualifies_for_exam_ready_for_export"><span class="warningInlineItem">no</span></tpl>'
    ),

    emailLinkTpl: Ext.create('Ext.XTemplate',
        'mailto:{from}?',
        'bcc={emailAddresses}'
    ),

    emailTooltip: 'Opens your email application to send email to all admins on selected rows. Use the checkbox in the upper left corner to select all visible rows.' +
        (Ext.isIE8? '<p>WARNING: Your browser, Internet Explorer, can not handle email links containing many addresses. Use another browser if you encounter this problem.</p>': ''),
    
    initComponent: function() {
        this._createStore();
        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            checkOnly: true
        });

        Ext.apply(this, {
            tbar: [
                //xtype: 'searchfield',
                //searchdelay: 30,
                //emptyText: 'Search...',
                //width: 200,
                //listeners: {
                    //scope: this,
                    //newSearchValue: this._onNewSearchValue,
                    //emptyInput: this._onEmptySearchValue
                //}
            {
                xtype: 'button',
                iconCls: 'icon-email-16',
                text: 'Send email to admin(s) on selected',
                listeners: {
                    scope: this,
                    click: this._sendEmailsToSelected,
                    render: function(button) {
                        Ext.tip.QuickTipManager.register({
                            target: button.getEl(),
                            title: 'Click to send email to admins on selected',
                            text: this.emailTooltip,
                            width: 350,
                            dismissDelay: 30000 // Hide after 30 seconds hover
                        });
                    }
                }
            }, '->', {
                xtype: 'combobox',
                width: 350,
                valueField: 'filterfunc',
                displayField: 'label',
                forceSelection: true,
                editable: false,
                emptyText: 'Show all',
                store: Ext.create('Ext.data.Store', {
                    fields: ['filterfunc', 'label'],
                    data: [{
                        filterfunc: this._clearFilters,
                        label: 'Show all'
                    }, {
                        filterfunc: this._filterQualifiesForExamYes,
                        label: 'Show qualifies-for-exam ready for export'
                    }, {
                        filterfunc: this._filterQualifiesForExamNo,
                        label: 'Show qualifies-for-exam NOT ready for export'
                    }],
                    proxy: 'memory'
                }),
                listeners: {
                    scope: this,
                    select: function(combo, records) {
                        var record = records[0];
                        var filterfunc = record.get('filterfunc');
                        Ext.bind(filterfunc, this)();
                    }
                }
            }],
            columns: [{
                text: 'Subject',
                dataIndex: 'subject_long_name',
                flex: 30,
                renderer: function(v, m, record) {
                    return this.linkTpl.apply({
                        data: record.data,
                        DevilrySettings: DevilrySettings
                    });
                }
            },{
                text: '&laquo;Qualifies for exam&raquo; ready for export?',
                dataIndex: 'qualifies_for_exam_ready_for_export',
                width: 230,
                renderer: function(value, m, record) {
                    return this.readyForExportTpl.apply(record.data);
                }
            }],
            listeners: {
                scope: this,
                //itemmouseup: function(view, record) {
                    //var url = Ext.String.format('{0}/administrator/period/{1}?open_students=yes&students_hidesidebar=yes', DevilrySettings.DEVILRY_URLPATH_PREFIX, record.get('period_id'));
                    //window.open(url, '_blank');
                //},
                render: function() {
                    Ext.defer(function() {
                        this._createAndLoadPeriodStore();
                    }, 100, this);
                }
            }
        });
        this.callParent(arguments);
    },


    _filterQualifiesForExamYes: function() {
        this.store.clearFilter();
        this.store.filter('qualifies_for_exam_ready_for_export', true);
    },
    _filterQualifiesForExamNo: function() {
        this.store.clearFilter();
        this.store.filter('qualifies_for_exam_ready_for_export', false);
    },
    _clearFilters: function() {
        this.store.clearFilter();
    },

    //_onNewSearchValue: function(value) {
        //console.log(value);
    //},

    //_onEmptySearchValue: function() {
    //},


    _createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.activeperiods.AggregatedPeriodModel',
            autoSync: false,
            proxy: 'memory'
        });
    },

    _createAndLoadPeriodStore: function() {
        this.getEl().mask('Loading overview');
        this.periodstore = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.periodstore.proxy.setDevilryFilters([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: this.nodeRecord.get('id')
        }, {
            field: 'start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.periodstore.proxy.setDevilryOrderby(['-publishing_time']);
        this.periodstore.pageSize = 100000;
        this.periodstore.load({
            scope: this,
            callback: this._onPeriodStoreLoad
        });
    },

    _onPeriodStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load active periods.');
        } else {
            this._createAndLoadPeriodAppKeyValueStore();
        }
    },

    _createAndLoadPeriodAppKeyValueStore: function() {
        this.periodappkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.periodappkeyvalue_store.proxy.setDevilryFilters([{
            field: 'period__parentnode__parentnode',
            comp: 'exact',
            value: this.nodeRecord.get('id')
        }, {
            field: 'period__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'period__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'application',
            comp: 'exact',
            value: 'statistics-qualifiesforexam'
        }, {
            field: 'key',
            comp: 'exact',
            value: 'ready-for-export'
        }]);
        this.periodappkeyvalue_store.pageSize = 100000;
        this.periodappkeyvalue_store.load({
            scope: this,
            callback: this._onPeriodAppKeyValueStoreLoad
        });
    },

    _onPeriodAppKeyValueStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load ready-for-export status on active periods.');
        } else {
            this._createAndLoadSubjectStore();
        }
    },


    _createAndLoadSubjectStore: function() {
        this.subjectstore = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedSubject',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.subjectstore.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.nodeRecord.get('id')
        }]);
        this.subjectstore.pageSize = 100000;
        this.subjectstore.load({
            scope: this,
            callback: this._onSubjectStoreLoad
        });
    },

    _onSubjectStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load subjects.');
        } else {
            this._populateStore();
        }
    },

    _handleLoadError: function(op, title) {
        this.getEl().unmask();
        devilry.extjshelpers.RestProxy.showErrorMessagePopup(op, title);
    },

    _populateStore: function() {
        Ext.each(this.periodstore.data.items, function(periodRecord, index) {
            this.store.add({
                'period_id': periodRecord.get('id'),
                'subject_long_name': periodRecord.get('parentnode__long_name'),
                'period_long_name': periodRecord.get('long_name'),
                'qualifies_for_exam_ready_for_export': false
            });
        }, this);

        Ext.each(this.periodappkeyvalue_store.data.items, function(appKeyValueRecord, index) {
            var period_id = appKeyValueRecord.get('period');
            var periodRecord = this.periodstore.getById(period_id);
            var storeRecord = this.store.getById(period_id);
            storeRecord.set('qualifies_for_exam_ready_for_export', true);
            storeRecord.commit(); // Removed red corner
        }, this);
        this.getEl().unmask();

        this.store.sort('subject_long_name', 'ASC');
    },

    //_sendEmailsToVisible: function() {
        //var emailAddresses = this._getAdminEmailAddressesFromRecords(this.store.data.items).join(',');
        //window.location = this.emailLinkTpl.apply({
            //emailAddresses: emailAddresses
        //});
    //},

    _sendEmailsToSelected: function() {
        var selected = this.getSelectionModel().getSelection();
        if(selected.length === 0) {
            Ext.MessageBox.alert('Error', 'Please select at least one row.');
            return;
        }
        var emailAddresses = this._getAdminEmailAddressesFromRecords(selected).join(',');
        window.location = this.emailLinkTpl.apply({
            emailAddresses: emailAddresses
        });
    },

    _getAdminEmailAddressesFromRecords: function(records) {
        var emails = [];
        Ext.each(records, function(record, index) {
            var periodRecord = this.periodstore.getById(record.get('period_id'));
            var subjectid = periodRecord.get('parentnode');
            var subjectRecord = this.subjectstore.getById(subjectid);
            emails = Ext.Array.merge(emails, periodRecord.get('admins__email'));
            emails = Ext.Array.merge(emails, subjectRecord.get('admins__email'));
        }, this);
        return emails;
    }
});


Ext.define('devilry.student.models.StaticFeedback', {
    extend: 'devilry.extjshelpers.models.StaticFeedback',
    belongsTo: 'devilry.student.models.Delivery',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/student/restfulsimplifiedstaticfeedback/'
    })
});


Ext.define('devilry.extjshelpers.GridPrintButton', {
    //extend: 'Ext.button.Split',
    extend: 'Ext.button.Button',
    alias: 'widget.gridprintbutton',

    initComponent: function() {
        Ext.apply(this, {
            text: 'Print',
            iconCls: 'icon-print-16',
            tooltip: {
                title: 'Open print formatted table in new window.',
                text: 'Use the print button/menu item in your browser to print the table.'
            }
            //menu: [{
                //text: 'Print format',
                //listeners: {
                    //scope: this,
                    //click: this._onPrintFormat
                //}
            //}]
        });
        this.on('click', this._onPrint, this);
        this.callParent(arguments);
    },

    _onPrint: function() {
        this.fireEvent('printformat');
    }

    //_onPrintFormat: function() {
        //this.fireEvent('printformat');
    //}
});


Ext.define('devilry.extjshelpers.studentsmanager.MultiResultWindow', {
    extend: 'devilry.extjshelpers.AutoSizedWindow',
    layout: 'fit',
    closeAction: 'hide',
    closable: false,
    width: 600,
    height: 400,
    modal: true,
    maximizable: true,

    config: {
        isAdministrator: undefined
    },

    logTpl: Ext.create('Ext.XTemplate',
        '<tpl for="log">',
        '    <div class="section {parent.csscls}-small">',
        '        <h1>',
        '            <tpl if="assgnmentGroupRecord.data.name">',
        '               {assgnmentGroupRecord.data.name} -',
        '            </tpl>',
        '            <tpl if="parent.isAdministrator">',
        '                <tpl for="assgnmentGroupRecord.data.candidates__student__username">',
        '                   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '                </tpl>',
        '            </tpl>',
        '            <tpl if="!parent.isAdministrator">',
        '                <tpl for="assgnmentGroupRecord.data.candidates">',
        '                   {identifier}<tpl if="xindex &lt; xcount">, </tpl>',
        '                </tpl>',
        '            </tpl>',
        '        </h1>',
        '        {msg}',
        '    </div>',
        '</tpl>'
    ),

    operationErrorTpl: Ext.create('Ext.XTemplate',
        '{msg}. ',
        '<tpl if="status === 0">',
        '    Error details: Could not connect to the Devilry server.',
        '</tpl>',
        '<tpl if="status !== 0">',
        '    (Error code: {status}) Error details: <strong>{statusText}</strong>',
        '</tpl>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.errorcontainer = Ext.widget('panel', {
            title: 'Errors',
            bodyPadding: 10
        });
        this.warningcontainer = Ext.widget('panel', {
            title: 'Warnings',
            bodyPadding: 10
        });
        this.successcontainer = Ext.widget('panel', {
            title: 'Successful',
            bodyPadding: 10
        });
        Ext.apply(this, {
            items: {
                xtype: 'panel',
                border: false,
                layout: 'accordion'
            },
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    text: 'Close this window',
                    scale: 'large',
                    listeners: {
                        scope: this,
                        click: function() {
                            this.close();
                        }
                    }
                }, '->']
            }]
        });
        this.callParent(arguments);
    },

    addToLog: function(level, assgnmentGroupRecord, msg) {
        
        var logitem = {
            assgnmentGroupRecord: assgnmentGroupRecord,
            msg: msg
        }
        this.log[level].push(logitem);
    },

    addError: function(assgnmentGroupRecord, msg) {
        this.addToLog('error', assgnmentGroupRecord, msg);
    },

    _createErrorMessageFromResponseData: function(responseData) {
        if(typeof responseData.items === 'undefined') {
            throw "responseData.items == undefined";
        }
        var messages = [];

        var fieldErrors = responseData.items.fielderrors;
        if(typeof fieldErrors !== 'undefined') {
            Ext.Object.each(fieldErrors, function(fieldname, errormessages) {
                if(fieldname !== '__all__') { // Note: We assume __all__ is also in errormessages, which is added below
                    messages.push(Ext.String.format('{0}: {1}', fieldname, errormessages.join('. ')));
                }
            }, this);
        }

        var globalErrors = responseData.items.errormessages;
        if(typeof globalErrors !== 'undefined') {
            Ext.Array.each(globalErrors, function(errormessage) {
                messages.push(errormessage);
            }, this);
        }

        return messages;
    },

    addErrorFromOperation: function(assgnmentGroupRecord, msg, operation) {
        var errormessage = operation.error.statusText;
        try {
            var responseData = Ext.JSON.decode(operation.response.responseText);
            var messages = this._createErrorMessageFromResponseData(responseData);
            if(messages.length > 0) {
                errormessage = messages.join('<br/>');
            }
        } catch(e) {
            // Ignore decode errors (we just use the generic statusText instead.
        }
        var fullMsg = this.operationErrorTpl.apply({
            msg: msg,
            status: operation.error.status,
            statusText: errormessage
        });
        this.addToLog('error', assgnmentGroupRecord, fullMsg);
    },

    addWarning: function(assgnmentGroupRecord, msg) {
        this.addToLog('warning', assgnmentGroupRecord, msg);
    },

    addSuccess: function(assgnmentGroupRecord, msg) {
        this.addToLog('success', assgnmentGroupRecord, msg);
    },


    start: function(title) {
        this.log = {
            error: [],
            warning: [],
            success: []
        };
        this.setTitle(title);
        this.down('panel').removeAll();
    },

    /**
     * @private
     */
    _addIfItems: function(log, csscls, title) {
        if(log.length > 0) {
            var container = Ext.widget('panel', {
                title: title,
                bodyPadding: 10,
                flex: 1,
                autoScroll: true,
                html: this.logTpl.apply({
                    csscls: csscls,
                    log: log,
                    isAdministrator: this.isAdministrator
                })
            });
            this.down('panel').add(container);
        }
    },

    finish: function(resultMsg, successMsg) {
        this._addIfItems(this.log.error, 'error', 'Errors');
        if(successMsg && this.log.error.length === 0) {
            this.down('panel').add({
                xtype: 'panel',
                title: successMsg.title,
                html: successMsg.html,
                bodyPadding: 10,
                flex: 1
            });
        }
        if(resultMsg) {
            this.down('panel').add({
                xtype: 'panel',
                title: resultMsg.title,
                html: resultMsg.html,
                bodyPadding: 10,
                flex: 1
            });
        }
        this._addIfItems(this.log.warning, 'warning', 'Warnings');
        this._addIfItems(this.log.success, 'info', 'Details about each successful save');
        this.show();
        this.down('panel').getComponent(0).expand();
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase', {
    extend: 'Ext.container.Container',

    config: {
        loader: undefined,
        path: undefined,
        aggregatedStore: undefined,
        labelname: undefined,
        negative_labelname: undefined,
        title: undefined,
        main: undefined
    },

    constructor: function(config) {
        this.saveButton = Ext.widget('button', {
            text: 'Save',
            iconCls: 'icon-save-32',
            scale: 'large',
            flex: 1,
            tooltip: {
                title: 'Save',
                text: Ext.String.format('Adds labels to students according to your current settings, and marks this period (semester) as ready for export to {0}.', DevilrySettings.DEVILRY_SYNCSYSTEM)
            },
            listeners: {
                scope: this,
                click: this._onSave
            }
        });
        this.previewButton = Ext.widget('button', {
            text: 'Show matching students',
            //iconCls: '',
            scale: 'large',
            flex: 1,
            tooltip: {
                title: 'Show matching students',
                text: 'Adds a filter to the table that limits visible rows to the ones matching this rule.'
            },
            listeners: {
                scope: this,
                click: this._onPreview
            }
        });

        this.defaultButtonPanel = Ext.widget('container', {
            items: [this.previewButton, this.saveButton],
            layout: {
                type: 'hbox',
                align: 'top'
            },
            height: 40
        });
        this.initConfig(config); // Must come before _loadSettings
        this._loadSettings(); // Must come before callParent, because callParent calls initComponent (which needs settings)
        this.callParent([config]);
    },

    _loadSettings: function() {
        if(this.main.settings && this.main.settings.path === this.path) {
            this.settings = this.main.settings.settings;
        }
    },

    _onSave: function() {
        if(!this.validInput()) {
            return;
        }
        Ext.MessageBox.show({
            title: 'Save?',
            msg: Ext.String.format('Are you sure you want to save? Students will be able to see if they are qualified for final exams. It will also mark <em>qualifies for exam</em> as <strong>ready for export</strong> to {0}.', DevilrySettings.DEVILRY_SYNCSYSTEM),
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            closable: false,
            scope: this,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this._onSaveYes();
                }
            }
        });
    },

    _onSaveYes: function() {
        this.loader.requireCompleteDataset(function() {
            this.main.saveSettings(this.path, this.getSettings(), function() {
                this._saveLabels();
            }, this);
        }, this);
    },

    _saveLabels: function() {
        this.loader.labelManager.setLabels({
            filter: this.filter,
            scope: this,
            label: this.labelname,
            negative_label: this.negative_labelname,
            student_can_read: true
        });
    },

    _onPreview: function() {
        if(this.validInput()) {
            this.loader.requireCompleteDataset(function() {
                this.loader.clearFilter();
                this.loader.filterBy(this.title, this.filter, this);
            }, this);
        }
    },

    validInput: function() {
        return true;
    },

    getSettings: function() {
        return false;
    }
});


Ext.define('devilry_header.model.AdminSearchResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'path', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'name',  type: 'string'},
        {name: 'students',  type: 'auto'},
        {name: 'assignment_id',  type: 'auto'},
        {name: 'type',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_search/rest/admincontent',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json',
            root: 'matches',
            totalProperty: 'total'
        }
    }
});


Ext.define('devilry.extjshelpers.DashGrid', {
    extend: 'Ext.Container',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    initComponent: function() {
        this.callParent(arguments);
        this.createStore();
        this.loadStore();
    },

    config: {
        noRecordsMessage: {}
    },

    createStore: function() {
        throw "createStore must be implemented";
    },

    loadStore: function() {
        this.store.load({
            scope: this,
            callback: function(records, operation, success) {
                if(!success || records.length === 0) {
                    var args = {};
                    if(success) {
                        Ext.apply(args, this.noRecordsMessage);
                        Ext.apply(args, {msgcls: 'info'});
                    } else {
                        args = {
                            title: 'Error',
                            msg: "Failed to load. Try re-loading the page.",
                            msgcls: 'error'
                        }
                    }
                    this.add({
                        xtype: 'box',
                        autoScroll: true,
                        flex: 1,
                        html: Ext.create('Ext.XTemplate',
                            '<div class="section {msgcls}-small extravisible-small">',
                            '   <h1>{title}</h1>',
                            '   <p>{msg}</p>',
                            '</div>'
                        ).apply(args)
                    });
                } else {
                    this.createBody();
                }
            }
        });
    },

    createBody: function() {
    }
});


Ext.define('devilry_extjsextras.ManageItemsPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.manageitemspanel',

    /**
     * @cfg {Ext.data.Store} store
     * The store where items are added/deleted by this panel. Used for the
     * grid.
     */

    /**
     * @cfg [{Object}] columns
     * Grid columns.
     */

    /**
     * @cfg {boolean} confirmBeforeRemove
     * Show confirm dialog on remove? Defaults to ``true``.
     */
    confirmBeforeRemove: true,

    /**
     * @cfg {bool} hideHeaders
     * Hide grid headers?
     */
    hideHeaders: true,


    /**
     * @cfg {boolean} includeRemove
     * Include remove and selectall buttons.
     */

    /**
     * @cfg {Function} [filterFunction]
     * Callback used by the filter field. Return ``true`` on match.
     * If this is not included, no filter field is shown.
     */


    constructor: function(config) {
        config.cls = config.cls || this.cls || '';
        config.cls += ' devilry_extjsextras_manageitemspanel';
        this.addEvents({
            /**
             * @event
             * Fired to signal that a item should be added.
             * @param {[object]} itemRecord A item record.
             * */
            "addItem" : true,

            /**
             * @event
             * Fired to signal that items should be removed.
             * @param {[object]} itemRecords Array of item records.
             * */
            "removeItems" : true

        });

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);
    },

    initComponent: function() {
        var me = this;
        this.prettyFormatItemTplCompiled = Ext.create('Ext.XTemplate', this.prettyFormatItemTpl);

        Ext.apply(this, {
            frame: false,
            border: 0,
            layout: 'fit',
            items: [{
                xtype: 'grid',
                hideHeaders: this.hideHeaders,
                multiSelect: true,
                store: this.store,
                columns: this.columns,
                listeners: {
                    scope: this,
                    selectionchange: this._onGridSelectionChange
                }
            }]
        });

        var tbar = [];
        if(this.includeRemove) {
            tbar.push({
                xtype: 'button',
                cls: 'selectAllButton',
                text: gettext('Select all'),
                listeners: {
                    scope: this,
                    click: this._onSelectAll
                }
            });
            tbar.push({
                xtype: 'button',
                text: gettext('Remove'),
                itemId: 'removeButton',
                cls: 'removeButton',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onRemoveItemsClicked
                }
            });
        }
        if(this.filterFunction) {
            tbar.push({
                xtype: 'textfield',
                cls: 'filterfield',
                emptyText: gettext('Filter ...'),
                listeners: {
                    scope: this,
                    change: this._onFilterChange
                }
            });
        }
        if(tbar.length > 0) {
            this.tbar = tbar;
        }

        this.callParent(arguments);
    },

    /** Show savemask. */
    saveMask: function() {
        this.setLoading(gettext('Saving ...'))
    },

    /** Remove the save mask */
    removeSaveMask: function() {
        this.setLoading(false);
    },


    /** Use this to tell the user that the added user is already in the list.
     * @param callbackConfig
     *      Configures the callback function to invoke after the messagebox is closed.
     *      Attributes: ``callback`` and ``scope``.
     * */
    showDuplicateItemMessage: function(callbackConfig) {
        Ext.MessageBox.show({
            title: gettext('Already in list'),
            msg: gettext('The selected item is already in the list'),
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.ERROR,
            fn: function() {
                Ext.callback(callbackConfig.callback, callbackConfig.scope);
            }
        });
    },



    /*
     * 
     * Remove
     *
     */

    _getSelectedItems: function() {
        return this.down('grid').getSelectionModel().getSelection();
    },

    _onRemoveItemsClicked: function() {
        var selectedItems = this._getSelectedItems();
        if(this.confirmBeforeRemove) {
            this._confirmRemove(selectedItems);
        } else {
            this._removeItems(selectedItems);
        }
    },

    _removeItems: function(selectedItems) {
        this.saveMask();
        this.fireEvent('removeItems', selectedItems);
    },

    _confirmRemove: function(selectedItems) {
        var confirmMessage = gettext('Do you really want to remove the {numselected} selected items from the list?');
        Ext.MessageBox.show({
            title: gettext('Confirm remove'),
            msg: Ext.create('Ext.XTemplate', confirmMessage).apply({
                numselected: selectedItems.length
            }),
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this._removeItems(selectedItems);
                }
            },
            scope: this
        });
    },


    /*
     *
     * Select
     *
     */

    _onSelectAll: function() {
        this.down('grid').getSelectionModel().selectAll();
    },

    _onGridSelectionChange: function(selectionmodel) {
        if(this.includeRemove) {
            if(selectionmodel.getSelection().length == 0) {
                this.down('#removeButton').disable();
            } else {
                this.down('#removeButton').enable();
            }
        }
    },


    /*
     *
     * Filter
     *
     */

    _onFilterChange: function(filterfield, newValue, oldValue) {
        if(newValue === '') {
            this.store.clearFilter();
        } else {
            this._filter(newValue);
        }
    },

    _filter: function(query) {
        this.store.filterBy(function(record) {
            return this.filterFunction(query, record);
        }, this);
    },



    /** Should be called when save is complete. */
    selectRecord: function(record) {
        this.down('grid').getSelectionModel().select([record]);
    },

    /** Call this after an item has been added successfully.
     * */
    afterItemAddedSuccessfully: function(record) {
        this.selectRecord(record);
        this.removeSaveMask();
    },

    /** Call this after items have been removed successfully.
     * Typically called from the ``removeItems`` event handler.
     * */
    afterItemsRemovedSuccessfully: function(removedRecords) {
        this.removeSaveMask();
    },


    clearAndfocusField: function(selector) {
        var field = this.down(selector);
        Ext.defer(function() {
            field.clearValue();
            field.focus();
        }, 200);
    },


    /*
     *
     * Static functions
     *
     */

    statics: {
        caseIgnoreContains: function(fieldvalue, query) {
            if(fieldvalue) {
                return fieldvalue.toLocaleLowerCase().indexOf(query) > -1;
            } else {
                return false;
            }
        }
    }
});


Ext.define('devilry_header.model.ExaminerSearchResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'path', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'name',  type: 'string'},
        {name: 'students',  type: 'auto'},
        {name: 'type',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_search/rest/examinercontent',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json',
            root: 'matches',
            totalProperty: 'total'
        }
    }
});


/**
 * Adds utilites for ``devilry.extjshelpers.RestProxy`` error handling.
 */
Ext.define('devilry_extjsextras.RestfulApiProxyErrorHandler', {
    extend: 'devilry_extjsextras.ProxyErrorHandler',

    /**
     * Adds the errors messages contained in the ``responseData`` added to
     * ``Ext.data.Operation`` objects by
     * ``devilry.extjshelpers.RestProxy.setException``.
     */
    addRestfulErrorsFromOperation: function(operation) {
        if(operation.responseData && operation.responseData.items) {
            var errors = operation.responseData.items;
            this.errormessages = errors.errormessages;
            this.fielderrors = this._removeGlobalFromFieldErrors(errors.fielderrors);
            return true;
        } else {
            return false;
        }
    },

    /** Copy fielderrors excluding any ``__all__`` attribute. */
    _removeGlobalFromFieldErrors: function(fielderrors) {
        var cleanedFieldErrors = {};
        Ext.Object.each(fielderrors, function(key, value) {
            if(key != '__all__') {
                cleanedFieldErrors[key] = value;
            }
        });
        return cleanedFieldErrors;
    },

    addErrors: function(operation) {
        if(!this.addRestfulErrorsFromOperation(operation)) {
            this.addErrorsFromOperation(operation);
        }
    }
});



/**
 * Panel to browse FileMeta.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel', {
    extend: 'Ext.view.View',
    alias: 'widget.filemetabrowserpanel',
    cls: 'widget-filemetabrowserpanel bootstrap',

    /**
     * @cfg {Ext.data.Store} [store]
     * FileMeta store. (Required).
     * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
     * class.
     */
    store: undefined,

    tpl: [
        '<h4>', gettext('Files'), ':</h4>',
        '<ul>',
            '<tpl for="files">',
                '<li class="filelinkitem">',
                    '<a href="{[this.getDownloadUrl(values.id)]}"><strong>{filename}</strong></a>',
                    ' <small class="muted">({[this.humanReadableSize(values.size)]})</small>',
                '</li>',
            '</tpl>',
        '</ul>',
        '<p><a class="btn" href="{downloadAllUrl}">',
            '<i class="icon-download"></i> ',
            gettext('Download all files (.zip)'),
        '</a></p>', {
            getDownloadUrl: function(id) {
                return Ext.String.format("{0}/student/show-delivery/filedownload/{1}",
                    DevilrySettings.DEVILRY_URLPATH_PREFIX, id);
            },
            humanReadableSize:function (size) {
                var units = ['Bytes', 'KBytes', 'MBytes', 'GBytes'];
                var i = 0;
                while(size >= 1024) {
                    size /= 1024;
                    ++i;
                }
                var sizeWithUnit;
                if(i < units.length) {
                    sizeWithUnit = size.toFixed() + ' ' + units[i];
                } else {
                    sizeWithUnit = size + ' ' + units[0];
                }
                return sizeWithUnit;
            }
        }
    ],

    itemSelector: 'li.filelinkitem',

    loadFilesForDelivery :function (deliveryid) {
        this.deliveryid = deliveryid;
        this.store.proxy.extraParams.filters = Ext.JSON.encode([
            {field: 'delivery', comp:'exact', value: this.deliveryid}
        ]);
        this.store.load();
    },

    collectData : function(records, startIndex){
        var files = this.callParent(arguments);
        return {
            files: files,
            downloadAllUrl: Ext.String.format("{0}/student/show-delivery/filedownload/{1}",
                DevilrySettings.DEVILRY_URLPATH_PREFIX, this.deliveryid)
        };
    }
});


/** Store with defaults tuned for Devilry and some extra utility functions. */
Ext.define('devilry.extjshelpers.Store', {
    extend: 'Ext.data.Store',

    config: {
        remoteFilter: true,
        remoteSort: true,
        autoSync: true
    },

    constructor: function(config) {
        this.callParent([config]);

        this.addEvents(
            /**
             * @event
             * Fired when loadAll() has successfully loaded all records. Same params as the load event.
             */
            'loadAll'
        );
    },

    /**
     * Load all records in the store. This is done in two requests. First we
     * ask for a single record, to get the totalCount, then we ask for all
     * records.
     *
     * @param options Same as for ``Ext.data.Store.load``.
     */
    loadAll: function(options) {
        this.pageSize = 1;
        var me = this;
        this.load({
            callback: function(records, operation, success) {
                if(success) {
                    me.pageSize = me.totalCount;
                    me.load(function(records, operation, success) {
                        me._callbackFromOptions(options, [records, operation, success]);
                        me.fireEvent('loadAll', me, records, success, operation);
                    });
                } else {
                    me._callbackFromOptions(options, [records, operation, false]);
                }
            }
        });
    },

    _callbackFromOptions: function(options, args) {
        if(Ext.typeOf(options) == 'function') {
            Ext.bind(options, this, args)();
        } else if(Ext.typeOf(options) == 'object' && options.callback) {
            Ext.bind(options.callback, options.scope, args)();
        }
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedSubject', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifiedsubject/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

/**
 * Restful submit with support for HTTP error codes and PUT, POST, DELETE and
 * GET. This is achieved in cooperation with {@link devilry.extjshelpers.RestProxy}.
 *
 * # Usage
 *
 *      myform.getForm().doAction('devilryrestsubmit', {...});
 * 
 * instead of
 *
 *      myform.getForm().submit({...});
 * 
 * Just remember require this class with:
 *
 *      requires: ['devilry.extjshelpers.RestSubmit']
 *
 * or
 *
 *      Ext.require('devilry.extjshelpers.RestSubmit');
 *
 * # See also
 * {@link devilry.extjshelpers.RestProxy}.
 * */
Ext.define('devilry.extjshelpers.RestSubmit', {
    extend: 'Ext.form.action.Submit',
    alias: 'formaction.devilryrestsubmit',

    run: function() {
        var record = this.form.getRecord();
        if(this.method == "DELETE") {
            this.deleteRequest(record);
        } else {
            this.saveRequest(record);
        }
    },

    deleteRequest: function(record) {
        if(!record) {
            throw "Can not DELETE a non-existing record.";
        }
        record = record.destroy({
            form: this.form,
            success: this.onSuccess,
            failure: this.onFailure,
            scope: this,
            timeout: (this.timeout * 1000) || (this.form.timeout * 1000),
        });
    },

    saveRequest: function(record) {
        if(record) { // Update the current record with data from form if editing existing (previously loaded with loadRecord())
            this.form.updateRecord(record);
        } else { // Create new record
            record = Ext.ModelManager.create(this.form.getValues(), this.model);
        }

        // save() automatically uses the correct REST method (post for create and put for update).
        record = record.save({
            form: this.form,
            success: this.onSuccess,
            failure: this.onFailure,
            scope: this,
            timeout: (this.timeout * 1000) || (this.form.timeout * 1000),
        });
    },


    onSuccess: function(record, operation) {
        this.record = record;
        this.operation = operation;
        this.form.afterAction(this, true);
    },

    onFailure: function(record, operation){
        this.record = record; // Always null?
        this.operation = operation;
        this.response = operation.response;
        if(operation.responseData) {
            this.form.markInvalid(operation.responseData.items.fielderrors);
        }

        if(operation.error.status === 0) {
            this.failureType = Ext.form.action.Action.CONNECT_FAILURE;
        } else if(operation.error.status >= 400 && operation.error.status < 500) {
            this.failureType = Ext.form.action.Action.SERVER_INVALID;
        } else {
            this.failureType = Ext.form.action.Action.LOAD_FAILURE;
        }
        this.form.afterAction(this, false);
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsBase', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',

    validPointInput: function() {
        var numberfield = this.down('numberfield');
        if(numberfield.getValue() === null) {
            Ext.MessageBox.alert('Points required', Ext.String.format(
                'Please specify "{0}".', numberfield.getFieldLabel())
            );
            return false;
        }
        return true;
    },

    getSettings: function() {
        var minimumScaledPoints = this.down('numberfield').getValue();
        return {
            minimumScaledPoints: minimumScaledPoints
        };
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.All', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: this.defaultButtonPanel
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        return true;
    }
});


Ext.define('devilry_authenticateduserinfo.UserInfoModel', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'username',  type: 'string'},
        {name: 'full_name',  type: 'string'},
        {name: 'email',  type: 'string'},
        {name: 'languagecode',  type: 'string'},
        {name: 'is_superuser',  type: 'bool'},
        {name: 'is_nodeadmin',  type: 'bool'},
        {name: 'is_subjectadmin',  type: 'bool'},
        {name: 'is_periodadmin',  type: 'bool'},
        {name: 'is_assignmentadmin',  type: 'bool'},
        {name: 'is_student',  type: 'bool'},
        {name: 'is_examiner',  type: 'bool'}
    ],

    proxy: {
        type: 'ajax',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_authenticateduserinfo/userinfo',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    /** Returns true is the user has any roles. */
    hasAnyRoles: function() {
        return this.get('is_superuser') || this.get('is_nodeadmin') ||
            this.get('is_subjectadmin') || this.get('is_periodadmin') || this.get('is_assignmentadmin') ||
            this.get('is_student') || this.get('is_examiner');
    },

    isAdmin:function () {
        return this.get('is_superuser') || this.get('is_nodeadmin') ||
            this.get('is_subjectadmin') || this.get('is_periodadmin') || this.get('is_assignmentadmin');
    },

    getDisplayName: function() {
        return this.get('full_name') || this.get('username');
    }
});


Ext.define('devilry.extjshelpers.searchwidget.SearchWindow', {
    extend: 'Ext.window.Window',
    closeAction: 'hide',
    plain: true,
    maximizable: false,
    maximized: true,
    modal: true,

    requires: [
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.searchwidget.MultiSearchResults'
    ],

    /**
     * @cfg {Object} [searchWidget]
     */

    /**
     * @cfg {Object} [searchResultItems]
     */

    /**
     * @cfg {string} [emptyText]
     * Empty text of the search field.
     */
    emptyText: gettext('Search for anything...'),

    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'searchfield',
                margin: 5,
                emptyText: this.emptyText
            }, {
                xtype: 'multisearchresults',
                items: this.searchResultItems,
                searchWidget: this,
                flex: 1
            }],

            listeners: {
                scope: this,
                show: this._forceFocus,
                render: this._forceFocus
            }
        });
        this.callParent(arguments);
        this.setupSearchEventListeners();
    },

    _forceFocus: function() {
        Ext.defer(function() {
            this.getSearchField().focus();
        }, 200, this);
    },

    setupSearchEventListeners: function() {
        var me = this;
        this.getSearchField().addListener('emptyInput', function() {
            me.search('');
        });
        this.getSearchField().addListener('newSearchValue', function(value) {
            //console.log(value);
            me.search(value);
        });
    },

    /**
     * @private
     */
    getSearchField: function() {
        return this.down('searchfield');
    },

    /**
     * @private
     */
    getResultContainer: function() {
        return this.down('multisearchresults');
    },

    search: function(value) {
        Ext.each(this.getResultContainer().items.items, function(searchresults, index, resultgrids) {
            var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
                searchstring: value,
                alwaysAppliedFilters: searchresults.alwaysAppliedFilters
            });
            searchresults.search(parsedSearch);
        });

        // Create a parsed search without any alwaysAppliedFilters for modifySearch() to use
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: value
        });
        this.currentParsedSearch = parsedSearch;
    },

    modifySearch: function(properties) {
        Ext.apply(this.currentParsedSearch, properties);
        this.setSearchValue(this.currentParsedSearch.toString());
    },

    setSearchValue: function(value) {
        this.getSearchField().setValue(value);
    }
});


/**
 * A box with text and a button.
 * */ 
Ext.define('devilry_extjsextras.SingleActionBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.singleactionbox',
    cls: 'devilry_singleactionbox bootstrap',

    /**
     * @cfg {String} [bodyTpl]
     * The body template.
     */
    bodyTpl: '<p>{html}</p>',

    /**
     * @cfg {Object} [bodyData=undefined]
     * Data for the ``bodyTpl``. Defaults to ``{html: bodyHtml}``.
     */

    /**
     * @cfg {string} [bodyHtml=undefined]
     */

    /**
     * @cfg {string} titleText (Required)
     */

    /**
     * @cfg {string} titleTpl (Optional)
     * Title template. Defaults to ``<strong>{text}</strong>``.
     */
    titleTpl: '<strong>{text}</strong>',

    /**
     * @cfg {string} buttonText (Required)
     */

    /**
     * @cfg {string} buttonScale (Optional)
     * Defaults to "medium".
     */
    buttonScale: 'medium',

    /**
     * @cfg {string} buttonWidth (Optional)
     * Defaults to ``130``.
     */
    buttonWidth: 130,

    /**
     * @cfg {Object} buttonListeners (Required)
     */

    /**
     * @cfg {String} [buttonUi="default"]
     * The ``ui``-attribute of the button.
     */
    buttonUi: 'default',

    initComponent: function() {
        this.addEvents({
            /**
             * @event
             * Fired when clicking the button.
             * @param {devilry_extjsextras.SingleActionBox} singleactionbox
             * */
            click: true
        });
        var bodyData = this.bodyData;
        if(Ext.isEmpty(bodyData)) {
            bodyData = {html: this.bodyHtml};
        }
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                anchor: '100%',
                xtype: 'box',
                itemId: 'singleactionbox_title',
                tpl: this.titleTpl,
                data: {
                    text: this.titleText
                }
            }, {
                anchor: '100%',
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'box',
                    itemId: 'singleactionbox_body',
                    tpl: this.bodyTpl,
                    data: bodyData,
                    padding: '0 20 0 0',
                    columnWidth: 1
                }, {
                    xtype: 'button',
                    scale: this.buttonScale,
                    text: this.buttonText,
                    ui: this.buttonUi,
                    itemId: 'singleactionbox_button',
                    width: this.buttonWidth,
                    listeners: {
                        scope: this,
                        click: this._onClick
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    setBodyHtml: function(html) {
        this.down('#singleactionbox_body').update({
            html: html
        });
    },
    setTitleText: function(text) {
        this.down('#singleactionbox_title').update({
            text: text
        });
    },
    setButtonText: function(text) {
        this.down('#singleactionbox_button').setText(text);
    },

    _onClick: function() {
        this.fireEvent('click', this);
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedSubject', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedsubject/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.NotificationManager', {
    height: 0,
    requires: [
        'devilry.extjshelpers.Notification'
    ],
    singleton: true,

    show: function(config) {
        var n = Ext.widget('notification', {
            iconCls: config.iconCls
        });
        n.setTitle(config.title);
        n.setMessage(config.message);
        n.show();
    }
});


/**
 * @class devilry_extjsextras.Spotlight
 * UX used to provide a spotlight around a specified component/element.
 *
 * Copied from Ext.ux.Spotlight
 */
Ext.define('devilry_extjsextras.Spotlight', {
    extend: 'Object',

    /**
     * @private
     * The baseCls for the spotlight elements
     */
    baseCls: 'x-spotlight',

    /**
     * @cfg animate {Boolean} True to animate the spotlight change
     * (defaults to true)
     */
    animate: true,

    /**
     * @cfg duration {Integer} The duration of the animation, in milliseconds
     * (defaults to 250)
     */
    duration: 250,

    /**
     * @cfg easing {String} The type of easing for the spotlight animatation
     * (defaults to null)
     */
    easing: null,

    /**
     * @private
     * True if the spotlight is active on the element
     */
    active: false,
    
    constructor: function(config){
        Ext.apply(this, config);
    },

    /**
     * Create all the elements for the spotlight
     */
    createElements: function() {
        var me = this,
            baseCls = me.baseCls,
            body = Ext.getBody();

        me.right = body.createChild({
            cls: baseCls
        });
        me.left = body.createChild({
            cls: baseCls
        });
        me.top = body.createChild({
            cls: baseCls
        });
        me.bottom = body.createChild({
            cls: baseCls
        });

        me.all = Ext.create('Ext.CompositeElement', [me.right, me.left, me.top, me.bottom]);
    },

    /**
     * Show the spotlight
     */
    show: function(el, callback, scope) {
        var me = this;
        
        //get the target element
        me.el = Ext.get(el);

        //create the elements if they don't already exist
        if (!me.right) {
            me.createElements();
        }

        if (!me.active) {
            //if the spotlight is not active, show it
            me.all.setDisplayed('');
            me.active = true;
            Ext.EventManager.onWindowResize(me.syncSize, me);
            me.applyBounds(me.animate, false);
        } else {
            //if the spotlight is currently active, just move it
            me.applyBounds(false, false);
        }
    },

    /**
     * Hide the spotlight
     */
    hide: function(callback, scope) {
        var me = this;
        
        Ext.EventManager.removeResizeListener(me.syncSize, me);

        me.applyBounds(me.animate, true);
    },

    /**
     * Resizes the spotlight with the window size.
     */
    syncSize: function() {
        this.applyBounds(false, false);
    },

    /**
     * Resizes the spotlight depending on the arguments
     * @param {Boolean} animate True to animate the changing of the bounds
     * @param {Boolean} reverse True to reverse the animation
     */
    applyBounds: function(animate, reverse) {
        var me = this,
            box = me.el.getBox(),
            //get the current view width and height
            viewWidth = Ext.Element.getViewWidth(true),
            viewHeight = Ext.Element.getViewHeight(true),
            i = 0,
            config = false,
            from, to, clone;
            
        //where the element should start (if animation)
        from = {
            right: {
                x: box.right,
                y: viewHeight,
                width: (viewWidth - box.right),
                height: 0
            },
            left: {
                x: 0,
                y: 0,
                width: box.x,
                height: 0
            },
            top: {
                x: viewWidth,
                y: 0,
                width: 0,
                height: box.y
            },
            bottom: {
                x: 0,
                y: (box.y + box.height),
                width: 0,
                height: (viewHeight - (box.y + box.height)) + 'px'
            }
        };

        //where the element needs to finish
        to = {
            right: {
                x: box.right,
                y: box.y,
                width: (viewWidth - box.right) + 'px',
                height: (viewHeight - box.y) + 'px'
            },
            left: {
                x: 0,
                y: 0,
                width: box.x + 'px',
                height: (box.y + box.height) + 'px'
            },
            top: {
                x: box.x,
                y: 0,
                width: (viewWidth - box.x) + 'px',
                height: box.y + 'px'
            },
            bottom: {
                x: 0,
                y: (box.y + box.height),
                width: (box.x + box.width) + 'px',
                height: (viewHeight - (box.y + box.height)) + 'px'
            }
        };

        //reverse the objects
        if (reverse) {
            clone = Ext.clone(from);
            from = to;
            to = clone;
        }

        if (animate) {
            Ext.Array.forEach(['right', 'left', 'top', 'bottom'], function(side) {
                me[side].setBox(from[side]);
                me[side].animate({
                    duration: me.duration,
                    easing: me.easing,
                    to: to[side]
                });
            },
            this);
        } else {
            Ext.Array.forEach(['right', 'left', 'top', 'bottom'], function(side) {
                me[side].setBox(Ext.apply(from[side], to[side]));
                me[side].repaint();
            },
            this);
        }
    },

    /**
     * Removes all the elements for the spotlight
     */
    destroy: function() {
        var me = this;
        
        Ext.destroy(me.right, me.left, me.top, me.bottom);
        delete me.el;
        delete me.all;
    }
});



Ext.define('devilry.statistics.AggregatedPeriodDataModel', {
    extend: 'Ext.data.Model',

    idProperty: 'userid',
    fields: [
        {name: 'userid',  type: 'int'},
        {name: 'user',  type: 'auto'},
        {name: 'relatedstudent',  type: 'auto'},
        {name: 'groups',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/aggregatedperiod/{0}',
        url: null, // Set dynamically using ``urlpatt``
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});


Ext.define('devilry.extjshelpers.models.Delivery', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "int", "name": "number"},
        {"type": "date", "name": "time_of_delivery", "dateFormat": "Y-m-d\\TH:i:s"},
        {"type": "auto", "name": "deadline"},
        {"type": "bool", "name": "successful"},
        {"type": "int", "name": "delivery_type"},
        {"type": "int", "name": "deadline"},
        {"type": "auto", "name": "alias_delivery"}
    ]
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedDelivery', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "int", 
            "name": "number"
        }, 
        {
            "type": "date", 
            "name": "time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline"
        }, 
        {
            "type": "bool", 
            "name": "successful"
        }, 
        {
            "type": "int", 
            "name": "delivery_type"
        }, 
        {
            "type": "auto", 
            "name": "alias_delivery"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode"
        }, 
        {
            "type": "int", 
            "name": "deadline__assignment_group__parentnode__delivery_types"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode"
        }, 
        {
            "type": "date", 
            "name": "deadline__assignment_group__parentnode__parentnode__start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "deadline__assignment_group__parentnode__parentnode__end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "delivered_by__identifier"
        }, 
        {
            "type": "date", 
            "name": "deadline__deadline", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifieddelivery/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment_group_users", "assignment", "period", "delivered_by", "deadline", "assignment_group", "candidates", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', {
    config: {
        assignments: [],
        min: undefined,
        max: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        if(Ext.typeOf(this.min) == 'number' && Ext.typeOf(this.max) == 'number' && this.min > this.max) {
            throw "Minimum points must be less than maximum points.";
        }
    },


    match: function(student) {
        var tot_scaled_points = 0;
        Ext.each(this.assignments, function(assignment_ids, index) {
            tot_scaled_points += this._findAssignmentWithMostScaledPoints(student, assignment_ids);
        }, this);
        //console.log(student.username, this.assignments, tot_scaled_points);
        if(this.min !== undefined && tot_scaled_points < this.min) {
            return false;
        }
        if(this.max !== undefined && tot_scaled_points > this.max) {
            return false;
        }
        return true;
    },

    _findAssignmentWithMostScaledPoints: function(student, assignment_ids) {
        var max = 0;
        Ext.each(assignment_ids, function(assignment_id, index) {
            var group = student.groupsByAssignmentId[assignment_id];
            var scaled_points = student.getScaledPoints(assignment_id);
            if(max < scaled_points) {
                max = scaled_points;
            }
        });
        return max;
    },

    toExportObject: function() {
        return {
            assignments: this.assignments,
            min: this.min,
            max: this.max
        };
    }
});


Ext.define('devilry.administrator.SimplifiedBulkActions', {
    requires: [
        'devilry.extjshelpers.RestProxy'
    ],

    config: {
        /**
         * @cfg
         * The URL path of the API without the prefix of the Devilry instance.
         * Example: "/administrator/restfulsimplifiedassignmentgroup/"
         */
        apipath: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.url = Ext.String.format('{0}{1}', DevilrySettings.DEVILRY_URLPATH_PREFIX, this.apipath);
    },


    /**
     * @private
     * Sanity check to make this easier to debug.
     * Throws an exception of the check fails, and this exception should not be
     * handled, since it is always a bug if it is thrown.
     */
    _sanityCheckData: function(data) {
        if(!Ext.typeOf(data) != 'array') {
            throw "Data must be an array";
        }
    },

    _sendRestRequest: function(data) {
        this._sanityCheckData(data);
        Ext.apply(data, {
            url: this.url
        });
        Ext.Ajax.request(args);

    },

    createMany: function(options) {
        this._sendRestRequest({
            params: Ext.JSON.encode(options.data),
            method: 'POST',
            scope: options.scope,
            callback: options.callback
        });
    },

    updateMany: function(options) {
        this._sendRestRequest({
            params: Ext.JSON.encode(options.data),
            method: 'PUT',
            scope: options.scope,
            callback: options.callback
        });
    },

    deleteMany: function(options) {
        this._sendRestRequest({
            params: Ext.JSON.encode(options.data),
            method: 'DELETE',
            scope: options.scope,
            callback: options.callback
        });
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedAssignment', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "date", 
            "name": "publishing_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "delivery_types"
        }, 
        {
            "type": "bool", 
            "name": "anonymous"
        }, 
        {
            "type": "int", 
            "name": "scale_points_percent"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "date", 
            "name": "parentnode__start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "parentnode__end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedassignment/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedDeadline', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "text"
        }, 
        {
            "type": "date", 
            "name": "deadline", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "number_of_deliveries"
        }, 
        {
            "type": "bool", 
            "name": "feedbacks_published"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__id"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__delivery_types"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__name"
        }, 
        {
            "type": "bool", 
            "name": "assignment_group__is_open"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__candidates__identifier"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifieddeadline/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "assignment_group", "assignment_group_users", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.examiner.RecentFeedbacksView', {
    extend: 'devilry.extjshelpers.DashGrid',
    alias: 'widget.examiner_recentfeedbackview',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],


    /**
     * @cfg {Object} [model]
     */

    /**
     * @cfg {int} [limit]
     */
    limit: 4,
    
    /**
     * @cfg {bool} [showStudentsCol]
     */
    showStudentsCol: true,

    /**
     * @cfg {Object} [noRecordsMessage]
     */
    noRecordsMessage: {
        title: interpolate(gettext('No recent %(feedbacks_term)s'), {
            feedbacks_term: gettext('feedbacks')
        }, true),
        msg: interpolate(gettext("You are not registered on any %(groups_term)s with recent %(feedbacks_term)s."), {
            groups_term: gettext('groups'),
            feedbacks_term: gettext('feedbacks')
        }, true)
    },


    studentsRowTpl: Ext.create('Ext.XTemplate',
        '<ul class="commaSeparatedList" style="margin: 0;">',
        '   <tpl for="delivery__deadline__assignment_group__candidates__identifier">',
        '       <li>{.}</li>',
        '   </tpl>',
        '</ul>'
    ),

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">',
            '{data.delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
            '{data.delivery__deadline__assignment_group__parentnode__parentnode__short_name}.',
            '{data.delivery__deadline__assignment_group__parentnode__short_name}',
        '</a>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery__deadline__assignment_group__parentnode__parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'delivery__deadline__assignment_group__parentnode__parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        this.store.pageSize = this.limit;
    },

    createBody: function() {
        var me = this;

        var urlCreateFunction = Ext.bind(this.urlCreateFn, this.urlCreateFnScope);
        var columns = [{
            text: 'Assignment',
            menuDisabled: true,
            flex: 30,
            dataIndex: 'id',
            renderer: function(value, meta, record) {
                return me.assignmentRowTpl.apply({
                    data: record.data,
                    url: urlCreateFunction(record)
                });
            }
        }, {
            text: 'Feedback save time',
            menuDisabled: true,
            width: 130,
            dataIndex: 'save_timestamp',
            renderer: function(value) {
                var rowTpl = Ext.create('Ext.XTemplate',
                    '{.:date}'
                );
                return rowTpl.apply(value);
            }
        }];
        if(this.showStudentsCol) {
            Ext.Array.insert(columns, 1, [{
                text: 'Students',
                menuDisabled: true,
                dataIndex: 'id',
                flex: 20,
                renderer: function(value, meta, record) {
                    return me.studentsRowTpl.apply(record.data);
                }
            }]);
        }

        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            hideHeaders: true,
            disableSelection: true,
            frameHeader: false,
            autoScroll: true,
            flex: 1,
            border: false,
            sortableColumns: false,
            cls: 'bootstrap',
            store: this.store,
            columns: columns
        });
        this.add({
            xtype: 'box',
            tpl: '<div class="section"><h3>{text}</h3></div>',
            cls: 'bootstrap',
            data: {
                text: interpolate(gettext("Recent %(feedbacks)s"), {
                    feedbacks: gettext('feedbacks')
                }, true)
            }
        });
        this.add(activeAssignmentsGrid);
    }
});


Ext.define('devilry.administrator.studentsmanager.AddDeliveriesMixin', {
    //requires: [
        //'devilry.student.FileUploadPanel'
        //'devilry.administrator.studentsmanager.LocateGroup'
    //],

    deliveryTypes: {
        TYPE_ELECTRONIC: 0,
        TYPE_NON_ELECTRONIC: 1,
        TYPE_ALIAS: 2
    },

    //onPreviouslyApproved: function() {
        //this.down('studentsmanager_studentsgrid').selModel.select(1);
        //if(this.noneSelected()) {
            //this.onNotSingleSelected();
            //return;
        //}
        //var groupRecord = this.getSelection()[0];
        //console.log(groupRecord);

        ////this.assignmentgroupPrevApprovedStore.proxy.extraParams.filters = Ext.JSON.encode([{
            ////field: 'parentnode__parentnode__parentnode',
            ////comp: 'exact',

        //Ext.widget('window', {
            //width: 800,
            //height: 700,
            //modal: true,
            //maximizable: true,
            //layout: 'fit',
            //title: 'Select previously approved group',
            //items: {
                //xtype: 'locategroup',
                //store: this.assignmentgroupPrevApprovedStore,
                //groupRecord: groupRecord
            //}
        //}).show();

        ////this.refreshStore();
    //},

    onAddNonElectronicDelivery: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }
        var groupRecord = this.getSelection()[0];
        
        var msg = Ext.create('Ext.XTemplate',
            '<p>Are you sure you want to create a dummy delivery for <em>',
            '    <tpl if="name">',
            '        {name}: ',
            '    </tpl>',
            '    <tpl for="candidates__identifier">',
            '        {.}<tpl if="xindex &lt; xcount">, </tpl>',
            '    </tpl>',
            '</em>?',
            '<tpl if="number_of_deliveries &gt; 0">',
            '   <p><strong>WARNING:</strong> One usually only creates dummy deliveries for groups with no ',
            '   deliveries, however this group has <strong>{number_of_deliveries}</strong> deliveries.</p>',
            '</tpl>'
        );
        var me = this;
        Ext.MessageBox.show({
            title: 'Confirm that you want to create dummy delivery',
            msg: msg.apply(groupRecord.data),
            animateTarget: this.deletebutton,
            buttons: Ext.Msg.YESNO,
            icon: (groupRecord.data.number_of_deliveries>0? Ext.Msg.WARNING: Ext.Msg.QUESTION),
            fn: function(btn) {
                if(btn == 'yes') {
                    me.addNonElectronicDelivery(groupRecord);
                }
            }
        });
    },

    /**
     * @private
     */
    addNonElectronicDelivery: function(groupRecord) {
        var delivery = this.createDeliveryRecord(groupRecord, this.deliveryTypes.TYPE_NON_ELECTRONIC);
        delivery.save();
        this.refreshStore();
    },


    onPreviouslyPassed: function() {
        //this.down('studentsmanager_studentsgrid').selModel.select(1);
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        this.prevPassedIntro();
    },

    /**
     * @private
     */
    prevPassedIntro: function() {
        Ext.widget('window', {
            width: 500,
            height: 400,
            layout: 'fit',
            modal: true,
            title: interpolate(gettext('Mark as delivered in a previous %(period_term)s'), {
                period_term: gettext('period')
            }, true),
            items: {
                'xtype': 'panel',
                frame: false,
                border: false,
                html:
                    '<div class="section helpsection">' +
                    '   <p>Marking a group as delivered in a previoud period/semester, does the following:</p>' +
                    '   <ul>' +
                    '       <li>Create a new <em>empty</em> delivery that is marked as imported from a previous semester. This is done automatically.</li>' +
                    '       <li>Create a feedback for the new <em>fake</em> delivery using the grade editor configured for this assignment.</li>' +
                    '   </ul>' +
                    '   <p>Click <em>next</em> to create the feedback. The feedback you select will be applied to each selected group.</p>' +
                    '</div>'
            },

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    iconCls: 'icon-next-32',
                    scale: 'large',
                    text: 'Next',
                    listeners: {
                        scope: this,
                        click: function(button) {
                            button.up('window').close();
                            this.prevPassedGiveFeedbackToSelected();
                        }
                    }
                }]
            }]
        }).show();
    },

    /**
     * @private
     */
    prevPassedGiveFeedbackToSelected: function() {
        var draftEditor = Ext.create('devilry.gradeeditors.EditManyDraftEditorWindow', {
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            buttonText: 'Next',
            buttonIcon: 'icon-next-32',
            listeners: {
                scope: this,
                createNewDraft: this.prevPassedOnPublishFeedback
            }
        });
        draftEditor.show();
    },


    /**
     * @private
     */
    prevPassedOnPublishFeedback: function(feedbackdraftModelName, draftstring) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        var msg = interpolate(gettext('Mark as delivered in a previous %(period_term)s'), {
            period_term: gettext('period')
        }, true);
        this.progressWindow.start(msg);
        this._finishedSavingGroupCount = 0;
        //this.down('studentsmanager_studentsgrid').performActionOnSelected({
            //scope: this,
            //callback: this.createPreviouslyPassedDelivery,
            //extraArgs: [feedbackdraftModelName, draftstring]
        //});

        this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
            scope: this,
            callback: function(groupRecords) {
                if(this.anyGroupHaveDeliveries(groupRecords)) {
                    Ext.MessageBox.show({
                        title: 'Selected groups that have deliveries',
                        msg: '<p>One or more of the selected groups have deliveries.</p><p>This usually means that they have made a delivery that should be corrected instead of marking the assignment as corrected in a previous period.</p><p>Click <em>yes</em> to continue, or click <em>no</em> to cancel this operation.</p>',
                        buttons: Ext.Msg.YESNO,
                        icon: Ext.Msg.WARNING,
                        scope: this,
                        fn: function(btn) {
                            if(btn == 'yes') {
                                this.createPreviouslyPassedDeliveries(groupRecords, feedbackdraftModelName, draftstring);
                            }
                        }
                    });
                } else {
                    this.createPreviouslyPassedDeliveries(groupRecords, feedbackdraftModelName, draftstring);
                }
            },
        });
    },

    /**
     * @private
     */
    createPreviouslyPassedDeliveries: function(groupRecords, feedbackdraftModelName, draftstring) {
        Ext.each(groupRecords, function(groupRecord, index) {
            this.createPreviouslyPassedDelivery(groupRecord, index, groupRecords.length, feedbackdraftModelName, draftstring);
        }, this);
    },

    /**
     * @private
     */
    anyGroupHaveDeliveries: function(groupRecords) {
        for(i=0; i<groupRecords.length; i++) {
            var groupRecord = groupRecords[i];
            if(groupRecord.data.number_of_deliveries > 0) {
                return true;
            }
        }
        return false;
    },

    /**
     * @private
     */
    createPreviouslyPassedDelivery: function(groupRecord, index, total, feedbackdraftModelName, draftstring) {
        var msg = Ext.String.format('Creating a delivery on group {0}/{1}', index, total);
        this.getEl().mask(msg);

        var delivery = this.createDeliveryRecord(groupRecord, this.deliveryTypes.TYPE_ALIAS);
        delivery.save({
            scope: this,
            failure: function() {
                this.progressWindow.addErrorFromOperation(
                    groupRecord, 'Failed to create delivery', operation
                );
            },
            success: function(record) {
                groupRecord.data.latest_delivery_id = record.data.id;
                this.giveFeedbackToSelected(groupRecord, index, total, feedbackdraftModelName, draftstring);
            }
        });
    },


    createDeliveryRecord: function(groupRecord, deliveryType) {
        var modelname = Ext.String.format('devilry.apps.{0}.simplified.SimplifiedDelivery', this.role);
        return Ext.create(modelname, {
            successful: true,
            deadline: groupRecord.data.latest_deadline_id,
            delivery_type: deliveryType
            //alias_delivery
        });
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedAssignmentGroupTag', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "tag"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedassignmentgrouptag/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.models.Deadline', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "auto", "name": "text"},
        {"type": "date", "name": "deadline", "dateFormat": "Y-m-d\\TH:i:s"},
        {"type": "auto", "name": "assignment_group"},
        {"type": "auto", "name": "number_of_deliveries"},
        {"type": "bool", "name": "feedbacks_published"}
    ]
});


Ext.define('devilry_extjsextras.form.DateField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.devilry_extjsextras_datefield',
    cls: 'devilry_extjsextras_datefield',
    format: pgettext('extjs date input format', 'Y-m-d')
});


Ext.define('devilry.statistics.ClearFilters', {
    extend: 'Ext.button.Button',
    alias: 'widget.statistics-clearfilters',
    text: 'Clear filters',
    hidden: true,
    
    config: {
        loader: undefined
    },

    filterTipTpl: Ext.create('Ext.XTemplate',
        '<ul>',
        '<tpl for="filterDescriptions">',
        '   <li>{.}</li>',
        '</tpl>',
        '</ul>'
    ),
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.filterDescriptions = [];
        this.loader.on('filterApplied', this._onFilterApplied, this);
        this.loader.on('filterCleared', this._onFilterCleared, this);
    },
    
    initComponent: function() {
        this.on('click', this._onClick, this);
        this.callParent(arguments);
    },

    _onClick: function() {
        this.fireEvent('filterClearedPressed');
        this.loader.clearFilter();
    },

    _onFilterApplied: function(loader, description) {
        Ext.Array.include(this.filterDescriptions, description);
        if(this.tooltip) {
            this.tooltip.hide();
        }
        this.tooltip = Ext.create('Ext.tip.ToolTip', {
            title: 'Active filters',
            html: this.filterTipTpl.apply(this),
            anchor: 'bottom',
            target: this.getEl().id,
            width: 415,
            closable: true,
            dismissDelay: 6000,
            autoHide: true
        });
        this.show();
        this.tooltip.show();
    },
    _onFilterCleared: function(loader) {
        if(this.tooltip) {
            this.tooltip.hide();
        }
        this.filterDescriptions = [];
        this.hide();
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedPeriod', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "date", 
            "name": "start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedperiod/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedRelatedStudentKeyValue', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "relatedstudent"
        }, 
        {
            "type": "auto", 
            "name": "relatedstudent__period"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "application"
        }, 
        {
            "type": "auto", 
            "name": "key"
        }, 
        {
            "type": "auto", 
            "name": "value"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedrelatedstudentkeyvalue/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.statistics.dataview.BaseView', {
    extend: 'Ext.container.Container',
    layout: 'fit',
    config: {
        loader: undefined
    },
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);
        this.refresh();
    }
});


Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    /**
     * @property {Object} [assignment_store]
     * Used to calculate scaled points.
     */

    hasLabel: function(label) {
        return Ext.Array.some(this.get('labels'), function(labelItem) {
            return labelItem.label === label;
        });
    },

    getLabelId: function(label) {
        var labels = this.get('labels');
        for(var index=0; index<labels.length; index++)  {
            var labelItem = labels[index];
            if(labelItem.label === label) {
                return labelItem.id;
            }
        }
        return -1;
    },

    countPassingAssignments: function(assignment_ids) {
        var passes = 0;
        Ext.Object.each(this.groupsByAssignmentId, function(assignment_id, group) {
            if(group.groupInfo && Ext.Array.contains(assignment_ids, parseInt(assignment_id, 10))) {
                var feedback = group.groupInfo.feedback;
                if(feedback !== null && feedback.is_passing_grade) {
                    passes ++;
                }
            }
        }, this);
        return passes;
    },
    passesAssignments: function(assignment_ids) {
        return this.countPassingAssignments(assignment_ids) === assignment_ids.length;
    },

    passesAllAssignments: function() {
        return passesAssignments(this.assignment_ids);
    },

    getSumScaledPoints: function(assignment_ids) {
        var sumScaledPoints = 0;
        Ext.Object.each(this.groupsByAssignmentId, function(assignment_id, group) {
            if(Ext.Array.contains(assignment_ids, parseInt(assignment_id, 10))) {
                sumScaledPoints += group.scaled_points;
            }
        }, this);
        return sumScaledPoints;
    },

    updateScaledPoints: function() {
        var assignment_ids = Ext.Object.getKeys(this.groupsByAssignmentId);
        var totalScaledPoints = 0;
        Ext.each(this.assignment_ids, function(assignment_id, index) {
            var group = this.groupsByAssignmentId[assignment_id];
            if(group.groupInfo) {
                group.scaled_points = this._calculateScaledPoints(group.groupInfo);
                this.set(assignment_id + '::scaledPoints', group.scaled_points);
                totalScaledPoints += group.scaled_points;
            }
        }, this);
        this.set('totalScaledPoints', totalScaledPoints);
        this.commit(); // NOTE: removes the red triangle from grid
    },

    hasMinimalNumberOfScaledPointsOn: function(assignment_ids, minimumScaledPoints) {
        return this.getSumScaledPoints(assignment_ids) >= minimumScaledPoints;
    },

    getScaledPoints: function(assignment_id) {
        var group = this.groupsByAssignmentId[assignment_id];
        if(group) {
            return group.scaled_points;
        } else {
            return 0;
        }
    },

    _calculateScaledPoints: function(groupInfo) {
        if(groupInfo && groupInfo.feedback) {
            var assignmentRecord = this.assignment_store.getById(groupInfo.assignment_id);
            var points = groupInfo.feedback.points;
            return assignmentRecord.get('scale_points_percent') * points / 100;
        } else {
            return 0;
        }
    }
});


/** A button-like component with ``click``-event, a special pressed css class,
 * and the ability to add an "extra" css class. */
Ext.define('devilry_header.FlatButton', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_flatbutton',
    loadingCls: 'flatbutton_loading',
    cls: 'flatbutton',
    overCls: 'flatbutton_hover',
    pressedCls: 'flatbutton_pressed',
    notPressedCls: 'flatbutton_not_pressed',
    enableToggle: false,

    tpl: [
        '<div class="textwrapper">{text}</div>'
    ],

    data: {
        text: gettext('Loading') + ' ...'
    },

    constructor: function(config) {
        var loadingCls = config.loadingCls || this.loadingCls;
        var notPressedCls = config.notPressedCls || this.notPressedCls;
        var cls = config.cls || this.cls;
        cls = Ext.String.format('{0} {1} {2}', cls, loadingCls, notPressedCls);
        if(config.enableToggle) {
            cls += ' flatbutton_toggleable';
        }
        config.cls = cls;
        this.currentCls = loadingCls;

        this.addEvents(
            'click'
        );
        if(config.enableToggle) {
            this.pressed = false;
        }
        this.callParent([config]);
    },

    initComponent: function() {
        this.on({
            scope: this,
            render: this._onRender
        });
        this.callParent(arguments);
    },

    _changeCls: function(cls) {
        this.removeCls(this.currentCls);
        this.addCls(cls);
        this.currentCls = cls;
    },

    /** Set the extra class. Replaces ``flatbutton_loading`` first time it is called. */
    addExtraClass: function(cls) {
        this._changeCls(cls);
    },

    /** Set button text */
    setText: function(text) {
        this.update({
            text: text
        });
    },

    /** Add the ``pressedCls`` to css classes. */
    setPressedCls: function() {
        this.removeCls(this.notPressedCls);
        this.addCls(this.pressedCls);
    },

    /** Remove the ``pressedCls`` from css classes. */
    setNotPressedCls: function() {
        this.removeCls(this.pressedCls);
        this.addCls(this.notPressedCls);
    },

    _onRender: function() {
        this.mon(this.getEl(), {
            scope: this,
            click: this._onClick
        });
    },

    toggle: function() {
        if(this.enableToggle) {
            this._onClick();
        } else {
            throw "Can not toggle unless enableToggle==true";
        }
    },

    _onClick: function() {
        if(this.enableToggle) {
            this.pressed = !this.pressed;
            this.fireEvent('toggle', this, this.pressed);
        } else {
            this.fireEvent('click', this);
        }
    },

    setPressed:function (pressed) {
        this.pressed = pressed;
        if(pressed) {
            this.setPressedCls();
        } else {
            this.setNotPressedCls();
        }
    },

    setPressedWithEvent:function (pressed) {
        if(pressed !== this.pressed) {
            this.setPressed(pressed);
            this.fireEvent('toggle', this, this.pressed);
        }
    }
});


Ext.define('devilry.statistics.SidebarPluginContainer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-sidebarplugincontainer',
    layout: 'accordion',

    constructor: function(config) {
        this.callParent([config]);
    },

    initComponent: function() {
        this.items = [];
        Ext.each(this.sidebarplugins, function(sidebarplugin, index) {
            var plugin = Ext.create(sidebarplugin, {
                loader: this.loader,
                aggregatedStore: this.aggregatedStore
            });
            this.items.push(plugin);
        }, this);
        this.callParent(arguments);
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliveriesgrid',
    cls: 'widget-deliveriesgrid',
    hideHeaders: true, // Hide column header
    mixins: [
        'devilry.extjshelpers.AddPagerIfNeeded'
    ],
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    rowTpl: Ext.create('Ext.XTemplate',
        '<div class="bootstrap" style="white-space:normal; line-height: 1.5em !important;">',
            '<div>',
                '<span class="delivery_number">{delivery.number}:</span> ',
                '<tpl if="assignmentgroup.parentnode__delivery_types === 1">',
                    '<span class="not_in_devilry">',
                        gettext('Non-electronic delivery'),
                    '</span>',
                '<tpl else>',
                    '<span class="time_of_delivery">{[this.formatDatetime(values.delivery.time_of_delivery)]}</span>',
                    '<tpl if="delivery.delivery_type == 0">',
                        '<div class="afterdeadline">',
                            '<tpl if="delivery.time_of_delivery &gt; deadline.deadline">',
                                 ' <span class="label label-important">',
                                    gettext('After deadline'),
                                 '</span>',
                            '</tpl>',
                        '</div>',
                    '</tpl>',
                '</tpl>',
            '</div>',
            '<tpl if="delivery.delivery_type == 2">',
                '<div><span class="label label-inverse">',
                    interpolate(gettext('From previous %(period_term)s'), {
                        period_term: gettext('period')
                    }, true),
                '</span></div>',
            '</tpl>',
            '<div class="feedback">',
                '<tpl if="feedback">',
                    '<span class="{[this.getFeedbackClass(values.feedback)]}">',
                        '{[this.getPassingLabel(values.feedback)]} ({feedback.grade})',
                    '</span>',
                '</tpl>',
                '<tpl if="hasLatestFeedback">',
                    ' <span class="label label-success">',
                        gettext('active feedback'),
                    '</span>',
                '</tpl>',
            '</div>',
        '</div>', {
            formatDatetime:function (dt) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
            },
            getFeedbackClass:function (feedback) {
                return feedback.is_passing_grade? 'text-success': 'text-warning';
            },
            getPassingLabel:function (feedback) {
                return feedback.is_passing_grade? gettext('Passed'): gettext('Failed');
            }
        }
    ),

    /**
     * @cfg {Object} [assignmentgroup_recordcontainer]
     * help
     */

    /**
     * @cfg {Object} [deadlineRecord]
     */

    /**
     * @cfg {Object} [delivery_recordcontainer]
     * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
     * The record is changed when a user selects a delivery.
     */


    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            border: false,
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, deliveryrecord) {
                    //console.log(deliveryrecord.data);
                    var staticfeedbackStore = deliveryrecord.staticfeedbacks();
                    return this.rowTpl.apply({
                        delivery: deliveryrecord.data,
                        hasLatestFeedback: deliveryrecord.hasLatestFeedback,
                        deadline: this.deadlineRecord.data,
                        assignmentgroup: this.assignmentgroup_recordcontainer.record.data,
                        feedback: staticfeedbackStore.count() > 0? staticfeedbackStore.data.items[0].data: undefined
                    });
                }
            }],
            listeners: {
                scope: this,
                select: this.onSelectDelivery
            }
        });

        this.addPagerIfNeeded();
        this.callParent(arguments);
    },

    /**
     * @private
     */
    onSelectDelivery: function(grid, deliveryRecord) {
        var allGrids = this.up('deliveriesgroupedbydeadline').query('deliveriesgrid');
        Ext.each(allGrids, function(grid, index) {
            if(grid !== this) {
                grid.getSelectionModel().deselectAll();
            }
        }, this);
        this.delivery_recordcontainer.setRecord(deliveryRecord);
    }
});


Ext.define('devilry.jsfiledownload.JsFileDownload', {
    singleton: true,
    baseurl: Ext.String.format('{0}/jsfiledownload/', DevilrySettings.DEVILRY_URLPATH_PREFIX),

    getOpenUrl: function() {
        return this.baseurl + 'open';
    },

    getSaveAsUrl: function() {
        return this.baseurl + 'saveas';
    },

    open: function(content_type, content) {
        this._post_to_url(this.getOpenUrl(), {
            content_type: content_type,
            content: content
        });
    },

    saveas: function(filename, content, content_type) {
        var args = {
            filename: filename,
            content: content
        };
        if(content_type) {
            args.content_type = content_type;
        }
        this._post_to_url(this.getSaveAsUrl(), args);
    },

    _post_to_url: function(path, params) { // See: http://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
        var form = document.createElement("form");
        form.setAttribute("method", 'post');
        form.setAttribute("style", 'display: none');
        form.setAttribute("action", path);

        for(var key in params) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
        }

        document.body.appendChild(form);
        form.submit();
    }
});


/** The examiner management methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageExaminers', {
    depends: [
        'devilry.administrator.studentsmanager.ManuallyCreateUsers',
        'devilry.extjshelpers.EvenRandomSelection'
    ],

    randomDistResultTpl: Ext.create('Ext.XTemplate',
        '<div class="section info">',
        '    <p>The selected examiners got the following number of groups:</p>',
        '    <ul>',
        '    <tpl for="result">',
        '       <li><strong>{examiner}</strong>: {groups.length}</li>',
        '    </tpl>',
        '    </ul>',
        '</div>'
    ),

    successSetExaminerTpl: Ext.create('Ext.XTemplate',
        'Examiners set successfully to: <tpl for="examiners">',
        '   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '</tpl>'
    ),

    errorSetExaminerTpl: Ext.create('Ext.XTemplate',
        'Failed to set examiners: <tpl for="examiners">',
        '   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '</tpl>. Error details: {errorDetails}'
    ),
    
    /**
     * @private
     */
    onRandomDistributeExaminers: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var win = Ext.widget('window', {
            title: 'Select examiners',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                //usernames: ['donald', 'scrooge', 'daisy', 'clarabelle'],
                usernames: [],
                helptext: '<p>The username of a single examiner on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.randomDistributeExaminersOnSelected(setlistofusersobj, usernames);
                    }
                },

                extraToolbarButtons: [{
                    xtype: 'button',
                    scale: 'large',
                    text: Ext.String.format('Import examiners registered in {0}', DevilrySettings.DEVILRY_SYNCSYSTEM),
                    listeners: {
                        scope: this,
                        click: this.onImportRelatedExaminers
                    }
                }]
            }
        });
        win.show();
    },

    /**
     * @private
     */
    randomDistributeExaminersOnSelected: function(setlistofusersobj, examiners) {
        setlistofusersobj.up('window').close();
        this.progressWindow.start('Change examiners');
        this._finishedSavingGroupCount = 0;

        var randomDistResult = [];
        Ext.each(examiners, function(examiner, index) {
            randomDistResult[examiner] = [];
        }, this);

        var randomExaminerPool = Ext.create('devilry.extjshelpers.EvenRandomSelection', {
            selection: examiners
        })

        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.randomDistributeExaminers,
            extraArgs: [randomExaminerPool, randomDistResult]
        });
    },

    /**
     * @private
     */
    getRandomDistributeResults: function(allExaminers, randomDistResult) {
        var resultArray = [];
        Ext.each(allExaminers, function(examiner, index) {
            resultArray.push({
                examiner: examiner,
                groups: randomDistResult[examiner]
            });
        }, this);
        return this.randomDistResultTpl.apply({result: resultArray});
    },


    /**
     * @private
     */
    randomDistributeExaminers: function(record, index, totalSelectedGroups, randomExaminerPool, randomDistResult) {
        var msg = Ext.String.format('Random distributing examiner to group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        var examiner = randomExaminerPool.getRandomItem();
        randomDistResult[examiner].push(editRecord);

        editRecord.data.fake_examiners = [examiner];
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(record, operation, [examiner], totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish({
                        title: 'Result of random distribution of examiners',
                        html: this.getRandomDistributeResults(randomExaminerPool.selection, randomDistResult)
                    });
                }
            }
        });
    },


    /**
     * @private
     */
    onSetExaminers: function(append) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var helptext = '<p>The username of a single examiner on each line.' +
            (append? '': '<strong> Current examiners will be replaced</strong>.') +
            '</p><p>Example:</p>';
        var win = Ext.widget('window', {
            title: (append? 'Add examiners': 'Replace examiners') + ' - select examiners',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                //usernames: ['donald', 'scrooge'],
                usernames: [],
                helptext: helptext,
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.setExaminersOnSelected(setlistofusersobj, usernames, append);
                    }
                },

                extraToolbarButtons: [{
                    xtype: 'button',
                    scale: 'large',
                    text: Ext.String.format('Import examiners registered in {0}', DevilrySettings.DEVILRY_SYNCSYSTEM),
                    listeners: {
                        scope: this,
                        click: this.onImportRelatedExaminers
                    }
                }]
            },
        });
        win.show();
    },

    onImportRelatedExaminers: function(button) {
        var setlistofusersobj = button.up('setlistofusers');
        this.loadAllRelatedExaminers({
            scope: this,
            callback: this.importRelatedExaminers,
            args: [setlistofusersobj]
        });
    },

    importRelatedExaminers: function(relatedExaminers, setlistofusersobj) {
        var usernames = [];
        Ext.each(relatedExaminers, function(relatedExaminer, index) {
            usernames.push(relatedExaminer.get('user__username'));
        }, this);
        setlistofusersobj.setValueFromArray(usernames);
    },


    /**
     * @private
     */
    onAddExaminers: function() {
        this.onSetExaminers(true);
    },

    /**
     * @private
     */
    onReplaceExaminers: function() {
        this.onSetExaminers(false);
    },

    /**
     * @private
     */
    onClearExaminers: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }

        this.progressWindow.start('Clear examiners');
        this._finishedSavingGroupCount = 0;
        Ext.MessageBox.show({
            title: 'Confirm clear examiners?',
            msg: 'Are you sure you want to clear examiners on all the selected groups?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.down('studentsmanager_studentsgrid').performActionOnSelected({
                        scope: this,
                        callback: this.setExaminers,
                        extraArgs: [[], false]
                    });
                }
            }
        });
    },


    /**
     * @private
     */
    setExaminersOnSelected: function(setlistofusersobj, usernames, append) {
        setlistofusersobj.up('window').close();
        this.progressWindow.start('Change examiners');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.setExaminers,
            extraArgs: [usernames, append]
        });
    },


    /**
     * @private
     */
    setExaminers: function(record, index, totalSelectedGroups, usernames, append) {
        var msg = Ext.String.format('Setting examiners on group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        if(append) {
            usernames = Ext.Array.merge(usernames, record.data.examiners__user__username);
        };

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.fake_examiners = usernames;
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(record, operation, usernames, totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish();
                }
            }
        });
    },

    /**
     * @private
     */
    setExaminerRecordCallback: function(record, operation, usernames, totalSelectedGroups) {
        if(operation.success) {
            var msg = this.successSetExaminerTpl.apply({
                examiners: usernames
            });
            this.progressWindow.addSuccess(record, msg);
        } else {
            var msg = this.errorSetExaminerTpl.apply({
                examiners: usernames,
                errorDetails: devilry.extjshelpers.RestProxy.formatHtmlErrorMessage(operation)
            });
            this.progressWindow.addError(record, msg);
        }

        this._finishedSavingGroupCount ++;
        if(this._finishedSavingGroupCount == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },


    onImportExaminersFromAnotherAssignmentInCurrentPeriod: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        Ext.widget('window', {
            text: interpolate(gettext('Import %(examiners_term)s from another %(assignment_term)s in the current %(period_term)s'), {
                examiners_term: gettext('examiners'),
                assignment_term: gettext('assignment'),
                period_term: gettext('period')
            }, true),
            layout: 'fit',
            width: 830,
            height: 600,
            modal: true,
            items: {
                xtype: 'importgroupsfromanotherassignment',
                periodid: this.periodid,
                help: '<div class="section helpsection">Select the assignment you wish to import examiners from. When you click next, every selected assignemnt group in the current assignment with <strong>exactly</strong> the same members as in the selected assignment, will have their examiners copied into the current assignment.</div>',
                listeners: {
                    scope: this,
                    next: this.importExaminersFromAnotherAssignmentInCurrentPeriod
                }
            }
        }).show();
    },

    /**
     * @private
     */
    importExaminersFromAnotherAssignmentInCurrentPeriod: function(importPanel, otherGroupRecords) {
        importPanel.up('window').close();
        this.progressWindow.start('Copy examiners from another assignment');
        this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
            scope: this,
            callback: function(currentGroupRecords) {
                var matchingRecordPairs = this.findGroupsWithSameStudents(currentGroupRecords, otherGroupRecords);
                this.copyExaminersFromOtherGroups(matchingRecordPairs);
            }
        });
    },

    findGroupsWithSameStudents: function(currentGroupRecords, otherGroupRecords) {
        var matchingRecordPairs = [];
        Ext.each(currentGroupRecords, function(currentRecord, index) {
            var currentUsernames = currentRecord.data.candidates__student__username;
            var matchFound = false;
            this.getEl().mask(Ext.String.format('Finding groups with the same students {0}/{1}...', index, currentGroupRecords.length));
            Ext.each(otherGroupRecords, function(otherRecord, index) {
                var otherUsernames = otherRecord.data.candidates__student__username;
                if(currentUsernames.length === otherUsernames.length) {
                    var difference = Ext.Array.difference(currentUsernames, otherUsernames);
                    if(difference.length === 0) {
                        //console.log(otherUsernames, '===', currentUsernames);
                        matchingRecordPairs.push({
                            current: currentRecord,
                            other: otherRecord
                        });
                        matchFound = true;
                        return false; // break
                    }
                }
            }, this);
            if(!matchFound) {
                this.progressWindow.addWarning(currentRecord, 'Group not found in the other assignment.');
            }
        }, this);
        return matchingRecordPairs;
    },


    copyExaminersFromOtherGroups: function(matchingRecordPairs) {
        this._finishedSavingGroupCount = 0;
        Ext.each(matchingRecordPairs, function(recordPair, index) {
            this.setExaminers(recordPair.current, index, matchingRecordPairs.length, recordPair.other.data.examiners__user__username, false);
        }, this);
    },


    onSetExaminersFromTags: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        this.loadAllRelatedExaminers({
            scope: this,
            callback: this.setExaminersFromTags
        });
    },

    setExaminersFromTags: function(relatedExaminers) {
        this.progressWindow.start('Match tagged examiners to equally tagged groups');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.setExaminersFromTagsOnSingleGroup,
            extraArgs: [relatedExaminers]
        });
    },

    setExaminersFromTagsOnSingleGroup: function(groupRecord, index, totalSelectedGroups, relatedExaminers) {
        var msg = Ext.String.format('Setting examiners on group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(groupRecord);
        var matchedExaminerUsernames = this.examinersMatchesGroupTags(groupRecord, relatedExaminers);

        editRecord.data.fake_examiners = matchedExaminerUsernames;
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(groupRecord, operation, matchedExaminerUsernames, totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish();
                }
            }
        });
    },

    examinersMatchesGroupTags: function(groupRecord, relatedExaminers) {
        var matchedExaminerUsernames = [];
        Ext.each(relatedExaminers, function(relatedExaminer, index) {
            var tagsString = relatedExaminer.get('tags');
            if(tagsString) {
                var tags = tagsString.split(',');
                //console.log(relatedExaminer.get('user__username'), tags);
                var intersect = Ext.Array.intersect(groupRecord.data.tags__tag, tags);
                if(intersect.length > 0) {
                    Ext.Array.include(matchedExaminerUsernames, relatedExaminer.get('user__username'));
                }
            }
        });
        return matchedExaminerUsernames;
    }
});


Ext.define('devilry_header.store.ExaminerSearchResults', {
    extend: 'devilry_header.store.BaseSearchResults',
    model: 'devilry_header.model.ExaminerSearchResult'
});

Ext.define('devilry.extjshelpers.studentsmanager.ImportGroupsFromAnotherAssignment', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.importgroupsfromanotherassignment',

    config: {
        help: undefined,
        periodid: undefined
    },
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var assignmentModel = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignment');
        this.assignmentStore = Ext.create('Ext.data.Store', {
            model: assignmentModel,
            proxy: Ext.create('devilry.extjshelpers.RestProxy', {
                url: assignmentModel.proxy.url
            })
        });
        this.assignmentStore.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.periodid
        }]);

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'form',
                padding: 20,
                border: false,
                flex: 6,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                fieldDefaults: {
                    labelAlign: 'top',
                    labelWidth: 100,
                    labelStyle: 'font-weight:bold'
                },
                defaults: {
                    margin: '0 0 10 0'
                },
                items: [{
                    xtype: 'combo',
                    store: this.assignmentStore,
                    name: "assignment",
                    fieldLabel: "Choose an assignment",
                    emptyText: 'Choose an assignment...',
                    displayField: 'long_name',
                    valueField: 'id',
                    forceSelection: true,
                    editable: false,
                    listeners: {
                        scope: this,
                        select: function() {
                            this.down('button').enable();
                        }
                    }
                }]
            }, {
                xtype: 'box',
                flex: 4,
                html: this.help
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',

                items: ['->', {
                    xtype: 'button',
                    text: 'Next',
                    scale: 'large',
                    iconCls: 'icon-next-32',
                    disabled: true,
                    listeners: {
                        scope: this,
                        click: this.onNext
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    onNext: function() {
        var assignmentid = this.down('form').getForm().getValues().assignment;
        this.getEl().mask('Loading assignment groups...');
        devilry.administrator.studentsmanager.StudentsManager.getAllGroupsInAssignment(assignmentid, {
            scope: this,
            callback: function(records, op, success) {
                if(success) {
                    this.getEl().unmask();
                    this.fireEvent('next', this, records);
                } else {
                    this.loadAssignmentGroupStoreFailed();
                }
            }
        });
    },

    loadAssignmentGroupStoreFailed: function() {
        this.getEl().unmask();
        Ext.MessageBox.alert('Failed to load assignment groups. Please try again.');
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig', {
            extend: 'Ext.tip.ToolTip',
            trackMouse: true,
        });

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedNode', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "auto", 
            "name": "admins__username"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiednode/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["admins"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry_extjsextras.AutoSizedWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.devilry_extjsextras_autosizedwindow',
    windowPadding: 20,

    initComponent: function() {
        this._preferredWidth = this.width;
        this._preferredHeight = this.height;
        this._setupAutosizing();
        this.maximizable = false;
        this.callParent(arguments);
    },

    _setupAutosizing: function() {
        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShowWindow, this);
    },
    _onShowWindow: function() {
        this.setSizeAndPosition();
    },
    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this.setSizeAndPosition();
        }
    },
    setSizeAndPosition: function() {
        if(this.isFloating()) {
            var padding = this.windowPadding;
            var bodysize = Ext.getBody().getViewSize();
            var bodyWidth = bodysize.width - padding;
            var bodyHeight = bodysize.height - padding;
            var height = bodyHeight;
            var width = bodyWidth;
            if(this._preferredHeight) {
                height = bodyHeight < this._preferredHeight? bodyHeight: this._preferredHeight;
            }
            if(this._preferredWidth) {
                width = bodyWidth < this._preferredWidth? bodyWidth: this._preferredWidth;
            }
            this.setSize({
                width: width,
                height: height
            });
            this.center();
        }
    },

    getPreferredHeight: function() {
        return this._preferredHeight;
    },
    getPreferredWidth: function() {
        return this._preferredWidth;
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter', {
    config: {
        pointspecArgs: undefined,
        must_pass: []
    },

    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec'
    ],

    strTpl: Ext.create('Ext.XTemplate',
        '<div style="white-space: normal">',
            '<tpl if="must_pass.length &gt; 0">',
                '<p>Must pass: ',
                    '<tpl for="must_pass">',
                        '(<tpl for=".">',
                            '{data.short_name}',
                            '<tpl if="xindex &lt; xcount"> OR </tpl>',
                        '</tpl>)',
                        '<tpl if="xindex &lt; xcount"> AND </tpl>',
                    '</tpl>',
                '</p>',
            '</tpl>',
            '<tpl if="pointassignments.length &gt; 0">',
                '<p>Must have between ',
                    '<tpl if="!min">0</tpl><tpl if="min">{min}</tpl>',
                    ' and ',
                    '<tpl if="!max">&#8734;</tpl><tpl if="max">{max}</tpl>',
                    ' points in total (including both ends) on ',
                    '<tpl for="pointassignments">',
                        '(',
                        '<tpl if="length &gt; 1">best of: </tpl>',
                        '<tpl for=".">',
                            '{data.short_name}',
                            '<tpl if="xindex &lt; xcount">, </tpl>',
                        '</tpl>)',
                        '<tpl if="xindex &lt; xcount"> AND </tpl>',
                    '</tpl>',
                '</p>',
            '</tpl>',
        '</div>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.pointspec = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', this.pointspecArgs);
    },

    toReadableSummary: function(assignment_store) {
        var data = {
            must_pass: this._assignmentIdListToAssignmentRecords(assignment_store, this.must_pass),
            min: this.pointspec.min,
            max: this.pointspec.max,
            pointassignments: this._assignmentIdListToAssignmentRecords(assignment_store, this.pointspec.assignments)
        };
        return this.strTpl.apply(data);
    },

    _assignmentIdListToAssignmentRecords: function(assignment_store, arrayOfArrayOfassignmentIds) {
        var arrayOfArrayOfAssignmentRecords = [];
        Ext.each(arrayOfArrayOfassignmentIds, function(assignmentIds, index) {
            var assignmentRecords = [];
            Ext.each(assignmentIds, function(assignmentId, index) {
                var assignmentRecordIndex = assignment_store.findExact('id', assignmentId);
                var assignmentRecord = assignment_store.getAt(assignmentRecordIndex);
                assignmentRecords.push(assignmentRecord);
            });
            arrayOfArrayOfAssignmentRecords.push(assignmentRecords);
        });
        return arrayOfArrayOfAssignmentRecords;
    },

    match: function(studentRecord) {
        return this._matchIsPassingGrade(studentRecord) && this._matchPointspec(studentRecord);
    },

    _matchIsPassingGrade: function(studentRecord) {
        if(this.must_pass.length === 0) {
            return true;
        }
        var matches = true;
        Ext.each(this.must_pass, function(assignment_ids, index) {
            var one_of_them_is_passing = studentRecord.countPassingAssignments(assignment_ids) > 0;
            if(!one_of_them_is_passing) {
                matches = false;
                return false; // Break
            }
        }, this);
        return matches;
    },

    _matchPointspec: function(studentRecord) {
        if(!this.pointspec) {
            return true;
        }
        return this.pointspec.match(studentRecord);
    },

    toExportObject: function() {
        return {
            must_pass: this.must_pass,
            pointspecArgs: this.pointspec.toExportObject()
        };
    }
});


Ext.define('devilry.extjshelpers.formfields.DateTimeField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.devilrydatetimefield',
    format: 'Y-m-d H:i:s',
    submitFormat: 'Y-m-d\\TH:i:s',
    emptyText: 'YYYY-MM-DD hh:mm:ss'
});


Ext.define('devilry.extjshelpers.assignmentgroup.DeadlineExpiredNoDeliveriesBox', {
    extend: 'Ext.Component',
    alias: 'widget.deadlineExpiredNoDeliveriesBox',
    cls: 'widget-deadlineExpiredNoDeliveriesBox bootstrap',

    html: [
        '<div class="alert">',
            '<h3>',
                gettext('Deadline expired - no deliveries'),
            '</h3>',
            '<p>',
                gettext('The active deadline of this group has expired, and they have not made any deliveries. What would you like to do?'),
            '</p>',
            '<p>',
                '<a class="btn btn-primary btn-large createnewdeadline">',
                    '<i class="icon-time icon-white"></i> ',
                    gettext('Add a new deadline'),
                '</a> ',
                '<a class="btn btn-large closegroup">',
                    '<i class="icon-folder-close"></i> ',
                    gettext('Close the group'),
                '</a>',
            '</p>',
            '<p><small>',
                gettext('Closing the group fails the student on this assignment. You can re-open the group at any time.'),
            '</small></p>',
        '</div>'
    ].join(''),


    initComponent:function () {
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.closegroup',
            click: this._onCloseGroup
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.createnewdeadline',
            click: this._onAddDeadline
        });
        this.callParent(arguments);
    },

    _onCloseGroup:function () {
        this.fireEvent('closeGroup');
    },

    _onAddDeadline:function () {
        this.fireEvent('addDeadline');
    }
});

Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: this.defaultButtonPanel
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        return student.passesAssignments(this.loader.assignment_ids);
    }
});


/** A button that has a load mask while a SingleRecordContainer loads. */
Ext.define('devilry.extjshelpers.SingleRecordContainerDepButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.singlerecordcontainerdepbutton',

    config: {
        singlerecordcontainer: undefined
    },

    listeners: {
        afterrender: function(button) {
            if(!this.singlerecordcontainer.record) {
                this.singlerecordcontainer.on('setRecord', function() {
                    button.getEl().unmask();
                });
                button.getEl().mask('Loading');
            }
        }
    }
});


/**
 * View panel bound to a {@link devilry.extjshelpers.SingleRecordContainer}.
 * Kind of like ``Ext.view.View`` only for a single record.
 */
Ext.define('devilry.extjshelpers.SingleRecordView', {
    extend: 'Ext.Component',
    alias: 'widget.singlerecordview',

    config: {
        /**
        * @cfg
        * A {@link devilry.extjshelpers.SingleRecordContainer} which contains data for the ``tpl``.
        */
        singlerecordontainer: undefined,

        /**
         * @cfg
         * An ``Ext.XTemplate`` which takes the record in ``singlerecordontainer.record.data`` as input.
         */
        tpl: undefined,

        /**
         * @cfg
         * Extra data for the ``tpl``. Applied before the data in
         * ``singlerecordontainer``, so any shared attributed with
         * ``singlerecordontainer.data`` will use the attribute in
         * ``singlerecordontainer.data``.
         */
        extradata: {}
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.callParent(arguments);
        if(this.singlerecordontainer.record) {
            this.updateBody();
        }
        this.singlerecordontainer.addListener('setRecord', this.onSetRecord, this);
    },

    /**
     * @private
     */
    onSetRecord: function(singlerecordontainer) {
        this.updateBody();
    },

    getData: function(data) {
        return data;
    },

    /**
     * @private
     */
    updateBody: function() {
        var data = {};
        Ext.apply(data, this.extradata);
        Ext.apply(data, this.singlerecordontainer.record.data);
        data = this.getData(data);
        this.update(this.tpl.apply(data));
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.None', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: [this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        return false;
    }
});


Ext.define('devilry.extjshelpers.studentsmanager.FilterSelector', {
    extend: 'Ext.panel.Panel',
    frame: false,
    border: false,
    alias: 'widget.studentsmanager_filterselector',
    html: 'Will be able to select filters here'
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "gradeeditorid"
        }, 
        {
            "type": "auto", 
            "name": "assignment"
        }, 
        {
            "type": "auto", 
            "name": "config"
        }
    ],
    idProperty: 'assignment',
    proxy: {
        type: 'devilryrestproxy',
        url: '/gradeeditors/administrator/restfulsimplifiedconfig/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

/** Pager which can be used with any store. */
Ext.define('devilry.extjshelpers.Pager', {
    extend: 'Ext.toolbar.Toolbar',
    alias: 'widget.devilrypager',
    cls: 'widget-devilrypager',
    style: {
        border: 'none'
    },

    layout: {
        type: 'hbox',
        align: 'middle'
    },

    config: {
        /**
         * @cfg
         * An ``Ext.data.Store``.
         */
        store: undefined,

        /**
         * @cfg
         * The ``Ext.XTemplate for the label between the next and previous buttons.
         */
        middleLabelTpl: Ext.create('Ext.XTemplate', '{from}-{to} of {total}'),

        /**
         * @cfg
         * Width of the entire container. Note that the label is stretched
         * while the buttons keep their width.
         */
        width: 150,

        /**
         * @cfg
         * Width of the container.
         */
        height: 30,

        /**
         * @cfg
         * Reverse direction? If this is ``true``, the next button goes backwards, and the previous button goes forward.
         */
        reverseDirection: false
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var me = this;

        this.previousButton = Ext.ComponentManager.create({
            xtype: 'button',
            text: '<',
            flex: 0,
            disabled: true,
            listeners: {
                click: function() {
                    me.store.previousPage();
                }
            },
        });

        this.middleLabel = Ext.ComponentManager.create({
            xtype: 'component',
            html: '',
            style: {
                'text-align': 'center'
            },
            flex: 1,
            //width: 200
        });

        this.nextButton = Ext.ComponentManager.create({
            xtype: 'button',
            text: '>',
            flex: 0,
            disabled: true,
            listeners: {
                click: function() {
                    me.store.nextPage();
                }
            }
        });

        this.items = [
            this.previousButton,
            this.middleLabel,
            this.nextButton
        ];
        if(this.reverseDirection) {
            this.nextButton.setText('<');
            this.previousButton.setText('>');
            this.items[2] = this.previousButton;
            this.items[0] = this.nextButton;
        }
        this.callParent(arguments);

        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.updatePageSwitcher(records);
            }
        });
    },

    updatePageSwitcher: function(records) {
        if(records.length == 0) {
            this.hide();
            return;
        } else {
            this.show();
        }
        var from = this.store.pageSize * (this.store.currentPage-1);
        var visibleOnCurrentPage = this.store.getCount();
        var totalPages = this.store.getTotalCount() / this.store.pageSize;

        var label = this.middleLabelTpl.apply({
            total: this.store.getTotalCount(),
            from: from + 1,
            to: from + visibleOnCurrentPage,
            //records: records, // Enable if we need it anywhere
            firstRecord: records.length == 0? undefined: records[0],
            currentPage: this.store.currentPage,
            currentNegativePageOffset: totalPages - this.store.currentPage + 1
        });
        this.middleLabel.update(label);

        this.previousButton.disable();
        if(from > 0) {
            this.previousButton.enable();
        }
        this.nextButton.disable();
        if(visibleOnCurrentPage == this.store.pageSize && (from+visibleOnCurrentPage) != this.store.getTotalCount()) {
            this.nextButton.enable();
        }
    }
});


Ext.define('devilry_extjsextras.OkCancelPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.okcancelpanel',
    cls: 'devilry_extjsextras_okcancelpanel bootstrap',

    /**
     * @cfg {String} [oktext]
     * The text of the OK button. Defauls to "Ok" translated.
     */
    oktext: pgettext('uibutton', 'Ok'),

    /**
     * @cfg {String} [canceltext]
     * The text of the Cancel button. Defauls to "Cancel" translated.
     */
    canceltext: gettext('Cancel'),

    /**
     * @cfg {String} [okbutton_ui="primary"]
     * The ``ui``-config for the OK-button.
     */
    okbutton_ui: 'primary',

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            /** @event
             * Fired when the OK-button is clicked.
             * @param panel This panel.
             */
            'ok',

            /** @event
             * Fired when the Cancel-button is clicked.
             * @param panel This panel.
             */
            'cancel'
        );
    },

    
    initComponent: function() {
        Ext.apply(this, {
            fbar: [{
                xtype: 'button',
                itemId: 'cancelbutton',
                cls: 'cancelbutton',
                text: this.canceltext,
                listeners: {
                    scope: this,
                    click: this._onCancelButtonClick
                }
            }, {
                xtype: 'button',
                itemId: 'okbutton',
                ui: this.okbutton_ui,
                scale: 'large',
                cls: 'okbutton',
                text: this.oktext,
                listeners: {
                    scope: this,
                    click: this._onOkButtonClick
                }
            }]
        });
        this.callParent(arguments);
    },

    _onCancelButtonClick: function() {
        this.fireEvent('cancel', this);
    },

    _onOkButtonClick: function() {
        this.fireEvent('ok', this);
    }
});


Ext.define('devilry_extjsextras.form.TimeFieldPicker', {
    extend: 'Ext.picker.Time',
    alias: 'widget.devilry_extjsextras_timefieldpicker',
    cls: 'devilry_extjsextras_timefieldpicker',

    requires: [
        'Ext.Date',
        'Ext.util.MixedCollection'
    ],

    /**
     * @cfg {String[]} [specialTimes]
     * Array of times that appears emphasized at the top of the list.
     * The format is ``hh:mm``.
     */
    specialTimes: [
        '12:00',
        '13:00',
        '14:00',
        '15:00',
        '16:00',
        '23:59'
    ],

    initComponent: function() {
        var me = this;
        this.tpl = Ext.create('Ext.XTemplate',
            '<ul><tpl for=".">',
                '<li role="option" class="' + this.itemCls + '">',
                    '<tpl if="isSpecial">',
                        '<tpl if="isLastSpecial">',
                            '<div style="margin-bottom: 6px;">',
                                '<strong>{disp}</strong>',
                            '<div>',
                        '<tpl else>',
                            '<strong>{disp}</strong>',
                        '</tpl>',
                    '<tpl else>',
                        '{disp}',
                    '</tpl>',
                '</li>',
            '</tpl></ul>'
        );
        this.callParent(arguments);
    },

    _createSpecialTimesMap: function() {
        var specialTimesMap = new Ext.util.MixedCollection();
        return specialTimesMap;
    },

    _addSpecialTimes: function(timesArray) {
        Ext.Array.each(this.specialTimes, function(timestring, index) {
            var dateobj = this._parseTimeStringToDateObj(timestring);
            var formatted = Ext.Date.format(dateobj, this.format);
            timesArray.push({
                disp: formatted,
                date: dateobj,
                isSpecial: true,
                isLastSpecial: (index == this.specialTimes.length-1)
            });
        }, this);
    },

    _addAutoIncrementedTimes: function(timesArray) {
        var min = this.absMin;
        var max = this.absMax;
        while(min <= max){
            timesArray.push({
                disp: Ext.Date.dateFormat(min, this.format),
                date: min
            });
            min = Ext.Date.add(min, 'mi', this.increment);
        }
    },

    createStore: function() {
        var me = this;
        var timesArray = [];
        this._addSpecialTimes(timesArray);
        this._addAutoIncrementedTimes(timesArray);
        return new Ext.data.Store({
            fields: [
                {name: 'disp', type: 'string'},
                {name: 'date', type: 'date'},
                {name: 'isSpecial', type: 'bool', defaultValue: false},
                {name: 'isLastSpecial', type: 'bool', defaultValue: false}
            ],
            data: timesArray
        });
    },

    /* Get a time-string (like in ``specialTimes``), and return the number of minutes from 00:00. */
    _parseTimeStringToDateObj: function(timestring) {
        var dateobj = Ext.Date.parse(timestring, 'H:i', true);
        return this._getTimeByMinuteOffset(dateobj.getHours() * 60 + dateobj.getMinutes());
    },

    _getTimeByMinuteOffset: function(minutes) {
        return Ext.Date.add(this.absMin, Ext.Date.MINUTE, minutes);
    }
});


/** Base class for windows used to Edit/Create RestfulSimplified models. */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
    extend: 'devilry.extjshelpers.AutoSizedWindow',
    //width: 800,
    //height: 600,
    layout: 'fit',
    modal: true,

    /**
     * @cfg
     * The {@link devilry.extjshelpers.RestfulSimplifiedEditPanel} to use for editing.
     */
    editpanel: undefined,
    
    initComponent: function() {
        var me = this;

        var form = this.editpanel.down('form');
        if(!this.width && form.suggested_windowsize) {
            this.width = form.suggested_windowsize.width,
            this.height = form.suggested_windowsize.height
        }
        this.maximizable = false; // Mazimize does not work with autosizing.

        this.editpanel.addListener('saveSucess', function(record) {
            me.onSaveSuccess(record);
        });

        Ext.apply(this, {
            items: this.editpanel
        });
        this.callParent(arguments);
    },

    onSaveSuccess: function(record) {
        throw "Must implement onSaveSuccess()"
    }
});


/** A panel containing multiple search results under a common title and store.
 *
 *      ------------------------
 *      | title                |
 *      ------------------------
 *      | result 1             |
 *      | result 2             |
 *      | result 3             |
 *      -----------------------|
 *
 * @xtype searchresults
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.searchresults',
    requires: [
        'devilry.extjshelpers.searchwidget.SearchResultItem',
        'devilry.extjshelpers.Pager'
    ],
    cls: 'searchresults',
    hidden: true,
    config: {
        /**
         * @cfg
         * Editor url prefix (__Required__). The editor url for a specific
         * item is ``editorurlprefix+id``. Note that this means that editorurlprefix _must_
         * end with ``/``. _Required_.
         */
        editorurlprefix: undefined,

        /**
         * @cfg
         * Title of these search results. _Required_.
         */
        title: undefined,

        /**
         * @cfg
         * The ``Ext.data.store`` where the results are loaded from. _Required_.
         */
        store: undefined,

        /**
         * @cfg
         * Formatting template for the text rendered for each result item. _Required_.
         */
        rowformattpl: undefined,

        filterconfig: undefined,

        itemtpldata: {
            is_student: undefined
        }
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
        var filterconfig = {
            type: undefined,
            shortcuts: new Object()
        };
        if(this.filterconfig) {
            Ext.apply(filterconfig, this.filterconfig);
        }
        this.filterconfig = filterconfig;
        return this;
    },

    initComponent: function() {
        var me = this;

        this.showmorebutton = Ext.create('Ext.button.Button', {
            text: 'Show more',
            listeners: {
                click: function() {
                    me.getSearchWidget().modifySearch({
                        type: me.filterconfig.type
                    });
                }
            }
        });

        Ext.apply(this, {
            frame: false,
            hideHeaders: true,
            minButtonWidth: 0,

            tbar: [this.showmorebutton, {
                xtype: 'box',
                flex: 1
            }, {
                xtype: 'devilrypager',
                store: this.store,
                width: 140
            }]
        });
        this.callParent(arguments);

        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.handleStoreLoadSuccess(records);
            } else {
                me.handleStoreLoadFailure();
            }
        });
    },

    getSearchWidget: function() {
        return this.up('multisearchresults').getSearchWidget();
    },

    handleStoreLoadFailure: function() {
        //console.log('Failed to load store'); // TODO Better error handling
    },

    handleStoreLoadSuccess: function(records) {
        this.removeAll();
        var me = this;
        Ext.each(records, function(record, index) {
            me.addRecord(record, index);
        });
    },

    addRecord: function(record, index) {
        var searchresultitem = Ext.clone(this.resultitemConfig);
        var data = {};
        Ext.apply(data, record.data);
        Ext.apply(data, this.itemtpldata);
        Ext.apply(searchresultitem, {
            xtype: 'searchresultitem',
            recorddata: data,
            recordindex: index,
            itemtpldata: this.itemtpldata
        });
        this.add(searchresultitem);
    },


    search: function(parsedSearch) {
        if(parsedSearch.type && parsedSearch.type != this.filterconfig.type) {
            this.hide();
            return;
        }
        this.store.proxy.extraParams = parsedSearch.applyToExtraParams(this.store.proxy.extraParams, this.filterconfig.shortcuts);
        parsedSearch.applyPageSizeToStore(this.store);
        if(parsedSearch.type) {
            this.enableStandaloneMode();
        } else {
            this.enableSharingMode();
        }
        this.loadStore();
    },

    loadStore: function() {
        var me = this;
        this.store.load(function(records, operation, success) {
            if(success) {
                if(me.store.data.items.length == 0) {
                    me.hide();
                } else {
                    me.show();
                }
            } else {
                me.hide();
            }
        });
    },

    /**
     * @private
     *
     * Used when this SearchResults is the only one beeing displayed.
     */
    enableStandaloneMode: function() {
        this.showmorebutton.hide();
    },

    /**
     * @private
     *
     * Used when this SearchResults is beeing displayed in a box with many other SearchResults.
     */
    enableSharingMode: function() {
        this.showmorebutton.show();
    }
});


Ext.define('devilry.asminimalaspossible_gradeeditor.DummyWindow', {
    extend: 'Ext.window.Window',

    width: 200,
    height: 200,
    modal: true,
    layout: 'fit',

    config: {
        /**
         * @cfg
         * A message to show. (required)
         */
        message: undefined,

        /**
         * @cfg
         * Label of the toolbar button. (required)
         */
        buttonLabel: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);

        this.addEvents(
            /**
             * @param stuff A message.
             */
            "gotSomeValue"
        );
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'panel',
                html: this.message
            }],
            
            bbar: [{
                xtype: 'button',
                text: this.buttonLabel,
                listeners: {
                    scope: this,
                    click: this.onClickButton
                }
            }]
        });
        this.callParent(arguments);
    },

    onClickButton: function() {
        this.fireEvent('gotSomeValue', 'Hello world!');
    }
});


Ext.define('devilry.examiner.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.examiner.models.Deadline',
    hasMany: {
        model: 'devilry.examiner.models.StaticFeedback',
        name: 'staticfeedbacks',
        foreignKey: 'delivery'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/examiner/restfulsimplifieddelivery/'
    })
});


Ext.define('devilry_extjsextras.form.Help', {
    extend: 'Ext.Component',
    alias: 'widget.formhelp',
    cls: 'formhelp bootstrap'
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedPeriod', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "date", 
            "name": "start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "admins__username"
        }, 
        {
            "type": "auto", 
            "name": "admins__email"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedperiod/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["admins", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain', {
    extend: 'Ext.data.Store',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter'
    ],

    config: {
        filterArgsArray: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.fields = ['filter'];
        this.callParent(arguments);
        if(this.filterArgsArray) {
            Ext.each(this.filterArgsArray, function(filterArgs, index) {
                this.addFilter(filterArgs);
            }, this);
        }
    },

    addFilter: function(filterConf) {
        this.add({
            filter: this.createFilter(filterConf)
        });
    },

    createFilter: function(filterConf) {
        return Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter', filterConf);
    },

    match: function(loader, studentRecord) {
        var matches = false;
        Ext.each(this.data.items, function(record, index) {
            var filter = record.get('filter');
            if(filter.match(studentRecord)) {
                matches = true;
                return false; // Break
            }
        }, this);
        return matches;
    },

    toExportArray: function() {
        var result = [];
        Ext.each(this.data.items, function(record, index) {
            var filter = record.get('filter');
            result.push(filter.toExportObject());
        }, this);
        return result;
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedFileMeta', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "filename"
        }, 
        {
            "type": "int", 
            "name": "size"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedfilemeta/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

/** A prettyview is a read-only view panel used to display a single model record. */
Ext.define('devilry.administrator.PrettyView', {
    extend: 'Ext.panel.Panel',
    cls: 'prettyviewpanel',
    bodyPadding: 0,
    layout: 'fit',

    requires: [
        'devilry.extjshelpers.SetListOfUsers',
        'devilry.extjshelpers.NotificationManager',
        'devilry.extjshelpers.RestProxy'
    ],

    config: {
        /**
         * @cfg
         * The name of the ``Ext.data.Model`` to present in the body. (Required).
         */
        modelname: undefined,

        /**
         * @cfg
         * Unique ID of the object to load from the model. (Required).
         */
        objectid: undefined,

        /**
         * @cfg
         * A ``Ext.XTemplate`` object for the body of this view. (Required).
         */
        bodyTpl: undefined,

        /**
         * @cfg
         * Optional list of buttons for related actions.
         */
        relatedButtons: undefined,

        /**
         * @cfg
         * The url to the dashboard. (Required). Used after delete to return to
         * the dashboard.
         */
        dashboardUrl: undefined

        /**
         * @cfg
         * Optional list of menuitems for plugin actions.
         */
        //pluginItems: undefined
    },

    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when the model record is loaded successfully.
             * @param {Ext.model.Model} record The loaded record.
             */
            'loadmodel',
            
            /**
             * @event
             * Fired when the edit button is clicked.
             * @param {Ext.model.Model} record The record to edit.
             * @param button The edit button.
             */
            'edit');
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.setadminsbutton = Ext.create('Ext.button.Button', {
            text: 'Manage administrators',
            scale: 'large',
            //enableToggle: true,
            listeners: {
                scope: this,
                click: this.onSetadministrators
            }
        });


        this.deletebutton = Ext.create('Ext.button.Button', {
            text: 'Delete',
            scale: 'large',
            //enableToggle: true,
            listeners: {
                scope: this,
                click: this.onDelete
            }
        });

        this.editbutton = Ext.create('Ext.button.Button', {
            text: 'Edit',
            //enableToggle: true,
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onEdit
            }
        });

        var tbar = ['->', this.deletebutton, this.setadminsbutton, this.editbutton];

        if(this.extraMeButtons) {
            Ext.Array.insert(tbar, 2, this.extraMeButtons);
        }

        //if(this.pluginItems) {
            //Ext.Array.insert(tbar, 0, this.pluginItems);
        //}

        if(this.relatedButtons) {
            Ext.Array.insert(tbar, 0, this.relatedButtons);
        }

        this.bodyBox = Ext.widget('box', {
            autoScroll: true,
            padding: 20
        });
        Ext.apply(this, {
            tbar: tbar,
            items: this.bodyBox
        });
        this.callParent(arguments);

        var model = Ext.ModelManager.getModel(this.modelname);
        model.load(this.objectid, {
            scope: this,
            success: this.onModelLoadSuccess,
            failure: this.onModelLoadFailure
        });
    },

    onModelLoadSuccess: function(record) {
        this.record = record;
        this.refreshBody();
        this.fireEvent('loadmodel', record);
    },

    refreshBody: function() {
        var bodyData = this.getExtraBodyData(this.record);
        Ext.apply(bodyData, this.record.data);
        this.bodyBox.update(this.bodyTpl.apply(bodyData));
    },

    /**
     * @private
     */
    getExtraBodyData: function(record) {
        return {};
    },

    /**
     * @private
     */
    onModelLoadFailure: function(record, operation) {
        this.fireEvent('loadmodelFailed', operation);
    },

    /**
     * @private
     */
    onEdit: function(button) {
        this.fireEvent('edit', this.record, button);
    },

    /** Set record. Triggers the loadmodel event. */
    setRecord: function(record) {
        this.onModelLoadSuccess(record);
    },

    /**
     * @private
     */
    onDelete: function(button) {
        var me = this;
        var win = Ext.MessageBox.show({
            title: 'Confirm delete',
            msg: 'Are you sure you want to delete?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            closable: false,
            fn: function(btn) {
                if(btn == 'yes') {
                    me.deleteObject();
                }
            }
        });
    },

    /**
     * @private
     */
    deleteObject: function() {
        this.record.destroy({
            scope: this,
            success: function() {
                window.location.href = this.dashboardUrl;
            },
            failure: this.onDeleteFailure
        });
    },

    /**
     * @private
     */
    onDeleteFailure: function(record, operation) {
        var title, msg;
        if(operation.error.status == 403) {
            title = "Forbidden";
            msg = 'You do not have permission to delete this item. Only super-administrators have permission to delete items with any content.';
        } else {
            title = 'An unknow error occurred';
            msg = "This is most likely caused by a bug, or a problem with the Devilry server.";
        }

        Ext.MessageBox.show({
            title: title,
            msg: msg,
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
    },

    /**
     * @private
     */
    onSetadministrators: function(button) {
        var win = Ext.widget('window', {
            title: 'Set administrators',
            modal: true,
            width: 550,
            height: 300,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                usernames: this.record.data.admins__username,
                helptext: '<p>The username of a single administrator on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: this.onSaveAdmins
                }
            }
        });
        win.show();
        //win.alignTo(button, 'br?', [-win.width, 0]);
    },

    /**
     * @private
     */
    onSaveAdmins: function(setlistofusersobj, usernames) {
        setlistofusersobj.getEl().mask('Saving...');
        this.record.data.fake_admins = usernames
        this.record.save({
            scope: this,
            success: function(record) {
                setlistofusersobj.getEl().unmask();
                record.data.admins__username = usernames
                this.onModelLoadSuccess(record)
                setlistofusersobj.up('window').close();
                devilry.extjshelpers.NotificationManager.show({
                    title: 'Save successful',
                    message: 'Updated adminstrators.'
                });
            },
            failure: function(record, operation) {
                setlistofusersobj.getEl().unmask();
                devilry.extjshelpers.RestProxy.showErrorMessagePopup(operation, 'Failed to change administrators');
            }
        });
    },

    alignToCoverBody: function(item) {
        item.alignTo(this.bodyBox, 'tl', [0, 0]);
    },

    setSizeToCoverBody: function(item, height) {
        item.setWidth(this.bodyBox.getWidth());
        if(!height) {
            height = this.bodyBox.getHeight();
            if(height > 500) {
                height = 500;
            }
        }
        item.setHeight(height);
    }
});


/**
 * A component for information display. Works just like a regular component,
 * except that it adds an extra attribute, ``MORE_BUTTON``, to the template
 * data. This extra attribute, inserts a button in the markup that toggles
 * the visibility of any element in the component with the ``.more`` css class.
 *
 * ## Example:
 *      {
 *          xtype: 'markupmoreinfobox',
 *          tpl: [
 *              'Always visible {MORE_BUTTON}',
 *              '<p {MORE_ATTRS}>Shown when more button is clicked.</p>'
 *          ],
 *          data: {}
 *      }
 *
 * **Note**: we use {MORE_ATTRS}, which simply inserts ``class="more" style="display: none;"``.
 *
 * ## Special template attributes
 *
 * - ``MORE_BUTTON``: The more button (an A-tag).
 * - ``MORE_ATTRS``: The html attributes required on a container for the
 *   more/less buttons show/hide the container. The value is:
 *   ``class="more" style="display: none;"``. If you set the
 *   ``moreCls`` config, that/those classes are added to ``class``.
 */
Ext.define('devilry_extjsextras.MarkupMoreInfoBox', {
    extend: 'Ext.Component',
    alias: 'widget.markupmoreinfobox',
    border: false,
    frame: false,

    /**
     * @cfg {String} [cls="markupmoreinfobox"]
     * Defaults to ``markupmoreinfobox bootstrap``.
     */
    cls: 'markupmoreinfobox bootstrap',

    /**
     * @cfg {String} [lesstext="Less info"]
     * The text to show on the Less info button. The default text is translated.
     */
    lesstext: gettext('Less info'),

    /**
     * @cfg {String} [lesstext="More info ..."]
     * The text to show on the More info button. The default text is translated.
     */
    moretext: gettext('More info'),

    moresuffix: '<span class="expandable-indicator"></span>',
    lesssuffix: '<span class="collapsible-indicator"></span>',

    /**
     * @cfg {String} [moreCls='']
     * Added to the ``class`` attribute of the ``MORE_ATTRS`` template variable.
     */
    moreCls: '',

    initComponent: function() {
        this.morebutton = [
            '<a href="#" class="morebutton">',
                this.moretext, this.moresuffix,
            '</a>'
        ].join('');
        if(!Ext.isEmpty(this.data)) {
            this.setTplAttrs(this.data);
        }

        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.morebutton',
            click: this._onMore
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.lessbutton',
            click: this._onLess
        });
        this.callParent(arguments);
    },

    _getMoreEl: function() {
        var element = Ext.get(this.getEl().query('.more')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },
    _getMoreButtonEl: function() {
        var element = Ext.get(this.getEl().query('a.morebutton')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },
    _getLessButtonEl: function() {
        var element = Ext.get(this.getEl().query('a.lessbutton')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },

    _onMore: function(e) {
        e.preventDefault();
        var button = this._getMoreButtonEl();
        this.moretext = button.getHTML();
        button.setHTML(this.lesstext + this.lesssuffix);
        this._getMoreEl().show();
        this.hide(); this.show(); // Force re-render
        Ext.defer(function() {
            // NOTE: We defer for two reasons: 1, prevent double click, 2: Prevent double event trigger (both more and less)
            button.replaceCls('morebutton', 'lessbutton');
        }, 200, this);
    },

    _onLess: function(e) {
        e.preventDefault();
        this._getMoreEl().hide();
        var button = this._getLessButtonEl();
        button.setHTML(this.moretext);
        this.hide(); this.show(); // Force re-render
        Ext.defer(function() {
            // NOTE: We defer for two reasons: 1, prevent double click, 2: Prevent double event trigger (both more and less)
            button.replaceCls('lessbutton', 'morebutton');
        }, 200, this);
    },

    setTplAttrs: function(data) {
        data.MORE_BUTTON = this.morebutton;
        data.MORE_ATTRS = Ext.String.format('class="more {0}" style="display: none;"', this.moreCls);
        data.MORE_STYLE = 'style="display: none;"';
    },

    update: function(data) {
        this.setTplAttrs(data);
        return this.callParent([data]);
    }
});


Ext.define('devilry_extjsextras.MoreInfoBox', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.moreinfobox',
    border: false,
    frame: false,

    /**
     * @cfg {string} [collapsedCls="muted"]
     * Class to add to ``intro`` and "More info"-link when collapsed.
     */
    collapsedCls: 'muted',

    /**
     * @cfg {String} [expandedCls=null]
     * Class to add to ``intro`` and "Less info"-link when expanded.
     */
    expandedCls: null,

    /**
     * @cfg {String} [introtext]
     * A single sentence to show as the intro. Always end it with ``.``.
     */

    /**
     * @cfg {Object} [moreWidget]
     * Config for the more-widget. This is the element that is shown in
     * addition to ``intro`` when "More info" is clicked.
     * Note that the ``anchor`` attribute will be overwritten.
     */

    /**
     * @cfg {String} [moretext="More info"]
     * Text of the "More info"-link
     */
    moretext: gettext('More info'),

    /**
     * @cfg {String} [lesstext="More info"]
     * Text of the "More info"-link
     */
    lesstext: gettext('Less info'),

    /**
     * @cfg {bool} [small_morelink=false]
     * Wrap the more-link in a html SMALL-tag?
     */
    small_morelink: false,
    
    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            /** @event
             * Fired when the "More info" button is clicked.
             * @param box This moreinfobox.
             */
            'moreclick',

            /** @event
             * Fired when the "Less info" button is clicked.
             * @param box This moreinfobox.
             */
            'lessclick'
        );
    },

    initComponent: function() {
        var cls = 'devilry_extjsextras_moreinfobox bootstrap';
        if(this.cls) {
            cls = Ext.String.format('{0} {1}', cls, this.cls);
        }
        if(!Ext.isEmpty(this.collapsedCls)) {
            this.bodyCls = this.collapsedCls;
        }
        this.cls = cls;

        this.moreWidget.anchor = '100%';
        this.moreWidget.hidden = true;
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'box',
                itemId: 'introBox',
                anchor: '100%',
                tpl: [
                    '<p>',
                        '{introtext}',
                        this.small_morelink? '<small>': '',
                        ' <a href="#" class="morebutton" style="white-space: nowrap;">',
                            '{moretext}',
                            '<span class="expandable-indicator"></span>',
                        '</a>',
                        '<a href="#" class="lessbutton" style="white-space: nowrap; display: none;">',
                            '{lesstext}',
                            '<span class="collapsible-indicator"></span>',
                        '</a>',
                        this.small_morelink? '</small>': '',
                    '</p>'
                ],
                data: {
                    introtext: this.introtext,
                    moretext: this.moretext,
                    lesstext: this.lesstext
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a',
                    click: this._onMoreOrLess
                }
            }, this.moreWidget]
        });
        this.callParent(arguments);
    },

    _getMoreWidget: function() {
        return this.getComponent(1);
    },
    _getIntroBox: function() {
        return this.down('#introBox');
    },
    _getLessButtonEl: function() {
        var element = Ext.get(this._getIntroBox().getEl().query('a.lessbutton')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },
    _getMoreButtonEl: function() {
        var element = Ext.get(this._getIntroBox().getEl().query('a.morebutton')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },

    _onMoreOrLess: function(e) {
        e.preventDefault();
        var element = Ext.get(e.target);
        if(element.hasCls('morebutton')) {
            this._onMore();
        } else {
            this._onLess();
        }
    },

    _onMore: function(e) {
        if(!Ext.isEmpty(this.collapsedCls)) {
            this.removeBodyCls(this.collapsedCls);
        }
        if(!Ext.isEmpty(this.expandedCls)) {
            this.addBodyCls(this.expandedCls);
        }

        this._getMoreButtonEl().hide(); // NOTE: Important that this comes before the other show()-calls below, because hide() on an element does not trigger re-rendering.
        this._getLessButtonEl().show();
        this._getMoreWidget().show();
        this.fireEvent('moreclick', this);
    },

    _onLess: function(e) {
        if(!Ext.isEmpty(this.expandedCls)) {
            this.removeBodyCls(this.expandedCls);
        }
        if(!Ext.isEmpty(this.collapsedCls)) {
            this.addBodyCls(this.collapsedCls);
        }

        this._getMoreButtonEl().show();
        this._getLessButtonEl().hide();
        this._getMoreWidget().hide();
        this.fireEvent('lessclick', this);
    }
});


Ext.define('devilry.student.stores.UploadedFileStore', {
    extend: 'Ext.data.ArrayStore',

    // Store configs
    autoDestroy: true,

    // Reader configs
    idIndex: 0,
    fields:[
        {name: 'filename', type: 'string'}
    ]
});


Ext.define('devilry.administrator.subject.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_subjectprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section help">',
        '    <h1>What is a subject?</h1>',
        '    <p>',
        '        A subject is usually a course or seminar. A subject contains periods, which are usually semesters.',
        '    </p>',
        '</div>'
    )
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Manual', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',

    msgTpl: Ext.create('Ext.XTemplate',
        '<div class="readable-section">',
        'Choose the students that qualifies for final exams, and click <strong>Save</strong>. ',
        'Press the <em>{ctrlbutton} button</em> while clicking students to select multiple students.',
        '<div>'
    ),

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                html: this.msgTpl.apply({
                    ctrlbutton: Ext.isMac? 'CMD/Command': 'CTRL/Control'
                }),
                margin: '0 0 10 0',
                store: this.loader.assignment_store
            }, this.saveButton]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var selected = this._getSelectedStudents();
        return Ext.Array.contains(selected, student);
    },

    validInput: function() {
        if(this._getSelectedStudents().length === 0) {
            Ext.MessageBox.alert('Select at least one', 'Please select at least one student.');
            return false;
        }
        return true;
    },

    _getSelectedStudents: function() {
        var dataview = this.up('statistics-periodadminlayout').down('statistics-dataview');
        var selected = dataview.getSelectedStudents();
        return selected;
    }

});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin', {
    extend: 'Ext.form.ComboBox',

    config: {
        availablePlugins: [],
        commonArgs: undefined
    },

    constructor: function(config) {
        this.addEvents('pluginSelected');
        this.initConfig(config);
        this.callParent([config]);
    },


    initComponent: function() {
        var model = Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.ChoicesModel', {
            extend: 'Ext.data.Model',
            fields: ['title', 'path', 'args'],
            idProperty: 'path'
        });
        var store = Ext.create('Ext.data.Store', {
            model: model,
            data: this.availablePlugins
        });

        Ext.apply(this, {
            store: store,
            fieldLabel: 'How?',
            queryMode: 'local',
            editable: false,
            displayField: 'title',
            valueField: 'path',
            emptyText: 'Please make a selection...',
            forceSelection: true
        });
        this.on('select', this._onSelect, this);
        this.callParent(arguments);
    },

    selectByPath: function(path) {
        var record = this.store.getById(path);
        this.select(record);
        this._onSelect(undefined, [record]);
    },

    _onSelect: function(field, values) {
        var record = values[0];
        var title = record.get('title');
        var path = record.get('path');
        var config = {title: title, path: path};
        Ext.apply(config, this.commonArgs);
        var pluginObj = Ext.create(path, config);
        this.fireEvent('pluginSelected', pluginObj);
    }
});


/**
Button intended as the primary button in a view (the one it is most natural to
click by default).
*/ 
Ext.define('devilry_extjsextras.PrimaryButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.primarybutton',
    cls: 'devilry_primarybutton',
    scale: 'large',
    //minWidth: 150,
    ui: 'primary'
});


/**
 * A mixin to perform an action each selected item in a grid, including grids using paging.
 */
Ext.define('devilry.extjshelpers.GridPeformActionOnSelected', {
    /**
     * Call the given action on each selected item. If all items on the current page is selected,
     * a MessageBox will be shown to the user where they can choose to call the action on all items
     * instead of just the ones on the current page.
     *
     * @param action See {@link #performActionOnAll}.
     */
    performActionOnSelected: function(action) {
        var selected = this.selModel.getSelection();
        var totalOnCurrentPage = this.store.getCount();
        if(selected.length === totalOnCurrentPage && this._getTotalStorePages() > 1) {
            var msg = Ext.String.format(
                'You have selected all items on the current page. Choose <strong>yes</strong> to perform the selected action on <strong>all {0}</strong> items instead of just the items on the current page.',
                this.store.getTotalCount()
            );
            Ext.MessageBox.show({
                title: 'Do you want to perform the action on ALL items?',
                msg: msg,
                buttons: Ext.Msg.YESNO,
                icon: Ext.Msg.QUESTION,
                scope: this,
                fn: function(btn) {
                    if(btn == 'yes') {
                        this.performActionOnAll(action);
                    } else {
                        this._performActionOnSelected(action, selected, 1, selected.length);
                    }
                }
            });
        } else {
            this._performActionOnSelected(action, selected, 1, selected.length);
        }
    },


    /**
     * Call the given action on each item in the store (on all pages in the store).
     *
     * @param action An object with the following attributes:
     *
     *      callback
     *          A callback function that is called for each record in the
     *          store. The callback gets the folling arguments: `(record,
     *          index, total)`. Index is the index of the record starting with
     *          1, and total is the total number of records.
     *      scope
     *          The scope to execute `callback` in.
     *      extraArgs
     *          Array of extra arguments to callback.
     *          
     */
    performActionOnAll: function(action) {
        this._performActionOnAllTmp = {
            originalCurrentPage: this.store.currentPage,
            action: action,
        }
        this._performActionOnPage(1);
    },

    /**
     * Gather all selected records in an array. This array is forwarded to the action specified as parameter.
     *
     * @param action An object with the following attributes:
     *
     *      callback
     *          A callback function that is called for each record in the
     *          store. The callback gets the array as argument.
     *      scope
     *          The scope to execute `callback` in.
     *      extraArgs
     *          Array of extra arguments to callback.
     *
     */
    gatherSelectedRecordsInArray: function(action) {
        var array = [];
        this.performActionOnSelected({
            scope: this,
            callback: function(record, index, totalSelected) {
                var msg = Ext.String.format('Gathering record {0}/{1}', index, totalSelected);
                this.getEl().mask(msg);
                array.push(record);
                if(index == totalSelected) {
                    this.getEl().unmask();
                    Ext.bind(action.callback, action.scope, action.extraArgs, true)(array);
                }
            }
        });
    },


    /**
     * @private
     */
    _getTotalStorePages: function() {
        var totalPages = this.store.getTotalCount() / this.store.pageSize;
        if(this.store.getTotalCount() % this.store.pageSize != 0) {
            totalPages = Math.ceil(totalPages);
        }
        return totalPages;
    },

    /**
     * @private
     */
    _performActionOnPage: function(pagenum) {
        var totalPages = this._getTotalStorePages();

        if(pagenum > totalPages) {
            //this.store.currentPage = this._performActionOnAllTmp.originalCurrentPage;
            //this.store.load();
        } else {
            this.store.currentPage = pagenum;
            this.store.load({
                scope: this,
                callback: function(records, op, success) {
                    if(success) {
                        this._performActionOnAllPageLoaded(pagenum, records);
                    } else {
                        throw "Failed to load page";
                    }
                }
            });
        }
    },

    /**
     * @private
     */
    _performActionOnAllPageLoaded: function(pagenum, records) {
        var startIndex = ((pagenum-1) * this.store.pageSize) + 1;
        this._performActionOnSelected(
            this._performActionOnAllTmp.action, records,
            startIndex, this.store.getTotalCount()
        );
        pagenum ++;
        this._performActionOnPage(pagenum);
    },

    /**
     * @private
     */
    _performActionOnSelected: function(action, selected, startIndex, total) {
        Ext.each(selected, function(record, index) {
            Ext.bind(action.callback, action.scope, action.extraArgs, true)(record, startIndex + index, total);
        });
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgrouptitle',
    cls: 'widget-assignmentgrouptitle section pathheading bootstrap',

    tpl: Ext.create('Ext.XTemplate',
        '<h1 style="margin: 0; line-height: 25px;"><small>{parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.</small>{parentnode__long_name}</h1>',
        '<tpl if="name">',
            '{name}: ',
        '</tpl>',
        '<ul class="names" style="margin: 0;">',
            '<tpl for="candidates">',
                '<li>{identifier} <tpl if="full_name">({full_name})</tpl></li>',
            '</tpl>',
        '</ul>',
        '<tpl if="canExamine">',
            '<tpl if="parentnode__anonymous == false">',
                '<small><a href="mailto:',
                    '<tpl for="candidates">',
                        '{email}<tpl if="xindex &lt; xcount">,</tpl>',
                    '</tpl>',
                '?subject={parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.{parentnode__short_name}',
                '&body={url}',
                '">',
                'Send email</a></small>',
            '</tpl>',
        '</tpl>'
    )
});


Ext.define('devilry.examiner.ActiveAssignmentsView', {
    extend: 'devilry.extjshelpers.DashGrid',
    alias: 'widget.examiner_activeassignmentsview',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    config: {
        model: undefined,
        noRecordsMessage: {
            title: gettext('No active assignments'),
            msg: interpolate(gettext('You are not registered on any assignments in any active %(periods_term)s.'), {
                periods_term: gettext('periods')
            }, true)
        },
        pageSize: 30,
        dashboard_url: undefined
    },

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">',
            '{data.parentnode__parentnode__short_name}.',
            '{data.parentnode__short_name} - ',
            '{data.long_name}',
        '</a>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            //groupField: 'parentnode__parentnode__long_name',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-publishing_time']);
        this.store.pageSize = this.pageSize
    },

    createBody: function() {
        //var groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            //groupHeaderTpl: '{name}',
        //});
        var me = this;
        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            sortableColumns: false,
            disableSelection: true,
            autoScroll: true,
            cls: 'bootstrap',
            store: this.store,
            flex: 1,
            hideHeaders: true,
            //features: [groupingFeature],
            columns: [{
                text: 'unused',
                menuDisabled: true,
                flex: 1,
                dataIndex: 'long_name',
                renderer: function(value, meta, record) {
                    return me.assignmentRowTpl.apply({
                        data: record.data,
                        url: Ext.String.format('{0}assignment/{1}', me.dashboard_url, record.get('id'))
                    });
                }
            }]
        });
        this.add({
            xtype: 'box',
            tpl: '<div class="section"><h2>{header}</h2></div>',
            data: {
                header: interpolate(gettext('Assignments in active %(periods_term)s'), {
                    periods_term: gettext('periods')
                }, true)
            }
        });
        this.add(activeAssignmentsGrid);
    }

});


Ext.define('devilry.administrator.studentsmanager.LoadRelatedUsersMixin', {

    /**
     * @private
     */
    _loadAllRelatedUsers: function(modelname, callback) {
        var relatedUserModel = Ext.ModelManager.getModel(modelname);

        var relatedUserStore = Ext.create('Ext.data.Store', {
            model: relatedUserModel,
            remoteFilter: true,
            remoteSort: true
        });

        relatedUserStore.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.periodid
        }]);
        //deliverystore.proxy.extraParams.orderby = Ext.JSON.encode(['-deadline__deadline', '-number']);

        relatedUserStore.proxy.extraParams.page = 1;
        relatedUserStore.pageSize = 1;
        relatedUserStore.load({
            scope: this,
            callback: function(records) {
                relatedUserStore.proxy.extraParams.page = 1;
                relatedUserStore.pageSize = relatedUserStore.totalCount;
                relatedUserStore.load({
                    scope: this,
                    callback: callback
                });
            }
        });
    },

    /**
     * @private
     */
    _postLoadAllRelatedUsers: function(callbackOpt, relatedUsers) {
        Ext.bind(
            callbackOpt.callback,
            callbackOpt.scope,
            callbackOpt.args,
            true
        )(relatedUsers);
    },

    relatedUserRecordsToStringArray: function(relatedUsers, format) {
        var tpl = Ext.create('Ext.XTemplate', format);
        return Ext.Array.map(relatedUsers, function(relatedUser) {
            return tpl.apply(relatedUser.data);
        }, this);
    },

    loadAllRelatedStudents: function(callbackOpt) {
        if(this._relatedStudents == undefined) {
            this.getEl().mask('Loading related students');
            this._onLoadAllRelatedStudentsCallbackOpt = callbackOpt
            this._loadAllRelatedUsers(
                'devilry.apps.administrator.simplified.SimplifiedRelatedStudent',
                this._onLoadAllRelatedStudents
            );
        } else {
            this._postLoadAllRelatedUsers(callbackOpt, this._relatedStudents);
        };
    },

    /**
     * @private
     */
    _onLoadAllRelatedStudents: function(records) {
        this.getEl().unmask();
        //console.log(records);
        this._relatedStudents = records;
        this._postLoadAllRelatedUsers(this._onLoadAllRelatedStudentsCallbackOpt, records);
        this._onLoadAllRelatedStudentsCallbackOpt = undefined;
    },


    loadAllRelatedExaminers: function(callbackOpt) {
        if(this._relatedExaminers == undefined) {
            this.getEl().mask('Loading related students');
            this._onLoadAllRelatedExaminersCallbackOpt = callbackOpt
            this._loadAllRelatedUsers(
                'devilry.apps.administrator.simplified.SimplifiedRelatedExaminer',
                this._onLoadAllRelatedExaminers
            );
        } else {
            this._postLoadAllRelatedUsers(callbackOpt, this._relatedExaminers);
        };
    },

    /**
     * @private
     */
    _onLoadAllRelatedExaminers: function(records) {
        this.getEl().unmask();
        this._relatedExaminers = records;
        this._postLoadAllRelatedUsers(this._onLoadAllRelatedExaminersCallbackOpt, records);
        this._onLoadAllRelatedExaminersCallbackOpt = undefined;
    }
});


/** A button bar containing {@link devilry.extjshelpers.ButtonBarButton} many.
 *
 * Add buttons as items to the container.
 * */
Ext.define('devilry.extjshelpers.ButtonBar', {
    extend: 'Ext.container.Container',
    requires: ['devilry.extjshelpers.ButtonBarButton'],
    alias: 'widget.buttonbar',
    border: 0,
    height: 40,
    layout: {
        type: 'hbox',
        align: 'stretch',
        pack: 'center'
    },

    config: {
        emptyHtml: undefined,
    },

    constructor: function(config) {
        this.loadedItems = 0;
        this.loadedWithRecords = 0;
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);
        this.on('render', this.updateMask, this);
    },

    updateMask: function() {
        if(this.loadedItems == this.items.items.length) {
            this.getEl().unmask();
            if(this.loadedWithRecords == 0) {
                this.height = 'auto';
                this.update(this.emptyHtml);
            };
        } else {
            this.getEl().mask('Loading...');
        }
    },

    notifyStoreLoad: function(hasRecords) {
        this.loadedItems ++;
        if(hasRecords) {
            this.loadedWithRecords ++;
        }
        this.updateMask();
    }
});


Ext.define('devilry_header.Roles', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_roles',
    cls: 'devilryheader_roles',

    tpl: [
        '<tpl if="loading">',
            '<div class="loading">', gettext('Loading'), ' ...</div>',
        '<tpl else>',
            '<tpl if="has_any_roles">',
                '<ul role="navigation">',
                    '<tpl if="userInfo.is_student">',
                        '<li><a href="{urlpath_prefix}/devilry_student/" class="student_role">',
                            '<div class="heading">',
                                gettext('Student'),
                            '</div>',
                            '<div class="description">',
                                gettext('Students can make deliveres and browse their own feedback history.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_examiner">',
                        '<li><a href="{urlpath_prefix}/examiner/" class="examiner_role">',
                            '<div class="heading">',
                                gettext('Examiner'),
                            '</div>',
                            '<div class="description">',
                                gettext('Examiners give students feedback on their deliveries.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_subjectadmin | userInfo.is_periodadmin | userInfo.is_assignmentadmin">',
                        '<li><a href="{urlpath_prefix}/devilry_subjectadmin/" class="subjectadmin_role">',
                            '<div class="heading">',
                                interpolate(gettext('%(Subject_term)s administrator'), {
                                    Subject_term: gettext('Subject')
                                }, true),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('%(Subject_term)s administrators manage %(subjects_term)s, %(periods_term)s and assignments where they have been explicitly registered as administrator.'), {
                                    Subject_term: gettext('Subject'),
                                    subjects_term: gettext('subjects'),
                                    nodes_term: gettext('nodes'),
                                    periods_term: gettext('periods')
                                }, true),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser | userInfo.is_nodeadmin">',
                        '<li><a href="{urlpath_prefix}/devilry_nodeadmin/" class="nodeadmin_role">',
                            '<div class="heading">',
                                interpolate(gettext('%(Node_term)s administrator'), {
                                    Node_term: gettext('Node')
                                }, true),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('%(Node_term)s administrators manage %(nodes_term)s where they have administrator-rights.'), {
                                    Node_term: gettext('Node'),
                                    nodes_term: gettext('nodes')
                                }, true),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser">',
                        '<li><a href="{urlpath_prefix}/superuser/" class="superuser_role">',
                            '<div class="heading">',
                                gettext('Superuser'),
                            '</div>',
                            '<div class="description">',
                                gettext('Superusers have complete access to all data stored in Devilry.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                '</ul>',
                '<p class="bootstrap"><a href="{lacking_permissions_url}">',
                    gettext('I should have had more roles'),
                '</a></p>',
            '<tpl else>',
                '<div class="nopermissions bootstrap">',
                    '<div class="alert alert-error">',
                        gettext('You have no permissions on anything in Devilry. Click <a href="{no_permissions_url}">this link</a> to go to a page explaining how to get access to Devilry.'),
                    '</div>',
                '</div>',
            '</tpl>',
        '</tpl>'
    ],

    data: {
        loading: true
    },


    /**
     * Set UserInfo record and update view.
     */
    setUserInfoRecord: function(userInfoRecord) {
        this.update({
            userInfo: userInfoRecord.data,
            has_any_roles: userInfoRecord.hasAnyRoles(),
            lacking_permissions_url: DevilrySettings.DEVILRY_LACKING_PERMISSIONS_URL,
            urlpath_prefix: DevilrySettings.DEVILRY_URLPATH_PREFIX,
            no_permissions_url: DevilrySettings.DEVILRY_LACKING_PERMISSIONS_URL
        });
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.examiner.simplified.SimplifiedAssignment', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "date", 
            "name": "publishing_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "delivery_types"
        }, 
        {
            "type": "bool", 
            "name": "anonymous"
        }, 
        {
            "type": "int", 
            "name": "scale_points_percent"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "date", 
            "name": "parentnode__start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "parentnode__end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/examiner/restfulsimplifiedassignment/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedStaticFeedback', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "grade"
        }, 
        {
            "type": "bool", 
            "name": "is_passing_grade"
        }, 
        {
            "type": "auto", 
            "name": "saved_by"
        }, 
        {
            "type": "date", 
            "name": "save_timestamp", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "auto", 
            "name": "rendered_view"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "date", 
            "name": "delivery__time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "delivery__number"
        }, 
        {
            "type": "auto", 
            "name": "delivery__delivered_by"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedstaticfeedback/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "period", "delivery", "candidates", "assignment_group", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedExaminer', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "user"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "assignmentgroup"
        }, 
        {
            "type": "auto", 
            "name": "user__username"
        }, 
        {
            "type": "auto", 
            "name": "user__email"
        }, 
        {
            "type": "auto", 
            "name": "user__devilryuserprofile__full_name"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedexaminer/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["userdetails"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

/** Breadcrumb management. */
Ext.define('devilry_header.Breadcrumbs', {
    extend: 'Ext.Component',
    alias: 'widget.breadcrumbs',
    cls: 'devilry_header_breadcrumbcomponent',

    requires: [
        'Ext.ComponentQuery'
    ],

    tpl: [
        '<ul class="devilry_header_breadcrumb">',
            '<tpl for="breadcrumbs">',
                '<tpl if="xindex != xcount">',
                    '<li>',
                        '<a href="{url}">{text}</a><span class="divider">/</span>',
                    '</li>',
                '</tpl>',
                '<tpl if="xindex == xcount">',
                    '<li class="active">{text}</li>',
                '</tpl>',
            '</tpl>',
        '</ul>'
    ],

    /**
     * @cfg {object} [defaultBreadcrumbs=undefined]
     * A list of breadcrumbs that will always be added to the beginning of
     * the breadcrumbs.
     */
    defaultBreadcrumbs: undefined,

    initComponent: function() {
        this.clear();
        this.callParent(arguments);
        this.draw();
    },

    /** Set the breadcrumbs.
     *
     * Example:
     *
     *      set([{
     *          url: '/hello',
     *          text: 'Hello'
     *      }, {
     *          url: '/hello/cruel',
     *          text: 'Cruel'
     *      }], 'World');
     * */
    set: function(breadcrumbs, current) {
        this.clear();
        if(this.getDefaultBreadcrumbs()) {
            this.addMany(this.getDefaultBreadcrumbs());
        }
        this.addMany(breadcrumbs);
        this.add('', current);
        this.draw();
    },

    /**
     * Get the default breadcrumbs. You can override this to generate
     * ``defaultBreadcrumbs`` dynamically. Defaults to returning
     * ``this.defaultBreadcrumbs``.
     */
    getDefaultBreadcrumbs:function () {
        return this.defaultBreadcrumbs;
    },

    addMany: function(breadcrumbs) {
        Ext.Array.each(breadcrumbs, function(breadcrumb) {
            this.add(breadcrumb.url, breadcrumb.text);
        }, this);
    },

    /**
     * Called every time an url is added to the breadcrumb. Override it
     * if you want to change the URLs (I.E.: Add a prefix).
     */
    formatUrl: function (url, meta) {
        return url;
    },

    /**
     * Add breadcrumb.
     * @param url The URL of the breadcrumb.
     * @param text The text for the breadcrumb.
     * @param meta Metadata that can be used by other systems when to customize the breadcrumb.
     */
    add: function(url, text, meta) {
        this.breadcrumbs.push({
            url: this.formatUrl(url),
            text: text,
            meta: meta
        });
    },

    clear: function() {
        this.breadcrumbs = [];
    },

    draw: function() {
        if(this.breadcrumbs.length === 0) {
            this.hide();
        } else {
            this.show();
            this.update({
                breadcrumbs: this.breadcrumbs
            });
        }
    },

    setHome: function() {
        this.clear();
        this.draw();
    },

    statics: {
        /** Return the first detected instance of this component in body. */
        getInBody: function() {
            var components = Ext.ComponentQuery.query('breadcrumbs');
            if(components.length === 1) {
                return components[0];
            } else if(components.length === 0) {
                throw "Could not find any devilry_header.Breadcrumbs component in body.";
            } else {
                throw "Found more than one devilry_header.Breadcrumbs component in body.";
            }
        }
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            target: 'tooltip-browse-files',
            anchor: 'left',
            html: 'Click to view the files in this delivery'
        });

Ext.define('devilry.statistics.AggregatedPeriodDataStore', {
    extend: 'Ext.data.Store',
    model: 'devilry.statistics.AggregatedPeriodDataModel',

    setPeriod: function(period_id) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, period_id);
    },

    setLoadEverything: function(loadEverything) {
        this.proxy.extraParams.load_everything = loadEverything? '1': '0';
    },

    loadForPeriod: function(period_id, loadEverything, loadConfig) {
        this.setPeriod(period_id);
        this.setLoadEverything(loadEverything);
        this.load(loadConfig);
    }
});


/** The close/open methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerCloseOpen', {
    /**
     * @private
     */
    onCloseGroups: function() {
        this.openOrCloseGroups(false);
    },

    /**
     * @private
     */
    onOpenGroups: function() {
        this.openOrCloseGroups(true);
    },

    /**
     * @private
     */
    openOrCloseGroups: function(is_open) {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var action = is_open? 'open': 'close';
        Ext.MessageBox.show({
            title: Ext.String.format('Confirm {0} groups?', action),
            msg: Ext.String.format('Are you sure you want to {0} the selected groups?', action),
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.progressWindow.start('Open/close groups');
                    this._finishedSavingGroupCount = 0;
                    this.down('studentsmanager_studentsgrid').performActionOnSelected({
                        scope: this,
                        callback: this.openOrCloseGroup,
                        extraArgs: [is_open]
                    });
                }
            }
        });

    },

    /**
     * @private
     */
    openOrCloseGroup: function(record, index, totalSelectedGroups, is_open) {
        var msg = Ext.String.format('{0} group {1}/{2}',
            (is_open? 'Opening': 'Closing'),
            index, totalSelectedGroups
        );
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.is_open = is_open;
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(record, Ext.String.format('Group successfully {0}.', (is_open? 'opened': 'closed')));
                } else {
                    this.progressWindow.addErrorFromOperation(
                        record,
                        Ext.String.format('Failed to {0} group.', (is_open? 'open': 'close')),
                        operation
                    );
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish(null, {
                        title: 'Success',
                        html: Ext.String.format(
                            '<div class="section info"><h1>Success</h1>Successfully {0} {1} groups.</div>',
                            (is_open? 'opened': 'closed'),
                            totalSelectedGroups
                        )
                    });
                }
            }
        });
    }

});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.gradeeditors.simplified.examiner.SimplifiedFeedbackDraft', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "auto", 
            "name": "saved_by"
        }, 
        {
            "type": "date", 
            "name": "save_timestamp", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "draft"
        }, 
        {
            "type": "bool", 
            "name": "published"
        }, 
        {
            "type": "auto", 
            "name": "staticfeedback"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/gradeeditors/examiner/restfulsimplifiedfeedbackdraft/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.charts.PointsOfGroupsOnSingleAssignment', {
    extend: 'Ext.chart.Chart',
    alias: 'widget.chart_pointsofgroupsonsingleassignment',
    cls: 'widget-chart_pointsofgroupsonsingleassignment',

    groupTpl: Ext.create('Ext.XTemplate',
        '<tpl for="candidates">',
        '   {.}<tpl if="xindex != xcount">, </tpl>',
        '</tpl>'
    ),

    hoverTpl: Ext.create('Ext.XTemplate',
        '<tpl for="candidates__identifier">',
        '   {.}<tpl if="xindex != xcount">, </tpl>',
        '</tpl>:',
        'points: {feedback__points}'
    ),

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            style: 'background:#fff',
            animate: true,
            shadow: true,
            axes: [{
                type: 'Numeric',
                position: 'bottom',
                fields: ['feedback__points'],
                label: {
                    renderer: Ext.util.Format.numberRenderer('0,0')
                },
                title: 'Points',
                grid: true,
                minimum: 0
            }, {
                type: 'Category',
                position: 'left',
                fields: ['candidates__identifier'],
                title: 'Group',

                label: {
                    renderer: function(data) {
                        return me.groupTpl.apply({candidates: data});
                    }
                },
            }],
            series: [{
                type: 'bar',
                axis: 'bottom',
                highlight: true,
                tips: {
                    trackMouse: true,
                    width: 140,
                    height: 28,
                    renderer: function(storeItem, item) {
                        this.setTitle(me.hoverTpl.apply(storeItem.data));
                    }
                },
                label: {
                    display: 'insideEnd',
                    'text-anchor': 'middle',
                    field: 'feedback__points',
                    renderer: Ext.util.Format.numberRenderer('0'),
                    orientation: 'vertical',
                    color: '#333'
                },
                xField: 'id',
                yField: 'feedback__points',

                renderer: function(sprite, record, attr, index, store) {
                    var color = record.get('feedback__is_passing_grade')? 'green': 'red';
                    return Ext.apply(attr, {
                        fill: color
                    });
                }

            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry_header.HelpLinkModel', {
    extend: 'Ext.data.Model',
    idProperty: 'url',
    fields: [
        {name: 'help_url', type: 'string'},
        {name: 'title', type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'superuser', type: 'bool'},
        {name: 'nodeadmin', type: 'bool'},
        {name: 'subjectadmin', type: 'bool'},
        {name: 'periodadmin', type: 'bool'},
        {name: 'assignmentadmin', type: 'bool'},
        {name: 'examiner', type: 'bool'},
        {name: 'student', type: 'bool'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_helplinks/helplinks/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },
    
    roles: ['superuser', 'nodeadmin', 'subjectadmin', 'periodadmin',
        'assignmentadmin', 'examiner', 'student'],

    matchesUserInfoRecord: function(userInfoRecord) {
        for(var i=0; i < this.roles.length; i++)  {
            var role = this.roles[i];
            if(this.get(role) && userInfoRecord.get('is_' + role)) {
                return true;
            }
        }
    }
});


Ext.define('devilry_header.store.AdminSearchResults', {
    extend: 'devilry_header.store.BaseSearchResults',
    model: 'devilry_header.model.AdminSearchResult'
});

/**
Message for highlighting the failure, possible failure, or success of
an action. Particularly useful for forms.
*/ 
Ext.define('devilry_extjsextras.AlertMessage', {
    extend: 'devilry_extjsextras.MarkupMoreInfoBox',
    alias: 'widget.alertmessage',

    requires: [
        'Ext.fx.Animator',
        'Ext.util.DelayedTask'
    ],
    
    tpl: [
        '<div class="alert alert-{type}{extracls}{closablecls}" style="{style}">',
            '<tpl if="closable">',
                '<button type="button" class="close" data-dismiss="alert">×</button>',
            '</tpl>',
            '<tpl if="title">',
                '<strong>{title}</strong>: ',
            '</tpl>',
            '{message}',
        '</div>'
    ],

    /**
     * @cfg {String} [boxMargin]
     * Override the margin style of the alert DIV.
     */
    boxMargin: undefined,


    /**
     * @cfg {String} [extracls=undefined]
     * Extra css classes. Example: ``"flat compact"``.
     */

    /**
     * @cfg
     * Type of message. Valid values: 'error', 'warning', 'info' or 'success'.
     * Defaults to 'warning'.
     */
    type: 'warning',

    /**
     * @cfg
     * The one line of message to display. This is not required, as it may be
     * useful to initialize an hidden alert message and use update() to change
     * the message when there is a message to show.
     */
    message: '',

    /**
     * @cfg {string|array} [messagetpl]
     * An XTemplate string or array to use instead of ``message``.
     * Requires that you specify ``messagedata``.
     */
    messagetpl: null,

    /**
     * @cfg {Object} [messagedata]
     * Data for ``messagetpl``.
     */
    messagedata: undefined,


    /**
     * @cfg {bool} [closable=false]
     * Show close button. The ``closed`` event is fired when the button is
     * clicked.
     */
    closable: false,

    /**
     * @cfg {int} [autoclose]
     * Fire the ``close`` event ``autoclose`` seconds after creating the message.
     * If ``true``, we calculate the autoclose time automatically based on the
     * number of words.
     */

    /**
     * @cfg
     * An optional title for the message.
     */
    title: null,

    moretext: gettext('Details'),
    lesstext: gettext('Details'),

    initComponent: function() {
        var cls = 'bootstrap devilry_extjsextras_alertmessage';
        if(this.cls) {
            cls = Ext.String.format('{0} {1}', cls, this.cls);
        }
        this.cls = cls;
        this.callParent(arguments);
        this.update(this.messagetpl || this.message, this.type, this.messagedata);

        this.addListener({
            scope: this,
            element: 'el',
            delegate: '.close',
            click: function(e) {
                e.preventDefault();
                this.fireEvent('closed', this);
            }
        });
        if(!Ext.isEmpty(this.autoclose)) {
            if(this.autoclose === true) {
                this.autoclose = this._calculateAutocloseTime();
            }
            this.cancelTask = new Ext.util.DelayedTask(function(){
                this.fadeOutAndClose();
            }, this);
            this.addListener({
                scope: this,
                element: 'el',
                delegate: 'div.alert',
                //mouseover: this._onMouseOver,
                mouseleave: this._onMouseLeave,
                mouseenter: this._onMouseEnter
            });
            this._deferAutoclose();
        }
    },

    _deferAutoclose: function() {
        this.cancelTask.delay(1000*this.autoclose);
    },

    _onMouseEnter: function() {
        this.cancelTask.cancel(); // We do not close the message while mouse is over it.
    },
    _onMouseLeave: function() {
        this._deferAutoclose();
    },

    _calculateAutocloseTime: function() {
        var alltext = this.message;
        if(!Ext.isEmpty(this.title)) {
            alltext += this.title;
        }
        var words = Ext.String.splitWords(alltext);
        var sec = words.length * 0.4; // One second per work
        sec = sec > 3? sec: 3; // ... but never less than 3 sec
        return Math.round(2 + sec); // 2 seconds to focus on the message + time to read it
    },

    fadeOutAndClose: function() {
        Ext.create('Ext.fx.Animator', {
            target: this.getEl(),
            duration: 3000,
            keyframes: {
                0: {
                    opacity: 1
                },
                100: {
                    opacity: 0.1
                }
            },
            listeners: {
                scope: this,
                afteranimate: function() {
                    this.fireEvent('closed', this);
                }
            }
        });
    },



    /**
     * Update the message and optionally the type. If the type is not
     * specified, the type will not be changed.
     *
     * @param messageOrTpl Message string, or XTemplate array/string if ``data`` is specified.
     * @param type The message type. Defaults to ``this.type`` if ``undefined``.
     * @param data If this is specified, ``message`` is an XTemplate config
     *    (see the ``messagetpl`` config), and ``data`` is the data for the
     *    template.
     * */
    update: function(messageOrTpl, type, data) {
        if(type) {
            this.type = type;
        }
        if(data) {
            this.setTplAttrs(data);
            this.message = Ext.create('Ext.XTemplate', messageOrTpl).apply(data);
        } else {
            this.message = messageOrTpl;
        }
        var style = '';
        if(!Ext.isEmpty(this.boxMargin)) {
            style = Ext.String.format('margin: {0};', this.boxMargin);
        }
        this.callParent([{
            type: this.type,
            message: this.message,
            title: this.title,
            style: style,
            closable: this.closable,
            extracls: Ext.isEmpty(this.extracls)? '': ' ' + this.extracls,
            closablecls: this.closable? ' closable': ''
        }]);
    },

    updateData: function(data, type) {
        this.update(this.messagetpl, type, data);
    }
});


Ext.define('devilry_header.BaseSearchResultsView', {
    extend: 'Ext.view.View',
    cls: 'devilry_header_searchresults bootstrap',

    /**
     * @cfg {string|string[]} [singleResultTpl]
     * The XTemplate for a single search result.
     */

    /**
     * @cfg {string} [heading=undefined]
     * The heading of the search result. Title is not shown if this is not defined.
     */

    hidden: true, // We show ourself automatically on search results
    loadCountDefault: 10,
    loadCountMax: 150,
    showHeading: false,
    noResultsMsgTpl: [
        '<small class="muted">',
            gettext('No results matching {search} found.'),
        '</small>'
    ],

    requires: [
        'Ext.XTemplate'
    ],

    constructor:function () {
        this.addEvents(
            /**
             * @event resultLinkClick
             * Fired when a link to a search result is clicked.
             */
            'resultLinkClick'
        );
        this.callParent(arguments);
    },

    initComponent: function() {
        var headingTpl = [];
        if(this.showHeading) {
            headingTpl = ['<h3>', this.heading, '</h3>'];
        }

        var typeNameMap = {
            core_node: gettext('Node'),
            core_subject: gettext('Subject'),
            core_period: gettext('Period'),
            core_assignment: gettext('Assignment'),
            core_assignmentgroup: gettext('Group')
        };

        var me = this;
        Ext.apply(this, {
            cls: Ext.String.format('{0} {1}', this.cls, this.extraCls),
            tpl: [
                headingTpl.join(''),
                '<ul class="unstyled search-results">',
                    '<tpl for=".">',
                        '<li class="single-result-wrapper">',
                            this.singleResultTpl.join(''),
                        '</li>',
                    '</tpl>',
                '</ul>',
                '<p class="no-searchresults-box" style="display: none;">',
                    // NOTE: We set the value of this when it is shown
                '</p>',
                '<p>',
                    '<a class="btn btn-primary btn-small more-searchresults-button" style="display: none;">',
                        // NOTE: We set the value of this when it is shown
                    '</a>',
                '</p>', {
                    getTypeName:function (type) {
                        return typeNameMap[type];
                    },
                    getUrl:function (values) {
                        return Ext.bind(me.getUrl, me)(values);
                    },
                    joinStringArray:function (arr) {
                        return arr.join(', ');
                    },
                    getResultLinkCls:function () {
                        return 'result-target-link';
                    }
                }
            ],
            itemSelector: 'ul li.single-result-wrapper'
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.more-searchresults-button',
            click: this._onMore
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.result-target-link',
            click: this._onResultLinkClick
        });
        this.callParent(arguments);
    },

    _search:function (config) {
        this.getStore().search(Ext.apply({
            search: this.currentSearch
        }, config), {
            scope: this,
            callback:function (records, op) {
                if(op.success) {
                    this._onSearchSuccess();
                }
            }
        });
    },

    search:function (search) {
        this.show();
        this.currentSearch = search;
        this._search({
            limit: this.loadCountDefault
        });
    },

    _getElement:function (cssselector) {
        var morebutton = Ext.get(this.getEl().query(cssselector)[0]);
        morebutton.enableDisplayMode();
        return morebutton;
    },

    _getMoreButton:function () {
        return this._getElement('.more-searchresults-button');
    },

    _getNoResultsBox:function () {
        return this._getElement('.no-searchresults-box');
    },

    _onSearchSuccess:function () {
        var store = this.getStore();
        if(store.getCount() <= this.loadCountDefault && store.getTotalCount() > store.getCount()) {
            this._onMoreResultsAvailable();
        }
        if(store.getCount() === 0) {
            this._onNoSearchResults();
        }
    },

    _onMoreResultsAvailable:function () {
        var store = this.getStore();
        var morebutton = this._getMoreButton();
        var loadcount = Ext.Array.min([store.getTotalCount(), this.loadCountMax]);
        morebutton.setHTML(interpolate(gettext('Load %(loadcount)s more'), {
            loadcount: loadcount
        }, true));
        morebutton.show();
    },

    _onNoSearchResults:function () {
        var box = this._getNoResultsBox();
        box.setHTML(Ext.create('Ext.XTemplate', this.noResultsMsgTpl).apply({
            search: Ext.String.format('<em>{0}</em>', this.currentSearch)
        }));
        box.show();
    },

    _onMore:function (e) {
        e.preventDefault();
        this._search({
            limit: this.loadCountMax
        });
    },

    _renderResult:function (unused, unused2, record) {
        return this.resultTplCompiled.apply(record.data);
    },

    getUrl:function (values) {
        return '#';
    },

    _onResultLinkClick:function (e) {
        this.fireEvent('resultLinkClick');
        // NOTE: We do not prevent the default action, so this does not prevent the link from
        //       triggering navigation.
    }
});

Ext.define('devilry.extjshelpers.forms.Deadline', {
    extend: 'Ext.form.Panel',
    alias: 'widget.deadlineform',
    cls: 'widget-deadlineform',
    requires: [
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    flex: 6,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: "deadline",
        fieldLabel: 'Deadline',
        xtype: 'devilrydatetimefield',
        flex: 0,
        allowBlank: false
    }, {
        name: "text",
        fieldLabel: "Text",
        flex: 1,
        height: 250,
        xtype: 'textarea'
    }],


    help: [
        '<strong>Choose a deadline</strong>. Students will be able to deliver after the deadline expires, however deliveries after the deadline will be clearly marked.',
        'The <strong>text</strong> is displayed to students when they view the deadline, and when they add deliveries on the deadline. The text is shown exactly as you see it in the text-box. No formatting of any kind is applied.',
        '<strong>NOTE:</strong> Examiners can not move Deadlines. We are planning a major cleanup of the Examiner UI, which will include the ability to move deadlines. In the meantime, ask your course administrator to move deadlines if needed.'
    ]
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedAssignmentGroup', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "name"
        }, 
        {
            "type": "bool", 
            "name": "is_open"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "feedback"
        }, 
        {
            "type": "auto", 
            "name": "latest_delivery_id"
        }, 
        {
            "type": "auto", 
            "name": "latest_deadline_id"
        }, 
        {
            "type": "auto", 
            "name": "latest_deadline_deadline"
        }, 
        {
            "type": "auto", 
            "name": "number_of_deliveries"
        }, 
        {
            "type": "auto", 
            "name": "candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "bool", 
            "name": "parentnode__anonymous"
        }, 
        {
            "type": "int", 
            "name": "parentnode__delivery_types"
        }, 
        {
            "type": "date", 
            "name": "parentnode__publishing_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "feedback__points"
        }, 
        {
            "type": "auto", 
            "name": "feedback__grade"
        }, 
        {
            "type": "bool", 
            "name": "feedback__is_passing_grade"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__short_name"
        }, 
        {
            "type": "int", 
            "name": "feedback__delivery__number"
        }, 
        {
            "type": "date", 
            "name": "feedback__delivery__time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "feedback__delivery__delivery_type"
        }, 
        {
            "type": "auto", 
            "name": "feedback__delivery__deadline"
        }, 
        {
            "type": "auto", 
            "name": "candidates"
        }, 
        {
            "type": "auto", 
            "name": "feedback__rendered_view"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__parentnode__short_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedassignmentgroup/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["users", "assignment", "feedback", "period", "feedbackdelivery", "candidates", "feedback_rendered_view", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedSubject', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "auto", 
            "name": "admins__username"
        }, 
        {
            "type": "auto", 
            "name": "admins__email"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedsubject/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["admins"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.CreateNewDeadline', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            html: 'Click to create a new deadline for deliveries'
        });

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "relatedstudent"
        }, 
        {
            "type": "bool", 
            "name": "student_can_read"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "application"
        }, 
        {
            "type": "auto", 
            "name": "key"
        }, 
        {
            "type": "auto", 
            "name": "value"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedrelatedstudentkeyvalue/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry_header.store.StudentSearchResults', {
    extend: 'devilry_header.store.BaseSearchResults',
    model: 'devilry_header.model.StudentSearchResult'
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedStaticFeedback', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "grade"
        }, 
        {
            "type": "bool", 
            "name": "is_passing_grade"
        }, 
        {
            "type": "auto", 
            "name": "saved_by"
        }, 
        {
            "type": "date", 
            "name": "save_timestamp", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "delivery"
        }, 
        {
            "type": "auto", 
            "name": "rendered_view"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "date", 
            "name": "delivery__time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "delivery__number"
        }, 
        {
            "type": "auto", 
            "name": "delivery__delivered_by"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__name"
        }, 
        {
            "type": "int", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__id"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "delivery__deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifiedstaticfeedback/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment", "period", "delivery", "candidates", "assignment_group", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.extjshelpers.HelpWindow', {
    extend: 'devilry.extjshelpers.AutoSizedWindow',
    alias: 'widget.helpwindow',
    modal: true,
    layout: 'fit',
    width: 1000,
    height: 800,
    closable: false, // To easy to double click and close an undelying window

    helptpl: Ext.create('Ext.XTemplate', '<div class="section helpsection">{helptext}</div>'),
    helpdata: {},

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'box',
                cls: 'helpbox',
                autoScroll: true,
                html: this.helptpl.apply(Ext.apply(this.helpdata, {helptext:this.helptext}))
            },
            dockedItems: [{
                xtype: 'toolbar',
                ui: 'footer',
                dock: 'bottom',
                items: ['->', {
                    xtype: 'button',
                    text: 'Close help',
                    scale: 'large',
                    listeners: {
                        scope: this,
                        click: function() {
                            this.close();
                        }
                    }
                }, '->']
            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.extjshelpers.formfields.StoreSearchField', {
    extend: 'devilry.extjshelpers.SearchField',
    alias: 'widget.storesearchfield',
    requires: [
        'devilry.extjshelpers.SearchStringParser'
    ],

    /**
     * @cfg
     * An ``Ext.dat.Store``.
     */
    store: undefined,

    /**
     * @cfg
     * Forwarded to {@link devilry.extjshelpers.SearchStringParser#applyToExtraParams}.
     */
    shortcuts: undefined,

    /**
     * @cfg
     * Forwarded to SearchStringParser.
     */
    alwaysAppliedFilters: undefined,

    /**
     * @cfg {bool} [autoLoadStore]
     */
    autoLoadStore: true,

    /**
     * @cfg {int} [pageSize]
     */
    pageSize: 10,

    constructor: function(config) {
        this.callParent(arguments);
    },

    initComponent: function() {
        this.addListener('newSearchValue', this.onNewSearchValue, this);
        this.addListener('emptyInput', this.onEmptyInput, this);
        this.callParent(arguments);
        if(this.autoLoadStore) {
            this.onEmptyInput();
        };
    },

    onNewSearchValue: function(value) {
        var parsedValue = Ext.create('devilry.extjshelpers.SearchStringParser', {
            pageSizeWithoutType: this.pageSize,
            searchstring: value,
            alwaysAppliedFilters: this.alwaysAppliedFilters
        });

        parsedValue.applyPageSizeToStore(this.store);
        parsedValue.applyToExtraParams(this.store.proxy.extraParams, this.shortcuts);
        this.store.load();
    },

    refreshStore: function() {
        this.onNewSearchValue(this.getValue());
    },

    onEmptyInput: function() {
        this.onNewSearchValue('');
    }
});


/** Restful API for gradeeditor RegistryItems */
Ext.define('devilry.gradeeditors.RestfulRegistryItem', {
    extend: 'Ext.data.Model',

    fields: [
        {name: 'gradeeditorid', type: 'string'},
        {name: 'title', type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'config_editor_url', type: 'string'},
        {name: 'draft_editor_url', type: 'string'}
    ],

    proxy: {
        type: 'devilryrestproxy',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/gradeeditors/restfulgradeeditorconfig/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }
    }
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.student.simplified.SimplifiedDelivery', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "int", 
            "name": "number"
        }, 
        {
            "type": "date", 
            "name": "time_of_delivery", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline"
        }, 
        {
            "type": "bool", 
            "name": "successful"
        }, 
        {
            "type": "int", 
            "name": "delivery_type"
        }, 
        {
            "type": "auto", 
            "name": "alias_delivery"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode"
        }, 
        {
            "type": "int", 
            "name": "deadline__assignment_group__parentnode__delivery_types"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode"
        }, 
        {
            "type": "date", 
            "name": "deadline__assignment_group__parentnode__parentnode__start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "deadline__assignment_group__parentnode__parentnode__end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "delivered_by__identifier"
        }, 
        {
            "type": "date", 
            "name": "deadline__deadline", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__candidates__identifier"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "deadline__assignment_group__parentnode__parentnode__parentnode__long_name"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/student/restfulsimplifieddelivery/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["assignment_group_users", "assignment", "period", "delivered_by", "deadline", "assignment_group", "candidates", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedAssignment', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "deadline_handling"
        }, 
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "parentnode"
        }, 
        {
            "type": "auto", 
            "name": "short_name"
        }, 
        {
            "type": "auto", 
            "name": "long_name"
        }, 
        {
            "type": "date", 
            "name": "publishing_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "int", 
            "name": "delivery_types"
        }, 
        {
            "type": "bool", 
            "name": "anonymous"
        }, 
        {
            "type": "int", 
            "name": "scale_points_percent"
        }, 
        {
            "type": "auto", 
            "name": "admins__username"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__long_name"
        }, 
        {
            "type": "date", 
            "name": "parentnode__start_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "date", 
            "name": "parentnode__end_time", 
            "dateFormat": "Y-m-d\\TH:i:s"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__short_name"
        }, 
        {
            "type": "auto", 
            "name": "parentnode__parentnode__long_name"
        }, 
        {
            "type": "auto", 
            "name": "fake_admins"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedassignment/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '["admins", "period", "subject"]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry.gradeeditors.GradeEditorModel', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'gradeeditorid',
        type: 'string'
    }, {
        name: 'title',
        type: 'string'
    }, {
        name: 'description',
        type: 'string'
    }],

    idProperty: 'gradeeditorid',

    proxy: {
        type: 'devilryrestproxy',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/gradeeditors/restfulgradeeditorconfig/',
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }
    }
});


Ext.define('devilry.gradeeditors.GradeEditorSelector', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.gradeeditorselector',
    cls: 'widget-gradeeditorselector',
    requires: ['devilry.gradeeditors.GradeEditorModel'],

    valueField: 'gradeeditorid',
    displayField: 'title',
    queryMode: 'local',
    editable: false,

    listConfig: {
        getInnerTpl: function() {
            return '<div class="section gradeeditorselector"><div class="important">{title}</div><div class="unimportant">{description}</div></div>';
        }
    },


    initComponent: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.gradeeditors.GradeEditorModel',
            autoSync: true
        });
        this.addListener('render', this._onRender, this);
        this.callParent(arguments);
    },

    _onRender: function() {
        try {
            this.setLoading(gettext('Loading'));
            this._loadStore();
        } catch(e) {
            Ext.defer(function() {
                this.setLoading(gettext('Loading'));
                this._loadStore();
            }, 500, this)
        }
    },

    _loadStore: function() {
        this.store.load({
            scope: this,
            callback: function(records, op, success) {
                if(success) {
                    this.onLoadSuccess(records);
                } else {
                    this.onLoadFailure(records);
                }
            }
        });
    },

    onLoadSuccess: function(records) {
        this.setLoading(false);
        this.setValue(this.value);
    },

    onLoadFailure: function() {
        this.setLoading(false);
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: 'Failed to load records',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.AboutTheDelivery', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            html: 'Click to get more info about the delivery'
        });

Ext.define('devilry.administrator.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.administrator.models.Deadline',
    hasMany: {
        model: 'devilry.administrator.models.StaticFeedback',
        name: 'staticfeedbacks',
        foreignKey: 'delivery'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifieddelivery/'
    })
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.administrator.simplified.SimplifiedRelatedStudent', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "int", 
            "name": "id"
        }, 
        {
            "type": "auto", 
            "name": "period"
        }, 
        {
            "type": "auto", 
            "name": "user"
        }, 
        {
            "type": "auto", 
            "name": "tags"
        }, 
        {
            "type": "auto", 
            "name": "user__username"
        }, 
        {
            "type": "auto", 
            "name": "user__devilryuserprofile__full_name"
        }, 
        {
            "type": "auto", 
            "name": "user__email"
        }, 
        {
            "type": "auto", 
            "name": "candidate_id"
        }
    ],
    idProperty: 'id',
    proxy: {
        type: 'devilryrestproxy',
        url: '/administrator/restfulsimplifiedrelatedstudent/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry_header.ExaminerSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_examinersearchresults',
    extraCls: 'devilry_header_examinersearchresults',

    singleResultTpl: [
        '<div>',
            '<a href="{[this.getUrl(values)]}" class="{[this.getResultLinkCls()]}">{title}</a>',
            ' <span class="label label-inverse typename">{[this.getTypeName(values.type)]}</span>',
        '</div>',
        '<div class="meta path">{path}</div>',
        '<tpl if="type == \'core_assignmentgroup\'">',
            '<div class="meta students">',
                '{[this.joinStringArray(values.students)]}',
            '</small></div>',
        '</tpl>'
    ],

    heading: gettext('Content where you are examiner'),

    getUrl:function (values) {
        var prefix = Ext.String.format('{0}/examiner/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        if(values.type === 'core_assignmentgroup') {
            return Ext.String.format('{0}assignmentgroup/{1}',
                prefix, values.id);
        } else if(values.type === 'core_assignment') {
            return Ext.String.format('{0}assignment/{1}',
                prefix, values.id);
        } else {
            throw Ext.String.format('Unknown type: {0}', values.type);
        }
    }
});

/**
A container of AlerMessages. This container is perfect for top-of-form
messages. It defaults to beeing hidden. When you add a message it
becomes invisible, and when you remove all messages, it hides itself
automatically.
*/ 
Ext.define('devilry_extjsextras.AlertMessageList', {
    extend: 'Ext.panel.Panel',
    requires: [
        'devilry_extjsextras.AlertMessage'
    ],
    alias: 'widget.alertmessagelist',
    hidden: true,
    frame: false,
    border: false,
    bodyStyle: 'background-color: transparent !important;',

    layout: 'anchor',

    initComponent: function() {
        if(Ext.isEmpty(this.cls)) {
            this.cls = [];
        } else {
            this.cls = Ext.toArray();
        }
        this.cls.push('devilry_extjsextras_alertmessagelist');
        this.on('remove', this._onRemove, this);
        this.callParent(arguments);
        this.addListener({
            scope: this,
            closed: this.onClose
        });
    },

    onClose: function(alertmessage) {
        this.remove(alertmessage, true);
    },

    /** Create and add a ``devilry_extjsextras.AlertMessage``. The config parameter is
     * forwarded to the AlertMessage constructor. */
    add: function(config) {
        var messageConfig = {};
        Ext.apply(messageConfig, this.messageDefaults);
        Ext.apply(messageConfig, config);
        var message = Ext.widget('alertmessage', messageConfig);
        this.callParent([message]);
        message.enableBubble('closed');
        this.show();
    },
    
    _onRemove: function() {
        var messages = this.query('alertmessage');
        if(messages.length === 0) {
            this.hide();
        }
    },

    /** Add many messages of the same type.
     *
     * @param messages Array of messages (strings).
     * @param type The type of the message (see ``devilry_extjsextras.AlertMessage.type``).
     * */
    addMany: function(messages, type) {
        Ext.Array.each(messages, function(message) {
            this.add({
                message: message,
                type: type
            });
        }, this);
    },

    /** Add many messages by array.
     *
     * Functionally the same as looping over ``configs``, and calling ``add()``
     * for each config.
     *
     * @param configs Array of configuration objects for ``add()``.
     * */
    addArray: function(configs) {
        Ext.Array.each(configs, function(config) {
            this.add(config);
        }, this);
    }
});


Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.SortFullNameByGlobalPolicyColumn',
        'Ext.ux.grid.Printer',
        'devilry.extjshelpers.GridPrintButton'
    ],

    labelTpl: Ext.create('Ext.XTemplate',
        '<ul class="labels-list">',
        '    <tpl for="labels">',
        '       <li class="label-{label}">{label}</li>',
        '    </tpl>',
        '</ul>'
    ),

    getGridColumns: function() {
        var me = this;
        var gridColumns = [{
            header: 'Username', dataIndex: 'username',
            menuDisabled: true,
            width: 100,
            locked: true
        }, {
            xtype: 'sortfullnamebyglobalpolicycolumn',
            menuDisabled: true,
            header: 'Full name', dataIndex: 'full_name',
            minWidth: 140,
            flex: 2
        }, {
            header: 'Labels', dataIndex: 'labelsSortKey',
            menuDisabled: true,
            width: 150,
            renderer: function(labels, p, record) {
                return me.labelTpl.apply(record.data);
            }
        }];
        return gridColumns;
    },

    refresh: function() {
        this.loadData();
    },

    loadData: function() {
        this.refreshView();
    },

    createGrid: function(extraOpts) {
        var gridColumns = this.getGridColumns();
        var gridOpts = Ext.apply({
            multiSelect: true,
            autoScroll: true,
            store: this.loader.store,
            columns: gridColumns,
            bbar: [{
                xtype: 'gridprintbutton',
                listeners: {
                    scope: this,
                    print: this._onPrint,
                    printformat: this._onPrintFormat
                }
            }, '->', {
                xtype: 'tbtext',
                text: this._getTbText()
            }]
        });
        if(extraOpts) {
            Ext.apply(gridOpts, extraOpts);
        }
        this.mon(this.loader, 'filterCleared', this._onFilterChange, this);
        this.mon(this.loader, 'filterApplied', this._onFilterChange, this);
        this.grid = Ext.widget('grid', gridOpts);
        return this.grid;
    },

    _getTbText: function() {
        return Ext.create('Ext.XTemplate', 
            'Showing {visible} of {total} students'
        ).apply({
            total: this.loader.totalStudents,
            visible: this.loader.store.data.items.length
        });
    },

    _onFilterChange: function() {
        this.down('tbtext').setText(this._getTbText());
    },

    createLayout: function() {
        this.add(this.createGrid());
    },

    refreshView: function() {
        this.removeAll();
        this.createLayout();
    },

    getSelectedStudents: function() {
        return this.down('grid').getSelectionModel().getSelection();
    },

    _onPrint: function() {
        Ext.ux.grid.Printer.print(this.grid, true);
    },

    _onPrintFormat: function() {
        Ext.ux.grid.Printer.print(this.grid, false);
    }
});


Ext.define('devilry.administrator.node.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_nodeprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section help">',
        '    <h1>What is a node?</h1>',
        '    <p>',
        '        A Node is a place to organise top-level administrators (administrators responsible for more than one subject).',
        '        Nodes are organised in a tree. This is very flexible, and can be used to emulate most administrative hierarchies.',
        '    </p>',
        '   <h1>Usage</h1>',
        '   <p>Use the <span class="menuref">Active periods/semesters</span> to get an overview over the currently running periods, and if the administrators have registered which students qualify for final exams.</p>',
        '   <p>The <span class="menuref">Direct childnodes</span> and <span class="menuref">Subjects</span> tabs are lists of everything organized directly below this node.</p>',
        '</div>'
    ),

    initComponent: function() {
        if(this.record) {
            this._onLoadRecord();
        } else {
            this.on('loadmodel', this._onLoadRecord, this);
        }
        this.callParent(arguments);
    },

    _onLoadRecord: function() {
    }
});


/** Layout for restful simplified editors.
 *
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.administratorrestfulsimplifiedlayout',
    requires: [
        'devilry.extjshelpers.ErrorList',
        'devilry.extjshelpers.RestSubmit'
    ],
    border: 0,

    config: {
        /**
         * @cfg
         * Items for the ``Ext.form.Panel`` used to edit the RestfulSimplified object. (Required).
         */
        editformitems: undefined,

        /**
         * @cfg
         * ``Ext.data.Model`` for the RestfulSimplified object. (Required).
         */
        model: undefined,

        /**
         * @cfg
         * Does the RestfulSimplified support delete? (Required).
         */
        supports_delete: undefined,

        /**
         * @cfg
         * List of foreign key field names in the model. (Required).
         */
        foreignkeyfieldnames: undefined
    },

    bodyStyle: {
        'background-color': 'transparent'
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;
        
        var savebuttonargs = {
            xtype: 'button',
            text: 'Save',
            scale: 'large',
            iconCls: 'icon-save-32',
            handler: function() {
                me.errorlist.clearErrors();
                me.editform.getForm().doAction('devilryrestsubmit', {
                    submitEmptyText: true,
                    waitMsg: 'Saving item...',
                    success: function(form, action) {
                        var record = action.record;
                        me.editform.loadRecord(record); // Need to load the record. If not, the proxy will do a POST instead of PUT on next save.
                        me.readonly();
                    },
                    failure: function(form, action) {
                        var errormessages = action.operation.responseData.items.errormessages;
                        Ext.each(errormessages, function(errormessage) {
                            me.errorlist.addError(errormessage);
                        });
                    }
                });
            }
        };

        var deletebuttonargs = {
            xtype: 'button',
            text: 'Delete',
            flex: 0,
            hidden: !this.supports_delete,
            scale: 'large',
            iconCls: 'icon-delete-32',
            handler: function() {
                Ext.MessageBox.show({
                    title: 'Confirm delete',
                    msg: 'Are you sure you want to delete?',
                    animateTarget: this,
                    buttons: Ext.Msg.YESNO,
                    icon: Ext.Msg.ERROR,
                    fn: function(btn) {
                        if(btn == 'yes') {
                            me.deleteCurrent();
                        }
                    }
                });
            }
        };

        var clicktoeditbuttonargs = {
            xtype: 'button',
            text: 'Click to edit',
            scale: 'large',
            iconCls: 'icon-edit-32',
            listeners: {
                click: function(button, pressed) {
                    me.editable();
                    //me.errorlist.addError('Hello world');
                    //me.errorlist.addError('This is a long error message. Message message message message message message message message message message message message message message message message message message message message message message message message message message message message.');
                }
            }
        };

        this.overlayBar = Ext.create('Ext.container.Container', {
            floating: true,
            cls: 'form-overlay-bar',
            height: 40,
            width: 300,
            layout: {
                type: 'hbox',
                align: 'stretch',
                pack: 'end'
            },
            items: [
                deletebuttonargs,
                {xtype: 'component', width: 10},
                clicktoeditbuttonargs
            ]
        });


        this.errorlist = Ext.create('devilry.extjshelpers.ErrorList', {});

        var editformargs = {
            id: me.getChildIdBySuffix('editform'),
            xtype: 'form',
            model: this.model,
            items: this.editformitems,

            // Fields will be arranged vertically, stretched to full width
            layout: 'anchor',
            defaults: {
                anchor: '100%',
            },

            cls: 'editform',
            bodyCls: 'editform-body',

            // Disable by default
            disabled: true,

            // Only save button. Other buttons are in overlayBar
            buttons: [
                savebuttonargs
            ]
        };


        Ext.apply(this, {
            items: [
                this.errorlist,
                editformargs
            ],
            layout: 'fit'
        });
        this.callParent(arguments);

        this.editform = Ext.getCmp(editformargs.id);
    },

    deleteCurrent: function() {
        this.editform.getForm().doAction('devilryrestsubmit', {
            submitEmptyText: true,
            method: 'DELETE',
            waitMsg: 'Deleting item...',
            success: function() {
            }
        });
    },

    getChildIdBySuffix: function(idsuffix) {
        return this.id + '-' + idsuffix;
    },


    /** Load the request record into the form. */
    loadRecordFromStore: function (record_id) {
        var me = this;
        Ext.ModelManager.getModel(this.model).load(record_id, {
            success: function(record) {
                me.editform.loadRecord(record);
                var fields = me.editform.getForm().getFields();
                Ext.each(me.foreignkeyfieldnames, function(fieldname) {
                    var field = fields.filter('name', fieldname).items[0];
                    field.store.load(function(store, records, successful) {
                        field.setValue(record.data[fieldname]);
                    });
                });
            }
        });
    },

    getFormButtonBar: function() {
        return this.editform.dockedItems.items[0];
    },

    readonly: function() {
        this.editform.disable();
        this.overlayBar.show();
        this.overlayBar.alignTo(this.editform, 'tr-tr');
        this.getFormButtonBar().hide();
    },
    editable: function() {
        this.editform.enable();
        this.overlayBar.hide();
        this.getFormButtonBar().show();
    },

    loadUpdateMode: function(record_id) {
        this.loadRecordFromStore(record_id);
        this.readonly();
    },
    loadCreateMode: function() {
        this.getFormButtonBar().hide(); // NOTE: This is required for some reason?
        this.editable();
    },
    loadMode: function(mode, record_id) {
        if(mode == "update") {
            this.loadUpdateMode(record_id);
        } else if(mode == "create") {
            this.loadCreateMode();
        }
    }
});


Ext.define('devilry.extjshelpers.ActivePeriodsGrid', {
    extend: 'devilry.extjshelpers.DashGrid',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],

    config: {
        model: undefined,
        noRecordsMessage: {
            title: interpolate(gettext('No active %(periods_term)s'), {
                periods_term: gettext('periods')
            }, true),
            msg: interpolate(gettext('You are not registered on any active %(periods_term)s.'), {
                periods_term: gettext('periods')
            }, true)
        },
        pageSize: 30,
        dashboard_url: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-publishing_time']);
        this.store.pageSize = this.pageSize
    },

    createBody: function() {
        var colTpl = Ext.create('Ext.XTemplate',
            '<a href="{dashboard_url}period/{data.id}">',
                '{data.parentnode__short_name} - {data.long_name}',
            '</a>'
        );
        var me = this;
        var activePeriodsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            frameHeader: false,
            border: false,
            cls: 'bootstrap',
            sortableColumns: false,
            autoScroll: true,
            store: this.store,
            hideHeaders: true,
            flex: 1,
            columns: [{
                text: 'unused',
                menuDisabled: true,
                dataIndex: 'id',
                flex: 1,
                renderer: function(unused, unused2, periodRecord) {
                    return colTpl.apply({
                        data: periodRecord.data,
                        dashboard_url: me.dashboard_url
                    });
                }
            }]
            //listeners: {
                //scope: this,
                //itemmouseup: function(view, record) {
                    //var url = this.dashboard_url + "period/" + record.data.id
                    //window.location = url;
                //}
            //}
        });
        this.add({
            xtype: 'box',
            html: Ext.String.format('<div class="section"><h2>{0}</h2></div>',
                interpolate(gettext('Active %(periods_term)s'), {
                    periods_term: gettext('periods')
                }, true)
            )
        });
        this.add(activePeriodsGrid);
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],
    autoScroll: true,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-chooseassignmentsgrid',
                margin: '0 0 10 0',
                selectedAssignmentIds: this.settings? this.settings.assignment_ids: undefined,
                store: this.loader.assignment_store
            }, {
                xtype: 'numberfield',
                fieldLabel: 'Minumum total points on selected',
                minValue: 0,
                value: this.settings? this.settings.minimumScaledPoints: '',
                margin: '0 0 10 0'
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    _getGrid: function() {
        return this.down('statistics-chooseassignmentsgrid');
    },


    filter: function(student) {
        var assignment_ids = this.down('statistics-chooseassignmentsgrid').getIdOfSelected();
        var minimumScaledPoints = this.down('numberfield').getValue();
        return student.hasMinimalNumberOfScaledPointsOn(assignment_ids, minimumScaledPoints);
    },

    validInput: function() {
        return this.validPointInput() && this.down('statistics-chooseassignmentsgrid').checkAtLeastOneSelected();
    },

    getSettings: function() {
        var settings = this.callParent(arguments);
        settings.assignment_ids = this._getGrid().getIdOfSelected();
        return settings;
    }
});


/** AssignmentGroup details panel.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupDetails', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgroupdetails',
    cls: 'widget-assignmentgroupdetails',

    tpl: Ext.create('Ext.XTemplate',
        // TODO !is_open without any published feedback and perhaps with failing grade?
        '<tpl if="canExamine">',
        '    <tpl if="is_open">',
        '        <div class="section info-small">',
        '           <h1>Open</h1>',
        '           <p>This group is <em>open</em>. A group should remain open until you have finished grading them, and Devilry normally opens and closes groups for you automatically. You may want to manually close a group, using <span class="menuref">Close group</span> in the toolbar, if you want to make the current grade their final grade on this assignment. A closed group can be re-opened at any time.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="!is_open">',
        '        <div class="section ok-small">',
        '           <h1>Closed</h1>',
        '           <p>This group is <em>closed</em>. This means that a group has been corrected and given feedback. If the group has not been given feedback, a closed group signals that this group will not get any correction on this assignment. A closed group can be re-opened at any time using <span class="menuref">Open group</span> in the toolbar.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="numDeliveries == 0">',
        '        <div class="section warning-small">',
        '           <h1>No deliveries</h1>',
        '           <p>This group has no deliveries.</p>',
        '        </div>',
        '    </tpl>',
        '</tpl>',
        '<tpl if="!canExamine">',
        '    <tpl if="is_open">',
        '        <div class="section info-small">',
        '           <h1>Open</h1>',
        '           <p>This assignment is open for more deliveries. You can add as many deliveries as you like, and your examiner(s) will normally correct your latest delivery.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="!is_open">',
        '        <div class="section ok-small">',
        '           <h1>Closed</h1>',
        '           <p>This assignment is <em>closed</em>. This usually means that you have been given feedback, and that the latest feedback is your final grade on this assignment. If you have not been given feedback, and you think this is wrong, you should contact your examiner or course administrator.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="numDeliveries == 0">',
        '        <div class="section warning-small">',
        '           <h1>No deliveries</h1>',
        '           <p>You have no deliveries on this assignment.</p>',
        '        </div>',
        '    </tpl>',
        '</tpl>'
    ),

    initComponent: function() {
        Ext.apply(this, {
            
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-listofassignments',
    hideHeaders: true,

    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],

    recordTpl: Ext.create('Ext.XTemplate',
        '<tpl if="assignmentRecords.length &gt; 1">',
        '    {prefix}',
        '    <tpl for="assignmentRecords">',
        '        {data.short_name}<tpl if="xindex &lt; xcount">{parent.splitter}</tpl>',
        '    </tpl>',
        '</tpl>',
        '<tpl if="assignmentRecords.length == 1">',
        '    <tpl for="assignmentRecords">',
        '        {data.short_name}',
        '    </tpl>',
        '</tpl>'
    ),

    config: {
        rowPrefix: '',
        rowSplitter: ' OR ',
        assignment_store: undefined,
        selected_assignments: undefined
    },

    constructor: function(config) {
        this.store = Ext.create('Ext.data.ArrayStore', {
            autoDestroy: true,
            idIndex: 0,
            fields: ['assignmentIds']
        });

        this.callParent([config]);
        this.initConfig(config);
        if(this.selected_assignments) {
            Ext.each(this.selected_assignments, function(assignmentIds, index) {
                this.store.add({
                    assignmentIds: assignmentIds
                });
            }, this);
        }
    },

    initComponent: function() {
        //this.store.add([{
            //assignmentIds: [1, 3]
        //}, {
            //assignmentIds: [2]
        //}])

        Ext.apply(this, {
            columns: [{
                header: 'Assignments', dataIndex: 'assignmentIds', flex: 1,
                renderer: function(assignmentIds, p, record) {
                    return this.recordTpl.apply({
                        assignmentRecords: this._getAssignmentRecordsFromIds(assignmentIds),
                        prefix: this.rowPrefix,
                        splitter: this.rowSplitter
                    });
                }
            }],
            tbar: [this.removeButton = Ext.widget('button', {
                text: 'Remove',
                iconCls: 'icon-delete-16',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onClickDelete
                }
            }), {
                xtype: 'button',
                text: 'Add',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this._onClickAdd
                }
            }]
        });
        this.on('selectionchange', this._onSelectionChange, this);
        this.callParent(arguments);
    },

    _onSelectionChange: function(grid, selected) {
        if(selected.length === 0) {
            this.removeButton.disable();
        } else {
            this.removeButton.enable();
        }
    },

    _onClickDelete: function() {
        var selected = this.getSelectionModel().getSelection();
        if(selected.length != 1) {
            Ext.MessageBox.alert('Error', 'Please select a row from the list.');
            return;
        }
        var selectedItem = selected[0];
        this.store.remove(selectedItem);
    },

    _onClickAdd: function() {
        var me = this;
        Ext.widget('window', {
            layout: 'fit',
            title: 'Select one or more assignment(s)',
            width: 500,
            height: 350,
            modal: true,
            items: {
                xtype: 'statistics-chooseassignmentsgrid',
                hideHeaders: true,
                store: this.assignment_store
            },
            bbar: ['->', {
                xtype: 'button',
                text: 'Add assignment(s)',
                scale: 'large',
                iconCls: 'icon-add-32',
                listeners: {
                    scope: this,
                    click: this._onAdd
                }
            }]
        }).show();
    },

    _onAdd: function(button) {
        var win = button.up('window');
        var grid = win.down('statistics-chooseassignmentsgrid');
        if(grid.checkAtLeastOneSelected()) {
            win.close();
            var assignmentIds = grid.getIdOfSelected();
            this._addToStore(assignmentIds);
        }
    },

    _parseAssignmentSpec: function(assignmentShortNames) {
        return assignmentShortNames.split(/\s*,\s*/);
    },

    _addToStore: function(assignmentIds) {
        this.store.add({
            assignmentIds: assignmentIds
        });
    },

    _getAssignmentRecordsFromIds: function(assignmentIds) {
        var assignmentRecords = [];
        Ext.each(assignmentIds, function(assignmentId, index) {
            var assignmentRecordIndex = this.assignment_store.findExact('id', assignmentId);
            var assignmentRecord = this.assignment_store.getAt(assignmentRecordIndex);
            assignmentRecords.push(assignmentRecord);
        }, this);
        return assignmentRecords;
    },

    getArrayOfAssignmentIds: function() {
        var ids = [];
        Ext.each(this.store.data.items, function(record, index) {
            ids.push(record.get('assignmentIds'));
        }, this);
        return ids;
    }
});


Ext.define('devilry.student.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.student.models.Deadline',
    hasMany: {
        model: 'devilry.student.models.StaticFeedback',
        name: 'staticfeedbacks',
        foreignKey: 'delivery'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/student/restfulsimplifieddelivery/'
    })
});


Ext.define('devilry.extjshelpers.RestFactory', {
    requires: [
        'devilry.extjshelpers.Store',
        'devilry.extjshelpers.RestProxy'
    ],
    statics: {
        createProxy: function(role, name_lower) {
            return Ext.create('devilry.extjshelpers.RestProxy', {
                url: Ext.String.format('/{0}/restfulsimplified{1}/', role, name_lower)
            });
        },

        getModelName: function(role, name) {
            return Ext.String.format('devilry.{0}.models.{1}', role, name);
        },

        getModel: function(role, name) {
            return Ext.ModelManager.getModel(devilry.extjshelpers.RestFactory.getModelName(role, name));
        },

        createStore: function(role, name, config) {
            var args = {
                model: devilry.extjshelpers.RestFactory.getModelName(role, name)
            };
            Ext.apply(args, config);
            return Ext.create('devilry.extjshelpers.Store', args);
        }
    }
});


Ext.define('devilry.student.models.Deadline', {
    extend: 'devilry.extjshelpers.models.Deadline',
    hasMany: {
        model: 'devilry.student.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/student/restfulsimplifieddeadline/'
    })
});


Ext.define('devilry.examiner.RecentDeliveriesView', {
    extend: 'devilry.extjshelpers.DashGrid',
    alias: 'widget.examiner_recentdeliveriesview',
    requires: [
        'devilry.extjshelpers.DateTime'
    ],


    /**
     * @cfg {Object} [model]
     */

    /**
     * @cfg {int} [limit]
     */
    limit: 4,
    
    /**
     * @cfg {bool} [showStudentsCol]
     */
    showStudentsCol: true,

    /**
     * @cfg {Object} [noRecordsMessage]
     */
    noRecordsMessage: {
        title: interpolate(gettext('No recent %(deliveries_term)s'), {
            deliveries_term: gettext('deliveries')
        }, true),
        msg: interpolate(gettext("You are not registered on any %(groups_term)s with recent %(deliveries_term)s."), {
            groups_term: gettext('groups'),
            deliveries_term: gettext('deliveries')
        }, true)
    },

    /**
     * @cfg {Function} [urlCreateFn]
     * Function to call to genereate urls. Takes a record of the given
     * ``model`` as argument.
     */

    /**
     * @cfg {Object} [urlCreateFnScope]
     * Scope of ``urlCreateFn``.
     */


    studentsRowTpl: Ext.create('Ext.XTemplate',
        '<ul class="commaSeparatedList"  style="margin: 0;">',
        '   <tpl for="deadline__assignment_group__candidates__identifier">',
        '       <li>{.}</li>',
        '   </tpl>',
        '</ul>'
    ),

    assignmentRowTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">',
            '{data.deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
            '{data.deadline__assignment_group__parentnode__parentnode__short_name}.',
            '{data.deadline__assignment_group__parentnode__short_name}',
        '</a>'
    ),

    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            groupField: 'deadline__assignment_group__parentnode__parentnode__parentnode__short_name',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'deadline__assignment_group__parentnode__parentnode__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'deadline__assignment_group__parentnode__parentnode__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'delivery_type',
            comp: 'exact',
            value: 0
        }]);
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-time_of_delivery']);
        this.store.pageSize = this.limit;
    },

    createBody: function() {
        var me = this;

        var urlCreateFunction = Ext.bind(this.urlCreateFn, this.urlCreateFnScope);
        var columns = [{
            text: 'Assignment',
            menuDisabled: true,
            flex: 18,
            dataIndex: 'deadline__assignment_group__parentnode__long_name',
            renderer: function(value, meta, record) {
                return me.assignmentRowTpl.apply({
                    data: record.data,
                    url: urlCreateFunction(record)
                });
            }
        }, {
            text: 'Time of delivery',
            menuDisabled: true,
            width: 130,
            dataIndex: 'time_of_delivery',
            renderer: function(value) {
                var rowTpl = Ext.create('Ext.XTemplate',
                    '{.:date}'
                );
                return rowTpl.apply(value);
            }
        }];

        if(this.showStudentsCol) {
            Ext.Array.insert(columns, 1, [{
                text: 'Students',
                menuDisabled: true,
                dataIndex: 'id',
                flex: 20,
                renderer: function(value, meta, record) {
                    return me.studentsRowTpl.apply(record.data);
                }
            }]);
        }



        var activeAssignmentsGrid = Ext.create('Ext.grid.Panel', {
            frame: false,
            cls: 'bootstrap',
            hideHeaders: true,
            frameHeader: false,
            disableSelection: true,
            border: false,
            sortableColumns: false,
            autoScroll: true,
            flex: 1,
            store: this.store,
            columns: columns
        });
        this.add({
            xtype: 'box',
            cls: 'bootstrap',
            tpl: '<div class="section"><h3>{text}</h3></div>',
            data: {
                text: interpolate(gettext('Recent %(deliveries)s'), {
                    deliveries: gettext('deliveries')
                }, true)
            }
        });
        this.add(activeAssignmentsGrid);
    }
});


Ext.define('devilry_extjsextras.NextButton', {
    extend: 'devilry_extjsextras.PrimaryButton',
    alias: 'widget.nextbutton',
    cls: 'devilry_extjsextras_nextbutton',
    text: pgettext('uibutton', 'Next')
});


// Autogenerated by the dev_coreextjsmodels script. DO NOT CHANGE MANUALLY

/*******************************************************************************
 * NOTE: You will need to add the following before your application code:
 *
 *    Ext.Loader.setConfig({
 *        enabled: true,
 *        paths: {
 *            'devilry': DevilrySettings.DEVILRY_STATIC_URL + '/extjs_classes'
 *        }
 *    });
 *    Ext.syncRequire('devilry.extjshelpers.RestProxy');
 ******************************************************************************/
Ext.define('devilry.apps.gradeeditors.simplified.examiner.SimplifiedConfig', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],
    fields: [
        {
            "type": "auto", 
            "name": "gradeeditorid"
        }, 
        {
            "type": "auto", 
            "name": "assignment"
        }, 
        {
            "type": "auto", 
            "name": "config"
        }
    ],
    idProperty: 'assignment',
    proxy: {
        type: 'devilryrestproxy',
        url: '/gradeeditors/examiner/restfulsimplifiedconfig/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        extraParams: {
            getdata_in_qrystring: true,
            result_fieldgroups: '[]'
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        },
        writer: {
            type: 'json'
        }
    }
});

Ext.define('devilry_extjsextras.form.TimeField', {
    extend: 'Ext.form.field.Time',
    alias: 'widget.devilry_extjsextras_timefield',
    cls: 'devilry_extjsextras_timefield',
    format: pgettext('extjs time input format', 'H:i'),
    increment: 30,
    requires: [
        'devilry_extjsextras.form.TimeFieldPicker'
    ],

    createPicker: function() {
        var picker;
        this.listConfig = Ext.apply({
            xtype: 'devilry_extjsextras_timefieldpicker',
            selModel: {
                mode: 'SINGLE'
            },
            cls: undefined,
            minValue: this.minValue,
            maxValue: this.maxValue,
            increment: this.increment,
            format: this.format,
            maxHeight: this.pickerMaxHeight
        }, this.listConfig);
        picker = this.callParent();
        this.store = picker.store;
        return picker;
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            html: 'Click to get to the previous feedback'
        });

Ext.define('devilry.examiner.models.Deadline', {
    extend: 'devilry.extjshelpers.models.Deadline',
    hasMany: {
        model: 'devilry.examiner.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/examiner/restfulsimplifieddeadline/'
    })
});


Ext.define('devilry_authenticateduserinfo.UserInfo', {
    singleton: true,
    requires: [
        'devilry_authenticateduserinfo.UserInfoModel'
    ],

    waitingForLoad: [],
    userInfoRecord: null,

    /**
     * Load UserInfo if required, or use the cached record.
     *
     * The first time this is called, the UserInfoModel is loaded.
     * While it is loading, callback functions are queued, and all
     * functions in the queue is called when the record is loaded.
     *
     * If the UserInfo record is already loaded, the callback function is
     * called at once.
     *
     * @param {Function} [fn=undefined]:
     *      Optional callback function. Called with the UserInfo record as
     *      first and only argument.
     * @param {Object} [scope=undefined]:
     *      Optional scope for ``fn``.
     */
    load: function(fn, scope) {
        if(this.userInfoRecord) {
            Ext.callback(fn, scope, [this.userInfoRecord]);
        } else {
            if(fn) {
                this.waitingForLoad.push({
                    fn: fn,
                    scope: scope
                });
            }
            if(this.loading) {
                return;
            }
            this.loading = true;
            devilry_authenticateduserinfo.UserInfoModel.load(null, {
                scope: this,
                success: function(record) {
                    this.userInfoRecord = record;
                    this.loading = false;
                    this._handleWaiting();
                },
                failure: this._onFailure
            });
        }
    },

    _handleWaiting: function() {
        Ext.Array.each(this.waitingForLoad, function(config) {
            Ext.callback(config.fn, config.scope, [this.userInfoRecord]);
        }, this);
        this.waitingForLoad = [];
    },

    _onFailure: function(unused, operation) {
        this.loading = false;
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: gettext('Failed to load infomation about the authenticated user. Try to reload the page.'),
            icon: Ext.MessageBox.ERROR
        });
    }
});


Ext.define('devilry.extjshelpers.RestfulSimplifiedEditPanelBase', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.restfulsimplified_editpanel_base',
    requires: ['devilry.extjshelpers.RestSubmit'],

    /**
     * @cfg
     * The model we are editing.
     */
    model: undefined,

    /**
     * @cfg
     * A instance of the ``Ext.data.Model`` which should be loaded into the
     * form.
     */
    record: undefined,

    /**
     * @cfg
     * Show the extra-bar (sidebar) at the bottom? Defaults to ``false``,
     * which means that it will be at the right hand side. This bar contains
     * help and error messages.
     */
    extrabaronbottom: false,


    autoScroll: true,


    cls: 'editform',
    bodyCls: 'editform-body',

    constructor: function(config) {
        this.addEvents(
            /**
             * Fired when save is clicked. This may be when the record have been
             * saved successfully, or when the save button has been clicked
             * depending on the subclass.  By default this is fired when the save
             * button in clicked.
             */
            'saveSuccess'
        );

        this.callParent(arguments);
    },

    initComponent: function() {
        this.errorlist = Ext.create('devilry.extjshelpers.ErrorList');
        this.model = Ext.ModelManager.getModel(this.model);

        this.editform.frame = false;
        if(this.editform.flex === undefined) {
            this.editform.flex = 15;
        }
        this.editform.border = 0;

        var extrabarCssCls = this.extrabaronbottom? 'extrabaronbottom': 'extrabaronright';
        var helpwidth;
        if(!this.extrabaronbottom) {
            this.layout = 'column';
            helpwidth = 300;
        }

        this.editform.columnWidth = 1;
        Ext.apply(this, {
            items: [this.editform, {
                xtype: 'panel',
                frame: false,
                //autoScroll: true,
                border: false,
                width: helpwidth,
                bodyCls: 'editform-sidebar ' + extrabarCssCls,
                items: [this.errorlist, {
                    xtype: 'box',
                    html: this.parseHelp()
                }]
            }]
        });
        this.dockedItems = [{
            xtype: 'toolbar',
            dock: 'bottom',
            ui: 'footer',
            defaults: {minWidth: 75},

            items: ['->', {
                xtype: 'button',
                text: gettext('Save'),
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onSave
                }
            }]
        }];
        this.callParent(arguments);

        if(this.record) {
            this.loadRecord();
        }
    },

    parseHelp: function() {
        if(!this.editform.help) {
            return '';
        }
        var help = '<div class="section helpsection">';
        var me = this;
        var state = this.record === undefined? 'new': 'existing';
        Ext.Array.each(this.editform.help, function(helpobj) {
            if(Ext.typeOf(helpobj) === 'string') {
                helpobj = {text: helpobj};
            }
            if(helpobj.state === undefined || (helpobj.state === state)) {
                help += Ext.String.format('<p>{0}</p>', helpobj.text);
            }
        });
        return help + '</div>';
    },

    onSave: function() {
        if(this.editform.getForm().isValid()) {
            var record = Ext.ModelManager.create(this.editform.getForm().getValues(),
                                                 this.model);
            this.fireEvent('saveSucess', record);
        }
    },

    loadRecord: function() {
        this.editform.loadRecord(this.record);
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.WarningField', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            html: 'Information about the current delivery'
        });

Ext.define('devilry.statistics.Loader', {
    extend: 'Ext.util.Observable',
    requires: [
        'devilry.extjshelpers.AsyncActionPool',
        'devilry.statistics.AggregatedPeriodDataStore',
        'devilry.statistics.AggregatedPeriodDataForStudentBase',
        'devilry.statistics.LabelManager'
    ],

    constructor: function(periodid, config) {
        this._completeDatasetStatus = {loaded: false}; // NOTE: When this is a boolean instead of an object, the attribute does not seem to update everywhere, which leads to multiple loads of complete dataset.
        this._students_by_releatedid = {};
        this.periodid = periodid;
        this.labelManager = Ext.create('devilry.statistics.LabelManager', {
            loader: this
            //listeners: {
                //scope: this,
                //changedMany: this._onDataChanged
            //}
        });

        this.assignment_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
            remoteFilter: true,
            remoteSort: true
        });
        this.assignment_ids = [];

        this.addEvents('completeDatasetLoaded', 'minimalDatasetLoaded', 'filterApplied', 'filterCleared');
        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);
        this._loadMinimalDataset();
    },


    _createModel: function() {
        var fields = [
            {name: 'userid', type: 'int'},
            {name: 'username', type: 'string'},
            {name: 'full_name', type: 'string'},
            {name: 'labels', type: 'auto'},
            {name: 'labelsSortKey', type: 'string'}, // Used for sorting - we pick the first label, or empty string (if labels.length==0)
            {name: 'relatedstudent_id', type: 'int'},
            {name: 'totalScaledPoints', type: 'int'}
        ];
        Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
            fields.push(assignmentRecord.get('short_name'));
            var scaledPointdataIndex = assignmentRecord.get('id') + '::scaledPoints';
            fields.push(scaledPointdataIndex);
        }, this);
        var model = Ext.define('devilry.statistics.AggregatedPeriodDataForStudentGenerated', {
            extend: 'devilry.statistics.AggregatedPeriodDataForStudentBase',
            idProperty: 'userid',
            fields: fields
        });
    },

    _createStore: function() {
        this._createModel();
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.AggregatedPeriodDataForStudentGenerated',
            autoSync: false,
            proxy: 'memory'
        });
    },

    updateScaledPoints: function() {
        Ext.each(this.store.data.items, function(studentRecord, index) {
            studentRecord.updateScaledPoints();
        }, this);
    },

    filterBy: function(description, fn, scope) {
        this.store.filterBy(fn, scope);
        this.fireEvent('filterApplied', this, description);
    },

    clearFilter: function() {
        this.store.clearFilter();
        this.fireEvent('filterCleared', this);
    },

    _handleLoadError: function(details, op) {
        this._unmask();
        var httperror = 'Lost connection with server';
        if(op.error.status !== 0) {
            httperror = Ext.String.format('{0} {1}', op.error.status, op.error.statusText);
        }
        Ext.MessageBox.show({
            title: 'Failed to load the period overview',
            msg: '<p>This is usually caused by an unstable server connection. <strong>Try reloading the page</strong>.</p>' +
                Ext.String.format('<p>Error details: {0}: {1}</p>', httperror, details),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    },

    findAssignmentByShortName: function(short_name) {
        return this.assignment_store.findRecord('short_name', short_name);
    },





    ////////////////////////////////////////////////
    //
    // Minimal dataset loaders
    //
    ////////////////////////////////////////////////

    _loadMinimalDataset: function() {
        this._mask('Loading all data about all students on the period', 'page-load-mask');
        this._loadPeriod();
    },

    /**
     * @private
     */
    _loadPeriod: function() {
        Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod').load(this.periodid, {
            scope: this,
            callback: function(record, op) {
                if(!op.success) {
                    this._handleLoadError('Failed to load period', op);
                    return;
                }
                this.periodRecord = record;
                this._loadAssignments();
            }
        });
    },


    /**
     * @private
     */
    _loadAssignments: function() {
        this.assignment_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.assignment_store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.periodid
        }]);
        this.assignment_store.proxy.setDevilryOrderby(['publishing_time']);
        this.assignment_store.load({
            scope: this,
            callback: this._onAssignmentsLoaded
        });
    },

    /**
     * @private
     */
    _onAssignmentsLoaded: function(assignmentrecords, op) {
        if(!op.success) {
            this._handleLoadError('Failed to load assignments', op);
            return;
        }
        this._tmpAssignmentsWithAllGroupsLoaded = 0;
        Ext.each(assignmentrecords, function(assignmentrecord, index) {
            this.assignment_ids.push(assignmentrecord.get('id'));
        }, this);
        this._loadAggregatedPeriodData(false, this._onMinimalDatasetLoaded);
    },




    _loadAggregatedPeriodData: function(loadEverything, callbackFn) {
        this.aggregatedPeriodDataStore = Ext.create('devilry.statistics.AggregatedPeriodDataStore');
        this.aggregatedPeriodDataStore.loadForPeriod(this.periodid, loadEverything, {
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    Ext.callback(callbackFn, this);
                } else {
                    Ext.MessageBox.show({
                        title: 'Failed to load the period overview',
                        msg: '<p>Try reloading the page.</p>',
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR,
                        closable: false
                    });
                }
            }
        });
    },








    ////////////////////////////////////////////////
    //
    // AFTER Minimal dataset loaded
    //
    ////////////////////////////////////////////////

    _onMinimalDatasetLoaded: function() {
        this._mask('Rendering table of all results. May take some time for many students.', 'page-load-mask');
        this._minimalDatasetLoaded = true;
        this._createStore();
        this.store.suspendEvents();
        this._mergeMinimalDatasetIntoStore();
        this.store.resumeEvents();
        this._unmask();

        this.fireEvent('minimalDatasetLoaded', this);
    },

    _mergeMinimalDatasetIntoStore: function() {
        this._addAllRelatedStudentsToStore();
    },

    _addAllRelatedStudentsToStore: function() {
        this.totalStudents = this.aggregatedPeriodDataStore.data.items.length;
        this.aggregatedPeriodDataStore.each(function(aggregatedPeriodDataItem) {
            var userid = aggregatedPeriodDataItem.get('userid');
            var user = aggregatedPeriodDataItem.get('user');
            var relatedStudent = aggregatedPeriodDataItem.get('relatedstudent');
            var record = Ext.create('devilry.statistics.AggregatedPeriodDataForStudentGenerated', {
                userid: userid,
                username: user.username,
                full_name: user.full_name,
                relatedstudent_id: relatedStudent.id,
                labels: relatedStudent.labels,
                labelsSortKey: relatedStudent.labels.length === 0? '': relatedStudent.labels[0].label
            });
            this.store.add(record);
            record.assignment_store = this.assignment_store;
            //record.relatedStudentRecord = relatedStudentRecord;
            record.groupsByAssignmentId = {};
            this._students_by_releatedid[relatedStudent.id] = record;
        }, this);
    },







    ////////////////////////////////////////////////////
    //
    // Complete dataset loaders
    //
    ////////////////////////////////////////////////////

    requireCompleteDataset: function(callback, scope, args) {
        if(this._completeDatasetStatus.loaded) {
            Ext.bind(callback, scope, args)();
        } else {
            this.addListener('completeDatasetLoaded', function() {
                Ext.bind(callback, scope, args)();
            }, this, {single: true});
            this._mask('Loading all results for all students', 'page-load-mask');
            //this._loadAllGroupsInPeriod();
            this._loadAggregatedPeriodData(true, this._onCompleteDatasetLoaded);
        }
    },




    //////////////////////////////////////////////
    //
    // AFTER complete dataset loaded
    //
    //////////////////////////////////////////////

    _onCompleteDatasetLoaded: function() {
        this._unmask();
        if(this._minimalDatasetLoaded) {
            this._mergeCompleteDatasetIntoStore();
        } else {
            this.addListener('minimalDatasetLoaded', this._mergeCompleteDatasetIntoStore, this, {single: true});
        }
    },

    _mergeCompleteDatasetIntoStore: function() {
        if(this._completeDatasetStatus.loaded) {
            return;
        }
        this._completeDatasetStatus.loaded = true;
        this._mask('Calculating table of all results. May take some time for many students.', 'page-load-mask');

        this.store.suspendEvents();
        this._addAssignmentsToStore(function() {
            this._addGroupsToStore(function() {
                this.updateScaledPoints();
                this.store.resumeEvents();

                this.fireEvent('completeDatasetLoaded', this);
                this._unmask();
            });
        });
    },

    _addAssignmentsToStore: function(onComplete) {
        var assignment_ids = [];
        Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
            assignment_ids.push(assignmentRecord.get('id'));
        }, this);
        this._iterateWithDeferYields(this.store.data.items, function(studentRecord, index) {
            Ext.each(this.assignment_store.data.items, function(assignmentRecord, index) {
                studentRecord.groupsByAssignmentId[assignmentRecord.get('id')] = {
                    groupInfo: null,
                    scaled_points: null
                };
            }, this);
            studentRecord.assignment_ids = assignment_ids;
        }, this, onComplete);
    },

    _addGroupsToStore: function(onComplete) {
        this._iterateWithDeferYields(this.aggregatedPeriodDataStore.data.items, function(aggregatedPeriodDataItem) {
            userid = aggregatedPeriodDataItem.get('userid');
            var studentRecord = this.store.getById(userid);
            var groups = aggregatedPeriodDataItem.get('groups');
            for(var index=0; index<groups.length; index++)  {
                var groupInfo = groups[index];
                var group = studentRecord.groupsByAssignmentId[groupInfo.assignment_id];
                group.groupInfo = groupInfo;
            }
        }, this, onComplete);
    },

    /**
     * @private
     * Almost drop-in replacement for Ext.Array.each that uses Ext.defer on
     * every 200 item to yield control back to the browser, which prevents
     * "stop script" popups.
     *
     * The primary difference from Ext.Array.each is that this function is
     * asynchronous. Therefore it takes the onComplete parameter which is a
     * callback function that is invoked when the iteration is complete.
     */
    _iterateWithDeferYields: function(items, callback, scope, onComplete, start) {
        if(start === undefined) {
            start = 0;
        }
        var index;
        for(index=start; index<items.length; index++) {
            Ext.bind(callback, scope)(items[index], index);
            if(index > 0 && index % 200 === 0) {
                Ext.defer(function() {
                    this._iterateWithDeferYields(items, callback, scope, onComplete, index+1);
                }, 5, this);
                break;
            }
        }
        if(index === items.length) {
            Ext.bind(onComplete, scope)();
        }
    },

    _mask: function(msg) {
        this.fireEvent('mask', this, msg);
    },

    _unmask: function() {
        this.fireEvent('unmask', this);
    }
});


Ext.define('devilry_extjsextras.CreateButton', {
    extend: 'devilry_extjsextras.PrimaryButton',
    alias: 'widget.createbutton',
    cls: 'devilry_extjsextras_createbutton',
    text: pgettext('uibutton', 'Create')
});


Ext.define('devilry.gradeeditors.GradeEditorSelectForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.gradeeditorselectform',
    cls: 'widget-gradeeditorselectform',
    requires: ['devilry.gradeeditors.GradeEditorSelector'],

    suggested_windowsize: {
        width: 900,
        height: 600
    },

    flex: 0.8,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: 'gradeeditorid',
        fieldLabel: "Select a grade editor",
        xtype: 'gradeeditorselector'
    }],

    help: [
        'A <strong>grade editor</strong> is what examiners use to give feedback to students.',

        'Internally in Devilry, a grade is:<ul>' +
        '   <li>The number of points. Any grade in Devilry is represented as a number, however this number is mainly for statistical purposes.</li>' +
        '   <li>A very short text that students view. Usually something like: <em>Approved</em>, <em>B</em> or <em>7/10</em>.</li>' +
        '   <li>A longer text that students can view.</li>' +
        '</ul>',

        'To make it easy for examiners to create all the information related to a <em>grade</em>, ' +
        'Devilry use <em>grade editors</em>. Grade editors give examiners a unified user-' +
        'interface tailored for different kinds of grading systems.'
    ]
});


/** Config editor widget. */
Ext.define('devilry.gradeeditors.ConfigEditorWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.gradeconfigeditor',
    cls: 'devilry_gradeconfigeditor',
    layout: 'fit',
    requires: [
        'devilry.gradeeditors.FailureHandler',
        'devilry.extjshelpers.HelpWindow'
    ],

    /**
     * @cfg {Object} [registryitem]
     * The data attribute of the record returned when loading the
     * grade-editor registry item. (Required).
     */


    /**
     * @cfg {Object} [gradeEditorConfigRecord]
     * The grade editor config record (Required).
     */


    /**
     * @cfg {String} [helpCls]
     * The css class(es) for the help box.
     */
    helpCls: 'bootstrap',


    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            items: [{
                xtype: 'box',
                html: gettext('Loading') + ' ...'
            }]
        });
        this.callParent(arguments);

        this.gradeEditorPanel = Ext.widget('panel', {
            border: false,
            frame: false,
            loader: {
                url: this.registryitem.config_editor_url,
                renderer: 'component',
                autoLoad: true,
                loadMask: true,
                scope: this, // for success and failure
                success: this._initializeEditor,
                failure: this._onLoadConfigEditorFailure
            }
        });
    },

    /**
     * @private
     */
    _getConfigModelName: function() {
        return 'devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig';
    },

    /**
     * @private
     */
    _onLoadConfigEditorFailure: function(elementloader, response) {
        console.error(Ext.String.format(
            'Loading grade config editor failed with {0}: {1}',
            response.status, response.statusText
        ));
        if(response.status === 404) {
            console.error('Status code 404 indicates that the config_editor_url is invalid.');
        } else if(response.status === 200) {
            console.error('Status code 200 indicates that the config_editor_url contains javascript with syntax errors.');
        }
        console.error('Complete response object:');
        console.error(response);
    },

    /**
     * @private
     */
    onHelp: function() {
        this.helpwindow.show();
    },

    /**
     * @private
     */
    _initializeEditor: function() {
        this.removeAll();
        this.gradeEditorPanel.padding = 0;
        this.gradeEditorPanel.margin = '0 40 0 0';
        if(this._getConfigEditor().help) {
            var helphtml = this._getConfigEditor().help;
            this.gradeEditorPanel.columnWidth = 0.6;
            this.add({
                xtype: 'container',
                layout: 'column',
                items: [this.gradeEditorPanel, {
                    xtype: 'box',
                    cls: this.helpCls,
                    padding: 0,
                    html: helphtml,
                    columnWidth: 0.4
                }]
            });
        } else {
            this.add(this.gradeEditorPanel);
        }

        this._getConfigEditor().initializeEditor(this.gradeEditorConfigRecord.data);
    },


    /**
     * @private
     * Get the config editor.
     */
    _getConfigEditor: function() {
        return this.gradeEditorPanel.getComponent(0);
    },

    /**
     * Call the onSave() method in the config editor. Typically used by a save button event handler.
     */
    triggerSave: function() {
        this._getConfigEditor().onSave();
    },


    /**
     * Called to save a configstring.
     *
     * @param configstring The config string to save.
     * @param onFailure
     *     The callback to invoke if save fails. Defaults to a
     *     autogenerated error message. ``onFailure`` is called in
     *     the scope of the grade editor that invoked ``saveConfig``,
     *     and the only parameter is the operation object that describes
     *     the error.
     */
    saveConfig: function(configstring, onFailure) {
        var onFailureCallback = onFailure || devilry.gradeeditors.FailureHandler.onFailure;
        var me = this;
        var configrecord = Ext.create(this._getConfigModelName(), {
            config: configstring,
            gradeeditorid: this.gradeEditorConfigRecord.get('gradeeditorid'),
            assignment: this.gradeEditorConfigRecord.get('assignment')
        });
        configrecord.save({
            scope: this,
            success: function(response) {
                this.fireEvent('saveSuccess', this, configrecord);
            },
            failure: function(unused, operation) {
                this.fireEvent('saveFailed', this);
                Ext.bind(onFailureCallback, this._getConfigEditor())(operation);
            }
        });
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.OtherDeliveries', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            target: 'tooltip-other-deliveries',
            html: 'Dropdown menu of other deliveries grouped by deadline'
        });

Ext.define('devilry.extjshelpers.studentsmanager.StudentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsmanager_studentsgrid',
    cls: 'widget-studentsmanager_studentsgrid',
    sortableColumns: true,

    requires: [
        'devilry.extjshelpers.GridSelectionModel'
    ],

    config: {
        assignmentid: undefined,
        dockedItems: [],
        isAdministrator: undefined,
        isAnonymous: undefined,
        assignmentrecord: undefined
    },

    mixins: {
        canPerformActionsOnSelected: 'devilry.extjshelpers.GridPeformActionOnSelected'
    },

    infoColTpl: Ext.create('Ext.XTemplate', 
        '<div class="section infocolumn">',
            '<div>',
                '<tpl if="is_open">',
                    '<span class="group_is_open">', gettext('Open'), '</span>',
                '</tpl>',
                '<tpl if="!is_open">',
                    '<span class="group_is_closed">', gettext('Closed'), '</span>',
                '</tpl>',
            '</div>',
            '<div>',
                '<tpl if="latest_deadline_id === null">',
                    '<span class="has_no_deadlines">',
                        interpolate(gettext('No %(deadlines_term)s'), {
                            deadlines_term: gettext('deadlines')
                        }, true),
                    '</span>',
                '</tpl>',
            '</div>',
        '</div>'
    ),

    candidatesCol_old: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates__identifier">',
        '       <li>',
        '           {.}',
        '       </li>',
        '    </tpl>',
        '</ul>'
    ),
    candidatesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates">',
        '       <li>',
        '           <a href="../assignmentgroup/{parent.id}">{identifier}</a>',
        '       </li>',
        '    </tpl>',
        '</ul>'
    ),
    candFullNamesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates">',
        '       <li>',
        '           {full_name}',
        '       </li>',
        '    </tpl>',
        '</ul>'
    ),

    realUsernamesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates__student__username">',
        '       <li><a href="../assignmentgroup/{parent.id}">{.}</a></li>',
        '    </tpl>',
        '</ul>'
    ),

    realFullnamesCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="candidates__student__devilryuserprofile__full_name">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    examinersCol: Ext.create('Ext.XTemplate', 
        '<ul class="namecolumn">',
        '    <tpl for="examiners__user__username">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    tagsColTpl: Ext.create('Ext.XTemplate', 
        '<ul class="tagscolumn">',
        '    <tpl for="tags__tag">',
        '       <li>{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    activeDeadlineColTpl: Ext.create('Ext.XTemplate', 
        '<span class="activedeadlinecol">{latest_deadline_deadline}</span>'
    ),

    deliveriesColTpl: Ext.create('Ext.XTemplate', 
        '<span class="deliveriescol">',
        '    <tpl if="number_of_deliveries &gt; 0">',
        '       {number_of_deliveries}',
        '    </tpl>',
        '    <tpl if="number_of_deliveries == 0">',
        '       <span class="nodeliveries">0</div>',
        '   </tpl>',
        '</span>'
    ),

    pointsColTpl: Ext.create('Ext.XTemplate', 
        '<span class="pointscolumn">',
        '    <tpl if="feedback">',
        '       {feedback__points}',
        '    </tpl>',
        '    <tpl if="!feedback">',
        '       <span class="nofeedback">&empty;</span>',
        '   </tpl>',
        '</span>'
    ),

    gradeColTpl: Ext.create('Ext.XTemplate', 
        '<div class="section gradecolumn">',
            '<tpl if="feedback">',
                '<div class="is_passing_grade">',
                    '<tpl if="feedback__is_passing_grade"><span class="passing_grade">', gettext('Passed'), '</span></tpl>',
                    '<tpl if="!feedback__is_passing_grade"><span class="not_passing_grade">', gettext('Failed'), '</span></tpl>',
                    ' : <span class="grade">{feedback__grade}</span>',
                '</div>',
                '<div class="delivery_type">',
                    '<tpl if="feedback__delivery__delivery_type == 0"><span class="electronic">',
                        gettext('Electronic'),
                    '</span></tpl>',
                    '<tpl if="feedback__delivery__delivery_type == 1"><span class="non-electronic">',
                        gettext('Non-electronic'),
                    '</span></tpl>',
                    '<tpl if="feedback__delivery__delivery_type == 2"><span class="alias">',
                        interpolate(gettext('From previous %(period_term)s'), {
                            period_term: gettext('period')
                        }, true),
                    '</span></tpl>',
                    '<tpl if="feedback__delivery__delivery_type &gt; 2"><span class="unknown">',
                        interpolate(gettext('Unknown %(delivery_term)s type'), {
                            delivery_term: gettext('delivery')
                        }, true),
                    '</span></tpl>',
                '</div>',
            '</tpl>',
            '<tpl if="!feedback">',
                '<div class="nofeedback">',
                    'No feedback',
                '</div>',
            '</tpl>',
        '</div>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.store.pageSize = 30;
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);


        this.selModel = Ext.create('devilry.extjshelpers.GridSelectionModel', {
            checkOnly: false
        });

        var studentsCol;
        if(this.isAdministrator) {
            studentsCol = {
                text: gettext('Students'), dataIndex: 'id',
                menuDisabled: true, sortable: false,
                columns: [{
                    text: gettext('Usernames'), dataIndex: 'candidates__student__username', width: 90,
                    menuDisabled: true, sortable: true,
                    renderer: this.formatRealUsernamesCol
                }, {
                    text: gettext('Full names'), dataIndex: 'candidates__student__devilryuserprofile__full_name', width: 155,
                    menuDisabled: true, sortable: true,
                    renderer: this.formatRealFullnamesCol
                }]
            };
            if(this.isAnonymous) {
                studentsCol.columns.push({
                    text: gettext('Candidate ID'), dataIndex: 'candidates__identifier',
                    width: 90,
                    menuDisabled: true, sortable: true,
                    renderer: this.formatCandidatesCol_old
                });
            }
        } else {
            if(this.isAnonymous) {
                studentsCol = {
                    text: gettext('Students'), dataIndex: 'candidates__identifier', flex: 4,
                    menuDisabled: true,
                    sortable: true,
                    renderer: this.formatCandidatesCol
                };
            } else {
                studentsCol = {
                    text: gettext('Students'), dataIndex: 'id',
                    menuDisabled: true, sortable: false,
                    columns: [{
                        text: gettext('Usernames'), dataIndex: 'candidates__identifier',
                        width: 90,
                        menuDisabled: true, sortable: true,
                        renderer: this.formatCandidatesCol
                    }, {
                        text: gettext('Full names'), dataIndex: 'candidates__full_name',
                        width: 155,
                        menuDisabled: true, sortable: true,
                        renderer: this.formatCandFullNamesCol
                    }]
                };
            }
        }

        Ext.apply(this, {
            columns: [{
                text: '', dataIndex: 'is_open', width: 100,
                menuDisabled: true,
                renderer: this.formatInfoCol
            }, studentsCol, {
                text: interpolate(gettext('Latest %(feedback_term)s'), {
                    feedback_term: gettext('feedback')
                }, true),
                menuDisabled: true,
                sortable: false,
                columns: [{
                    text: gettext('Points'),
                    dataIndex: 'feedback__points',
                    renderer: this.formatPointsCol,
                    menuDisabled: true,
                    sortable: true,
                    width: 70
                }, {
                    text: gettext('Grade'),
                    dataIndex: 'feedback__grade',
                    width: 150,
                    menuDisabled: true,
                    sortable: true,
                    renderer: this.formatGradeCol
                }]
            }, {
                text: gettext('Tags'), dataIndex: 'tags__tag', flex: 2,
                menuDisabled: true,
                renderer: this.formatTagsCol
            }, {
                text: gettext('Group name'), dataIndex: 'name', flex: 3,
                menuDisabled: true
            }]
        });
        if(this.isAdministrator) {
            Ext.Array.insert(this.columns, 3, [{
                text: gettext('Examiners'), dataIndex: 'examiners__user__username', flex: 3,
                menuDisabled: true,
                renderer: this.formatExaminersCol
            }]);
        }
        if(this.assignmentrecord.get('delivery_types') != 1) {
            this.columns.push({
                text: interpolate(gettext('Active %(deadline_term)s'), {
                    deadline_term: gettext('deadline')
                }, true),
                dataIndex: 'latest_deadline_deadline', width: 125,
                menuDisabled: true,
                renderer: this.formatActiveDeadlineCol
            });

            Ext.Array.insert(this.columns, 2, [{
                text: gettext('Deliveries'), dataIndex: 'number_of_deliveries', flex: 2,
                menuDisabled: true,
                renderer: this.formatDeliveriesCol
            }]);
        }

        this.dockedItems.push({
            xtype: 'pagingtoolbar',
            store: this.store,
            dock: 'bottom',
            displayInfo: true
        });

        this.callParent(arguments);
        this.store.load();
    },

    formatInfoCol: function(value, p, record) {
        return this.infoColTpl.apply(record.data);
    },

    formatCandidatesCol: function(value, p, record) {
        return this.candidatesCol.apply(record.data);
    },
    formatCandidatesCol_old: function(value, p, record) {
        return this.candidatesCol_old.apply(record.data);
    },
    formatCandFullNamesCol: function(value, p, record) {
        return this.candFullNamesCol.apply(record.data);
    },

    formatRealUsernamesCol: function(value, p, record) {
        return this.realUsernamesCol.apply(record.data);
    },
    formatRealFullnamesCol: function(value, p, record) {
        return this.realFullnamesCol.apply(record.data);
    },

    formatExaminersCol: function(value, p, record) {
        return this.examinersCol.apply(record.data);
    },

    formatDeliveriesCol: function(value, p, record) {
        return this.deliveriesColTpl.apply(record.data);
    },

    formatPointsCol: function(value, p, record) {
        return this.pointsColTpl.apply(record.data);
    },

    formatGradeCol: function(value, p, record) {
        return this.gradeColTpl.apply(record.data);
    },

    formatActiveDeadlineCol: function(value, p, record) {
        return this.activeDeadlineColTpl.apply(record.data);
    },

    formatTagsCol: function(value, p, record) {
        return this.tagsColTpl.apply(record.data);
    }
});


Ext.define('devilry.administrator.models.Deadline', {
    extend: 'devilry.extjshelpers.models.Deadline',
    hasMany: {
        model: 'devilry.administrator.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifieddeadline/'
    })
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnAll', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'numberfield',
                fieldLabel: 'Minumum total points',
                minValue: 0,
                value: this.settings? this.settings.minimumScaledPoints: '',
                margin: '0 0 10 0'
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var assignment_ids = this.loader.assignment_ids;
        var minimumScaledPoints = this.down('numberfield').getValue();
        return student.hasMinimalNumberOfScaledPointsOn(assignment_ids, minimumScaledPoints);
    },

    validInput: function() {
        return this.validPointInput();
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],
    autoScroll: true,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-chooseassignmentsgrid',
                margin: '0 0 10 0',
                store: this.loader.assignment_store,
                selectedAssignmentIds: this.settings? this.settings.assignment_ids: undefined
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    _getGrid: function() {
        return this.down('statistics-chooseassignmentsgrid');
    },

    filter: function(student) {
        var assignment_ids = this._getGrid().getIdOfSelected();
        return student.passesAssignments(assignment_ids);
    },

    validInput: function() {
        return this._getGrid().checkAtLeastOneSelected();
    },

    getSettings: function() {
        var assignment_ids = this._getGrid().getIdOfSelected();
        return {
            assignment_ids: assignment_ids
        };
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.SearchField', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            html: 'Search within this assignment'
        });

/**
 * A dialog that we use to confirm deleting something.
 * */
Ext.define('devilry_extjsextras.ConfirmDeleteDialog', {
    extend: 'Ext.window.Window',
    cls: 'devilry_confirmdeletedialog bootstrap',
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.CancelButton',
        'devilry_extjsextras.DeleteButton'
    ],

    width: 350,
    height: 230,

    /**
     * @cfg {string} required_confirm_text (optional)
     * Defaults to ``DELETE``.
     */
    required_confirm_text: gettext('DELETE'),

    /**
     * @cfg {string} short_description (required)
     * Short description of what you are deleting (normally the name of the item).
     */

    /**
     * @cfg {string} helptpl (optional)
     * A Ext.XTemplate template string. Defaults to a useful localized message,
     * however it can be overridden.  Can use ``required_confirm_text`` and
     * ``short_description`` as template variables.
     */
    helptpl: [
        '<p>',
            gettext('Type {required_confirm_text} in the field below to confirm that you really intend to delete {short_description}.'),
        '</p>'
    ],

    _apply_template: function(tpl, data) {
        return Ext.create('Ext.XTemplate', tpl).apply(data);
    },

    initComponent: function() {
        this.addEvents({
            /**
             * @event
             * Fired when delete is confirmed.
             * @param dialog This confirm dialog.
             * */
            "deleteConfirmed" : true
        });

        var short_helptext = this._apply_template(gettext('Write "{something}"'), {
            something: this.required_confirm_text
        });

        Ext.apply(this, {
            layout: 'fit',
            closable: false,
            modal: true,
            title: this._apply_template(gettext('Delete {something}?'), {
                something: this.short_description
            }),
            items: {
                xtype: 'form',
                bodyPadding: 20,
                autoScroll: true,
                border: 0,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'box',
                    margin: {bottom: 5},
                    cls: 'bootstrap',
                    tpl: this.helptpl,
                    data: {
                        short_description: this.short_description,
                        required_confirm_text: this.required_confirm_text
                    }
                }, {
                    name: "confirm_text",
                    xtype: 'textfield',
                    regex: new RegExp('^' + this.required_confirm_text + '$'),
                    invalidText: short_helptext,
                    allowBlank: false,
                    listeners: {
                        scope: this,
                        render: function(field) {
                            Ext.defer(function() {
                                field.focus();
                            }, 200);
                        }
                    }
                }],
                buttons: ['->', {
                    xtype: 'cancelbutton',
                    listeners: {
                        scope: this,
                        click: function() {
                            this._close();
                        }
                    }
                }, {
                    xtype: 'deletebutton',
                    formBind: true,
                    listeners: {
                        scope: this,
                        click: this._onDelete
                    }
                }],
                listeners: {
                    scope: this,
                    render: this._onRenderForm
                }
            }
        });
        this.callParent(arguments);
    },

    _getForm: function() {
        return this.down('form').getForm();
    },
    getFormPanel: function() {
        return this.down('form');
    },

    _onRenderForm: function() {
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onDelete,
            scope: this
        });
    },

    _onDelete: function() {
        var form = this._getForm();
        if(form.isValid()) {
            this.fireEvent('deleteConfirmed', this)
        }
    },

    _close: function() {
        this.close();
    }
});


Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.FeedbackWindow', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            target: 'tooltip-feedback-window',
            html: 'Click to create a new feedback for this delivery'
        });


Ext.define('devilry_header.StudentSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_studentsearchresults',
    extraCls: 'devilry_header_studentsearchresults',

    singleResultTpl: [
        '<div><a href="{[this.getUrl(values)]}" class="{[this.getResultLinkCls()]}">{title}</a></div>',
        '<div class="meta path">{path}</div>',
        '<tpl if="type == \'core_assignmentgroup\'">',
            '<tpl if="values.students.length &gt; 1">',
                '<div class="meta students">',
                    '{[this.joinStringArray(values.students)]}',
                '</small></div>',
            '</tpl>',
        '</tpl>'
    ],

    heading: gettext('Content where you are student'),

    getUrl:function (values) {
        var prefix = Ext.String.format('{0}/devilry_student/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        if(values.type === 'core_assignmentgroup') {
            return Ext.String.format('{0}#/group/{1}/',
                prefix, values.id);
        } else {
            throw Ext.String.format('Unknown type: {0}', values.type);
        }
    }
});

/**
 * Search widget with a {@link devilry.extjshelpers.searchwidget.MultiSearchField} on top
 * and results in a {@link devilry.extjshelpers.searchwidget.MultiSearchResults} below.
 *
 *     Search: ______________
 *    
 *     |Result1             |
 *     +--------------------|
 *     |                    |
 *     |                    |
 *     |                    |
 *     +--------------------+
 *    
 *     |Result2             |
 *     +--------------------|
 *     |                    |
 *     |                    |
 *     |                    |
 *     +--------------------+
 *
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchwidget',
    cls: 'widget-searchwidget',
    requires: [
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.searchwidget.SearchResults',
        'devilry.extjshelpers.searchwidget.MultiSearchResults',
        'devilry.extjshelpers.SearchStringParser',
        'devilry.extjshelpers.searchwidget.SearchWindow'
    ],

    /**
     * @cfg {devilry.extjshelpers.searchwidget.SearchResults} [searchResultItems]
     * The SearchResults widget to use when searching.
     */

    /**
     * @cfg {string} [emptyText]
     * Empty text of the search field.
     */
    emptyText: gettext('Search for anything...'),

    initComponent: function() {
        this.searchwindow = Ext.create('devilry.extjshelpers.searchwidget.SearchWindow', {
            searchResultItems: this.searchResultItems,
            searchWidget: this,
            emptyText: this.emptyText
        });
        this.searchwindow.on('hide', function() {
            this.getSearchField().setValue('');
        }, this);
        this.searchfield = Ext.widget('searchfield', {
            emptyText: this.emptyText,
            flex: 1
        });

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            height: 40,
            items: [this.searchfield, {
                xtype: 'button',
                text: gettext('Browse') + ' ...',
                scale: 'medium',
                listeners: {
                    scope: this,
                    click: function() {
                        this.search('');
                    }
                }
            }]
        });

        this.callParent(arguments);
        this.setupSearchEventListeners();
    },

    setupSearchEventListeners: function() {
        var me = this;
        this.getSearchField().addListener('newSearchValue', function(value) {
            me.search(value);
        });
    },

    getSearchField: function() {
        return this.searchfield;
    },

    focusOnSearchfield: function() {
        this.getSearchField().focus();
    },

    search: function(value) {
        this.searchwindow.show();
        this.searchwindow.setSearchValue(value);
        this.searchwindow.getSearchField().triggerSearch(value);
    },

    loadInitialValues: function() {
        //var value = 'type:delivery deadline__assignment_group:>:33 3580';
        //var value = 'type:delivery assignment__short_name:week1';
        //var value = 'type:delivery group:'
        //var value = 'type:delivery deadline__assignment_group__parentnode__parentnode__short_name:duck3580';
        //var value = '';
        //this.search(value);
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackView', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.staticfeedbackview',
    cls: 'widget-staticfeedbackview',

    tpl: Ext.create('Ext.XTemplate',
        '<div class="bootstrap">',
            '<tpl if="!isactive">',
                '<div class="alert">',
                    '<h4>This is not the active feedback</h4>',
                    'When an examiner publish a feedback, the feedback is ',
                    'stored forever. When an examiner needs to modify a feedback, ',
                    'they create a new feedback. Therefore, you see more than ',
                    'one feedback in the toolbar above. Unless there is something ',
                    'wrong with the latest feedback, you should not have to ',
                    'read this feedback',
                '</div>',
            '</tpl>',

            '<div class="alert alert-{gradecls}">',
                '<strong>', gettext('Grade'), '</strong>: ',
                '{is_passing_grade_label} ({grade})',
            '</div>',

            '<div class="rendered_view_preview">{rendered_view}</div>',
        '</div>'
    ),

    
    getData: function(data) {
        data.gradecls = data.is_passing_grade? 'success': 'warning';
        data.is_passing_grade_label = data.is_passing_grade? gettext('Passed'): gettext('Failed');
        return data;
    }
});


/**
 * Tooltip for previous button
 * 
 */
Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackPrevious', {
            extend: 'devilry.extjshelpers.tooltips.assignmentgroup.CommonConfig',
            html: 'Click to get to the previous feedback'
        });

Ext.define('devilry_extjsextras.SaveButton', {
    extend: 'devilry_extjsextras.PrimaryButton',
    alias: 'widget.savebutton',
    cls: 'devilry_extjsextras_savebutton',
    text: pgettext('uibutton', 'Save')
});


/** Default config for the Edit window, which is opened to edit an item in the
 * admin interface. */
Ext.define('devilry.administrator.DefaultEditWindow', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
    title: 'Edit',
    
    config: {
        /**
         * @cfg
         * The {@link devilry.administrator.PrettyView} to refresh when a save succeeds.
         */
        prettyview: undefined
    },

    onSaveSuccess: function(record) {
        this.prettyview.setRecord(record);
        this.close();
    }
});


Ext.define('devilry_extjsextras.OkButton', {
    extend: 'devilry_extjsextras.PrimaryButton',
    alias: 'widget.okbutton',
    cls: 'devilry_extjsextras_okbutton',
    text: pgettext('uibutton', 'Ok'),
    width: 70
});


Ext.define('devilry.examiner.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-dashboard',

    requires: [
        'devilry.examiner.ActiveAssignmentsView',
        'devilry.examiner.RecentDeliveriesView',
        'devilry.examiner.RecentFeedbacksView'
    ],

    cls: 'devilry_subtlebg',

    /**
     * @cfg {string} [dashboardUrl]
     */
    dasboardUrl: undefined,

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            autoScroll: true,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'examiner_activeassignmentsview',
                model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedAssignment'),
                dashboard_url: this.dashboardUrl
            }, {
                xtype: 'container',
                margin: '10 0 0 0',
                layout: 'column',
                items: [{
                    xtype: 'examiner_recentdeliveriesview',
                    model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDelivery'),
                    dashboard_url: this.dashboardUrl,
                    columnWidth: 0.5,
                    margin: '0 10px 0 0',
                    urlCreateFn: function(record) {
                        return Ext.String.format(
                            "{0}assignmentgroup/{1}?deliveryid={2}",
                            this.dashboardUrl,
                            record.get('deadline__assignment_group'),
                            record.get('id')
                        );
                    },
                    urlCreateFnScope: this
                }, {
                    xtype: 'examiner_recentfeedbackview',
                    model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedStaticFeedback'),
                    dashboard_url: this.dashboardUrl,
                    columnWidth: 0.5,
                    margin: '0 0 0 10px',
                    urlCreateFn: function(record) {
                        return Ext.String.format(
                            "{0}assignmentgroup/{1}?deliveryid={2}",
                            this.dashboardUrl,
                            record.get('delivery__deadline__assignment_group'),
                            record.get('delivery')
                        );
                    },
                    urlCreateFnScope: this
                }]
            }]
        });
        this.callParent(arguments);
    }
});


/** Popup window used by {@link devilry.extjshelpers.formfields.ForeignKeySelector} */
Ext.define('devilry.extjshelpers.formfields.ForeignKeyBrowser', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.foreignkeybrowser',
    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],
    hideHeaders: true,
    border: false,

    /**
     * @cfg {string} [tpl]
     */
    tpl: '{id}',

    /**
     * @cfg {Ext.data.Model} [model]
     */
    model: undefined,

    /**
     * @cfg {Object} [foreignkeyselector]
     * The form field that the value ends up in.
     */
    foreignkeyselector: undefined,

    /**
     * @cfg {Boolean} [allowEmpty]
     * Allow empty field?
     */
    allowEmpty: false,


    initComponent: function() {
        var me = this;
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true,
            autoLoad: true
        });

        var toolbarItems = [{
            xtype: 'storesearchfield',
            emptyText: 'Search...',
            store: this.store,
            autoLoadStore: false,
            listeners: {
                scope: this,
                render: function() {
                    var field = this.down('storesearchfield')
                    Ext.defer(function() {
                        field.focus();
                    }, 500, this);
                }
            }
        }];
        if(this.allowEmpty) {
            toolbarItems.push('->');
            toolbarItems.push({
                xtype: 'button',
                text: 'Clear value',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onClearValue
                }
            });
        }

        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: toolbarItems
            }, {
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: false
            }],

            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, record) {
                    return this.tpl.apply(record.data);
                }
            }],

            listeners: {
                scope: this,
                itemmouseup: this.onSelect
            }
        });
        this.callParent(arguments);

    },

    /**
     * @private
     */
    onClearValue: function() {
        this.foreignkeyselector.onClearValue();
        this.up('window').close();
    },

    /**
     * @private
     */
    onSelect: function(grid, record) {
        this.foreignkeyselector.onSelect(record);
        this.up('window').close();
    }
});


Ext.define('devilry_header.AdminSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_adminsearchresults',
    extraCls: 'devilry_header_adminsearchresults',

    singleResultTpl: [
        '<div><a href="{[this.getUrl(values)]}" class="{[this.getResultLinkCls()]}">{title}</a>',
            ' <span class="label label-inverse typename">{[this.getTypeName(values.type)]}</span>',
        '</div>',
        '<div class="meta path">{path}</div>',
        '<tpl if="type == \'core_assignmentgroup\'">',
            '<div class="meta students">',
                '{[this.joinStringArray(values.students)]}',
            '</small></div>',
        '</tpl>'
    ],

    heading: gettext('Content where you are admin'),


    getUrl:function (values) {
        var subjectadmin_prefix = Ext.String.format('{0}/devilry_subjectadmin/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        var nodeadmin_prefix = Ext.String.format('{0}/devilry_nodeadmin/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        if(values.type === 'core_assignmentgroup') {
            return Ext.String.format('{0}#/assignment/{1}/@@manage-students/@@select/{2}',
                subjectadmin_prefix, values.assignment_id, values.id);
        } else if(values.type === 'core_assignment') {
            return Ext.String.format('{0}#/assignment/{1}/',
                subjectadmin_prefix, values.id);
        } else if(values.type === 'core_period') {
            return Ext.String.format('{0}#/period/{1}/',
                subjectadmin_prefix, values.id);
        } else if(values.type === 'core_subject') {
            return Ext.String.format('{0}#/subject/{1}/',
                subjectadmin_prefix, values.id);
        } else if(values.type === 'core_node') {
            return Ext.String.format('{0}#/node/{1}',
                nodeadmin_prefix, values.id);
        } else {
            throw Ext.String.format('Unknown type: {0}', values.type);
        }
    }
});

Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.MustPassEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-mustpasseditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments'
    ],

    config: {
        assignment_store: undefined,
        must_pass: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            items: {
                xtype: 'statistics-listofassignments',
                title: 'Require passing grade on the following assignments:',
                selected_assignments: this.must_pass,
                assignment_store: this.assignment_store
            }
        });
        this.callParent(arguments);
    },

    getResult: function() {
        return this.down('statistics-listofassignments').getArrayOfAssignmentIds();
    }
});


Ext.define('devilry_header.HelpLinksStore', {
    extend: 'Ext.data.Store',
    model: 'devilry_header.HelpLinkModel',

    getHelpLinksForUser: function(userInfoRecord) {
        var helpLinkRecords = [];
        this.each(function(helpLinkRecord) {
            if(helpLinkRecord.matchesUserInfoRecord(userInfoRecord)) {
                helpLinkRecords.push(helpLinkRecord);
            }
        }, this);
        return helpLinkRecords;
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
    alias: 'widget.multicreatenewdeadlinewindow',
    title: 'Create deadline',
    width: 700,
    height: 450,

    requires: [
        'devilry.extjshelpers.RestfulSimplifiedEditPanelBase',
        'devilry.extjshelpers.forms.Deadline'
    ],

    config: {

        /**
         * @cfg
         * Deadline ``Ext.data.Model``.
         */
        deadlinemodel: undefined,

        suggestedDeadline: undefined,
        deadlineRecord: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        if(this.suggestedDeadline && !this.deadlineRecord) {
            this.deadlineRecord = Ext.create(this.deadlinemodel, {
                deadline: this.suggestedDeadline
            });
        }
        Ext.apply(this, {
            editpanel: Ext.widget('restfulsimplified_editpanel_base', {
                model: this.deadlinemodel,
                editform: Ext.create('devilry.extjshelpers.forms.Deadline'),
                record: this.deadlineRecord
            }),
        });
        this.callParent(arguments);
    }
});


/** The feedback creation methods for StudentsManager. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerCreateFeedback', {

    requires: [
        'devilry.gradeeditors.RestfulRegistryItem'
    ],

    /**
     * @private
     */
    loadGradeEditorConfigModel: function() {
        this.gradeeditor_config_model.load(this.assignmentid, {
            scope: this,
            success: function(configRecord) {
                this.gradeeditor_config_recordcontainer.setRecord(configRecord);
                this.loadRegistryItem();
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
    },

    /**
     * @private
     */
    loadRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        registryitem_model.load(this.gradeeditor_config_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(registryItemRecord) {
                this.registryitem_recordcontainer.setRecord(registryItemRecord);
            }
        });
    },

    /**
     * @private
     */
    onLoadRegistryItem: function() {
        if(this.giveFeedbackButton.rendered) {
            this.giveFeedbackButton.getEl().unmask();
        }
    },

    /**
     * @private
     */
    onGiveFeedbackToSelected: function(button) {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var draftEditor = Ext.create('devilry.gradeeditors.EditManyDraftEditorWindow', {
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            listeners: {
                scope: this,
                createNewDraft: this.onPublishFeedback
            }
        });
        draftEditor.show();
    },


    /**
     * @private
     */
    onPublishFeedback: function(feedbackdraftModelName, draftstring) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        this.progressWindow.start('Give feedback to many');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
            scope: this,
            callback: function(groupRecords) {
                if(this.assignmentrecord.data.delivery_types === this.deliveryTypes.TYPE_ELECTRONIC && this.anyGroupHaveNoDeliveries(groupRecords)) {
                    Ext.MessageBox.show({
                        title: 'Selected groups with no deliveries',
                        msg: 'One or more of the selected groups have no deliveries. You can only give feedback to groups with deliveries. Please review your selection and try again.',
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR
                    });
                } else {
                    Ext.each(groupRecords, function(groupRecord, index) {
                        this.giveFeedbackToSelected(groupRecord, index, groupRecords.length, feedbackdraftModelName, draftstring);
                    }, this);
                }
            },
        });
    },

    /**
     * @private
     */
    anyGroupHaveNoDeliveries: function(groupRecords) {
        for(i=0; i<groupRecords.length; i++) {
            var groupRecord = groupRecords[i];
            if(groupRecord.data.number_of_deliveries == 0) {
                return true;
            }
        }
        return false;
    },

    /**
     * @private
     */
    giveFeedbackToSelected: function(assignmentGroupRecord, index, totalSelectedGroups, feedbackdraftModelName, draftstring) {
        var msg = Ext.String.format('Setting feedback on group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        if(assignmentGroupRecord.data.latest_delivery_id == null)  {
            if(this.assignmentrecord.data.delivery_types === this.deliveryTypes.TYPE_ELECTRONIC) {
                this.progressWindow.addWarning(assignmentGroupRecord, 'Has no deliveries, and therefore we can not add any feedback.');
                this._finishedSavingGroupCount ++;
                this.checkIfFinishedGivingFeedback(totalSelectedGroups);
            } else {
                var delivery = this.createDeliveryRecord(assignmentGroupRecord, this.deliveryTypes.TYPE_NON_ELECTRONIC);
                delivery.save({
                    scope: this,
                    callback: function(deliveryrecord, operation) {
                        if(operation.success) {
                            this.progressWindow.addSuccess(assignmentGroupRecord, 'Non-electronic delivery successfully registered.');
                            this.publishFeedbackOnDelivery(assignmentGroupRecord, deliveryrecord.data.id, totalSelectedGroups, feedbackdraftModelName, draftstring);
                        } else {
                            this.progressWindow.addErrorFromOperation(
                                assignmentGroupRecord, 'Failed to register non-electronic delivery', operation
                            );
                            this.checkIfFinishedGivingFeedback(totalSelectedGroups);
                        }
                    }
                });
            }
        } else {
            this.publishFeedbackOnDelivery(assignmentGroupRecord, assignmentGroupRecord.data.latest_delivery_id, totalSelectedGroups, feedbackdraftModelName, draftstring);
        }
    },

    /**
     * @private
     */
    publishFeedbackOnDelivery: function(assignmentGroupRecord, delivery_id, totalSelectedGroups, feedbackdraftModelName, draftstring) {
        var draftrecord = Ext.create(feedbackdraftModelName, {
            draft: draftstring,
            published: true,
            delivery: delivery_id
        });
        draftrecord.save({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(assignmentGroupRecord, 'Feedback successfully created.');
                } else {
                    this.progressWindow.addErrorFromOperation(
                        assignmentGroupRecord, 'Failed to create feedback', operation
                    );
                }

                this._finishedSavingGroupCount ++;
                this.checkIfFinishedGivingFeedback(totalSelectedGroups);
            }
        });
    },


    checkIfFinishedGivingFeedback: function(totalSelectedGroups) {
        if(this._finishedSavingGroupCount == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
            this.progressWindow.finish();
        }
    }
});


Ext.define('devilry.extjshelpers.searchwidget.DashboardSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],
    mixins: {
        comboBoxTemplates: 'devilry.extjshelpers.ComboboxTemplatesMixin'
    },

    _createStore: function(modelname) {
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
        return store;
    }
});


/**
*  AlertMessageList that floats and automatically closes when all messages are closed.
*/ 
Ext.define('devilry_extjsextras.FloatingAlertmessageList', {
    extend: 'devilry_extjsextras.AlertMessageList',
    alias: 'widget.floatingalertmessagelist',
    cls: 'devilry_extjsextras_floatingalertmessagelist',

    messageDefaults: {
        closable: true,
        boxMargin: '0'
    },

    //onClose: function(alertmessage) {
        //this.callParent(arguments);
    //},

    initComponent: function() {
        Ext.apply(this, {
            hidden: true,
            border: false,
            frame: false,
            floating: true,
            shadow: false,
            bodyPadding: 0,
            sidePadding: 10
        });
        this._setupAutosizing();
        this.callParent(arguments);
    },

    _setupAutosizing: function() {
        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShowWindow, this);
    },
    _onShowWindow: function() {
        this._setSizeAndPosition();
        // NOTE: Defer to work around the problem of the window triggering show-event before the
        // message is rendered completely. Without this, setSize will get the wrong height
        Ext.defer(function () {
            this._setSizeAndPosition();
        }, 100, this);
        Ext.defer(function () {
            this._setSizeAndPosition();
        }, 400, this);
    },
    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this._setSizeAndPosition();
        }
    },
    _setSizeAndPosition: function() {
        if(this.isFloating()) {
            var bodysize = Ext.getBody().getViewSize();
            var width = bodysize.width * 0.42;
            var left = bodysize.width - width - this.sidePadding;
            this.setSize({
                width: width
            });
            this.setPosition(left, 0);
        }
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentgrouptodolist',
    cls: 'widget-assignmentgrouptodolist',
    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],

    studentsColTpl: Ext.create('Ext.XTemplate',
        '<div class="section popuplistitem">',
            '<a href="{groupUrlPrefix}{id}" style="display: block;">',
            '<tpl if="name">',
                '{name}: ',
            '</tpl>',
            '<tpl for="candidates">',
                '{identifier} <tpl if="full_name">({full_name})</tpl>',
                '<tpl if="xindex < xcount">, </tpl>',
            '</tpl>',
            '<tpl if="id == current_assignment_group_id">',
                ' &mdash; <strong>(', gettext('currently selected'), ')</strong>',
            '</tpl>',
            '</a>',
        '</div>'
    ),

    deliveriesColTpl: Ext.create('Ext.XTemplate', 
        '<div class="section popuplistitem">',
        '<span class="deliveriescol">',
        '    <tpl if="number_of_deliveries &gt; 0">',
        '       {number_of_deliveries}',
        '    </tpl>',
        '    <tpl if="number_of_deliveries == 0">',
        '       <span class="nodeliveries">0</div>',
        '   </tpl>',
        '</span>',
        '</div>'
    ),

    todohelptext: [
        '<p>',
            interpolate(gettext('This is your to-do list on this %(assignment_term)s. It shows all <em>open</em> %(groups_term)s. An <em>open</em> %(group_term)s is a %(group_term)s that is still waiting for %(deliveries_term)s or %(feedback_term)s.'), {
                assignment_term: gettext('assignment'),
                groups_term: gettext('groups'),
                group_term: gettext('group'),
                deliveries_term: gettext('deliveries'),
                feedback_term: gettext('feedback')
            }, true),
        '</p>'
    ].join(''),

    /**
     * @cfg
     * The name of the assignment group ``Ext.data.Model`` to use in the store
     * (Required).  The store copies the proxy from this model.
     *
     */
    assignmentgroupmodelname: undefined,

    /**
    * @cfg
    * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup. (Optional).
    *
    * This is optional, however if it is not provided, you will have to call
    * loadTodoListForAssignment(assignmentid) manually to load data into the
    * store.
    */
    assignmentgroup_recordcontainer: undefined,

    /**
     * @cfg
     */
    pageSize: 7,

    /**
     * @cfg
     * (Optional)
     */
    toolbarExtra: undefined,

    /**
     * @cfg
     * (Optional)
     */
    helpTpl: Ext.create('Ext.XTemplate',
        '<div class="section helpsection">{todohelptext}</div>'
    ),

    initComponent: function() {
        this._createStore();
        var me = this;
        this.tbarItems = [{
            xtype: 'storesearchfield',
            emptyText: gettext('Search') + ' ...',
            store: this.store,
            pageSize: this.pageSize,
            width: 300,
            autoLoadStore: false
        }];
        if(this.toolbarExtra) {
            Ext.Array.insert(this.tbarItems, 1, this.toolbarExtra);
        }

        var groupUrlPrefix = this.getGroupUrlPrefix();
        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                flex: 6,
                xtype: 'grid',
                disableSelection: true,
                //rowLines: false,
                store: this.store,
                frame: false,
                border: false,
                sortableColumns: false,
                autoScroll: true,
                columns: [{
                    header: gettext('Students'),
                    dataIndex: 'id',
                    flex: 2,
                    menuDisabled: true,
                    renderer: function(value, metaData, grouprecord) {
                        var data = {
                            groupUrlPrefix: groupUrlPrefix
                        };
                        if(me.assignmentgroup_recordcontainer) {
                            data.current_assignment_group_id = me.assignmentgroup_recordcontainer.record.data.id;
                        }
                        Ext.apply(data, grouprecord.data);
                        return me.studentsColTpl.apply(data);
                    }
                }, {
                    text: gettext('Deliveries'), dataIndex: 'id', width: 100, menuDisabled: true,
                    renderer: function(v, p, record) { return me.deliveriesColTpl.apply(record.data); }
                }],

                listeners: {
                    scope: this,
                    render: this._onRenderGrid
                }
            }, {
                xtype: 'box',
                width: 300,
                autoScroll: true,
                flex: 4,
                html: this.helpTpl.apply({todohelptext: this.todohelptext})
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                //ui: 'footer',
                items: this.tbarItems
            }, {
                xtype: 'pagingtoolbar',
                store: me.store,
                dock: 'bottom',
                displayInfo: true
            }]
        });

        this.callParent(arguments);

    },

    _onRenderGrid: function() {
        Ext.defer(function() {
            if(this.assignmentgroup_recordcontainer) {
                if(this.assignmentgroup_recordcontainer.record) {
                    this.onSetAssignmentGroup();
                }
                this.assignmentgroup_recordcontainer.addListener('setRecord', this.onSetAssignmentGroup, this);
            }
            this.down('searchfield').focus();
        }, 300, this);
    },

    _createStore: function() {
        var model = Ext.ModelManager.getModel(this.assignmentgroupmodelname);
        this.store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
    },

    getGroupUrlPrefix: function() {
        return '';
    },

    /**
     * @private
     */
    onSetAssignmentGroup: function() {
        this.loadTodoListForAssignment(this.assignmentgroup_recordcontainer.record.data.parentnode);
    },

    /**
     * Reload store with the given assignmentid.
     * */
    loadTodoListForAssignment: function(assignmentid) {
        this.store.pageSize = this.pageSize;
        var searchfield = this.down('storesearchfield');
        searchfield.alwaysAppliedFilters = [{
            field: 'parentnode',
            comp: 'exact',
            value: assignmentid
        }, {
            field: 'is_open',
            comp: 'exact',
            value: true
        }];
        searchfield.refreshStore();
    },
});


Ext.define('devilry.statistics.ScalePointsPanel', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-scalepointspanel',
    requires: [
        'devilry.extjshelpers.HelpWindow',
        'devilry.extjshelpers.NotificationManager'
    ],

    saveMessageTpl: Ext.create('Ext.XTemplate',
        '{long_name}: {scale_points_percent}%'
    ),
    
    initComponent: function() {
        Ext.apply(this, {
            selType: 'cellmodel',
            plugins: [
                Ext.create('Ext.grid.plugin.CellEditing', {
                    clicksToEdit: 1
                })
            ],

            columns: [{
                header: 'Long name',
                dataIndex: 'long_name',
                flex: 1
            }, {
                header: 'Scale by (percent)',
                dataIndex: 'scale_points_percent',
                width: 110,
                field: {
                    xtype: 'numberfield',
                    allowBlank: false
                }
            }],

            listeners: {
                scope: this,
                edit: this._onEdit
            },

            bbar: [{
                xtype: 'button',
                iconCls: 'icon-help-32',
                text: 'Help',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this._onHelp
                }
            }]
        });
        this.callParent(arguments);
    },

    _onEdit: function(editor, e) {
        Ext.getBody().mask('Saving point scale', 'page-load-mask');
        e.record.commit();
        e.record.save({
            scope: this,
            callback: this._onSaveComplete
        });
    },

    _onSaveComplete: function(record, op) {
        Ext.getBody().unmask();
        if(op.success) {
            this.loader.updateScaledPoints();
            devilry.extjshelpers.NotificationManager.show({
                title: 'Save successful',
                message: this.saveMessageTpl.apply(record.data)
            });
        } else {
            Ext.MessageBox.show({
                title: 'Failed to save point scale changes',
                msg: '<p>This is usually caused by an unstable server connection. Please try to reload the page.</p>',
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR,
                closable: false
            });
        }
    },

    _onHelp: function() {
        Ext.widget('helpwindow', {
            title: 'Help',
            width: 500,
            height: 400,
            helptext: '<p>Click on cells in the <em>Scale by</em> column to increase/decrease the weight of assignments.</p>' +
                '<h2>How it works</h2><p>Points are calculated as <code>scale-by * points / 100</code>.</p>' +
                '<h2>Warning</h2><p>Labels are <strong>not</strong> updated automatically when you change <em>Scale by</em>. You need to re-apply labels manually.</p>'
        }).show();
    }
});


Ext.define('devilry.administrator.studentsmanager.LocateGroup', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.locategroup',
    cls: 'widget-locategroup selectable-grid',

    rowTpl: Ext.create('Ext.XTemplate',
        '<div class="section popuplistitem">',
        '    <tpl if="name">',
        '        {name}: ',
        '    </tpl>',
        '    <ul style="display: inline-block;">',
        '    <tpl for="candidates__identifier">',
        '        <li>{.}</li>',
        '    </tpl>',
        '    </ul>',
        '    <tpl if="id == current_assignment_group_id">',
        '        &mdash; <strong>(currently selected)</strong>',
        '    </tpl>',
        '</div>'
    ),

    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],

    deliveriesColTpl: Ext.create('Ext.XTemplate', 
        '<span class="deliveriescol">',
        '    <tpl if="number_of_deliveries &gt; 0">',
        '       {number_of_deliveries}',
        '    </tpl>',
        '    <tpl if="number_of_deliveries == 0">',
        '       <span class="nodeliveries">0</div>',
        '   </tpl>',
        '</span>'
    ),

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Store``. (Required).
         */
        store: undefined,

        groupRecord: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;

        this.searchfield = Ext.widget('storesearchfield', {
            emptyText: 'Search...',
            store: this.store,
            pageSize: 30,
            width: 300,
            autoLoadStore: true,
            alwaysAppliedFilters: [{
                field: 'is_open',
                comp: 'exact',
                value: false
            }]
        });

        //var searchdefault = '';
        //Ext.each(this.groupRecord.data.candidates__student__username, function(username, index) {
            //searchdefault += username + ' ';
        //});
        //console.log(searchdefault);
        //var searchdefault = ''
        //this.searchfield.setValue(searchdefault);

        Ext.apply(this, {
            columns: [{
                header: 'Students',
                dataIndex: 'id',
                flex: 2,
                renderer: function(value, metaData, grouprecord) {
                    return this.rowTpl.apply(grouprecord.data);
                }
            }, {
                text: 'Group name', dataIndex: 'name', flex: 1
            }, {
                text: 'Deliveries', dataIndex: 'id', width: 70,
                renderer: function(v, p, record) { return this.deliveriesColTpl.apply(record.data); }
            }],

            listeners: {
                scope: this,
                itemmouseup: this.onSelectGroup
            },

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [this.searchfield]
            }, {
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: true
            }]
        });

        this.callParent(arguments);
    },

    onSelectGroup: function(grid, assignmentgroupRecord) {
        console.log('selected');
    },
});


/** Apanel for editing RestfulSimplified models. */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditPanel', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditPanelBase',
    alias: 'widget.restfulsimplified_editpanel',
    requires: [
        'devilry.extjshelpers.RestSubmit',
        'devilry.extjshelpers.NotificationManager'
    ],

    /**
     * @cfg {String} [saveSuccessMessage]
     * help
     */
    saveSuccessMessage: undefined,

    onSave: function() {
        this.errorlist.clearErrors();
        this.beforeSave();
    },

    beforeSave: function() {
        this.doSave();
    },

    doSave: function() {
        var me = this;
        this.setLoading(gettext('Saving') + ' ...');
        this.editform.getForm().doAction('devilryrestsubmit', {
            submitEmptyText: true,
            model: this.model,
            scope: this,
            success: function(form, action) {
                this.setLoading(false);
                me.onSaveSuccess(form, action);
            },
            failure: function(form, action) {
                this.setLoading(false);
                me.onSaveFailure(form, action);
            }
        });
    },

    onSaveSuccess: function(form, action) {
        var record = action.record;        
        devilry.extjshelpers.NotificationManager.show({
            title: 'Save successful',
            message: this.saveSuccessMessage
        });
        this.fireEvent('saveSucess', record);
    },

    onSaveFailure: function(record, action) {
        var errormessages = action.operation.responseData.items.errormessages;
        var me = this;
        Ext.each(errormessages, function(errormessage) {
            me.errorlist.addError(errormessage);
        });
    }
});


/**
 * Tooltip classes for Assignmentgroup.
 * 
 */
Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.AssignmentGroup', {
 
    tooltip_models: ["StaticFeedbackNext", 'StaticFeedbackPrevious',
                        'BrowseFiles', 'AboutTheDelivery',
                        'CreateNewDeadline', 'OtherDeliveries',
                        'SearchField'
                    ],
 
    prefix: 'devilry.extjshelpers.tooltips.assignmentgroup.AssignmentGroup',
 
    requires: [
        'devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext',
        'devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles'
    ],
    
    initComponent: function() { 

        this.feedback_next = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext', {});
        this.feedback_previous = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackPrevious', {});   
        //this.browse_files = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles', {});
        this.about = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.AboutTheDelivery', {});
        this.create_new_deadline = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.CreateNewDeadline', {});
        this.other_deliveries = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.OtherDeliveries', {});
        this.search_field = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.SearchField', {});
        this.warning_field = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.WarningField', {});
        this.feedback_window = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.FeedbackWindow', {});
    },
    /**
     * Animate all tooltips as a wizard.
     * 
     */    
    animateAndShowAll: function() {
        //TODO activated when HELP button in the upper right corner is pressed
        for (tooltip in this.tooltip_models) {
            console.log(this.tooltip_models[tooltip]);
        }
        console.log(this.prefix);
    },
    
    toString: function() {
        return "Hei dette er klassen sin det!";
    }

});


/** List deliveries on a single group, grouped by deadline. */
Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliveriesonsinglegrouplisting',
    cls: 'widget-deliveriesonsinglegrouplisting',
    requires: [
        'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel'
    ],
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        'Delivery number {number}, ',
        'delivered <span class="time_of_delivery">{time_of_delivery:date}</span>',
        '<tpl if="time_of_delivery &gt; deadline__deadline">',
        '   <span class="after-deadline">(After deadline)</span>',
        '</tpl>'
    ),

    helptext: '<div class="section helpsection">' +
        '   <p>Select a delivery from the list of all deliveries made by this group. The deliveries are grouped by deadline.</p>' +
        '   <p>Deliveries are numbered by the order they are delivered. The first delivery has number <strong>1</strong>.</p>' +
        '   <p>Deliveries are made on a specific deadline. Students can deliver after the deadline, as long as the group is open. However when a delivery was made after the deadline, it is shown by a message after the time of delivery.</p>' +
        '</div>',

    config: {
        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            enableGroupingMenu: false,
            groupHeaderTpl: 'Deadline: {name:date}' // {name} is the current data from the groupField for some reason
        });

        this.pagingtoolbar = Ext.widget('pagingtoolbar', {
            store: this.store,
            dock: 'bottom',
            displayInfo: false
        });

        var me = this;
        Ext.apply(this, {
            features: [groupingFeature],
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, deliveryrecord) {
                    //console.log(deliveryrecord.data);
                    return this.rowTpl.apply(deliveryrecord.data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectDelivery
            },
            dockedItems: [this.pagingtoolbar, {
                xtype: 'panel',
                html: this.helptext,
                dock: 'right',
                width: 300
            }]
        });

        this.store.addListener('load', this.onLoadStore, this);

        this.callParent(arguments);
    },

    /**
     * @private
     */
    onLoadStore: function() {
        if(this.store.totalCount == 0) {
            this.up('window').close();
        };
        //this.removeDocked(this.pagingtoolbar);
        //this.addDocked({
            //xtype: 'box',
            //dock: 'top',
            //padding: 10,
            //frame: true,
            //html: 'This group has no deliveries. Close this window and '
        //});
    },

    /**
     * @private
     */
    onSelectDelivery: function(grid, deliveryRecord) {
        this.delivery_recordcontainer.setRecord(deliveryRecord);
        this.up('window').close();
    },
});


Ext.define('devilry.markup.MarkdownFullEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.markdownfulleditor',
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.HelpWindow'
    ],

    markdownHelp: Ext.create('Ext.XTemplate',
        '   <h1>Devilry-flavoured markdown</h1>',
        '   <p>Devilry uses a special configuration of a markup language named Markdown.</p>',
        '   <ul class="right_toc">',
        '       <li><a href="#{idprefix}-block-elements">Block elements</a>',
        '           <ul>',
        '               <li><a href="#{idprefix}-para">Paragraphs</a></li>',
        '               <li><a href="#{idprefix}-headers">Headers</a></li>',
        '               <li><a href="#{idprefix}-blockquotes">Blockquotes</a></li>',
        '               <li><a href="#{idprefix}-lists">Lists</a></li>',
        '               <li><a href="#{idprefix}-codeblocks">Code/unformatted</a></li>',
        '           </ul>',
        '       </li>',
        '       <li><a href="#{idprefix}-inline-elements">Inline elements</a>',
        '           <ul>',
        '               <li><a href="#{idprefix}-links">Links</a></li>',
        '               <li><a href="#{idprefix}-emphasis">Emphasis</a></li>',
        '               <li><a href="#{idprefix}-code">Code</a></li>',
        '           </ul>',
        '       </li>',
        '       <li><a href="#{idprefix}-escaping">Escaping</a></li>',
        '       <li><a href="#{idprefix}-math">LaTeX math</a>',
        '           <ul>',
        '               <li><a href="#{idprefix}-inlinemath">Inline</a></li>',
        '               <li><a href="#{idprefix}-blockmath">Block</a></li>',
        '           </ul>',
        '       </li>',
        '   </ul>',


        '   <h2 id="{idprefix}-block-elements">Block elements</h2>',
        '   <h3 id="{idprefix}-para">Paragraphs and Breaks</h3>',
        '   <p>To create a paragraph, simply create a block of text that is not separated by one or more blank lines. Blocks of text separated by one or more blank lines will be parsed as paragraphs.</p>',
        '   <p>If you want to create a line break, end a line with two or more spaces, then hit Return/Enter.</p>',
        
        '   <h3 id="{idprefix}-headers">Headers</h3>',
        '   <p>Write the header text on its own line. Prefix your header text with the number of # characters to specify heading depth. For example:<br/><code># Heading 1</code><br/><code>## My Heading 2</code></p>',
        '   <p></p>',

        '   <h3 id="{idprefix}-blockquotes">Blockquotes</h3>',
        '   <p>Markdown creates blockquotes email-style by prefixing each line with the >. This looks best if you decide to hard-wrap text and prefix each line with a > character, but Markdown supports just putting > before your paragraph.</p>',

        '   <h3 id="{idprefix}-lists">Lists</h3>',
        '   <p>Markdown supports both ordered and unordered lists. To create an ordered list, simply prefix each line with a number (any number will do). To create an unordered list, you can prefix each line with <strong>-</strong>.</p>',

        '   <h3 id="{idprefix}-codeblocks">Code/unformatted blocks</h3>',
        '   <p>Markdown wraps code blocks in pre-formatted tags to preserve indentation in your code blocks. To create a code block, indent the entire block by at least 4 spaces. Markdown will strip the extra indentation you’ve added to the code block.</p>',
        '   <p>To get <strong>syntax highlighting</strong>, add <code>:::somelanguage</code> at the top of a code block. For example:</p>',
        '   <pre>    :::python\n    def sum(a, b):\n        return a + b</pre>',
        '   <p>The syntax hilighter uses Pygments. Check out the <a href="https://github.com/devilry/devilry-django/wiki/Markdown">Devilry wiki</a> for supported programming languages.</p>',


        '   <h2 id="{idprefix}-inline-elements">Inline elements</h2>',
        '   <h3 id="{idprefix}-links">Links</h3>',
        '   <p>To create a link, create a pair of brackets surrounding your link text, immediately followed by a pair of parentheses and write your URL within the parentheses. Example: <code>[Devilry website](http://devilry.org)</code>.</p>',
        '   <p>If you want to create a link that displays the actual URL, markdown allows you to quickly wrap the URL in &lt; and &gt; to do so. For example, the link <a href="http://devilry.org">http://devilry.org</a> is easily produced by writing <code>&lt;http://devilry.org&gt;</code>.</p>',
        
        '   <h3 id="{idprefix}-emphasis">Emphasis</h3>',
        '   <p>Surround you text by single underscore (i.e.: <code>_my text_</code>) for italic text, and by double asterisks (i.e.: <code>**my text**</code>) for bold text.</p>',

        '   <h3 id="{idprefix}-code">Code</h3>',
        '   <p>To create inline spans of code, simply wrap the code in backticks (`). Markdown will turn `myFunction` into <code>myFunction</code>.</p>',


        '   <h2 id="{idprefix}-escaping">Escaping</h2>',
        '   <p>If you want to use a special Markdown character in your document (such as displaying literal asterisks), you can escape the character with a backslash. Markdown will ignore the character directly after a backslash. Example:</p>',
        '   <pre>This is how the &#92;_ (underscore) and &#92;* asterisks characters look.</pre>',

        '   <h2 id="{idprefix}-math">LaTeX Math</h2>',
        '   <p>We provide two methods for writing <a href="http://www.mathjax.org/">MathJax</a> compatible math. <strong>Note:</strong> You must escape <em>backslash</em> as <a href="#{idprefix}-escaping">described above</a>.</p>',

        '   <h3 id="{idprefix}-inlinemath">Inline</h3>',
        '   <p>For inline math, use <code>$math$your math here$/math$</code>. For example:</p>',
        '   <pre>You know that $math$2^3 = 10$/math$ right?</pre>',

        '   <h3 id="{idprefix}-blockmath">Block</h3>',
        '   <p>For a block of math (a centered paragrath), use <code>$mathBlock$your math here$/mathBlock$</code>. For example:</p>',
        '   <pre>$mathblock$\n^3/_7\n$/mathblock$</pre>'
    ),

    initComponent: function() {
        this.helpwindow = Ext.widget('helpwindow', {
            title: 'Devilry-flavoured markdown',
            closeAction: 'hide',
            helptext: this.markdownHelp.apply(idprefix=this.getId())
        });


        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                cls: 'edit-toolbar',
                dock: 'top',
                items: [{
                    xtype: 'button',
                    text: 'h1',
                    cls: 'headbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onH1
                    }
                }, {
                    xtype: 'button',
                    text: 'h2',
                    cls: 'headbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onH2
                    }
                }, {
                    xtype: 'button',
                    text: 'h3',
                    cls: 'headbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onH3
                    }
                }, {xtype: 'box', width: 15}, {
                    xtype: 'button',
                    text: 'b',
                    cls: 'bbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onBold
                    }
                }, {
                    xtype: 'button',
                    text: 'i',
                    cls: 'ibtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onItalic
                    }
                }, {
                    xtype: 'button',
                    text: '{}',
                    scale: 'medium',
                    cls: 'codebtn',
                    listeners: {
                        scope: this,
                        click: this.onCode
                    }
                }, {
                    xtype: 'button',
                    text: 'a',
                    cls: 'linkbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onUrl
                    }
                }, '->', {
                    xtype: 'button',
                    text: '?',
                    cls: 'helpbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onHelp
                    }
                }]
            }],
            items: [{
                xtype: 'textareafield'
            }]
        });
        this.callParent(arguments);
    },

    /**
     * @private
     */
    onH1: function() {
        this.surroundCursorSelection('\n# ', '');
    },
    /**
     * @private
     */
    onH2: function() {
        this.surroundCursorSelection('\n## ', '');
    },
    /**
     * @private
     */
    onH3: function() {
        this.surroundCursorSelection('\n### ', '');
    },

    /**
     * @private
     */
    onBold: function() {
        this.surroundCursorSelection('**');
    },
    /**
     * @private
     */
    onItalic: function() {
        this.surroundCursorSelection('_');
    },
    /**
     * @private
     */
    onCode: function() {
        this.surroundCursorSelection('`');
    },
    /**
     * @private
     */
    onUrl: function() {
        this.surroundCursorSelection('[', '](http://)');
    },

    /**
     * @private
     */
    onBulletList: function() {
        this.surroundCursorSelection('\n- ', '');
    },
    /**
     * @private
     */
    onNumberedList: function() {
        this.surroundCursorSelection('\n1. ', '');
    },
    /**
     * @private
     */
    onBlockQuote: function() {
        this.surroundCursorSelection('\n> ', '');
    },


    /**
     * @private
     */
    getValue: function() {
        return this.getField().getValue();
    },

    /**
     * @private
     */
    setValue: function(value) {
        this.getField().setValue(value);
    },

    /**
     * @private
     */
    getField: function() {
        return this.down('textareafield');
    },

    /**
     * @private
     */
    getCursorSelection: function() {
        var field = this.getField().inputEl;
        if (Ext.isIE) {
            var bookmark = document.selection.createRange().getBookmark();
            var selection = field.dom.createTextRange();
            selection.moveToBookmark(bookmark);

            var before = field.dom.createTextRange();
            before.collapse(true);
            before.setEndPoint("EndToStart", selection);

            var selLength = selection.text.length;

            var start = before.text.length;
            return {
                start: start,
                end: start + selLength
            };
        } else {
            return {
                start: field.dom.selectionStart,
                end: field.dom.selectionEnd
            };
        }
    },
    
    /**
     * @private
     */
    surroundCursorSelection: function(prefix, suffix) {
        if(suffix == undefined) {
            suffix = prefix;
        }
        var selection = this.getCursorSelection();
        var curText = this.getValue();
        var textPrefix = curText.substring(0, selection.start);
        var textSuffix = curText.substring(selection.end, curText.length);
        var selectionText = curText.substring(selection.start, selection.end);
        var result = textPrefix + prefix + selectionText + suffix + textSuffix;
        this.setValue(result);

        var cursorPosition = selection.start + prefix.length;
        this.getField().selectText(cursorPosition, cursorPosition);
    },


    /**
     * @private
     */
    onHelp: function() {
        this.helpwindow.show();
    }
});


/**
 * A dialog that we use to show longer HTML formatted error messages, which
 * Ext.window.MessageBox is not suited to handle.
 * */
Ext.define('devilry_extjsextras.HtmlErrorDialog', {
    extend: 'Ext.window.Window',
    cls: 'devilry_extjsextras_htmlerrordialog bootstrap',
    alias: 'widget.htmlerrordialog',
    requires: [
        'devilry_extjsextras.OkButton'
    ],

    width: 350,
    height: 250,
    modal: true,
    closable: false,
    bodyPadding: 15,

    /** Forwarded to the body element (an Ext.Component) as ``html``. */
    bodyHtml: undefined,

    /** Forwarded to the body element (an Ext.Component) as ``tpl``. */
    bodyTpl: undefined,

    /** Forwarded to the body element (an Ext.Component) as ``data``. */
    bodyData: undefined,

    /**
     * @cfg {String} title
     * Title, default to localized "Error".
     */
    title: gettext('Error'),

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            autoScroll: true,
            items: {
                xtype: 'box',
                tpl: this.bodyTpl,
                data: this.data,
                html: this.bodyHtml
            },

            buttons: ['->', {
                xtype: 'okbutton',
                listeners: {
                    scope: this,
                    click: function() {
                        this.close();
                    },
                    render: function(button) {
                        Ext.defer(function() {
                            button.focus();
                        }, 150);
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.statistics.dataview.FullGridView', {
    extend: 'devilry.statistics.dataview.MinimalGridView',
    cellTpl: Ext.create('Ext.XTemplate',
        '<tpl if="has_feedback">',
        '   <tpl if="is_open">',
        '       <span class="nofeedback">Not finished</span>',
        '   </tpl>',
        '   <tpl if="!is_open">',
        '      {scaled_points:number("0.00")}',
        '      <span class="grade"> ({grade})</span>',
        '      <tpl if="is_passing_grade"> <span class="passing_grade">passed</span></tpl>',
        '      <tpl if="!is_passing_grade"> <span class="not_passing_grade">failed</span></tpl>',
        '   </tpl>',
        '</tpl>',
        '<tpl if="!has_feedback">',
        '   <span class="nofeedback">No feedback</span>',
        '</tpl>'
    ),

    selectedStudentTitleTpl: Ext.create('Ext.XTemplate',
        '{full_name} ({username})'
    ),

    loadData: function() {
        this.loader.requireCompleteDataset(function() {
            this.refreshView();
        }, this);
    },

    getGridColumns: function() {
        var gridColumns = this.callParent();
        gridColumns.push({
            flex: 1,
            xtype: 'numbercolumn',
            format: '0.00',
            text: 'Total points',
            menuDisabled: true,
            dataIndex: 'totalScaledPoints',
            minWidth: 80,
            sortable: true
        });
        var me = this;
        Ext.each(this.loader.assignment_store.data.items, function(assignmentRecord, index) {
            var assignment_id = assignmentRecord.get('id');
            var scaledPointdataIndex = assignment_id + '::scaledPoints';
            gridColumns.push({
                text: assignmentRecord.get('short_name'),
                dataIndex: scaledPointdataIndex,
                flex: 1,
                minWidth: 140,
                menuDisabled: true,
                sortable: true,
                renderer: function(scaled_points, p, studentRecord) {
                    var group = studentRecord.groupsByAssignmentId[assignment_id];
                    if(group.groupInfo) {
                        var tpldata = {
                            scaled_points: scaled_points,
                            is_open: group.groupInfo.is_open,
                            has_feedback: false
                        };
                        if(group.groupInfo.feedback !== null) {
                            Ext.apply(tpldata, {
                                has_feedback: true,
                                is_passing_grade: group.groupInfo.feedback.is_passing_grade,
                                grade: group.groupInfo.feedback.grade
                            });
                        }
                        var result = me.cellTpl.apply(tpldata);
                        return result;
                    } else {
                        return '';
                    }
                }
            });
        }, this);
        return gridColumns;
    },

    createLayout: function() {
        var grid = this.createGrid({
            region: 'center',
            listeners: {
                scope: this,
                select: this._onSelectStudent
            }
        });
        this._detailsPanel = Ext.widget('panel', {
            title: 'Select a student to view their details',
            region: 'south',
            autoScroll: true,
            layout: 'fit',
            height: 200,
            collapsed: true,
            collapsible: true
        });
        this.add({
            xtype: 'container',
            layout: 'border',
            items: [grid, this._detailsPanel]
        });
        //this.up('statistics-dataview').on('selectStudent', this._onSelectStudent, this);
    },

    _onSelectStudent: function(grid, record) {
        this._detailsPanel.removeAll();
        var groupInfos = [];
        Ext.Object.each(record.groupsByAssignmentId, function(assignmentid, group) {
            if(group.groupInfo !== null) {
                groupInfos.push(group.groupInfo);
            }
        }, this);
        this._detailsPanel.setTitle(this.selectedStudentTitleTpl.apply(record.data));
        this._detailsPanel.add({
            xtype: 'statistics-overviewofsinglestudent',
            assignment_store: record.assignment_store,
            groupInfos: groupInfos,
            username: record.get('username'),
            full_name: record.get('full_name'),
            labels: record.get('labels')
        });
        this._detailsPanel.expand();
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.PointSpecEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-pointspeceditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.RangeSelect',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec'
    ],

    config: {
        assignment_store: undefined,
        pointspec: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'statistics-rangeselect',
                height: 160,
                title: 'Require the following amount of points:',
                initialMin: this.pointspec? this.pointspec.min: undefined,
                initialMax: this.pointspec? this.pointspec.max: undefined
            }, {
                xtype: 'statistics-listofassignments',
                assignment_store: this.assignment_store,
                flex: 1,
                selected_assignments: this.pointspec? this.pointspec.assignments: undefined,
                title: '... in total on the following assignments:',
                rowPrefix: 'Highest score of: ',
                rowSplitter: ', '
            }]
        });
        this.callParent(arguments);
    },

    getResult: function() {
        var range = this.down('statistics-rangeselect').getForm().getFieldValues();
        var assignments = this.down('statistics-listofassignments').getArrayOfAssignmentIds();
        var pointSpec = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', {
            assignments: assignments,
            min: range.min,
            max: range.max
        });
        return pointSpec;
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow', {
    extend: 'Ext.window.Window',
    title: gettext('To-do list (Open groups on this assignment)'),
    height: 370,
    width: 750,
    modal: true,
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList'
    ],

    /**
     * @cfg
     */
    assignmentgroupmodelname: undefined,

    /**
     * @cfg
     */
    assignmentgroup_recordcontainer: undefined,

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'assignmentgrouptodolist',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                assignmentgroupmodelname: this.assignmentgroupmodelname
            }
        });
        this.callParent(arguments);
    }
});


/** Default config for the Create New window, which is opened to create an item
 * in the admin interface. */
Ext.define('devilry.administrator.DefaultCreateWindow', {
    extend: 'devilry.administrator.DefaultEditWindow',
    title: 'Create new',

    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` for the url to visit on successful save. The
         * template gets the record data as input.
         */
        successUrlTpl: undefined
    },

    onSaveSuccess: function(record) {
        window.location.href = this.successUrlTpl.apply(record.data);
    }
});


Ext.define('devilry_header.SearchMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_searchmenu',
    cls: 'devilryheader_searchmenu',

    requires: [
        'devilry_authenticateduserinfo.UserInfo',
        'devilry_header.store.StudentSearchResults',
        'devilry_header.StudentSearchResultsView',
        'devilry_header.store.ExaminerSearchResults',
        'devilry_header.ExaminerSearchResultsView',
        'devilry_header.store.AdminSearchResults',
        'devilry_header.AdminSearchResultsView'
    ],

    initComponent: function() {
        this._setupAutosizing();
        Ext.apply(this, {
            layout: 'anchor',
            floating: true,
            frame: false,
            border: 0,
//            autoShow: true,
            autoScroll: true,
            topOffset: 30,
            padding: 20,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'textfield',
                emptyText: gettext('Search') + ' ...',
                enableKeyEvents: true,
                itemId: 'searchfield',
                cls: 'searchmenu_searchfield',
                listeners: {
                    scope: this,
                    change: this._onSearchFieldChange,
                    keypress: this._onSearchFieldKeyPress
                }
            }, {
                xtype: 'container',
                itemId: 'searchResultsContainer',
                layout: 'column',
                items: [],
                listeners: {
                    scope: this,
                    render: this._onRenderSearchResultsContainer
                }
            }]
        });
        this.callParent(arguments);
    },

    _onRenderSearchResultsContainer:function () {
        devilry_authenticateduserinfo.UserInfo.load(function(userInfoRecord) {
            this._addSearchResultViews(userInfoRecord);
        }, this);
    },

    _addSearchResultViews:function (userInfoRecord) {
        var container = this.down('#searchResultsContainer');
        var views = [];

        this.isAdmin = userInfoRecord.isAdmin();
        this.isExaminer = userInfoRecord.get('is_examiner');
        this.isStudent = userInfoRecord.get('is_student');
        var rolecount = 0;
        if(this.isAdmin) {
            rolecount ++;
        }
        if(this.isExaminer) {
            rolecount ++;
        }
        if(this.isStudent) {
            rolecount ++;
        }
        var columnWidth = 1.0 / rolecount;
        var showHeading = rolecount > 1;

        var listeners = {
            scope: this,
            resultLinkClick: this._onResultLinkClick
        };
        if(this.isStudent) {
            views.push({
                xtype: 'devilry_header_studentsearchresults',
                columnWidth: columnWidth,
                showHeading: showHeading,
                store: Ext.create('devilry_header.store.StudentSearchResults'),
                listeners: listeners
            });
        }
        if(this.isExaminer) {
            views.push({
                xtype: 'devilry_header_examinersearchresults',
                columnWidth: columnWidth,
                showHeading: showHeading,
                store: Ext.create('devilry_header.store.ExaminerSearchResults'),
                listeners: listeners
            });
        }
        if(this.isAdmin) {
            views.push({
                xtype: 'devilry_header_adminsearchresults',
                columnWidth: columnWidth,
                showHeading: showHeading,
                store: Ext.create('devilry_header.store.AdminSearchResults'),
                listeners: listeners
            });
        }
        container.add(views);
    },


    _onSearchFieldChange:function (field) {
        if(Ext.isEmpty(this.task)) {
            this.task = new Ext.util.DelayedTask(this._search, this, [field]);
        }
        this.task.delay(500);
    },

    _onSearchFieldKeyPress:function (field, e) {
        if(e.getKey() === e.ENTER) {
            if(!Ext.isEmpty(this.task)) {
                this.task.cancel();
            }
            this._search(field);
        }
    },

    _search:function (field) {
        var search = field.getValue();
        if(this.isAdmin) {
            this.down('devilry_header_adminsearchresults').search(search);
        }
        if(this.isExaminer) {
            this.down('devilry_header_examinersearchresults').search(search);
        }
        if(this.isStudent) {
            this.down('devilry_header_studentsearchresults').search(search);
        }
    },


    //
    //
    // Autoresize to window size
    //
    //

    _setupAutosizing: function() {
        // Get the DOM disruption over with before the component renders and begins a layout
        Ext.getScrollbarSize();

        // Clear any dimensions, we will size later on
        this.width = this.height = undefined;

        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShow, this);
    },

    _onWindowResize: function() {
        if(this.isVisible()) {
            this._setSizeAndPosition();
        }
    },

    _setSizeAndPosition: function() {
        var bodysize = Ext.getBody().getViewSize();
        this.setSize({
            width: bodysize.width,
            height: bodysize.height - this.topOffset
        });
        this.setPagePosition(0, this.topOffset);
    },

    _onShow: function() {
        this._setSizeAndPosition();
        Ext.defer(function () {
            this.down('#searchfield').focus();
//            this.down('#searchfield').setValue('Obligatorisk oppgave 1');
        }, 300, this);
    },

    _onResultLinkClick:function () {
        this.hide();
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
    alias: 'widget.createnewdeadlinewindow',
    cls: 'widget-createnewdeadlinewindow',
    title: 'Create deadline',
    width: 700,
    height: 450,

    requires: [
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.Deadline'
    ],

    assignmentgroupid: undefined,
    deadlinemodel: undefined,

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var deadlineRecord = Ext.create(this.deadlinemodel, {
            'assignment_group': this.assignmentgroupid
        });

        Ext.apply(this, {
            editpanel: Ext.widget('restfulsimplified_editpanel', {
                model: this.deadlinemodel,
                editform: Ext.create('devilry.extjshelpers.forms.Deadline'),
                record: deadlineRecord
            })
        });
        this.callParent(arguments);
    }
});


/** SearchWidget used in every page in the entire administrator interface.
 *
 * Enables users to search for everything (like the dashboard) or just within
 * the current item.
 * */
Ext.define('devilry.administrator.AdministratorSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.DashboardSearchWidget',

    nodeRowTpl: [
        '<div class="section popuplistitem">',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    subjectRowTpl: [
        '<div class="section popuplistitem">',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    periodRowTpl: [
        '<div class="section popuplistitem">',
        '    <p class="path">{parentnode__short_name}</p>',
        '    <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    /**
    * @cfg
    * Url prefix. Should be the absolute URL path to /administrator/.
    */
    urlPrefix: '',

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: gettext('Nodes'),
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedNode'),
                filterconfig: {
                    type: 'node'
                },
                resultitemConfig: {
                    tpl: this.nodeRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'node/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Subjects'),
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedSubject'),
                filterconfig: {
                    type: 'subject'
                },
                resultitemConfig: {
                    tpl: this.subjectRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'subject/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Periods'),
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedPeriod'),
                filterconfig: {
                    type: 'period'
                },
                resultitemConfig: {
                    tpl: this.periodRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'period/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Assignments'),
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedAssignment'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: this.assignmentRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignment/{id}'
                    },
                    menuitems: [{
                        text: 'Show deliveries',
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Groups'),
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Deliveries'),
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedDelivery'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: this.deliveryRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.statistics.dataview.DataView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-dataview',
    layout: 'fit',

    requires: [
        'devilry.extjshelpers.SearchField',
        'devilry.statistics.dataview.SelectViewCombo',
        'devilry.statistics.dataview.MinimalGridView',
        'devilry.statistics.ClearFilters',
        'devilry.statistics.ScalePointsPanel',
        'devilry.statistics.dataview.FullGridView'
    ],

    config: {
        loader: undefined,
        availableViews: [{
            clsname: 'devilry.statistics.dataview.MinimalGridView',
            label: 'View: Minimal'
        }, {
            clsname: 'devilry.statistics.dataview.FullGridView',
            label: 'View: Detailed'
        }],
        defaultViewClsname: 'devilry.statistics.dataview.FullGridView'
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var selectViewStore = Ext.create('Ext.data.Store', {
            fields: ['clsname', 'label'],
            data: this.availableViews,
            proxy: 'memory'
        });
        Ext.apply(this, {
            tbar: [{
                xtype: 'searchfield',
                width: 250,
                emptyText: 'Search...',
                listeners: {
                    scope: this,
                    newSearchValue: this._search,
                    emptyInput: function() { this._search(); }
                }
            }, {
                xtype: 'button',
                text: 'x',
                listeners: {
                    scope: this,
                    click: function() {
                        this.down('searchfield').setValue('');
                    }
                }
            }, '->', {
                xtype: 'statistics-clearfilters',
                loader: this.loader,
                listeners: {
                    scope: this,
                    filterClearedPressed: function() {
                        this.down('searchfield').setValue('');
                    }
                }
            }, {
                xtype: 'button',
                text: 'Change weight of assignments',
                iconCls: 'icon-edit-16',
                itemId: 'changeWeightButton',
                hidden: true,
                listeners: {
                    scope: this,
                    click: this._onScaleAssignments
                }
            }, {
                xtype: 'tbseparator',
                itemId: 'changeWeightButtonSeparator'
            }, {
                xtype: 'statistics-dataview-selectviewcombo',
                availableViews: this.availableViews,
                defaultViewClsname: this.defaultViewClsname,
                listeners: {
                    scope: this,
                    selectView: this._setView
                }
            }]
        });
        this.callParent(arguments);
        this._setView(this.defaultViewClsname);
    },

    _search: function(input) {
        if(input) {
            this.loader.clearFilter();
            this.loader.filterBy('Search for: ' + input, function(record) {
                var username = record.get('username') || '';
                var full_name = record.get('full_name') || '';
                return username.search(input) != -1 || full_name.search(input) != -1;
            }, this);
        } else {
            this.loader.clearFilter();
        }
    },

    _setView: function(clsname) {
        this.removeAll();
        if(clsname === 'devilry.statistics.dataview.FullGridView') {
            this.down('#changeWeightButton').show();
            this.down('#changeWeightButtonSeparator').show();
        } else {
            this.down('#changeWeightButton').hide();
            this.down('#changeWeightButtonSeparator').hide();
        }
        this._layout = Ext.create(clsname, {
            loader: this.loader
        });
        this.add(this._layout);
    },

    refresh: function() {
        this._layout.refresh();
    },

    getSelectedStudents: function() {
        return this._layout.getSelectedStudents();
    },

    _onScaleAssignments: function(button) {
        Ext.widget('window', {
            width: 350,
            height: 250,
            title: button.text,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'statistics-scalepointspanel',
                store: this.loader.assignment_store,
                loader: this.loader
            }
        }).show();
    }
});


Ext.define('devilry.administrator.studentsmanager.ManuallyCreateUsers', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.manuallycreateusers',
    frame: false,
    border: false,

    requires: [
        'devilry.extjshelpers.AsyncActionPool',
        'devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow'
    ],

    layout: {
        type: 'vbox',
        align: 'stretch' // Child items are stretched to full width
    },

    config: {
        /**
         * @cfg
         * Lines to fill in on load (one line for each element in the array).
         */
        initialLines: undefined,

        currentGroupRecords: undefined,
        assignmentrecord: undefined,
        deadlinemodel: undefined,
        suggestedDeadline: undefined
    },

    helptext:
        '<div class="section helpsection">' +
        //'   <h1>Help</h1>' +
        '   <p>Students are organized in <em>assignment groups</em>. You should specify <strong>one</strong> <em>assignment group</em> on each line in the input box.</p>' +
        '   <p>Check <strong>Ignore duplicates</strong> to ignore any assignment groups that contains students that already has an assignment group on this assignment.</p>' +
        '   <h2>Common usage examples</h2>' +
        '   <h3>Individual deliveries</h3>' +
        '   <p>Very often, an assignment requires <strong>individual</strong> deliveries and feedback. In this case, each <em>assignment group</em> should contain a single student. In this case, the input box should contain something similar to this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">bob\nalice\neve\ndave</pre>' +

        '   <h3>Group deliveries</h3>' +
        '   <p>When students are supposed to <strong>cooperate</strong> on the same assignment, they should be in the same <em>assignment group</em>. In this case, the input box should contain something similar to this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">bob, alice\neve, dave, charlie</pre>' +

        '   <h3>Anonymous assignments</h3>' +
        '   <p>When you have specified the the assignment is anonymous, you may want to give each student a <em>candidate-id</em> that the examiners will see instead of the username. Specify candidate-id with a colon at the end of each username like this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">bob:10, alice:232\ncharlie:4X23</pre>' +

        '   <h3>Project groups and group naming</h3>' +
        '   <p>It is often useful to give an <em>assignment group</em> a <strong>name</strong>. The name is primarily intended for project assignments, where it is useful to name a group after their project. However, the name can be used for other purposes, such as <em>tagging</em> of groups of special interest. Since you can search for groups by name, you can name multiple groups with tags, such as <em>exceptional</em>, and find these groups using the search field. You specify group name like this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">Secret project:: bob, alice\nTake over world:: eve, dave, charlie</pre>' +

        '   <h2>Input format explained in detail</h2>' +
        '   <p>The format used to create the assignment groups is:</p>' +
        '   <ul>' +
        '       <li>One assignment group on each line.</li>' +
        '       <li>Each username is separated by a comma.</li>' +
        '       <li>Group name is identified by two colons at the end of the name, and must be placed at the beginning of the line.</li>' +
        '       <li>A group name or at least one username is required for each group.</li>' +
        '       <li>An optional <em>candidate-id</em> for a candidate is denoted by a colon and the <em>candidate-id</em> after the username.</li>' +
        '       <li>A an optional comma-separated list of tags surrounded by parentheses.</li>' +
        '   </ul>' +
        '</div>',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.assignmentGroupModelCls = 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup';

        var currentValue = "";
        if(this.initialLines) {
            Ext.each(this.initialLines, function(line, index) {
                currentValue += Ext.String.format('{0}\n', line);
            });
        };

        this.userinput = Ext.widget('textareafield', {
            //hideLabel: true,
            fieldLabel: 'Assignment groups',
            labelAlign: 'top',
            labelWidth: 100,
            labelStyle: 'font-weight:bold',
            emptyText: 'Read the text on your right hand side for help...',
            flex: 10,
            value: currentValue
        });

        this.clearDupsCheck = Ext.widget('checkbox', {
            boxLabel: "Ignore duplicates?",
            checked: true
        });
        //this.userinput.setValue('dewey\nlouie:401, hue\n\nSaker azz:: donald, dela:30');
        //this.userinput.setValue('dewey\nlouie:401');
        Ext.apply(this, {
            //items: this.userinput,

            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [{
                margin: 10,
                flex: 10,
                xtype: 'panel',
                border: false,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [this.userinput, this.clearDupsCheck],
            }, {
                flex: 10,
                xtype: 'box',
                padding: 20,
                autoScroll: true,
                html: this.helptext
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    iconCls: this.assignmentrecord.get('delivery_types') == 1? 'icon-save-32': 'icon-next-32',
                    scale: 'large',
                    text: this.assignmentrecord.get('delivery_types') == 1? 'Create groups': 'Select deadline',
                    listeners: {
                        scope: this,
                        click: this.onCreate
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    /**
     * @private
     */
    parseGroupSpec: function(groupSpec) {
        groupSpec = Ext.String.trim(groupSpec);
        if(groupSpec == "") {
            return null;
        }
        groupSpecObj = {
            name: null,
            is_open: true,
            fake_candidates: [],
            fake_examiners: [],
            fake_tags: []
        };

        var nameSplit = groupSpec.split(/\s*::\s*/);
        if(nameSplit.length > 1) {
            groupSpecObj.name = nameSplit[0];
            groupSpec = nameSplit[1];
        }

        var usernamesAndTags = this.statics().parseUsernamesAndTags(groupSpec);
        groupSpecObj.fake_tags = usernamesAndTags.tags;

        Ext.Array.each(usernamesAndTags.usernames, function(candidateSpec) {
            groupSpecObj.fake_candidates.push(devilry.administrator.studentsmanager.StudentsManagerManageGroups.parseCandidateSpec(candidateSpec));
        }, this);
        return groupSpecObj;
    },

    /**
     * @private
     */
    parseTextToGroupSpec: function(rawValue) {
        var asArray = rawValue.split('\n');
        var resultArray = [];
        var me = this;
        Ext.Array.each(asArray, function(groupSpec) {
            var groupSpecObj = me.parseGroupSpec(groupSpec);
            if(groupSpecObj != null) {
                resultArray.push(groupSpecObj);
            }
        });
        return resultArray;
    },

    /**
     * @private
     */
    createAll: function(parsedArray) {
        this.getEl().mask(Ext.String.format('Saving {0} groups', parsedArray.length));
        this.finishedCounter = 0;
        this.unsuccessful = [];
        this.parsedArray = parsedArray;
        Ext.Array.each(this.parsedArray, function(groupSpecObj) {
            this.createGroup(groupSpecObj);
        }, this);
    },

    /**
     * @private
     */
    clearDuplicates: function(parsedArray) {
        var current_usernames = []
        Ext.each(this.currentGroupRecords, function(groupRecord) {
            var group_usernames = groupRecord.data.candidates__student__username;
            current_usernames = Ext.Array.merge(current_usernames, group_usernames);
        });

        var uniqueGroupSpecObjs = [];
        var new_usernames = [];
        Ext.Array.each(parsedArray, function(groupSpecObj) {
            var dups = false;
            Ext.Array.each(groupSpecObj.fake_candidates, function(candidate) {
                if(Ext.Array.contains(current_usernames, candidate.username) || Ext.Array.contains(new_usernames, candidate.username)) {
                    dups = true;
                }
            }, this);
            if(!dups) {
                Ext.Array.each(groupSpecObj.fake_candidates, function(candidate) {
                    new_usernames.push(candidate.username);
                });
                uniqueGroupSpecObjs.push(groupSpecObj);
            }
        }, this);

        return uniqueGroupSpecObjs;
    },


    _createGroupCallback: function(pool, groupSpecObj) {
        var completeGroupSpecObj = {
            parentnode: this.assignmentrecord.data.id
        };
        Ext.apply(completeGroupSpecObj, groupSpecObj);
        var group = Ext.create(this.assignmentGroupModelCls, completeGroupSpecObj);
        group.save({
            scope: this,
            callback: function(records, op) {
                pool.notifyTaskCompleted();
                if(op.success) {
                    this.createDeadline(records);
                } else {
                    this.finishedCounter ++;
                    this.unsuccessful.push(groupSpecObj);
                    this.getEl().mask(
                        Ext.String.format('Finished saving {0}/{1} groups',
                            this.finishedCounter, this.parsedArray.length, this.parsedArray.length
                        )
                    );
                    if(this.finishedCounter == this.parsedArray.length) {
                        this.onFinishedSavingAll();
                    }
                }
            }
        });
    },

    /**
     * @private
     */
    createGroup: function(groupSpecObj) {
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            args: [groupSpecObj],
            callback: this._createGroupCallback
        });
    },

    _createDeadlineCallback: function(pool, assignmentGroupRecord) {
        devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines.createDeadline(
            assignmentGroupRecord, this.deadlineRecord, this.deadlinemodel, {
                scope: this,
                callback: function(records, op) {
                    pool.notifyTaskCompleted();
                    if(op.success) {
                        this.onCreateDeadlineSuccess();
                    } else {
                        console.error('Failed to save deadline record');
                    }
                }
            }
        );
    },

    /**
     * @private
     */
    createDeadline: function(assignmentGroupRecord) {
        if(this.assignmentrecord.get('delivery_types') == 1) {
            // For non-electronic assignments, a "dummy deadline" is created automatically
            this.onCreateDeadlineSuccess();
        } else {
            devilry.extjshelpers.AsyncActionPool.add({
                scope: this,
                args: [assignmentGroupRecord],
                callback: this._createDeadlineCallback
            });
        }
    },

    /**
     * @private
     */
    onCreateDeadlineSuccess: function() {
        this.finishedCounter ++;
        this.getEl().mask(Ext.String.format('Finished saving {0}/{1} groups',
            this.finishedCounter, this.parsedArray.length,
            this.parsedArray.length
        ));
        if(this.finishedCounter == this.parsedArray.length) {
            this.onFinishedSavingAll();
        }
    },

    /**
     * @private
     */
    groupSpecObjToString: function(groupSpecObj) {
        var groupSpecStr = "";
        if(groupSpecObj.name) {
            groupSpecStr += groupSpecObj.name + ":: ";
        }
        Ext.Array.each(groupSpecObj.fake_candidates, function(candidate, index) {
            groupSpecStr += candidate.username;
            if(candidate.candidate_id) {
                groupSpecStr += ':' + candidate.candidate_id;
            }
            if(index != groupSpecObj.fake_candidates.length-1) {
                groupSpecStr += ', ';
            }
        }, this);
        return groupSpecStr;
    },

    /**
     * @private
     */
    groupSpecObjArrayToString: function(groupSpecObjArray) {
        var str = "";
        Ext.Array.each(groupSpecObjArray, function(groupSpecObj) {
            str += this.groupSpecObjToString(groupSpecObj) + '\n';
        }, this);
        return str;
    },

    /**
     * @private
     */
    onFinishedSavingAll: function() {
        this.getEl().unmask();
        if(this.unsuccessful.length == 0) {
            this.onSuccess();
        } else {
            this.onFailure();
        }
    },

    /**
     * @private
     */
    onSuccess: function() {
        var me = this;
        Ext.MessageBox.show({
            title: 'Success',
            msg: Ext.String.format('Created {0} assignment groups.', this.finishedCounter),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.INFO,
            fn: function() {
                me.userinput.setValue('');
                me.up('window').close();
            }
        });
    },

    /**
     * @private
     */
    onFailure: function() {
        this.userinput.setValue(this.groupSpecObjArrayToString(this.unsuccessful));
        Ext.MessageBox.show({
            title: 'Error',
            msg: Ext.String.format(
                'Failed to create {0} of {1} assignment groups. This is usually caused by invalid usernames. The groups with errors have been re-added to the input box.',
                this.unsuccessful.length, this.finishedCounter),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
    },

    /**
     * @private
     */
    onCreate: function() {
        this.getEl().mask('Parsing input');
        var parsedArray = this.parseTextToGroupSpec(this.userinput.getValue());
        this.getEl().unmask();
        var clearDuplicates = this.clearDupsCheck.getValue();
        if(clearDuplicates) {
            cleanedParsedArray = this.clearDuplicates(parsedArray);
            var diff = Ext.Array.difference(parsedArray, cleanedParsedArray);
            var me = this;
            if(diff.length > 0) {
                this.showClearedDuplicatesInfoWindow(cleanedParsedArray, diff);
            } else {
                this.checkForNoGroups(parsedArray);
            }
        } else {
            this.checkForNoGroups(parsedArray);
        }
    },

    /**
     * @private
     */
    showClearedDuplicatesInfoWindow: function(cleanedParsedArray, diff) {
        var me = this;
        var msg = Ext.create('Ext.XTemplate',
            '<div class="section helpsection">',
            '<p>The groups listed below contains at least one student that already has a group on this assignment. If you choose <em>Next</em>, these groups will be ignored. Choose <em>Cancel</em> to return to the <em>Create assignment groups</em> window.</p>',
            '<ul>',
            '   <tpl for="diff"><li>',
            '       <tpl if="name">',
            '           {name}:: ',
            '       </tpl>',
            '       <tpl for="fake_candidates">',
            '           {username}<tpl if="candidate_id">{candidate_id}</tpl><tpl if="xindex &lt; xcount">, </tpl>',
            '       </tpl>',
            '       <tpl if="fake_tags.length &gt; 0">',
            '          (<tpl for="fake_tags">',
            '              {.}<tpl if="xindex &lt; xcount">, </tpl>',
            '          </tpl>)',
            '       </tpl>',
            '   </tpl></li>',
            '</ul></div>'
        ).apply({diff: diff});
        Ext.widget('devilry_autosizedwindow', {
            width: 500,
            height: 400,
            modal: true,
            title: 'Confirm clear duplicates',
            layout: 'fit',
            items: {
                xtype: 'panel',
                border: false,
                autoScroll: true,
                html: msg
            },
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: [{
                    xtype: 'button',
                    scale: 'large',
                    text: 'Cancel',
                    listeners: {
                        click: function() {
                            this.up('window').close();
                        }
                    }
                }, '->', {
                    xtype: 'button',
                    iconCls: 'icon-next-32',
                    scale: 'large',
                    text: 'Next',
                    listeners: {
                        click: function() {
                            this.up('window').close();
                            me.checkForNoGroups(cleanedParsedArray, 'No groups where created because all groups contained students that already have a group, and you chose to ignore duplicates.');
                        }
                    }
                }]
            }]
        }).show();
    },

    /**
     * @private
     */
    checkForNoGroups: function(parsedArray, noGroupsMsg) {
        if(parsedArray.length == 0) {
            var msg = noGroupsMsg || 'You must add at least one group in the <em>assignment groups</em> box.';
            Ext.MessageBox.alert('No assignment groups created', msg);
            this.up('window').close();
        } else {
            if(this.assignmentrecord.get('delivery_types') == 1) {
                this.createAll(parsedArray);
            } else {
                this.selectDeadline(parsedArray);
            }
        }
    },

    selectDeadline: function(parsedArray) {
        var me = this;
        var createDeadlineWindow = Ext.widget('multicreatenewdeadlinewindow', {
            width: this.up('window').getPreferredWidth(),
            height: this.up('window').getPreferredHeight(),
            deadlinemodel: this.deadlinemodel,
            suggestedDeadline: this.suggestedDeadline,
            deadlineRecord: this.deadlineRecord,
            onSaveSuccess: function(record) {
                this.close();
                me.deadlineRecord = record;
                var publishing_time = me.assignmentrecord.data.publishing_time;
                var period_end_time = me.assignmentrecord.data.parentnode__end_time;
                if(record.data.deadline <= publishing_time || record.data.deadline >= period_end_time) {
                    var error = Ext.create('Ext.XTemplate',
                        'Deadline must be between {publishing_time:date} and {period_end_time:date}.'
                    ).apply({publishing_time: publishing_time, period_end_time: period_end_time});
                    Ext.MessageBox.show({
                        title: 'Error',
                        msg: error,
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR
                    });
                } else {
                    me.createAll(parsedArray);
                }
            }
        });
        createDeadlineWindow.show();
    },


    statics: {
        parseUsernamesAndTags: function(rawstr) {
            var tags = [];
            var tagSplit = rawstr.split(/\s*\(\s*/);
            if(tagSplit.length > 1) {
                rawstr = tagSplit[0];
                var tagsString = tagSplit[1];
                tagsString = tagsString.replace(/\)/, "");
                tags = tagsString.split(/\s*,\s*/);
            }
            return {
                usernames: rawstr.split(/\s*,\s*/),
                tags: tags
            };
        }
    },
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterEditor', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.statistics-filtereditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.MustPassEditor',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.PointSpecEditor'
    ],

    config: {
        assignment_store: undefined,
        filterRecord: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var filter;
        if(this.filterRecord) {
            filter = this.filterRecord.get('filter');
        }
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-mustpasseditor',
                title: 'Must pass',
                must_pass: filter? filter.must_pass: undefined,
                assignment_store: this.assignment_store
            }, {
                xtype: 'statistics-pointspeceditor',
                title: 'Must have points',
                pointspec: filter? filter.pointspec: undefined,
                assignment_store: this.assignment_store
            }],

            bbar: ['->', {
                xtype: 'button',
                text: this.filterRecord? 'Update rule': 'Add rule',
                iconCls: this.filterRecord? 'icon-save-32': 'icon-add-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this._onAdd
                }
            }]
        });
        this.callParent(arguments);
    },

    getFilterArgs: function() {
        var must_pass = this.down('statistics-mustpasseditor').getResult();
        var pointspec;
        try {
            pointspec = this.down('statistics-pointspeceditor').getResult();
        } catch(e) {
            this.down('statistics-pointspeceditor').show();
            Ext.MessageBox.alert('Error', e);
            return false;
        }
        return {
            must_pass: must_pass,
            pointspecArgs: pointspec
        };
    },

    _onAdd: function() {
        var filterArgs = this.getFilterArgs();
        if(filterArgs !== false) {
            this.fireEvent('addFilter', filterArgs, this.filterRecord);
        }
    }
});


/** Field for selection of foreign key values.
 *
 * **NOTE**: Assumes that the foreign key is a number and that its value is in
 * the ``id`` attribute.
 */
Ext.define('devilry.extjshelpers.formfields.ForeignKeySelector', {
    extend: 'Ext.form.field.Trigger',
    alias: 'widget.foreignkeyselector',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeyBrowser'
    ],

    config: {
        /**
         * @cfg
         * Ext.XTemplate for the selected item.
         */
        displayTpl: '{id}',

        /**
         * @cfg
         * Text to display when field is blank.
         */
        emptyText: 'Select something',

        /**
         * @cfg
         * Ext.XTemplate for items in the dropdown.
         */
        dropdownTpl: '{id}',

        /**
         * @cfg
         * The ``Ext.data.Model`` where the data is located. The model must have a proxy.
         */
        model: undefined,

        /**
         * @cfg
         * Allow empty?
         */
        allowEmpty: false
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.model = Ext.ModelManager.getModel(this.model);
        this.displayTpl = Ext.create('Ext.XTemplate', this.displayTpl);
        this.realValue = '';
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            editable: false,
            listeners: {
                scope: this,
                focus: this.onTriggerClick
            }
        });
        this.callParent(arguments);
    },

    onTriggerClick: function() {
        var win = Ext.create('Ext.window.Window', {
            height: 300,
            width: this.getWidth(),
            modal: true,
            layout: 'fit',
            items: {
                xtype: 'foreignkeybrowser',
                model: this.model,
                foreignkeyselector: this,
                allowEmpty: this.allowEmpty,
                tpl: this.dropdownTpl
            },
            listeners: {
                scope: this,
                show: this._onShowWindow
            }
        });
        win.show();
    },

    _onShowWindow: function(win) {
        try {
            win.alignTo(this, 'bl', [0, 0]);
        } catch(e) {
            Ext.defer(function() {
                win.alignTo(this, 'bl', [0, 0]);
            }, 300, this)
        }
    },
    
    setValue: function(value) {
        var valueType = Ext.typeOf(value);
        if(valueType == 'number') {
            var recordId = value;
            this.model.load(recordId, {
                scope: this,
                success: this.onLoadSuccess,
                failure: this.onLoadFailure
            });
        } else {
            this.callParent([value]);
        }
    },

    getValue: function() {
        return this.realValue;
    },

    getRawValue: function() {
        return this.realValue;
    },

    onLoadSuccess: function(record) {
        this.setRecordValue(record);
    },

    setRecordValue: function(record) {
        this.realValue = record.data.id;
        this.setValue(this.displayTpl.apply(record.data));
    },

    onLoadFailure: function() {
        throw "Failed to load foreign key value.";
    },

    // Triggered by ForeignKeyBrowser.
    onClearValue: function(record) {
        this.realValue = '';
        this.setValue('');
    },

    // Triggered by ForeignKeyBrowser.
    onSelect: function(record) {
        this.setRecordValue(record);
    }
});


/** Panel to show StaticFeedback info.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo', {
    extend: 'Ext.container.Container',
    alias: 'widget.staticfeedbackinfo',
    cls: 'widget-staticfeedbackinfo',
    requires: [
        'devilry.extjshelpers.Pager',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackView',
        'devilry.extjshelpers.SingleRecordContainerDepButton',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    assignmentgroup_recordcontainer: undefined,

    /**
     * @cfg {Ext.data.Store} [filemetastore]
     * FileMeta ``Ext.data.Store``. (Required).
     * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
     * class.
     */
    filemetastore: undefined,

    /**
     * @cfg {object} [staticfeedbackstore]
     * FileMeta ``Ext.data.Store``. (Required).
     * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
     * class.
     */
    staticfeedbackstore: undefined,

    /**
     * @cfg {object} [delivery_recordcontainer]
     * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
     */
    delivery_recordcontainer: undefined,

    titleTpl: [
        '<tpl if="loading">',
            gettext('Loading'), ' ...',
        '<tpl else>',
            '<h2 style="margin: 0 0 5 0;">',
                gettext('Delivery'), ' #{delivery.number}',
            '</h2>',
            '<p>',
                '<tpl if="assignmentgroup.parentnode__delivery_types === 1">',
                    '<span class="label label-info">',
                        gettext('Non-electronic delivery'),
                    '</span>',
                '<tpl else>',
                    gettext('Time of delivery: '),
                    '{[this.formatDatetime(values.delivery.time_of_delivery)]}',
                '</tpl>',
            '</p>',
        '</tpl>', {
            formatDatetime:function (dt) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
            }
        }
    ],


    constructor: function(config) {
        this.addEvents('afterStoreLoadMoreThanZero');
        this.callParent([config]);
        this.initConfig(config);
    },
    
    initComponent: function() {
        this.staticfeedback_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.bodyContent = Ext.create('Ext.container.Container', {
            layout: 'fit',
            autoScroll: true
        });

        var group = this.assignmentgroup_recordcontainer.record;
        Ext.apply(this, {
            layout: 'anchor',
            border: false,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'panel',
                border: false,
                cls: 'bootstrap',
                itemId: 'deliveryTitle',
                bodyStyle: 'background-color: transparent;',
                tpl: this.titleTpl,
                data: {
                    loading: true
                }
            }, {
                xtype: 'filemetabrowserpanel',
                store: this.filemetastore,
                hidden: true
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                itemId: 'isClosedMessage',
                hidden: group.get('is_open'),
                html: [
                    '<p class="alert alert-info">',
                        gettext('This group is closed. Students can not add deliveries on closed groups. Use the button above to re-open it if you need to change their feedback.'),
                    '</p>'
                ].join('')
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                html: [
                    '<h3 style="margin: 20px 0 0 0;">',
                        gettext('Feedback'),
                    '</h3>'
                ].join('')
            }, {
                xtype: 'panel',
                tbar: this.getToolbarItems(),
                layout: 'fit',
                margin: '0 0 20 0',
                items: this.bodyContent
            }]
        });
        this.callParent(arguments);

        this.staticfeedbackstore.pageSize = 1;
        this.staticfeedbackstore.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);

        this.staticfeedback_recordcontainer.addListener('setRecord', this.onSetStaticFeedbackRecord, this);
        this.staticfeedbackstore.addListener('load', this.onLoadStaticfeedbackstore, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDelivery();
        }
        this.delivery_recordcontainer.addListener('setRecord', this.onLoadDelivery, this);
    },

    getToolbarItems: function() {
        var items = ['->', {
            xtype: 'devilrypager',
            store: this.staticfeedbackstore,
            width: 200,
            reverseDirection: true,
            middleLabelTpl: Ext.create('Ext.XTemplate',
                '<tpl if="firstRecord">',
                    '{currentNegativePageOffset})&nbsp;',
                    '{[this.formatDatetime(values.firstRecord.data.save_timestamp)]}',
                '</tpl>', {
                    formatDatetime:function (dt) {
                        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
                    }
                }
            )
        }];
        return items;
    },


    onLoadDelivery: function() {
        this.staticfeedbackstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery',
            comp: 'exact',
            value: this.delivery_recordcontainer.record.data.id
        }]);
        this.staticfeedbackstore.load();

        var deliveryrecord = this.delivery_recordcontainer.record;
        var staticfeedbackStore = deliveryrecord.staticfeedbacks();
        this.down('#deliveryTitle').update({
            loading: false,
            delivery: deliveryrecord.data,
            assignmentgroup: this.assignmentgroup_recordcontainer.record.data,
            feedback: staticfeedbackStore.count() > 0? staticfeedbackStore.data.items[0].data: undefined
        });
    },


    onSetStaticFeedbackRecord: function() {
        var isactive = this.staticfeedbackstore.currentPage === 1;
        this.setBody({
            xtype: 'staticfeedbackview',
            padding: 10,
            singlerecordontainer: this.staticfeedback_recordcontainer,
            extradata: {
                isactive: isactive
            }
        });
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    },

    onLoadStaticfeedbackstore: function(store, records, successful) {
        if(successful) {
            if(records.length === 0) {
                this.bodyWithNoFeedback();
            }
            else {
                this.staticfeedback_recordcontainer.setRecord(records[0]);
                this.fireEvent('afterStoreLoadMoreThanZero');
            }
       } else {
            // TODO: handle failure
        }
    },

    setBody: function(content) {
        this.bodyContent.removeAll();
        this.bodyContent.add(content);
    },


    bodyWithNoFeedback: function() {
        this.setBody({
            xtype: 'box',
            padding: 10,
            cls: 'no-feedback',
            html: 'No feedback'
        });
    }
});


Ext.define('devilry.extjshelpers.forms.administrator.Subject', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_subjectform',
    cls: 'widget-periodform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector'
    ],

    suggested_windowsize: {
        width: 600,
        height: 400
    },

    flex: 8,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': math101'
    }, {
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield',
        emptyText: gettext('Example') + ': MATH101 - Introduction to mathematics'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Node"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedNode',
        emptyText: interpolate(gettext('Select a %(node_term)s'), {
            node_term: gettext('node')
        }, true),
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>'
    }],

    help: [
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.')
    ]
});


Ext.define('devilry.extjshelpers.forms.administrator.Assignment', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_assignmentform',
    cls: 'widget-assignmentform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector',
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    suggested_windowsize: {
        width: 850,
        height: 550
    },

    flex: 5,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },
    defaults: {
        margin: '0 0 10 0'
    },


    items: [{
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': firstassignment'
    }, {
        name: "long_name",
        fieldLabel: gettext("Long name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': Obligatory assignment 1'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Period"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
        emptyText: interpolate(gettext('Select a %(period_term)s'), {
            period_term: gettext('period')
        }, true),
        displayTpl: '{long_name} ({parentnode__short_name}.{short_name})',
        dropdownTpl: '<div class="important">{parentnode__short_name}.{short_name}</div>'+
            '<div class="unimportant">{parentnode__long_name}</div>' +
            '<div class="unimportant">{long_name}</div>'
    }, {
        name: "publishing_time",
        fieldLabel: gettext("Publishing time"),
        xtype: 'devilrydatetimefield',
        value: new Date()
    }, {
        name: "delivery_types",
        fieldLabel: gettext("How do students add deliveries?"),
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        value: 0,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:0, label: gettext("Electronically using Devilry")},
                {value:1, label: gettext("Non-electronic (hand in on paper, oral examination, ...)")}
            ]
        })
    }, {
        name: "deadline_handling",
        fieldLabel: interpolate(gettext("How would you like to handle %(deadlines_term)s?"), {
            deadlines_term: gettext('deadlines')
        }, true),
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        value: DevilrySettings.DEVILRY_DEFAULT_DEADLINE_HANDLING_METHOD,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:0, label: gettext("SOFT: Students can add deliveries after the deadline, but deliveries after the deadline are distinctly highlighted in the examiner and admin interfaces.")},
                {value:1, label: gettext("HARD: Students can not add deliveries after the deadline.")}
            ]
        })
    }, {
        name: "anonymous",
        fieldLabel: gettext("Anonymous?"),
        xtype: 'combobox',
        queryMode: 'local',
        valueField: 'value',
        displayField: 'label',
        forceSelection: true,
        editable: false,
        value: false,
        store: Ext.create('Ext.data.Store', {
            fields: ['value', 'label'],
            data : [
                {value:false, label: gettext("No")},
                {value:true, label: gettext("Yes")}
            ]
        })
    }, {
        xtype: 'hiddenfield',
        name: 'scale_points_percent',
        value: 100
    }],

    help: [
        {state: 'new', text: gettext('Set up the mandatory properties of an assignment. Further customization is available after you create the assignment.')},
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.'),
        gettext('The <strong>publishing time</strong> is the time when students will be able to start adding deliveries on the assignment.'),
        gettext('If you only use Devilry to give feedback, but students deliver through an alternative channel, change <strong>how students add deliveries</strong>. This can also be used if the students deliver through an alternative electronic system such as <em>email</em>.'),
        gettext('If you set <strong>anonymous</strong> to <em>yes</em>, examiners see a <em>candidate-id</em> instead of a username. A candidate-id must be set for each student.')
    ]
});


Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveriesgroupedbydeadline',
    cls: 'widget-deliveriesgroupedbydeadline',
    requires: [
        'devilry.administrator.models.Deadline',
        'devilry.administrator.models.Delivery',
        'devilry.administrator.models.StaticFeedback',
        'devilry.examiner.models.Deadline',
        'devilry.examiner.models.Delivery',
        'devilry.examiner.models.StaticFeedback',
        'devilry.student.models.Deadline',
        'devilry.student.models.Delivery',
        'devilry.student.models.StaticFeedback',

        'devilry.extjshelpers.RestFactory',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGrid',
        'devilry.extjshelpers.assignmentgroup.DeliveriesPanel',
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    autoScroll: true,
//    style: 'border-right: 1px solid #ddd !important; border-top: 1px solid #ddd !important;',
    border: 1,

    /**
    * @cfg {string} [role]
    */
    role: undefined,

    /**
    * @cfg {object} [assignmentgroup_recordcontainer]
    * AssignmentGroup record container. The view is reloaded on the setRecord
    * event.
    */
    assignmentgroup_recordcontainer: undefined,

    /**
    * @cfg {object} [delivery_recordcontainer]
    * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
    * The record is changed when a user selects a delivery.
    */
    delivery_recordcontainer: undefined,

    constructor: function(config) {
        this.addEvents('loadComplete');
        this.callParent(arguments);
    },

    initComponent: function() {
        this.isLoading = true;
        this.assignmentgroup_recordcontainer.on('setRecord', this._onLoadAssignmentGroup, this);
        if(this.assignmentgroup_recordcontainer.record) {
            this._onLoadAssignmentGroup();
        }

        this.callParent(arguments);
        this.on('render', function() {
            Ext.defer(function() {
                this.addLoadMask();
            }, 100, this);
        }, this);
    },

    _onLoadAssignmentGroup: function(groupRecordContainer) {
        var groupRecord = groupRecordContainer.record;
        this.loadAllDeadlines();
    },


    /**
     * @private
     */
    addLoadMask: function() {
        if(this.rendered && this.isLoading) {
            this.getEl().mask('Loading deliveries ...');
        }
    },

    /**
     * @private
     */
    loadAllDeadlines: function() {
        this.isLoading = true;
        this._allDeliveries = [];
        this._tmp_deliveriespanels = [];
        this._tmp_active_feedbacks = [];
        this.addLoadMask();
        this.removeAll();
        var deadlinestore = devilry.extjshelpers.RestFactory.createStore(this.role, 'Deadline', {
            filters: [{
                property: 'assignment_group',
                value: this.assignmentgroup_recordcontainer.record.data.id
            }]
        });
        deadlinestore.proxy.setDevilryOrderby(['-deadline']);
        deadlinestore.loadAll({
            scope: this,
            callback: this.onLoadAllDeadlines
        });
    },

    /**
     * @private
     */
    onLoadAllDeadlines: function(deadlineRecords) {
        Ext.each(deadlineRecords, this.handleSingleDeadline, this);
    },

    /**
     * @private
     */
    handleSingleDeadline: function(deadlineRecord, index, deadlineRecords) {
        var deliveriesStore = deadlineRecord.deliveries();
        deliveriesStore.pageSize = 1000;
        deliveriesStore.load({
            scope: this,
            callback: function(deliveryRecords) {
                if(index === 0) {
                    this._handleLatestDeadline(deadlineRecords[0], deliveryRecords);
                }

                if(deliveryRecords.length === 0) {
                    this.addDeliveriesPanel(deadlineRecords, deadlineRecord, deliveriesStore);
                } else {
                    this.findLatestFeebackInDeadline(deadlineRecords, deadlineRecord, deliveriesStore, deliveryRecords);
                }
            }
        });
    },

    _handleLatestDeadline: function(deadlineRecord, deliveryRecords) {
        var is_open = this.assignmentgroup_recordcontainer.record.get('is_open');
        if(this.role !== 'student' && deliveryRecords.length === 0 && deadlineRecord.get('deadline') < Ext.Date.now() && is_open) {
            this.fireEvent('expiredNoDeliveries');
        }
    },

    findLatestFeebackInDeadline: function(deadlineRecords, deadlineRecord, deliveriesStore, deliveryRecords) {
        var allStaticFeedbacks = [];
        var loadedStaticFeedbackStores = 0;
        Ext.each(deliveryRecords, function(deliveryRecord, index) {
            var staticfeedbackStore = deliveryRecord.staticfeedbacks();
            staticfeedbackStore.load({
                scope: this,
                callback: function(staticFeedbackRecords) {
                    loadedStaticFeedbackStores ++;
                    if(staticFeedbackRecords.length > 0) {
                        allStaticFeedbacks.push(staticFeedbackRecords[0]);
                    }
                    if(loadedStaticFeedbackStores === deliveryRecords.length) {
                        this._sortStaticfeedbacks(allStaticFeedbacks);
                        var activeFeedback = allStaticFeedbacks[0];
                        this.addDeliveriesPanel(deadlineRecords, deadlineRecord, deliveriesStore, activeFeedback);
                    }
                }
            });
        }, this);
    },

    /**
     * @private
     */
    _sortStaticfeedbacks: function(allStaticFeedbacks) {
        allStaticFeedbacks.sort(function(a, b) {
            if(a.data.save_timestamp > b.data.save_timestamp) {
                return -1;
            } else if(a.data.save_timestamp === b.data.save_timestamp) {
                return 0;
            } else {
                return 1;
            }
        });
    },

    /**
     * @private
     */
    addDeliveriesPanel: function(deadlineRecords, deadlineRecord, deliveriesStore, activeFeedback) {
        this._tmp_deliveriespanels.push({
            xtype: 'deliveriespanel',
            delivery_recordcontainer: this.delivery_recordcontainer,
            deadlineRecord: deadlineRecord,
            deliveriesStore: deliveriesStore,
            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
            activeFeedback: activeFeedback
        });
        this._tmp_active_feedbacks.push(activeFeedback);

        this._cacheAllDeliveriesInStore(deliveriesStore);
        if(this._tmp_deliveriespanels.length === deadlineRecords.length) {
            this._sortDeliveryPanels();
            this._findAndMarkActiveFeedback();
            this.add(this._tmp_deliveriespanels);
            this.getEl().unmask();
            this.isLoading = false;
            this.fireEvent('loadComplete', this);
            this._onLoadComplete();
        }
    },

    _onLoadComplete:function () {
        var group = this.assignmentgroup_recordcontainer.record;
        if(group.get('parentnode__delivery_types') !== 1) {
            this.add({
                xtype: 'button',
                scale: 'medium',
                text: '<i class="icon-time"></i> ' + gettext('New deadline'),
                cls: 'bootstrap',
                listeners: {
                    scope: this,
                    click:function () {
                        this.fireEvent('createNewDeadline');
                    }
                }
            });
        }
    },

    _cacheAllDeliveriesInStore: function(store) {
        Ext.each(store.data.items, function(deliveryRecord, index) {
            this._allDeliveries.push(deliveryRecord);
        }, this);
    },

    _findAndMarkActiveFeedback: function() {
        this._sortStaticfeedbacks(this._tmp_active_feedbacks);
        this.latestStaticFeedbackRecord = this._tmp_active_feedbacks[0];
        if(!this.latestStaticFeedbackRecord) {
            return;
        }
        Ext.each(this._tmp_deliveriespanels, function(deliveriespanel, index) {
            Ext.each(deliveriespanel.deliveriesStore.data.items, function(deliveryRecord, index) {
                if(deliveryRecord.data.id === this.latestStaticFeedbackRecord.get('delivery')) {
                    deliveryRecord.hasLatestFeedback = true;
                }
            }, this);
        }, this);
    },

    /**
     * @private
     * Sort delivery panels, since they are added on response from an
     * asynchronous operation. Sorted descending by deadline datetime.
     */
    _sortDeliveryPanels: function() {
        this._tmp_deliveriespanels.sort(function(a, b) {
            if(a.deadlineRecord.data.deadline > b.deadlineRecord.data.deadline) {
                return -1;
            } else if(a.deadlineRecord.data.deadline === b.deadlineRecord.data.deadline) {
                return 0;
            } else {
                return 1;
            }
        });
    },

    getLatestDelivery: function() {
        return this._allDeliveries[0];
    },

    selectDelivery: function(deliveryid) {
        Ext.each(this.items.items, function(deliveriespanel) {
            var index = deliveriespanel.deliveriesStore.find('id', deliveryid);
            if(index !== -1) {
                var deliveriesgrid = deliveriespanel.down('deliveriesgrid');
//                if(deliveriespanel.collapsed) {
//                    deliveriespanel.toggleCollapse();
//                }
                deliveriesgrid.getSelectionModel().select(index);
                return false; // break
            }
        }, this);
    }
});


Ext.define('devilry_header.HelpLinksBox', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_helplinksbox',
    cls: 'devilryheader_helplinksbox',

    requires: [
        'devilry_header.HelpLinksStore'
    ],

    tpl: [
        '<h2>',
            gettext('Help'),
        '</h2>',
        '<tpl if="loading">',
            '<p>', gettext('Loading'), ' ...</p>',
        '<tpl elseif="error">',
            '<p class="error">',
                gettext('Failed to load help links. Try reloading the page.'),
            '</p>',
        '<tpl else>',
            '<tpl if="helpLinkRecords.length == 0">',
                gettext('Your local Devilry system administrator(s) have not added any external help for you. If you feel anything in Devilry is unclear, contact your local Devilry system administrator(s) and ask them to add help links.'),
            '</tpl>',
            '<ul class="helplinks">',
                '<tpl for="helpLinkRecords">',
                    '<li>',
                        '<div class="title"><a href="{data.help_url}">{data.title}</a></div>',
                        '<div class="description">{data.description}</div>',
                    '</li>',
                '</tpl>',
            '</ul>',
            '<tpl if="is_superuser">',
                '<p><a class="edit_helplinks" href="{edit_helplinks_url}">',
                    gettext('Edit help links'),
                '</a></p>',
            '</tpl>',
        '</tpl>'
    ],

    data: {
        loading: true
    },


    /**
     * Set UserInfo record and update view.
     */
    setUserInfoRecord: function(userInfoRecord) {
        this.userInfoRecord = userInfoRecord;
        this.store = Ext.create('devilry_header.HelpLinksStore');
        this.store.load({
            scope: this,
            callback: this._onLoadStore
        });
    },

    _onLoadStore: function(records, operation) {
        if(operation.success) {
            this._onLoadStoreSuccess();
        } else {
            this._onLoadStoreFailure();
        }
    },

    _onLoadStoreSuccess: function() {
        var helpLinkRecords = this.store.getHelpLinksForUser(this.userInfoRecord);
        this.update({
            helpLinkRecords: helpLinkRecords,
            is_superuser: this.userInfoRecord.get('is_superuser'),
            edit_helplinks_url: DevilrySettings.DEVILRY_SUPERUSERPANEL_URL + 'devilry_helplinks/helplink/'
        });
    },

    _onLoadStoreFailure: function() {
        this.update({
            error: true
        });
    }
});


Ext.define('devilry.extjshelpers.forms.administrator.Period', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_periodform',
    cls: 'widget-periodform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector',
        'devilry.extjshelpers.formfields.DateTimeField'
    ],

    suggested_windowsize: {
        width: 700,
        height: 500
    },

    flex: 8,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },
    defaults: {
        margin: '0 0 10 0'
    },


    items: [{
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': spring01'
    }, {
        name: "long_name",
        fieldLabel: gettext("Long name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': Spring 2001'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Subject"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedSubject',
        emptyText: interpolate(gettext('Select a %(subject_term)s'), {
            subject_term: gettext('subject')
        }, true),
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>'
    }, {
        xtype: 'fieldcontainer',
        fieldLabel: 'Time span',
        //labelStyle: 'font-weight:bold;padding:0',
        layout: 'hbox',

        fieldDefaults: {
            labelAlign: 'top'
        },

        items: [{
            name: "start_time",
            fieldLabel: gettext("Start"),
            xtype: 'devilrydatetimefield',
            flex: 1
        }, {
            xtype: 'box',
            width: 20
        }, {
            name: "end_time",
            fieldLabel: gettext("End"),
            xtype: 'devilrydatetimefield',
            flex: 1
        }]
    }],

    help: [
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.')
    ]
});


/** The deadline management methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines', {
    requires: [
        'devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow'
    ],

    /**
     * @private
     */
    onAddDeadline: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var me = this;
        var createDeadlineWindow = Ext.widget('multicreatenewdeadlinewindow', {
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                this.close();
                me.addDeadlineToSelected(record);
            }
        });
        createDeadlineWindow.show();
    },

    /**
     * @private
     */
    addDeadlineToSelected: function(record) {
        this.progressWindow.start('Add deadline');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.addDeadline,
            extraArgs: [record]
        });
    },

    /**
     * @private
     */
    addDeadline: function(assignmentGroupRecord, index, totalSelectedGroups, deadlineRecord) {
        var msg = Ext.String.format('Adding deadline to group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        this.statics().createDeadline(assignmentGroupRecord, deadlineRecord, this.deadlinemodel, {
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(assignmentGroupRecord, 'Deadline successfully created.');
                } else {
                    this._onAddDeadlineFailure(assignmentGroupRecord, operation);
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish();
                }
            }
        });

        if(index == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },

    _onAddDeadlineFailure: function(assignmentGroupRecord, operation) {
        this.progressWindow.addErrorFromOperation(
            assignmentGroupRecord, 'Failed to create deadline', operation
        );
    },

    statics: {
        createDeadline: function(assignmentGroupRecord, deadlineRecord, deadlinemodel, saveopt) {
            var newDeadlineRecord = Ext.ModelManager.create(deadlineRecord.data, deadlinemodel);
            newDeadlineRecord.data.assignment_group = assignmentGroupRecord.data.id;
            newDeadlineRecord.save(saveopt);
        }
    }
});


/** The group management methods for StudentsManager. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageGroups', {
    requires: [
        'devilry.administrator.studentsmanager.ManuallyCreateUsers',
        'devilry.extjshelpers.RestProxy',
        'devilry.extjshelpers.AutoSizedWindow'
    ],

    /**
     * @private
     */
    showCreateGroupsInBulkWindow: function(initialLines, currentGroupRecords) {
        var win = Ext.widget('devilry_autosizedwindow', {
            title: 'Create assignment groups',
            modal: true,
            width: 1400, // NOTE: This is autosized to fit the body if the body is smaller.
            height: 1000,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'manuallycreateusers',
                deadlinemodel: this.deadlinemodel,
                assignmentrecord: this.assignmentrecord,
                suggestedDeadline: this.guessDeadlineFromCurrentlyLoadedGroups(),
                currentGroupRecords: currentGroupRecords,
                initialLines: initialLines
            },
            listeners: {
                scope: this,
                close: function() {
                    this.refreshStore();
                }
            }
        });
        win.show();
    },

    /**
     * @private
     */
    createManyGroupsInBulk: function(initialLines) {
        this.getEl().mask('Loading current assignment groups...');
        devilry.administrator.studentsmanager.StudentsManager.getAllGroupsInAssignment(this.assignmentid, {
            scope: this,
            callback: function(records, op, success) {
                this.getEl().unmask();
                if(success) {
                    this.showCreateGroupsInBulkWindow(initialLines, records);
                } else {
                    Ext.MessageBox.alert('Failed to load current assignment groups. Please try again.');
                }
            }
        });
    },

    /**
     * @private
     *
     * Pick the latest deadline on the last group in the current view. The idea
     * is to get the last created group, however we do not load the last page,
     * so this is a balance of efficiency and convenience.
     */
    guessDeadlineFromCurrentlyLoadedGroups: function() {
        var groupRecords = this.assignmentgroupstore.data.items;
        if(groupRecords.length > 0) {
            var lastLoadedGroup = groupRecords[groupRecords.length-1];
            return lastLoadedGroup.data.latest_deadline_deadline;
        } else {
            return undefined;
        }
    },

    /**
     * @private
     */
    onManuallyCreateUsers: function() {
        this.createManyGroupsInBulk();
    },

    /**
     * @private
     */
    onOneGroupForEachRelatedStudent: function() {
        this.loadAllRelatedStudents({
            scope: this,
            callback: this.createOneGroupForEachRelatedStudent
            //args: ['Hello world']
        });
    },

    /**
     * @private
     */
    createOneGroupForEachRelatedStudent: function(relatedStudents) {
        var format = '{user__username}';
        if(this.assignmentrecord.data.anonymous) {
            format += '<tpl if="candidate_id">:{candidate_id}</tpl>'
        }
        format += '<tpl if="tags"> ({tags})</tpl>';
        var userspecs = this.relatedUserRecordsToStringArray(relatedStudents, format);
        this.createManyGroupsInBulk(userspecs);
    },


    onChangeGroupName: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var record = this.getSelection()[0];
        Ext.Msg.prompt('Change group name', 'Please enter a new group name:', function(btn, name){
            if (btn == 'ok'){
                record.data.name = name;
                record.save();
            }
        });
    },

    onChangeGroupMembers: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var record = this.getSelection()[0];
        var candidates = this.statics().getCandidateInfoFromGroupRecord(record);

        var candidatestrings = [];
        var statics = this.statics();
        Ext.each(candidates, function(candidate, index) {
            candidatestrings.push(statics.formatCandidateInfoAsString(candidate));
        });

        var win = Ext.widget('window', {
            title: 'Select members',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                usernames: candidatestrings,
                anonymous: record.data.parentnode__anonymous,
                helptpl: Ext.create('Ext.XTemplate',
                    '<div class="section helpsection">',
                    '   <tpl if="anonymous">',
                    '       <p>One candidate of on each line. Username and <em>candidate ID</em> is separated by a single colon. Note that <em>candidate ID</em> does not have to be a number.</p>',
                    '       <p>Example:</p>',
                    '       <pre style="padding: 5px;">bob:20\nalice:A753\neve:SEC-01\ndave:30</pre>',
                    '   </tpl>',
                    '   <tpl if="!anonymous">',
                    '       <p>One username on each line. Example</p>',
                    '       <pre style="padding: 5px;">bob\nalice\neve\ndave</pre>',
                    '   </tpl>',
                    '</div>'
                ),
                listeners: {
                    scope: this,
                    saveClicked: Ext.bind(this.changeGroupMembers, this, [record], true)
                }
            },
        });
        win.show();
    },

    changeGroupMembers: function(setlistofusersobj, candidateSpecs, caller, record) {
        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.fake_candidates = [];
        Ext.Array.each(candidateSpecs, function(candidateSpec) {
            editRecord.data.fake_candidates.push(devilry.administrator.studentsmanager.StudentsManagerManageGroups.parseCandidateSpec(candidateSpec));
        }, this);

        setlistofusersobj.getEl().mask("Changing group members");
        editRecord.save({
            scope: this,
            failure: function(records, operation) {
                setlistofusersobj.getEl().unmask();
                devilry.extjshelpers.RestProxy.showErrorMessagePopup(operation, 'Failed to change group members');
            },
            success: function() {
                setlistofusersobj.up('window').close();
                this.loadFirstPage();
            }
        });
    },

    onDeleteGroups: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        Ext.MessageBox.show({
            title: 'Are you sure that you want to delete the selected groups',
            msg: '<p>Are you sure you want to delete the selected groups?</p><p>If you are a <strong>superadmin</strong>, this will delete the group and all their related data on this assignment, including deliveries and feedback.</p><p>If you are a normal administrator, you will only be permitted to delete groups without any deliveries.</p>',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
                        scope: this,
                        callback: this.deleteGroups
                    });
                }
            }
        });

    },

    /**
     * @private
     */
    deleteGroups: function(groupRecords) {
        this.progressWindow.start('Delete groups');
        this._finishedSavingGroupCount = 0;
        Ext.each(groupRecords, function(groupRecord, index) {
            this.deleteGroup(groupRecord, index, groupRecords.length);
        }, this);
    },

    /**
     * @private
     */
    deleteGroup: function(record, index, totalSelectedGroups) {
        var msg = Ext.String.format('Deleting group {0}/{1}',
            index, totalSelectedGroups
        );
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.destroy({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(record, 'Group successfully deleted.');
                } else {
                    this.progressWindow.addErrorFromOperation(record, 'Failed to delete group.', operation);
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish();
                }
            }
        });
    },

    
    onImportGroupsFromAnotherAssignmentInCurrentPeriod: function() {
        Ext.widget('window', {
            text: interpolate(gettext('Import %(groups_term)s from another %(assignment_term)s in the current %(period_term)s'), {
                groups_term: gettext('groups'),
                examiners_term: gettext('examiners'),
                assignment_term: gettext('assignment'),
                period_term: gettext('period')
            }, true),
            layout: 'fit',
            width: 830,
            height: 600,
            modal: true,
            items: {
                xtype: 'importgroupsfromanotherassignment',
                periodid: this.periodid,
                help: '<div class="section helpsection">Select the assignment you wish to import assignment groups from, and click <em>Next</em> to further edit the selected groups.</div>',
                listeners: {
                    scope: this,
                    next: this._importGroupsFromAnotherAssignmentInCurrentPeriod
                }
            }
        }).show();
    },

    _convertGroupRecordToGroupSpec: function(groupRecord) {
        var statics = this.statics();
        var candidates = statics.getCandidateInfoFromGroupRecord(groupRecord);
        var groupString = '';
        Ext.each(candidates, function(candidate, index) {
            var candidateString = statics.formatCandidateInfoAsString(candidate);
            if(index != candidates.length-1)
                candidateString += ', ';
            groupString += candidateString;
        }, this);
        var tags = groupRecord.get('tags__tag');
        if(tags && tags.length > 0) {
            var tagsString = tags.join(',');
            groupString += Ext.String.format(' ({0})', tagsString);
        }
        var name = groupRecord.get('name');
        if(name) {
            groupString = name + ":: " + groupString;
        }
        return groupString;
    },

    _importGroupsFromAnotherAssignmentInCurrentPeriod: function(importPanel, assignmentGroupRecords) {
        importPanel.up('window').close();
        var groups = [];
        Ext.each(assignmentGroupRecords, function(groupRecord, index) {
            groups.push(this._convertGroupRecordToGroupSpec(groupRecord));
        }, this);
        this.createManyGroupsInBulk(groups);
    },


    onSetCandidateIdBulk: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var win = Ext.widget('window', {
            title: 'Import candidate IDs',
            modal: true,
            width: 800,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                usernames: [],
                fieldLabel: 'Candidates',
                anonymous: this.assignmentrecord.anonymous,
                helptpl: Ext.create('Ext.XTemplate',
                    '<div class="section helpsection">',
                    '    <p><strong>Warning:</strong> This action will replace/clear candidate IDs on every selected group.</p>',
                    '    <p>The <em>intended use case</em> for this window is to paste candidate IDs into Devilry instead of setting candidate IDs manually.</p>',
                    '    <p>The format is one candidate on each line. Username and <em>candidate ID</em> is separated by whitespace and/or a single colon, comma or semicolon. Note that <em>candidate ID</em> does not have to be a number.</p>',
                    '    <p><strong>Example</strong> (using colon to separate username and candidate ID):</p>',
                    '    <pre style="padding: 5px;">bob:20\nalice:A753\neve:SEC-01\ndave:30</pre>',
                    '    <p><strong>Example</strong> (showing all of the supported separators):</p>',
                    '    <pre style="padding: 5px;">bob    20\nalice : A753\neve, SEC-01\ndave;  30</pre>',
                    '</div>'
                ),
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, candidateSpecs, caller) {
                        try {
                            var usernameToCandidateIdMap = this.parseCandidateImportFormat(candidateSpecs);
                        } catch(e) {
                            Ext.MessageBox.alert('Error', e);
                            return;
                        }
                        setlistofusersobj.up('window').close();
                        this.progressWindow.start('Set candidate ID on many');
                        this._finishedSavingGroupCount = 0;
                        this.down('studentsmanager_studentsgrid').performActionOnSelected({
                            scope: this,
                            callback: this.setCandidateId,
                            extraArgs: [usernameToCandidateIdMap]
                        });
                        
                    },
                }
            }
        });
        win.show();

    },

    /**
     * @private
     */
    parseCandidateImportFormat: function(candidateSpecs) {
        var usernameToCandidateIdMap = {};
        Ext.each(candidateSpecs, function(candidateSpec, index) {
            var s = candidateSpec.split(/\s*[:,;\s]\s*/);
            if(candidateSpec.length > 0) {
                if(s.length != 2) {
                    throw Ext.String.format('Invalid format on line {0}: {1}', index, candidateSpec)
                }
                usernameToCandidateIdMap[s[0]] = s[1];
            }
        }, this);
        return usernameToCandidateIdMap;
    },

    /**
     * @private
     */
    setCandidateId: function(record, index, totalSelectedGroups, usernameToCandidateIdMap) {
        var msg = Ext.String.format('Setting candidate ID on group {0}/{1}',
            index, totalSelectedGroups
        );
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.fake_candidates = [];

        var result_preview = '';
        var usernames = record.data.candidates__student__username;
        Ext.Array.each(usernames, function(username, index) {
            var candidate_id = usernameToCandidateIdMap[username];
            editRecord.data.fake_candidates.push({
                username: username,
                candidate_id: candidate_id
            });
            result_preview += username;
            if(candidate_id) {
                result_preview += username + ':';
            } else {
                this.progressWindow.addWarning(record, Ext.String.format('No Candidate ID for {0}.', username));
            }
            if(index < usernames.length) {
                result_preview += ', ';
            }
        }, this);

        editRecord.save({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(record, Ext.String.format('Candidate IDs successfully updated to: {0}.', result_preview));
                } else {
                    this.progressWindow.addErrorFromOperation(record, 'Failed to save changes to group.', operation);
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish();
                }
            }
        });
    },


    statics: {
        getCandidateInfoFromGroupRecord: function(record) {
            var candidates = [];
            Ext.each(record.data.candidates__student__username, function(username, index) {
                candidate = {username: username};
                if(record.data.parentnode__anonymous) {
                    candidate.candidate_id = record.data.candidates__identifier[index];
                }
                candidates.push(candidate);
            });
            return candidates;
        },

        formatCandidateInfoAsString: function(candidate) {
            if(candidate.candidate_id == undefined || candidate.candidate_id == "candidate-id missing") {
                return candidate.username;
            } else {
                return Ext.String.format('{0}:{1}', candidate.username, candidate.candidate_id);
            }
        },

        parseCandidateSpec: function(candidateSpec) {
            var asArray = candidateSpec.split(/\s*:\s*/);
            var candidate_id = asArray.length > 1? asArray[1]: null;
            return {
                username: asArray[0],
                candidate_id: candidate_id
            };
        },
    }
});


/** SearchWidget used in every page in the entire examiner interface.
 * */
Ext.define('devilry.examiner.ExaminerSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.DashboardSearchWidget',

    /**
     * @cfg
     * Url prefix. Should be the absolute URL path to /student/.
     */
    urlPrefix: '',

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: gettext('Deliveries'),
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedDelivery'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: this.deliveryRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Groups'),
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedAssignmentGroup'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    },
                    menuitems: [{
                        text: interpolate('Show %(deliveries_term)s', {
                            deliveries_term: gettext('deliveries')
                        }, true),
                        clickFilter: 'type:delivery group:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Assignments'),
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedAssignment'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: this.assignmentRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignment/{id}'
                    },
                    menuitems: [{
                        text: interpolate(gettext('Show %(groups_term)s'), {
                            groups_term: gettext('groups')
                        }, true),
                        clickFilter: 'type:group assignment:{id}'
                    }, {
                        text: interpolate('Show %(deliveries_term)s', {
                            deliveries_term: gettext('deliveries')
                        }, true),
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deadlinesonsinglegrouplisting',
    cls: 'widget-deadlinesonsinglegrouplisting selectable-grid',
    sortableColumns: false,
    requires: [
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    rowTpl: Ext.create('Ext.XTemplate',
        '{deadline:date}'
    ),

    deadlinemodel: undefined,
    assignmentgroup_recordcontainer: undefined,
    enableDeadlineCreation: false,


    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store = this.createDeadlineStore();
        Ext.apply(this, {
            columns: [{
                header: 'Deadline',
                dataIndex: 'deadline',
                menuDisabled: true,
                width: 150,
                renderer: function(value, metaData, deadlinerecord) {
                    return this.rowTpl.apply(deadlinerecord.data);
                }
            }, {
                header: 'Text',
                dataIndex: 'text',
                menuDisabled: true,
                flex: 2
            }, {
                header: 'Deliveries',
                menuDisabled: true,
                dataIndex: 'number_of_deliveries',
                width: 85
            }]
        });

        this.dockedItems = [{
            xtype: 'pagingtoolbar',
            store: this.store,
            dock: 'bottom',
            displayInfo: false
        }];
        if(this.enableDeadlineCreation) {
            this.addCreateNewDeadlineButton();
        }

        this.callParent(arguments);
        if(this.assignmentgroup_recordcontainer.record) {
            this.reload();
        }
        this.assignmentgroup_recordcontainer.addListener('setRecord', this.reload, this);
    },

    /**
     * @private
     * Reload all empty deadlines on this assignmentgroup.
     * */
    reload: function() {
        this.loadDeadlines(this.assignmentgroup_recordcontainer.record.data.id);
    },

    /**
     * @private
     */
    loadDeadlines: function(assignmentgroupid) {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'assignment_group',
            comp: 'exact',
            value: assignmentgroupid
        }]);
        this.store.load({
            scope: this,
            callback: this.onDeadlineStoreLoad
        });
    },

    /**
     * @private
     */
    onDeadlineStoreLoad: function(records, op, success) {
    },

    /**
     * @private
     * */
    createDeadlineStore: function() {
        var deadlinestore = Ext.create('Ext.data.Store', {
            model: this.deadlinemodel,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        deadlinestore.proxy.extraParams.orderby = Ext.JSON.encode(['-deadline']);
        return deadlinestore;
    },


    /**
     * @private
     * */
    addCreateNewDeadlineButton: function() {
        Ext.Array.insert(this.dockedItems, 0, [{
            xtype: 'toolbar',
            ui: 'footer',
            dock: 'bottom',
            items: ['->', {
                xtype: 'button',
                text: 'Create deadline',
                iconCls: 'icon-add-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onCreateNewDeadline
                }
            }]
        }]);
    },

    /**
     * @private
     */
    onCreateNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                this.close();
                me.reload();
            }
        });
        createDeadlineWindow.show();
    }
});


/** Draft editor window. */
Ext.define('devilry.gradeeditors.DraftEditorWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradedrafteditormainwin',
    title: 'Create feedback',
    layout: 'fit',
    modal: true,
    maximizable: false,
    requires: [
        'devilry.extjshelpers.NotificationManager',
        'devilry.gradeeditors.FailureHandler',
        'devilry.markup.MarkdownFullEditor',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackView',
        'devilry.extjshelpers.HelpWindow'
    ],

    config: {
        /**
         * @cfg
         * ID of the Delivery where the feedback belongs. (Required).
         */
        deliveryid: undefined,

        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor config. (Required).
         */
        gradeeditor_config: undefined,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor registry item. (Required).
         */
        registryitem: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.addEvents('publishNewFeedback');
    },

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'panel',
                frame: false,
                border: false,
                layout: 'fit',
                loader: {
                    url: this.registryitem.draft_editor_url,
                    renderer: 'component',
                    autoLoad: true,
                    loadMask: true,
                    scope: this, // for success and failure
                    success: this.onLoadDraftEditorSuccess,
                    failure: this.onLoadDraftEditorFailure
                }
            },
            onEsc: Ext.emptyFn
        });
        this._setupAutosizing();
        this.initComponentExtra();
        this.callParent(arguments);
    },

    _setupAutosizing: function() {
        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShow, this);
    },


    initComponentExtra: function() {
        this.previewButton = Ext.widget('button', {
            text: 'Show preview',
            scale: 'medium',
            //iconCls: 'icon-save-32',
            listeners: {
                scope: this,
                click: this.onPreview
            }
        });

        this.draftButton = Ext.widget('button', {
            text: 'Save draft',
            scale: 'medium',
            listeners: {
                scope: this,
                click: this.onSaveDraft
            }
        });

        this.publishButton = Ext.widget('button', {
            text: 'Publish',
            scale: 'large',
            ui: 'primary',
            listeners: {
                scope: this,
                click: this.onPublish
            }
        });

        this.buttonBar = Ext.widget('toolbar', {
            dock: 'bottom',
            ui: 'footer',
            items: ['->', this.previewButton, this.draftButton, {xtype:'box', width: 20}, this.publishButton]
        });

        Ext.apply(this, {
            dockedItems: [this.buttonBar]
        });
    },

    /**
     * @private
     */
    onHelp: function() {
        this.helpwindow.show();
    },

    /**
     * @private
     */
    getSimplifiedFeedbackDraftModelName: function() {
        return Ext.String.format(
            'devilry.apps.gradeeditors.simplified.{0}.SimplifiedFeedbackDraft',
            this.isAdministrator? 'administrator': 'examiner'
        );
    },

    /**
     * @private
     */
    onLoadDraftEditorSuccess: function() {
        this.helpwindow = Ext.widget('helpwindow', {
            title: 'Help',
            closeAction: 'hide',
            //width: this.getDraftEditor().helpwidth || 600,
            //height: this.getDraftEditor().helpheight || 500,
            helptext: this.getDraftEditor().help
        });

        if(this.getDraftEditor().help) {
            this.buttonBar.insert(0, {
                text: 'Help',
                scale: 'medium',
                listeners: {
                    scope: this,
                    click: this.onHelp
                }
            });
        }

        this.getDraftEditor().getEl().mask('Loading current draft');

        var model = Ext.ModelManager.getModel(this.getSimplifiedFeedbackDraftModelName());
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true,
            proxy: model.proxy.copy()
        });

        store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery',
            comp: 'exact',
            value: this.deliveryid
        }]);
        store.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        store.pageSize = 1;
        store.load({
            scope: this,
            callback: this.onLoadCurrentDraft
        });
    },

    /**
     * @private
     */
    onLoadDraftEditorFailure: function(elementloader, response) {
        console.error(Ext.String.format(
            'Loading grade editor failed with {0}: {1}',
            response.status, response.statusText
        ));
        if(response.status === 404) {
            console.error('Status code 404 indicates that the draft_editor_url is invalid.');
        } else if(response.status === 200) {
            console.error('Status code 200 indicates that the draft_editor_url contains javascript with syntax errors.');
        }
        console.error('Complete response object:');
        console.error(response);
    },

    /**
     * @private
     */
    onLoadCurrentDraft: function(records, operation, successful) {
        if(successful) {
            var draftstring;
            if(records.length !== 0) {
                draftstring = records[0].data.draft;
            }
            this.initializeDraftEditor(draftstring);
        } else {
            throw "Failed to load current draft.";
        }
    },

    /**
     * @private
     * @param draftstring May be undefined.
     */
    initializeDraftEditor: function(draftstring) {
        this.getDraftEditor().initializeEditor(this.getGradeEditorConfig());
        this.getDraftEditor().setDraftstring(draftstring);
    },

    /**
     * @private
     * Get the draft editor.
     */
    getDraftEditor: function() {
        return this.getComponent(0).getComponent(0);
    },

    /**
     * @private
     * Call the onPublish() method in the draft editor.
     */
    onPublish: function() {
        this.publishButton.getEl().mask('');
        this.getDraftEditor().onPublish();
    },

    /**
     * @private
     * Call the onSaveDraft() method in the draft editor.
     */
    onSaveDraft: function() {
        this.draftButton.getEl().mask('');
        this.getDraftEditor().onSaveDraft();
    },

    /**
     * @private
     * Save draft and show preview. Does the same as onSaveDraft(), however a
     * preview is shown after the draft has been saved.
     */
    onPreview: function() {
        this.previewButton.getEl().mask('');
        this._tmp_showpreview = true;
        this.getDraftEditor().onSaveDraft();
    },

    /**
     * @private
     * Exit the grade editor.
     */
    exit: function() {
        this.close();
    },

    /**
     * @private
     */
    save: function(published, draftstring, saveconfig) {
        var draftrecord = Ext.create(this.getSimplifiedFeedbackDraftModelName(), {
            draft: draftstring,
            published: published,
            delivery: this.deliveryid
        });
        draftrecord.save(saveconfig);
    },

    /**
     * Save the current draftstring.
     *
     * @param draftstring The draftstring to save.
     * @param onFailure Called when the save fails. The scope is the draft
     *    editor that ``saveDraft`` was called from.
     */
    saveDraft: function(draftstring, onFailure) {
        var showpreview = this._tmp_showpreview;
        this._tmp_showpreview = false; // Reset the show preview (if we dont, any subsequent draft save after a preview will show a preview).

        onFailure = onFailure || devilry.gradeeditors.FailureHandler.onFailure;
        var me = this;
        this.save(false, draftstring, {
            scope: this.getDraftEditor(),
            callback: function() {
                me.draftButton.getEl().unmask();
                me.previewButton.getEl().unmask();
            },
            failure: onFailure,
            success: function(response, operation) {
                devilry.extjshelpers.NotificationManager.show({
                    title: 'Draft saved',
                    message: 'The feedback draft has been saved.'
                });
                if(showpreview) {
                    me.showPreview(response, operation);
                }
            }
        });
    },

    showPreview: function(record, operation) {
        var responseData = Ext.JSON.decode(operation.response.responseText);
        var fake_staticfeedback = responseData.items.extra_responsedata;
        var fake_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        fake_recordcontainer.setRecord({data: fake_staticfeedback});
        Ext.widget('window', {
            width: this.width,
            height: this.height,
            modal: true,
            layout: 'fit',
            closable: false, // To easy to double click and close an undelying window
            items: [{
                xtype: 'panel',
                autoScroll: true,
                items: [{
                    xtype: 'staticfeedbackview',
                    padding: 20,
                    singlerecordontainer: fake_recordcontainer
                }]
            }],
            dockedItems: [{
                xtype: 'toolbar',
                ui: 'footer',
                dock: 'bottom',
                items: ['->', {
                    xtype: 'button',
                    text: 'Close preview',
                    scale: 'medium',
                    listeners: {
                        click: function() {
                            this.up('window').close();
                        }
                    }
                }, '->']
            }]
        }).show();

        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    },

    /**
     * Save and publish draftstring.
     *
     * @param draftstring The draftstring to save.
     * @param onFailure Called when the save fails. The scope is the draft
     *    editor that ``saveDraft`` was called from.
     */
    saveDraftAndPublish: function(draftstring, onFailure) {
        onFailure = onFailure || devilry.gradeeditors.FailureHandler.onFailure;
        var me = this;
        this.save(true, draftstring, {
            scope: this.getDraftEditor(),
            callback: function(unused, operation) {
                if(operation.wasSuccessful()) {
                    me.fireEvent('publishNewFeedback');
                    me.exit();
                    devilry.extjshelpers.NotificationManager.show({
                        title: 'Published',
                        message: 'The feedback has been saved and published.'
                    });
                } else {
                    me.publishButton.getEl().unmask();
                }
            },
            failure: onFailure
        });
    },

    /**
     * Get the grade editor configuration that is stored on the current
     * assignment.
     */
    getGradeEditorConfig: function() {
        return this.gradeeditor_config;
    },


    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this._setSizeAndPosition();
        }
    },

    _onShow: function() {
        this._setSizeAndPosition();
    },

    _setSizeAndPosition: function() {
        if(this.isFloating()) {
            var bodysize = Ext.getBody().getViewSize();
            this.setSize({
                width: bodysize.width - 40,
                height: bodysize.height - 40
            });
            this.setPagePosition(20, 20);
        }
    }
});


Ext.define('devilry.extjshelpers.forms.administrator.Node', {
    extend: 'Ext.form.Panel',
    alias: 'widget.administrator_nodeform',
    cls: 'widget-nodeform',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeySelector'
    ],

    suggested_windowsize: {
        width: 600,
        height: 400
    },

    flex: 8,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: "short_name",
        fieldLabel: gettext("Short name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': mathfaculty'
    }, {
        name: "long_name",
        fieldLabel: gettext("Long name"),
        xtype: 'textfield',
        emptyText: gettext('Example') + ': Faculty of Mathematics'
    }, {
        name: "parentnode",
        fieldLabel: gettext("Parent"),
        xtype: 'foreignkeyselector',
        model: 'devilry.apps.administrator.simplified.SimplifiedNode',
        emptyText: gettext('Select a parent, or leave blank for no parent'),
        displayTpl: '{long_name} ({short_name})',
        dropdownTpl: '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>',
        allowEmpty: true
    }],

    help: [
        '<strong>' + gettext('Short name') + ':</strong> ' + gettext('A short name used when the long name takes to much space. Short name can only contain english lower-case letters, numbers and underscore (_).'),
        '<strong>' + gettext('Long name') + ':</strong> ' + gettext('A longer descriptive name which can contain any character.'),
        '<strong>' + gettext('Parent') + ':</strong> ' + interpolate(gettext('Organize this %(node_term)s below another %(node_term)s. May be empty.'), {
            node_term: gettext('node')
        }, true)
    ]
});


Ext.define('devilry.administrator.ListOfChildnodes', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.administrator-listofchildnodes',
    cls: 'selectable-grid',
    hideHeaders: true,

    requires: [
        'devilry.extjshelpers.forms.administrator.Node',
        'devilry.extjshelpers.forms.administrator.Subject',
        'devilry.extjshelpers.forms.administrator.Period',
        'devilry.extjshelpers.forms.administrator.Assignment',
        'devilry.administrator.DefaultCreateWindow',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel'
    ],

    mixins: [
        'devilry.extjshelpers.AddPagerIfNeeded'
    ],

    /**
     * @cfg
     * Id of the parentnode.
     */
    parentnodeid: undefined,

    /**
     * @cfg
     * Orderby field.
     */
    orderby: undefined,

    /**
     * @cfg
     * Name of the model for the childnode type.
     */
    modelname: undefined,

    /**
     * @cfg
     * The part of the url that identifies this childnode type, such as "node" or "assignment".
     */
    urlrolepart: undefined,

    /**
     * @cfg
     * Readable type description.
     */
    readable_type: undefined,
    
    initComponent: function() {
        var model = Ext.ModelManager.getModel(this.modelname);
        this.store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
        //this.store.pageSize = 2; // Uncomment to test paging
        this._loadStore();
        Ext.apply(this, {
            columns: [{
                header: 'Long name',  dataIndex: 'long_name', flex: 1
            }],
            listeners: {
                scope: this,
                select: this._onSelect
            },
            bbar: [{
                xtype: 'button',
                iconCls: 'icon-add-16',
                text: Ext.String.format('Add {0}', this.readable_type),
                listeners: {
                    scope: this,
                    click: this._onAdd
                }
            }]
        });
        this.callParent(arguments);
        this.addPagerIfNeeded();
    },

    _loadStore: function() {
        this.store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.parentnodeid
        }]);
        this.store.proxy.setDevilryOrderby([this.orderby]);
        this.store.load();
    },

    _onSelect: function(grid, record) {
        var url = Ext.String.format('{0}/administrator/{1}/{2}', DevilrySettings.DEVILRY_URLPATH_PREFIX, this.urlrolepart, record.get('id'));
        window.location.href = url;
    },

    _onAdd: function() {
        var successUrlPrefix = Ext.String.format('{0}/administrator/{1}/', DevilrySettings.DEVILRY_URLPATH_PREFIX, this.urlrolepart);
        Ext.create('devilry.administrator.DefaultCreateWindow', {
            title: Ext.String.format('Create new {0}', this.readable_type),
            editpanel: Ext.ComponentManager.create({
                xtype: 'restfulsimplified_editpanel',
                model: this.modelname,
                editform: Ext.widget(Ext.String.format('administrator_{0}form', this.urlrolepart)),
                record: Ext.create(this.modelname, {
                    parentnode: this.parentnodeid
                })
            }),
            successUrlTpl: Ext.create('Ext.XTemplate', successUrlPrefix + '{id}')
        }).show();
    }
});


Ext.define('devilry.administrator.subject.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-subjectlayout',

    requires: [
        'devilry.administrator.subject.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Subject',
        'devilry.administrator.ListOfChildnodes'
    ],
    
    /**
     * @cfg
     */
    subjectid: undefined,

    subjectmodel_name: 'devilry.apps.administrator.simplified.SimplifiedSubject',
    
    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {},
                cls: 'section pathheading',
                tpl: [
                    '<tpl if="!hasdata">',
                        '<span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                        '<h1>{subject.long_name}</h1>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                items: [{
                    xtype: 'administrator-listofchildnodes',
                    title: 'Periods/semesters',
                    parentnodeid: this.subjectid,
                    orderby: 'start_time',
                    modelname: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
                    readable_type: 'period/semester',
                    urlrolepart: 'period'
                }, this.prettyview = Ext.widget('administrator_subjectprettyview', {
                    title: 'Administer',
                    modelname: this.subjectmodel_name,
                    objectid: this.subjectid,
                    dashboardUrl: DASHBOARD_URL,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        loadmodelFailed: this._onLoadRecordFailed,
                        edit: this._onEdit
                    }
                })]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(subjectRecord) {
        this.heading.update({
            hasdata: true,
            subject: subjectRecord.data
        });
        this._setBreadcrumbAndTitle(subjectRecord);
    },

    _onLoadRecordFailed: function(operation) {
        this.removeAll();
        var title = operation.error.statusText;
        if(operation.error.status == '403') {
            title = gettext('Permission denied');
            message = gettext('You are not administrator on this item or any of its parents.');
        }
        this.add({
            xtype: 'box',
            padding: 20,
            tpl: [
                '<div class="section warning">',
                    '<h2>{title}</h2>',
                    '<p>{message}</p>',
                '</div>'
            ],
            data: {
                title: title,
                message: message
            }
        });
    },

    _setBreadcrumbAndTitle: function(subjectRecord) {
        window.document.title = Ext.String.format('{0} - Devilry', subjectRecord.get('short_name'));
        devilry_header.Breadcrumbs.getInBody().set([], subjectRecord.get('short_name'));
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.subjectmodel_name,
            editform: Ext.widget('administrator_subjectform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    }
});


Ext.define('devilry_header.HoverMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_hovermenu',
    cls: 'devilryheader_hovermenu',
    floating: true,
    frame: false,
    border: 0,
    //autoShow: true,
    autoScroll: true,
    topOffset: 30,

    requires: [
        'devilry_header.Roles',
        'devilry_header.HelpLinksBox',
        'devilry_header.UserInfoBox',
        'devilry_i18n.LanguageSelectWidget'
    ],

    initComponent: function() {
        this._setupAutosizing();

        Ext.apply(this, {
            layout: 'border',
            items: [{
                xtype: 'container',
                region: 'center',
                layout: 'column',
                items: [{
                    width: 300,
                    xtype: 'container',
                    padding: '10 20 10 10',
                    items: [{
                        xtype: 'box',
                        html: [
                            '<h2>',
                                gettext('Choose your role'),
                            '</h2>'
                        ].join('')
                    }, {
                        xtype: 'devilryheader_roles'
                    }]
                }, {
                    columnWidth: 1.0,
                    padding: '10 10 10 20',
                    xtype: 'container',
                    items: [{
                        xtype: 'devilryheader_userinfobox'
                    }, {
                        xtype: 'container',
                        margin: '30 0 0 0',
                        items: [{
                            xtype: 'box',
                            html: ['<h2>', gettext('Language'), '</h2>'].join('')
                        }, {
                            xtype: 'devilry_i18n_languageselect',
                            width: 250
                        }]

                    }, {
                        margin: '30 0 0 0',
                        xtype: 'devilryheader_helplinksbox'
                    }]
                }]
            }, {
                xtype: 'box',
                cls: 'devilryheader_footer',
                region: 'south',
                height: 30,
                tpl: [
                    '<p><small>',
                        'Devilry {version} (<a href="http://devilry.org">http://devilry.org</a>)',
                    '</small></p>'
                ],
                data: {
                    version: DevilrySettings.DEVILRY_VERSION
                }
            }]
        });
        this.callParent(arguments);
    },

    _getRoles: function() {
        return this.down('devilryheader_roles');
    },
    _getUserInfoBox: function() {
        return this.down('devilryheader_userinfobox');
    },
    _getHelpLinksBox: function() {
        return this.down('devilryheader_helplinksbox');
    },

    setUserInfoRecord: function(userInfoRecord) {
        this._getRoles().setUserInfoRecord(userInfoRecord);
        this._getUserInfoBox().setUserInfoRecord(userInfoRecord);
        this._getHelpLinksBox().setUserInfoRecord(userInfoRecord);
    },


    //
    //
    // Autoresize to window size
    //
    //

    _setupAutosizing: function() {
       // Get the DOM disruption over with before the component renders and begins a layout
        Ext.getScrollbarSize();
        
        // Clear any dimensions, we will size later on
        this.width = this.height = undefined;

        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShow, this);
    },

    _onWindowResize: function() {
        if(this.isVisible()) {
            this._setSizeAndPosition();
        }
    },

    _setSizeAndPosition: function() {
        var bodysize = Ext.getBody().getViewSize();
        this.setSize({
            width: bodysize.width,
            height: bodysize.height - this.topOffset
        });
        this.setPagePosition(0, this.topOffset);
    },

    _onShow: function() {
        this._setSizeAndPosition();
    }
});


Ext.define('devilry.gradeeditors.EditManyDraftEditorWindow', {
    extend: 'devilry.gradeeditors.DraftEditorWindow',

    config: {
        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor config. (Required).
         */
        gradeeditor_config: undefined,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor registry item. (Required).
         */
        registryitem: undefined,

        buttonText: 'Publish this feedback to all selected groups',
        buttonIcon: 'icon-add-32'
    },

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents('createNewDraft');
    },

    initComponentExtra: function() {
        this.publishButton = Ext.widget('button', {
            text: this.buttonText,
            scale: 'medium',
//            iconCls: this.buttonIcon,
            listeners: {
                scope: this,
                click: this.onPublish
            }
        });
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', this.publishButton]
            }]
        });
    },

    /**
     * @private
     *
     * Skip loading of current draft.
     */
    onLoadDraftEditorSuccess: function() {
        this.initializeDraftEditor();
    },

    /**
     * Not allowed in EditManyDraftEditorWindow.
     */
    saveDraft: function(draftstring, onFailure) {
        throw "Save draft is not allowed in EditManyDraftEditorWindow.";
    },

    /**
     * Fire createNewDraft event with the draft string as argument.
     *
     * @param draftstring The draftstring.
     */
    saveDraftAndPublish: function(draftstring, onFailure) {
        this.fireEvent('createNewDraft', this.getSimplifiedFeedbackDraftModelName(), draftstring);
        this.exit();
    }
});


/**
 * Devilry page header.
 */
Ext.define('devilry_header.Header', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader',
    margin: '0 0 0 0',
    height: 30, // NOTE: Make sure to adjust $headerHeight in the stylesheet if this is changed

    requires: [
        'devilry_header.FlatButton',
        'devilry_header.HoverMenu',
        'devilry_header.SearchMenu',
        'devilry_header.Roles',
        'devilry_authenticateduserinfo.UserInfo',
        'devilry_header.Breadcrumbs'
    ],


    navclass_to_rolename: {
        'no_role': gettext('Select role'),
        'student': gettext('Student'),
        'examiner': gettext('Examiner'),
        'subjectadmin': interpolate(gettext('%(Subject_term)s administrator'), {
            Subject_term: gettext('Subject')
        }, true),
        'nodeadmin': interpolate(gettext('%(Node_term)s administrator'), {
            Node_term: gettext('Node')
        }, true),
        'superuser': gettext('Superuser')
    },

    navclass_to_dashboard_url: {
        'student': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/#',
        'examiner': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/examiner/',
        'administrator': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/',
        'superuser': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/superuser/'
    },

    /**
     * @cfg {string} [navclass]
     * The css class to style the header buttons with.
     */

    /**
     * @cfg {Object} [breadcrumbs=devilry_header.Breadcrumbs]
     * The object to use for breadcrumbs. You can also set this after load with #setBreadcrumbComponent.
     * Defaults to an instance of devilry_header.Breadcrumbs.
     */

    constructor: function(config) {
        if(Ext.isEmpty(config.cls)) {
            config.cls = 'devilryheader';
        } else {
            config.cls = ['devilryheader', config.cls].join(' ');
        }
        if(!this.navclass_to_rolename[config.navclass]) {
            throw "Invalid navclass: " + config.navclass;
        }
        devilry_authenticateduserinfo.UserInfo.load(); // Load the userinfo as soon as possible.
        this.callParent(arguments);
    },

    initComponent: function() {
        var breadcrumbareaItem;
        if(this.breadcrumbs) {
            breadcrumbareaItem = this.breadcrumbs;
        } else {
            var defaultBreadcrumbs = [{
                url: this.navclass_to_dashboard_url[this.navclass],
                text: gettext('Dashboard')
            }];
            breadcrumbareaItem = Ext.widget('breadcrumbs', {
                defaultBreadcrumbs: defaultBreadcrumbs
            });
        }
        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'box',
                //width: 110,
                cls: 'devilrylogo',
                tpl: '<a class="logotext" href="{frontpageurl}">{text}</a>',
                data: {
                    text: 'Devilry',
                    frontpageurl: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/'
                }
            }, {
                xtype: 'devilryheader_flatbutton',
                itemId: 'currentRoleButton',
                cls: 'flatbutton currentrolebutton',
                listeners: {
                    scope: this,
                    render: this._onRenderCurrentRoleButton,
                    click: this._onClickCurrentRoleButton
                }
            }, {
                xtype: 'container',
                itemId: 'breadcrumbarea',
                cls: 'breadcrumbarea',
                items: [breadcrumbareaItem],
                flex: 1
            }, {
                xtype: 'devilryheader_flatbutton',
                itemId: 'searchButton',
                enableToggle: true,
                width: 50,
                tpl: [
                    '<div class="textwrapper bootstrap">',
                    '<i class="icon-search icon-white"></i>',
                    '</div>'
                ],
                data: {},
                listeners: {
                    scope: this,
                    render: this._onRenderSearchButton,
                    toggle: this._onToggleSearchButton
                }
            }, {
                xtype: 'devilryheader_flatbutton',
                itemId: 'userButton',
                enableToggle: true,
                width: 100,
                listeners: {
                    scope: this,
                    render: this._onRenderUserButton,
                    toggle: this._onToggleUserButton
                }
            }, {
                // NOTE: This component is floating, so it is not really part of the layout
                xtype: 'devilryheader_searchmenu',
                listeners: {
                    scope: this,
                    show: this._onShowSearchmenu,
                    hide: this._onHideSearchmenu
                }
            }, {
                // NOTE: This component is floating, so it is not really part of the layout
                xtype: 'devilryheader_hovermenu',
                listeners: {
                    scope: this,
                    show: this._onShowHovermenu,
                    hide: this._onHideHovermenu
                }
            }]
        });
        this.callParent(arguments);
    },

    _getCurrentRoleButton: function() {
        return this.down('#currentRoleButton');
    },
    _getHoverMenu: function() {
        return this.down('devilryheader_hovermenu');
    },
    _getUserButton: function() {
        return this.down('#userButton');
    },
    _getSearchButton: function() {
        return this.down('#searchButton');
    },
    _getSearchMenu: function() {
        return this.down('devilryheader_searchmenu');
    },
    _getBreadcrumbArea: function() {
        return this.down('#breadcrumbarea');
    },

    setBreadcrumbComponent: function(config) {
        this._getBreadcrumbArea().removeAll();
        this._getBreadcrumbArea().add(config);
    },

    _onRenderCurrentRoleButton: function() {
        this._getCurrentRoleButton().setText(this.navclass_to_rolename[this.navclass]);
        this._getCurrentRoleButton().addExtraClass(this.navclass);
    },
    _onRenderUserButton: function() {
        devilry_authenticateduserinfo.UserInfo.load(function(userInfoRecord) {
            this._getHoverMenu().setUserInfoRecord(userInfoRecord);
            this._getUserButton().addExtraClass(this.navclass);
            this._getUserButton().setText(userInfoRecord.getDisplayName());
        }, this);
    },

    _onClickCurrentRoleButton: function() {
        this._getUserButton().toggle();
    },

    _onToggleUserButton: function(button) {
        var hovermenu = this._getHoverMenu();
        if(button.pressed) {
            hovermenu.show();
        } else {
            hovermenu.hide();
        }
    },

    _onShowHovermenu: function() {
        this._getSearchButton().setPressedWithEvent(false); // Hide search menu when showing hover menu
        this._getCurrentRoleButton().setPressedCls();
        this._getUserButton().setPressedCls();
    },
    _onHideHovermenu: function() {
        this._getCurrentRoleButton().setNotPressedCls();
        this._getUserButton().setNotPressedCls();
    },


    _onRenderSearchButton:function () {
        this._getSearchButton().addExtraClass('devilry_header_search_button');
    },

    _onToggleSearchButton: function(button) {
        var searchmenu = this._getSearchMenu();
        if(button.pressed) {
            searchmenu.show();
        } else {
            searchmenu.hide();
        }
    },

    _onShowSearchmenu: function() {
        this._getUserButton().setPressedWithEvent(false); // Hide hover menu when showing search menu
        this._getSearchButton().setPressedCls();
    },
    _onHideSearchmenu: function() {
        this._getSearchButton().setPressed(false);
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterChainEditor', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-filterchaineditor',
    hideHeaders: true,

    config: {
        filterchain: undefined,
        assignment_store: undefined
    },

    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterEditor'
    ],

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.store = this.filterchain;

        Ext.apply(this, {
            columns: [{
                header: 'Filters', dataIndex: 'filter', flex: 1,
                renderer: function(filter, p, record) {
                    return filter.toReadableSummary(this.assignment_store);
                }
            }],
            tbar: [this.removeButton = Ext.widget('button', {
                text: 'Remove',
                iconCls: 'icon-delete-16',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onClickDelete
                }
            }), {
                xtype: 'button',
                text: 'Add',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this._onClickAddFilter
                }
            }]
        });
        this.on('selectionchange', this._onSelectionChange, this);
        this.on('itemdblclick', this._onItemDblClick, this);
        this.callParent(arguments);
    },

    _onItemDblClick: function(grid, filterRecord) {
        this._editFilter(filterRecord);
    },

    _onSelectionChange: function(grid, selected) {
        if(selected.length === 0) {
            this.removeButton.disable();
        } else {
            this.removeButton.enable();
        }
    },

    _onClickDelete: function() {
        var selected = this.getSelectionModel().getSelection();
        if(selected.length != 1) {
            Ext.MessageBox.alert('Error', 'Please select a row from the list.');
            return;
        }
        var selectedItem = selected[0];
        this.store.remove(selectedItem);
    },

    _onClickAddFilter: function() {
        this._editFilter();
    },

    _editFilter: function(filterRecord) {
        var win = Ext.widget('window', {
            layout: 'fit',
            title: 'Edit rule',
            onEsc: Ext.emptyFn,
            modal: true,
            width: 600,
            height: 400,
            items: {
                xtype: 'statistics-filtereditor',
                filterRecord: filterRecord,
                assignment_store: this.assignment_store,
                listeners: {
                    scope: this,
                    addFilter: function(filterArgs, filterRecord) {
                        win.close();
                        this._onAddFilter(filterArgs, filterRecord);
                    }
                }
            }
        });
        win.show();
    },

    _onAddFilter: function(filterArgs, filterRecord) {
        if(filterRecord) {
            filterRecord.set('filter', this.filterchain.createFilter(filterArgs));
            filterRecord.commit();
        } else {
            this.filterchain.addFilter(filterArgs);
        }
    }
});


Ext.define('devilry.administrator.node.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-nodelayout',

    requires: [
        'devilry.administrator.node.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Node',
        'devilry.administrator.ListOfChildnodes',
        'devilry.statistics.activeperiods.Overview'
    ],
    
    /**
     * @cfg
     */
    nodeid: undefined,

    nodemodel_name: 'devilry.apps.administrator.simplified.SimplifiedNode',
    
    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {},
                cls: 'section treeheading',
                tpl: [
                    '<tpl if="!hasdata">',
                    '   <span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                    '    <h1 class="endoflist">',
                    '       {node.long_name}',
                    '    </h1>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                items: [this.prettyview = Ext.widget('administrator_nodeprettyview', {
                    title: 'Administer',
                    modelname: this.nodemodel_name,
                    objectid: this.nodeid,
                    dashboardUrl: DASHBOARD_URL,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        loadmodelFailed: this._onLoadRecordFailed,
                        edit: this._onEdit
                    }
                }), this.activePeriodsTab = Ext.widget('panel', {
                    title: 'Active periods/semesters (loading...)',
                    frame: false,
                    border: false,
                    layout: 'fit',
                    disabled: true,
                    listeners: {
                        scope: this,
                        activate: this._onActivePeriods
                    }
                }), {
                    xtype: 'administrator-listofchildnodes',
                    title: 'Direct childnodes',
                    parentnodeid: this.nodeid,
                    orderby: 'short_name',
                    modelname: 'devilry.apps.administrator.simplified.SimplifiedNode',
                    readable_type: 'node',
                    urlrolepart: 'node'
                }, {
                    xtype: 'administrator-listofchildnodes',
                    title: 'Subjects',
                    parentnodeid: this.nodeid,
                    orderby: 'short_name',
                    modelname: 'devilry.apps.administrator.simplified.SimplifiedSubject',
                    readable_type: 'subject',
                    urlrolepart: 'subject'
                }]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(nodeRecord) {
        this.nodeRecord = nodeRecord;
        this.activePeriodsTab.enable();
        this.activePeriodsTab.setTitle('Active periods/semesters');
        this.heading.update({
            hasdata: true,
            node: nodeRecord.data
        });
    },

    _onLoadRecordFailed: function(operation) {
        this.removeAll();
        var title = operation.error.statusText;
        if(operation.error.status == '403') {
            title = gettext('Permission denied');
            message = gettext('You are not administrator on this item or any of its parents.');
        }
        this.add({
            xtype: 'box',
            padding: 20,
            tpl: [
                '<div class="section warning">',
                    '<h2>{title}</h2>',
                    '<p>{message}</p>',
                '</div>'
            ],
            data: {
                title: title,
                message: message
            }
        });
    },

    _onActivePeriods: function(tab) {
        if(this.activePeriodsLoaded) {
            return;
        }
        this.activePeriodsLoaded = true;
        this.activePeriodsTab.add({
            xtype: 'activeperiods-overview',
            nodeRecord: this.nodeRecord
        });
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.nodemodel_name,
            editform: Ext.widget('administrator_nodeform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    }
});


/** Panel to show StaticFeedback info and create new static feedbacks.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor', {
    extend: 'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditor',
    requires: [
        'devilry.gradeeditors.DraftEditorWindow',
        'devilry.gradeeditors.RestfulRegistryItem',
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    config: {
        /**
         * @cfg {object} [gradeeditor_config_recordcontainer]
         * A {@link devilry.extjshelpers.SingleRecordContainer} for GradeEditor Config.
         */
        gradeeditor_config_recordcontainer: undefined,

        /**
         * @cfg {bool} [isAdministrator]
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        assignmentgroupmodel: undefined,
        deadlinemodel: undefined
    },

    constructor: function(config) {
        return this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);

        this.staticfeedback_recordcontainer.addListener('setRecord', this.onSetStaticFeedbackRecordInEditor, this);
        this.on('afterStoreLoadMoreThanZero', this.onAfterStoreLoadMoreThanZero, this);

        if(this.gradeeditor_config_recordcontainer.record) {
            this.onLoadGradeEditorConfig();
        }
        this.gradeeditor_config_recordcontainer.addListener('setRecord', this.onLoadGradeEditorConfig, this);

        this.registryitem_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer.addListener('setRecord', this.onLoadRegistryItem, this);

        this.assignmentgroup_recordcontainer.addListener('setRecord', this.enableEditButton, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDeliveryInEditor();
        }
        this.delivery_recordcontainer.on('setRecord', this.onLoadDeliveryInEditor, this);
    },


    getToolbarItems: function() {
        var defaultItems = this.callParent();
        var group = this.assignmentgroup_recordcontainer.record;
        if(group.get('is_open')) {
            this.createButton = Ext.create('Ext.button.Button', {
                text: [
                    '<i class="icon-pencil"></i> ',
                    gettext('Create feedback')
                ].join(''),
                hidden: false,
                cls: 'bootstrap',
                scale: 'medium',
                listeners: {
                    scope: this,
                    click: this.loadGradeEditor,
                    render: this.onRenderEditButton
                }
            });
            Ext.Array.insert(defaultItems, 0, [this.createButton]);
        }
        return defaultItems;
    },


    /**
     * @private
     */
    onAfterStoreLoadMoreThanZero: function() {
        this.enableEditButton();
        if(this.editFeedbackTip) {
            this.editFeedbackTip.hide();
        }
    },

    /**
     * @private
     */
    onRenderEditButton: function(button) {
        //var id = button.getEl().id
        Ext.defer(function() {
            if(!this.isReadyToEditFeedback()) {
                button.getEl().mask(gettext('Loading') + ' ...');
            }
        }, 100, this);
        this.editFeedbackTip = Ext.create('Ext.tip.ToolTip', {
            title: gettext('Click to give feedback on this delivery'),
            anchor: 'top',
            target: button.getEl().id,
            html: gettext('You add a feedback to a specific delivery. The latest feedback you publish on any delivery on this assignment becomes their active feedback/grade on the assignment.'),
            width: 415
//            dismissDelay: 35000,
//            autoHide: true
        });
    },

    onLoadDelivery: function() {
        this.callParent(arguments);
        var group = this.assignmentgroup_recordcontainer.record;
        if(group.get('parentnode__delivery_types') !== 1) {
            this._addElectronicDeliveryExtras();
        }
    },

    _addElectronicDeliveryExtras: function() {
        var deliveryrecord = this.delivery_recordcontainer.record;
        var panel = this.down('filemetabrowserpanel');
        panel.loadFilesForDelivery(deliveryrecord.get('id'));
        panel.show();
    },


    /**
     * @private
     */
    showNoFeedbackTip: function() {
        if(this.editFeedbackTip) {
            this.editFeedbackTip.show();
        } else {
            Ext.defer(function() {
                this.showNoFeedbackTip();
            }, 300, this);
        }
    },

    /**
     * @private
     * This is suffixed with InEditor to not crash with superclass.onLoadDelivery().
     */
    onLoadDeliveryInEditor: function() {
        this.enableEditButton();
    },

    /**
     * @private
     */
    onLoadGradeEditorConfig: function() {
        this.loadRegistryItem();
    },

    /**
     * @private
     */
    loadRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        registryitem_model.load(this.gradeeditor_config_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(record) {
                this.registryitem_recordcontainer.setRecord(record);
            }
        });
    },

    /**
     * @private
     */
    onLoadRegistryItem: function() {
        this.enableEditButton();
    },

    /**
     * @private
     * Show create button when:
     *
     * - Delivery has loaded.
     * - Grade editor config has loaded.
     * - Registry item has loaded.
     */
    enableEditButton: function() {
        if(this.isReadyToEditFeedback() && !Ext.isEmpty(this.createButton)) {
            this.createButton.getEl().unmask();
        }
    },

    /**
     * @private
     */
    isReadyToEditFeedback: function() {
        return this.gradeeditor_config_recordcontainer.record &&
                this.delivery_recordcontainer.record &&
                this.registryitem_recordcontainer.record &&
                this.assignmentgroup_recordcontainer.record;
    },

    /**
     * @private
     */
    loadGradeEditor: function() {
        Ext.widget('gradedrafteditormainwin', {
            deliveryid: this.delivery_recordcontainer.record.data.id,
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            listeners: {
                scope: this,
                publishNewFeedback: this.onPublishNewFeedback
            }
        }).show();
    },

    /**
     * Overrides parent method to enable examiners to click to create feedback.
     */
    bodyWithNoFeedback: function() {
        var me = this;
        this.setBody({
            xtype: 'component',
            html: ''
        });
//        this.showNoFeedbackTip();
        //this.setBody({
            //xtype: 'component',
            //cls: 'no-feedback-editable',
            //html: '<p class="no-feedback-message">No feedback</p><p class="click-create-create-feedback-message">Click to create feedback</p>',
            //listeners: {
                //render: function() {
                    //this.getEl().addListener('mouseup', me.loadGradeEditor, me);
                //}
            //}
        //});
    },

    /**
     * @private
     */
    onPublishNewFeedback: function() {
        this.hasNewPublishedStaticFeedback = true;
        this.onLoadDelivery();
    },

    /**
     * @private
     */
    onSetStaticFeedbackRecordInEditor: function() {
        if(this.hasNewPublishedStaticFeedback) {
            this.hasNewPublishedStaticFeedback = false;
            this.onNewPublishedStaticFeedback();
        }
    },

    /**
     * @private
     */
    onNewPublishedStaticFeedback: function() {
        var staticfeedback = this.staticfeedback_recordcontainer.record.data;
        if(staticfeedback.is_passing_grade) {
            this.reloadAssignmentGroup();
        } else {
            this.onFailingGrade();
        }
    },

    /**
     * @private
     */
    reloadAssignmentGroup: function() {
        window.location.reload();
//        this.assignmentgroupmodel.load(this.assignmentgroup_recordcontainer.record.data.id, {
//            scope: this,
//            success: function(record) {
//                this.assignmentgroup_recordcontainer.setRecord(record);
//            },
//            failure: function() {
//                TODO: Handle errors
//            }
//        });
    },

    /**
     * @private
     */
    onFailingGrade: function() {
        var win = Ext.MessageBox.show({
            title: gettext('You published a feedback with a failing grade'),
            msg: [
                '<p>', gettext('Would you like to give them another try?'), '</p>',
                '<ul>',
                    '<li>',
                        gettext('Choose <strong>yes</strong> to create a new deadline'),
                    '</li>',
                    '<li>',
                        gettext('Choose <strong>no</strong> to close the group. This fails the student(s) on this assignment. You can re-open the group at any time.'),
                    '</li>',
                '</ul>'
            ].join(''),
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId === 'yes') {
                    this.createNewDeadline();
                } else {
                    this.reloadAssignmentGroup();
                }
            }
        });
    },

    /**
     * @private
     */
    createNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                me.reloadAssignmentGroup();
                this.close();
            }
        });
        createDeadlineWindow.show();
    }
});


Ext.define('devilry.administrator.DashboardButtonBar', {
    extend: 'devilry.extjshelpers.ButtonBar',
    cls: 'dashboard-buttonbar',

    requires: [
        'devilry.extjshelpers.forms.administrator.Node',
        'devilry.extjshelpers.forms.administrator.Subject',
        'devilry.extjshelpers.forms.administrator.Period',
        'devilry.extjshelpers.forms.administrator.Assignment',
        'devilry.administrator.DefaultCreateWindow',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.ButtonBarButton'
    ],

    node_modelname: 'devilry.apps.administrator.simplified.SimplifiedNode',
    subject_modelname: 'devilry.apps.administrator.simplified.SimplifiedSubject',
    period_modelname: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
    assignment_modelname: 'devilry.apps.administrator.simplified.SimplifiedAssignment',


    /**
     * @cfg
     * (Required)
     */
    is_superuser: undefined,

    initComponent: function() {
        var nodestore_node = this._createStore(this.node_modelname);
        var nodestore = this._createStore(this.node_modelname);
        var subjectstore = this._createStore(this.subject_modelname);
        var periodstore = this._createStore(this.period_modelname);
        
        var me = this;
        Ext.apply(this, {
            items: [{
                xtype: 'buttonbarbutton',
                is_superuser: this.is_superuser,
                text: gettext('Node'),
                store: nodestore_node,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        '<span class="tooltip-title-current-item">', gettext('Node'), '</span> &rArr; ',
                        gettext('Subject'), ' &rArr; ',
                        gettext('Period'), ' &rArr; ',
                        gettext('Assignment')
                    ].join(''),
                    body: interpolate(gettext('A %(Node_term)s is a place to organise top-level administrators.'), {
                        Node_term: gettext('Node')
                    }, true)
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(node_term)s'), {
                            node_term: gettext('node')
                        }, true),
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.node_modelname,
                            editform: Ext.widget('administrator_nodeform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'node/{id}')
                    }).show();
                }
            }, {
                xtype: 'buttonbarbutton',
                text: gettext('Subject'),
                store: nodestore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        gettext('Node'), ' &rArr; ',
                        '<span class="tooltip-title-current-item">', gettext('Subject'), '</span> &rArr; ',
                        gettext('Period'), ' &rArr; ',
                        gettext('Assignment')
                    ].join(''),
                    body: ''
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(subject_term)s'), {
                            subject_term: gettext('subject')
                        }, true),
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.subject_modelname,
                            editform: Ext.widget('administrator_subjectform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'subject/{id}')
                    }).show();
                }
            }, {
                xtype: 'buttonbarbutton',
                text: gettext('Period'),
                store: subjectstore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        gettext('Node'), ' &rArr; ',
                        gettext('Subject'), ' &rArr; ',
                        '<span class="tooltip-title-current-item">', gettext('Period'), '</span> &rArr; ',
                        gettext('Assignment')
                    ].join(''),
                    body: ''
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(period_term)s'), {
                            period_term: gettext('period')
                        }, true),
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.period_modelname,
                            editform: Ext.widget('administrator_periodform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'period/{id}')
                    }).show();
                }
            }, {
                xtype: 'buttonbarbutton',
                text: gettext('Assignment'),
                store: periodstore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        gettext('Node'), ' &rArr; ',
                        gettext('Subject'), ' &rArr; ',
                        gettext('Period'), ' &rArr; ',
                        '<span class="tooltip-title-current-item">', gettext('Assignment'), '</span>'
                    ].join(''),
                    body: interpolate(gettext('An %(assignment_term)s, such as an obligatory %(assignment_term)s, an anoymous home examination or a semester %(assignment_term)s.'), {
                        assignment_term: gettext('assignment')
                    }, true)
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(assignment_term)s'), {
                            assignment_term: gettext('assignment')
                        }, true),
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.assignment_modelname,
                            editform: Ext.widget('administrator_assignmentform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'assignment/{id}')
                    }).show();
                }
            }]
        });
        this.callParent(arguments);
    },

    _createStore: function(modelname) {
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            pageSize: 1,
            proxy: model.proxy.copy()
        });
        return store;
    },
});


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


/** Assignment layout TODO-list. Reloads the TODO-list whenever it is shown (on
 * the show-event). */
Ext.define('devilry.examiner.AssignmentLayoutTodoList', {
    extend: 'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
    alias: 'widget.examiner-assignmentlayout-todolist',

    requires: [
        'devilry.extjshelpers.studentsmanager.StudentsManager',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
        'devilry.extjshelpers.charts.PointsOfGroupsOnSingleAssignment'
    ],

    /**
     * @cfg
     * Assignment ID to show todo items within (Required).
     */
    assignmentid: undefined,

    initComponent: function() {
        Ext.apply(this, {
            title: gettext('Todo-list'),
            toolbarExtra: ['->', {
                xtype: 'button',
                scale: 'medium',
                text: '<i class="icon-download"></i> ' + gettext('Download all deliveries'),
                cls: 'bootstrap',
                listeners: {
                    scope: this,
                    click: this.onDownload
                }
            }],
            
            helpTpl: Ext.create('Ext.XTemplate',
                '<div class="section helpsection">',
                '   {todohelptext}',
                '   <p>Choose the <span class="menuref">Detailed overview of all students tab</span> to view all groups, and to give feedback in bulk.</p>',
                '   <p>You may want to <span class="menuref">Download all deliveries</span> as a zip file instead of downloading the delivery for each student/group separately. This will download all deliveries from all assignment groups where you are examiner on this assignment, not just the deliveries in your todo-list.</p>',
                '</div>'
            ),

            //onSelectGroup: function(grid, assignmentgroupRecord) {
                //var url = Ext.String.format('../assignmentgroup/{0}',
                    //assignmentgroupRecord.data.id
                //);
                //window.location.href = url;
            //},
            getGroupUrlPrefix: function() {
                return '../assignmentgroup/';
            }
        });
        this.on('show', this._loadTodoList);
        this.callParent(arguments);
        this._loadTodoList();
    },


    _loadTodoList: function() {
        this.loadTodoListForAssignment(this.assignmentid);
    },

    onDownload: function() {
        window.location.href = Ext.String.format('compressedfiledownload/{0}', this.assignmentid);
    }
});


/**
 *
 * Requires the following icnlude in the django template:
 *
 *     {% include "extjshelpers/AssignmentGroupOverviewExtjsClasses.django.html" %}
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupoverview',
    cls: 'widget-assignmentgroupoverview devilry_subtlebg',
    requires: [
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline',
        'devilry.extjshelpers.assignmentgroup.IsOpen',
        'devilry.extjshelpers.RestFactory',
        'devilry.administrator.models.Delivery',
        'devilry.examiner.models.Delivery',
        'devilry.student.models.Delivery',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.assignmentgroup.DeadlineExpiredNoDeliveriesBox'
    ],

    nonElectronicNodeTpl: Ext.create('Ext.XTemplate',
        '<div class="bootstrap">',
            '<div class="alert" style="margin: 0;">',
                '<p><strong>Warning</strong>: This assignment only uses Devilry for registering results, not for deliveries. ',
                'Deliveries are registered (by examiners) as a placeholder for results.</p>',
                '<tpl if="canExamine">',
                '   <p>See <a href="{DEVILRY_HELP_URL}" target="_blank">help</a> for details about how to correct non-electronic deliveries.</p>',
                '</tpl>',
            '</div>',
        '</div>'
    ),

    /**
     * @cfg {bool} [canExamine]
     * Enable creation of new feedbacks? Defaults to ``false``.
     *
     * When this is ``true``, the authenticated user still needs to have
     * permission to POST new feedbacks for the view to work.
     */
    canExamine: false,

    /**
     * @cfg {int} [assignmentgroupid]
     * AssignmentGroup ID.
     */
    assignmentgroupid: undefined,

    /**
     * @cfg {bool} [isAdministrator]
     * Use the administrator RESTful interface to store drafts? If this is
     * ``false``, we use the examiner RESTful interface.
     */
    isAdministrator: false,


    autoScroll: true,


    constructor: function() {
        this.addEvents('assignmentGroupLoaded');
        this.callParent(arguments);
    },


    initComponent: function() {
        this.assignmentgroup_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.delivery_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditor_config_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');

        this.createAttributes();
        this.createLayout();
        this.callParent(arguments);
        this.loadAssignmentgroupRecord(); // NOTE: Must come after createLayout() because components listen for the setRecord event
    },

    /**
     * @private
     */
    createAttributes: function() {
        this.role = !this.canExamine? 'student': this.isAdministrator? 'administrator': 'examiner';
        this.assignmentgroupmodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedAssignmentGroup'));
        this.filemetastore = this._createStore('SimplifiedFileMeta');
        this.staticfeedbackstore = this._createStore('SimplifiedStaticFeedback');
        this.deadlinemodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedDeadline'));

        if(this.canExamine) {
            this.gradeeditor_config_model = Ext.ModelManager.getModel(Ext.String.format(
                'devilry.apps.gradeeditors.simplified.{0}.SimplifiedConfig',
                this.role
            ));
        }
    },


    _createStore: function(shortmodelname) {
        var modelname = this.getSimplifiedClassName(shortmodelname);
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
        return store;
    },

    /**
     * @private
     */
    loadAssignmentgroupRecord: function() {
        this.assignmentgroupmodel.load(this.assignmentgroupid, {
            scope: this,
            success: function(record) {
                this.assignmentgroup_recordcontainer.setRecord(record);
                this.loadGradeEditorConfigModel();
                this.fireEvent('assignmentGroupLoaded', record);
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
    },

    /**
     * @private
     */
    loadGradeEditorConfigModel: function() {
        if(this.canExamine) {
            this.gradeeditor_config_model.load(this.assignmentgroup_recordcontainer.record.data.parentnode, {
                scope: this,
                success: function(record) {
                    this.gradeeditor_config_recordcontainer.setRecord(record);
                },
                failure: function() {
                    // TODO: Handle errors
                }
            });
        }
    },

    /**
     * @private
     */
    getSimplifiedClassName: function(name) {
        var classname = Ext.String.format(
            'devilry.apps.{0}.simplified.{1}',
            this.role, name
        );
        return classname;

    },

    /**
     * @private
     */
    _showFeedbackPanel: function() {
        if(this.delivery_recordcontainer.record && this.assignmentgroup_recordcontainer.record) {
            if(!this.feedbackPanel) {
                this.feedbackPanel = Ext.widget('staticfeedbackeditor', {
                    staticfeedbackstore: this.staticfeedbackstore,
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    filemetastore: this.filemetastore,
                    assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                    isAdministrator: this.isAdministrator, // Only required by staticfeedbackeditor
                    deadlinemodel: this.deadlinemodel, // Only required by staticfeedbackeditor
                    assignmentgroupmodel: this.assignmentgroupmodel, // Only required by staticfeedbackeditor
                    gradeeditor_config_recordcontainer: this.gradeeditor_config_recordcontainer // Only required by staticfeedbackeditor
                });
                this.centerArea.removeAll();
                this.centerArea.add(this.feedbackPanel);
            }
        }
    },

    _showNonElectronicNote: function() {
        if(this.assignmentgroup_recordcontainer.record.get('parentnode__delivery_types') === 1) {
            this.nonElectronicNote.show();
        }
    },

    /**
     * @private
     */
    createLayout: function() {
        if(this.delivery_recordcontainer.record) {
            this._showFeedbackPanel();
        } else {
            this.delivery_recordcontainer.addListener('setRecord', this._showFeedbackPanel, this);
        }
        if(this.assignmentgroup_recordcontainer.record) {
            this._showFeedbackPanel();
            this._showNonElectronicNote();
        } else {
            this.assignmentgroup_recordcontainer.addListener('setRecord', this._showFeedbackPanel, this);
            this.assignmentgroup_recordcontainer.addListener('setRecord', this._showNonElectronicNote, this);
        }

        Ext.apply(this, {
            layout: 'anchor',
            padding: '20 30 20 30',
            defaults: {anchor: '100%'},
            items: [{
                xtype: 'deadlineExpiredNoDeliveriesBox',
                hidden: true,
                listeners: {
                    scope: this,
                    closeGroup: this._onCloseGroup,
                    addDeadline: this._onCreateNewDeadline
                }
            }, {
                xtype: 'container',
                layout: 'column',
                items: [{
                    columnWidth: 1,
                    xtype: 'assignmentgrouptitle',
                    singlerecordontainer: this.assignmentgroup_recordcontainer,
                    margin: '0 0 10 0',
                    extradata: {
                        canExamine: this.canExamine,
                        url: window.location.href
                    }
                }, {
                    xtype: 'container',
                    width: 350,
                    layout: 'column',
//                    defaults: {anchor: '100%'},
                    items: [{
                        xtype: 'assignmentgroup_isopen',
                        columnWidth: 0.6,
                        assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                        canExamine: this.canExamine
                    }, {
                        xtype: 'button',
                        columnWidth: 0.4,
                        hidden: !this.canExamine,
                        text: '<i class="icon-white icon-th-list"></i> ' + gettext('To-do list'),
                        cls: 'bootstrap',
                        scale: 'medium',
                        ui: 'inverse',
                        margin: '0 0 0 3',
                        listeners: {
                            scope: this,
                            click: function() {
                                Ext.create('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow', {
                                    assignmentgroupmodelname: this.getSimplifiedClassName('SimplifiedAssignmentGroup'),
                                    assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer
                                }).show();
                            }
                        }
                    }]
                }]
            }, {
                xtype: 'container',
                layout: 'column',
                style: 'background-color: transparent',
                flex: 1,
                border: false,
                items: [{
                    xtype: 'container',
                    margin: '0 40 0 0',
                    columnWidth: 0.3,
                    layout: 'anchor',
                    defaults: {anchor: '100%'},
                    items: [{
                        xtype: 'container',
                        margin: '8 0 0 0',
                        flex: 1,
                        border: false,
                        layout: {
                            type: 'vbox',
                            align: 'stretch'
                        },
                        items: [this.nonElectronicNote = Ext.widget('box', {
                            margin: '0 0 10 0',
                            hidden: true,
                            cls: 'readable-section',
                            html: this.nonElectronicNodeTpl.apply({canExamine: this.canExamine, DEVILRY_HELP_URL: DevilrySettings.DEVILRY_HELP_URL})
                        }), {
                            xtype: 'deliveriesgroupedbydeadline',
                            minHeight: 40,
                            role: this.role,
                            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                            delivery_recordcontainer: this.delivery_recordcontainer,
                            flex: 1,
                            listeners: {
                                scope: this,
                                loadComplete: this._selectAppropriateDelivery,
                                expiredNoDeliveries: this._onExpiredNoDeliveries,
                                createNewDeadline: this._onCreateNewDeadline
                            }
                        }]
                    }]
                }, this.centerArea = Ext.widget('container', {
                    columnWidth: 0.7,
                    layout: 'fit',
                    items: {
                        xtype: 'box',
                        html: ''
                    }
                })]
            }]
        });
    },

    /**
     * @private
     *
     * Select most natural delivery:
     *  - The one with active feedback
     *  - ... unless a delivery with timestamp after the latest feedback.
     */
    _selectMostNaturalDelivery: function(deliveriesgroupedbydeadline) {
        var latestDelivery = deliveriesgroupedbydeadline.getLatestDelivery();
        if(!latestDelivery) {
            return;
        }
        if(deliveriesgroupedbydeadline.latestStaticFeedbackRecord) {
            var latestFeedbackTime = deliveriesgroupedbydeadline.latestStaticFeedbackRecord.get('save_timestamp');
            if(latestDelivery.get('time_of_delivery') > latestFeedbackTime) {
                deliveriesgroupedbydeadline.selectDelivery(latestDelivery.get('id'));
            } else {
                deliveriesgroupedbydeadline.selectDelivery(deliveriesgroupedbydeadline.latestStaticFeedbackRecord.get('delivery'));
            }
        } else {
            deliveriesgroupedbydeadline.selectDelivery(latestDelivery.get('id'));
        }
    },

    _selectAppropriateDelivery: function(deliveriesgroupedbydeadline) {
        var query = Ext.Object.fromQueryString(window.location.search);
        if(query.deliveryid) {
            deliveriesgroupedbydeadline.selectDelivery(query.deliveryid);
        } else {
            this._selectMostNaturalDelivery(deliveriesgroupedbydeadline);
        }
    },


    /**
     * @private
     */
    _onCreateNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: Ext.String.format('devilry.{0}.models.Deadline', this.role),
            onSaveSuccess: function(record) {
                this.close();
//                me.loadAllDeadlines();
                window.location.reload();
            }
        });
        createDeadlineWindow.show();
    },

    _onCloseGroup:function () {
        devilry.extjshelpers.assignmentgroup.IsOpen.closeGroup(this.assignmentgroup_recordcontainer, function() {
            window.location.reload();
        });
    },


    /**
     * @private
     */
    _onExpiredNoDeliveries: function() {
        var group = this.assignmentgroup_recordcontainer.record;
        if(group.get('is_open')) {
            this.down('deadlineExpiredNoDeliveriesBox').show();
        }
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterChainEditor'
    ],

    initComponent: function() {
        this.filterchain = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain', {
            filterArgsArray: this.settings? this.settings.filterArgsArray: undefined
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'box',
                cls: 'readable-section',
                html: Ext.String.format('Advanced filters have a dedicated guide in the Administrator section of the <a href="{0}" target="_blank">Help</a>.', DevilrySettings.DEVILRY_HELP_URL)
            }, {
                xtype: 'statistics-filterchaineditor',
                title: 'Rules',
                filterchain: this.filterchain,
                assignment_store: this.loader.assignment_store,
                flex: 1,
                margin: '10 0 10 0'
            }, this.defaultButtonPanel]
        });

        this.callParent(arguments);
    },

    getSettings: function() {
        return {
            filterArgsArray: this.filterchain.toExportArray()
        };
    },

    filter: function(studentRecord) {
        return this.filterchain.match(this.loader, studentRecord);
    }
});


Ext.define('devilry.administrator.studentsmanager.StudentsManager', {
    extend: 'devilry.extjshelpers.studentsmanager.StudentsManager',
    alias: 'widget.administrator_studentsmanager',
    requires: [
        'devilry.extjshelpers.studentsmanager.ImportGroupsFromAnotherAssignment'
    ],

    mixins: {
        manageExaminers: 'devilry.administrator.studentsmanager.StudentsManagerManageExaminers',
        createGroups: 'devilry.administrator.studentsmanager.StudentsManagerManageGroups',
        loadRelatedUsers: 'devilry.administrator.studentsmanager.LoadRelatedUsersMixin'
    },

    //config: {
        //assignmentgroupPrevApprovedStore: undefined
    //},

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.addStudentsButton = Ext.widget('button', {
            text: interpolate(gettext('Add %(students_term)s'), {
                students_term: gettext('students')
            }, true),
            iconCls: 'icon-add-32',
            scale: 'large',
            menu: [{
                text: interpolate(gettext('Import %(students_term)s registered in %(syncsystem)s'), {
                    students_term: gettext('students'),
                    syncsystem: DevilrySettings.DEVILRY_SYNCSYSTEM
                }, true),
                listeners: {
                    scope: this,
                    click: this.onOneGroupForEachRelatedStudent
                }
            }, {
                text: interpolate(gettext('Import from another %(assignment_term)s'), {
                    assignment_term: gettext('assignment')
                }, true),
                listeners: {
                    scope: this,
                    click: this.onImportGroupsFromAnotherAssignmentInCurrentPeriod
                }
            }, {
                text: gettext('Manually'),
                listeners: {
                    scope: this,
                    click: this.onManuallyCreateUsers
                }
            }]
        });

        this.callParent(arguments);
    },

    getToolbarItems: function() {
        var defaults = this.callParent();
        Ext.Array.insert(defaults, 2, [this.addStudentsButton, {
            xtype: 'button',
            text: interpolate(gettext('Set %(examiners_term)s'), {
                examiners_term: gettext('examiners')
            }, true),
            scale: 'large',
            menu: this.getSetExaminersMenuItems()
        }]);
        return defaults;
    },

    getSetExaminersMenuItems: function() {
        return [{
            text: gettext('Replace'),
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onReplaceExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Replace %(examiners_term)s'), {
                            examiners_term: gettext('examiners')
                        }, true),
                        html: interpolate(gettext('Replace %(examiners_term)s on the selected %(groups_term)s (removes current %(examiners_term)s).'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Add'),
            iconCls: 'icon-add-16',
            listeners: {
                scope: this,
                click: this.onAddExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Add %(examiners_term)s'), {
                            examiners_term: gettext('examiners')
                        }, true),
                        html: interpolate(gettext('Add %(examiners_term)s to the selected %(groups_term)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Random distribute'),
            listeners: {
                scope: this,
                click: this.onRandomDistributeExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        html: interpolate(gettext('Random distribute a list of %(examiners_term)s to the selected %(groups_term)s. Replaces current %(examiners_term)s on the selected %(groups_term)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: interpolate(gettext('Copy from another %(assignment_term)s'), {
                assignment_term: gettext('assignment')
            }, true),
            listeners: {
                scope: this,
                click: this.onImportExaminersFromAnotherAssignmentInCurrentPeriod,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Copy from another %(assignment_term)s'), {
                            assignment_term: gettext('assignment')
                        }, true),
                        html: interpolate(gettext('Lets you choose another %(assignment_term)s, and import %(examiners_term)s. Replaces current %(examiners_term)s on the selected %(groups_term)s.'), {
                            assignment_term: gettext('assignment'),
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Automatically'),
            listeners: {
                scope: this,
                click: this.onSetExaminersFromTags,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: interpolate(gettext('Automatically set %(examiners_term)'), {
                            examiners_term: gettext('examiners')
                        }, true),
                        html: interpolate(gettext('Match tagged %(examiners_term)s to equally tagged %(groups_term)s. Tags are normally imported from %(syncsystem)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups'),
                            syncsystem: DevilrySettings.DEVILRY_SYNCSYSTEM
                        }, true)
                    });
                }
            }
        }, {
            text: gettext('Clear'),
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: this.onClearExaminers,
                render: function(menuitem) {
                    this._addMenuItemTooltip(menuitem, {
                        title: gettext('Clear'),
                        html: interpolate(gettext('Remove all %(examiners_term)s on selected %(groups_term)s.'), {
                            examiners_term: gettext('examiners'),
                            groups_term: gettext('groups')
                        }, true)
                    });
                }
            }
        }];
    },

    getContexMenuManySelectItems: function() {
        var defaultItems = this.callParent();
        return Ext.Array.merge(defaultItems, [{
            text: interpolate(gettext('Set %(examiners_term)s'), {
                examiners_term: gettext('examiners')
            }, true),
            menu: this.getSetExaminersMenuItems()
        }]);
    },

    getFilters: function() {
        var defaultFilters = this.callParent();
        var me = this;
        var adminFilters = [{xtype: 'menuheader', html: 'Missing users'}, {
            text: interpolate(gettext('Has no %(students_term)s'), {
                students_term: gettext('students')
            }, true),
            handler: function() { me.setFilter('candidates__student__username:none'); }
        }, {
            text: interpolate(gettext('Has no %(examiners_term)s'), {
                examiners_term: gettext('examiners')
            }, true),
            handler: function() { me.setFilter('examiners__user__username:none'); }
        }];
        Ext.Array.insert(adminFilters, 0, defaultFilters);
        return adminFilters;
    },

    getOnSingleMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: gettext('Change group members'),
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onChangeGroupMembers
            }
        });
        menu.push({
            text: gettext('Change group name'),
            iconCls: 'icon-edit-16',
            listeners: {
                scope: this,
                click: this.onChangeGroupName
            }
        });
        return menu;
    },

    getOnManyMenuItems: function() {
        var menu = this.callParent();
        menu.push({
            text: interpolate(gettext('Mark as delivered in a previous %(period_term)s'), {
                period_term: gettext('period')
            }, true),
            listeners: {
                scope: this,
                click: this.onPreviouslyPassed
            }
        });
        menu.push({
            text: gettext('Delete'),
            iconCls: 'icon-delete-16',
            listeners: {
                scope: this,
                click: this.onDeleteGroups
            }
        });
        if(this.assignmentrecord.data.anonymous) {
            menu.push({
                text: gettext('Import candidate IDs'),
                listeners: {
                    scope: this,
                    click: this.onSetCandidateIdBulk
                }
            });
        }
        return menu;
    },

    _addMenuItemTooltip: function(menuitem, args) {
        Ext.create('Ext.tip.ToolTip', Ext.apply(args, {
            target: menuitem.getEl(),
            showDelay: 50,
            width: 300,
            anchor: 'left',
            dismissDelay: 30000 // Hide after 30 seconds hover
        }));
    },

    statics: {
        getAllGroupsInAssignment: function(assignmentid, action) {
            var model = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup');
            var assignmentGroupStore = Ext.create('Ext.data.Store', {
                model: model,
                remoteFilter: true,
                remoteSort: true
            });

            assignmentGroupStore.proxy.setDevilryFilters([{
                field: 'parentnode',
                comp: 'exact',
                value: assignmentid
            }]);

            assignmentGroupStore.pageSize = 1;
            assignmentGroupStore.load({
                scope: this,
                callback: function(records, op, success) {
                    if(!success) {
                        this.loadAssignmentGroupStoreFailed();
                    }
                    assignmentGroupStore.pageSize = assignmentGroupStore.totalCount;
                    assignmentGroupStore.load({
                        scope: this,
                        callback: function(records, op, success) {
                            Ext.bind(action.callback, action.scope, action.extraArgs, true)(records, op, success);
                        }
                    });
                }
            });
        }
    }
});


Ext.define('devilry.administrator.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-dashboard',

    requires: [
        'devilry.extjshelpers.PermissionChecker',
        'devilry.examiner.ActiveAssignmentsView',
        'devilry.administrator.DashboardButtonBar'
    ],

    /**
     * @cfg
     * 
     */
    dashboardUrl: undefined,
    
    initComponent: function() {
        var searchwidget = Ext.create('devilry.administrator.AdministratorSearchWidget', {
            urlPrefix: this.dashboardUrl
        });

        var buttonbar = Ext.create('devilry.administrator.DashboardButtonBar', {
            is_superuser: DevilryUser.is_superuser
        });

        var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
            model: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignment'),
            dashboard_url: this.dashboardUrl
        });

        var activePeriodsView = Ext.create('devilry.extjshelpers.ActivePeriodsGrid', {
            model: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod'),
            dashboard_url: this.dashboardUrl
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [searchwidget, {xtype:'box', height: 20}, buttonbar, {
                xtype: 'container',
                flex: 1,
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [{
                    xtype: 'panel',
                    flex: 3,
                    layout: 'fit',
                    border: false,
                    items: activePeriodsView
                }, {
                    xtype: 'box',
                    width: 30
                }, {
                    xtype: 'panel',
                    flex: 7,
                    layout: 'fit',
                    border: false,
                    items: activeAssignmentsView
                }]
            }]
        });
        this.callParent(arguments);
    }
});


Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Main', {
    extend: 'Ext.form.Panel',
    title: 'Label students that qualifies for final exams',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin',
        'devilry.statistics.sidebarplugin.qualifiesforexam.None',
        'devilry.statistics.sidebarplugin.qualifiesforexam.All',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnAll',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Advanced',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Manual',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset',
        'devilry.extjshelpers.DateTime'
    ],
    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: 'qualifies-for-exam',
        negative_labelname: 'unqualified-for-exam',
        sidebarplugins: []
    },
    applicationid: 'statistics-qualifiesforexam',

    bodyPadding: 10,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },
    defaults: {
        margin: '0 0 10 0'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.chooseplugin = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin', {
            availablePlugins: [{
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll',
                title: 'Require passing grade on all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset',
                title: 'Require passing grade on a subset of all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnAll',
                title: 'Require a minimum number of points in total on all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset',
                title: 'Require a minimum number of points in total on a subset of all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.None',
                title: 'No students qualify for final exams'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.All',
                title: 'All students qualify for final exams'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.Advanced',
                title: 'Advanced'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.Manual',
                title: 'Manually select the students that qualify for final exams'
            }],
            commonArgs: {
                loader: this.loader,
                aggregatedStore: this.aggregatedStore,
                labelname: this.labelname,
                negative_labelname: this.negative_labelname,
                main: this
            },

            listeners: {
                scope: this,
                pluginSelected: this._pluginSelected,
                render: this._onRenderChoices
            }
        });
        this._main = Ext.widget('container', {
            flex: 1,
            layout: 'fit'
        });
        Ext.apply(this, {
            items: [this.chooseplugin, this._main]
        });
        this.callParent(arguments);
    },

    _onRenderChoices: function() {
        this._loadSettings();
    },

    _pluginSelected: function(pluginObj) {
        this._main.removeAll();
        this.loader.clearFilter();
        this._main.add(pluginObj);
    },


    _loadSettings: function() {
        this._mask('Loading current settings', 'page-load-mask');
        this.periodapplicationkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue',
            remoteFilter: true,
            remoteSort: true
        });
        this.periodapplicationkeyvalue_store.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.loader.periodid
        }, {
            field: 'application',
            comp: 'exact',
            value: this.applicationid
        //}, {
            //field: 'key',
            //comp: 'exact',
            //value: 'settings'
        }]);
        this.periodapplicationkeyvalue_store.proxy.setDevilryOrderby(['-key']);
        this.periodapplicationkeyvalue_store.pageSize = 2; // settings and ready-for-export
        this.periodapplicationkeyvalue_store.load({
            scope: this,
            callback: this._onLoadSettings
        });
    },

    _onLoadSettings: function(records, op) {
        this._unmask();
        if(!op.success) {
            this._handleComError('Save settings', op);
            return;
        }

        var settingsindex = this.periodapplicationkeyvalue_store.findExact('key', 'settings');
        if(settingsindex > -1) {
            this.settingsRecord = records[settingsindex];
            this.settings = Ext.JSON.decode(this.settingsRecord.get('value'));
            this.chooseplugin.selectByPath(this.settings.path);
        } else {
            this.settingsRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
                period: this.loader.periodid,
                application: this.applicationid,
                key: 'settings',
                value: null
            });
        }

        var readyForExportIndex = this.periodapplicationkeyvalue_store.findExact('key', 'ready-for-export');
        if(readyForExportIndex > -1) {
            this.readyForExportRecord = records[readyForExportIndex];
        } else {
            this.readyForExportRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
                period: this.loader.periodid,
                application: this.applicationid,
                key: 'ready-for-export',
                value: null
            });
        }
    },

    saveSettings: function(path, settings, callback, scope) {
        this._mask('Saving current settings', 'page-load-mask');
        var settingData = {
            path: path,
            settings: settings
        };
        this.settingsRecord.set('value', Ext.JSON.encode(settingData));
        this.settingsRecord.save({
            scope: this,
            callback: function(record, op) {
                this._unmask();
                if(!op.success) {
                    this._handleComError('Save settings', op);
                    return;
                }
                this.settings = settingData;
                this._saveReadyForExportRecord(callback, scope);
            }
        });
    },

    _saveReadyForExportRecord: function(callback, scope) {
        this._mask('Marking as ready for export', 'page-load-mask');
        this.readyForExportRecord.set('value', Ext.JSON.encode({
            isready: 'yes',
            savetime: devilry.extjshelpers.DateTime.restfulNow()
        }));
        this.readyForExportRecord.save({
            scope: this,
            callback: function(record, op) {
                this._unmask();
                if(!op.success) {
                    this._handleComError('Mark ready for export', op);
                    return;
                }
                Ext.bind(callback, scope)();
            }
        });
    },

    _handleComError: function(details, op) {
        this._unmask();
        var httperror = 'Lost connection with server';
        if(op.error.status !== 0) {
            httperror = Ext.String.format('{0} {1}', op.error.status, op.error.statusText);
        }
        Ext.MessageBox.show({
            title: 'Error',
            msg: '<p>This is usually caused by an unstable server connection. <strong>Try reloading the page</strong>.</p>' +
                Ext.String.format('<p>Error details: {0}: {1}</p>', httperror, details),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    },

    _mask: function(msg) {
        this.getEl().mask(msg);
    },

    _unmask: function() {
        this.getEl().unmask();
    }
});


Ext.define('devilry.examiner.AssignmentLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-assignmentlayout',
    requires: [
        'devilry.examiner.AssignmentLayoutTodoList',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.SingleRecordView',
        'devilry_extjsextras.Router',
        'devilry_header.Breadcrumbs'
    ],
    cls: 'devilry_subtlebg',

    /**
     * @cfg
     */
    assignmentid: undefined,
    

    assignmentmodelname: 'devilry.apps.examiner.simplified.SimplifiedAssignment',
    assignmentgroupmodelname: 'devilry.apps.examiner.simplified.SimplifiedAssignmentGroup',
    
    constructor: function(config) {
        this.assignment_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.assignment_recordcontainer.on('setRecord', this._onLoadRecord, this);
        this.callParent(arguments);
    },
    
    initComponent: function() {
        this.route = Ext.create('devilry_extjsextras.Router', this);
        this.route.add("", 'todo_route');
        this.route.add("students", 'students_route');

        var assignmentmodel = Ext.ModelManager.getModel(this.assignmentmodelname);
        assignmentmodel.load(this.assignmentid, {
            scope: this,
            success: this._onLoadAssignmentSuccess,
            failure: this._onLoadAssignmentFailure
        });

        this.heading = Ext.widget('singlerecordview', {
            singlerecordontainer: this.assignment_recordcontainer,
            margin: '20 0 0 0',
            tpl: Ext.create('Ext.XTemplate',
                '<div class="section pathheading bootstrap">',
                    '<h1 style="margin: 0; line-height: 25px;"><small>{parentnode__parentnode__short_name}.{parentnode__short_name}.</small>{long_name}</h1>',
                '</div>'
            )
        });
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: []
        });
        this.callParent(arguments);
    },

    _init: function() {
        this.route.start();
    },

    todo_route: function() {
        var todo = this.down('examiner-assignmentlayout-todolist');
        if(todo !== null) { // Will be null for non-electronic
            todo.show();
        }
        this._setBreadcrumbsAndTitle();
    },
    students_route: function() {
        this.down('studentsmanager').show();
        this._setBreadcrumbsAndTitle(true);
    },

    _setBreadcrumbsAndTitle: function(students) {
        var record = this.assignmentRecord;
        var path = [
            record.get('parentnode__parentnode__short_name'),
            record.get('parentnode__short_name'),
            record.get('short_name')].join('.');
        var breadcrumbs = [];
        var active = path;
        if(students) {
            breadcrumbs.push({
                text: path,
                url: '#'
            });
            active = gettext('Students');
        }
        devilry_header.Breadcrumbs.getInBody().set(breadcrumbs, active);
        window.document.title = Ext.String.format('{0} - Devilry', path);
    },

    _onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.assignment_recordcontainer.setRecord(record);
    },

    _onLoadAssignmentFailure: function() {
        Ext.MessageBox.alert("Failed to load assignment. Please try to reload the page.");
    },

    _getStudentsManagerConfig: function() {
        return {
            xtype: 'studentsmanager',
            title: gettext('Detailed overview of all students'),
            assignmentgroupmodelname: this.assignmentgroupmodelname,
            assignmentid: this.assignmentid,
            assignmentrecord: this.assignment_recordcontainer.record,
            deadlinemodel: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDeadline'),
            gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.examiner.SimplifiedConfig'),
            isAdministrator: false,
            listeners: {
                scope: this,
                activate: function() {
                    this.route.navigate('#students');
                }
            }
        };
    },

    _getTodoListConfig: function() {
        return {
            xtype: 'examiner-assignmentlayout-todolist',
            assignmentid: this.assignmentid,
            pageSize: 30,
            assignmentmodelname: this.assignmentmodelname,
            assignmentgroupmodelname: this.assignmentgroupmodelname,
            listeners: {
                scope: this,
                activate: function() {
                    if(this.finishedLoading) {
                        this.route.navigate('');
                    }
                }
            }
        };
    },

    _electronicLayout: function() {
        this.add([this.heading, {
            xtype: 'tabpanel',
            flex: 1,
            items: [this._getTodoListConfig(), this._getStudentsManagerConfig()]
        }]);
    },

    _nonElectronicLayout: function() {
        var studentsmanagerConf = this._getStudentsManagerConfig();
        studentsmanagerConf.flex = 1;
        this.add([this.heading, studentsmanagerConf]);
    },

    _onLoadRecord: function() {
        if(this.assignment_recordcontainer.record.get('delivery_types') === 1) {
            this._nonElectronicLayout();
        } else {
            this._electronicLayout();
        }
        this._init();
        this.finishedLoading = true;
        Ext.getBody().unmask();
    }
});


Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-periodadminlayout', // NOTE: devilry.statistics.sidebarplugin.qualifiesforexam.Manual depends on this alias
    layout: 'fit',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.SidebarPluginContainer',
        'devilry.statistics.dataview.DataView',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main',
        'devilry.statistics.OverviewOfSingleStudent'
    ],

    /**
     * @cfg
     */
    periodid: undefined,

    /**
     * @cfg
     */
    defaultViewClsname: 'devilry.statistics.dataview.FullGridView',

    /**
     * @cfg
     */
    hidesidebar: false,

    sidebarplugins: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
    ],

    titleTpl: Ext.create('Ext.XTemplate',
        '{parentnode__long_name:ellipsis(60)} &mdash; {long_name}'
    ),

    constructor: function() {
        this.callParent(arguments);
    },
    
    initComponent: function() {
        this._isLoaded = false;
        Ext.apply(this, {
            items: [],
            frame: false,
            border: false
        });
        this.on('afterrender', this._onAfterRender, this);
        this.callParent(arguments);
    },

    loadIfNotLoaded: function() {
        if(!this._isLoaded) {
            this._isLoaded = true;
            this._loadStudents();
        }
    },

    _loadStudents: function() {
        Ext.create('devilry.statistics.Loader', this.periodid, {
            listeners: {
                scope: this,
                minimalDatasetLoaded: this._onMinimalDatasetLoaded,
                mask: this._onMask,
                unmask: this._onUnmask
            }
        });
    },

    _onAfterRender: function() {
        Ext.defer(function() {
            this._rendered = true;
            if(this._unappliedMask) {
                this._mask(this._unappliedMask);
                this._unappliedMask = null;
            }
        }, 100, this);
    },
    _onMask: function(loader, msg) {
        if(this._rendered) {
            this._mask(msg);
        } else {
            this._unappliedMask = msg;
        }
    },
    _onUnmask: function() {
        this._unappliedMask = null;
        if(this._rendered) {
            this._unmask();
        }
    },
    _mask: function(msg) {
        this.getEl().mask(msg);
    },
    _unmask: function() {
        this.getEl().unmask();
    },

    _onMinimalDatasetLoaded: function(loader) {
        var title = this.titleTpl.apply(loader.periodRecord.data);
        this.removeAll();
        this.add({
            xtype: 'panel',
            border: false,
            frame: false,
            layout: 'border',
            items: [{
                xtype: 'statistics-sidebarplugincontainer',
                title: 'Label students',
                region: 'east',
                collapsible: true,
                collapsed: this.hidesidebar,
                width: 350,
                autoScroll: true,
                loader: loader,
                sidebarplugins: this.sidebarplugins
            }, this._dataview = Ext.widget('statistics-dataview', {
                defaultViewClsname: this.defaultViewClsname,
                region: 'center',
                loader: loader
            })]
        });
    }
});


/** PrettyView for an assignment. */
Ext.define('devilry.administrator.assignment.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_assignmentprettyview',
    requires: [
        'devilry.administrator.studentsmanager.StudentsManager',
        'devilry.extjshelpers.AutoSizedWindow',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.MaximizableWindow',
        'devilry.gradeeditors.GradeEditorModel',
        'devilry.gradeeditors.RestfulRegistryItem',
        'devilry.gradeeditors.ConfigEditorWidget',
        'devilry.gradeeditors.GradeEditorSelectForm',
        'devilry.extjshelpers.NotificationManager'
    ],

    /**
     * @cfg
     * The name of the assignment group ``Ext.data.Model`` to use in the store
     * (Required).  The store copies the proxy from this model.
     */
    assignmentgroupmodelname: undefined,

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section">',
            '<tpl if="totalAssignmentGroups == 0">',
                '<div class="section error">',
                    '<h1>No students</h1>',
                    '<p>',
                        'Students have to be added to the assignment before they can add any deliveries. Please choose the <span class="menuref">Students</span> tab and select <span class="menuref">Add students</span>.',
                    '</p>',
                '</div>',
            '</tpl>',
            '<tpl if="missingGradeEditorConfig">',
                '<div class="section error">',
                    '<h1>Missing grade editor config</h1>',
                    '<p>',
                    '    The selected grade editor, <em>{graderegistryitem.data.title}</em>, requires',
                    '    configuration. Examiners will not be able to give feedback ',
                    '    without a configuration, however students will be able to add deliveries.',
                    '    Choose <span class="menuref">Grade editor &rarr; Configure current grade editor</span> in the toolbar to create a configuration.',
                    '</p>',
                '</div>',
            '</tpl>',
            '<tpl if="graderegistryitem">',
            '    <div class="section info">',
            '        <h1>Grade editor: {graderegistryitem.data.title}</h1>',
            '        <h2>About the grade editor:</strong></h2>',
            '        <p>',
            '            {graderegistryitem.data.description}',
            '        </p>',
            '        <h2>Why grade editors?</h2>',
            '        <p>',
                        'To make it easy for examiners to create all the information related to a grade, Devilry use <em>grade editors</em>. Grade editors give examiners a unified user-interface tailored for different kinds of grading systems. Select <span class="menuref">Grade editor</span> in the toolbar to change or configure the grade editor.',
            '        </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="deadline_handling==1">',
            '    <div class="section info">',
            '        <h1>HARD deadlines</h1>',
            '        <p>',
            '           The assignment is configured to use HARD deadlines. This means that students will be unable to make deliveries when a deadline has expired.',
            '           Unless you have problems with students not understanding the consequences of delivering after the deadline without a valid reason, SOFT deadlines usually means less administrative overhead, since students can just add deliveries, and examiners can clearly see, and ignore deliveries made after the deadline without a valid reason.',
            '            Select <span class="menuref">Edit</span> in the toolbar to change how deadlines are handled.',
            '        </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="deadline_handling==0">',
            '    <div class="section info">',
            '        <h1>Soft deadlines</h1>',
            '        <p>',
            '           The assignment is configured to use SOFT deadlines. This means that students will be able to make deliveries after the deadline has expired. All deliveries after their deadline are clearly highligted.',
            '            Select <span class="menuref">Edit</span> in the toolbar to change how deadlines are handled.',
            '        </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="published">',
            '    <div class="section info">',
            '        <h1>Published</h1>',
            '        <p>',
            '           The assignment is currently visible to students and examiners. ',
            '           Its publishing time was <strong>{publishing_time:date}</strong>.',
            '           You may change the publishing time by selecting the <span class="menuref">Edit</span> button ',
            '           in the toolbar, however since it is already published, this may lead ',
            '           to confusion among students and examiners.',
            '        </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="!published">',
            '    <div class="section warning">',
            '         <h1>Not published</h1>',
            '         <p>',
            '            This assignment is currently <em>not visible</em> to students or examiners. ',
            '            The assignment will become visible to students and examiners ',
            '            <strong>{publishing_time:date}</strong>.',
            '            You may change the publishing time by selecting the <span class="menuref">Edit</span> button in the toolbar.',
            '         </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="anonymous">',
            '    <div class="section info">',
            '        <h1>Anonymous</h1>',
            '        <p>',
            '            The assignment <em>is anonymous</em>. This means that examiners ',
            '            see the <em>candidate ID</em> instead of user name and ',
            '            email. Furthermore, students do not see who their examiner(s)',
            '            are. ',
            '            Select <span class="menuref">Edit</span> ',
            '            in the toolbar to change this setting.',
            '        </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="!anonymous">',
            '    <div class="section info">',
            '        <h1>Not anonymous</h1>',
            '        <p>',
            '            The assignment is <em>not</em> anonymous. This means that examiners ',
            '            can see information about who their students are. ',
            '            Furthermore, students can see who their examiner(s)',
            '            are. This is usually OK, however on exams this is usually ',
            '            not the recommended setting. ',
            '            Select <span class="menuref">Edit</span> ',
            '            in the toolbar to change this setting.',
            '        </p>',
            '    </div>',
            '</tpl>',
            '<tpl if="delivery_types == 1">',
            '    <div class="section info">',
            '        <h1>Non-electronic deliveries</h1>',
            '        <p>',
            '           This assignment does not use Devilry for deliveries, only for feedback.',
            '           You may choose to use Devilry for electronic deliveries on this assignment using the <span class="menuref">Edit</span> button in the toolbar.',
            '        </p>',
            '    </div>',
            '</tpl>',
        '</div>'
    ),

    getExtraBodyData: function(record) {
        return {
            published: record.data.publishing_time < Ext.Date.now(),
            missingGradeEditorConfig: this.missingGradeEditorConfig,
            graderegistryitem: this.gradeeditor_registryitem_recordcontainer.record,
            totalAssignmentGroups: this.assignmentgroupstore.totalCount
        };
    },

    initComponent: function() {
        this._createAssignmentgroupStore();
        this.gradeeditorconfig_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditorconfig_recordcontainer.addListener('setRecord', this.onGradeEditorConfigLoad, this);

        this.gradeeditor_registryitem_recordcontainer= Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditor_registryitem_recordcontainer.addListener('setRecord', this.onGradeEditorRegistryItemLoad, this);

        if(this.record) {
            this.onLoadRecord();
        } else {
            this.addListener('loadmodel', this.onLoadRecord, this);
        }

        this.selectgradeeditorbutton = Ext.widget('menuitem', {
            text: 'Change grade editor',
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onSelectGradeEditorBtn,
                render: function(button) {
                    if(!this.gradeeditorconfig_recordcontainer.record) {
                        button.getEl().mask('Loading');
                    }
                }
            }
        });

        this.configuregradeeditorbutton = Ext.widget('menuitem', {
            text: 'Configure current grade editor',
            scale: 'large',
            disabled: true,
            listeners: {
                scope: this,
                click: this.onConfigureGradeEditorBtn,
                render: function(button) {
                    if(!this.gradeeditorconfig_recordcontainer.record) {
                        button.getEl().mask('Loading');
                    }
                }
            }
        });

        this.gradeeditormenu = Ext.widget('button', {
            text: 'Grade editor',
            scale: 'large',
            menu: [
                this.selectgradeeditorbutton,
                this.configuregradeeditorbutton
            ]
        });

        Ext.apply(this, {
            extraMeButtons: [this.gradeeditormenu],
        });
        this.callParent(arguments);
    },

    onLoadRecord: function() {
        this.checkStudentsAndRefreshBody();
        Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig').load(this.record.data.id, {
            scope: this,
            success: function(record) {
                this.gradeeditorconfig_recordcontainer.setRecord(record);
            },
            failure: function() {
                var record = Ext.create('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig', {
                    assignment: this.record.data.id
                });
                this.gradeeditorconfig_recordcontainer.setRecord(record);
            }
        });
    },

    checkStudentsAndRefreshBody: function() {
        // Load a single records to get totalCount
        this.assignmentgroupstore.pageSize = 1;
        this.assignmentgroupstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.objectid
        }]);
        this.assignmentgroupstore.load({
            scope: this,
            callback: function(records, operation, success) {
                if(success) {
                    this.refreshBody();
                }
            }
        });
    },

    _createAssignmentgroupStore: function() {
        var model = Ext.ModelManager.getModel(this.assignmentgroupmodelname);
        this.assignmentgroupstore = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
    },

    onGradeEditorConfigLoad: function() {
        if(this.selectgradeeditorbutton.rendered) {
            this.selectgradeeditorbutton.getEl().unmask();
        }
        this.loadGradeEditorRegistryItem();
    },

    loadGradeEditorRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        if(this.gradeeditormenu.isVisible()) {
            this.gradeeditormenu.getEl().mask('Loading');
        }
        registryitem_model.load(this.gradeeditorconfig_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(record) {
                this.gradeeditor_registryitem_recordcontainer.setRecord(record);
            }
        });
    },

    onGradeEditorRegistryItemLoad: function() {
        var config = this.gradeeditorconfig_recordcontainer.record.data;
        var registryitem = this.gradeeditor_registryitem_recordcontainer.record.data;
        this.missingGradeEditorConfig = config.config === "" && registryitem.config_editor_url != "";
        this.refreshBody();
        if(this.gradeeditormenu.isVisible()) {
            this.gradeeditormenu.getEl().unmask();
        }
        if(this.gradeeditor_registryitem_recordcontainer.record.data.config_editor_url) {
            this.configuregradeeditorbutton.enable();
        } else {
            this.configuregradeeditorbutton.disable();
        }
    },

    onSelectGradeEditorBtn: function(button) {
        var currentGradeEditorId = this.gradeeditorconfig_recordcontainer.record.data.gradeeditorid
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: 'devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig',
            editform: Ext.widget('gradeeditorselectform'),
            record: this.gradeeditorconfig_recordcontainer.record,
            extrabaronbottom: true,
            beforeSave: function() {
                var config = this.record.data.config;
                if(this.down('gradeeditorselector').getValue() == currentGradeEditorId) {
                    // Clicked save without changing grade editor
                    this.up('window').close();
                    return;
                }
                if(config == null || config == '') {
                    // Do not warn when config will not be lost
                    this.doSave();
                } else {
                    Ext.MessageBox.show({
                        title: 'Confirm grade editor change',
                        msg: 'This will <strong>permanently</strong> remove your current configuration for the grade editor.',
                        buttons: Ext.Msg.YESNO,
                        icon: Ext.Msg.WARNING,
                        scope: this,
                        fn: function(btn) {
                            if(btn == 'yes') {
                                this.record.data.config = '';
                                this.doSave();
                            } else {
                                this.up('window').close();
                            }
                        }
                    });
                }
            }
        });
        var me = this;
        var editwindow = Ext.create('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
            editpanel: editpanel,
            onSaveSuccess: function(record) {
                me.gradeeditorconfig_recordcontainer.setRecord(record);
                window.location.href = window.location.href; // TODO: Make so this hack is not needed.
                this.close();
            }
        });
        editwindow.show();
    },

    onConfigureGradeEditorBtn: function(button) {
        Ext.widget('devilry_autosizedwindow', {
            width: 2000, // NOTE: this is autosized to fit the viewport.
            height: 1200,
            title: 'Edit grade editor config',
            layout: 'fit',
            modal: true,
            items: {
                itemId: 'gradeconfigeditorContainer',
                autoScroll: true,
                xtype: 'panel',
                border: false,
                items: [{
                    xtype: 'gradeconfigeditor',
                    helpCls: 'section',
                    registryitem: this.gradeeditor_registryitem_recordcontainer.record.data,
                    gradeEditorConfigRecord: this.gradeeditorconfig_recordcontainer.record,
                    listeners: {
                        scope: this,
                        saveSuccess: function(gradeconfigeditor, configrecord) {
                            this.gradeeditorconfig_recordcontainer.setRecord(configrecord);
                            window.location.reload();
                        }
                    }
                }],
                dockedItems: [{
                    dock: 'bottom',
                    xtype: 'toolbar',
                    ui: 'footer',
                    items: ['->', {
                        xtype: 'button',
                        text: 'Save',
                        scale: 'large',
                        iconCls: 'icon-save-32',
                        listeners: {
                            scope: this,
                            click: function(button) {
                                var win = button.up('#gradeconfigeditorContainer');
                                var gradeconfigeditor = win.down('gradeconfigeditor');
                                gradeconfigeditor.triggerSave();
                            }
                        }
                    }]
                }]
            }
        }).show();
    },

    onEdit: function(button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.modelname,
            editform: Ext.widget('administrator_assignmentform'),
            record: this.record,
            saveSuccessMessage: 'Assignment successfully saved'
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this,
            listeners: {
                scope: this,
                close: function() {
                    window.location.href = window.location.href; // NOTE: Required because some stuff in studentmanager check delivery_types, and we do not check for changes
                }
            }
        });
        editwindow.show();
    }
});


Ext.define('devilry.administrator.assignment.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-assignmentlayout',

    requires: [
        'devilry.administrator.assignment.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Assignment',
        'devilry_header.Breadcrumbs',
        'devilry_extjsextras.Router',
        'devilry_header.Breadcrumbs'
    ],

    /**
     * @cfg
     */
    assignmentid: undefined,

    /**
     * @cfg
     */
    dashboardUrl: undefined,

    assignmentmodel_name: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
    assignmentgroupmodelname: 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup',
    
    initComponent: function() {
        this.studentsLoaded = false;
        this.route = Ext.create('devilry_extjsextras.Router', this);
        this.route.add("", 'administer_route');
        this.route.add("students", 'students_route');
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {hasdata: false},
                cls: 'section pathheading',
                tpl: [
                    '<tpl if="!hasdata">',
                    '   <span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                    '    <h1><small>{assignment.parentnode__parentnode__short_name}.{assignment.parentnode__short_name}.</small>{assignment.long_name}</h1>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                activeTab: window.location.hash == '#students'? 1: 0,
                items: [this.prettyview = Ext.widget('administrator_assignmentprettyview', {
                    title: gettext('Administer'),
                    itemId: 'administer',
                    modelname: this.assignmentmodel_name,
                    objectid: this.assignmentid,
                    dashboardUrl: this.dashboardUrl,
                    assignmentgroupmodelname: this.assignmentgroupmodelname,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        loadmodelFailed: this._onLoadRecordFailed,
                        edit: this._onEdit,
                        activate: function() {
                            this.route.navigate('');
                            if(this.prettyview.record) {
                                this.prettyview.checkStudentsAndRefreshBody();
                            }
                        }
                    }
                }), this.studentstab = Ext.widget('panel', {
                    title: gettext('Students'),
                    itemId: 'students',
                    layout: 'fit',
                    listeners: {
                        scope: this,
                        activate: function() {
                            this.route.navigate('students');
                        }
                    }
                })]
            }]
        });
        this.callParent(arguments);
    },

    _starteRouting: function() {
        if(!this.route_started) {
            this.route_started = true;
            this.route.start();
        }
    },

    administer_route: function() {
        this.down('#administer').show();
        this._setBreadcrumbAndTitle();
    },
    students_route: function() {
        this.down('#students').show();
        this._setBreadcrumbAndTitle(true);
    },

    _onLoadRecord: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.heading.update({
            hasdata: true,
            assignment: assignmentRecord.data,
            DEVILRY_URLPATH_PREFIX: DevilrySettings.DEVILRY_URLPATH_PREFIX
        });
        this._onStudents();
        this._starteRouting();
    },

    _onLoadRecordFailed: function(operation) {
        this.removeAll();
        var title = operation.error.statusText;
        if(operation.error.status == '403') {
            title = gettext('Permission denied');
            message = gettext('You are not administrator on this item or any of its parents.');
        }
        this.add({
            xtype: 'box',
            padding: 20,
            tpl: [
                '<div class="section warning">',
                    '<h2>{title}</h2>',
                    '<p>{message}</p>',
                '</div>'
            ],
            data: {
                title: title,
                message: message
            }
        });
    },

    _setBreadcrumbAndTitle: function(students) {
        var assignmentRecord = this.assignmentRecord;
        var path = [
            assignmentRecord.get('parentnode__parentnode__short_name'),
            assignmentRecord.get('parentnode__short_name'),
            assignmentRecord.get('short_name')].join('.');
        window.document.title = Ext.String.format('{0} - Devilry', path);
        var breadcrumbs = [{
            text: assignmentRecord.get('parentnode__parentnode__short_name'),
            url: '../subject/' + assignmentRecord.get('parentnode__parentnode')
        }, {
            text: assignmentRecord.get('parentnode__short_name'),
            url: '../period/' + assignmentRecord.get('parentnode')
        }];
        var active = assignmentRecord.get('short_name');
        if(students) {
            breadcrumbs.push({
                text: assignmentRecord.get('short_name'),
                url: '#'
            });
            active = gettext('Students')
        }
        devilry_header.Breadcrumbs.getInBody().set(breadcrumbs, active);
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.periodmodel_name,
            editform: Ext.widget('administrator_periodform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    },


    _onStudents: function() {
        if(this.studentsLoaded) {
            return;
        }
        this.studentsLoaded = true;
        this.studentstab.add({
            xtype: 'administrator_studentsmanager',
            assignmentid: this.assignmentid,
            assignmentrecord: this.assignmentRecord,
            periodid: this.assignmentRecord.data.parentnode,
            deadlinemodel: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedDeadline'),
            gradeeditor_config_model: Ext.ModelManager.getModel('devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig'),
            assignmentgroupmodelname: this.assignmentgroupmodelname,
            isAdministrator: true
        });
    }
});


/** PrettyView for an period. */
Ext.define('devilry.administrator.period.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_periodprettyview',
    requires: [
        'devilry.statistics.PeriodAdminLayout'
    ],

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section">',
        '   <tpl if="is_old">',
        '       <div class="section warning">',
        '           <h1>Expired period</h1>',
        '           <p>',
        '               This period was active from <strong>{start_time:date}</strong> to ',
        '               <strong>{end_time:date}</strong>. Examiners do not have ',
        '               access to any data related to the period, including the ',
        '               feedback they have given to students. ',
        '               Students can still view all their deliveries and feedback.',
        '           </p>',
        '       </div>',
        '   </tpl>',
        '   <tpl if="starttime_in_future">',
        '       <div class="section warning">',
        '           <h1>In the future</h1>',
        '           <p>',
        '               This period has not yet started. Students and examiners ',
        '               can not access the period until its <strong>start time</strong>, which is ',
        '               <strong>{start_time:date}</strong>',
        '           </p>',
        '       </div>',
        '   </tpl>',
        '   <tpl if="is_active">',
        '       <div class="section ok">',
        '           <h1>Active</h1>',
        '           <p>',
        '               This period is currently active. It started <strong>{start_time:date}</strong> ',
        '               and it expires <strong>{end_time:date}</strong>. When the period expires, examiners ',
        '               will not have access to any data related to the period, including the ',
        '               feedback they have given to students.',
        '           </p>',
        '       </div>',
        '   </tpl>',
        '</div>'
    ),

    getExtraBodyData: function(record) {
        var is_old = record.data.end_time < Ext.Date.now();
        var starttime_in_future = record.data.start_time > Ext.Date.now();
        return {
            is_old: is_old,
            starttime_in_future: starttime_in_future,
            is_active: (!is_old && !starttime_in_future),
        };
    },

    initComponent: function() {
        //Ext.apply(this, {
            //relatedButtons: [{
                //xtype: 'splitbutton',
                //scale: 'large',
                //text: 'Overview of all students',
                //listeners: {
                    //scope: this,
                    //click: function() {
                        //this._onPeriodOverview(false, false);
                    //}
                //},
                //menu: [{
                    //text: 'Open in minimal view mode',
                    //listeners: {
                        //scope: this,
                        //click: function() {
                            //this._onPeriodOverview(true, true);
                        //}
                    //}
                //}]
            //}]
        //});
        this.callParent(arguments);
        if(this.record) {
            this._onLoadRecord();
        } else {
            this.addListener('loadmodel', this._onLoadRecord, this);
        }
    },

    _onLoadRecord: function() {
    }
});


Ext.define('devilry.administrator.period.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-periodlayout',

    requires: [
        'devilry.administrator.period.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Period',
        'devilry.statistics.PeriodAdminLayout',
        'devilry.administrator.ListOfChildnodes',
        'devilry_header.Breadcrumbs'
    ],

    mainHelpTpl: Ext.create('Ext.XTemplate',
        '<div class="helpsection">',
        '<p>On the left hand side all assignments within this period/semester are listed. Click an assignment to manage the assignment.</p>',
        '<p>In the <span class="menuref">Students</span> tab you can view an overview of all students, and select the criteria that must be met to qualify for final examinations.</p>',
        '<p>Use the <span class="menuref">Administer</span> tab to change the properties of this period/semester, such as administrators and its timespan.</p>',
        '</div>'
    ),
    
    /**
     * @cfg
     */
    periodid: undefined,

    periodmodel_name: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
    
    initComponent: function() {
        var query = Ext.Object.fromQueryString(window.location.search);
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {},
                cls: 'section pathheading',
                tpl: [
                    '<tpl if="!hasdata">',
                    '   <span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                    '    <h1><small>{period.parentnode__short_name}.</small>{period.long_name}</h1>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                activeTab: query.open_students == 'yes'? 1: 0,
                items: [
                {
                    xtype: 'panel',
                    title: 'Assignments',
                    layout: {
                        type: 'hbox',
                        align: 'stretch'
                    },
                    items: [{
                        xtype: 'administrator-listofchildnodes',
                        parentnodeid: this.periodid,
                        orderby: 'publishing_time',
                        modelname: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
                        urlrolepart: 'assignment',
                        readable_type: 'assignment',
                        flex: 7,
                        frame: false,
                        border: false
                    }, {
                        xtype: 'box',
                        flex: 3,
                        html: this.mainHelpTpl.apply({}),
                        autoScroll: true
                    }]
                }, {
                    title: 'Students',
                    xtype: 'statistics-periodadminlayout',
                    periodid: this.periodid,
                    hidesidebar: query.students_hidesidebar == 'yes',
                    defaultViewClsname: 'devilry.statistics.dataview.MinimalGridView',
                    listeners: {
                        activate: function(tab) {
                            tab.loadIfNotLoaded();
                            tab.doLayout();
                        }
                    }
                    //defaultViewClsname: 'devilry.statistics.dataview.FullGridView'
                }, this.prettyview = Ext.widget('administrator_periodprettyview', {
                    title: 'Administer',
                    modelname: this.periodmodel_name,
                    objectid: this.periodid,
                    dashboardUrl: DASHBOARD_URL,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        loadmodelFailed: this._onLoadRecordFailed,
                        edit: this._onEdit
                    }
                })]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(record) {
        this.heading.update({
            hasdata: true,
            period: record.data,
            DEVILRY_URLPATH_PREFIX: DevilrySettings.DEVILRY_URLPATH_PREFIX
        });
        this._setBreadcrumbAndTitle(record);
    },

    _onLoadRecordFailed: function(operation) {
        this.removeAll();
        var title = operation.error.statusText;
        if(operation.error.status == '403') {
            title = gettext('Permission denied');
            message = gettext('You are not administrator on this item or any of its parents.');
        }
        this.add({
            xtype: 'box',
            padding: 20,
            tpl: [
                '<div class="section warning">',
                    '<h2>{title}</h2>',
                    '<p>{message}</p>',
                '</div>'
            ],
            data: {
                title: title,
                message: message
            }
        });
    },

    _setBreadcrumbAndTitle: function(periodRecord) {
        var path = [
            periodRecord.get('parentnode__short_name'),
            periodRecord.get('short_name')].join('.');
        window.document.title = Ext.String.format('{0} - Devilry', path);

        devilry_header.Breadcrumbs.getInBody().set([{
            text: periodRecord.get('parentnode__short_name'),
            url: '../subject/' + periodRecord.get('parentnode')
        }], periodRecord.get('short_name'));
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.periodmodel_name,
            editform: Ext.widget('administrator_periodform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    }
});
