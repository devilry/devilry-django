import ThreeColumnLayout from './ThreeColumnLayout'

export default class ThreeColumnNoLoadingIndicatorLayout extends ThreeColumnLayout {
  renderLoadingIndicator () {
    return null
  }
}
