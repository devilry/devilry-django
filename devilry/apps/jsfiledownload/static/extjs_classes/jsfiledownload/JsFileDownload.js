Ext.define('devilry.jsfiledownload.JsFileDownload', {
    singleton: true,
    url: Ext.String.format('{0}/jsfiledownload/', DevilrySettings.DEVILRY_URLPATH_PREFIX),

    open: function(content_type, content) {
        this._post_to_url(this.url + 'open', {
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
        this._post_to_url(this.url + 'saveas', args);
    },

    _post_to_url: function(path, params) { // See: http://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
        var form = document.createElement("form");
        form.setAttribute("method", 'post');
        form.setAttribute("action", path);

        for(var key in params) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
        }

        //document.body.appendChild(form); // Needed for IE? we do not care about IE6..
        form.submit();
    }
});
