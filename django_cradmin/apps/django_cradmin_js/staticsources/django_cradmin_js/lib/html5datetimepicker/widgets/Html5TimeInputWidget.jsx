import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import Html5TimeInput from '../Html5TimeInput'

/**
 * Add the widget to a Django template
 *
 * @example
 * <input type="hidden" id="id_test100">
 * <div data-ievv-jsbase-widget="cradmin-html5-timepicker"
 *      data-ievv-jsbase-widget-config='{"hiddenFieldId": "id_test100", "ariaLabel": "Select a time"}'>
 * </div>
 */
export default class Html5TimeInputWidget extends AbstractWidget {
  getDefaultConfig () {
    return {
      hiddenFieldId: null
    }
  }

  getHiddenFieldInitialValue (hiddenFieldDomElement) {
    const value = hiddenFieldDomElement.value
    if (!value || value === '' || !Html5TimeInput.isValidTime(value)) {
      return ''
    }
    return value
  }

  get wrapperProps () {
    const hiddenFieldDomElement = document.getElementById(this.config.hiddenFieldId)
    const hiddenFieldValue = this.getHiddenFieldInitialValue(hiddenFieldDomElement)
    let wrappedComponentProps = Object.assign({value: hiddenFieldValue, ...this.config})
    delete wrappedComponentProps.hiddenFieldId
    return {
      componentClass: Html5TimeInput,
      wrappedComponentProps: wrappedComponentProps,
      hiddenFieldId: this.config.hiddenFieldId,
      hiddenFieldDomElement: hiddenFieldDomElement
    }
  }

  renderWrapper () {
    return <Html5TimeInputWrapper {...this.wrapperProps}/>
  }

  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId)
    ReactDOM.render(
      this.renderWrapper(),
      this.element
    )
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.element)
  }
}


export class Html5TimeInputWrapper extends React.Component {
  static get defaultProps () {
    return {
      hiddenFieldId: null,
      hiddenFieldDomElement: null,
      wrappedComponentProps: null,
      componentClass: null
    }
  }

  static get propTypes () {
    return {
      hiddenFieldId: PropTypes.string.isRequired,
      hiddenFieldDomElement: PropTypes.any.isRequired,
      wrappedComponentProps: PropTypes.object.isRequired,
      componentClass: PropTypes.any.isRequired
    }
  }

  constructor (props) {
    super(props)
    this.onChange = this.onChange.bind(this)
  }

  onChange (isoStringValue) {
    this.props.hiddenFieldDomElement.value = isoStringValue
  }

  renderWrappedComponent () {
    const ComponentClass = this.props.componentClass
    return <ComponentClass
      key={'html5dateComponent'}
      onChange={this.onChange}
      {...this.props.wrappedComponentProps}/>
  }

  render () {
    return this.renderWrappedComponent()
  }
}
