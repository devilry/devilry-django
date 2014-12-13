(function() {
  var EditMarkdownWidget,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  EditMarkdownWidget = (function() {
    function EditMarkdownWidget(options) {
      this._onInsertUrl = __bind(this._onInsertUrl, this);
      this._onChange = __bind(this._onChange, this);
      this._onFocusTextArea = __bind(this._onFocusTextArea, this);
      var aceboxid;
      this.id = options.id, this.translations = options.translations;
      this.$wrapper = this.$textarea = $("#" + this.id + "_wrapper");
      this.$textarea = $("#" + this.id);
      this.$toolbar = this.$wrapper.find('.btn-toolbar');
      aceboxid = "" + this.id + "_aceeditor";
      this.$editordiv = $("#" + aceboxid);
      this.editor = ace.edit(aceboxid);
      this._configure();
      this._setupToolbar();
      this._setInitialValues();
      this.editor.on('change', this._onChange);
      if (this.$textarea.val() === '') {
        this.$textarea.on('focus', this._onFocusTextArea);
      } else {
        this._show();
      }
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

    EditMarkdownWidget.prototype._show = function() {
      this.$textarea.hide();
      this.$toolbar.show();
      this.$editordiv.show();
      return this.editor.focus();
    };

    EditMarkdownWidget.prototype._onFocusTextArea = function() {
      return this._show();
    };

    EditMarkdownWidget.prototype._onChange = function() {
      return this.$textarea.val(this.editor.getSession().getValue());
    };

    EditMarkdownWidget.prototype._setupToolbar = function() {
      var _this = this;
      this.$toolbar.find('.markdownH1').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n\n# ', '\n', _this.translations.heading);
      });
      this.$toolbar.find('.markdownH2').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n\n## ', '\n', _this.translations.heading);
      });
      this.$toolbar.find('.markdownH3').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n\n### ', '\n', _this.translations.heading);
      });
      this.$toolbar.find('.markdownBoldButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('**', '**');
      });
      this.$toolbar.find('.markdownItalicButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('*', '*');
      });
      this.$toolbar.find('.markdownBulletlistButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n* ', '\n');
      });
      this.$toolbar.find('.markdownNumberedlistButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n1. ', '\n');
      });
      this.$toolbar.find('.markdownBlockquoteButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n> ', '\n');
      });
      this.$toolbar.find('.markdownCodeButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n``` ', '\n\n```\n', _this.translations.programminglanguage);
      });
      this.$toolbar.find('.markdownMathBlockButton').on('click', function(e) {
        e.preventDefault();
        return _this._surroundSelectionWith('\n$mathblock$\n', '\n$/mathblock$\n', 'x + 2 = 4');
      });
      return this.$toolbar.find('.markdownUrlButton').on('click', this._onInsertUrl);
    };

    EditMarkdownWidget.prototype._surroundSelectionWith = function(before, after, emptyText) {
      var beforesplit, currentcolumn, currentrow, newlines_before, newlines_selectedText, newlines_total, newtext, noSelection, selectedText, selectionRange, startcolumn;
      if (emptyText == null) {
        emptyText = 'tekst';
      }
      selectionRange = this.editor.getSelectionRange();
      selectedText = this.editor.session.getTextRange(selectionRange);
      noSelection = selectedText === '';
      if (noSelection) {
        selectedText = emptyText;
      }
      currentrow = selectionRange.start.row;
      currentcolumn = selectionRange.start.column;
      newtext = "" + before + selectedText + after;
      this.editor.insert(newtext);
      if (noSelection) {
        newlines_total = newtext.split('\n').length - 1;
        newlines_before = before.split('\n').length - 1;
        newlines_selectedText = selectedText.split('\n').length - 1;
        selectionRange.start.row = currentrow + newlines_before;
        selectionRange.end.row = selectionRange.start.row + newlines_selectedText;
        startcolumn = 0;
        beforesplit = before.split('\n');
        if (beforesplit.length === 1) {
          startcolumn = currentcolumn + before.length;
        } else {
          startcolumn = beforesplit[beforesplit.length - 1].length;
        }
        selectionRange.start.column = startcolumn;
        selectionRange.end.column = selectionRange.start.column + emptyText.length;
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
