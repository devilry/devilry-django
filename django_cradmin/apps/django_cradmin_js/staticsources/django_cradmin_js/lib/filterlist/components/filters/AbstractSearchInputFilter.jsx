import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from './AbstractFilter'
import BemUtilities from '../../../utilities/BemUtilities'
import SearchInputClearButton from './components/SearchInputClearButton'
import AriaDescribedByTarget from '../../../components/AriaDescribedByTarget'
import * as gettext from 'ievv_jsbase/lib/gettext'
// import { KEYBOARD_NAVIGATION_GROUP_KEY_UP_DOWN } from '../../filterListConstants'

/**
 * Abstract base class for filters.
 *
 * See {@link AbstractSearchInputFilter.defaultProps} for documentation for
 * props and their defaults.
 */
export default class AbstractSearchInputFilter extends AbstractFilter {
  static get propTypes () {
    return Object.assign({}, {
      label: PropTypes.string.isRequired,
      labelIsScreenreaderOnly: PropTypes.bool.isRequired,
      labelBemBlock: PropTypes.string.isRequired,
      labelBemVariants: PropTypes.arrayOf(PropTypes.string),
      placeholder: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string)
      ]),
      fieldWrapperBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      value: PropTypes.string,
      searchInputExtraAriaDescription: PropTypes.string
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractFilter.defaultProps}.
   *
   * @return {Object}
   * @property {[string]|string} placeholder A placeholder string,
   *    or an array of placeholder strings.
   *    **Can be used in spec**.
   * @property {string} label A required label for the search field.
   *    Defaults null, but you have to set it (for accessibility compliancy).
   *    Use the `labelIsScreenreaderOnly` prop to make the label only visible
   *    to screenreaders.
   *    **Can be used in spec**.
   * @property {string} labelIsScreenreaderOnly Make the label only visible to
   *    screenreaders. Defaults to ``false``.
   *    **Can be used in spec**.
   * @property {string} labelBemBlock BEM block for the label.
   *    Defaults to "label".
   *    **Can be used in spec**.
   * @property {[]} labelBemVariants BEM variants for the label.
   *    Defaults to empty array.
   *    **Can be used in spec**.
   * @property {[string]} fieldWrapperBemVariants Array of BEM variants
   *    for the field wrapper element.
   *    Defaults to `['outlined']`.
   *    **Can be used in spec**.
   * @property {string} value The value as a string.
   *    _Provided automatically by the parent component_.
   */
  static get defaultProps () {
    return {
      ...super.defaultProps,
      placeholder: '',
      label: gettext.gettext('Search'),
      labelIsScreenreaderOnly: false,
      labelBemBlock: 'label',
      labelBemVariants: [],
      fieldWrapperBemVariants: ['outlined'],
      value: '',
      searchInputExtraAriaDescription: null
    }
  }

  static filterHttpRequest (httpRequest, name, value) {
    httpRequest.urlParser.queryString.set(name, value || '')
  }

  // static getKeyboardNavigationGroups (componentSpec) {
  //   return [KEYBOARD_NAVIGATION_GROUP_KEY_UP_DOWN]
  // }

  constructor (props) {
    super(props)
    this.placeholderRotateTimeoutId = null
  }

  static getDerivedStateFromProps() {
    return {
      currentPlaceholderIndex: 0
    }
  }

  componentDidMount () {
    super.componentDidMount()
    if (this.placeholderIsRotatable()) {
      this.queuePlaceholderRotation()
    }
  }

  componentWillUnmount () {
    this.cancelPlaceholderRotation()
  }

  getInitialState () {
    return {
      currentPlaceholderIndex: 0
    }
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChange = this.onChange.bind(this)
    this.onClickClearButton = this.onClickClearButton.bind(this)
    this.rotatePlaceholder = this.rotatePlaceholder.bind(this)
  }

  get stringValue () {
    return this.props.value || ''
  }

  //
  //
  // Rotating placeholder
  //
  //

  get placeholderArray () {
    if (Array.isArray(this.props.placeholder)) {
      return this.props.placeholder
    }
    return [this.props.placeholder]
  }

  get placeholderRotateIntervalMilliseconds () {
    return 2000
  }

  get placeholder () {
    if (Array.isArray(this.props.placeholder)) {
      if (this.props.placeholder.length === 0) {
        return ''
      }
      return this.props.placeholder[this.state.currentPlaceholderIndex]
    }
    return this.props.placeholder
  }

  placeholderIsRotatable () {
    return Array.isArray(this.props.placeholder) && this.props.placeholder.length > 1
  }

  cancelPlaceholderRotation () {
    if (this.placeholderRotateTimeoutId !== null) {
      window.clearTimeout(this.placeholderRotateTimeoutId)
    }
  }

  queuePlaceholderRotation () {
    this.cancelPlaceholderRotation()
    this.placeholderRotateTimeoutId = window.setTimeout(
      this.rotatePlaceholder,
      this.placeholderRotateIntervalMilliseconds)
  }

  rotatePlaceholder () {
    let currentPlaceholderIndex = this.state.currentPlaceholderIndex + 1
    if (currentPlaceholderIndex >= this.placeholderArray.length) {
      currentPlaceholderIndex = 0
    }
    this.setState({
      currentPlaceholderIndex: currentPlaceholderIndex
    })
    this.queuePlaceholderRotation()
  }

  //
  //
  // Search text value change
  //
  //

  onChange (event) {
    const searchString = event.target.value
    this.setFilterValue(searchString)
  }

  onClickClearButton () {
    this.setFilterValue('')
    window.setTimeout(() => {
      this.getSearchInputRef().focus()
    }, 100)
  }

  //
  //
  // Rendering
  //
  //

  getSearchInputRef () {
    return this._searchInputRef
  }

  get labelClassName () {
    if (this.props.labelIsScreenreaderOnly) {
      return 'screenreader-only'
    }
    return BemUtilities.addVariants(this.props.labelBemBlock, this.props.labelBemVariants)
  }

  get fieldWrapperClassName () {
    return BemUtilities.addVariants('searchinput', this.props.fieldWrapperBemVariants)
  }

  get bodyClassName () {
    return 'searchinput__body'
  }

  get inputClassName () {
    return 'searchinput__input'
  }

  get labelTextClassName () {
    if (process.env.NODE_ENV === 'test') {
      return 'test-label-text'
    }
    return null
  }

  get inputFieldDomId () {
    return this.makeDomId('inputField')
  }

  get labelDomId () {
    return this.makeDomId('label')
  }

  renderLabelText () {
    if (this.props.label) {
      return <span className={this.labelTextClassName}>{this.props.label}</span>
    }
    return null
  }

  renderClearButton () {
    return <SearchInputClearButton
      key={'clear-button'}
      onClick={this.onClickClearButton}
      onBlur={this.onBlur}
      onFocus={this.onFocus}
      ariaHidden />
  }

  renderButtons () {
    throw new Error('renderButtons() must be overridden in subclasses')
  }

  get searchInputExtraAriaDescribedByDomId () {
    return this.makeDomId('searchInputExtraAriaDescribedBy')
  }

  renderSearchInputExtraAriaDescribedBy () {
    if (this.props.searchInputExtraAriaDescription === null) {
      return null
    }
    return <AriaDescribedByTarget
      domId={this.searchInputExtraAriaDescribedByDomId}
      message={this.props.searchInputExtraAriaDescription}
      key={'searchInput extra aria-describedby'} />
  }

  get searchInputAriaDescribedByDomIds () {
    if (this.props.searchInputExtraAriaDescription !== null) {
      return this.searchInputExtraAriaDescribedByDomId
    }
    return null
  }

  renderSearchInputField (extraProps) {
    let allExtraProps = {
      ...extraProps,
      ...this.ariaProps
    }
    return <input
      {...allExtraProps}
      key={'search input'}
      type='text'
      ref={(input) => { this._searchInputRef = input }}
      id={this.inputFieldDomId}
      aria-describedby={this.searchInputAriaDescribedByDomIds}
      placeholder={this.placeholder}
      className={this.inputClassName}
      value={this.stringValue}
      onChange={this.onChange}
      onBlur={this.onBlur}
      onFocus={this.onFocus}
    />
  }

  renderSearchInput (extraProps = {}) {
    return [
      this.renderSearchInputExtraAriaDescribedBy(),
      this.renderSearchInputField(extraProps)
    ]
  }

  renderBodyContent () {
    return this.renderSearchInput()
  }

  renderFieldWrapper () {
    return <div className={this.fieldWrapperClassName} key={`${this.props.name}-fieldwrapper`}>
      <span className={this.bodyClassName}>
        {this.renderBodyContent()}
      </span>
      {this.renderButtons()}
    </div>
  }

  renderIf (shouldRender, content) {
    if (shouldRender) {
      return content
    }
    return null
  }

  renderLabel (includeFieldWrapper) {
    let labelProps = {
      key: `${this.props.name}-label`,
      id: this.labelDomId,
      className: this.labelClassName,
      htmlFor: this.inputFieldDomId
    }
    return <label {...labelProps}>
      {this.renderLabelText()}
      {this.renderIf(includeFieldWrapper, this.renderFieldWrapper())}
    </label>
  }

  render () {
    return [
      this.renderLabel(false),
      this.renderFieldWrapper()
    ]
  }
}
