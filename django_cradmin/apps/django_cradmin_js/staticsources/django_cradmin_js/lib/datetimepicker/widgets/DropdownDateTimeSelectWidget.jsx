import DropdownDateTimeSelect from '../components/DropdownDateTimeSelect'
import AbstractDateOrDateTimeSelectWidget from './AbstractDateOrDateTimeSelectWidget'

export default class DropdownDateTimeSelectWidget extends AbstractDateOrDateTimeSelectWidget {
  getDefaultConfig () {
    return Object.assign({}, super.getDefaultConfig(), {
      hiddenFieldFormat: 'YYYY-MM-DD HH:mm:ss',
      showSeconds: false
    })
  }

  get componentClass () {
    return DropdownDateTimeSelect
  }
}
