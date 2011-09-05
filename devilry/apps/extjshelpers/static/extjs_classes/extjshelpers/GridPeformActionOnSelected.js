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
