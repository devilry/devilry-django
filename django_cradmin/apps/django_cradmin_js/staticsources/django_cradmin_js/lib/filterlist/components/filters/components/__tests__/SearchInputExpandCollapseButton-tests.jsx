/* eslint-env jest */
import React from 'react'
import {shallow} from 'enzyme'
import SearchInputExpandCollapseButton from '../SearchInputExpandCollapseButton'

function render (props) {
  const fullProps = Object.assign({
    onClick: jest.fn(),
    onFocus: jest.fn(),
    onBlur: jest.fn(),
    isExpanded: false
  }, props)
  return React.createElement(SearchInputExpandCollapseButton, fullProps)
}

function getIconComponent (component) {
  return component.find('span')
}

test('className', () => {
  const component = shallow(render())
  expect(component.prop('className')).toBe('searchinput__button')
})

test('icon className - not expanded', () => {
  const component = shallow(render({isExpanded: false}))
  expect(getIconComponent(component).prop('className')).toBe('searchinput__buttonicon cricon cricon--chevron-down')
})

test('icon className - expanded', () => {
  const component = shallow(render({isExpanded: true}))
  expect(getIconComponent(component).prop('className')).toBe('searchinput__buttonicon cricon cricon--chevron-up')
})

test('title - not expanded', () => {
  const component = shallow(render({isExpanded: false}))
  expect(component.prop('title')).toBe('Expand')
})

test('title - not expanded', () => {
  const component = shallow(render({isExpanded: true}))
  expect(component.prop('title')).toBe('Collapse')
})

test('onClick', () => {
  const onClick = jest.fn()
  const component = shallow(render({onClick: onClick}))
  component.simulate('click')
  expect(onClick).toBeCalled()
})

test('onFocus', () => {
  const onFocus = jest.fn()
  const component = shallow(render({onFocus: onFocus}))
  component.simulate('focus')
  expect(onFocus).toBeCalled()
})

test('onBlur', () => {
  const onBlur = jest.fn()
  const component = shallow(render({onBlur: onBlur}))
  component.simulate('blur')
  expect(onBlur).toBeCalled()
})
