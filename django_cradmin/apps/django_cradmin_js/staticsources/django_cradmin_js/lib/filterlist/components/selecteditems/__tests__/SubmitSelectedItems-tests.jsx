/* eslint-env jest */
import { shallow, mount } from 'enzyme'
import SubmitSelectedItems from '../SubmitSelectedItems'
import { renderSelectedItems } from '../testHelpers'

function render (props = {}) {
  return renderSelectedItems(
    SubmitSelectedItems, Object.assign({
      hiddenFieldName: 'test',
      formAction: 'testaction'
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
  expect(component.find('button').length).toBe(1)
})

test('label', () => {
  const component = shallow(render({
    label: 'test label',
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.find('button').text())
    .toEqual('test label')
})

test('type', () => {
  const component = shallow(render({
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.find('button').prop('type'))
    .toEqual('submit')
})

test('single selected item hidden fields sanity', () => {
  const component = mount(render({
    hiddenFieldName: 'myfield',
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.find('input').prop('name')).toEqual('myfield')
  expect(component.find('input').prop('type')).toEqual('hidden')
  expect(component.find('input').prop('defaultValue')).toBe(1)
})

test('multiple selected items sanity', () => {
  const component = mount(render({
    hiddenFieldName: 'myfield',
    selectedListItemsMap: new Map([
      [1, {}],
      [3, {}]
    ])
  }))
  expect(component.find('input').at(0).prop('defaultValue')).toBe(1)
  expect(component.find('input').at(1).prop('defaultValue')).toBe(3)
})

test('debug prop true', () => {
  const component = mount(render({
    debug: true,
    selectedListItemsMap: new Map([
      [1, {}]
    ])
  }))
  expect(component.find('input').prop('type')).toEqual('text')
})

test('extraHiddenFields', () => {
  const component = mount(render({
    debug: true,
    selectedListItemsMap: new Map([
      [1, {}]
    ]),
    extraHiddenFields: {
      myExtraField: 1
    }
  }))
  expect(component.find('input').at(1).prop('type')).toEqual('hidden')
  expect(component.find('input').at(1).prop('name')).toEqual('myExtraField')
  expect(component.find('input').at(1).prop('defaultValue')).toEqual(1)
})
