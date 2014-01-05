(function() {
  var EditFeedback;

  EditFeedback = (function() {
    function EditFeedback(js_editor_api_name) {
      this.js_editor_api_name = js_editor_api_name;
    }

    return EditFeedback;

  })();

  window.devilry_examiner_edit_feedback = {
    EditFeedback: EditFeedback
  };

}).call(this);
