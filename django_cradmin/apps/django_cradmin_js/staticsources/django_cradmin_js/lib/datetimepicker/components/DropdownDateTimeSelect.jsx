import DateTimePicker from './DateTimePicker'
import AbstractDropdownDateOrDateTimeSelect from './AbstractDropdownDateOrDateTimeSelect'
import OpenDateTimePicker from './OpenDateTimePicker'

export default class DropdownDateTimeSelect extends AbstractDropdownDateOrDateTimeSelect {
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
