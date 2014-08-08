(function() {
  var EditFeedback,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  EditFeedback = (function() {
    /*
    */

    function EditFeedback(unique_name) {
      this._onClickPreview = __bind(this._onClickPreview, this);
      this._onClickPublishWithoutPreview = __bind(this._onClickPublishWithoutPreview, this);
      var $footer;
      this.editor_api = window[unique_name];
      $footer = $("#wrapper-footer-" + unique_name);
      $footer.find('.btn.publish-feedback-without-preview').click(this._onClickPublishWithoutPreview);
      $footer.find('.btn.preview-feedback').click(this._onClickPreview);
    }

    EditFeedback.prototype._onClickPublishWithoutPreview = function(e) {
      e.preventDefault();
      return console.log('_onClickPublishWithoutPreview');
    };

    EditFeedback.prototype._onClickPreview = function(e) {
      var html, raw_text;
      e.preventDefault();
      console.log('_onClickPreview');
      raw_text = this.editor_api.get_raw_text();
      html = this.editor_api.get_html();
      return console.log(html, raw_text);
    };

    return EditFeedback;

  })();

  window.devilry_examiner_edit_feedback = {
    EditFeedback: EditFeedback
  };

}).call(this);
