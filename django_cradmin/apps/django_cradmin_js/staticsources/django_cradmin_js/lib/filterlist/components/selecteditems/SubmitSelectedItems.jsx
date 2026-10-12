import React from 'react'
import PropTypes from 'prop-types'
import AbstractSelectedItems from './AbstractSelectedItems'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import BemUtilities from '../../../utilities/BemUtilities'
import HiddenFieldRenderSelectedItems from './HiddenFieldRenderSelectedItems'

/**
 * Render a button for submitting selected items in a form
 * (a `<button type="submit">`).
 *
 * See {@link SubmitSelectedItems.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "SubmitSelectedItems",
 *    "props": {
 *       "formAction": "https://example.com/my/submit/view"
 *    }
 * }
 *
 * @example <caption>Spec - custom label</caption>
 * {
 *    "component": "SubmitSelectedItems",
 *    "props": {
 *       "formAction": "https://example.com/my/submit/view",
 *       "label": "Submit the selected items!"
 *    }
 * }
 *
 * @example <caption>Spec - custom min and max selected items</caption>
 * {
 *    "component": "SubmitSelectedItems",
 *    "props": {
 *       "formAction": "https://example.com/my/submit/view",
 *       "minSelectedItems": 2,
 *       "maxSelectedItems": 2
 *    }
 * }
 */
export default class SubmitSelectedItems extends AbstractSelectedItems {
  static get propTypes () {
    return Object.assign({}, {
      formAction: PropTypes.string.isRequired,
      formMethod: PropTypes.string.isRequired,
      hiddenFieldName: PropTypes.string.isRequired,
      debug: PropTypes.bool.isRequired,
      formClassName: PropTypes.string.isRequired,
      buttonBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      label: PropTypes.string.isRequired,
      minSelectedItems: PropTypes.number.isRequired,
      maxSelectedItems: PropTypes.number,
      extraHiddenFields: PropTypes.object.isRequired
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractSelectedItems.defaultProps}.
   *
   * @return {Object}
   * @property {string} formAction The form `action` attribute.
   *    This is required.
   *    **Must be provided in spec**.
   * @property {string} formMethod The form `method` attribute.
   *    This is required, and defaults to "POST".
   *    **Can be used in spec**.
   * @property {string} hiddenFieldName The name of the hidden field.
   *    This is required.
   *    **Must be provided in spec**.
   * @property {[string]} buttonBemVariants BEM variants for the selectable-list.
   *    **Can be used in spec**.
   * @property {number} minSelectedItems Minimum number of selected items
   *    required before the button is rendered.
   *    This is required, and defaults to `1`. Setting this to `0` will be
   *    the same as setting it to `1` since the button is never rendered
   *    if we have no selected items.
   *    **Can be used in spec**.
   * @property {number} minSelectedItems Maximum number of selected items
   *    required before the button is rendered. If this is `null`,
   *    the button is rendered as long as more than `minSelectedItems`
   *    is selected.
   *    This is not required (can be null), and defaults to `null`.
   *    **Can be used in spec**.
   * @property {bool} debug If this is `true`, we render input elements of
   *    type "text" instead of "hidden". Nice for debugging.
   *    Defaults to `false`.
   *    **Can be used in spec**.
   * @property {{}} extraHiddenFields Extra hidden fields. Object mapping
   *    field name to field value.
   *    Defaults to empty object (`{}`).
   *    **Can be used in spec**.
   */
  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      formAction: null,
      formMethod: 'POST',
      hiddenFieldName: null,
      debug: false,
      formClassName: 'paragraph',
      buttonBemVariants: [],
      minSelectedItems: 1,
      maxSelectedItems: null,
      label: window.gettext('Submit'),
      extraHiddenFields: {}
    })
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClick = this.onClick.bind(this)
  }

  onClick (listItemId) {
    this.props.childExposedApi.deselectItem(listItemId)
  }

  get buttonBemBlock () {
    return 'button'
  }

  get buttonClassName () {
    return BemUtilities.addVariants(this.buttonBemBlock, this.props.buttonBemVariants)
  }

  get formClassName () {
    return this.props.formClassName
  }

  renderLabel () {
    return this.props.label
  }

  renderButton () {
    return <button type='submit' key='button' className={this.buttonClassName}>
      {this.renderLabel()}
    </button>
  }

  renderHiddenFields () {
    const uniqueComponentKey = `${this.props.uniqueComponentKey}-HiddenFieldRenderSelectedItems`
    const domIdPrefix = `${this.props.domIdPrefix}-HiddenFieldRenderSelectedItems`
    return <HiddenFieldRenderSelectedItems
      key='hiddenFields'
      name={this.props.hiddenFieldName}
      debug={this.props.debug}
      selectedListItemsMap={this.props.selectedListItemsMap}
      childExposedApi={this.props.childExposedApi}
      uniqueComponentKey={uniqueComponentKey}
      domIdPrefix={domIdPrefix}
      location={this.props.location}
    />
  }

  renderExtraHiddenField (fieldName, fieldValue) {
    const key = `extraHiddenField-${fieldName}`
    return <input
      key={key}
      type='hidden'
      name={fieldName}
      defaultValue={fieldValue} />
  }

  renderExtraHiddenFields () {
    const renderedHiddenFields = []
    for (let fieldName of Object.keys(this.props.extraHiddenFields)) {
      renderedHiddenFields.push(this.renderExtraHiddenField(
        fieldName, this.props.extraHiddenFields[fieldName]))
    }
    return renderedHiddenFields
  }

  renderFormContent () {
    return [
      this.renderHiddenFields(),
      this.renderButton(),
      ...this.renderExtraHiddenFields()
    ]
  }

  renderForm () {
    return <form
      method={this.props.formMethod}
      action={this.props.formAction}
      className={this.formClassName}>
      {this.renderFormContent()}
    </form>
  }

  render () {
    const selectedItemCount = this.props.selectedListItemsMap.size
    if (selectedItemCount === 0) {
      return null
    }
    if (selectedItemCount < this.props.minSelectedItems) {
      return null
    }
    if (this.props.maxSelectedItems !== null && selectedItemCount > this.props.maxSelectedItems) {
      return null
    }
    return this.renderForm()
  }
}
