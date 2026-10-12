/* eslint-env jest */
import React from 'react'
import { shallow } from 'enzyme'
import TightLabeledEmptyBooleanFilter from '../TightLabeledEmptyBooleanFilter'
import { renderFilter } from '../testHelpers'
import { ChildExposedApiMock } from '../../filterlists/testHelpers'

function render (props = {}) {
  return renderFilter(TightLabeledEmptyBooleanFilter, Object.assign({
    label: 'Test', domIdPrefix: 'test',
    selectedListItemsMap: new Map()
  }, props))
}

test('className', () => {
  const component = shallow(render())
  expect(component.find('label').prop('className')).toBe('select select--outlined select--size-xsmall select--width-xxsmall')
})

test('wrapperClassName', () => {
  const component = shallow(render())
  expect(component.prop('className')).toBe('paragraph paragraph--xtight')
})

test('label', () => {
  const component = shallow(render({label: 'Testlabel'}))
  expect(component.find('span').text()).toBe('Testlabel')
})

test('aria-label defaults to label', () => {
  const component = shallow(render({label: 'Testlabel'}))
  expect(component.find('select').prop('aria-label')).toBe('Testlabel')
})

test('custom aria-label', () => {
  const component = shallow(render({ariaLabel: 'Test Aria label'}))
  expect(component.find('select').prop('aria-label')).toBe('Test Aria label')
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
