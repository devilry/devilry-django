import EmbeddedDateSelect from '../components/EmbeddedDateSelect'
import AbstractDateOrDateTimeSelectWidget from './AbstractDateOrDateTimeSelectWidget'

export default class EmbeddedDateSelectWidget extends AbstractDateOrDateTimeSelectWidget {
  getDefaultConfig () {
    return Object.assign({}, super.getDefaultConfig(), {
      hiddenFieldFormat: 'YYYY-MM-DD'
    })
  }

  get componentClass () {
    return EmbeddedDateSelect
  }
}
