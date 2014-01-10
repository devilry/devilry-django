class EditMarkdownWidget

    constructor: (options) ->
        {@id, @translations} = options
        @$wrapper = @$textarea = $("##{@id}_wrapper")
        @$textarea = $("##{@id}")
        aceboxid = "#{@id}_aceeditor"
        @editor = ace.edit(aceboxid)
        @_configure()
        @_setupToolbar()
        @_setInitialValues()
        @editor.on('change', @_onChange)

    _setInitialValues: ->
        markdownString = @$textarea.val()
        @editor.getSession().setValue(markdownString)

    _configure: ->
        # @editor.setTheme('ace/theme/textmate')
        @editor.setTheme('ace/theme/tomorrow')
        @editor.setHighlightActiveLine(false)
        @editor.setShowPrintMargin(false)
        @editor.renderer.setShowGutter(false)
        session = @editor.getSession()
        session.setMode("ace/mode/markdown")
        session.setUseWrapMode(true)
        session.setUseSoftTabs(true)

    _onChange: =>
        @$textarea.val(@editor.getSession().getValue())

    _setupToolbar: ->
        @$wrapper.find('.btn-toolbar .markdownH1').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n\n# ', '\n', @translations.heading)
        @$wrapper.find('.btn-toolbar .markdownH2').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n\n## ', '\n', @translations.heading)
        @$wrapper.find('.btn-toolbar .markdownH3').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n\n### ', '\n', @translations.heading)
        @$wrapper.find('.btn-toolbar .markdownBoldButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('**', '**')
        @$wrapper.find('.btn-toolbar .markdownItalicButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('_', '_')
        @$wrapper.find('.btn-toolbar .markdownBulletlistButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n* ', '\n')
        @$wrapper.find('.btn-toolbar .markdownNumberedlistButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n1. ', '\n')
        @$wrapper.find('.btn-toolbar .markdownBlockquoteButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n> ', '\n')
        @$wrapper.find('.btn-toolbar .markdownUrlButton').on('click', @_onInsertUrl)

    _surroundSelectionWith: (before, after, emptyText='tekst') ->
        selectionRange = @editor.getSelectionRange()
        selectedText = @editor.session.getTextRange(selectionRange)
        noSelection = selectedText == ''
        if noSelection
            selectedText = emptyText
        @editor.insert("#{before}#{selectedText}#{after}")
        if noSelection
            newlines = before.split('\n').length - 1
            selectionRange.start.row += newlines
            selectionRange.end.row = selectionRange.start.row
            selectionRange.start.column += before.length - newlines
            selectionRange.end.column += selectionRange.start.column + emptyText.length
            @editor.getSelection().setSelectionRange(selectionRange)
        @editor.focus()

    _onInsertUrl: (e) =>
        e.preventDefault()
        url = window.prompt('Skriv inn ønsket URL', 'http://')
        if url?
            @_surroundSelectionWith('[', "](#{url})")


if not window.devilry_gradingsystem?
    window.devilry_gradingsystem = {}
window.devilry_gradingsystem.EditMarkdownWidget = EditMarkdownWidget
