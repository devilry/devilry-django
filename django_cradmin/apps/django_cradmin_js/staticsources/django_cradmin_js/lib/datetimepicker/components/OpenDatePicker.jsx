import * as gettext from 'ievv_jsbase/lib/gettext'
import AbstractOpenPicker from './AbstractOpenPicker'

export default class OpenDatePicker extends AbstractOpenPicker {
  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      nowButtonLabel: gettext.gettext('Today'),
      momentObjectFormat: 'll'
    })
  }
}
