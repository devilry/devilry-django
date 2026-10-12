/* eslint-env jest */
import { shallow } from 'enzyme'
import SelectableListRenderSelectedItems from '../SelectableListRenderSelectedItems'
import { renderSelectedItems } from '../testHelpers'

function render (props = {}) {
  return renderSelectedItems(
    SelectableListRenderSelectedItems, Object.assign({
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
  expect(component.find('.selectable-list__item').length).toBe(1)
})

test('single selected item sanity', () => {
  const component = shallow(render({
    name: 'myfield',
    selectedListItemsMap: new Map([
      [1, {title: 'test title'}]
    ])
  }))
  expect(component.find('.selectable-list__itemcontent').text())
    .toEqual('test title')
})

test('multiple selected items sanity', () => {
  const component = shallow(render({
    name: 'myfield',
    selectedListItemsMap: new Map([
      [1, {title: 'test title 1'}],
      [2, {title: 'test title 2'}]
    ])
  }))
  expect(component.find('.selectable-list__itemcontent').at(0).text())
    .toEqual('test title 1')
  expect(component.find('.selectable-list__itemcontent').at(1).text())
    .toEqual('test title 2')
})
