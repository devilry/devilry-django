/* eslint-env jest */
import React from 'react'
import { shallow } from 'enzyme'
import CheckboxBooleanFilter from '../CheckboxBooleanFilter'
import { renderFilter } from '../testHelpers'
import { ChildExposedApiMock } from '../../filterlists/testHelpers'

function render (props = {}) {
  return renderFilter(CheckboxBooleanFilter, Object.assign({
    label: 'Test', domIdPrefix: 'test',
    selectedListItemsMap: new Map()
  }, props))
}

test('className', () => {
  const component = shallow(render())
  expect(component.prop('className')).toBe('checkbox checkbox--block')
})

test('Label', () => {
  const component = shallow(render({
    label: 'Test label'
  }))
  expect(component.text()).toEqual('Test label')
})

test('Change checkbox sets filter value from false to true', () => {
  const childExposedApi = new ChildExposedApiMock(true)
  const component = shallow(render({
    childExposedApi: childExposedApi,
    name: 'myfilter',
    value: false
  }))
  component.find('input').simulate('change')
  expect(childExposedApi.setFilterValue).toBeCalledWith('myfilter', true)
})

test('Change checkbox sets filter value from true to false', () => {
  const childExposedApi = new ChildExposedApiMock(true)
  const component = shallow(render({
    childExposedApi: childExposedApi,
    name: 'myfilter',
    value: true
  }))
  component.find('input').simulate('change')
  expect(childExposedApi.setFilterValue).toBeCalledWith('myfilter', false)
})
