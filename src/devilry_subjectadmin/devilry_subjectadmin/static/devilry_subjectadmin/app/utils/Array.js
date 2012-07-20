Ext.define('devilry_subjectadmin.utils.Array', {
    singleton: true,

    _findMatchingItem: function(destItem, sourceArray, isEqual) {
        for(var sourceIndex=0; sourceIndex<sourceArray.length; sourceIndex++)  {
            var sourceItem = sourceArray[sourceIndex];
            if(isEqual(destItem, sourceItem)) {
                return {
                    sourceItem: sourceItem,
                    sourceIndex: sourceIndex
                };
            }
        }
        return null;
    },

    /**
     * Helper to merge items from one array into another array. The intended is
     * when we have a ``sourceArray`` of items that the user wants to add or
     * update in ``destArray``. The items in sourceArray an destArray may not be of the same type, so the caller defines:
     *  - how they match
     *  - what to do when they match
     *  - what to do with the items that was not in ``destinationArray``
     *
     * @param {Object} [config] Configuration for the method.
     * @param {[Object]} [config.destinationArray] The destination array.
     * @param {[Object]} [config.sourceArray] The source array.
     * @param {Object} [scope] The scope to execute the functions in.
     * @param {Function} [config.isEqual]
     *      Takes ``destItem`` and ``sourceItem`` as parameters, and returns
     *      ``true`` if they match.
     * @param {Function} [config.onMatch]
     *      Called when isEqual returns ``true``, with ``destItem`` and
     *      ``sourceItem`` as parameters.
     * @param {Function} [config.onNoMatch]
     *      Called when isEqual returns ``false``, with ``destItem`` and
     *      ``sourceItem`` as parameters.
     * @param {Function} [config.onAdd]
     *      Called for all items in ``sourceArray`` that is not in
     *      ``destinationArray``, with ``sourceItems`` as parameter.
     */
    mergeIntoArray: function(config) {
        var matchedSourceItems = {}; // Filled with sourceItems already in destinationArray, indexed by their index in sourceArray.
        for(var destIndex=0; destIndex<config.destinationArray.length; destIndex++)  {
            var destItem = config.destinationArray[destIndex];
            var match = this._findMatchingItem(destItem, config.sourceArray, config.isEqual);
            if(match) {
                Ext.callback(config.onMatch, config.scope, [destItem, destIndex, match.sourceItem]);
                matchedSourceItems[match.sourceIndex] = true;
            } else {
                Ext.callback(config.onNoMatch, config.scope, [destItem, destIndex]);
            }
        }
        for(var sourceIndex=0; sourceIndex<config.sourceArray.length; sourceIndex++)  {
            // NOTE: We only add sourceItems not already matched
            if(!matchedSourceItems[sourceIndex]) {
                var sourceItem = config.sourceArray[sourceIndex];
                config.onAdd(sourceItem);
            }
        }
    }
});
