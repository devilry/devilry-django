import AbstractWidget from "ievv_jsbase/widget/AbstractWidget";
import HttpDjangoJsonRequest from "ievv_jsbase/http/HttpDjangoJsonRequest";
import HttpJsonRequest from "ievv_jsbase/http/HttpJsonRequest";

/**
 * Run ``window.print()`` on click widget.
 *
 * @example
 * <button type="button" data-ievv-jsbase-widget="cradmin-print-on-click">
 *     Print
 * </button>
 */
export default class DownloadCompressedArchiveWidget extends AbstractWidget {
  constructor(element) {
    super(element);
    this.status = null;
    this.cssClassPrefix = 'devilry-batchprocessed-download';
    this.statuses = [
      'none',
      'not-created',
      'not-started',
      'running',
      'finished'];
    this._onStartSignal = this._onStartSignal.bind(this);
    this.logger = new window.ievv_jsbase_core.LoggerSingleton().getLogger(
      'devilry.DownloadCompressedArchiveWidget');
    this.signalHandler = new window.ievv_jsbase_core.SignalHandlerSingleton();
    this.processingStartedTime = null;
    this.signalHandler.addReceiver(
      `${this.config.signalNameSpace}.Start`,
      `${this.config.signalNameSpace}.MainReceiver`,
      this._onStartSignal);

    // this.onClickTime = null;
    this._requestStatusUpdate();
  }

  _updateCssClassesFromStatus() {
    this.element.classList.remove(`${this.cssClassPrefix}--finished-within-same-session`);
    for(let status of this.statuses) {
      this.element.classList.remove(`${this.cssClassPrefix}--${status}`);
    }
    this.element.classList.add(`${this.cssClassPrefix}--${this.status}`);
    if(this.status == 'finished' && this.processingStartedTime != null) {
      this.element.classList.add(`${this.cssClassPrefix}--finished-within-same-session`);
    }
  }

  _requestStatusUpdate() {
    if(this.isLoading) {
      return;
    }
    new HttpJsonRequest(this.config.apiurl).get()
      .then((response) => {
        this._handleApiResponse(response, 'GET');
      })
      .catch((error) => {
        throw error;
      });
  }

  _handleFinishedStatus(response) {
    this.logger.debug('Download finished processing', response.bodydata);
    this.element.setAttribute('href', response.bodydata.download_link);
    // if(this.onClickTime != null) {
    //   let millisecondsSinceLastClick = new Date() - this.onClickTime;
    //   console.log('millisecondsSinceLastClick:', millisecondsSinceLastClick);
    //   if(millisecondsSinceLastClick < 4000) {
    //     window.location.href = response.bodydata.download_link;
    //   }
    // }
    this.signalHandler.send(`${this.config.signalNameSpace}.Finished`,
      response.bodydata);
  }

  _handleApiResponse(response, method) {
    this.logger.debug(`${method} ${this.config.apiurl}:`, response.bodydata);
    this.status = response.bodydata.status;
    this._updateCssClassesFromStatus();
    if(this.status == 'not-created') {
      return;  // Do nothing - wait for someone to click the button and start the processing
    }
    if(this.status == 'not-started' || this.status == 'running') {
      window.setTimeout(() => {
        this._requestStatusUpdate();
      }, 2000);
    } else if(this.status == 'finished') {
      this._handleFinishedStatus(response);
    } else {
      throw new Error(`Invalid status: ${this.status}`);
    }
  }

  _onStartSignal() {
    this.logger.debug('Start signal received');
    if(this.status == 'finished') {
      return;
    }
    this.processingStartedTime = new Date();
    new HttpDjangoJsonRequest(this.config.apiurl).post()
      .then((response) => {
        this._handleApiResponse(response, 'POST');
      })
      .catch((error) => {
        throw error;
      });
  }

  destroy() {
    this.signalHandler.removeAllSignalsFromReceiver(
      `${this.config.signalNameSpace}.MainReceiver`);
  }
}
