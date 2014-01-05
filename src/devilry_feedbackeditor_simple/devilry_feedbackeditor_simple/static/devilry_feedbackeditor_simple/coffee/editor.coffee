class Editor
    constructor: (@$textarea) ->

  get_raw_text: ->
    return @$textarea.val()

  _get_escaped_raw_text: ->
    div = document.createElement('div')
    div.appendChild(document.createTextNode(@get_raw_text()))
    return div.innerHTML

  get_rendered_view: ->
    return "<div style='white-space: pre-wrap'>#{@_get_escaped_raw_text()}</div>"


window.devilry_feedbackeditor_simple = {
  Editor: Editor
}