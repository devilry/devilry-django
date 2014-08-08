/** Groups on an assignment. */
Ext.define('devilry_subjectadmin.store.GroupByExaminerGrouper', {
    extend: 'Ext.util.Grouper',

    property: 'is_open',
    root: 'data',

    //transform: function(examiners) {
        //var examinersString = '';
        //for(var index=0; index<examiners.length; index++)  {
            //var examiner = examiners[index];
            //examinersString += examiner.user.full_name;
            //if(index < examiner.length-1) {
                //examinersString += ', ';
            //}
        //}
        //return examinersString;
    //},

    //getExaminersString: function(examiners) {
        //var examinersString = '';
        //for(var index=0; index<examiners.length; index++)  {
            //var examiner = examiners[index];
            //examinersString += examiner.user.full_name;
            //if(index < examiner.length-1) {
                //examinersString += ', ';
            //}
        //}
        //return examinersString;
    //},
    //sorterFn: function(a, b) {
        //var examinersA = this.getExaminersString(a.get('examiners'));
        //var examinersB = this.getExaminersString(b.get('examiners'));
        ////console.log(examinersA, examinersB);
        //return examinersA.localeCompare(examinersB);
    //},

    getGroupString: function() {
        console.log('YO'); // TF?
        return 'examiners';
    }
});
