import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'

/**
 * Widget used by uicontainer.Form for disabling "Enter" key to prevent form being submitted when
 * editing e.g a input-field.
 *
 * This widget exists mostly to prevent form submitting because we have
 * a lot of views combining jsbase-widgets and django-forms resulting in editing a input-field in a widget with the same
 * name as a django-form input-field resulted in the data being posted and django-form input-field value being
 * overwritten in the data from the jsbase-widget.
 *
 * This widget will prevent registering "Enter"-keypress on all input and non-input fields unless it's:
 *  - of type 'textarea'
 *  - html-element is a button (for accessibility)
 */
export default class DisableFormSubmitOnEnter extends AbstractWidget {
  constructor (element, widgetInstanceId) {
    super(element, widgetInstanceId)

    const suppressEnter = (event) => {
      let target = null
      if (event.target) {
        target = event.target
      } else if (event.srcElement) {
        target = event.srcElement
      }

      if (target && event.keyCode === 13 && target.nodeName === 'BUTTON') {
        return true
      }
      else if (target && event.keyCode === 13 && target.type !== 'textarea') {
        return false
      }
    }
    element.onkeypress = suppressEnter
  }
}
