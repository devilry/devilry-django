
class EditFeedback
  ###
  ###
  constructor: (unique_name) ->
    @editor_api = window[unique_name]
    $footer = $("#wrapper-footer-#{unique_name }")
    $footer.find('.btn.publish-feedback-without-preview').click(@_onClickPublishWithoutPreview)
    $footer.find('.btn.preview-feedback').click(@_onClickPreview)

  _onClickPublishWithoutPreview: (e) =>
    e.preventDefault()
    console.log '_onClickPublishWithoutPreview'

  _onClickPreview: (e) =>
    e.preventDefault()
    console.log '_onClickPreview'

window.devilry_examiner_edit_feedback = {
  EditFeedback: EditFeedback
}