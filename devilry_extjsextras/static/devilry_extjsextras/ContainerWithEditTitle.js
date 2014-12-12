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
