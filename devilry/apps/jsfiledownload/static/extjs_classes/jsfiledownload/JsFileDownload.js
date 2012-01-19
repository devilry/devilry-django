Ext.define('devilry.jsfiledownload.JsFileDownload', {
    singleton: true,
    baseurl: Ext.String.format('{0}/jsfiledownload/', DevilrySettings.DEVILRY_URLPATH_PREFIX),

    getOpenUrl: function() {
        return this.baseurl + 'open';
    },

    getSaveAsUrl: function() {
        return this.baseurl + 'saveas';
    },

    open: function(content_type, content) {
        this._post_to_url(this.getOpenUrl(), {
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
        this._post_to_url(this.getSaveAsUrl(), args);
    },

    _post_to_url: function(path, params) { // See: http://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
        var form = document.createElement("form");
        form.setAttribute("method", 'post');
        form.setAttribute("style", 'display: none');
        form.setAttribute("action", path);

        for(var key in params) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
        }

        document.body.appendChild(form);
        form.submit();
    }
});
