Ext.require(["Ext.util.Cookies", "Ext.Ajax"], function(){
    // Add csrf token to every ajax request
    var token = Ext.util.Cookies.get('csrftoken');
    if(!token){
        Ext.Error.raise("Missing csrftoken cookie");
    } else {
        Ext.Ajax.defaultHeaders = Ext.apply(Ext.Ajax.defaultHeaders || {}, {
            'X-CSRFToken': token
        });
    }
});
