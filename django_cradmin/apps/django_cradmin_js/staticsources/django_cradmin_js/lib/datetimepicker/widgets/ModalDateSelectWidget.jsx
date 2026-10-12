import ModalDateSelect from '../components/ModalDateSelect'
import AbstractDateOrDateTimeSelectWidget from './AbstractDateOrDateTimeSelectWidget'

export default class ModalDateSelectWidget extends AbstractDateOrDateTimeSelectWidget {
  getDefaultConfig () {
    return Object.assign({}, super.getDefaultConfig(), {
      hiddenFieldFormat: 'YYYY-MM-DD'
    })
  }

  get componentClass () {
    return ModalDateSelect
  }
}
