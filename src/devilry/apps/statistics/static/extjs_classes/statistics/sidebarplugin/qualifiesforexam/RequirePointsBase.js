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
