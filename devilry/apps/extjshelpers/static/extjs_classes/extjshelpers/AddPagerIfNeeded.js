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
