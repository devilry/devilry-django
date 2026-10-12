/**
 * General purpose DOM utilities.
 */
export default class DomUtilities {
  /**
   * Force focus on a DOM element.
   *
   * Works around timing issues with visibility and signals by
   * trying multiple times with a short interval between each attempt.
   *
   * @param {Element} domElement A DOM Element.
   * @param {Number} maxAttempts Number of attempts to make. The first attempt
   *    is made at once, and the other attempts is performed each
   *    ``pollIntervalMilliseconds`` until we get focus, or
   *    we have used up the attempts.
   * @param {Number} pollIntervalMilliseconds Numer of milliseconds
   *    between each attempt.
   */
  static forceFocus(domElement, maxAttempts=3, pollIntervalMilliseconds=80) {
    let _forceFocus = (attemptNumber) => {
      if(attemptNumber > maxAttempts) {
        // Give up - the element will probably not become visible
        // within a useful amount of time.
        return;
      }
      domElement.focus();
      if(window.document.activeElement != domElement) {
        setTimeout(() => {
          _forceFocus(attemptNumber + 1);
        }, pollIntervalMilliseconds);
      }
    };
    _forceFocus(0);
  }

  static show(element, displayStyle="block") {
    element.setAttribute('style', `display: ${displayStyle}`);
  }

  static hide(element) {
    element.setAttribute('style', `display: none`);
  }
}
