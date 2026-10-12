import DatePicker from './DatePicker'
import AbstractModalDateOrDateTimeSelect from './AbstractModalDateOrDateTimeSelect'
import OpenDatePicker from './OpenDatePicker'

export default class ModalDateSelect extends AbstractModalDateOrDateTimeSelect {
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
