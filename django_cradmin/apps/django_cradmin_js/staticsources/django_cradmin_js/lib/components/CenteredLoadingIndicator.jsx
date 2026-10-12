import React from 'react'
import LoadingIndicator from './LoadingIndicator'


export default class CenteredLoadingIndicator extends LoadingIndicator {
  render () {
    return <div className={'text-center'}>
      <LoadingIndicator {...this.props} />
    </div>
  }
}
