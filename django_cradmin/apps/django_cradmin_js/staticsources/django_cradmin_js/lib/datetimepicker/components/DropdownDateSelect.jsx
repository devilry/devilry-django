import DatePicker from './DatePicker'
import AbstractDropdownDateOrDateTimeSelect from './AbstractDropdownDateOrDateTimeSelect'
import OpenDatePicker from './OpenDatePicker'

export default class DropdownDateSelect extends AbstractDropdownDateOrDateTimeSelect {
  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      hiddenFieldFormat: 'YYYY-MM-DD',
      selectedPreviewFormat: 'll'
    })
  }

  get selectType () {
    return 'date'
  }

  get pickerComponentClass () {
    return DatePicker
  }

  get openPickerComponentClass () {
    return OpenDatePicker
  }
}
