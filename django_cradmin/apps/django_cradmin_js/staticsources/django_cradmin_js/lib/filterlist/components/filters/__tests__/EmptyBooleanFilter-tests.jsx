/* eslint-env jest */
import React from 'react'
import { shallow } from 'enzyme'
import EmptyBooleanFilter from '../EmptyBooleanFilter'
import { renderFilter } from '../testHelpers'
import { ChildExposedApiMock } from '../../filterlists/testHelpers'

function render (props = {}) {
  return renderFilter(EmptyBooleanFilter, Object.assign({
    domIdPrefix: 'test', ariaLabel: 'Test',
    selectedListItemsMap: new Map()
  }, props))
}

test('className', () => {
  const component = shallow(render())
  expect(component.prop('className')).toBe('select select--outlined')
})

test('aria-label', () => {
  const component = shallow(render({ariaLabel: 'Testlabel'}))
  expect(component.find('select').prop('aria-label')).toBe('Testlabel')
})

test('option values', () => {
  const component = shallow(render())
  expect(component.find('option').at(0).prop('value')).toBe('empty')
  expect(component.find('option').at(1).prop('value')).toBe('true')
  expect(component.find('option').at(2).prop('value')).toBe('false')
})

test('Select change sets filter value', () => {
  const childExposedApi = new ChildExposedApiMock(true)
  const component = shallow(render({
    childExposedApi: childExposedApi,
    name: 'myfilter',
    value: false
  }))
  component.find('select').simulate('change', {target: {value: 'true'}})
  expect(childExposedApi.setFilterValue).toBeCalledWith('myfilter', true)
})
