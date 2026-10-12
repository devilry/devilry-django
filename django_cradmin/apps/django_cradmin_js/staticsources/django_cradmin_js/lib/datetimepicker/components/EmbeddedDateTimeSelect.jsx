import AbstractEmbeddedDateOrDateTimeSelect from './AbstractEmbeddedDateOrDateTimeSelect'
import DateTimePicker from './DateTimePicker'

export default class EmbeddedDateTimeSelect extends AbstractEmbeddedDateOrDateTimeSelect {
  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      selectedPreviewFormat: 'llll'
    })
  }

  get pickerComponentClass () {
    return DateTimePicker
  }
}
