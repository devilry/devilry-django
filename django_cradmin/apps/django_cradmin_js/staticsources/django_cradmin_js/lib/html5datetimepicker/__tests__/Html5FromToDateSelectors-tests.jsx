/* eslint-env jest */
import React from 'react'
import { RENDER_LOCATION_DEFAULT } from '../../filterlist/filterListConstants'
import Html5FromToDateSelectors from '../Html5FromToDateSelectors'
import { shallow } from 'enzyme'

function renderSelector (selectorComponentClass, props = {}) {
  const fullProps = Object.assign({
    location: RENDER_LOCATION_DEFAULT,
    uniqueComponentKey: 'test',
    name: 'test',
    fromDateValue: '',
    toDateValue: '',
    onChange: jest.fn(),
    label: 'testing',
    expandedLabel: null,
    commonDateOptions: {},
    isExpandedInitially: false,
    displayExpandToggle: true,
    expandToggleLabel: ('Display to-date?'),
    toDateExpandedLabel: ('To date'),
    fromDateExpandedLabel: ('From date')
  }, props)
  return React.createElement(selectorComponentClass, fullProps)
}

function render (props = {}) {
  return renderSelector(Html5FromToDateSelectors, props)
}

test('sanity', () => {
  const component = shallow(render())
  expect(component.prop('className')).toBe('fieldwrapper')
})

test('Default item width', () => {
  const wrapper = shallow(render({label: 'Test'})).instance()
  const component = wrapper.getLineItemWidth()
  expect(component).toBe('fieldwrapper-line__item--width-small')
})

test('Extra small item width', () => {
  const wrapper = shallow(render({label: 'Test', commonDateOptions: {'lineItemWidth': 'xsmall'}})).instance()
  const component = wrapper.getLineItemWidth(wrapper.props.commonDateOptions.lineItemWidth)
  expect(component).toBe('fieldwrapper-line__item--width-xsmall')
})

test('Medium item width', () => {
  const wrapper = shallow(render({label: 'Test', commonDateOptions: {'lineItemWidth': 'medium'}})).instance()
  const component = wrapper.getLineItemWidth(wrapper.props.commonDateOptions.lineItemWidth)
  expect(component).toBe('fieldwrapper-line__item--width-medium')
})
