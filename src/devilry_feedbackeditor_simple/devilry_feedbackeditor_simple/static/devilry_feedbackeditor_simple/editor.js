(function() {
  var Editor;

  Editor = (function() {
    function Editor($textarea) {
      this.$textarea = $textarea;
      console.log('Init');
    }

    Editor.prototype.get_raw_text = function() {};

    return Editor;

  })();

  window.devilry_feedbackeditor_simple = {
    Editor: Editor
  };

}).call(this);
