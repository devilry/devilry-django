/* eslint-env jest */
import { shallow } from 'enzyme'
import LoadMorePaginator from '../LoadMorePaginator'
import { ChildExposedApiMock } from '../../filterlists/testHelpers'
import { renderPaginator } from '../testHelpers'

function makeChildExposedApiMock (hasNextPaginationPage) {
  const childExposedApi = new ChildExposedApiMock()
  childExposedApi.hasNextPaginationPage.mockReturnValue(hasNextPaginationPage)
  return childExposedApi
}

function render (props) {
  return renderPaginator(LoadMorePaginator, {domIdPrefix: 'test', ...props})
}

test('hasNextPaginationPage() is false', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(false)
  }))
  expect(component.type()).toBeNull()
})

test('hasNextPaginationPage() is true', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(true)
  }))
  expect(component.type()).not.toBeNull()
})

test('Default className', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(true)
  }))
  expect(component.prop('className')).toBe('button')
})

test('Custom bemBlock', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(true),
    bemBlock: 'myblock'
  }))
  expect(component.prop('className')).toBe('myblock')
})

test('Custom bemVariants', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(true),
    bemVariants: ['large', 'dark']
  }))
  expect(component.prop('className')).toBe('button button--large button--dark')
})

test('Default label', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(true)
  }))
  expect(component.text()).toEqual('Load more')
})

test('Custom label', () => {
  const component = shallow(render({
    childExposedApi: makeChildExposedApiMock(true),
    label: 'My Label'
  }))
  expect(component.text()).toEqual('My Label')
})

test('Click button calls loadMoreItemsFromApi', () => {
  const childExposedApi = makeChildExposedApiMock(true)
  const component = shallow(render({
    childExposedApi: childExposedApi
  }))
  component.at(0).simulate('click', {preventDefault: jest.fn()})
  expect(childExposedApi.loadMoreItemsFromApi).toBeCalled()
})
