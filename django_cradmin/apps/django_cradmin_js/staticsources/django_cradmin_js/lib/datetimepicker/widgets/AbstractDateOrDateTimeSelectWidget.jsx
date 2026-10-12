import React from 'react'
import ReactDOM from 'react-dom'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import moment from 'moment'
import PropTypes from 'prop-types'

export default class AbstractDateOrDateTimeSelectWidget extends AbstractWidget {
  /**
   * @returns {Object}
   * @property datetime Something that can be passed into ``moment()`` for the initial date.
   */
  getDefaultConfig () {
    return {
      locale: 'en',
      initialFocusValue: null,
      hiddenFieldId: null,
      hiddenFieldFormat: null,
      debug: true
    }
  }

  get componentClass () {
    throw new Error('componentClass getter must be implemented in subclasses')
  }

  getHiddenFieldDomElement () {
    if (this.config.hiddenFieldId === null) {
      throw new Error(`The hiddenFieldId config is required`)
    }
    const domElement = document.getElementById(this.config.hiddenFieldId)
    if (domElement === null) {
      throw new Error(`No DOM element with ID=${this.config.hiddenFieldId} found`)
    }
    return domElement
  }

  getMomentObjectFromHiddenField (hiddenFieldDomElement) {
    const value = hiddenFieldDomElement.value
    if (!value || value === '') {
      return null
    }
    return moment(value)
  }

  getInitialFocusMomentObject () {
    if (this.config.initialFocusValue === null) {
      return moment()
    }
    return moment(this.config.initialFocusValue)
  }

  get wrapperProps () {
    const hiddenFieldDomElement = this.getHiddenFieldDomElement()
    let momentObject = this.getMomentObjectFromHiddenField(hiddenFieldDomElement)
    let wrappedComponentProps = Object.assign({
      initialFocusMomentObject: this.getInitialFocusMomentObject()
    }, this.config)
    delete wrappedComponentProps.hiddenFieldId
    delete wrappedComponentProps.hiddenFieldFormat
    delete wrappedComponentProps.initialFocusValue
    return {
      wrappedComponentProps: wrappedComponentProps,
      componentClass: this.componentClass,
      momentObject: momentObject,
      hiddenFieldId: this.config.hiddenFieldId,
      hiddenFieldFormat: this.config.hiddenFieldFormat,
      hiddenFieldDomElement: hiddenFieldDomElement,
      debug: this.config.debug
    }
  }

  renderWrapper () {
    return <DateOrDateTimeSelectWrapper {...this.wrapperProps} />
  }

  constructor (element, widgetInstanceId) {
    super(element, widgetInstanceId)
    ReactDOM.render(
      this.renderWrapper(),
      this.element
    )
  }

  destroy () {
    ReactDOM.unmountComponentAtNode(this.element)
  }
}

export class DateOrDateTimeSelectWrapper extends React.Component {
  static get defaultProps () {
    return {
      momentObject: null,
      hiddenFieldId: null,
      hiddenFieldFormat: null,
      hiddenFieldDomElement: null,
      componentClass: null,
      wrappedComponentProps: null,
      debug: false
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any,
      hiddenFieldId: PropTypes.string.isRequired,
      hiddenFieldFormat: PropTypes.string.isRequired,
      hiddenFieldDomElement: PropTypes.any.isRequired,
      componentClass: PropTypes.any.isRequired,
      wrappedComponentProps: PropTypes.object.isRequired,
      debug: PropTypes.bool.isRequired
    }
  }

  constructor (props) {
    super(props)
    this.onChange = this.onChange.bind(this)
    this.state = this.makeInitialState()
  }

  makeInitialState () {
    return {
      selectedMoment: this.props.momentObject
    }
  }

  get hiddenFieldValue () {
    if (this.state.selectedMoment !== null) {
      return this.state.selectedMoment.format(this.props.hiddenFieldFormat)
    }
    return ''
  }

  onChange (momentObject) {
    this.setState({
      selectedMoment: momentObject
    }, () => {
      this.props.hiddenFieldDomElement.value = this.hiddenFieldValue
    })
  }

  renderWrappedComponent () {
    const ComponentClass = this.props.componentClass
    return <ComponentClass
      key={'datetimeComponent'}
      momentObject={this.state.selectedMoment}
      onChange={this.onChange}
      {...this.props.wrappedComponentProps}
    />
  }

  render () {
    return this.renderWrappedComponent()
  }
}
