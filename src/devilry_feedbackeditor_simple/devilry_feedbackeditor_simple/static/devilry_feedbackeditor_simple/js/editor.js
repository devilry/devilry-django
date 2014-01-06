(function() {
  var Editor;

  Editor = (function() {
    function Editor($textarea) {
      this.$textarea = $textarea;
    }

    Editor.prototype.get_raw_text = function() {
      return this.$textarea.val();
    };

    Editor.prototype._get_escaped_raw_text = function() {
      var div;
      div = document.createElement('div');
      div.appendChild(document.createTextNode(this.get_raw_text()));
      return div.innerHTML;
    };

    Editor.prototype.get_html = function() {
      return "<div style='white-space: pre-wrap'>" + (this._get_escaped_raw_text()) + "</div>";
    };

    return Editor;

  })();

  window.devilry_feedbackeditor_simple = {
    Editor: Editor
  };

}).call(this);
