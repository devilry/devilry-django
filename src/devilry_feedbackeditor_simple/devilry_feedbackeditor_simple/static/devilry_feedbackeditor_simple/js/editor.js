(function() {
  var Editor;

  Editor = (function() {
    function Editor($textarea) {
      this.$textarea = $textarea;
    }

    return Editor;

  })();

  ({
    get_raw_text: function() {
      return this.$textarea.val();
    },
    _get_escaped_raw_text: function() {
      var div;
      div = document.createElement('div');
      div.appendChild(document.createTextNode(this.get_raw_text()));
      return div.innerHTML;
    },
    get_rendered_view: function() {
      return "<div style='white-space: pre-wrap'>" + (this._get_escaped_raw_text()) + "</div>";
    }
  });

  window.devilry_feedbackeditor_simple = {
    Editor: Editor
  };

}).call(this);
