import React from 'react'
import AbstractComponentGroup from './AbstractComponentGroup'
import BemUtilities from '../../../utilities/BemUtilities'
import PropTypes from 'prop-types'

export default class SelectComponentGroup extends AbstractComponentGroup {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      selectableComponentGroups: PropTypes.arrayOf(PropTypes.object).isRequired,
      initialEnabled: PropTypes.string.isRequired,
      bemBlock: PropTypes.string.isRequired,
      wrapperClassName: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      name: PropTypes.string.isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      selectableComponentGroups: [],
      initialEnabled: '',
      bemBlock: 'radio',
      name: null,
      bemVariants: ['block'],
      label: '',
      wrapperClassName: 'label'
    })
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    let selected = ''
    for (const componentGroup of nextProps.selectableComponentGroups) {
      if (nextProps.childExposedApi.componentGroupIsEnabled(componentGroup.name)) {
        if (selected) {
          SelectComponentGroup.selectComponentGroup(selected, nextProps)
          break
        }
        selected = componentGroup.name
      }
    }

    if (!selected) {
      SelectComponentGroup.selectComponentGroup(nextProps.initialEnabled, nextProps)
    }
    return null
  }


  setupBoundMethods () {
    super.setupBoundMethods()
    this.selectComponentGroupClickListener = this.selectComponentGroupClickListener.bind(this)
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  static selectComponentGroup (enabledComponentGroup, props) {
    if (!props.childExposedApi.componentGroupIsEnabled(enabledComponentGroup)) {
      props.childExposedApi.enableComponentGroup(enabledComponentGroup)
    }

    for (const componentGroup of props.selectableComponentGroups) {
      if (componentGroup.name !== enabledComponentGroup &&
          props.childExposedApi.componentGroupIsEnabled(componentGroup.name)) {
        props.childExposedApi.disableComponentGroup(componentGroup.name)
      }
    }
  }

  selectComponentGroupClickListener (event) {
    SelectComponentGroup.selectComponentGroup(event.target.value, this.props)
  }

  renderSelectableComponentGroups () {
    const selectableComponentGroups = []
    for (const componentGroup of this.props.selectableComponentGroups) {
      selectableComponentGroups.push(
        <label className={this.className} key={componentGroup.name}>
          <input
            type={'radio'}
            name={this.props.name}
            value={componentGroup.name}
            checked={this.props.enabledComponentGroups.has(componentGroup.name)}
            onChange={this.selectComponentGroupClickListener} />
          <span className={'radio__control-indicator'} />
          {componentGroup.label}
        </label>
      )
    }

    return selectableComponentGroups
  }

  render () {
    if (this.props.selectableComponentGroups.length === 0) {
      console.warn('attempting to use SelectComponentGroup without passing any selectableComponentGroups - not rendering anything.')
      return null
    }
    return <p className={this.props.wrapperClassName}>
      {this.props.label}
      {this.renderSelectableComponentGroups()}
    </p>
  }
}
