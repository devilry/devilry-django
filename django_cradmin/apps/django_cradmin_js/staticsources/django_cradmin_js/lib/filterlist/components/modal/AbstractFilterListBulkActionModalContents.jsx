import React from 'react'
import PropTypes from 'prop-types'
import ModalContentsBase from '../../../components/ModalPortal/ModalContentsBase'
import * as gettext from 'ievv_jsbase/lib/gettext'
import LoadingIndicator from '../../../components/LoadingIndicator'

export default class AbstractFilterListBulkActionModalContents extends ModalContentsBase {
  static get propTypes () {
    return {
      ...super.propTypes,
      childExposedApi: PropTypes.any.isRequired,
      pageSize: PropTypes.number
    }
  }

  static get defaultProps () {
    return {
      ...super.defaultProps,
      pageSize: 1000
    }
  }

  constructor (props) {
    super(props)
    this.state = this.getInitialState()
    this.setupBoundFunctions()
  }

  componentDidMount () {
    this.loadIdsFromApi()
  }

  /* initialization functions */

  getInitialState () {
    return {
      idList: [],
      isLoadingIds: false
    }
  }

  setupBoundFunctions () {
    this.handleIdListResponse = this.handleIdListResponse.bind(this)
  }

  get loadingMessage () {
    return null
  }

  get message () {
    return null
  }

  /* view logic functions */

  handleIdListResponse (idList) {
    this.setState({
      idList: idList.map(idObject => idObject.id),
      isLoadingIds: false
    })
  }

  loadIdsFromApi () {
    this.setState({
      isLoadingIds: true
    })
    const request = this.props.childExposedApi.makeListItemsHttpRequest(null, true, false)
    request.urlParser.queryString.set('page_size', this.props.pageSize)
    request.getAllPaginationPages()
      .then(this.handleIdListResponse)
      .catch((error) => {
        console.error('Something went wrong while loading idList: ', error)
        throw error
      })
  }

  /* Render functions */

  renderLoadingIndicator () {
    return <div className={'text-center'} key={'loading-indicator'}>
      <LoadingIndicator
        message={this.loadingMessage}
        visibleMessage={!!this.loadingMessage}
      />
    </div>
  }

  renderBodyContents () {
    throw new Error('override renderBodyContents function')
  }

  renderBody () {
    return <React.Fragment>
      {this.message ? this.message : null}
      {this.state.isLoadingIds
        ? this.renderLoadingIndicator()
        : this.renderBodyContents()}
    </React.Fragment>
  }
}
