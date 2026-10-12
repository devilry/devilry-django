/* eslint-env jest */
import {mount, shallow} from 'enzyme'
import { renderFilter } from '../testHelpers'
import SearchFilter from '../SearchFilter'
import {ChildExposedApiMock} from '../../filterlists/testHelpers'
import SearchInputClearButton from '../components/SearchInputClearButton'

function render (props = {}) {
  return renderFilter(SearchFilter, props)
}

describe('SearchFilter', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  const getClearButtonComponent = (component) => {
    return component.find(SearchInputClearButton)
  }

  const getSearchInputComponent = (component) => {
    return component.find('input')
  }

  const getFieldWrapperComponent = (component) => {
    return component.find('.searchinput')
  }

  test('label className', () => {
    const component = shallow(render())
    expect(component.find('label').prop('className')).toBe('label')
  })

  test('has label prop', () => {
    const component = shallow(render({
      label: 'Test label'
    }))
    expect(component.find('.test-label-text').exists()).toBe(true)
    expect(component.find('.test-label-text').text()).toEqual('Test label')
  })

  test('fieldWrapper className default', () => {
    const component = shallow(render())
    expect(getFieldWrapperComponent(component).prop('className')).toEqual(
      'searchinput searchinput--outlined')
  })

  test('fieldWrapper className custom fieldWrapperBemVariants', () => {
    const component = shallow(render({
      fieldWrapperBemVariants: ['stuff', 'things']
    }))
    expect(getFieldWrapperComponent(component).prop('className')).toEqual(
      'searchinput searchinput--stuff searchinput--things')
  })

  test('clearButton is rendered', () => {
    const component = shallow(render())
    expect(getClearButtonComponent(component).exists()).toBe(true)
  })

  test('clearButton click clears filter value', () => {
    const childExposedApi = new ChildExposedApiMock(true)
    const component = mount(render({
      name: 'search',
      value: 'Test',
      childExposedApi: childExposedApi
    }))
    getClearButtonComponent(component).simulate('click')
    expect(childExposedApi.setFilterValue).toBeCalledWith('search', '')
  })

  test('searchInput is rendered', () => {
    const component = shallow(render())
    expect(getSearchInputComponent(component).exists()).toBe(true)
  })

  test('searchInput className', () => {
    const component = shallow(render())
    expect(getSearchInputComponent(component).prop('className')).toEqual(
      'searchinput__input')
  })

  test('searchInput default value', () => {
    const component = shallow(render())
    expect(getSearchInputComponent(component).prop('value')).toEqual('')
  })

  test('searchInput custom value', () => {
    const component = shallow(render({
      value: 'my search'
    }))
    expect(getSearchInputComponent(component).prop('value')).toEqual(
      'my search')
  })

  test('searchInput change event calls API', () => {
    const childExposedApi = new ChildExposedApiMock(true)
    const component = mount(render({
      name: 'search',
      childExposedApi: childExposedApi
    }))
    getSearchInputComponent(component).simulate('change', {
      target: {value: 'testsearch'}
    })
    expect(childExposedApi.setFilterValue).toBeCalledWith('search', 'testsearch')
  })

  test('searchInput change event empty value calls API', () => {
    const childExposedApi = new ChildExposedApiMock(true)
    const component = mount(render({
      name: 'search',
      childExposedApi: childExposedApi
    }))
    getSearchInputComponent(component).simulate('change', {
      target: {value: ''}
    })
    expect(childExposedApi.setFilterValue).toBeCalledWith('search', '')
  })

  test('searchInput placeholder string', () => {
    const component = mount(render({
      placeholder: 'search...'
    }))
    expect(getSearchInputComponent(component).prop('placeholder')).toEqual(
      'search...')
  })

  test('searchInput placeholder array initial', () => {
    const component = mount(render({
      placeholder: ['people', 'animals']
    }))
    expect(getSearchInputComponent(component).prop('placeholder')).toEqual(
      'people')
  })

  // NOTE: Test need to be rewritten to work with latest enzyme
  // test('searchInput placeholder array rotate', () => {
  //   const component = shallow(render({
  //     placeholder: ['people', 'animals']
  //   }))
  //   expect(getSearchInputComponent(component).prop('placeholder')).toEqual(
  //     'people')
  //   jest.runOnlyPendingTimers()
  //   component.update()
  //   expect(getSearchInputComponent(component).prop('placeholder')).toEqual(
  //     'animals')
  // })
})
