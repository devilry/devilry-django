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
    this.apiurl = `/devilry_group/student/${this.config.group_id}/` +
      `feedbackfeed/${this.config.apiname}/` +
      `${this.config.content_object_id}`;
    this._onClick = this._onClick.bind(this);
    this.element.addEventListener('click', this._onClick);
    this.isFinished = false;
    this._requestStatusUpdate();
  }

  _requestStatusUpdate() {
    if(this.isLoading) {
      return;
    }
    new HttpJsonRequest(this.apiurl).get()
      .then((response) => {
        this._handleApiResponse(response, 'get');
      })
      .catch((error) => {
        throw error;
      });
  }

  _handleFinishedStatus(response) {
    console.log('FINISHED!!!!', response.bodydata);
    this.element.setAttribute('href', response.bodydata.download_link);
    this.isFinished = true;
  }

  _handleApiResponse(response, method) {
    console.log(method, response.bodydata);
    if(response.bodydata.status == 'not created') {
      return;  // Do nothing - wait for someone to click the button and start the processing
    }
    if(response.bodydata.status == 'not started' || response.bodydata.status == 'running') {
      window.setTimeout(() => {
        this._requestStatusUpdate();
      }, 2000);
    } else {
      this._handleFinishedStatus(response);
    }
  }

  _onClick(event) {
    if(this.isFinished) {
      return;
    }
    event.preventDefault();
    new HttpDjangoJsonRequest(this.apiurl).post()
      .then((response) => {
        this._handleApiResponse(response, 'post');
      })
      .catch((error) => {
        throw error;
      });
  }

  destroy() {
    this.element.removeEventListener('click', this._onClick);
  }
}
