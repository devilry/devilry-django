/* Since ExtJS for some reason goes into panic mode for any HTTP status
 * code except 200 (and ignores the response text), we need to override
 * setException in the REST proxy and manually decode the responseText.
 * (http://www.sencha.com/forum/showthread.php?135143-RESTful-Model-How-to-indicate-that-the-PUT-operation-failed&highlight=store+failure)
 *
 * However how do we get this into the form when we do not have any link to the form?
 *      - We add the response and the the decoded responsedata to the
 *        operation object, which is available to onFailure in Submit.
 * */
Ext.override(Ext.data.proxy.Rest, {
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
    }
})
