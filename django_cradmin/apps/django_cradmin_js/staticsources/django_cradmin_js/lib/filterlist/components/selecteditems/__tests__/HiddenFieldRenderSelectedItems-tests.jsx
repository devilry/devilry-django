/* eslint-env jest */
import { shallow } from 'enzyme'
import HiddenFieldRenderSelectedItems from '../HiddenFieldRenderSelectedItems'
import { renderSelectedItems } from '../testHelpers'

function render (props = {}) {
  return renderSelectedItems(
    HiddenFieldRenderSelectedItems, Object.assign({
      domIdPrefix: 'test',
      name: 'test'
    }, props))
}

test('no selected items - do not render anything', () => {
  const component = shallow(render())
  expect(component.type()).toBeNull()
})

test('single selected item renders something', () => {
  const component = shallow(render({
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.type()).not.toBeNull()
  expect(component.find('input').length).toBe(1)
})

test('single selected item sanity', () => {
  const component = shallow(render({
    name: 'myfield',
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.find('input').prop('name')).toEqual('myfield')
  expect(component.find('input').prop('type')).toEqual('hidden')
  expect(component.find('input').prop('defaultValue')).toBe(1)
})

test('multiple selected items sanity', () => {
  const component = shallow(render({
    name: 'myfield',
    selectedListItemsMap: new Map([
      [1, {}],
      [3, {}]
    ])
  }))
  expect(component.find('input').at(0).prop('defaultValue')).toBe(1)
  expect(component.find('input').at(1).prop('defaultValue')).toBe(3)
})

test('debug prop true', () => {
  const component = shallow(render({
    debug: true,
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.find('input').prop('type')).toEqual('text')
})
