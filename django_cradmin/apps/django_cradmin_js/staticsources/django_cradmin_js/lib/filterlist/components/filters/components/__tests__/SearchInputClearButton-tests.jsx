/* eslint-env jest */
import React from 'react'
import {shallow} from 'enzyme'
import SearchInputClearButton from '../SearchInputClearButton'

function render (props) {
  const fullProps = Object.assign({
    onClick: jest.fn(),
    onFocus: jest.fn(),
    onBlur: jest.fn()
  }, props)
  return React.createElement(SearchInputClearButton, fullProps)
}

function getIconComponent (component) {
  return component.find('span')
}

test('className', () => {
  const component = shallow(render())
  expect(component.prop('className')).toBe('searchinput__button')
})

test('icon className', () => {
  const component = shallow(render())
  expect(getIconComponent(component).prop('className')).toBe('searchinput__buttonicon cricon cricon--close')
})

test('title', () => {
  const component = shallow(render())
  expect(component.prop('title')).toBe('Clear search field')
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
