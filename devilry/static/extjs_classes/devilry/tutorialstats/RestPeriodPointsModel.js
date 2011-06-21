Ext.define('devilry.tutorialstats.RestPeriodPointsModel', {
    extend: 'Ext.data.Model',
    fields: [
        {"type": "string", "name": "username"},
        {"type": "int", "name": "sumperiod"}
    ],
    idProperty: 'username'
});
