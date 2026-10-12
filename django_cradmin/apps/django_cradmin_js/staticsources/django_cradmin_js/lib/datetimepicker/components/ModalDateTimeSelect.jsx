import DateTimePicker from './DateTimePicker'
import AbstractModalDateOrDateTimeSelect from './AbstractModalDateOrDateTimeSelect'
import OpenDateTimePicker from './OpenDateTimePicker'

export default class ModalDateTimeSelect extends AbstractModalDateOrDateTimeSelect {
  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      selectedPreviewFormat: 'llll'
    })
  }

  get selectType () {
    return 'datetime'
  }

  get pickerComponentClass () {
    return DateTimePicker
  }

  get openPickerComponentClass () {
    return OpenDateTimePicker
  }
}
