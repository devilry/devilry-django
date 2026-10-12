import AbstractModalDateOrDateTimeSelect from './AbstractModalDateOrDateTimeSelect'

export default class AbstractDropdownDateOrDateTimeSelect extends AbstractModalDateOrDateTimeSelect {
  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      bemVariants: ['dropdown'],
      bodyBemVariants: ['dropdown']
    })
  }

  renderBackdrop () {
    return null
  }
}
