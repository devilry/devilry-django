class EditMarkdownWidget

    constructor: (options) ->
        {@id, @translations} = options
        @$wrapper = @$textarea = $("##{@id}_wrapper")
        @$textarea = $("##{@id}")
        @$toolbar = @$wrapper.find('.btn-toolbar')
        aceboxid = "#{@id}_aceeditor"
        @$editordiv = $("##{aceboxid}")
        @editor = ace.edit(aceboxid)
        @_configure()
        @_setupToolbar()
        @_setInitialValues()
        @editor.on('change', @_onChange)
        if @$textarea.val() == ''
            @$textarea.on('focus', @_onFocusTextArea)
        else
            @_show()

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

    _show: ->
        @$textarea.hide()
        @$toolbar.show()
        @$editordiv.show()
        @editor.focus()

    _onFocusTextArea: =>
        @_show()

    _onChange: =>
        @$textarea.val(@editor.getSession().getValue())

    _setupToolbar: ->
        @$toolbar.find('.markdownH1').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n\n# ', '\n', @translations.heading)
        @$toolbar.find('.markdownH2').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n\n## ', '\n', @translations.heading)
        @$toolbar.find('.markdownH3').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n\n### ', '\n', @translations.heading)
        @$toolbar.find('.markdownBoldButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('**', '**')
        @$toolbar.find('.markdownItalicButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('*', '*')
        @$toolbar.find('.markdownBulletlistButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n* ', '\n')
        @$toolbar.find('.markdownNumberedlistButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n1. ', '\n')
        @$toolbar.find('.markdownBlockquoteButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n> ', '\n')
        @$toolbar.find('.markdownCodeButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n``` ', '\n\n```\n', @translations.programminglanguage)
        @$toolbar.find('.markdownMathBlockButton').on 'click', (e) =>
            e.preventDefault()
            @_surroundSelectionWith('\n$mathblock$\n', '\n$/mathblock$\n', 'x + 2 = 4')
        @$toolbar.find('.markdownUrlButton').on('click', @_onInsertUrl)

    _surroundSelectionWith: (before, after, emptyText='tekst') ->
        selectionRange = @editor.getSelectionRange()
        selectedText = @editor.session.getTextRange(selectionRange)
        noSelection = selectedText == ''
        if noSelection
            selectedText = emptyText
        currentrow = selectionRange.start.row
        currentcolumn = selectionRange.start.column
        newtext = "#{before}#{selectedText}#{after}"
        @editor.insert(newtext)
        if noSelection
            newlines_total = newtext.split('\n').length - 1
            newlines_before = before.split('\n').length - 1
            newlines_selectedText = selectedText.split('\n').length - 1
            selectionRange.start.row = currentrow + newlines_before
            selectionRange.end.row = selectionRange.start.row + newlines_selectedText
            startcolumn = 0
            beforesplit = before.split('\n')
            if beforesplit.length == 1
                startcolumn = currentcolumn + before.length
            else
                startcolumn = beforesplit[beforesplit.length-1].length
            selectionRange.start.column = startcolumn
            selectionRange.end.column = selectionRange.start.column + emptyText.length
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
