import DropdownDateSelect from '../components/DropdownDateSelect'
import AbstractDateOrDateTimeSelectWidget from './AbstractDateOrDateTimeSelectWidget'

export default class DropdownDateSelectWidget extends AbstractDateOrDateTimeSelectWidget {
  getDefaultConfig () {
    return Object.assign({}, super.getDefaultConfig(), {
      hiddenFieldFormat: 'YYYY-MM-DD'
    })
  }

  get componentClass () {
    return DropdownDateSelect
  }
}
