import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";

/**
 * Autosubmit form after a timeout widget.
 *
 * @example
 * <form action="/test" method="post">
 *     <p>
 *        Will autosubmit in
 *        <span data-ievv-jsbase-widget="cradmin-auto-submit-form-after-countdown"
 *              data-ievv-jsbase-widget-config='{
 *                "timeoutSeconds": 5
 *              }'>
 *            5
 *        </span>
 *        seconds!
 *     </p>
 * </form>
 */
export default class AutoSubmitFormAfterCountdownWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      timeoutSeconds: 5,
    }
  }

  constructor(element) {
    super(element);
    this._timeoutId = null;
    this._secondsRemaining = this.config.timeoutSeconds;
    this._form = this._findForm();
    this._onTick();
  }

  _findForm() {
    let element = this.element;
    while(element != null) {
      if(element.nodeName.toLowerCase() == 'form') {
        return element;
      }
      element = element.parentElement;
    }
    throw new Error('Could not find a FORM element within the parent hierarchy of this element.');
  }

  _onTick() {
      this._secondsRemaining --;
      this._updateCounter();
      if(this._secondsRemaining < 1) {
          this._form.submit();
      } else {
          this._timeoutId = window.setTimeout(() => {
              this._onTick();
          }, 1000);
      }
  }

  _updateCounter() {
    this.element.innerHTML = `${this._secondsRemaining}`;
  }

  destroy() {
    if(this._timeoutId != null) {
      window.clearTimeout(this._timeoutId);
    }
  }
}
