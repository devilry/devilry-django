(function() {
  var EditMarkdownWidget,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  EditMarkdownWidget = (function() {
    function EditMarkdownWidget(options) {
      this._onInsertUrl = __bind(this._onInsertUrl, this);
      this._onChange = __bind(this._onChange, this);
      var aceboxid;
      this.id = options.id, this.translations = options.translations;
      this.$wrapper = this.$textarea = $("#" + this.id + "_wrapper");
      this.$textarea = $("#" + this.id);
      aceboxid = "" + this.id + "_aceeditor";
      this.editor = ace.edit(aceboxid);
      this._configure();
      this._setupToolbar();
      this._setInitialValues();
      this.editor.on('change', this._onChange);
    }

    EditMarkdownWidget.prototype._setInitialValues = function() {
      var markdownString;
      markdownString = this.$textarea.val();
      return this.editor.getSession().setValue(markdownString);
    };

    EditMarkdownWidget.prototype._configure = function() {
      var session;
      this.editor.setTheme('ace/theme/tomorrow');
      this.editor.setHighlightActiveLine(false);
      this.editor.setShowPrintMargin(false);
      this.editor.renderer.setShowGutter(false);
      session = this.editor.getSession();
      session.setMode("ace/mode/markdown");
      session.setUseWrapMode(true);
      return session.setUseSoftTabs(true);
    };

    EditMarkdownWidget.prototype._onChange = function() {
      return this.$textarea.val(this.editor.getSession().getValue());
    };

    EditMarkdownWidget.prototype._setupToolbar = function() {
      var _this = this;
      this.$wrapper.find('.btn-toolbar .markdownH1').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n\n# ', '\n', _this.translations.heading);
      });
      this.$wrapper.find('.btn-toolbar .markdownH2').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n\n## ', '\n', _this.translations.heading);
      });
      this.$wrapper.find('.btn-toolbar .markdownH3').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n\n### ', '\n', _this.translations.heading);
      });
      this.$wrapper.find('.btn-toolbar .markdownBoldButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('**', '**');
      });
      this.$wrapper.find('.btn-toolbar .markdownItalicButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('_', '_');
      });
      this.$wrapper.find('.btn-toolbar .markdownBulletlistButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n* ', '\n');
      });
      this.$wrapper.find('.btn-toolbar .markdownNumberedlistButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n1. ', '\n');
      });
      this.$wrapper.find('.btn-toolbar .markdownBlockquoteButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n> ', '\n');
      });
      return this.$wrapper.find('.btn-toolbar .markdownUrlButton').on('click', this._onInsertUrl);
    };

    EditMarkdownWidget.prototype._surroundSelectionWith = function(before, after, emptyText) {
      var newlines, noSelection, selectedText, selectionRange;
      if (emptyText == null) {
        emptyText = 'tekst';
      }
      selectionRange = this.editor.getSelectionRange();
      selectedText = this.editor.session.getTextRange(selectionRange);
      noSelection = selectedText === '';
      if (noSelection) {
        selectedText = emptyText;
      }
      this.editor.insert("" + before + selectedText + after);
      if (noSelection) {
        newlines = before.split('\n').length - 1;
        selectionRange.start.row += newlines;
        selectionRange.end.row = selectionRange.start.row;
        selectionRange.start.column += before.length - newlines;
        selectionRange.end.column += selectionRange.start.column + emptyText.length;
        this.editor.getSelection().setSelectionRange(selectionRange);
      }
      return this.editor.focus();
    };

    EditMarkdownWidget.prototype._onInsertUrl = function(e) {
      var url;
      e.preventDefault();
      url = window.prompt('Skriv inn ønsket URL', 'http://');
      if (url != null) {
        return this._surroundSelectionWith('[', "](" + url + ")");
      }
    };

    return EditMarkdownWidget;

  })();

  if (window.devilry_gradingsystem == null) {
    window.devilry_gradingsystem = {};
  }

  window.devilry_gradingsystem.EditMarkdownWidget = EditMarkdownWidget;

}).call(this);
