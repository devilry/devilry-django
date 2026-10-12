(function() {
  angular.module('cradminLegacy.acemarkdown', []).directive('cradminLegacyAcemarkdown', function() {
    return {
      restrict: 'A',
      transclude: true,
      templateUrl: 'acemarkdown/acemarkdown.tpl.html',
      scope: {
        'config': '=cradminLegacyAcemarkdown'
      },
      controller: function($scope) {
        this.setEditor = function(editorScope) {
          $scope.editor = editorScope;
          $scope.editor.aceEditor.on('focus', function() {
            return $scope.element.addClass('cradmin-focus');
          });
          return $scope.editor.aceEditor.on('blur', function() {
            return $scope.element.removeClass('cradmin-focus');
          });
        };
        this.setTextarea = function(textareaScope) {
          $scope.textarea = textareaScope;
          return $scope.editor.setValue($scope.textarea.getValue());
        };
        this.setTextAreaValue = function(value) {
          return $scope.textarea.setValue(value);
        };
        this.focusOnEditor = function() {
          return $scope.editor.focus();
        };
        this.editorSurroundSelectionWith = function(options) {
          return $scope.editor.surroundSelectionWith(options);
        };
      },
      link: function(scope, element) {
        var theme;
        scope.element = element;
        if (scope.config.showTextarea) {
          element.addClass('cradmin-acemarkdown-textareavisible');
        }
        theme = scope.config.theme;
        if (!theme) {
          theme = 'tomorrow';
        }
        return scope.editor.setTheme(theme);
      }
    };
  }).directive('cradminLegacyAcemarkdownEditor', function() {
    return {
      require: '^cradminLegacyAcemarkdown',
      restrict: 'A',
      template: '<div></div>',
      scope: {},
      controller: function($scope) {
        /*
        Set the value of the ace editor.
        
        Used by the cradminLegacyAcemarkdownTextarea to set the
        initial value of the editor.
        */

        $scope.setValue = function(value) {
          return $scope.aceEditor.getSession().setValue(value);
        };
        /*
        Focus on the ACE editor. Called when a user focuses
        on the cradminLegacyAcemarkdownTextarea.
        */

        $scope.focus = function() {
          return $scope.aceEditor.focus();
        };
        /*
        Set the theme for the ACE editor.
        */

        $scope.setTheme = function(theme) {
          return $scope.aceEditor.setTheme("ace/theme/" + theme);
        };
        /*
        Triggered each time the aceEditor value changes.
        Updates the textarea with the current value of the
        ace editor.
        */

        $scope.onChange = function() {
          var value;
          value = $scope.aceEditor.getSession().getValue();
          return $scope.markdownCtrl.setTextAreaValue(value);
        };
        $scope.surroundSelectionWith = function(options) {
          var emptyText, newlines, noSelection, post, pre, selectedText, selectionRange;
          pre = options.pre, post = options.post, emptyText = options.emptyText;
          if (emptyText == null) {
            emptyText = '';
          }
          if (pre == null) {
            pre = '';
          }
          if (post == null) {
            post = '';
          }
          selectionRange = $scope.aceEditor.getSelectionRange();
          selectedText = $scope.aceEditor.session.getTextRange(selectionRange);
          noSelection = selectedText === '';
          if (noSelection) {
            selectedText = emptyText;
          }
          $scope.aceEditor.insert("" + pre + selectedText + post);
          if (noSelection) {
            newlines = pre.split('\n').length - 1;
            selectionRange.start.row += newlines;
            selectionRange.end.row = selectionRange.start.row;
            selectionRange.start.column += pre.length - newlines;
            selectionRange.end.column += pre.length - newlines + emptyText.length;
            $scope.aceEditor.getSelection().setSelectionRange(selectionRange);
          }
          return $scope.aceEditor.focus();
        };
      },
      link: function(scope, element, attrs, markdownCtrl) {
        var session;
        scope.markdownCtrl = markdownCtrl;
        scope.aceEditor = ace.edit(element[0]);
        scope.aceEditor.setHighlightActiveLine(false);
        scope.aceEditor.setShowPrintMargin(false);
        scope.aceEditor.commands.removeCommand(scope.aceEditor.commands.byName.indent);
        scope.aceEditor.commands.removeCommand(scope.aceEditor.commands.byName.outdent);
        scope.aceEditor.renderer.setShowGutter(false);
        session = scope.aceEditor.getSession();
        session.setMode("ace/mode/markdown");
        session.setUseWrapMode(true);
        session.setUseSoftTabs(true);
        scope.aceEditor.on('change', function() {
          return scope.onChange();
        });
        markdownCtrl.setEditor(scope);
      }
    };
  }).directive('cradminLegacyAcemarkdownTool', function() {
    return {
      require: '^cradminLegacyAcemarkdown',
      restrict: 'A',
      scope: {
        'config': '=cradminLegacyAcemarkdownTool'
      },
      link: function(scope, element, attr, markdownCtrl) {
        element.on('click', function(e) {
          e.preventDefault();
          return markdownCtrl.editorSurroundSelectionWith(scope.config);
        });
      }
    };
  }).directive('cradminLegacyAcemarkdownLink', [
    '$window', function($window) {
      return {
        require: '^cradminLegacyAcemarkdown',
        restrict: 'A',
        scope: {
          'config': '=cradminLegacyAcemarkdownLink'
        },
        link: function(scope, element, attr, markdownCtrl) {
          element.on('click', function(e) {
            var url;
            e.preventDefault();
            url = $window.prompt(scope.config.help, '');
            if (url != null) {
              return markdownCtrl.editorSurroundSelectionWith({
                pre: '[',
                post: "](" + url + ")",
                emptyText: scope.config.emptyText
              });
            }
          });
        }
      };
    }
  ]).directive('cradminLegacyAcemarkdownTextarea', function() {
    return {
      require: '^cradminLegacyAcemarkdown',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        /*
        Get the current value of the textarea.
        
        Used on load to initialize the ACE editor with the current
        value of the textarea.
        */

        $scope.getValue = function() {
          return $scope.textarea.val();
        };
        /*
        Set the value of the textarea. Does nothing if the
        value is the same as the current value.
        
        Used by the cradminLegacyAcemarkdownEditor to update the
        value of the textarea for each change in the editor.
        */

        $scope.setValue = function(value) {
          if ($scope.getValue() !== value) {
            return $scope.textarea.val(value);
          }
        };
      },
      link: function(scope, element, attrs, markdownCtrl) {
        scope.textarea = element;
        scope.textarea.addClass('cradmin-acemarkdowntextarea');
        scope.textarea.on('focus', function() {
          return markdownCtrl.focusOnEditor();
        });
        markdownCtrl.setTextarea(scope);
      }
    };
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.backgroundreplace_element.directives', []).directive('cradminLegacyBgReplaceElementOnPageLoad', [
    '$window', 'cradminLegacyBgReplaceElement', function($window, cradminLegacyBgReplaceElement) {
      /*
      This is just an example/debugging directive for cradminLegacyBgReplaceElement.
      */

      return {
        restrict: 'A',
        controller: function($scope, $element) {},
        link: function($scope, $element, attributes) {
          var remoteElementSelector, remoteUrl;
          remoteElementSelector = attributes.cradminLegacyRemoteElementSelector;
          remoteUrl = attributes.cradminLegacyRemoteUrl;
          if (remoteElementSelector == null) {
            if (typeof console !== "undefined" && console !== null) {
              if (typeof console.error === "function") {
                console.error("You must include the 'cradmin-legacy-remote-element-id' attribute.");
              }
            }
          }
          if (remoteUrl == null) {
            if (typeof console !== "undefined" && console !== null) {
              if (typeof console.error === "function") {
                console.error("You must include the 'cradmin-legacy-remote-url' attribute.");
              }
            }
          }
          angular.element(document).ready(function() {
            console.log('load', remoteUrl, remoteElementSelector);
            return cradminLegacyBgReplaceElement.load({
              parameters: {
                method: 'GET',
                url: remoteUrl
              },
              remoteElementSelector: remoteElementSelector,
              targetElement: $element,
              $scope: $scope,
              replace: true,
              onHttpError: function(response) {
                return console.log('ERROR', response);
              },
              onSuccess: function() {
                return console.log('Success!');
              },
              onFinish: function() {
                return console.log('Finish!');
              }
            });
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  angular.module('cradminLegacy.backgroundreplace_element.providers', []).provider('cradminLegacyBgReplaceElement', function() {
    /*
    Makes a request to a an URL, and replaces or extends a DOM element
    on the current page with the same DOM element within
    the requested URL.
    
    Can be used for many things, such as:
    
    - Infinite scroll (append content from ``?page=<pagenumber>``).
    - Live filtering (replace the filtered list when a filter changes).
    */

    var BgReplace;
    BgReplace = (function() {
      function BgReplace($http, $compile, $rootScope) {
        this.updateTargetElement = __bind(this.updateTargetElement, this);
        this.http = $http;
        this.compile = $compile;
        this.rootScope = $rootScope;
      }

      BgReplace.prototype.loadUrlAndExtractRemoteElementHtml = function(options, onSuccess) {
        var parsedUrl, url;
        url = options.parameters.url;
        parsedUrl = URI(url);
        parsedUrl.setSearch("cradmin-bgreplaced", 'true');
        options.parameters.url = parsedUrl.toString();
        return this.http(options.parameters).then(function(response) {
          var $remoteHtmlDocument, html, remoteElement, remoteElementInnerHtml;
          html = response.data;
          $remoteHtmlDocument = angular.element(html);
          remoteElement = $remoteHtmlDocument.find(options.remoteElementSelector);
          remoteElementInnerHtml = remoteElement.html();
          return onSuccess(remoteElementInnerHtml, $remoteHtmlDocument);
        }, function(response) {
          if (options.onFinish != null) {
            options.onFinish();
          }
          if (options.onHttpError != null) {
            return options.onHttpError(response);
          } else {
            return typeof console !== "undefined" && console !== null ? typeof console.error === "function" ? console.error("Failed to load", options.parameters) : void 0 : void 0;
          }
        });
      };

      BgReplace.prototype.__removeElement = function($element) {
        var $childElement, childDomElement, isolatedScope, _i, _len, _ref;
        _ref = $element.children();
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          childDomElement = _ref[_i];
          $childElement = angular.element(childDomElement);
          this.__removeElement($childElement);
        }
        isolatedScope = $element.isolateScope();
        if (isolatedScope != null) {
          isolatedScope.$destroy();
        }
        return $element.remove();
      };

      BgReplace.prototype.__removeAllChildren = function($element) {
        var $childElement, childDomElement, _i, _len, _ref, _results;
        _ref = $element.children();
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          childDomElement = _ref[_i];
          $childElement = angular.element(childDomElement);
          _results.push(this.__removeElement($childElement));
        }
        return _results;
      };

      BgReplace.prototype.updateTargetElement = function(options, remoteElementInnerHtml, $remoteHtmlDocument) {
        var $compile, linkingFunction, loadedElement;
        if (options.replace) {
          this.__removeAllChildren(options.targetElement);
        }
        $compile = this.compile;
        linkingFunction = $compile(remoteElementInnerHtml);
        loadedElement = linkingFunction(options.$scope);
        options.targetElement.append(loadedElement);
        if (options.onFinish != null) {
          options.onFinish();
        }
        if (options.onSuccess) {
          options.onSuccess($remoteHtmlDocument);
        }
        return this.rootScope.$broadcast('cradminLegacyBgReplaceElementEvent', options);
      };

      BgReplace.prototype.load = function(options) {
        var me;
        me = this;
        return this.loadUrlAndExtractRemoteElementHtml(options, function(remoteElementInnerHtml, $remoteHtmlDocument) {
          return me.updateTargetElement(options, remoteElementInnerHtml, $remoteHtmlDocument);
        });
      };

      return BgReplace;

    })();
    this.$get = [
      '$http', '$compile', '$rootScope', function($http, $compile, $rootScope) {
        return new BgReplace($http, $compile, $rootScope);
      }
    ];
    return this;
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.bulkfileupload', ['angularFileUpload', 'ngCookies']).provider('cradminBulkfileuploadCoordinator', function() {
    var FileUploadCoordinator;
    FileUploadCoordinator = (function() {
      function FileUploadCoordinator($window) {
        this.hiddenfieldnameToScopeMap = {};
        this.window = $window;
      }

      FileUploadCoordinator.prototype.register = function(hiddenfieldname, scope) {
        var existingScope;
        existingScope = this.hiddenfieldnameToScopeMap[hiddenfieldname];
        if (existingScope != null) {
          console.error('Trying to register a fieldname that is already registered with ' + 'cradminBulkfileuploadCoordinator. Fieldname:', hiddenfieldname);
          return;
        }
        return this.hiddenfieldnameToScopeMap[hiddenfieldname] = scope;
      };

      FileUploadCoordinator.prototype.unregister = function(hiddenfieldname) {
        var scope;
        scope = this.hiddenfieldnameToScopeMap[hiddenfieldname];
        if (scope == null) {
          console.error('Trying to unregister a field that is not registered with ' + 'cradminBulkfileuploadCoordinator. Fieldname:', hiddenfieldname);
        }
        return this.hiddenfieldnameToScopeMap[hiddenfieldname] = void 0;
      };

      FileUploadCoordinator.prototype._getScope = function(hiddenfieldname) {
        var scope;
        scope = this.hiddenfieldnameToScopeMap[hiddenfieldname];
        if (scope == null) {
          console.error('Trying to get a field that is not registered with ' + 'cradminBulkfileuploadCoordinator. Fieldname:', hiddenfieldname);
        }
        return scope;
      };

      FileUploadCoordinator.prototype.showOverlayForm = function(hiddenfieldname) {
        var scope;
        scope = this._getScope(hiddenfieldname);
        return scope.formController.showOverlay();
      };

      return FileUploadCoordinator;

    })();
    this.$get = [
      '$window', function($window) {
        return new FileUploadCoordinator($window);
      }
    ];
    return this;
  }).factory('cradminBulkfileupload', function() {
    var FileInfo;
    FileInfo = (function() {
      function FileInfo(options) {
        this.file = options.file;
        this.autosubmit = options.autosubmit;
        this.i18nStrings = options.i18nStrings;
        this.temporaryfileid = options.temporaryfileid;
        if (this.file != null) {
          this.name = this.file.name;
        } else {
          this.name = options.name;
        }
        this.isRemoving = false;
        this.percent = options.percent;
        if (options.finished) {
          this.finished = true;
        } else {
          this.finished = false;
        }
        if (options.hasErrors) {
          this.hasErrors = true;
        } else {
          this.hasErrors = false;
        }
        this.errors = options.errors;
      }

      FileInfo.prototype.markAsIsRemoving = function() {
        return this.isRemoving = true;
      };

      FileInfo.prototype.markAsIsNotRemoving = function() {
        return this.isRemoving = false;
      };

      FileInfo.prototype.updatePercent = function(percent) {
        return this.percent = percent;
      };

      FileInfo.prototype.finish = function(temporaryfile, singlemode) {
        var index;
        this.finished = true;
        index = 0;
        this.file = void 0;
        this.temporaryfileid = temporaryfile.id;
        return this.name = temporaryfile.filename;
      };

      FileInfo.prototype.setErrors = function(errors) {
        this.hasErrors = true;
        return this.errors = errors;
      };

      FileInfo.prototype.indexOf = function(fileInfo) {
        return this.files.indexOf(fileInfo);
      };

      FileInfo.prototype.remove = function(index) {
        return this.files.splice(index, 1);
      };

      return FileInfo;

    })();
    return {
      createFileInfo: function(options) {
        return new FileInfo(options);
      }
    };
  }).directive('cradminLegacyBulkfileuploadForm', [
    function() {
      /*
      A form containing ``cradmin-legacy-bulkfileupload`` fields
      must use this directive.
      */

      return {
        restrict: 'AE',
        scope: {},
        controller: function($scope) {
          $scope._inProgressCounter = 0;
          $scope._submitButtonScopes = [];
          $scope._setSubmitButtonsInProgress = function() {
            var buttonScope, _i, _len, _ref, _results;
            _ref = $scope._submitButtonScopes;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              buttonScope = _ref[_i];
              _results.push(buttonScope.setNotInProgress());
            }
            return _results;
          };
          $scope._setSubmitButtonsNotInProgress = function() {
            var buttonScope, _i, _len, _ref, _results;
            _ref = $scope._submitButtonScopes;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              buttonScope = _ref[_i];
              _results.push(buttonScope.setInProgress());
            }
            return _results;
          };
          this.addInProgress = function() {
            $scope._inProgressCounter += 1;
            if ($scope._inProgressCounter === 1) {
              return $scope._setSubmitButtonsInProgress();
            }
          };
          this.removeInProgress = function() {
            if ($scope._inProgressCounter === 0) {
              throw new Error("It should not be possible to get _inProgressCounter below 0");
            }
            $scope._inProgressCounter -= 1;
            if ($scope._inProgressCounter === 0) {
              return $scope._setSubmitButtonsNotInProgress();
            }
          };
          this.addSubmitButtonScope = function(submitButtonScope) {
            return $scope._submitButtonScopes.push(submitButtonScope);
          };
          this.addSubmitButtonScope = function(submitButtonScope) {
            return $scope._submitButtonScopes.push(submitButtonScope);
          };
          this.registerOverlayControls = function(overlayControlsScope) {
            return $scope._overlayControlsScope = overlayControlsScope;
          };
          this.registerOverlayUploadingmessageScope = function(overlayUploadingmessageScope) {
            return $scope._overlayUploadingmessageScope = overlayUploadingmessageScope;
          };
          this.submitForm = function() {
            if ($scope.overlay) {
              $scope._overlayUploadingmessageScope.onSubmitForm();
            }
            return $scope.element.submit();
          };
          $scope._showOverlay = function() {
            if ($scope.overlay) {
              return $scope.wrapperElement.addClass('cradmin-legacy-bulkfileupload-overlaywrapper-show');
            } else {
              throw new Error('Can only show the overlay if the form has the ' + 'cradmin-legacy-bulkfileupload-form-overlay="true" attribute.');
            }
          };
          this.showOverlay = function() {
            return $scope._showOverlay();
          };
          this.hideOverlay = function() {
            if ($scope.overlay) {
              return $scope.wrapperElement.removeClass('cradmin-legacy-bulkfileupload-overlaywrapper-show');
            } else {
              throw new Error('Can only hide the overlay if the form has the ' + 'cradmin-legacy-bulkfileupload-form-overlay="true" attribute.');
            }
          };
        },
        link: function($scope, element, attr, uploadController) {
          var body;
          $scope.overlay = attr.cradminLegacyBulkfileuploadFormOverlay === 'true';
          $scope.preventWindowDragdrop = attr.cradminLegacyBulkfileuploadFormPreventWindowDragdrop !== 'false';
          $scope.openOverlayOnWindowDragdrop = attr.cradminLegacyBulkfileuploadFormOpenOverlayOnWindowDragdrop === 'true';
          $scope.element = element;
          if ($scope.overlay) {
            element.addClass('cradmin-legacy-bulkfileupload-form-overlay');
            body = angular.element('body');
            $scope.wrapperElement = angular.element('<div></div>');
            $scope.wrapperElement.addClass('cradmin-legacy-bulkfileupload-overlaywrapper');
            $scope.wrapperElement.appendTo(body);
            element.appendTo($scope.wrapperElement);
            $scope._overlayControlsScope.element.appendTo($scope.wrapperElement);
            if (element.find('.has-error').length > 0) {
              $scope._showOverlay();
            }
            if ($scope.preventWindowDragdrop) {
              window.addEventListener("dragover", function(e) {
                return e.preventDefault();
              }, false);
              window.addEventListener("drop", function(e) {
                return e.preventDefault();
              }, false);
            }
            window.addEventListener("dragover", function(e) {
              e.preventDefault();
              $scope.wrapperElement.addClass('cradmin-legacy-bulkfileupload-overlaywrapper-window-dragover');
              if ($scope.openOverlayOnWindowDragdrop) {
                return $scope._showOverlay();
              }
            }, false);
            window.addEventListener("drop", function(e) {
              e.preventDefault();
              return $scope.wrapperElement.removeClass('cradmin-legacy-bulkfileupload-overlaywrapper-window-dragover');
            }, false);
            angular.element('body').on('mouseleave', function(e) {
              return $scope.wrapperElement.removeClass('cradmin-legacy-bulkfileupload-overlaywrapper-window-dragover');
            });
          }
          element.on('submit', function(evt) {
            if ($scope._inProgressCounter !== 0) {
              return evt.preventDefault();
            }
          });
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadSubmit', [
    function() {
      return {
        require: '^cradminLegacyBulkfileuploadForm',
        restrict: 'A',
        scope: true,
        controller: function($scope) {
          $scope.inProgress = false;
          $scope.setInProgress = function() {
            $scope.element.prop('disabled', false);
            return $scope.inProgress = false;
          };
          return $scope.setNotInProgress = function() {
            $scope.element.prop('disabled', true);
            return $scope.inProgress = true;
          };
        },
        link: function(scope, element, attr, formController) {
          scope.element = element;
          formController.addSubmitButtonScope(scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkfileupload', [
    '$upload', '$cookies', 'cradminDetectize', 'cradminBulkfileuploadCoordinator', function($upload, $cookies, cradminDetectize, cradminBulkfileuploadCoordinator) {
      return {
        require: '^cradminLegacyBulkfileuploadForm',
        restrict: 'AE',
        scope: true,
        controller: function($scope) {
          var validateSelectedFiles;
          $scope.collectionid = null;
          $scope.cradminLastFilesSelectedByUser = [];
          $scope.fileUploadQueue = [];
          $scope.firstUploadInProgress = false;
          $scope.simpleWidgetScope = null;
          $scope.advancedWidgetScope = null;
          $scope.rejectedFilesScope = null;
          this.setInProgressOrFinishedScope = function(inProgressOrFinishedScope) {
            return $scope.inProgressOrFinishedScope = inProgressOrFinishedScope;
          };
          this.setFileUploadFieldScope = function(fileUploadFieldScope, fieldname) {
            $scope.fileUploadFieldScope = fileUploadFieldScope;
            return cradminBulkfileuploadCoordinator.register(fileUploadFieldScope.fieldname, $scope);
          };
          this.setSimpleWidgetScope = function(simpleWidgetScope) {
            $scope.simpleWidgetScope = simpleWidgetScope;
            return $scope._showAppropriateWidget();
          };
          this.setAdvancedWidgetScope = function(advancedWidgetScope) {
            $scope.advancedWidgetScope = advancedWidgetScope;
            return $scope._showAppropriateWidget();
          };
          this.setRejectFilesScope = function(rejectedFilesScope) {
            return $scope.rejectedFilesScope = rejectedFilesScope;
          };
          this.getUploadUrl = function() {
            return $scope.uploadapiurl;
          };
          this.getCollectionId = function() {
            return $scope.collectionid;
          };
          this.onAdvancedWidgetDragLeave = function() {
            return $scope.formController.onAdvancedWidgetDragLeave();
          };
          $scope._hideUploadWidget = function() {
            $scope.simpleWidgetScope.hide();
            return $scope.advancedWidgetScope.hide();
          };
          $scope._showAppropriateWidget = function() {
            var deviceType;
            if ($scope.advancedWidgetScope && $scope.simpleWidgetScope) {
              deviceType = cradminDetectize.device.type;
              if (deviceType === 'desktop') {
                $scope.simpleWidgetScope.hide();
                return $scope.advancedWidgetScope.show();
              } else {
                $scope.advancedWidgetScope.hide();
                return $scope.simpleWidgetScope.show();
              }
            }
          };
          $scope.filesDropped = function(files, evt, rejectedFiles) {
            /*
            Called when a file is draggen&dropped into the widget.
            */

            if (rejectedFiles.length > 0) {
              return $scope.rejectedFilesScope.setRejectedFiles(rejectedFiles, 'invalid_filetype', $scope.i18nStrings);
            }
          };
          validateSelectedFiles = function() {
            var file, filesToUpload, _i, _len, _ref;
            filesToUpload = [];
            _ref = $scope.cradminLastFilesSelectedByUser;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              file = _ref[_i];
              if ($scope.apiparameters.max_filesize_bytes) {
                if (file.size > $scope.apiparameters.max_filesize_bytes) {
                  $scope.rejectedFilesScope.addRejectedFile(file, 'max_filesize_bytes_exceeded', $scope.i18nStrings);
                  continue;
                }
              }
              filesToUpload.push(file);
            }
            if ($scope.rejectedFilesScope.hasRejectedFiles() && $scope.autosubmit) {
              return [];
            }
            return filesToUpload;
          };
          $scope.$watch('cradminLastFilesSelectedByUser', function() {
            var file, filesToUpload, _i, _len;
            if ($scope.cradminLastFilesSelectedByUser.length > 0) {
              $scope.rejectedFilesScope.clearRejectedFiles();
              filesToUpload = validateSelectedFiles();
              if (filesToUpload.length > 0) {
                if ($scope.autosubmit) {
                  $scope._hideUploadWidget();
                }
                for (_i = 0, _len = filesToUpload.length; _i < _len; _i++) {
                  file = filesToUpload[_i];
                  $scope._addFileToQueue(file);
                  if ($scope.apiparameters.singlemode) {
                    break;
                  }
                }
              }
              return $scope.cradminLastFilesSelectedByUser = [];
            }
          });
          $scope._addFileToQueue = function(file) {
            var progressFileInfo;
            if ($scope.apiparameters.singlemode) {
              $scope.inProgressOrFinishedScope.clear();
            }
            progressFileInfo = $scope.inProgressOrFinishedScope.addFileInfo({
              percent: 0,
              file: file,
              autosubmit: $scope.autosubmit,
              i18nStrings: $scope.i18nStrings
            });
            $scope.fileUploadQueue.push(progressFileInfo);
            if ($scope.firstUploadInProgress) {
              return;
            }
            if ($scope.collectionid === null) {
              $scope.firstUploadInProgress = true;
            }
            return $scope._processFileUploadQueue();
          };
          $scope._onFileUploadComplete = function(successful) {
            /*
            Called both on file upload success and error
            */

            $scope.firstUploadInProgress = false;
            $scope.formController.removeInProgress();
            if ($scope.fileUploadQueue.length > 0) {
              return $scope._processFileUploadQueue();
            } else if ($scope.autosubmit) {
              if (successful) {
                return $scope.formController.submitForm();
              } else {
                return $scope._showAppropriateWidget();
              }
            }
          };
          $scope._processFileUploadQueue = function() {
            var apidata, progressFileInfo;
            progressFileInfo = $scope.fileUploadQueue.shift();
            apidata = angular.extend({}, $scope.apiparameters, {
              collectionid: $scope.collectionid
            });
            $scope.formController.addInProgress();
            return $scope.upload = $upload.upload({
              url: $scope.uploadapiurl,
              method: 'POST',
              data: apidata,
              file: progressFileInfo.file,
              fileFormDataName: 'file',
              headers: {
                'X-CSRFToken': $cookies.get('csrftoken'),
                'Content-Type': 'multipart/form-data'
              }
            }).progress(function(evt) {
              return progressFileInfo.updatePercent(parseInt(100.0 * evt.loaded / evt.total));
            }).success(function(data, status, headers, config) {
              progressFileInfo.finish(data.temporaryfiles[0], $scope.apiparameters.singlemode);
              $scope._setCollectionId(data.collectionid);
              return $scope._onFileUploadComplete(true);
            }).error(function(data, status) {
              console.log(data);
              if (status === 503) {
                progressFileInfo.setErrors({
                  file: [
                    {
                      message: $scope.errormessage503
                    }
                  ]
                });
              } else {
                progressFileInfo.setErrors(data);
              }
              $scope.inProgressOrFinishedScope.removeFileInfo(progressFileInfo);
              $scope.rejectedFilesScope.addRejectedFileInfo(progressFileInfo);
              return $scope._onFileUploadComplete(false);
            });
          };
          $scope._setCollectionId = function(collectionid) {
            $scope.collectionid = collectionid;
            return $scope.fileUploadFieldScope.setCollectionId(collectionid);
          };
        },
        link: function($scope, element, attributes, formController) {
          var options;
          options = angular.fromJson(attributes.cradminLegacyBulkfileupload);
          $scope.uploadapiurl = options.uploadapiurl;
          $scope.apiparameters = options.apiparameters;
          $scope.errormessage503 = options.errormessage503;
          $scope.autosubmit = options.autosubmit;
          $scope.i18nStrings = {
            close_errormessage_label: options.close_errormessage_label,
            remove_file_label: options.remove_file_label,
            removing_file_message: options.removing_file_message,
            upload_status: options.upload_status
          };
          $scope.formController = formController;
          $scope.$on('$destroy', function() {
            if ($scope.fileUploadFieldScope != null) {
              return cradminBulkfileuploadCoordinator.unregister($scope.fileUploadFieldScope.fieldname);
            }
          });
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadRejectedFiles', [
    'cradminBulkfileupload', function(cradminBulkfileupload) {
      /*
      This directive is used to show files that are rejected on drop because
      of wrong mimetype. Each time a user drops one or more file with invalid
      mimetype, this template is re-rendered and displayed.
      */

      return {
        restrict: 'A',
        require: '^cradminLegacyBulkfileupload',
        templateUrl: 'bulkfileupload/rejectedfiles.tpl.html',
        transclude: true,
        scope: {
          errorMessageMap: '=cradminLegacyBulkfileuploadRejectedFiles'
        },
        controller: function($scope) {
          $scope.rejectedFiles = [];
          $scope.clearRejectedFiles = function() {
            return $scope.rejectedFiles = [];
          };
          $scope.addRejectedFileInfo = function(fileInfo, errormessagecode) {
            return $scope.rejectedFiles.push(fileInfo);
          };
          $scope.addRejectedFile = function(file, errormessagecode, i18nStrings) {
            return $scope.addRejectedFileInfo(cradminBulkfileupload.createFileInfo({
              file: file,
              hasErrors: true,
              i18nStrings: i18nStrings,
              errors: {
                files: [
                  {
                    message: $scope.errorMessageMap[errormessagecode]
                  }
                ]
              }
            }));
          };
          $scope.hasRejectedFiles = function() {
            return $scope.rejectedFiles.length > 0;
          };
          $scope.setRejectedFiles = function(rejectedFiles, errormessagecode, i18nStrings) {
            var file, _i, _len, _results;
            $scope.clearRejectedFiles();
            _results = [];
            for (_i = 0, _len = rejectedFiles.length; _i < _len; _i++) {
              file = rejectedFiles[_i];
              _results.push($scope.addRejectedFile(file, errormessagecode, i18nStrings));
            }
            return _results;
          };
          return $scope.closeMessage = function(fileInfo) {
            var index;
            index = $scope.rejectedFiles.indexOf(fileInfo);
            if (index !== -1) {
              return $scope.rejectedFiles.splice(index, 1);
            }
          };
        },
        link: function(scope, element, attr, bulkfileuploadController) {
          bulkfileuploadController.setRejectFilesScope(scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadProgress', [
    'cradminBulkfileupload', '$http', '$cookies', function(cradminBulkfileupload, $http, $cookies) {
      return {
        restrict: 'AE',
        require: '^cradminLegacyBulkfileupload',
        templateUrl: 'bulkfileupload/progress.tpl.html',
        scope: {},
        controller: function($scope) {
          $scope.fileInfoArray = [];
          $scope.removeFileInfo = function(fileInfo) {
            var fileInfoIndex;
            fileInfoIndex = $scope.fileInfoArray.indexOf(fileInfo);
            if (fileInfoIndex !== -1) {
              return $scope.fileInfoArray.splice(fileInfoIndex, 1);
            } else {
              throw new Error("Could not find requested fileInfo with temporaryfileid=" + fileInfo.temporaryfileid + ".");
            }
          };
          this.removeFile = function(fileInfo) {
            if (fileInfo.temporaryfileid == null) {
              throw new Error("Can not remove files without a temporaryfileid");
            }
            fileInfo.markAsIsRemoving();
            $scope.$apply();
            return $http({
              url: $scope.uploadController.getUploadUrl(),
              method: 'DELETE',
              headers: {
                'X-CSRFToken': $cookies.get('csrftoken')
              },
              data: {
                collectionid: $scope.uploadController.getCollectionId(),
                temporaryfileid: fileInfo.temporaryfileid
              }
            }).success(function(data, status, headers, config) {
              return $scope.removeFileInfo(fileInfo);
            }).error(function(data, status, headers, config) {
              if (typeof console !== "undefined" && console !== null) {
                if (typeof console.error === "function") {
                  console.error('ERROR', data);
                }
              }
              alert('An error occurred while removing the file. Please try again.');
              return fileInfo.markAsIsNotRemoving();
            });
          };
          $scope.addFileInfo = function(options) {
            var fileInfo;
            fileInfo = cradminBulkfileupload.createFileInfo(options);
            $scope.fileInfoArray.push(fileInfo);
            return fileInfo;
          };
          $scope.clear = function(options) {
            return $scope.fileInfoArray = [];
          };
          $scope.clearErrors = function() {
            var fileInfo, index, _i, _ref, _results;
            _results = [];
            for (index = _i = _ref = $scope.fileInfoArray.length - 1; _i >= 0; index = _i += -1) {
              fileInfo = $scope.fileInfoArray[index];
              if (fileInfo.hasErrors) {
                _results.push($scope.fileInfoArray.splice(index, 1));
              } else {
                _results.push(void 0);
              }
            }
            return _results;
          };
        },
        link: function(scope, element, attr, uploadController) {
          scope.uploadController = uploadController;
          uploadController.setInProgressOrFinishedScope(scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkFileInfo', [
    function() {
      /**
      Renders a single file info with progress info, errors, etc.
      
      Used both the cradminLegacyBulkfileuploadProgress directive.
      */

      return {
        restrict: 'AE',
        scope: {
          fileInfo: '=cradminLegacyBulkFileInfo'
        },
        templateUrl: 'bulkfileupload/fileinfo.tpl.html',
        transclude: true,
        controller: function($scope) {
          this.close = function() {
            return $scope.element.remove();
          };
        },
        link: function(scope, element, attr) {
          scope.element = element;
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadErrorCloseButton', [
    function() {
      return {
        restrict: 'A',
        require: '^cradminLegacyBulkFileInfo',
        scope: {},
        link: function(scope, element, attr, fileInfoController) {
          element.on('click', function(evt) {
            evt.preventDefault();
            return fileInfoController.close();
          });
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadRemoveFileButton', [
    function() {
      return {
        restrict: 'A',
        require: '^cradminLegacyBulkfileuploadProgress',
        scope: {
          'fileInfo': '=cradminLegacyBulkfileuploadRemoveFileButton'
        },
        link: function(scope, element, attr, progressController) {
          element.on('click', function(evt) {
            evt.preventDefault();
            return progressController.removeFile(scope.fileInfo);
          });
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadCollectionidField', [
    function() {
      return {
        require: '^cradminLegacyBulkfileupload',
        restrict: 'AE',
        scope: {},
        controller: function($scope) {
          $scope.setCollectionId = function(collectionid) {
            return $scope.element.val("" + collectionid);
          };
        },
        link: function(scope, element, attr, uploadController) {
          scope.element = element;
          scope.fieldname = attr.name;
          uploadController.setFileUploadFieldScope(scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadAdvancedWidget', [
    '$timeout', function($timeout) {
      return {
        require: '^cradminLegacyBulkfileupload',
        restrict: 'AE',
        scope: {},
        link: function(scope, element, attr, uploadController) {
          scope.hide = function() {
            return element.css('display', 'none');
          };
          scope.show = function() {
            return element.css('display', 'block');
          };
          uploadController.setAdvancedWidgetScope(scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadSimpleWidget', [
    function() {
      return {
        require: '^cradminLegacyBulkfileupload',
        restrict: 'AE',
        scope: {},
        link: function(scope, element, attr, uploadController) {
          scope.hide = function() {
            return element.css('display', 'none');
          };
          scope.show = function() {
            return element.css('display', 'block');
          };
          uploadController.setSimpleWidgetScope(scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadShowOverlay', [
    'cradminBulkfileuploadCoordinator', function(cradminBulkfileuploadCoordinator) {
      return {
        restrict: 'AE',
        scope: {
          hiddenfieldname: '@cradminLegacyBulkfileuploadShowOverlay'
        },
        link: function($scope, element, attr) {
          element.on('click', function() {
            return cradminBulkfileuploadCoordinator.showOverlayForm($scope.hiddenfieldname);
          });
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadHideOverlay', [
    function() {
      return {
        restrict: 'AE',
        require: '^cradminLegacyBulkfileuploadForm',
        scope: {
          hiddenfieldname: '@cradminLegacyBulkfileuploadHideOverlay'
        },
        link: function($scope, element, attr, uploadFormController) {
          element.on('click', function() {
            return uploadFormController.hideOverlay();
          });
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadOverlayControls', [
    function() {
      return {
        restrict: 'AE',
        require: '^cradminLegacyBulkfileuploadForm',
        scope: {},
        link: function($scope, element, attr, uploadFormController) {
          $scope.element = element;
          uploadFormController.registerOverlayControls($scope);
        }
      };
    }
  ]).directive('cradminLegacyBulkfileuploadOverlayUploadingmessage', [
    function() {
      return {
        restrict: 'AE',
        require: '^cradminLegacyBulkfileuploadForm',
        scope: {},
        controller: function($scope) {
          $scope.onSubmitForm = function() {
            return $scope.element.addClass('cradmin-legacy-bulkfileupload-overlay-uploadingmessage-visible');
          };
        },
        link: function($scope, element, attr, uploadFormController) {
          $scope.element = element;
          uploadFormController.registerOverlayUploadingmessageScope($scope);
        }
      };
    }
  ]);

}).call(this);

(function() {
  var app;

  app = angular.module('cradminLegacy.calendar.providers', []);

  app.provider('cradminLegacyCalendarApi', function() {
    /**
    Get an array of the short names for all the weekdays
    in the current locale, in the the correct order for the
    current locale.
    */

    var CalendarCoordinator, CalendarDay, CalendarMonth, CalendarWeek, Month, MonthlyCalendarCoordinator, getWeekdaysShortForCurrentLocale;
    getWeekdaysShortForCurrentLocale = function() {
      var firstDayOfWeek, index, weekday, weekdays, weekdaysWithSundayFirst, _i, _ref;
      weekdays = [];
      weekdaysWithSundayFirst = moment.weekdaysShort();
      firstDayOfWeek = moment.localeData().firstDayOfWeek();
      for (index = _i = firstDayOfWeek, _ref = firstDayOfWeek + 6; firstDayOfWeek <= _ref ? _i <= _ref : _i >= _ref; index = firstDayOfWeek <= _ref ? ++_i : --_i) {
        if (index > 6) {
          index = Math.abs(7 - index);
        }
        weekday = weekdaysWithSundayFirst[index];
        weekdays.push(weekday);
      }
      return weekdays;
    };
    Month = (function() {
      function Month(firstDayOfMonth) {
        this.firstDayOfMonth = firstDayOfMonth;
        this.lastDayOfMonth = this.firstDayOfMonth.clone().add({
          days: this.firstDayOfMonth.daysInMonth() - 1
        });
      }

      Month.prototype.getDaysInMonth = function() {
        return this.firstDayOfMonth.daysInMonth();
      };

      return Month;

    })();
    CalendarDay = (function() {
      function CalendarDay(momentObject, isInCurrentMonth, isDisabled, nowMomentObject) {
        this.momentObject = momentObject;
        this.isInCurrentMonth = isInCurrentMonth;
        this.nowMomentObject = nowMomentObject;
        this._isDisabled = isDisabled;
      }

      CalendarDay.prototype.getNumberInMonth = function() {
        return this.momentObject.format('D');
      };

      CalendarDay.prototype.isToday = function() {
        return this.momentObject.isSame(this.nowMomentObject, 'day');
      };

      CalendarDay.prototype.isDisabled = function() {
        return this._isDisabled;
      };

      return CalendarDay;

    })();
    CalendarWeek = (function() {
      function CalendarWeek() {
        this.calendarDays = [];
      }

      CalendarWeek.prototype.addDay = function(calendarDay) {
        return this.calendarDays.push(calendarDay);
      };

      CalendarWeek.prototype.getDayCount = function() {
        return this.calendarDays.length;
      };

      CalendarWeek.prototype.prettyOneLineFormat = function() {
        var calendarDay, formattedDay, formattedDays, _i, _len, _ref;
        formattedDays = [];
        _ref = this.calendarDays;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          calendarDay = _ref[_i];
          formattedDay = calendarDay.momentObject.format('DD');
          if (calendarDay.isInCurrentMonth) {
            formattedDay = " " + formattedDay + " ";
          } else {
            formattedDay = "(" + formattedDay + ")";
          }
          formattedDays.push(formattedDay);
        }
        return formattedDays.join(' ');
      };

      return CalendarWeek;

    })();
    CalendarMonth = (function() {
      function CalendarMonth(calendarCoordinator, momentObject) {
        this.calendarCoordinator = calendarCoordinator;
        this.changeMonth(momentObject);
      }

      CalendarMonth.prototype.changeMonth = function(momentObject) {
        var firstDayOfMonthMomentObject;
        firstDayOfMonthMomentObject = momentObject.clone().set({
          date: 1,
          hour: 0,
          minute: 0,
          second: 0,
          millisecond: 0
        });
        this.month = new Month(firstDayOfMonthMomentObject);
        this.calendarWeeks = [new CalendarWeek()];
        this.currentWeekIndex = 0;
        this.daysPerWeek = 7;
        this.totalWeeks = 6;
        this.currentDayCount = 0;
        this.lastDay = null;
        return this.__build();
      };

      CalendarMonth.prototype.__buildPrefixedDays = function() {
        var index, momentObject, _i, _ref, _results;
        if (this.month.firstDayOfMonth.weekday() > 0) {
          _results = [];
          for (index = _i = _ref = this.month.firstDayOfMonth.weekday(); _ref <= 1 ? _i <= 1 : _i >= 1; index = _ref <= 1 ? ++_i : --_i) {
            momentObject = this.month.firstDayOfMonth.clone().subtract({
              days: index
            });
            _results.push(this.__addMomentObject(momentObject, false));
          }
          return _results;
        }
      };

      CalendarMonth.prototype.__buildSuffixedDays = function() {
        var momentObject, totalDayCount, _results;
        totalDayCount = this.totalWeeks * this.daysPerWeek;
        _results = [];
        while (this.currentDayCount < totalDayCount) {
          momentObject = this.lastDay.momentObject.clone().add({
            days: 1
          });
          _results.push(this.__addMomentObject(momentObject, false));
        }
        return _results;
      };

      CalendarMonth.prototype.__buildDaysBelongingInMonth = function() {
        var dayIndex, momentObject, _i, _ref, _results;
        _results = [];
        for (dayIndex = _i = 1, _ref = this.month.getDaysInMonth(); 1 <= _ref ? _i <= _ref : _i >= _ref; dayIndex = 1 <= _ref ? ++_i : --_i) {
          momentObject = this.month.firstDayOfMonth.clone().date(dayIndex);
          _results.push(this.__addMomentObject(momentObject, true));
        }
        return _results;
      };

      CalendarMonth.prototype.__build = function(momentFirstDayOfMonth) {
        this.__buildPrefixedDays();
        this.__buildDaysBelongingInMonth();
        return this.__buildSuffixedDays();
      };

      CalendarMonth.prototype.__addMomentObject = function(momentObject, isInCurrentMonth) {
        var calendarDay, isDisabled, week;
        week = this.calendarWeeks[this.currentWeekIndex];
        if (week.getDayCount() >= this.daysPerWeek) {
          this.calendarWeeks.push(new CalendarWeek());
          this.currentWeekIndex += 1;
          week = this.calendarWeeks[this.currentWeekIndex];
        }
        isDisabled = !this.calendarCoordinator.momentObjectIsAllowed(momentObject);
        calendarDay = new CalendarDay(momentObject, isInCurrentMonth, isDisabled, this.calendarCoordinator.nowMomentObject);
        week.addDay(calendarDay);
        this.currentDayCount += 1;
        return this.lastDay = calendarDay;
      };

      CalendarMonth.prototype.prettyprint = function() {
        var rowFormatted, week, _i, _len, _ref, _results;
        _ref = this.calendarWeeks;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          week = _ref[_i];
          rowFormatted = [];
          _results.push(typeof console !== "undefined" && console !== null ? typeof console.log === "function" ? console.log(week.prettyOneLineFormat()) : void 0 : void 0);
        }
        return _results;
      };

      return CalendarMonth;

    })();
    /*
    Coordinates the common calendar data no matter what kind of
    view we present.
    */

    CalendarCoordinator = (function() {
      function CalendarCoordinator(_arg) {
        this.selectedMomentObject = _arg.selectedMomentObject, this.minimumDatetime = _arg.minimumDatetime, this.maximumDatetime = _arg.maximumDatetime, this.defaultNowTime = _arg.defaultNowTime, this.nowMomentObject = _arg.nowMomentObject;
        if (this.selectedMomentObject != null) {
          this.shownMomentObject = this.selectedMomentObject.clone();
        } else {
          this.setToNow();
          this.setInitialTimeForDate();
          if (!this.momentObjectIsAllowed(this.shownMomentObject)) {
            this.shownMomentObject = this.minimumDatetime.clone();
          }
        }
      }

      CalendarCoordinator.prototype.selectShownValue = function() {
        return this.selectedMomentObject = this.shownMomentObject.clone();
      };

      CalendarCoordinator.prototype.clearSelectedMomentObject = function() {
        return this.selectedMomentObject = null;
      };

      CalendarCoordinator.prototype.momentObjectIsAllowed = function(momentObject, ignoreTime) {
        var isAllowed, maximumDatetime, minimumDatetime;
        if (ignoreTime == null) {
          ignoreTime = true;
        }
        isAllowed = true;
        if (this.minimumDatetime != null) {
          minimumDatetime = this.minimumDatetime;
          if (ignoreTime) {
            minimumDatetime = minimumDatetime.clone().set({
              hour: 0,
              minute: 0,
              second: 0
            });
          }
          isAllowed = !momentObject.isBefore(minimumDatetime);
        }
        if (isAllowed && (this.maximumDatetime != null)) {
          maximumDatetime = this.maximumDatetime;
          if (ignoreTime) {
            maximumDatetime = maximumDatetime.clone().set({
              hour: 23,
              minute: 59,
              second: 59
            });
          }
          isAllowed = !momentObject.isAfter(maximumDatetime);
        }
        return isAllowed;
      };

      CalendarCoordinator.prototype.todayIsValidValue = function() {
        return this.momentObjectIsAllowed(this.nowMomentObject);
      };

      CalendarCoordinator.prototype.nowIsValidValue = function() {
        return this.momentObjectIsAllowed(this.nowMomentObject, false);
      };

      CalendarCoordinator.prototype.shownDateIsToday = function() {
        return this.shownMomentObject.isSame(this.nowMomentObject, 'day');
      };

      CalendarCoordinator.prototype.shownDateIsTodayAndNowIsValid = function() {
        return this.shownDateIsToday() && this.nowIsValidValue();
      };

      CalendarCoordinator.prototype.setToNow = function() {
        return this.shownMomentObject = this.nowMomentObject.clone();
      };

      CalendarCoordinator.prototype.setInitialTimeForDate = function() {
        var hour, minute;
        if (this.defaultNowTime) {
          hour = this.nowMomentObject.hour;
          minute = this.nowMomentObject.minute;
          if (this.defaultNowTime.hour !== void 0 && this.defaultNowTime.hour !== null) {
            hour = this.defaultNowTime.hour;
          }
          if (this.defaultNowTime.minute !== void 0 && this.defaultNowTime.minute !== null) {
            minute = this.defaultNowTime.minute;
          }
          return this.shownMomentObject = this.nowMomentObject.clone().set({
            hour: this.defaultNowTime.hour ? this.defaultNowTime.hour : hour,
            minute: this.defaultNowTime.minute != null ? this.defaultNowTime.minute : minute,
            second: 0
          });
        }
      };

      return CalendarCoordinator;

    })();
    /**
    Coordinates the common calendar data for a month-view.
    */

    MonthlyCalendarCoordinator = (function() {
      function MonthlyCalendarCoordinator(_arg) {
        this.calendarCoordinator = _arg.calendarCoordinator, this.yearselectValues = _arg.yearselectValues, this.hourselectValues = _arg.hourselectValues, this.minuteselectValues = _arg.minuteselectValues, this.yearFormat = _arg.yearFormat, this.monthFormat = _arg.monthFormat, this.dayOfMonthSelectFormat = _arg.dayOfMonthSelectFormat, this.dayOfMonthTableCellFormat = _arg.dayOfMonthTableCellFormat, this.hourFormat = _arg.hourFormat, this.minuteFormat = _arg.minuteFormat;
        this.dayobjects = null;
        this.__initWeekdays();
        this.__initMonthObjects();
        this.__initYearObjects();
        this.__initHourObjects();
        this.__initMinuteObjects();
        this.__changeSelectedDate();
      }

      MonthlyCalendarCoordinator.prototype.__sortConfigObjectsByValue = function(configObjects) {
        var compareFunction;
        compareFunction = function(a, b) {
          if (a.value < b.value) {
            return -1;
          }
          if (a.value > b.value) {
            return 1;
          }
          return 0;
        };
        return configObjects.sort(compareFunction);
      };

      MonthlyCalendarCoordinator.prototype.__initWeekdays = function() {
        return this.shortWeekdays = getWeekdaysShortForCurrentLocale();
      };

      MonthlyCalendarCoordinator.prototype.__initYearObjects = function() {
        var formatMomentObject, hasSelectedYearValue, label, selectedYearValue, year, yearConfig, _i, _len, _ref;
        selectedYearValue = this.calendarCoordinator.shownMomentObject.year();
        hasSelectedYearValue = false;
        formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
          month: 0,
          date: 0,
          hour: 0,
          minute: 0,
          second: 0
        });
        this.__yearsMap = {};
        this.yearselectConfig = [];
        _ref = this.yearselectValues;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          year = _ref[_i];
          label = formatMomentObject.set({
            year: year
          }).format(this.yearFormat);
          yearConfig = {
            value: year,
            label: label
          };
          this.yearselectConfig.push(yearConfig);
          this.__yearsMap[year] = yearConfig;
          if (year === selectedYearValue) {
            hasSelectedYearValue = true;
          }
        }
        if (!hasSelectedYearValue) {
          label = formatMomentObject.set({
            year: selectedYearValue
          }).format(this.yearFormat);
          yearConfig = {
            value: selectedYearValue,
            label: label
          };
          this.yearselectConfig.push(yearConfig);
          this.__yearsMap[yearConfig.value] = yearConfig;
          return this.__sortConfigObjectsByValue(this.yearselectConfig);
        }
      };

      MonthlyCalendarCoordinator.prototype.__initMonthObjects = function() {
        var formatMomentObject, label, monthObject, monthnumber, _i, _results;
        this.monthselectConfig = [];
        this.__monthsMap = {};
        formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
          month: 0,
          date: 0,
          hour: 0,
          minute: 0,
          second: 0
        });
        _results = [];
        for (monthnumber = _i = 0; _i <= 11; monthnumber = ++_i) {
          label = formatMomentObject.set({
            month: monthnumber
          }).format(this.monthFormat);
          monthObject = {
            value: monthnumber,
            label: label
          };
          this.monthselectConfig.push(monthObject);
          _results.push(this.__monthsMap[monthnumber] = monthObject);
        }
        return _results;
      };

      MonthlyCalendarCoordinator.prototype.__initHourObjects = function() {
        var formatMomentObject, hasSelectedHourValue, hour, hourConfig, label, selectedHourValue, _i, _len, _ref;
        selectedHourValue = this.calendarCoordinator.shownMomentObject.hour();
        hasSelectedHourValue = false;
        formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
          minute: 0,
          second: 0
        });
        this.__hoursMap = {};
        this.hourselectConfig = [];
        _ref = this.hourselectValues;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          hour = _ref[_i];
          label = formatMomentObject.set({
            hour: hour
          }).format(this.hourFormat);
          hourConfig = {
            value: hour,
            label: label
          };
          this.hourselectConfig.push(hourConfig);
          this.__hoursMap[hourConfig.value] = hourConfig;
          if (hourConfig.value === selectedHourValue) {
            hasSelectedHourValue = true;
          }
        }
        if (!hasSelectedHourValue) {
          label = formatMomentObject.set({
            hour: selectedHourValue
          }).format(this.hourFormat);
          hourConfig = {
            value: selectedHourValue,
            label: label
          };
          this.hourselectConfig.push(hourConfig);
          this.__hoursMap[hourConfig.value] = hourConfig;
          return this.__sortConfigObjectsByValue(this.hourselectConfig);
        }
      };

      MonthlyCalendarCoordinator.prototype.__initMinuteObjects = function() {
        var formatMomentObject, hasSelectedMinuteValue, label, minute, minuteConfig, selectedMinuteValue, _i, _len, _ref;
        selectedMinuteValue = this.calendarCoordinator.shownMomentObject.minute();
        hasSelectedMinuteValue = false;
        formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
          second: 0
        });
        this.__minutesMap = {};
        this.minuteselectConfig = [];
        _ref = this.minuteselectValues;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          minute = _ref[_i];
          label = formatMomentObject.set({
            minute: minute
          }).format(this.minuteFormat);
          minuteConfig = {
            value: minute,
            label: label
          };
          this.minuteselectConfig.push(minuteConfig);
          this.__minutesMap[minuteConfig.value] = minuteConfig;
          if (minuteConfig.value === selectedMinuteValue) {
            hasSelectedMinuteValue = true;
          }
        }
        if (!hasSelectedMinuteValue) {
          label = formatMomentObject.set({
            minute: selectedMinuteValue
          }).format(this.minuteFormat);
          minuteConfig = {
            value: selectedMinuteValue,
            label: label
          };
          this.minuteselectConfig.push(minuteConfig);
          this.__minutesMap[minuteConfig.value] = minuteConfig;
          return this.__sortConfigObjectsByValue(this.minuteselectConfig);
        }
      };

      MonthlyCalendarCoordinator.prototype.__setCurrentYear = function() {
        var currentYearNumber;
        currentYearNumber = this.calendarMonth.month.firstDayOfMonth.year();
        this.currentYearObject = this.__yearsMap[currentYearNumber];
        if (this.currentYearObject == null) {
          return typeof console !== "undefined" && console !== null ? typeof console.warn === "function" ? console.warn("The given year, " + currentYearNumber + " is not one of the available choices") : void 0 : void 0;
        }
      };

      MonthlyCalendarCoordinator.prototype.__setCurrentMonth = function() {
        var currentMonthNumber;
        currentMonthNumber = this.calendarMonth.month.firstDayOfMonth.month();
        this.currentMonthObject = this.__monthsMap[currentMonthNumber];
        if (this.currentMonthObject == null) {
          return typeof console !== "undefined" && console !== null ? typeof console.warn === "function" ? console.warn("The given month number, " + currentMonthNumber + " is not one of the available choices") : void 0 : void 0;
        }
      };

      MonthlyCalendarCoordinator.prototype.__setCurrentHour = function() {
        var currentHourNumber;
        currentHourNumber = this.calendarCoordinator.shownMomentObject.hour();
        this.currentHourObject = this.__hoursMap[currentHourNumber];
        if (this.currentHourObject == null) {
          return typeof console !== "undefined" && console !== null ? typeof console.warn === "function" ? console.warn("The given hour, " + currentHourNumber + " is not one of the available choices") : void 0 : void 0;
        }
      };

      MonthlyCalendarCoordinator.prototype.__setCurrentMinute = function() {
        var currentMinuteNumber;
        currentMinuteNumber = this.calendarCoordinator.shownMomentObject.minute();
        this.currentMinuteObject = this.__minutesMap[currentMinuteNumber];
        if (this.currentMinuteObject == null) {
          return typeof console !== "undefined" && console !== null ? typeof console.warn === "function" ? console.warn("The given minute, " + currentMinuteNumber + " is not one of the available choices") : void 0 : void 0;
        }
      };

      MonthlyCalendarCoordinator.prototype.__updateDayObjects = function() {
        var dayNumberObject, daynumber, formatMomentObject, label, _i, _ref, _results;
        formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
          hour: 0,
          minute: 0,
          second: 0
        });
        this.dayobjects = [];
        _results = [];
        for (daynumber = _i = 1, _ref = this.calendarMonth.month.getDaysInMonth(); 1 <= _ref ? _i <= _ref : _i >= _ref; daynumber = 1 <= _ref ? ++_i : --_i) {
          label = formatMomentObject.set({
            date: daynumber
          }).format(this.dayOfMonthSelectFormat);
          dayNumberObject = {
            value: daynumber,
            label: label
          };
          _results.push(this.dayobjects.push(dayNumberObject));
        }
        return _results;
      };

      /*
      Change month to the month containing the given momentObject,
      and select the date.
      
      As long as you change ``@calendarCoordinator.shownMomentObject``, this
      will update everything to mirror the change (selected day, month, year, ...).
      */


      MonthlyCalendarCoordinator.prototype.__changeSelectedDate = function() {
        this.calendarMonth = new CalendarMonth(this.calendarCoordinator, this.calendarCoordinator.shownMomentObject);
        this.__setCurrentYear();
        this.__setCurrentMonth();
        this.__setCurrentHour();
        this.__setCurrentMinute();
        this.__updateDayObjects();
        return this.currentDayObject = this.dayobjects[this.calendarCoordinator.shownMomentObject.date() - 1];
      };

      MonthlyCalendarCoordinator.prototype.handleDayChange = function(momentObject) {
        this.calendarCoordinator.shownMomentObject = momentObject.clone().set({
          hour: this.currentHourObject.value,
          minute: this.currentMinuteObject.value
        });
        return this.__changeSelectedDate();
      };

      MonthlyCalendarCoordinator.prototype.handleCurrentDayObjectChange = function() {
        var momentObject;
        momentObject = moment({
          year: this.currentYearObject.value,
          month: this.currentMonthObject.value,
          day: this.currentDayObject.value
        });
        return this.handleDayChange(momentObject);
      };

      MonthlyCalendarCoordinator.prototype.handleCalendarDayChange = function(calendarDay) {
        return this.handleDayChange(calendarDay.momentObject);
      };

      MonthlyCalendarCoordinator.prototype.handleCurrentMonthChange = function() {
        this.calendarCoordinator.shownMomentObject.set({
          month: this.currentMonthObject.value
        });
        return this.__changeSelectedDate();
      };

      MonthlyCalendarCoordinator.prototype.handleCurrentYearChange = function() {
        this.calendarCoordinator.shownMomentObject.set({
          year: this.currentYearObject.value
        });
        return this.__changeSelectedDate();
      };

      MonthlyCalendarCoordinator.prototype.handleCurrentHourChange = function() {
        this.calendarCoordinator.shownMomentObject.set({
          hour: this.currentHourObject.value
        });
        return this.__changeSelectedDate();
      };

      MonthlyCalendarCoordinator.prototype.handleCurrentMinuteChange = function() {
        this.calendarCoordinator.shownMomentObject.set({
          minute: this.currentMinuteObject.value
        });
        return this.__changeSelectedDate();
      };

      MonthlyCalendarCoordinator.prototype.handleFocusOnCalendarDay = function(calendarDay) {
        return this.lastFocusedMomentObject = calendarDay.momentObject;
      };

      MonthlyCalendarCoordinator.prototype.getLastFocusedMomentObject = function() {
        if (this.lastFocusedMomentObject != null) {
          return this.lastFocusedMomentObject;
        } else {
          return this.calendarCoordinator.shownMomentObject;
        }
      };

      MonthlyCalendarCoordinator.prototype.getDayOfMonthLabelForTableCell = function(calendarDay) {
        return calendarDay.momentObject.format(this.dayOfMonthTableCellFormat);
      };

      MonthlyCalendarCoordinator.prototype.setToToday = function() {
        return this.handleDayChange(this.calendarCoordinator.nowMomentObject.clone());
      };

      return MonthlyCalendarCoordinator;

    })();
    this.$get = function() {
      return {
        MonthlyCalendarCoordinator: MonthlyCalendarCoordinator,
        CalendarCoordinator: CalendarCoordinator
      };
    };
    return this;
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.collapse', []).directive('cradminLegacyCollapse', [
    function() {
      /** A box that collapses/expands its content automatically when the header is clicked.
      
      Example
      =======
      
      ```html
      <div cradmin-legacy-collapse>
        <button ng-click="toggleContentVisible()" type="button">
          <span ng-if="contentHidden">Show</span>
          <span ng-if="!contentHidden">Hide</span>
        </button>
        <div ng-class="{'ng-hide': contentHidden}">
          Something here
        </div>
      </div>
      ```
      
      You can make it visible by default using ``initial-state="visible"``:
      
      ```html
      <div cradmin-legacy-collapse initial-state="visible">
        ...
      </div>
      ```
      
      If you want to avoid the initial flicker before the directive
      hides the content, add the ``ng-hide`` css class to the content div:
      
      ```html
      <div cradmin-legacy-collapse>
        <button ng-click="toggleContentVisible()" type="button">
          ...
        </button>
        <div ng-class="{'ng-hide': contentHidden}" ng-class="ng-hide">
          Something here
        </div>
      </div>
      ```
      */

      return {
        scope: true,
        controller: function($scope) {
          $scope.contentHidden = true;
          $scope.toggleContentVisible = function() {
            return $scope.contentHidden = !$scope.contentHidden;
          };
        },
        link: function($scope, $element, attrs) {
          return $scope.contentHidden = attrs.initialState !== 'visible';
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.directives', []).directive('cradminLegacyBack', function() {
    return {
      restrict: 'A',
      link: function(scope, element, attrs) {
        element.on('click', function() {
          history.back();
          return scope.$apply();
        });
      }
    };
  }).directive('cradminLegacyFormAction', function() {
    return {
      restrict: 'A',
      scope: {
        'value': '=cradminLegacyFormAction'
      },
      controller: function($scope) {
        $scope.$watch('value', function(newValue) {
          return $scope.element.attr('action', newValue);
        });
      },
      link: function(scope, element, attrs) {
        scope.element = element;
      }
    };
  }).directive('cradminLegacySelectTextForCopyOnFocus', function() {
    /*
    Select text of an input field or textarea when the field
    receives focus.
    
    Example:
    ```
    <p>Copy the url below and share it on social media!</p>
    <input type="text" value="example.com" cradmin-legacy-select-text-for-copy-on-focus="http://example.com">
    ```
    */

    return {
      restrict: 'A',
      scope: {
        valueToCopy: '@cradminLegacySelectTextForCopyOnFocus'
      },
      link: function(scope, element, attrs) {
        scope.value = attrs['value'];
        element.on('click', function() {
          element.val(scope.valueToCopy);
          return this.select();
        });
        scope.resetValue = function() {
          return element.val(scope.value);
        };
        element.on('change', function() {
          return scope.resetValue();
        });
        element.on('blur', function() {
          return scope.resetValue();
        });
      }
    };
  }).directive('focusonme', [
    '$timeout', function($timeout) {
      return {
        restrict: 'A',
        link: function($scope, $element) {
          $timeout(function() {
            $element[0].focus();
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  angular.module('cradminLegacy.providers', []).provider('cradminLegacyWindowDimensions', function() {
    /** Provider that makes it easy to listen for window resize.
    
    How it works
    ============
    You register a ``scope`` with the provider. Each time the window
    is resized, the provider will call ``scope.onWindowResize()``.
    The provider uses a ``300ms`` timeout before it triggers a
    resize, so your ``onWindowResize`` method will not be flooded
    with every pixel change.
    
    Example
    =======
    
    ```coffeescript
    mymodule.directive('myDirective', [
      'cradminLegacyWindowDimensions'
      (cradminLegacyWindowDimensions) ->
        return {
          controller: ($scope) ->
            $scope.onWindowResize = (newWindowDimensions) ->
              console.log 'Window was resized to', newWindowDimensions
            return
    
          link: ($scope, element, attrs) ->
            cradminLegacyWindowDimensions.register $scope
            $scope.$on '$destroy', ->
              cradminLegacyWindowDimensions.unregister $scope
            return
        }
    ])
    ```
    */

    var WindowDimensionsProvider;
    WindowDimensionsProvider = (function() {
      function WindowDimensionsProvider($window, timeout) {
        this.timeout = timeout;
        this._onWindowResize = __bind(this._onWindowResize, this);
        this.mainWindow = angular.element($window);
        this.deviceMinWidths = {
          tablet: 768,
          mediumDesktop: 992,
          largeDesktop: 1200
        };
        this.windowDimensions = this._getWindowDimensions();
        this.applyResizeTimer = null;
        this.applyResizeTimerTimeoutMs = 300;
        this.listeningScopes = [];
      }

      WindowDimensionsProvider.prototype._triggerResizeEventsForScope = function(scope) {
        return scope.onWindowResize(this.windowDimensions);
      };

      WindowDimensionsProvider.prototype.register = function(scope) {
        var scopeIndex;
        scopeIndex = this.listeningScopes.indexOf(scope);
        if (scopeIndex !== -1) {
          console.error('Trying to register a scope that is already registered with ' + 'cradminLegacyWindowDimensions. Scope:', scope);
          return;
        }
        if (this.listeningScopes.length < 1) {
          this.mainWindow.bind('resize', this._onWindowResize);
        }
        return this.listeningScopes.push(scope);
      };

      WindowDimensionsProvider.prototype.unregister = function(scope) {
        var scopeIndex;
        scopeIndex = this.listeningScopes.indexOf(scope);
        if (scopeIndex === -1) {
          console.error('Trying to unregister a scope that is not registered with ' + 'cradminLegacyWindowDimensions. Scope:', scope);
        }
        this.listeningScopes.splice(scopeIndex, 1);
        if (this.listeningScopes.length < 1) {
          return this.mainWindow.unbind('resize', this._onWindowResize);
        }
      };

      WindowDimensionsProvider.prototype._getWindowDimensions = function() {
        return {
          height: this.mainWindow.height(),
          width: this.mainWindow.width()
        };
      };

      WindowDimensionsProvider.prototype.getDeviceFromWindowDimensions = function(windowDimensions) {
        if (windowDimensions < this.deviceMinWidths.tablet) {
          return 'phone';
        } else if (windowDimensions < this.deviceMinWidths.mediumDesktop) {
          return 'tablet';
        } else if (windowDimensions < this.deviceMinWidths.largeDesktop) {
          return 'medium-desktop';
        } else {
          return 'large-desktop';
        }
      };

      WindowDimensionsProvider.prototype._updateWindowDimensions = function(newWindowDimensions) {
        this.windowDimensions = newWindowDimensions;
        return this._onWindowDimensionsChange();
      };

      WindowDimensionsProvider.prototype._setWindowDimensions = function() {
        var newWindowDimensions;
        newWindowDimensions = this._getWindowDimensions();
        if (!angular.equals(newWindowDimensions, this.windowDimensions)) {
          return this._updateWindowDimensions(newWindowDimensions);
        }
      };

      WindowDimensionsProvider.prototype._onWindowDimensionsChange = function() {
        var scope, _i, _len, _ref, _results;
        _ref = this.listeningScopes;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          scope = _ref[_i];
          _results.push(this._triggerResizeEventsForScope(scope));
        }
        return _results;
      };

      WindowDimensionsProvider.prototype.triggerWindowResizeEvent = function() {
        return this._onWindowDimensionsChange();
      };

      WindowDimensionsProvider.prototype._onWindowResize = function() {
        var _this = this;
        this.timeout.cancel(this.applyResizeTimer);
        return this.applyResizeTimer = this.timeout(function() {
          return _this._setWindowDimensions();
        }, this.applyResizeTimerTimeoutMs);
      };

      return WindowDimensionsProvider;

    })();
    this.$get = [
      '$window', '$timeout', function($window, $timeout) {
        return new WindowDimensionsProvider($window, $timeout);
      }
    ];
    return this;
  }).provider('cradminLegacyWindowScrollTop', function() {
    /** Provider that makes it easy to listen for scrolling on the main window.
    
    How it works
    ============
    You register a ``scope`` with the provider. Each time the window
    is scrolled, the provider will call ``scope.onWindowScrollTop()``.
    The provider uses a ``100ms`` timeout before it triggers a
    resize, so your ``onWindowScrollTop`` method will not be flooded
    with every pixel change.
    
    Example
    =======
    
    ```coffeescript
    mymodule.directive('myDirective', [
      'cradminLegacyWindowScrollTop'
      (cradminLegacyWindowScrollTop) ->
        return {
          controller: ($scope) ->
            $scope.onWindowScrollTop = (newTopPosition) ->
              console.log 'Window was scrolled to', newTopPosition
            return
    
          link: ($scope, element, attrs) ->
            cradminLegacyWindowScrollTop.register $scope
            $scope.$on '$destroy', ->
              cradminLegacyWindowScrollTop.unregister $scope
            return
        }
    ])
    ```
    */

    var WindowScrollProvider;
    WindowScrollProvider = (function() {
      function WindowScrollProvider($window, timeout) {
        this.timeout = timeout;
        this._onScroll = __bind(this._onScroll, this);
        this.mainWindow = angular.element($window);
        this.scrollTopPosition = this._getScrollTopPosition();
        this.applyScrollTimer = null;
        this.applyScrollTimerTimeoutMs = 50;
        this.listeningScopes = [];
        this.isScrolling = false;
      }

      WindowScrollProvider.prototype.register = function(scope) {
        var scopeIndex;
        scopeIndex = this.listeningScopes.indexOf(scope);
        if (scopeIndex !== -1) {
          console.error('Trying to register a scope that is already registered with ' + 'cradminLegacyWindowScrollTop. Scope:', scope);
          return;
        }
        if (this.listeningScopes.length < 1) {
          this.mainWindow.bind('scroll', this._onScroll);
        }
        this.listeningScopes.push(scope);
        return scope.onWindowScrollTop(this.scrollTopPosition, true);
      };

      WindowScrollProvider.prototype.unregister = function(scope) {
        var scopeIndex;
        scopeIndex = this.listeningScopes.indexOf(scope);
        if (scopeIndex === -1) {
          console.error('Trying to unregister a scope that is not registered with ' + 'cradminLegacyWindowScrollTop. Scope:', scope);
        }
        this.listeningScopes.splice(scopeIndex, 1);
        if (this.listeningScopes.length < 1) {
          return this.mainWindow.unbind('scroll', this._onScroll);
        }
      };

      WindowScrollProvider.prototype._getScrollTopPosition = function() {
        return this.mainWindow.scrollTop();
      };

      WindowScrollProvider.prototype._setScrollTopPosition = function() {
        var scrollTopPosition;
        scrollTopPosition = this._getScrollTopPosition();
        this.scrollTopPosition = scrollTopPosition;
        return this._onScrollTopChange();
      };

      WindowScrollProvider.prototype._onScrollTopChange = function() {
        var scope, _i, _len, _ref, _results;
        _ref = this.listeningScopes;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          scope = _ref[_i];
          _results.push(scope.onWindowScrollTop(this.scrollTopPosition));
        }
        return _results;
      };

      WindowScrollProvider.prototype._notifyScrollStarted = function() {
        var scope, scrollTopPosition, _i, _len, _ref, _results;
        scrollTopPosition = this._getScrollTopPosition();
        if (scrollTopPosition !== this.scrollTopPosition) {
          _ref = this.listeningScopes;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            scope = _ref[_i];
            if (scope.onWindowScrollTopStart != null) {
              _results.push(scope.onWindowScrollTopStart());
            } else {
              _results.push(void 0);
            }
          }
          return _results;
        }
      };

      WindowScrollProvider.prototype._onScroll = function() {
        var _this = this;
        this.timeout.cancel(this.applyScrollTimer);
        if (!this.isScrolling) {
          this._notifyScrollStarted();
        }
        this.isScrolling = true;
        return this.applyScrollTimer = this.timeout(function() {
          _this._setScrollTopPosition();
          return _this.isScrolling = false;
        }, this.applyScrollTimerTimeoutMs);
      };

      return WindowScrollProvider;

    })();
    this.$get = [
      '$window', '$timeout', function($window, $timeout) {
        return new WindowScrollProvider($window, $timeout);
      }
    ];
    return this;
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.detectizr', []).factory('cradminDetectize', function() {
    Detectizr.detect({
      addAllFeaturesAsClass: false,
      detectDevice: true,
      detectDeviceModel: true,
      detectScreen: true,
      detectOS: true,
      detectBrowser: true,
      detectPlugins: false
    });
    return Detectizr;
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.forms.clearabletextinput', []).directive('cradminLegacyClearableTextinput', [
    function() {
      return {
        restrict: 'A',
        link: function($scope, $element, attributes) {
          var $target, onTargetValueChange, targetElementSelector;
          targetElementSelector = attributes.cradminLegacyClearableTextinput;
          $target = angular.element(targetElementSelector);
          onTargetValueChange = function() {
            if ($target.val() === '') {
              return $element.removeClass('cradmin-legacy-clearable-textinput-button-visible');
            } else {
              return $element.addClass('cradmin-legacy-clearable-textinput-button-visible');
            }
          };
          $element.on('click', function(e) {
            e.preventDefault();
            $target.val('');
            $target.focus();
            return $target.change();
          });
          $target.on('change', function() {
            return onTargetValueChange();
          });
          $target.on('keydown', function(e) {
            return onTargetValueChange();
          });
          return onTargetValueChange();
        }
      };
    }
  ]);

}).call(this);

(function() {
  var app;

  app = angular.module('cradminLegacy.forms.datetimewidget', ['cfp.hotkeys']);

  app.directive('cradminLegacyDatetimeSelector', [
    '$timeout', '$compile', '$rootScope', 'hotkeys', 'cradminLegacyCalendarApi', 'cradminLegacyWindowDimensions', function($timeout, $compile, $rootScope, hotkeys, cradminLegacyCalendarApi, cradminLegacyWindowDimensions) {
      return {
        scope: {
          config: "=cradminLegacyDatetimeSelector"
        },
        templateUrl: 'forms/dateselector.tpl.html',
        controller: function($scope, $element) {
          var __addCommonHotkeys, __addPage1Hotkeys, __getFirstFocusableItemInCurrentPage, __getFocusItemAfterHide, __getInitialFocusItemForCurrentPage, __getLastFocusableItemInCurrentPage, __removeHotkeys;
          $scope.page = null;
          /*
          Handles keyboard navigation.
          */

          $scope.__keyboardNavigation = function(event, direction) {
            var activeElement, lastFocusedElement, newFocusTd, nextSibling, nextTr, previousSibling, previousTr;
            if (direction === 'pageup' || direction === 'pagedown') {
              event.preventDefault();
            }
            if ($element.find('.cradmin-legacy-datetime-selector-table').is(':visible')) {
              activeElement = angular.element(document.activeElement);
              if (activeElement.hasClass('cradmin-legacy-datetime-selector-daybuttoncell-button')) {
                event.preventDefault();
                if (direction === 'right') {
                  nextSibling = activeElement.parent().next();
                  if (nextSibling.length > 0) {
                    newFocusTd = nextSibling;
                  }
                }
                if (direction === 'left') {
                  previousSibling = activeElement.parent().prev();
                  if (previousSibling.length > 0) {
                    newFocusTd = previousSibling;
                  }
                }
                if (direction === 'up') {
                  previousTr = activeElement.parent().parent().prev();
                  if (previousTr.length > 0) {
                    newFocusTd = angular.element(previousTr.children().get(activeElement.parent().index()));
                  }
                }
                if (direction === 'down') {
                  nextTr = activeElement.parent().parent().next();
                  if (nextTr.length > 0) {
                    newFocusTd = angular.element(nextTr.children().get(activeElement.parent().index()));
                  }
                }
                if ((newFocusTd != null) && newFocusTd.length > 0) {
                  newFocusTd.find('button').focus();
                }
                if (direction === 'home') {
                  activeElement.parent().parent().parent().find('button:enabled').first().focus();
                }
                if (direction === 'end') {
                  activeElement.parent().parent().parent().find('button:enabled').last().focus();
                }
                if (direction === 'pageup') {
                  return $element.find('.cradmin-legacy-datetime-selector-monthselect').focus();
                }
              } else if (direction === 'pagedown') {
                if (activeElement.parent().hasClass('cradmin-legacy-datetime-selector-dateselectors')) {
                  lastFocusedElement = $element.find('.cradmin-legacy-datetime-selector-daybuttoncell-lastfocused button');
                  if (lastFocusedElement.is(':visible')) {
                    return lastFocusedElement.focus();
                  } else {
                    return angular.element($element.find('.cradmin-legacy-datetime-selector-daybuttoncell-in-current-month button').first()).focus();
                  }
                }
              }
            }
          };
          /*
          Called when enter is pressed in any of the select fields.
          
          If we have a visible use-button, we do the same as if the user
          pressed that. If we are on page1, on desktop (no use-button),
          we move the focus into the first day of the current month
          in the day select table, or to the selected day if that is visible.
          */

          $scope.__onSelectEnterPressed = function() {
            var selectedButton, tableElement, useButton;
            if ($scope.page === 1) {
              useButton = $element.find('.cradmin-legacy-datetime-selector-dateview ' + '.cradmin-legacy-datetime-selector-use-button');
              if (useButton.is(":visible")) {
                return $scope.onClickUseTime();
              } else {
                tableElement = $element.find('.cradmin-legacy-datetime-selector-table');
                selectedButton = tableElement.find('.cradmin-legacy-datetime-selector-daybuttoncell-selected button');
                if (selectedButton.length > 0) {
                  return selectedButton.focus();
                } else {
                  return tableElement.find('.cradmin-legacy-datetime-selector-daybuttoncell-in-current-month button').first().focus();
                }
              }
            } else if ($scope.page === 2) {
              return $scope.onClickUseTime();
            }
          };
          /*
          Returns the item we want to focus on when we tab forward from the last
          focusable item on the current page.
          */

          __getFirstFocusableItemInCurrentPage = function() {
            if ($scope.page === 1) {
              return $element.find('.cradmin-legacy-datetime-selector-dateview ' + '.cradmin-legacy-datetime-selector-closebutton');
            } else if ($scope.page === 2) {
              return $element.find('.cradmin-legacy-datetime-selector-timeview ' + '.cradmin-legacy-datetime-selector-closebutton');
            }
          };
          /*
          Returns the item we want to focus on when we tab back from the first
          focusable item on the current page.
          */

          __getLastFocusableItemInCurrentPage = function() {
            var useButton;
            if ($scope.page === 1) {
              useButton = $element.find('.cradmin-legacy-datetime-selector-dateview ' + '.cradmin-legacy-datetime-selector-use-button');
              if (useButton.is(":visible")) {
                return useButton;
              } else {
                return $element.find('.cradmin-legacy-datetime-selector-table ' + 'td.cradmin-legacy-datetime-selector-daybuttoncell-in-current-month button').last();
              }
            } else if ($scope.page === 2) {
              return $element.find('.cradmin-legacy-datetime-selector-timeview ' + '.cradmin-legacy-datetime-selector-use-button');
            }
          };
          /*
          Get the initial item to focus on when we open/show a page.
          */

          __getInitialFocusItemForCurrentPage = function() {
            var dayselectElement;
            if ($scope.page === 1) {
              dayselectElement = $element.find('.cradmin-legacy-datetime-selector-dayselect');
              if (dayselectElement.is(':visible')) {
                return dayselectElement;
              } else {
                return $element.find('.cradmin-legacy-datetime-selector-monthselect');
              }
            } else if ($scope.page === 2) {
              return $element.find('.cradmin-legacy-datetime-selector-timeview ' + '.cradmin-legacy-datetime-selector-hourselect');
            }
          };
          /*
          Get the item to focus on when we close the datetime picker.
          */

          __getFocusItemAfterHide = function() {
            return $scope.triggerButton;
          };
          /*
          Triggered when the user focuses on the hidden (sr-only) button we have
          added to the start of the datetime-selector div.
          */

          $scope.onFocusHead = function() {
            if ($scope.page !== null) {
              __getLastFocusableItemInCurrentPage().focus();
            }
          };
          /*
          Triggered when the user focuses on the hidden (sr-only) button we have
          added to the end of the datetime-selector div.
          */

          $scope.onFocusTail = function() {
            if ($scope.page !== null) {
              __getFirstFocusableItemInCurrentPage().focus();
            }
          };
          /*
          Called when a users selects a date using the mobile-only <select>
          menu to select a day.
          */

          $scope.onSelectDayNumber = function() {
            $scope.monthlyCalendarCoordinator.handleCurrentDayObjectChange();
          };
          /*
          Called when a user selects a date by clicking on a day
          in the calendar table.
          */

          $scope.onClickCalendarDay = function(calendarDay) {
            $scope.monthlyCalendarCoordinator.handleCalendarDayChange(calendarDay);
            if ($scope.config.include_time) {
              $scope.showPage2();
            } else {
              $scope.__useShownValue();
            }
          };
          /*
          Called when a users focuses a date in the calendar table.
          */

          $scope.onFocusCalendayDay = function(calendarDay) {
            $scope.monthlyCalendarCoordinator.handleFocusOnCalendarDay(calendarDay);
          };
          /*
          Called when a users selects a month using the month <select>
          menu.
          */

          $scope.onSelectMonth = function() {
            $scope.monthlyCalendarCoordinator.handleCurrentMonthChange();
          };
          /*
          Called when a users selects a year using the year <select>
          menu.
          */

          $scope.onSelectYear = function() {
            $scope.monthlyCalendarCoordinator.handleCurrentYearChange();
          };
          /*
          Called when a users selects an hour using the hour <select>
          menu.
          */

          $scope.onSelectHour = function() {
            $scope.monthlyCalendarCoordinator.handleCurrentHourChange();
          };
          /*
          Called when a users selects a minute using the minute <select>
          menu.
          */

          $scope.onSelectMinute = function() {
            $scope.monthlyCalendarCoordinator.handleCurrentMinuteChange();
          };
          /*
          Called when a user clicks the "Use" button on the time page.
          */

          $scope.onClickUseTime = function() {
            $scope.__useShownValue();
          };
          /*
          Used to get the preview of the selected date on page2 (above the time selector).
          */

          $scope.getTimeselectorDatepreview = function() {
            return $scope.calendarCoordinator.shownMomentObject.format($scope.config.timeselector_datepreview_momentjs_format);
          };
          /*
          This is used to get the aria-label attribute for the "Use" button.
          */

          $scope.getUseButtonAriaLabel = function() {
            var formattedDate;
            if ($scope.monthlyCalendarCoordinator != null) {
              formattedDate = $scope.calendarCoordinator.shownMomentObject.format($scope.config.usebutton_arialabel_momentjs_format);
              return ("" + $scope.config.usebutton_arialabel_prefix + " ") + ("" + formattedDate);
            } else {

            }
            return '';
          };
          /*
          Get day-button (button in the calendar table) aria-label attribute.
          */

          $scope.getDaybuttonAriaLabel = function(calendarDay) {
            var isSelected, label;
            label = "" + (calendarDay.momentObject.format('MMMM D'));
            if ($scope.config.today_label_text !== '' && calendarDay.isToday()) {
              label = "" + label + " (" + $scope.config.today_label_text + ")";
            } else {
              isSelected = calendarDay.momentObject.isSame($scope.calendarCoordinator.selectedMomentObject, 'day');
              if ($scope.config.selected_day_label_text !== '' && isSelected) {
                label = "" + label + " (" + $scope.config.selected_day_label_text + ")";
              }
            }
            return label;
          };
          /*
          Returns ``true`` if we have any buttons in the buttonrow.
          */

          $scope.hasShortcuts = function() {
            if ($scope.calendarCoordinator.nowIsValidValue()) {
              return true;
            } else if (!$scope.config.required) {
              return true;
            } else {
              return false;
            }
          };
          $scope.onClickTodayButton = function() {
            $scope.monthlyCalendarCoordinator.setToToday();
            if ($scope.config.include_time) {
              $scope.showPage2();
            } else {
              $scope.__useShownValue();
            }
          };
          $scope.onClickNowButton = function() {
            $scope.calendarCoordinator.setToNow();
            return $scope.__useShownValue();
          };
          $scope.onClickClearButton = function() {
            return $scope.__clearSelectedValue();
          };
          $scope.getTabindexForCalendarDay = function(calendarDay) {
            if (calendarDay.isInCurrentMonth) {
              return "0";
            } else {

            }
            return "-1";
          };
          /*
          Update the preview text to reflect the selected value.
          */

          $scope.__updatePreviewText = function() {
            var preview, templateScope;
            if ($scope.calendarCoordinator.selectedMomentObject != null) {
              templateScope = $rootScope.$new(true);
              templateScope.momentObject = $scope.calendarCoordinator.selectedMomentObject.clone();
              preview = $compile($scope.previewAngularjsTemplate)(templateScope);
              $scope.previewElement.empty();
              $scope.previewElement.append(preview);
              return $scope.previewElement.show();
            } else {
              if (($scope.config.no_value_preview_text != null) && $scope.config.no_value_preview_text !== '') {
                $scope.previewElement.html($scope.config.no_value_preview_text);
                return $scope.previewElement.show();
              } else {
                return $scope.previewElement.hide();
              }
            }
          };
          /*
          Apply a css animation to indicate that the preview text has
          changed.
          
          The ``delay_milliseconds`` parameter is the number of milliseonds
          to delay starting the animation.
          */

          $scope.__animatePreviewText = function(delay_milliseconds) {
            if ($scope.config.preview_change_animation_cssclass != null) {
              $scope.previewElement.addClass($scope.config.preview_change_animation_cssclass);
              return $timeout(function() {
                return $timeout(function() {
                  $scope.previewElement.removeClass($scope.config.preview_change_animation_cssclass);
                  return $scope.previewElement.first().offsetWidth = $scope.previewElement.first().offsetWidth;
                }, $scope.config.preview_change_animation_duration_milliseconds);
              }, delay_milliseconds);
            }
          };
          /*
          Update the trigger button label to reflect the selected value.
          */

          $scope.__updateTriggerButtonLabel = function() {
            var label;
            if ($scope.calendarCoordinator.selectedMomentObject != null) {
              label = $scope.config.buttonlabel;
            } else {
              label = $scope.config.buttonlabel_novalue;
            }
            return $scope.triggerButton.html(label);
          };
          /*
          Update the value of the destination field to reflect the selected value.
          */

          $scope.__updateDestinationFieldValue = function() {
            var destinationFieldValue;
            if ($scope.calendarCoordinator.selectedMomentObject != null) {
              destinationFieldValue = $scope.calendarCoordinator.selectedMomentObject.format($scope.config.destinationfield_momentjs_format);
            } else {
              destinationFieldValue = '';
            }
            return $scope.destinationField.val(destinationFieldValue);
          };
          /*
          Update destination field value, preview text and trigger button label,
          and hide the datetime selector.
          */

          $scope.__hideWithSelectedValueApplied = function() {
            $scope.__updateDestinationFieldValue();
            $scope.__updatePreviewText();
            $scope.__updateTriggerButtonLabel();
            return $scope.hide();
          };
          /*
          Make the shown value the selected value and call
          ``$scope.__hideWithSelectedValueApplied()``.
          */

          $scope.__useShownValue = function() {
            $scope.calendarCoordinator.selectShownValue();
            return $scope.__hideWithSelectedValueApplied();
          };
          /*
          Clear the selected value and call ``$scope.__hideWithSelectedValueApplied()``.
          */

          $scope.__clearSelectedValue = function() {
            $scope.calendarCoordinator.clearSelectedMomentObject();
            return $scope.__hideWithSelectedValueApplied();
          };
          __addCommonHotkeys = function() {
            hotkeys.add({
              combo: 'esc',
              callback: function(event) {
                return $scope.hide();
              },
              allowIn: ['BUTTON', 'SELECT', 'INPUT']
            });
            hotkeys.add({
              combo: 'up',
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'up');
              }
            });
            hotkeys.add({
              combo: 'down',
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'down');
              }
            });
            hotkeys.add({
              combo: 'left',
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'left');
              }
            });
            hotkeys.add({
              combo: 'right',
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'right');
              }
            });
            hotkeys.add({
              combo: 'home',
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'home');
              }
            });
            hotkeys.add({
              combo: 'end',
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'end');
              }
            });
            hotkeys.add({
              combo: 'pagedown',
              allowIn: ['BUTTON', 'SELECT', 'INPUT'],
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'pagedown');
              }
            });
            return hotkeys.add({
              combo: 'pageup',
              allowIn: ['BUTTON', 'SELECT', 'INPUT', 'BUTTON'],
              callback: function(event) {
                return $scope.__keyboardNavigation(event, 'pageup');
              }
            });
          };
          __addPage1Hotkeys = function() {};
          __removeHotkeys = function() {
            hotkeys.del('esc');
            hotkeys.del('up');
            hotkeys.del('down');
            hotkeys.del('left');
            hotkeys.del('right');
            hotkeys.del('home');
            hotkeys.del('end');
            hotkeys.del('pagedown');
            return hotkeys.del('pageup');
          };
          $scope.__onMouseWheel = function(e) {
            e.preventDefault();
            return e.stopPropagation();
          };
          $scope.__adjustPosition = function() {
            var contentWrapperElement, scrollTop, windowHeight;
            contentWrapperElement = $element.find('.cradmin-legacy-datetime-selector-contentwrapper');
            scrollTop = angular.element(window).scrollTop();
            windowHeight = angular.element(window).height();
            return $scope.datetimeSelectorElement.css({
              top: scrollTop,
              height: "" + windowHeight + "px"
            });
          };
          $scope.onWindowResize = function() {
            return $scope.__adjustPosition();
          };
          $scope.__show = function() {
            __removeHotkeys();
            __addCommonHotkeys();
            return $scope.__adjustPosition();
          };
          $scope.showPage1 = function() {
            angular.element('body').on('mousewheel touchmove', $scope.__onMouseWheel);
            $scope.page = 1;
            $timeout(function() {
              return __getInitialFocusItemForCurrentPage().focus();
            }, 150);
            $scope.__show();
            __addPage1Hotkeys();
          };
          $scope.showPage2 = function() {
            $scope.page = 2;
            $scope.calendarCoordinator.selectShownValue();
            $timeout(function() {
              return __getInitialFocusItemForCurrentPage().focus();
            }, 150);
            $scope.__show();
          };
          $scope.hide = function() {
            angular.element('body').off('mousewheel touchmove', $scope.__onMouseWheel);
            if ($scope.page === 2) {
              $scope.page = 3;
              $timeout(function() {
                return $scope.page = null;
              }, $scope.config.hide_animation_duration_milliseconds);
            } else {
              $scope.page = null;
            }
            __removeHotkeys();
            $timeout(function() {
              return $scope.__animatePreviewText();
            }, $scope.config.hide_animation_duration_milliseconds);
            $timeout(function() {
              return __getFocusItemAfterHide().focus();
            }, 150);
          };
          return $scope.initialize = function() {
            var currentDateIsoString, maximumDatetime, minimumDatetime, selectedMomentObject;
            currentDateIsoString = $scope.destinationField.val();
            if ((currentDateIsoString != null) && currentDateIsoString !== '') {
              selectedMomentObject = moment(currentDateIsoString);
              $scope.triggerButton.html($scope.config.buttonlabel);
            } else {
              selectedMomentObject = null;
              $scope.triggerButton.html($scope.config.buttonlabel_novalue);
            }
            minimumDatetime = null;
            maximumDatetime = null;
            if ($scope.config.minimum_datetime != null) {
              minimumDatetime = moment($scope.config.minimum_datetime);
            }
            if ($scope.config.maximum_datetime != null) {
              maximumDatetime = moment($scope.config.maximum_datetime);
            }
            $scope.calendarCoordinator = new cradminLegacyCalendarApi.CalendarCoordinator({
              selectedMomentObject: selectedMomentObject,
              minimumDatetime: minimumDatetime,
              maximumDatetime: maximumDatetime,
              defaultNowTime: $scope.config.default_now_time,
              nowMomentObject: moment($scope.config.now)
            });
            $scope.monthlyCalendarCoordinator = new cradminLegacyCalendarApi.MonthlyCalendarCoordinator({
              calendarCoordinator: $scope.calendarCoordinator,
              yearselectValues: $scope.config.yearselect_values,
              hourselectValues: $scope.config.hourselect_values,
              minuteselectValues: $scope.config.minuteselect_values,
              yearFormat: $scope.config.yearselect_momentjs_format,
              monthFormat: $scope.config.monthselect_momentjs_format,
              dayOfMonthSelectFormat: $scope.config.dayofmonthselect_momentjs_format,
              dayOfMonthTableCellFormat: $scope.config.dayofmonthtablecell_momentjs_format,
              hourFormat: $scope.config.hourselect_momentjs_format,
              minuteFormat: $scope.config.minuteselect_momentjs_format
            });
            return $scope.__updatePreviewText();
          };
        },
        link: function($scope, $element) {
          var body, configname, configvalue, labelElement, previewTemplateScriptElement, required_config_attributes, _i, _len;
          body = angular.element('body');
          $element.appendTo(body);
          cradminLegacyWindowDimensions.register($scope);
          $scope.$on('$destroy', function() {
            return cradminLegacyWindowDimensions.unregister($scope);
          });
          if ($scope.config.no_value_preview_text == null) {
            $scope.config.no_value_preview_text = '';
          }
          required_config_attributes = ['now', 'destinationfieldid', 'triggerbuttonid', 'previewid', 'previewtemplateid', 'required', 'usebuttonlabel', 'usebutton_arialabel_prefix', 'usebutton_arialabel_momentjs_format', 'close_icon', 'back_icon', 'back_to_datepicker_screenreader_text', 'destinationfield_momentjs_format', 'timeselector_datepreview_momentjs_format', 'year_screenreader_text', 'month_screenreader_text', 'day_screenreader_text', 'hour_screenreader_text', 'minute_screenreader_text', 'dateselector_table_screenreader_caption', 'today_label_text', 'selected_day_label_text', 'yearselect_values', 'hourselect_values', 'yearselect_momentjs_format', 'monthselect_momentjs_format', 'dayofmonthselect_momentjs_format', 'dayofmonthtablecell_momentjs_format', 'hourselect_momentjs_format', 'minuteselect_momentjs_format', 'minuteselect_values', 'now_button_text', 'today_button_text', 'clear_button_text', 'hide_animation_duration_milliseconds'];
          for (_i = 0, _len = required_config_attributes.length; _i < _len; _i++) {
            configname = required_config_attributes[_i];
            configvalue = $scope.config[configname];
            if ((configvalue == null) || configvalue === '') {
              if (typeof console !== "undefined" && console !== null) {
                if (typeof console.error === "function") {
                  console.error("The " + configname + " config is required!");
                }
              }
            }
          }
          $scope.destinationField = angular.element("#" + $scope.config.destinationfieldid);
          if ($scope.destinationField.length === 0) {
            if (typeof console !== "undefined" && console !== null) {
              if (typeof console.error === "function") {
                console.error("Could not find the destinationField element with ID: " + $scope.config.destinationfieldid);
              }
            }
          }
          $scope.triggerButton = angular.element("#" + $scope.config.triggerbuttonid);
          if ($scope.triggerButton.length > 0) {
            $scope.triggerButton.on('click', function() {
              $scope.initialize();
              $scope.showPage1();
              $scope.$apply();
            });
            labelElement = angular.element("label[for=" + $scope.config.destinationfieldid + "]");
            if (labelElement.length > 0) {
              if (!labelElement.attr('id')) {
                labelElement.attr('id', "" + $scope.config.destinationfieldid + "_label");
              }
              $scope.triggerButton.attr('aria-labeledby', "" + (labelElement.attr('id')) + " " + $scope.config.previewid);
            }
          } else {
            if (typeof console !== "undefined" && console !== null) {
              if (typeof console.warn === "function") {
                console.warn("Could not find the triggerButton element with ID: " + $scope.config.triggerbuttonid);
              }
            }
          }
          $scope.previewElement = angular.element("#" + $scope.config.previewid);
          if ($scope.previewElement.length === 0) {
            if (typeof console !== "undefined" && console !== null) {
              if (typeof console.warn === "function") {
                console.warn("Could not find the previewElement element with ID: " + $scope.config.previewid);
              }
            }
          }
          previewTemplateScriptElement = angular.element("#" + $scope.config.previewtemplateid);
          if (previewTemplateScriptElement.length === 0) {
            if (typeof console !== "undefined" && console !== null) {
              if (typeof console.warn === "function") {
                console.warn("Could not find the previewTemplateScriptElement element " + ("with ID: " + $scope.config.previewtemplateid));
              }
            }
          } else {
            $scope.previewAngularjsTemplate = previewTemplateScriptElement.html();
          }
          $scope.datetimeSelectorElement = $element.find('.cradmin-legacy-datetime-selector');
          $scope.initialize();
          $scope.destinationField.on('change', function() {
            $scope.initialize();
            $scope.$apply();
            return $scope.__animatePreviewText(0);
          });
          $timeout(function() {
            return $element.find('select').on('keydown', function(e) {
              if (e.which === 13) {
                $scope.__onSelectEnterPressed();
                e.preventDefault();
              }
            });
          }, 100);
        }
      };
    }
  ]);

}).call(this);

(function() {
  var app;

  app = angular.module('cradminLegacy.forms.filewidget', []);

  app.controller('CradminFileFieldController', function($scope, $filter) {
    $scope.init = function() {
      $scope.$watch('cradmin_filefield_has_value', function(newValue) {
        if (newValue != null) {
          if (newValue) {
            return $scope.cradmin_filefield_clearcheckbox_value = '';
          } else {
            return $scope.cradmin_filefield_clearcheckbox_value = 'checked';
          }
        }
      });
    };
    $scope.cradminClearFileField = function() {
      return $scope.cradmin_filefield_clear_value = true;
    };
    $scope.init();
  });

  app.directive('cradminFilefieldValue', function() {
    return {
      scope: false,
      link: function($scope, element, attributes) {
        var fileFieldElement, setupFileFieldChangeListener;
        $scope.cradmin_filefield_clear_value = false;
        fileFieldElement = element;
        if ((attributes.cradminFilefieldValue != null) && attributes.cradminFilefieldValue !== "") {
          $scope.cradmin_filefield_has_value = true;
          $scope.cradmin_filefield_has_original_value = true;
        }
        setupFileFieldChangeListener = function() {
          return fileFieldElement.bind('change', function(changeEvent) {
            var reader;
            reader = new FileReader;
            reader.onload = function(loadEvent) {
              $scope.$apply(function() {
                $scope.cradmin_filefield_has_value = true;
                $scope.cradmin_filefield_has_original_value = false;
              });
            };
            reader.readAsDataURL(changeEvent.target.files[0]);
          });
        };
        $scope.$watch('cradmin_filefield_clear_value', function(newValue) {
          var newFileFieldElement;
          if (newValue) {
            $scope.cradmin_filefield_has_value = false;
            $scope.cradmin_filefield_clear_value = false;
            $scope.cradmin_filefield_has_original_value = false;
            newFileFieldElement = fileFieldElement.clone();
            jQuery(fileFieldElement).replaceWith(newFileFieldElement);
            fileFieldElement = newFileFieldElement;
            return setupFileFieldChangeListener();
          }
        });
        setupFileFieldChangeListener();
      }
    };
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.forms.modelchoicefield', []).provider('cradminLegacyModelChoiceFieldCoordinator', function() {
    var ModelChoiceFieldOverlay;
    ModelChoiceFieldOverlay = (function() {
      function ModelChoiceFieldOverlay(cradminLegacyWindowDimensions) {
        this.cradminLegacyWindowDimensions = cradminLegacyWindowDimensions;
        this.modelChoiceFieldIframeWrapper = null;
        this.bodyContentWrapperElement = angular.element('#cradmin_legacy_bodycontentwrapper');
        this.bodyElement = angular.element('body');
      }

      ModelChoiceFieldOverlay.prototype.registerModeChoiceFieldIframeWrapper = function(modelChoiceFieldIframeWrapper) {
        return this.modelChoiceFieldIframeWrapper = modelChoiceFieldIframeWrapper;
      };

      ModelChoiceFieldOverlay.prototype.onChangeValueBegin = function(fieldWrapperScope) {
        return this.modelChoiceFieldIframeWrapper.onChangeValueBegin(fieldWrapperScope);
      };

      ModelChoiceFieldOverlay.prototype.addBodyContentWrapperClass = function(cssclass) {
        return this.bodyContentWrapperElement.addClass(cssclass);
      };

      ModelChoiceFieldOverlay.prototype.removeBodyContentWrapperClass = function(cssclass) {
        return this.bodyContentWrapperElement.removeClass(cssclass);
      };

      ModelChoiceFieldOverlay.prototype.disableBodyScrolling = function() {
        return this.bodyElement.addClass('cradmin-legacy-noscroll');
      };

      ModelChoiceFieldOverlay.prototype.enableBodyScrolling = function() {
        this.bodyElement.removeClass('cradmin-legacy-noscroll');
        return this.cradminLegacyWindowDimensions.triggerWindowResizeEvent();
      };

      return ModelChoiceFieldOverlay;

    })();
    this.$get = [
      'cradminLegacyWindowDimensions', function(cradminLegacyWindowDimensions) {
        return new ModelChoiceFieldOverlay(cradminLegacyWindowDimensions);
      }
    ];
    return this;
  }).directive('cradminLegacyModelChoiceFieldIframeWrapper', [
    '$window', '$timeout', 'cradminLegacyModelChoiceFieldCoordinator', 'cradminLegacyWindowDimensions', function($window, $timeout, cradminLegacyModelChoiceFieldCoordinator, cradminLegacyWindowDimensions) {
      return {
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.origin = "" + window.location.protocol + "//" + window.location.host;
          $scope.bodyElement = angular.element($window.document.body);
          cradminLegacyModelChoiceFieldCoordinator.registerModeChoiceFieldIframeWrapper(this);
          this.setIframe = function(iframeScope) {
            return $scope.iframeScope = iframeScope;
          };
          this._setField = function(fieldScope) {
            return $scope.fieldScope = fieldScope;
          };
          this._setPreviewElement = function(previewElementScope) {
            return $scope.previewElementScope = previewElementScope;
          };
          this.setLoadSpinner = function(loadSpinnerScope) {
            return $scope.loadSpinnerScope = loadSpinnerScope;
          };
          this.setIframeWrapperInner = function(iframeInnerScope) {
            return $scope.iframeInnerScope = iframeInnerScope;
          };
          this.onChangeValueBegin = function(fieldWrapperScope) {
            this._setField(fieldWrapperScope.fieldScope);
            this._setPreviewElement(fieldWrapperScope.previewElementScope);
            $scope.iframeScope.beforeShowingIframe(fieldWrapperScope.iframeSrc);
            return $scope.show();
          };
          this.onIframeLoadBegin = function() {
            return $scope.loadSpinnerScope.show();
          };
          this.onIframeLoaded = function() {
            $scope.iframeInnerScope.show();
            return $scope.loadSpinnerScope.hide();
          };
          $scope.onChangeValue = function(event) {
            var data;
            if (event.origin !== $scope.origin) {
              console.error("Message origin '" + event.origin + "' does not match current origin '" + $scope.origin + "'.");
              return;
            }
            data = angular.fromJson(event.data);
            if ($scope.fieldScope.fieldid !== data.fieldid) {
              return;
            }
            $scope.fieldScope.setValue(data.value);
            $scope.previewElementScope.setPreviewHtml(data.preview);
            $scope.hide();
            return $scope.iframeScope.afterFieldValueChange();
          };
          $window.addEventListener('message', $scope.onChangeValue, false);
          $scope.onWindowResize = function(newWindowDimensions) {
            return $scope.iframeScope.setIframeSize();
          };
          $scope.show = function() {
            $scope.iframeWrapperElement.addClass('cradmin-legacy-floating-fullsize-iframe-wrapper-show');
            cradminLegacyModelChoiceFieldCoordinator.disableBodyScrolling();
            cradminLegacyModelChoiceFieldCoordinator.addBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper');
            cradminLegacyModelChoiceFieldCoordinator.addBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper-push');
            return cradminLegacyWindowDimensions.register($scope);
          };
          $scope.hide = function() {
            $scope.iframeWrapperElement.removeClass('cradmin-legacy-floating-fullsize-iframe-wrapper-show');
            cradminLegacyModelChoiceFieldCoordinator.removeBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper');
            cradminLegacyModelChoiceFieldCoordinator.removeBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper-push');
            cradminLegacyModelChoiceFieldCoordinator.enableBodyScrolling();
            $scope.iframeScope.onHide();
            return cradminLegacyWindowDimensions.unregister($scope);
          };
          this.closeIframe = function() {
            return $scope.hide();
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.iframeWrapperElement = element;
        }
      };
    }
  ]).directive('cradminLegacyModelChoiceFieldIframeWrapperInner', [
    '$window', function($window) {
      return {
        require: '^^cradminLegacyModelChoiceFieldIframeWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.scrollToTop = function() {
            return $scope.element.scrollTop(0);
          };
          $scope.show = function() {
            return $scope.element.removeClass('ng-hide');
          };
          $scope.hide = function() {
            return $scope.element.addClass('ng-hide');
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.element = element;
          wrapperCtrl.setIframeWrapperInner(scope);
        }
      };
    }
  ]).directive('cradminLegacyModelChoiceFieldIframeClosebutton', function() {
    return {
      require: '^cradminLegacyModelChoiceFieldIframeWrapper',
      restrict: 'A',
      scope: {},
      link: function(scope, element, attrs, iframeWrapperCtrl) {
        element.on('click', function(e) {
          e.preventDefault();
          return iframeWrapperCtrl.closeIframe();
        });
      }
    };
  }).directive('cradminLegacyModelChoiceFieldLoadSpinner', function() {
    return {
      require: '^^cradminLegacyModelChoiceFieldIframeWrapper',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        $scope.hide = function() {
          return $scope.element.addClass('ng-hide');
        };
        return $scope.show = function() {
          return $scope.element.removeClass('ng-hide');
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.element = element;
        wrapperCtrl.setLoadSpinner(scope);
      }
    };
  }).directive('cradminLegacyModelChoiceFieldIframe', [
    '$interval', function($interval) {
      return {
        require: '^cradminLegacyModelChoiceFieldIframeWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          var currentScrollHeight, getIframeDocument, getIframeScrollHeight, getIframeWindow, resizeIfScrollHeightChanges, scrollHeightInterval, startScrollHeightInterval, stopScrollHeightInterval;
          scrollHeightInterval = null;
          currentScrollHeight = 0;
          getIframeWindow = function() {
            return $scope.element.contents();
          };
          getIframeDocument = function() {
            return getIframeWindow()[0];
          };
          getIframeScrollHeight = function() {
            var iframeDocument;
            iframeDocument = getIframeDocument();
            if ((iframeDocument != null ? iframeDocument.body : void 0) != null) {
              return iframeDocument.body.scrollHeight;
            } else {
              return 0;
            }
          };
          resizeIfScrollHeightChanges = function() {
            var newScrollHeight;
            newScrollHeight = getIframeScrollHeight();
            if (newScrollHeight !== currentScrollHeight) {
              currentScrollHeight = newScrollHeight;
              return $scope.setIframeSize();
            }
          };
          startScrollHeightInterval = function() {
            if (scrollHeightInterval == null) {
              return scrollHeightInterval = $interval(resizeIfScrollHeightChanges, 500);
            }
          };
          stopScrollHeightInterval = function() {
            if (scrollHeightInterval != null) {
              $interval.cancel(scrollHeightInterval);
              return scrollHeightInterval = null;
            }
          };
          $scope.onHide = function() {
            return stopScrollHeightInterval();
          };
          $scope.afterFieldValueChange = function() {
            return stopScrollHeightInterval();
          };
          $scope.beforeShowingIframe = function(iframeSrc) {
            var currentSrc;
            currentSrc = $scope.element.attr('src');
            if ((currentSrc == null) || currentSrc === '' || currentSrc !== iframeSrc) {
              $scope.loadedSrc = currentSrc;
              $scope.wrapperCtrl.onIframeLoadBegin();
              $scope.resetIframeSize();
              $scope.element.attr('src', iframeSrc);
            }
            return startScrollHeightInterval();
          };
          $scope.setIframeSize = function() {};
          $scope.resetIframeSize = function() {};
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.element = element;
          scope.wrapperCtrl = wrapperCtrl;
          wrapperCtrl.setIframe(scope);
          scope.element.on('load', function() {
            wrapperCtrl.onIframeLoaded();
            return scope.setIframeSize();
          });
        }
      };
    }
  ]).directive('cradminLegacyModelChoiceFieldWrapper', [
    'cradminLegacyModelChoiceFieldCoordinator', function(cradminLegacyModelChoiceFieldCoordinator) {
      return {
        restrict: 'A',
        scope: {
          iframeSrc: '@cradminLegacyModelChoiceFieldWrapper'
        },
        controller: function($scope) {
          this.setField = function(fieldScope) {
            return $scope.fieldScope = fieldScope;
          };
          this.setPreviewElement = function(previewElementScope) {
            return $scope.previewElementScope = previewElementScope;
          };
          this.onChangeValueBegin = function() {
            return cradminLegacyModelChoiceFieldCoordinator.onChangeValueBegin($scope);
          };
        }
      };
    }
  ]).directive('cradminLegacyModelChoiceFieldInput', [
    'cradminLegacyModelChoiceFieldCoordinator', function(cradminLegacyModelChoiceFieldCoordinator) {
      return {
        require: '^^cradminLegacyModelChoiceFieldWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.setValue = function(value) {
            return $scope.inputElement.val(value);
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.inputElement = element;
          scope.fieldid = attrs['id'];
          wrapperCtrl.setField(scope);
        }
      };
    }
  ]).directive('cradminLegacyModelChoiceFieldPreview', [
    'cradminLegacyModelChoiceFieldCoordinator', function(cradminLegacyModelChoiceFieldCoordinator) {
      return {
        require: '^^cradminLegacyModelChoiceFieldWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.setPreviewHtml = function(previewHtml) {
            return $scope.previewElement.html(previewHtml);
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.previewElement = element;
          wrapperCtrl.setPreviewElement(scope);
        }
      };
    }
  ]).directive('cradminLegacyModelChoiceFieldChangebeginButton', [
    'cradminLegacyModelChoiceFieldCoordinator', function(cradminLegacyModelChoiceFieldCoordinator) {
      return {
        require: '^^cradminLegacyModelChoiceFieldWrapper',
        restrict: 'A',
        scope: {},
        link: function(scope, element, attrs, wrapperCtrl) {
          element.on('click', function(e) {
            e.preventDefault();
            return wrapperCtrl.onChangeValueBegin();
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.forms.select', []).directive('cradminLegacyOpenUrlStoredInSelectedOption', [
    function() {
      return {
        restrict: 'A',
        link: function($scope, $element, attributes) {
          var getValue;
          getValue = function() {
            return $element.find("option:selected").attr('value');
          };
          return $element.on('change', function() {
            var remoteUrl;
            remoteUrl = getValue();
            return window.location = value;
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  var app;

  app = angular.module('cradminLegacy.forms.setfieldvalue', ['cfp.hotkeys']);

  /**
  Directive for setting the value of a form field to specified value.
  
  Example:
  
  ```
    <button type="button"
            cradmin-legacy-setfieldvalue="2015-12-24 12:30"
            cradmin-legacy-setfieldvalue-field-id="my_datetimefield_id">
        Set value to 2015-12-24 12:30
    </button>
  ```
  
  You can make the directive change the focus on click after applying the
  value with ``cradmin-legacy-setfieldvalue-move-focus-on-click="<id>"``:
  
  ```
    <button type="button"
            cradmin-legacy-setfieldvalue="2015-12-24 12:30"
            cradmin-legacy-setfieldvalue-field-id="my_datetimefield_id"
            cradmin-legacy-setfieldvalue-move-focus-on-click="my_datetimefield_id">
        Set value to 2015-12-24 12:30
    </button>
  ```
  
  
  Can also be used on ``<a>``-elements. The directive uses ``e.preventDefault``
  to ensure the href is not triggered.
  */


  app.directive('cradminLegacySetfieldvalue', [
    function() {
      return {
        scope: {
          value: "@cradminLegacySetfieldvalue",
          fieldid: "@cradminLegacySetfieldvalueFieldId",
          moveFocusOnClick: "@cradminLegacySetfieldvalueMoveFocusOnClick"
        },
        link: function($scope, $element) {
          var fieldElement, focusElement;
          fieldElement = angular.element("#" + $scope.fieldid);
          if ($scope.moveFocusOnClick != null) {
            focusElement = angular.element("#" + $scope.moveFocusOnClick);
          }
          if (fieldElement.length === 0) {
            return typeof console !== "undefined" && console !== null ? typeof console.error === "function" ? console.error("Could not find a field with the '" + $scope.fieldid + "' ID.") : void 0 : void 0;
          } else {
            $element.on('click', function(e) {
              e.preventDefault();
              fieldElement.val($scope.value);
              fieldElement.trigger('change');
              if (focusElement != null) {
                return focusElement.focus();
              }
            });
          }
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.forms.usethisbutton', []).directive('cradminLegacyUseThis', [
    '$window', function($window) {
      /*
      The cradmin-legacy-use-this directive is used to select elements for
      the ``cradmin-legacy-model-choice-field`` directive. You add this directive
      to a button or a-element within an iframe, and this directive will use
      ``window.postMessage`` to send the needed information to the
      ``cradmin-legacy-model-choice-field-wrapper``.
      
      You may also use this if you create your own custom iframe communication
      receiver directive where a "use this" button within an iframe is needed.
      
      Example
      =======
      ```
        <a class="btn btn-default" cradmin-legacy-use-this="Peter Pan" cradmin-legacy-fieldid="id_name">
          Use this
        </a>
      ```
      
      How it works
      ============
      When the user clicks an element with this directive, the click
      is captured, the default action is prevented, and we decode the
      given JSON encoded value and add ``postmessageid='cradmin-legacy-use-this'``
      to the object making it look something like this::
      
        ```
        {
          postmessageid: 'cradmin-legacy-use-this',
          value: '<the value provided via the cradmin-legacy attribute>',
          fieldid: '<the fieldid provided via the cradmin-legacy-fieldid attribute>',
          preview: '<the preview HTML>'
        }
        ```
      
      We assume there is a event listener listening for the ``message`` event on
      the message in the parent of the iframe where this was clicked, but no checks
      ensuring this is made.
      */

      return {
        restrict: 'A',
        scope: {
          data: '@cradminLegacyUseThis'
        },
        link: function(scope, element, attrs) {
          element.on('click', function(e) {
            var data;
            e.preventDefault();
            data = angular.fromJson(scope.data);
            data.postmessageid = 'cradmin-legacy-use-this';
            return $window.parent.postMessage(angular.toJson(data), window.parent.location.href);
          });
        }
      };
    }
  ]).directive('cradminLegacyUseThisHidden', [
    '$window', function($window) {
      /*
      Works just like the ``cradmin-legacy-use-this`` directive, except this
      is intended to be triggered on load.
      
      The intended use-case is to trigger the same action as clicking a
      ``cradmin-legacy-use-this``-button but on load, typically after creating/adding
      a new item that the user wants to be selected without any further manual input.
      */

      return {
        restrict: 'A',
        scope: {
          data: '@cradminLegacyUseThisHidden'
        },
        link: function(scope, element, attrs) {
          var data;
          data = angular.fromJson(scope.data);
          data.postmessageid = 'cradmin-legacy-use-this';
          $window.parent.postMessage(angular.toJson(data), window.parent.location.href);
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.imagepreview', []).directive('cradminLegacyImagePreview', function() {
    /*
    A directive that shows a preview when an image field changes
    value.
    
    Components:
      - A wrapper (typically a DIV) using this directive (``cradmin-legacy-image-preview``)
      - An IMG element using the ``cradmin-legacy-image-preview-img`` directive. This is
        needed even if we have no initial image.
      - A file input field using the ``cradmin-legacy-image-preview-filefield`` directive.
    
    Example:
    
      <div cradmin-legacy-image-preview>
        <img cradmin-legacy-image-preview-img>
        <input type="file" name="myfile" cradmin-legacy-image-preview-filefield>
      </div>
    */

    var controller;
    controller = function($scope) {
      this.setImg = function(imgscope) {
        return $scope.cradminImagePreviewImage = imgscope;
      };
      this.previewFile = function(file) {
        return $scope.cradminImagePreviewImage.previewFile(file);
      };
    };
    return {
      restrict: 'A',
      controller: controller
    };
  }).directive('cradminLegacyImagePreviewImg', function() {
    var controller, link, onFilePreviewLoaded;
    onFilePreviewLoaded = function($scope, srcData) {
      $scope.element.attr('height', '');
      $scope.element[0].src = srcData;
      return $scope.element.removeClass('ng-hide');
    };
    controller = function($scope) {
      $scope.previewFile = function(file) {
        var reader;
        reader = new FileReader();
        reader.onload = function(evt) {
          return onFilePreviewLoaded($scope, evt.target.result);
        };
        return reader.readAsDataURL(file);
      };
    };
    link = function($scope, element, attrs, previewCtrl) {
      $scope.element = element;
      previewCtrl.setImg($scope);
      if ((element.attr('src') == null) || element.attr('src') === '') {
        element.addClass('ng-hide');
      }
    };
    return {
      require: '^cradminLegacyImagePreview',
      restrict: 'A',
      scope: {},
      controller: controller,
      link: link
    };
  }).directive('cradminLegacyImagePreviewFilefield', function() {
    var link;
    link = function($scope, element, attrs, previewCtrl) {
      $scope.previewCtrl = previewCtrl;
      $scope.element = element;
      $scope.wrapperelement = element.parent();
      element.bind('change', function(evt) {
        var file;
        if (evt.target.files != null) {
          file = evt.target.files[0];
          return $scope.previewCtrl.previewFile(file);
        }
      });
      element.bind('mouseover', function() {
        return $scope.wrapperelement.addClass('cradmin-legacy-filewidget-field-and-overlay-wrapper-hover');
      });
      element.bind('mouseleave', function() {
        return $scope.wrapperelement.removeClass('cradmin-legacy-filewidget-field-and-overlay-wrapper-hover');
      });
    };
    return {
      require: '^cradminLegacyImagePreview',
      restrict: 'A',
      scope: {},
      link: link
    };
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.iosaddtohomescreen', []).directive('iosAddToHomeScreen', [
    '$window', 'cradminDetectize', function($window, cradminDetectize) {
      return {
        transclude: true,
        template: '<div ng-transclude>This is my directive content</div>',
        link: function($scope, $element, attrs) {
          if (attrs.forceOs != null) {
            $scope.os = attrs.forceOs;
          } else {
            $scope.os = cradminDetectize.os.name;
          }
          if (attrs.forceBrowser != null) {
            $scope.browser = attrs.forceBrowser;
          } else {
            $scope.browser = cradminDetectize.browser.name;
          }
          if (attrs.forceDeviceModel != null) {
            $scope.deviceModel = attrs.forceDeviceModel;
          } else {
            $scope.deviceModel = cradminDetectize.device.model;
          }
          if ($scope.os === 'ios' && $scope.browser === 'safari') {
            $element.show();
          } else {
            $element.hide();
          }
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy', ['cradminLegacy.templates', 'cradminLegacy.directives', 'cradminLegacy.providers', 'cradminLegacy.calendar.providers', 'cradminLegacy.messages', 'cradminLegacy.detectizr', 'cradminLegacy.menu', 'cradminLegacy.objecttable', 'cradminLegacy.acemarkdown', 'cradminLegacy.bulkfileupload', 'cradminLegacy.iosaddtohomescreen', 'cradminLegacy.imagepreview', 'cradminLegacy.collapse', 'cradminLegacy.modal', 'cradminLegacy.scrollfixed', 'cradminLegacy.pagepreview', 'cradminLegacy.forms.modelchoicefield', 'cradminLegacy.forms.usethisbutton', 'cradminLegacy.forms.datetimewidget', 'cradminLegacy.forms.filewidget', 'cradminLegacy.forms.setfieldvalue', 'cradminLegacy.forms.select', 'cradminLegacy.forms.clearabletextinput', 'cradminLegacy.backgroundreplace_element.providers', 'cradminLegacy.backgroundreplace_element.directives', 'cradminLegacy.listfilter.directives', 'cradminLegacy.multiselect2.services', 'cradminLegacy.multiselect2.directives', 'cradminLegacy.loadmorepager.services', 'cradminLegacy.loadmorepager.directives']);

}).call(this);

(function() {
  angular.module('cradminLegacy.listfilter.directives', []).directive('cradminLegacyListfilter', [
    '$window', '$timeout', 'cradminLegacyBgReplaceElement', function($window, $timeout, cradminLegacyBgReplaceElement) {
      return {
        restrict: 'A',
        scope: {
          options: '=cradminLegacyListfilter'
        },
        controller: function($scope, $element) {
          var $messageElement, filterListDomId, filterScopes, hideMessage, loadInProgress, onLoadSuccess, queueMessage, setLoadFinished, setLoadInProgress, showMessage, showMessageTimer;
          filterListDomId = $element.attr('id');
          filterScopes = [];
          loadInProgress = false;
          $messageElement = null;
          showMessageTimer = null;
          this.loadIsInProgress = function() {
            return loadInProgress;
          };
          setLoadInProgress = function(options) {
            var filterScope, _i, _len, _results;
            loadInProgress = true;
            $scope.targetElement.attr('aria-busy', 'true');
            _results = [];
            for (_i = 0, _len = filterScopes.length; _i < _len; _i++) {
              filterScope = filterScopes[_i];
              _results.push(filterScope.onLoadInProgress(options.filterDomId));
            }
            return _results;
          };
          setLoadFinished = function(options) {
            var filterScope, _i, _len;
            loadInProgress = false;
            for (_i = 0, _len = filterScopes.length; _i < _len; _i++) {
              filterScope = filterScopes[_i];
              filterScope.onLoadFinished(options.filterDomId);
            }
            return $scope.targetElement.attr('aria-busy', 'false');
          };
          onLoadSuccess = function($remoteHtmlDocument, remoteUrl) {
            var $remoteFilterList, filterScope, parsedRemoteUrl, title, _i, _len, _results;
            $remoteFilterList = $remoteHtmlDocument.find('#' + filterListDomId);
            title = $window.document.title;
            parsedRemoteUrl = URI(remoteUrl);
            parsedRemoteUrl.removeSearch('cradmin-bgreplaced').normalizeQuery();
            console.log(parsedRemoteUrl.toString());
            $window.history.pushState("list filter change", title, parsedRemoteUrl.toString());
            _results = [];
            for (_i = 0, _len = filterScopes.length; _i < _len; _i++) {
              filterScope = filterScopes[_i];
              _results.push(filterScope.syncWithRemoteFilterList($remoteFilterList));
            }
            return _results;
          };
          showMessage = function(variant, message) {
            var aria_role, loadspinner;
            hideMessage();
            $scope.targetElement.removeClass('cradmin-legacy-listfilter-target-loaderror');
            loadspinner = "";
            aria_role = 'alert';
            if (variant === 'error') {
              $scope.targetElement.addClass('cradmin-legacy-listfilter-target-loaderror');
              aria_role = 'alert';
            } else if (variant === 'loading') {
              $scope.targetElement.addClass('cradmin-legacy-listfilter-target-loading');
              aria_role = 'progressbar';
              if ($scope.options.loadspinner_css_class != null) {
                loadspinner = "<span class='cradmin-legacy-listfilter-message-loadspinner " + ("" + $scope.options.loadspinner_css_class + "' aria-hidden='true'></span>");
              }
            } else {
              throw new Error("Invalid message variant: " + variant);
            }
            $messageElement = angular.element(("<div aria-role='" + aria_role + "' ") + ("class='cradmin-legacy-listfilter-message cradmin-legacy-listfilter-message-" + variant + "'>") + ("" + loadspinner) + ("<span class='cradmin-legacy-listfilter-message-text'>" + message + "</span></div>"));
            return $messageElement.prependTo($scope.targetElement);
          };
          queueMessage = function(variant, message) {
            if (showMessageTimer != null) {
              $timeout.cancel(showMessageTimer);
            }
            return showMessageTimer = $timeout(function() {
              return showMessage(variant, message);
            }, $scope.options.loadingmessage_delay_milliseconds);
          };
          hideMessage = function() {
            if (showMessageTimer != null) {
              $timeout.cancel(showMessageTimer);
            }
            if ($messageElement) {
              $messageElement.remove();
              $messageElement = null;
            }
            return $scope.targetElement.removeClass('cradmin-legacy-listfilter-target-loading');
          };
          this.load = function(options) {
            setLoadInProgress(options);
            queueMessage('loading', options.loadingmessage);
            return cradminLegacyBgReplaceElement.load({
              parameters: {
                method: 'GET',
                url: options.remoteUrl
              },
              remoteElementSelector: '#' + $scope.options.target_dom_id,
              targetElement: $scope.targetElement,
              $scope: $scope,
              replace: true,
              onHttpError: function(response) {
                if (typeof console !== "undefined" && console !== null) {
                  if (typeof console.error === "function") {
                    console.error('Error while filtering', response);
                  }
                }
                return showMessage('error', $scope.options.loaderror_message);
              },
              onSuccess: function($remoteHtmlDocument) {
                onLoadSuccess($remoteHtmlDocument, options.remoteUrl);
                if (options.onLoadSuccess != null) {
                  return options.onLoadSuccess(options.onLoadSuccessData);
                }
              },
              onFinish: function() {
                setLoadFinished(options);
                return hideMessage();
              }
            });
          };
          this.addFilterScope = function(filterScope) {
            return filterScopes.push(filterScope);
          };
        },
        link: function($scope, $element, attributes) {
          $scope.targetElement = angular.element('#' + $scope.options.target_dom_id);
          angular.element($window).on('popstate', function(e) {
            var state;
            state = e.originalEvent.state;
            if (state) {
              return $window.location.reload();
            }
          });
        }
      };
    }
  ]).directive('cradminLegacyListfilterSelect', [
    function() {
      return {
        restrict: 'A',
        require: '^cradminLegacyListfilter',
        scope: {
          options: '=cradminLegacyListfilterSelect'
        },
        controller: function($scope, $element) {
          /*
          Replace all <option>-elements with new <option>-elements from the server.
          */

          $scope.syncWithRemoteFilterList = function($remoteFilterList) {
            var $remoteElement, domId;
            domId = $element.attr('id');
            $remoteElement = $remoteFilterList.find('#' + domId);
            $element.empty();
            return $element.append(angular.element($remoteElement.html()));
          };
          $scope.onLoadInProgress = function(filterDomId) {
            return $element.prop('disabled', true);
          };
          $scope.onLoadFinished = function(filterDomId) {
            return $element.prop('disabled', false);
          };
        },
        link: function($scope, $element, attributes, listfilterCtrl) {
          var getValue;
          listfilterCtrl.addFilterScope($scope);
          getValue = function() {
            return $element.find("option:selected").attr('value');
          };
          $element.on('change', function() {
            var remoteUrl;
            remoteUrl = getValue();
            return listfilterCtrl.load({
              remoteUrl: remoteUrl,
              filterDomId: $element.attr('id'),
              loadingmessage: $scope.options.loadingmessage,
              onLoadSuccess: function() {
                return $element.focus();
              }
            });
          });
        }
      };
    }
  ]).directive('cradminLegacyListfilterTextinput', [
    '$timeout', function($timeout) {
      var emptyvalueUrlAttribute, urlpatternAttribute, urlpatternReplaceText;
      urlpatternAttribute = 'cradmin-legacy-listfilter-urlpattern';
      emptyvalueUrlAttribute = 'cradmin-legacy-listfilter-emptyvalue-url';
      urlpatternReplaceText = '_-_TEXTINPUT_-_VALUE_-_';
      return {
        restrict: 'A',
        require: '^cradminLegacyListfilter',
        scope: {
          options: '=cradminLegacyListfilterTextinput'
        },
        controller: function($scope, $element) {
          /*
          Update the "cradmin-legacy-listfilter-urlpattern"-attribute with
          the one from the server.
          */

          $scope.syncWithRemoteFilterList = function($remoteFilterList) {
            var $remoteElement, domId;
            domId = $element.attr('id');
            $remoteElement = $remoteFilterList.find('#' + domId);
            $element.attr(urlpatternAttribute, $remoteElement.attr(urlpatternAttribute));
            return $element.attr(emptyvalueUrlAttribute, $remoteElement.attr(emptyvalueUrlAttribute));
          };
          $scope.onLoadInProgress = function(filterDomId) {
            if (filterDomId !== $element.attr('id')) {
              return $element.prop('disabled', true);
            }
          };
          $scope.onLoadFinished = function(filterDomId) {
            return $element.prop('disabled', false);
          };
        },
        link: function($scope, $element, attributes, listfilterCtrl) {
          var applySearchTimer, buildUrl, loadSearch, loadedValue, onLoadSearchSuccess, onValueChange, timeoutMilliseconds;
          listfilterCtrl.addFilterScope($scope);
          applySearchTimer = null;
          loadedValue = $element.val();
          timeoutMilliseconds = $scope.options.timeout_milliseconds;
          if (timeoutMilliseconds == null) {
            timeoutMilliseconds = 500;
          }
          buildUrl = function(value) {
            var encodedValue, urlpattern;
            value = value.trim();
            if (value === '') {
              return $element.attr(emptyvalueUrlAttribute);
            } else {
              urlpattern = $element.attr(urlpatternAttribute);
              encodedValue = URI.encodeQuery(value);
              console.log(value);
              console.log(encodedValue);
              return urlpattern.replace($scope.options.urlpattern_replace_text, encodedValue);
            }
          };
          onLoadSearchSuccess = function(data) {
            var currentValue;
            currentValue = $element.val();
            if (data.value !== currentValue) {
              onValueChange(true);
            }
            return loadedValue = data.value;
          };
          loadSearch = function() {
            var remoteUrl, value;
            if (listfilterCtrl.loadIsInProgress()) {
              return;
            }
            value = $element.val();
            if (loadedValue === value) {
              return;
            }
            remoteUrl = buildUrl(value);
            loadedValue = value;
            return listfilterCtrl.load({
              remoteUrl: remoteUrl,
              onLoadSuccess: onLoadSearchSuccess,
              onLoadSuccessData: {
                value: value
              },
              filterDomId: $element.attr('id'),
              loadingmessage: $scope.options.loadingmessage
            });
          };
          onValueChange = function(useTimeout) {
            if (applySearchTimer != null) {
              $timeout.cancel(applySearchTimer);
            }
            if (!listfilterCtrl.loadIsInProgress()) {
              if (useTimeout) {
                return applySearchTimer = $timeout(loadSearch, timeoutMilliseconds);
              } else {
                return loadSearch();
              }
            }
          };
          $element.on('change', function() {
            return onValueChange(false);
          });
          $element.on('keydown', function(e) {
            if (e.which === 13) {
              return onValueChange(false);
            } else {
              return onValueChange(true);
            }
          });
        }
      };
    }
  ]).directive('cradminLegacyListfilterCheckboxlist', [
    function() {
      return {
        restrict: 'A',
        require: '^cradminLegacyListfilter',
        scope: {
          options: '=cradminLegacyListfilterCheckboxlist'
        },
        controller: function($scope, $element) {
          /*
          Replace all contents with new elements from the server.
          */

          $scope.syncWithRemoteFilterList = function($remoteFilterList) {
            var $remoteElement, domId;
            domId = $element.attr('id');
            $remoteElement = $remoteFilterList.find('#' + domId);
            $element.empty();
            $element.append(angular.element($remoteElement.html()));
            return $scope.registerCheckboxChangeListeners(true);
          };
          $scope.onLoadInProgress = function(filterDomId) {
            return $element.find('input').prop('disabled', true);
          };
          $scope.onLoadFinished = function(filterDomId) {
            return $element.find('input').prop('disabled', false);
          };
        },
        link: function($scope, $element, attributes, listfilterCtrl) {
          var getUrl, onLoadSuccess;
          listfilterCtrl.addFilterScope($scope);
          getUrl = function($inputElement) {
            return $inputElement.attr('data-url');
          };
          onLoadSuccess = function(data) {
            return $element.find('#' + data.checkboxId).focus();
          };
          $scope.onCheckboxChange = function(e) {
            var checkboxId, remoteUrl;
            remoteUrl = getUrl(angular.element(e.target));
            checkboxId = angular.element(e.target).attr('id');
            return listfilterCtrl.load({
              remoteUrl: remoteUrl,
              filterDomId: $element.attr('id'),
              onLoadSuccess: onLoadSuccess,
              onLoadSuccessData: {
                checkboxId: checkboxId
              },
              loadingmessage: $scope.options.loadingmessage
            });
          };
          $scope.registerCheckboxChangeListeners = function(removeFirst) {
            if (removeFirst) {
              $element.find('input').off('change', $scope.onCheckboxChange);
            }
            return $element.find('input').on('change', $scope.onCheckboxChange);
          };
          $scope.registerCheckboxChangeListeners(false);
        }
      };
    }
  ]).directive('cradminLegacyListfilterRadiolist', [
    function() {
      return {
        restrict: 'A',
        require: '^cradminLegacyListfilter',
        scope: {
          options: '=cradminLegacyListfilterRadiolist'
        },
        controller: function($scope, $element) {
          /*
          Replace all contents with new elements from the server.
          */

          $scope.syncWithRemoteFilterList = function($remoteFilterList) {
            var $remoteElement, domId;
            domId = $element.attr('id');
            $remoteElement = $remoteFilterList.find('#' + domId);
            $element.empty();
            $element.append(angular.element($remoteElement.html()));
            return $scope.registerCheckboxChangeListeners(true);
          };
          $scope.onLoadInProgress = function(filterDomId) {
            return $element.find('input').prop('disabled', true);
          };
          $scope.onLoadFinished = function(filterDomId) {
            return $element.find('input').prop('disabled', false);
          };
        },
        link: function($scope, $element, attributes, listfilterCtrl) {
          var getUrl, onLoadSuccess;
          listfilterCtrl.addFilterScope($scope);
          getUrl = function($inputElement) {
            return $inputElement.attr('data-url');
          };
          onLoadSuccess = function(data) {
            return $element.find('#' + data.checkboxId).focus();
          };
          $scope.onRadioChange = function(e) {
            var checkboxId, remoteUrl;
            remoteUrl = getUrl(angular.element(e.target));
            checkboxId = angular.element(e.target).attr('id');
            return listfilterCtrl.load({
              remoteUrl: remoteUrl,
              filterDomId: $element.attr('id'),
              onLoadSuccess: onLoadSuccess,
              onLoadSuccessData: {
                checkboxId: checkboxId
              },
              loadingmessage: $scope.options.loadingmessage
            });
          };
          $scope.registerCheckboxChangeListeners = function(removeFirst) {
            if (removeFirst) {
              $element.find('input').off('change', $scope.onRadioChange);
            }
            return $element.find('input').on('change', $scope.onRadioChange);
          };
          $scope.registerCheckboxChangeListeners(false);
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.loadmorepager.directives', []).directive('cradminLegacyLoadMorePager', [
    '$timeout', 'cradminLegacyBgReplaceElement', 'cradminLegacyLoadmorepagerCoordinator', function($timeout, cradminLegacyBgReplaceElement, cradminLegacyLoadmorepagerCoordinator) {
      var pagerWrapperCssSelector;
      pagerWrapperCssSelector = '.cradmin-legacy-loadmorepager';
      return {
        restrict: 'A',
        scope: true,
        controller: function($scope, $element) {
          $scope.loadmorePagerIsLoading = false;
          $scope.getNextPageNumber = function() {
            return $scope.loadmorePagerOptions.nextPageNumber;
          };
          $scope.pagerLoad = function(options) {
            var $targetElement, nextPageUrl, replaceMode, updatedQueryDictAttributes;
            options = angular.extend({}, $scope.loadmorePagerOptions, options);
            $scope.loadmorePagerIsLoading = true;
            $targetElement = angular.element(options.targetElementCssSelector);
            replaceMode = false;
            nextPageUrl = URI();
            updatedQueryDictAttributes = {};
            if (options.mode === "reloadPageOneOnLoad") {
              replaceMode = true;
            } else if (options.mode === "loadAllOnClick") {
              replaceMode = true;
              nextPageUrl.setSearch('disablePaging', "true");
            } else {
              nextPageUrl.setSearch(options.pageQueryStringAttribute, $scope.getNextPageNumber());
            }
            return cradminLegacyBgReplaceElement.load({
              parameters: {
                method: 'GET',
                url: nextPageUrl.toString()
              },
              remoteElementSelector: options.targetElementCssSelector,
              targetElement: $targetElement,
              $scope: $scope,
              replace: replaceMode,
              onHttpError: function(response) {
                return typeof console !== "undefined" && console !== null ? typeof console.error === "function" ? console.error('ERROR loading page', response) : void 0 : void 0;
              },
              onSuccess: function($remoteHtmlDocument) {
                if (options.mode === "reloadPageOneOnLoad") {
                  $targetElement.removeClass('cradmin-legacy-loadmorepager-target-reloading-page1');
                } else {
                  $element.addClass('cradmin-legacy-loadmorepager-hidden');
                }
                if (options.onSuccess != null) {
                  return options.onSuccess();
                }
              },
              onFinish: function() {
                return $scope.loadmorePagerIsLoading = false;
              }
            });
          };
        },
        link: function($scope, $element, attributes) {
          var domId;
          $scope.loadmorePagerOptions = {
            pageQueryStringAttribute: "page",
            mode: "loadMoreOnClick"
          };
          if ((attributes.cradminLegacyLoadMorePager != null) && attributes.cradminLegacyLoadMorePager !== '') {
            angular.extend($scope.loadmorePagerOptions, angular.fromJson(attributes.cradminLegacyLoadMorePager));
          }
          if ($scope.loadmorePagerOptions.targetElementCssSelector == null) {
            throw Error('Missing required option: targetElementCssSelector');
          }
          domId = $element.attr('id');
          cradminLegacyLoadmorepagerCoordinator.registerPager(domId, $scope);
          $scope.$on("$destroy", function() {
            return cradminLegacyLoadmorepagerCoordinator.unregisterPager(domId, $scope);
          });
          if ($scope.loadmorePagerOptions.mode === "reloadPageOneOnLoad") {
            $timeout(function() {
              return $scope.pagerLoad();
            }, 500);
          }
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.loadmorepager.services', []).factory('cradminLegacyLoadmorepagerCoordinator', function() {
    /*
    Coordinates between cradminLegacyLoadMorePager directives.
    */

    var Coordinator;
    Coordinator = (function() {
      function Coordinator() {
        this.targets = {};
      }

      Coordinator.prototype.registerPager = function(targetDomId, pagerScope) {
        if (this.targets[targetDomId] == null) {
          this.targets[targetDomId] = {};
        }
        return this.targets[targetDomId][pagerScope.getNextPageNumber()] = pagerScope;
      };

      Coordinator.prototype.unregisterPager = function(targetDomId, pagerScope) {
        return del(this.targets[targetDomId][pagerScope.getNextPageNumber()]);
      };

      Coordinator.prototype.__getPagerScope = function(targetDomId, nextPageNumber) {
        var pagerScope, target;
        target = this.targets[targetDomId];
        if (target == null) {
          throw Error("No target with ID '" + targetDomId + "' registered with cradminLegacyLoadmorepagerCoordinator.");
        }
        pagerScope = target[nextPageNumber];
        if (pagerScope == null) {
          throw Error(("No pagerScope for targetDomId='" + targetDomId + "' and nextPageNumber=" + nextPageNumber + " ") + "registered with cradminLegacyLoadmorepagerCoordinator.");
        }
        return pagerScope;
      };

      return Coordinator;

    })();
    return new Coordinator();
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.menu', []).directive('cradminLegacyMenu', [
    function() {
      /** Menu that collapses automatically on small displays.
      
      Example
      =======
      
      ```html
      <nav cradmin-legacy-menu class="cradmin-legacy-menu">
        <div class="cradmin-legacy-menu-mobileheader">
          <a href="#" role="button"
              class="cradmin-legacy-menu-mobiletoggle"
              ng-click="cradminMenuTogglePressed()"
              ng-class="{'cradmin-legacy-menu-mobile-toggle-button-expanded': cradminMenuDisplay}"
              aria-pressed="{{ getAriaPressed() }}">
            Menu
          </a>
        </div>
        <div class="cradmin-legacy-menu-content"
            ng-class="{'cradmin-legacy-menu-content-display': cradminMenuDisplay}">
          <ul>
            <li><a href="#">Menu item 1</a></li>
            <li><a href="#">Menu item 2</a></li>
          </ul>
        </div>
      </nav>
      ```
      
      Design notes
      ============
      
      The example uses css classes provided by the default cradmin CSS, but
      you specify all classes yourself, so you can easily provide your own
      css classes and still use the directive.
      */

      return {
        scope: true,
        controller: function($scope, cradminLegacyPagePreview) {
          $scope.cradminMenuDisplay = false;
          $scope.cradminMenuTogglePressed = function() {
            return $scope.cradminMenuDisplay = !$scope.cradminMenuDisplay;
          };
          $scope.getAriaPressed = function() {
            if ($scope.cradminMenuDisplay) {
              return 'true';
            } else {
              return 'false';
            }
          };
          this.close = function() {
            $scope.cradminMenuDisplay = false;
            return $scope.$apply();
          };
        }
      };
    }
  ]).directive('cradminLegacyMenuAutodetectOverflowY', [
    'cradminLegacyWindowDimensions', function(cradminLegacyWindowDimensions) {
      /**
      */

      return {
        require: '?cradminLegacyMenu',
        controller: function($scope) {
          var disableInitialWatcher;
          $scope.onWindowResize = function(newWindowDimensions) {
            return $scope.setOrUnsetOverflowYClass();
          };
          $scope.setOrUnsetOverflowYClass = function() {
            var menuDomElement, _ref;
            menuDomElement = (_ref = $scope.menuElement) != null ? _ref[0] : void 0;
            if (menuDomElement != null) {
              if (menuDomElement.clientHeight < menuDomElement.scrollHeight) {
                return $scope.menuElement.addClass($scope.overflowYClass);
              } else {
                return $scope.menuElement.removeClass($scope.overflowYClass);
              }
            }
          };
          disableInitialWatcher = $scope.$watch(function() {
            var _ref;
            if (((_ref = $scope.menuElement) != null ? _ref[0] : void 0) != null) {
              return true;
            } else {
              return false;
            }
          }, function(newValue) {
            if (newValue) {
              $scope.setOrUnsetOverflowYClass();
              return disableInitialWatcher();
            }
          });
        },
        link: function($scope, element, attrs) {
          $scope.overflowYClass = attrs.cradminLegacyMenuAutodetectOverflowY;
          $scope.menuElement = element;
          cradminLegacyWindowDimensions.register($scope);
          $scope.$on('$destroy', function() {
            return cradminLegacyWindowDimensions.unregister($scope);
          });
        }
      };
    }
  ]).directive('cradminLegacyMenuCloseOnClick', [
    function() {
      /** Directive that you can put on menu links to automatically close the
      menu on click.
      */

      return {
        require: '^^cradminLegacyMenu',
        link: function(scope, element, attrs, cradminLegacyMenuCtrl) {
          element.on('click', function() {
            cradminLegacyMenuCtrl.close();
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.messages', []).controller('DjangoCradminMessagesCtrl', [
    '$scope', '$timeout', function($scope, $timeout) {
      $scope.loading = true;
      $timeout(function() {
        return $scope.loading = false;
      }, 650);
      $scope.messageHidden = {};
      $scope.hideMessage = function(index) {
        return $scope.messageHidden[index] = true;
      };
      $scope.messageIsHidden = function(index) {
        return $scope.messageHidden[index];
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.modal', []).directive('cradminLegacyModalWrapper', [
    function() {
      /** Shows a modal window on click.
      
      Example
      =======
      
      ```html
      <div cradmin-legacy-modal-wrapper>
        <button ng-click="showModal($event)" type="button">
          Show modal window
        </button>
        <div cradmin-legacy-modal class="cradmin-legacy-modal"
                ng-class="{'cradmin-legacy-modal-visible': modalVisible}">
            <div class="cradmin-legacy-modal-backdrop" ng-click="hideModal()"></div>
            <div class="cradmin-legacy-modal-content">
                <p>Something here</p>
                <button ng-click="hideModal()" type="button">
                  Hide modal window
                </button>
            </div>
        </div>
      </div>
      ```
      */

      return {
        scope: true,
        controller: function($scope) {
          var bodyElement;
          $scope.modalVisible = false;
          bodyElement = angular.element('body');
          $scope.showModal = function(e) {
            if (e != null) {
              e.preventDefault();
            }
            $scope.modalVisible = true;
            bodyElement.addClass('cradmin-legacy-noscroll');
          };
          $scope.hideModal = function() {
            $scope.modalVisible = false;
            bodyElement.removeClass('cradmin-legacy-noscroll');
          };
        }
      };
    }
  ]).directive('cradminLegacyModal', [
    function() {
      return {
        require: '^^cradminLegacyModalWrapper',
        link: function($scope, element) {
          var body;
          body = angular.element('body');
          return element.appendTo(body);
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.multiselect2.directives', []).directive('cradminLegacyMultiselect2Target', [
    'cradminLegacyMultiselect2Coordinator', '$window', function(cradminLegacyMultiselect2Coordinator, $window) {
      return {
        restrict: 'A',
        scope: true,
        controller: function($scope, $element) {
          var domId;
          domId = $element.attr('id');
          $scope.selectedItemsScope = null;
          if (domId == null) {
            throw Error('Elements using cradmin-legacy-multiselect2-target must have an id.');
          }
          cradminLegacyMultiselect2Coordinator.registerTarget(domId, $scope);
          $scope.$on("$destroy", function() {
            return cradminLegacyMultiselect2Coordinator.unregisterTarget(domId);
          });
          $scope.select = function(selectScope) {
            /*
            Called by cradminLegacyMultiselect2Select via
            cradminLegacyMultiselect2Coordinator when an item is selected.
            
            Calls ``cradminLegacyMultiselect2TargetSelectedItems.select()``.
            */

            $scope.selectedItemsScope.select(selectScope);
            if (!$scope.$$phase) {
              return $scope.$apply();
            }
          };
          $scope.isSelected = function(selectScope) {
            /*
            Called by cradminLegacyMultiselect2Select via
            cradminLegacyMultiselect2Coordinator to check if the item is selected.
            */

            return $scope.selectedItemsScope.isSelected(selectScope);
          };
          $scope.hasItems = function() {
            var _ref;
            return (_ref = $scope.selectedItemsScope) != null ? _ref.hasItems() : void 0;
          };
          this.setSelectedItemsScope = function(selectedItemsScope) {
            return $scope.selectedItemsScope = selectedItemsScope;
          };
          this.getSelectedItemsScope = function() {
            return $scope.selectedItemsScope;
          };
        },
        link: function($scope, $element, attributes) {
          var options;
          $scope.options = {
            updateFormActionToWindowLocation: false
          };
          if (attributes.cradminLegacyMultiselect2Target !== '') {
            options = angular.fromJson(attributes.cradminLegacyMultiselect2Target);
            angular.merge($scope.options, options);
          }
          $element.on('submit', function(e) {
            if ($scope.options.updateFormActionToWindowLocation) {
              return $element.attr('action', $window.location.href);
            }
          });
        }
      };
    }
  ]).directive('cradminLegacyMultiselect2TargetSelectedItems', [
    '$compile', 'cradminLegacyMultiselect2Coordinator', function($compile, cradminLegacyMultiselect2Coordinator) {
      var selectedItemCssClass;
      selectedItemCssClass = 'cradmin-legacy-multiselect2-target-selected-item';
      return {
        restrict: 'A',
        require: '^cradminLegacyMultiselect2Target',
        scope: true,
        controller: function($scope, $element) {
          $scope.selectedItemsCount = 0;
          $scope.selectedItemsData = {};
          $scope.select = function(selectScope) {
            var html, linkingFunction, loadedElement, previewHtml, selectButtonDomId;
            previewHtml = selectScope.getPreviewHtml();
            selectButtonDomId = selectScope.getDomId();
            html = ("<div id='" + selectButtonDomId + "_selected_item'") + ("cradmin-legacy-multiselect2-target-selected-item='" + selectButtonDomId + "' ") + ("class='" + selectedItemCssClass + "'>") + ("" + previewHtml + "</div>");
            linkingFunction = $compile(html);
            loadedElement = linkingFunction($scope);
            angular.element(loadedElement).appendTo($element);
            $scope.selectedItemsCount += 1;
            return $scope.selectedItemsData[selectButtonDomId] = selectScope.getCustomData();
          };
          $scope.deselectSelectedItem = function(selectedItemScope) {
            $scope.selectedItemsCount -= 1;
            delete $scope.selectedItemsData[selectedItemScope.selectButtonDomId];
            return cradminLegacyMultiselect2Coordinator.onDeselect(selectedItemScope.selectButtonDomId);
          };
          $scope.isSelected = function(selectScope) {
            var selectButtonDomId;
            selectButtonDomId = selectScope.getDomId();
            return $element.find("#" + selectButtonDomId + "_selected_item").length > 0;
          };
          $scope.hasItems = function() {
            return $scope.selectedItemsCount > 0;
          };
          $scope.getItemsCustomDataList = function() {
            var customData, customDataList, selectButtonDomId, _ref;
            customDataList = [];
            _ref = $scope.selectedItemsData;
            for (selectButtonDomId in _ref) {
              customData = _ref[selectButtonDomId];
              customDataList.push(customData);
            }
            return customDataList;
          };
        },
        link: function($scope, $element, attributes, targetCtrl) {
          targetCtrl.setSelectedItemsScope($scope);
        }
      };
    }
  ]).directive('cradminLegacyMultiselect2TargetSelectedItem', [
    'cradminLegacyMultiselect2Coordinator', function(cradminLegacyMultiselect2Coordinator) {
      return {
        restrict: 'A',
        scope: true,
        controller: function($scope, $element) {
          $scope.deselect = function() {
            $element.remove();
            $scope.deselectSelectedItem($scope);
          };
        },
        link: function($scope, $element, attributes) {
          $scope.selectButtonDomId = attributes.cradminLegacyMultiselect2TargetSelectedItem;
        }
      };
    }
  ]).directive('cradminLegacyMultiselect2Select', [
    '$rootScope', 'cradminLegacyMultiselect2Coordinator', function($rootScope, cradminLegacyMultiselect2Coordinator) {
      var itemWrapperSelectedCssClass;
      itemWrapperSelectedCssClass = 'cradmin-legacy-multiselect2-item-wrapper-selected';
      return {
        restrict: 'A',
        scope: {
          options: '=cradminLegacyMultiselect2Select'
        },
        controller: function($scope, $element) {
          var unregisterBgReplaceEventHandler;
          $scope.getPreviewHtml = function() {
            var $containerElement, $previewElement;
            $containerElement = $element.parents($scope.options.preview_container_css_selector);
            $previewElement = $containerElement.find($scope.options.preview_css_selector);
            return $previewElement.html();
          };
          $scope.getDomId = function() {
            return $element.attr('id');
          };
          $scope.getListElementCssSelector = function() {
            return $scope.options.listelement_css_selector;
          };
          $scope.onDeselect = function() {
            /*
            Called by cradminLegacyMultiselect2Coordinator when the item is deselected.
            */

            return $scope.getItemWrapperElement().removeClass(itemWrapperSelectedCssClass);
          };
          $scope.markAsSelected = function() {
            return $scope.getItemWrapperElement().addClass(itemWrapperSelectedCssClass);
          };
          $scope.getItemWrapperElement = function() {
            return $element.closest($scope.options.item_wrapper_css_selector);
          };
          $scope.getTargetDomId = function() {
            return $scope.options.target_dom_id;
          };
          $scope.getCustomData = function() {
            if ($scope.options.custom_data != null) {
              return $scope.options.custom_data;
            } else {
              return {};
            }
          };
          unregisterBgReplaceEventHandler = $scope.$on('cradminLegacyBgReplaceElementEvent', function(event, options) {
            var targetDomId;
            if ($element.closest(options.remoteElementSelector).length > 0) {
              targetDomId = $scope.options.target_dom_id;
              if (cradminLegacyMultiselect2Coordinator.isSelected(targetDomId, $scope)) {
                return $scope.markAsSelected();
              }
            }
          });
          cradminLegacyMultiselect2Coordinator.registerSelectScope($scope);
          $scope.$on('$destroy', function() {
            unregisterBgReplaceEventHandler();
            return cradminLegacyMultiselect2Coordinator.unregisterSelectScope($scope);
          });
        },
        link: function($scope, $element, attributes) {
          var select, targetScopeExistsWatcherCancel;
          select = function() {
            return cradminLegacyMultiselect2Coordinator.select($scope);
          };
          if ($scope.options.is_selected) {
            if (cradminLegacyMultiselect2Coordinator.targetScopeExists($scope.getTargetDomId())) {
              select();
            } else {
              targetScopeExistsWatcherCancel = $scope.$watch(function() {
                return cradminLegacyMultiselect2Coordinator.targetScopeExists($scope.getTargetDomId());
              }, function(newValue, oldValue) {
                if (newValue) {
                  select();
                  return targetScopeExistsWatcherCancel();
                }
              });
            }
          }
          $element.on('click', function(e) {
            e.preventDefault();
            return select();
          });
        }
      };
    }
  ]).directive('cradminLegacyMultiselect2Selectall', [
    '$rootScope', 'cradminLegacyMultiselect2Coordinator', function($rootScope, cradminLegacyMultiselect2Coordinator) {
      return {
        restrict: 'A',
        scope: true,
        controller: function($scope, $element) {},
        link: function($scope, $element, attributes) {
          var selectAll, targetDomId;
          $scope.options = angular.fromJson(attributes.cradminLegacyMultiselect2Selectall);
          targetDomId = $scope.options.target_dom_id;
          selectAll = function() {
            return cradminLegacyMultiselect2Coordinator.selectAll(targetDomId);
          };
          $element.on('click', function(e) {
            e.preventDefault();
            return $scope.pagerLoad({
              onSuccess: function() {
                return selectAll();
              }
            });
          });
        }
      };
    }
  ]).directive('cradminLegacyMultiselect2UseThis', [
    '$window', function($window) {
      /*
      The ``cradmin-legacy-multiselect2-use-this`` directive is used to select elements for
      the ``cradmin-legacy-model-choice-field`` directive. You add this directive
      to a button or a-element within an iframe, and this directive will use
      ``window.postMessage`` to send the needed information to the
      ``cradmin-legacy-model-choice-field-wrapper``.
      
      You may also use this if you create your own custom iframe communication
      receiver directive where a "use this" button within an iframe is needed.
      
      Example
      =======
      ```
        <button type="button"
                class="btn btn-default"
                cradmin-legacy-multiselect2-use-this='{"fieldid": "id_name"}'>
            Use this
        </button>
      ```
      
      How it works
      ============
      When the user clicks an element with this directive, the click
      is captured, the default action is prevented, and we decode the
      given JSON encoded value and add ``postmessageid='cradmin-legacy-use-this'``
      to the object making it look something like this::
      
        ```
        {
          postmessageid: 'cradmin-legacy-use-this',
          value: '<JSON encoded data for the selected items>',
          preview: '<preview HTML for the selected items>'
          <all options provided to the directive>
        }
        ```
      
      We assume there is a event listener listening for the ``message`` event on
      the message in the parent of the iframe where this was clicked, but no checks
      ensuring this is made.
      */

      return {
        restrict: 'A',
        require: '^cradminLegacyMultiselect2Target',
        scope: {
          data: '@cradminLegacyMultiselect2UseThis'
        },
        link: function($scope, $element, attributes, targetCtrl) {
          var getSelectedItemsData;
          getSelectedItemsData = function() {
            var allData, itemData, _i, _len, _ref;
            allData = {
              values: [],
              preview: ""
            };
            _ref = targetCtrl.getSelectedItemsScope().getItemsCustomDataList();
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              itemData = _ref[_i];
              allData.values.push(itemData.value);
              allData.preview += itemData.preview;
            }
            return allData;
          };
          $element.on('click', function(e) {
            var data, selectedItemsData;
            e.preventDefault();
            data = angular.fromJson($scope.data);
            data.postmessageid = 'cradmin-legacy-use-this';
            selectedItemsData = getSelectedItemsData();
            data.value = angular.toJson(selectedItemsData.values);
            data.preview = selectedItemsData.preview;
            return $window.parent.postMessage(angular.toJson(data), window.parent.location.href);
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.multiselect2.services', []).factory('cradminLegacyMultiselect2Coordinator', function() {
    /*
    Coordinates between cradminLegacyMultiselect2Select
    and cradminLegacyMultiselect2Target.
    */

    var Coordinator;
    Coordinator = (function() {
      function Coordinator() {
        this.targets = {};
        this.selectScopes = {};
      }

      Coordinator.prototype.registerTarget = function(targetDomId, targetScope) {
        return this.targets[targetDomId] = targetScope;
      };

      Coordinator.prototype.unregisterTarget = function(targetDomId, targetScope) {
        return delete this.targets[targetDomId];
      };

      Coordinator.prototype.__getTargetScope = function(targetDomId) {
        var targetScope;
        targetScope = this.targets[targetDomId];
        if (targetScope == null) {
          throw Error("No target with ID '" + targetDomId + "' registered with cradminLegacyMultiselect2Coordinator.");
        }
        return targetScope;
      };

      Coordinator.prototype.targetScopeExists = function(targetDomId) {
        return this.targets[targetDomId] != null;
      };

      Coordinator.prototype.select = function(selectScope) {
        var targetScope;
        targetScope = this.__getTargetScope(selectScope.getTargetDomId());
        if (!targetScope.isSelected(selectScope)) {
          targetScope.select(selectScope);
          return selectScope.markAsSelected();
        }
      };

      Coordinator.prototype.onDeselect = function(selectButtonDomId) {
        var $selectElement, selectScope;
        $selectElement = angular.element('#' + selectButtonDomId);
        if ($selectElement != null) {
          selectScope = $selectElement.isolateScope();
          if (selectScope != null) {
            return selectScope.onDeselect();
          }
        }
      };

      Coordinator.prototype.isSelected = function(targetDomId, selectScope) {
        var targetScope;
        targetScope = this.__getTargetScope(targetDomId);
        return targetScope.isSelected(selectScope);
      };

      Coordinator.prototype.registerSelectScope = function(selectScope) {
        var listIndex, _ref;
        if (((_ref = this.selectScopes[selectScope.getTargetDomId()]) != null ? _ref.map[selectScope.getDomId()] : void 0) != null) {
          return console.log(("selectScope with id=" + (selectScope.getDomId()) + " is already ") + ("registered for target " + (selectScope.getTargetDomId())));
        } else {
          if (this.selectScopes[selectScope.getTargetDomId()] == null) {
            this.selectScopes[selectScope.getTargetDomId()] = {
              map: {},
              list: []
            };
          }
          listIndex = this.selectScopes[selectScope.getTargetDomId()].list.push(selectScope);
          return this.selectScopes[selectScope.getTargetDomId()].map[selectScope.getDomId()] = listIndex;
        }
      };

      Coordinator.prototype.unregisterSelectScope = function(selectScope) {
        var listIndex, _ref;
        if (((_ref = this.selectScopes[selectScope.getTargetDomId()]) != null ? _ref.map[selectScope.getDomId()] : void 0) != null) {
          listIndex = this.selectScopes[selectScope.getTargetDomId()][selectScope.getDomId()];
          this.selectScopes[selectScope.getTargetDomId()].list.splice(listIndex, 1);
          return delete this.selectScopes[selectScope.getTargetDomId()].map[selectScope.getDomId()];
        } else {
          throw Error(("selectScope with id=" + (selectScope.getDomId()) + " is not ") + ("registered for target " + (selectScope.getTargetDomId())));
        }
      };

      Coordinator.prototype.selectAll = function(targetDomId) {
        var selectScope, _i, _len, _ref, _results;
        _ref = this.selectScopes[targetDomId].list;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          selectScope = _ref[_i];
          _results.push(this.select(selectScope));
        }
        return _results;
      };

      return Coordinator;

    })();
    return new Coordinator();
  });

}).call(this);

(function() {
  angular.module('cradminLegacy.objecttable', []).controller('CradminMultiselectObjectTableViewController', [
    '$scope', function($scope) {
      $scope.selectAllChecked = false;
      $scope.numberOfSelected = 0;
      $scope.selectedAction = null;
      $scope.setCheckboxValue = function(itemkey, value) {
        return $scope.items[itemkey] = value;
      };
      $scope.getCheckboxValue = function(itemkey) {
        return $scope.items[itemkey];
      };
      $scope.toggleAllCheckboxes = function() {
        $scope.selectAllChecked = !$scope.selectAllChecked;
        $scope.numberOfSelected = 0;
        return angular.forEach($scope.items, function(checked, itemkey) {
          $scope.setCheckboxValue(itemkey, $scope.selectAllChecked);
          if ($scope.selectAllChecked) {
            return $scope.numberOfSelected += 1;
          }
        });
      };
      return $scope.toggleCheckbox = function(itemkey) {
        var newvalue;
        newvalue = !$scope.getCheckboxValue(itemkey);
        $scope.setCheckboxValue(itemkey, newvalue);
        if (newvalue) {
          return $scope.numberOfSelected += 1;
        } else {
          $scope.numberOfSelected -= 1;
          return $scope.selectAllChecked = false;
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.pagepreview', []).provider('cradminLegacyPagePreview', function() {
    var PagePreview;
    PagePreview = (function() {
      function PagePreview() {
        this.pagePreviewWrapper = null;
        this.bodyContentWrapperElement = angular.element('#cradmin_legacy_bodycontentwrapper');
        this.bodyElement = angular.element('body');
      }

      PagePreview.prototype.registerPagePreviewWrapper = function(pagePreviewWrapper) {
        return this.pagePreviewWrapper = pagePreviewWrapper;
      };

      PagePreview.prototype.setPreviewConfig = function(previewConfig) {
        return this.pagePreviewWrapper.setPreviewConfig(previewConfig);
      };

      PagePreview.prototype.addBodyContentWrapperClass = function(cssclass) {
        return this.bodyContentWrapperElement.addClass(cssclass);
      };

      PagePreview.prototype.removeBodyContentWrapperClass = function(cssclass) {
        return this.bodyContentWrapperElement.removeClass(cssclass);
      };

      PagePreview.prototype.disableBodyScrolling = function() {
        return this.bodyElement.addClass('cradmin-legacy-noscroll');
      };

      PagePreview.prototype.enableBodyScrolling = function() {
        return this.bodyElement.removeClass('cradmin-legacy-noscroll');
      };

      return PagePreview;

    })();
    this.$get = function() {
      return new PagePreview();
    };
    return this;
  }).directive('cradminLegacyPagePreviewWrapper', [
    '$window', '$timeout', 'cradminLegacyPagePreview', function($window, $timeout, cradminLegacyPagePreview) {
      /*
      A directive that shows a preview of a page in an iframe.
      value.
      
      Components:
      
        - A DIV using this directive (``cradmin-legacy-page-preview-wrapper``)
          with the following child elements:
          - A child DIV using the ``cradmin-legacy-page-preview-iframe-wrapper``
            directive with the following child elements:
            - A "Close" link/button using the ``cradmin-legacy-page-preview-iframe-closebutton`` directive.
            - A IFRAME element using the ``cradmin-legacy-page-preview-iframe`` directive.
          - A child element with one of the following directives:
            - ``cradmin-legacy-page-preview-open-on-page-load`` to show the preview when the page loads.
            - ``cradmin-legacy-page-preview-open-on-click`` to show the preview when the element is clicked.
      
      The outer wrapper (``cradmin-legacy-page-preview-wrapper``) coordinates everything.
      
      You can have one wrapper with many ``cradmin-legacy-page-preview-open-on-click`` directives.
      This is typically used in listings where each item in the list has its own preview button.
      Just wrap the entire list in a ``cradmin-legacy-page-preview-wrapper``, add the
      ``cradmin-legacy-page-preview-iframe-wrapper`` before the list, and a button/link with
      the ``cradmin-legacy-page-preview-open-on-click``-directive for each entry in the list.
      
      
      Example:
      
      ```
      <div cradmin-legacy-page-preview-wrapper>
          <div class="cradmin-legacy-floating-fullsize-iframe-wrapper"
               cradmin-legacy-page-preview-iframe-wrapper>
              <a href="#" class="cradmin-legacy-floating-fullsize-iframe-closebutton"
                 cradmin-legacy-page-preview-iframe-closebutton>
                  <span class="fa fa-close"></span>
                  <span class="sr-only">Close preview</span>
              </a>
              <div class="ng-hide cradmin-legacy-floating-fullsize-loadspinner">
                  <span class="fa fa-spinner fa-spin"></span>
              </div>
              <div class="cradmin-legacy-floating-fullsize-iframe-inner">
                  <iframe cradmin-legacy-page-preview-iframe></iframe>
              </div>
          </div>
      
          <div cradmin-legacy-page-preview-open-on-page-load="'/some/view'"></div>
      </div>
      ```
      */

      return {
        restrict: 'A',
        scope: {},
        controller: function($scope, cradminLegacyPagePreview) {
          var previewConfigWaitingForStartup;
          cradminLegacyPagePreview.registerPagePreviewWrapper(this);
          $scope.origin = "" + window.location.protocol + "//" + window.location.host;
          $scope.mainWindow = angular.element($window);
          $scope.windowDimensions = null;
          previewConfigWaitingForStartup = null;
          this.setIframeWrapper = function(iframeWrapperScope) {
            $scope.iframeWrapperScope = iframeWrapperScope;
            return this._readyCheck();
          };
          this.setIframe = function(iframeScope) {
            $scope.iframeScope = iframeScope;
            return this._readyCheck();
          };
          this.setNavbar = function(navbarScope) {
            $scope.navbarScope = navbarScope;
            return this._readyCheck();
          };
          this.setLoadSpinner = function(loadSpinnerScope) {
            $scope.loadSpinnerScope = loadSpinnerScope;
            return this._readyCheck();
          };
          this.setIframeWrapperInner = function(iframeInnerScope) {
            return $scope.iframeInnerScope = iframeInnerScope;
          };
          this.showNavbar = function() {
            return $scope.iframeWrapperScope.showNavbar();
          };
          this.setUrl = function(url) {
            $scope.loadSpinnerScope.show();
            $scope.iframeInnerScope.scrollToTop();
            return $scope.iframeScope.setUrl(url);
          };
          this._readyCheck = function() {
            var isReady;
            isReady = ($scope.iframeInnerScope != null) && ($scope.loadSpinnerScope != null) && ($scope.navbarScope != null) && ($scope.iframeScope != null) && ($scope.iframeWrapperScope != null);
            if (isReady) {
              return this._onReady();
            }
          };
          this._onReady = function() {
            if (previewConfigWaitingForStartup != null) {
              return this._applyPreviewConfig();
            }
          };
          this._applyPreviewConfig = function() {
            var url;
            url = previewConfigWaitingForStartup.urls[0].url;
            $scope.navbarScope.setConfig(previewConfigWaitingForStartup);
            $scope.iframeInnerScope.hide();
            previewConfigWaitingForStartup = null;
            this.showPreview();
            return this.setUrl(url);
          };
          this.setPreviewConfig = function(previewConfig) {
            /*
            Called once on startup
            */

            previewConfigWaitingForStartup = previewConfig;
            return this._readyCheck();
          };
          this.showPreview = function() {
            cradminLegacyPagePreview.addBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper');
            $scope.iframeWrapperScope.show();
            return $scope.mainWindow.bind('resize', $scope.onWindowResize);
          };
          this.hidePreview = function() {
            $scope.iframeWrapperScope.hide();
            $scope.mainWindow.unbind('resize', $scope.onWindowResize);
            return cradminLegacyPagePreview.removeBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper');
          };
          this.onIframeLoaded = function() {
            $scope.iframeInnerScope.show();
            return $scope.loadSpinnerScope.hide();
          };
          $scope.getWindowDimensions = function() {
            return {
              height: $scope.mainWindow.height(),
              width: $scope.mainWindow.width()
            };
          };
          $scope.$watch('windowDimensions', (function(newSize, oldSize) {
            $scope.iframeScope.setIframeSize();
          }), true);
          $scope.onWindowResize = function() {
            $timeout.cancel($scope.applyResizeTimer);
            $scope.applyResizeTimer = $timeout(function() {
              $scope.windowDimensions = $scope.getWindowDimensions();
              return $scope.$apply();
            }, 300);
          };
        },
        link: function(scope, element) {}
      };
    }
  ]).directive('cradminLegacyPagePreviewIframeWrapper', [
    '$window', 'cradminLegacyPagePreview', function($window, cradminLegacyPagePreview) {
      return {
        require: '^^cradminLegacyPagePreviewWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.show = function() {
            $scope.iframeWrapperElement.addClass('cradmin-legacy-floating-fullsize-iframe-wrapper-show');
            cradminLegacyPagePreview.disableBodyScrolling();
            return cradminLegacyPagePreview.addBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper-push');
          };
          $scope.hide = function() {
            $scope.iframeWrapperElement.removeClass('cradmin-legacy-floating-fullsize-iframe-wrapper-show');
            cradminLegacyPagePreview.enableBodyScrolling();
            return cradminLegacyPagePreview.removeBodyContentWrapperClass('cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper-push');
          };
          $scope.showNavbar = function() {
            return $scope.iframeWrapperElement.addClass('cradmin-legacy-floating-fullsize-iframe-wrapper-with-navbar');
          };
          $scope.scrollToTop = function() {
            return $scope.iframeWrapperElement.scrollTop(0);
          };
          this.hide = function() {
            return $scope.hide();
          };
          this.show = function() {
            return $scope.show();
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.iframeWrapperElement = element;
          wrapperCtrl.setIframeWrapper(scope);
        }
      };
    }
  ]).directive('cradminLegacyPagePreviewIframeWrapperInner', [
    '$window', function($window) {
      return {
        require: '^^cradminLegacyPagePreviewWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.scrollToTop = function() {
            return $scope.element.scrollTop(0);
          };
          $scope.show = function() {
            return $scope.element.removeClass('ng-hide');
          };
          $scope.hide = function() {
            return $scope.element.addClass('ng-hide');
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.element = element;
          wrapperCtrl.setIframeWrapperInner(scope);
        }
      };
    }
  ]).directive('cradminLegacyPagePreviewIframeClosebutton', function() {
    return {
      require: '^^cradminLegacyPagePreviewWrapper',
      restrict: 'A',
      scope: {},
      link: function(scope, element, attrs, wrapperCtrl) {
        element.on('click', function(e) {
          e.preventDefault();
          return wrapperCtrl.hidePreview();
        });
      }
    };
  }).directive('cradminLegacyPagePreviewLoadSpinner', function() {
    return {
      require: '^^cradminLegacyPagePreviewWrapper',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        $scope.hide = function() {
          return $scope.element.addClass('ng-hide');
        };
        return $scope.show = function() {
          return $scope.element.removeClass('ng-hide');
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.element = element;
        wrapperCtrl.setLoadSpinner(scope);
      }
    };
  }).directive('cradminLegacyPagePreviewNavbar', function() {
    return {
      require: '^^cradminLegacyPagePreviewWrapper',
      restrict: 'A',
      scope: {
        mobileMenuHeader: '@cradminLegacyPagePreviewNavbarMobileMenuHeader'
      },
      templateUrl: 'pagepreview/navbar.tpl.html',
      controller: function($scope) {
        $scope.activeIndex = 0;
        $scope.activeUrlConfig = null;
        $scope.setConfig = function(previewConfig) {
          if (previewConfig.urls.length > 1) {
            $scope.previewConfig = previewConfig;
            $scope.setActive(0);
            $scope.$apply();
            return $scope.wrapperCtrl.showNavbar();
          }
        };
        return $scope.setActive = function(index) {
          $scope.activeIndex = index;
          return $scope.activeUrlConfig = $scope.previewConfig.urls[$scope.activeIndex];
        };
      },
      link: function($scope, element, attrs, wrapperCtrl) {
        $scope.element = element;
        $scope.wrapperCtrl = wrapperCtrl;
        $scope.wrapperCtrl.setNavbar($scope);
        $scope.onNavlinkClick = function(e, index) {
          e.preventDefault();
          $scope.setActive(index);
          $scope.wrapperCtrl.setUrl($scope.previewConfig.urls[index].url);
        };
      }
    };
  }).directive('cradminLegacyPagePreviewIframe', function() {
    return {
      require: '^^cradminLegacyPagePreviewWrapper',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        $scope.setUrl = function(url) {
          $scope.element.attr('src', url);
          return $scope.resetIframeSize();
        };
        $scope.setIframeSize = function() {
          var iframeBodyHeight, iframeDocument, iframeWindow;
          iframeWindow = $scope.element.contents();
          iframeDocument = iframeWindow[0];
          if (iframeDocument != null) {
            iframeBodyHeight = iframeDocument.body.offsetHeight;
            return $scope.element.height(iframeBodyHeight + 60);
          }
        };
        return $scope.resetIframeSize = function() {
          return $scope.element.height('40px');
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.element = element;
        wrapperCtrl.setIframe(scope);
        scope.element.on('load', function() {
          wrapperCtrl.onIframeLoaded();
          return scope.setIframeSize();
        });
      }
    };
  }).directive('cradminLegacyPagePreviewOpenOnPageLoad', [
    'cradminLegacyPagePreview', function(cradminLegacyPagePreview) {
      /*
      A directive that opens the given URL in an iframe overlay instantly (on page load).
      */

      return {
        restrict: 'A',
        scope: {
          previewConfig: '=cradminLegacyPagePreviewOpenOnPageLoad'
        },
        link: function(scope, element, attrs) {
          cradminLegacyPagePreview.setPreviewConfig(scope.previewConfig);
        }
      };
    }
  ]).directive('cradminLegacyPagePreviewOpenOnClick', [
    'cradminLegacyPagePreview', function(cradminLegacyPagePreview) {
      /*
      A directive that opens the given URL in an iframe overlay on click.
      */

      return {
        restrict: 'A',
        scope: {
          previewConfig: '=cradminLegacyPagePreviewOpenOnClick'
        },
        link: function(scope, element, attrs) {
          element.on('click', function(e) {
            e.preventDefault();
            return cradminLegacyPagePreview.setPreviewConfig(scope.previewConfig);
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  angular.module('cradminLegacy.scrollfixed', []).directive('cradminLegacyScrollTopFixed', [
    'cradminLegacyWindowScrollTop', function(cradminLegacyWindowScrollTop) {
      /** Keep an item aligned relative to a given top pixel position on the screen when scrolling.
      
      Example
      =======
      
      ```html
      <div cradmin-legacy-scroll-top-fixed>
        Some content here.
      </div>
      ```
      
      Make sure you style your element with absolute position. Example:
      
      ```
      position: absolute;
      top: 0;
      left: 0;
      ```
      
      Uses the initial top position as the offset. This means that you can style an element
      with something like this:
      
      ```
      position: absolute;
      top: 40px;
      right: 90px;
      ```
      
      And have it stay 40px from the top of the viewarea.
      
      Handling mobile devices
      =======================
      You may not want to scroll content on small displays. You
      should solve this with CSS media queries - simply do not
      use ``position: absolute;`` for the screen sizes you do
      not want to scroll.
      */

      var isUsingDefaultScroll, swapClasses, swapCssClasses;
      isUsingDefaultScroll = true;
      swapClasses = false;
      swapCssClasses = function($scope, $element, newWindowTopPosition) {
        var settings;
        settings = $scope.cradminLegacyScrollTopFixedSettings;
        if (newWindowTopPosition >= $scope.cradminLegacyScrollTopFixedInitialTopOffset) {
          if (isUsingDefaultScroll) {
            $element.removeClass(settings.cssClasses.defaultClass);
            $element.addClass(settings.cssClasses.scrollClass);
            return isUsingDefaultScroll = false;
          }
        } else if (newWindowTopPosition < $scope.cradminLegacyScrollTopFixedInitialTopOffset) {
          if (!isUsingDefaultScroll) {
            $element.addClass(settings.cssClasses.defaultClass);
            $element.removeClass(settings.cssClasses.scrollClass);
            return isUsingDefaultScroll = true;
          }
        }
      };
      return {
        controller: function($scope, $element, $attrs) {
          $scope.cradminLegacyScrollTopFixedSettings = $scope.$eval($attrs.cradminLegacyScrollTopFixed);
          if ($scope.cradminLegacyScrollTopFixedSettings.cssClasses != null) {
            if ($scope.cradminLegacyScrollTopFixedSettings.cssClasses.defaultClass && $scope.cradminLegacyScrollTopFixedSettings.cssClasses.scrollClass) {
              swapClasses = true;
            }
          }
          $scope.onWindowScrollTopStart = function() {
            var _ref;
            if (((_ref = $scope.cradminLegacyScrollTopFixedSettings.cssClasses) != null ? _ref.scrollingClass : void 0) != null) {
              return $element.addClass($scope.cradminLegacyScrollTopFixedSettings.cssClasses.scrollingClass);
            }
          };
          $scope.onWindowScrollTop = function(newWindowTopPosition, initialScrollTrigger) {
            var newTopPosition, offset, _ref;
            if (swapClasses) {
              swapCssClasses($scope, $element, newWindowTopPosition);
            }
            offset = $scope.cradminLegacyScrollTopFixedInitialTopOffset;
            if ($scope.cradminLegacyScrollTopFixedSettings.pinToTopOnScroll) {
              if (newWindowTopPosition > offset) {
                offset = 0;
              } else {
                offset = offset - newWindowTopPosition;
              }
            }
            newTopPosition = newWindowTopPosition + offset;
            $scope.cradminLegacyScrollTopFixedElement.css('top', "" + newTopPosition + "px");
            if (((_ref = $scope.cradminLegacyScrollTopFixedSettings.cssClasses) != null ? _ref.scrollingClass : void 0) != null) {
              return $element.removeClass($scope.cradminLegacyScrollTopFixedSettings.cssClasses.scrollingClass);
            }
          };
        },
        link: function($scope, element, attrs) {
          $scope.cradminLegacyScrollTopFixedElement = element;
          $scope.cradminLegacyScrollTopFixedInitialTopOffset = parseInt(element.css('top'), 10) || 0;
          cradminLegacyWindowScrollTop.register($scope);
          $scope.$on('$destroy', function() {
            return cradminLegacyWindowScrollTop.unregister($scope);
          });
        }
      };
    }
  ]);

}).call(this);

angular.module('cradminLegacy.templates', ['acemarkdown/acemarkdown.tpl.html', 'bulkfileupload/fileinfo.tpl.html', 'bulkfileupload/progress.tpl.html', 'bulkfileupload/rejectedfiles.tpl.html', 'forms/dateselector.tpl.html', 'pagepreview/navbar.tpl.html']);

angular.module("acemarkdown/acemarkdown.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("acemarkdown/acemarkdown.tpl.html",
    "<div ng-transclude></div>");
}]);

angular.module("bulkfileupload/fileinfo.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bulkfileupload/fileinfo.tpl.html",
    "<p class=\"cradmin-legacy-bulkfileupload-progress-item\"\n" +
    "        ng-class=\"{\n" +
    "            'cradmin-legacy-bulkfileupload-progress-item-finished': fileInfo.finished,\n" +
    "            'cradmin-legacy-bulkfileupload-progress-item-error cradmin-legacy-bulkfileupload-errorparagraph': fileInfo.hasErrors\n" +
    "        }\">\n" +
    "    <span class=\"cradmin-legacy-bulkfileupload-iteminfo\">\n" +
    "        <span class=\"cradmin-legacy-progressbar\">\n" +
    "            <span class=\"cradmin-legacy-progressbar-progress\" ng-style=\"{'width': fileInfo.percent+'%'}\">&nbsp;</span>\n" +
    "            <span class=\"cradmin-legacy-progresspercent\" role='progressbar' aria-valuenow=\"{{ fileInfo.percent }}\" aria-valuemin=\"0\" aria-valuemax=\"100\"\n" +
    "                    aria-labelledby=\"id_uploadfilename_{{ fileInfo.temporaryfileid }}\">\n" +
    "                <span class=\"cradmin-legacy-progresspercent-number\" aria-hidden=\"true\">{{ fileInfo.percent }}</span>%\n" +
    "            </span>\n" +
    "        </span>\n" +
    "        <span id=\"id_uploadfilename_{{ fileInfo.temporaryfileid }}\" style=\"display: none;\">{{fileInfo.name}}: {{fileInfo.i18nStrings.upload_status}} {{ fileInfo.percent }}%</span>\n" +
    "        <span class=\"cradmin-legacy-filename\" aria-hidden=\"true\">{{fileInfo.name}}</span>\n" +
    "    </span>\n" +
    "\n" +
    "    <button cradmin-legacy-bulkfileupload-remove-file-button=\"fileInfo\"\n" +
    "            ng-if=\"fileInfo.finished\"\n" +
    "            type=\"button\"\n" +
    "            class=\"btn btn-link cradmin-legacy-bulkfileupload-remove-file-button\"\n" +
    "            aria-describedby=\"id_uploadfilename_{{ fileInfo.temporaryfileid }}\">\n" +
    "        <span ng-if=\"!fileInfo.isRemoving &amp;&amp; !fileInfo.autosubmit\"\n" +
    "              class=\"cradmin-legacy-bulkfileupload-remove-file-button-isnotremoving\">\n" +
    "            <span class=\"fa fa-times\"></span>\n" +
    "            <span class=\"sr-only\">{{fileInfo.i18nStrings.remove_file_label}}</span>\n" +
    "        </span>\n" +
    "        <span ng-if=\"fileInfo.isRemoving\"\n" +
    "              class=\"cradmin-legacy-bulkfileupload-remove-file-button-isremoving\">\n" +
    "            <span class=\"fa fa-spinner fa-spin\"></span>\n" +
    "            <span class=\"sr-only\">{{fileInfo.i18nStrings.removing_file_message}}</span>\n" +
    "        </span>\n" +
    "    </button>\n" +
    "</p>\n" +
    "");
}]);

angular.module("bulkfileupload/progress.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bulkfileupload/progress.tpl.html",
    "<div class=\"cradmin-legacy-bulkfileupload-progress\">\n" +
    "    <div ng-repeat=\"fileInfo in fileInfoArray\" aria-live='assertive'>\n" +
    "        <div cradmin-legacy-bulk-file-info=\"fileInfo\"\n" +
    "             class=\"cradmin-legacy-bulkfileupload-progress-file\"></div>\n" +
    "    </div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("bulkfileupload/rejectedfiles.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bulkfileupload/rejectedfiles.tpl.html",
    "<div class=\"cradmin-legacy-bulkfileupload-rejectedfiles\">\n" +
    "    <p ng-repeat=\"fileInfo in rejectedFiles\"\n" +
    "            class=\"cradmin-legacy-bulkfileupload-rejectedfile cradmin-legacy-bulkfileupload-errorparagraph\">\n" +
    "\n" +
    "        <span class=\"cradmin-legacy-bulkfileupload-iteminfo\">\n" +
    "            <span class=\"cradmin-legacy-bulkfileupload-rejectedfile-filename\">{{ fileInfo.name }}:</span>\n" +
    "            <span ng-repeat=\"(errorfield,errors) in fileInfo.errors\">\n" +
    "                <span ng-repeat=\"error in errors\"\n" +
    "                    class=\"cradmin-legacy-bulkfileupload-error\">\n" +
    "                    {{ error.message }}\n" +
    "                </span>\n" +
    "            </span>\n" +
    "        </span>\n" +
    "\n" +
    "        <button ng-click=\"closeMessage(fileInfo)\"\n" +
    "                type=\"button\"\n" +
    "                class=\"btn btn-link cradmin-legacy-bulkfileupload-error-closebutton\">\n" +
    "            <span class=\"fa fa-times\"></span>\n" +
    "            <span class=\"sr-only\">{{fileInfo.i18nStrings.close_errormessage_label}}</span>\n" +
    "        </button>\n" +
    "    </p>\n" +
    "</div>\n" +
    "");
}]);

angular.module("forms/dateselector.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("forms/dateselector.tpl.html",
    "<div class=\"cradmin-legacy-datetime-selector\"\n" +
    "        ng-class=\"{\n" +
    "            'cradmin-legacy-datetime-selector-show': page != null,\n" +
    "            'cradmin-legacy-datetime-selector-page1': page == 1,\n" +
    "            'cradmin-legacy-datetime-selector-page2': page == 2,\n" +
    "            'cradmin-legacy-datetime-selector-page3': page == 3,\n" +
    "            'cradmin-legacy-datetime-selector-has-shortcuts': hasShortcuts()\n" +
    "        }\">\n" +
    "\n" +
    "    <div class=\"cradmin-legacy-datetime-selector-backdrop\"></div>\n" +
    "\n" +
    "    <div class=\"cradmin-legacy-datetime-selector-contentwrapper\">\n" +
    "        <div class=\"cradmin-legacy-datetime-selector-closeoverlay\" ng-click=\"hide()\"></div>\n" +
    "        <div class=\"cradmin-legacy-datetime-selector-page cradmin-legacy-datetime-selector-dateview\">\n" +
    "            <button type=\"button\" class=\"sr-only\" ng-focus=\"onFocusHead()\"></button>\n" +
    "            <button type=\"button\"\n" +
    "                    class=\"btn btn-link cradmin-legacy-datetime-selector-closebutton\"\n" +
    "                    aria-label=\"{{ config.close_screenreader_text }}\"\n" +
    "                    ng-click=\"hide()\">\n" +
    "                        <span class=\"{{ config.close_icon }}\" aria-hidden=\"true\"></span>\n" +
    "                    </button>\n" +
    "\n" +
    "            <div class=\"cradmin-legacy-datetime-selector-selectors-wrapper\">\n" +
    "                <div class=\"cradmin-legacy-datetime-selector-selectors\">\n" +
    "                    <div class=\"cradmin-legacy-datetime-selector-dateselectors\">\n" +
    "                        <label class=\"cradmin-legacy-datetime-selector-date-label\" ng-if=\"config.date_label_text\">\n" +
    "                            {{ config.date_label_text }}\n" +
    "                        </label>\n" +
    "                        <label for=\"{{ config.destinationfieldid }}_dayselect\" class=\"sr-only\">\n" +
    "                            {{ config.day_screenreader_text }}\n" +
    "                        </label>\n" +
    "                        <select id=\"{{ config.destinationfieldid }}_dayselect\"\n" +
    "                                class=\"form-control cradmin-legacy-datetime-selector-dayselect\"\n" +
    "                                ng-model=\"monthlyCalendarCoordinator.currentDayObject\"\n" +
    "                                ng-options=\"dayobject.label for dayobject in monthlyCalendarCoordinator.dayobjects track by dayobject.value\"\n" +
    "                                ng-change=\"onSelectDayNumber()\">\n" +
    "                        </select>\n" +
    "\n" +
    "                        <label for=\"{{ config.destinationfieldid }}_monthselect\" class=\"sr-only\">\n" +
    "                            {{ config.month_screenreader_text }}\n" +
    "                        </label>\n" +
    "                        <select id=\"{{ config.destinationfieldid }}_monthselect\"\n" +
    "                                class=\"form-control cradmin-legacy-datetime-selector-monthselect\"\n" +
    "                                ng-model=\"monthlyCalendarCoordinator.currentMonthObject\"\n" +
    "                                ng-options=\"monthobject.label for monthobject in monthlyCalendarCoordinator.monthselectConfig track by monthobject.value\"\n" +
    "                                ng-change=\"onSelectMonth()\">\n" +
    "                        </select>\n" +
    "\n" +
    "                        <label for=\"{{ config.destinationfieldid }}_yearselect\" class=\"sr-only\">\n" +
    "                            {{ config.year_screenreader_text }}\n" +
    "                        </label>\n" +
    "                        <select id=\"{{ config.destinationfieldid }}_yearselect\"\n" +
    "                                class=\"form-control cradmin-legacy-datetime-selector-yearselect\"\n" +
    "                                ng-model=\"monthlyCalendarCoordinator.currentYearObject\"\n" +
    "                                ng-options=\"yearobject.label for yearobject in monthlyCalendarCoordinator.yearselectConfig track by yearobject.value\"\n" +
    "                                ng-change=\"onSelectYear()\">\n" +
    "                        </select>\n" +
    "                    </div>\n" +
    "\n" +
    "                    <div class=\"cradmin-legacy-datetime-selector-timeselectors\" ng-if=\"config.include_time\">\n" +
    "                        <label class=\"cradmin-legacy-datetime-selector-time-label\" ng-if=\"config.time_label_text\">\n" +
    "                            {{ config.time_label_text }}\n" +
    "                        </label>\n" +
    "                        <label for=\"{{ config.destinationfieldid }}_hourselect\" class=\"sr-only\">\n" +
    "                            {{ config.hour_screenreader_text }}\n" +
    "                        </label>\n" +
    "                        <select id=\"{{ config.destinationfieldid }}_hourselect\"\n" +
    "                                class=\"form-control cradmin-legacy-datetime-selector-hourselect\"\n" +
    "                                ng-model=\"monthlyCalendarCoordinator.currentHourObject\"\n" +
    "                                ng-options=\"hourobject.label for hourobject in monthlyCalendarCoordinator.hourselectConfig track by hourobject.value\"\n" +
    "                                ng-change=\"onSelectHour()\">\n" +
    "                        </select>\n" +
    "                        :\n" +
    "                        <label for=\"{{ config.destinationfieldid }}_minuteselect\" class=\"sr-only\">\n" +
    "                            {{ config.minute_screenreader_text }}\n" +
    "                        </label>\n" +
    "                        <select id=\"{{ config.destinationfieldid }}_minuteselect\"\n" +
    "                                class=\"form-control cradmin-legacy-datetime-selector-minuteselect\"\n" +
    "                                ng-model=\"monthlyCalendarCoordinator.currentMinuteObject\"\n" +
    "                                ng-options=\"minuteobject.label for minuteobject in monthlyCalendarCoordinator.minuteselectConfig track by minuteobject.value\"\n" +
    "                                ng-change=\"onSelectMinute()\">\n" +
    "                        </select>\n" +
    "                    </div>\n" +
    "\n" +
    "                    <button type=\"button\"\n" +
    "                            class=\"btn btn-primary cradmin-legacy-datetime-selector-use-button\"\n" +
    "                            ng-click=\"onClickUseTime()\"\n" +
    "                            aria-label=\"{{ getUseButtonAriaLabel() }}\">\n" +
    "                        {{ config.usebuttonlabel }}\n" +
    "                    </button>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "\n" +
    "            <table class=\"cradmin-legacy-datetime-selector-table\">\n" +
    "                <caption class=\"sr-only\">\n" +
    "                    {{ config.dateselector_table_screenreader_caption }}\n" +
    "                </caption>\n" +
    "                <thead>\n" +
    "                    <tr>\n" +
    "                        <th ng-repeat=\"weekday in monthlyCalendarCoordinator.shortWeekdays\">\n" +
    "                            {{ weekday }}\n" +
    "                        </th>\n" +
    "                    </tr>\n" +
    "                </thead>\n" +
    "                <tbody>\n" +
    "                    <tr ng-repeat=\"calendarWeek in monthlyCalendarCoordinator.calendarMonth.calendarWeeks\">\n" +
    "                        <td ng-repeat=\"calendarDay in calendarWeek.calendarDays\"\n" +
    "                                class=\"cradmin-legacy-datetime-selector-daybuttoncell\"\n" +
    "                                ng-class=\"{\n" +
    "                                    'cradmin-legacy-datetime-selector-daybuttoncell-not-in-current-month': !calendarDay.isInCurrentMonth,\n" +
    "                                    'cradmin-legacy-datetime-selector-daybuttoncell-in-current-month': calendarDay.isInCurrentMonth,\n" +
    "                                    'cradmin-legacy-datetime-selector-daybuttoncell-selected': calendarDay.momentObject.isSame(calendarCoordinator.selectedMomentObject, 'day'),\n" +
    "                                    'cradmin-legacy-datetime-selector-daybuttoncell-lastfocused': calendarDay.momentObject.isSame(monthlyCalendarCoordinator.getLastFocusedMomentObject(), 'day'),\n" +
    "                                    'cradmin-legacy-datetime-selector-daybuttoncell-today': calendarDay.isToday(),\n" +
    "                                    'cradmin-legacy-datetime-selector-daybuttoncell-disabled': calendarDay.isDisabled()\n" +
    "                                }\">\n" +
    "                            <button type=\"button\" class=\"btn btn-link cradmin-legacy-datetime-selector-daybuttoncell-button\"\n" +
    "                                    ng-click=\"onClickCalendarDay(calendarDay)\"\n" +
    "                                    tabindex=\"{{ getTabindexForCalendarDay(calendarDay) }}\"\n" +
    "                                    ng-focus=\"onFocusCalendayDay(calendarDay)\"\n" +
    "                                    aria-label=\"{{ getDaybuttonAriaLabel(calendarDay) }}\"\n" +
    "                                    ng-disabled=\"{{ calendarDay.isDisabled() }}\">\n" +
    "                                {{ monthlyCalendarCoordinator.getDayOfMonthLabelForTableCell(calendarDay) }}\n" +
    "                                <span class=\"cradmin-legacy-datetime-selector-daybuttoncell-label\n" +
    "                                             cradmin-legacy-datetime-selector-daybuttoncell-label-today\"\n" +
    "                                        ng-if=\"config.today_label_text &amp;&amp; calendarDay.isToday()\">\n" +
    "                                    {{ config.today_label_text }}\n" +
    "                                </span>\n" +
    "                                <span class=\"cradmin-legacy-datetime-selector-daybuttoncell-label\n" +
    "                                             cradmin-legacy-datetime-selector-daybuttoncell-label-selected\"\n" +
    "                                        ng-if=\"\n" +
    "                                            config.selected_day_label_text &amp;&amp;\n" +
    "                                            calendarDay.momentObject.isSame(calendarCoordinator.selectedMomentObject, 'day')\">\n" +
    "                                    {{ config.selected_day_label_text }}\n" +
    "                                </span>\n" +
    "                            </button>\n" +
    "                        </td>\n" +
    "                    </tr>\n" +
    "                </tbody>\n" +
    "            </table>\n" +
    "\n" +
    "            <div class=\"cradmin-legacy-datetime-selector-shortcuts\" ng-if=\"hasShortcuts()\">\n" +
    "                <button type=\"button\"\n" +
    "                        class=\"btn btn-default cradmin-legacy-datetime-selector-shortcuts-todaybutton\"\n" +
    "                        ng-if=\"calendarCoordinator.todayIsValidValue()\"\n" +
    "                        ng-click=\"onClickTodayButton()\">\n" +
    "                    {{ config.today_button_text }}\n" +
    "                </button>\n" +
    "                <button type=\"button\"\n" +
    "                        class=\"btn btn-default cradmin-legacy-datetime-selector-shortcuts-nowbutton\"\n" +
    "                        ng-if=\"calendarCoordinator.nowIsValidValue()\"\n" +
    "                        ng-click=\"onClickNowButton()\">\n" +
    "                    {{ config.now_button_text }}\n" +
    "                </button>\n" +
    "                <button type=\"button\"\n" +
    "                        class=\"btn btn-danger cradmin-legacy-datetime-selector-shortcuts-clearbutton\"\n" +
    "                        ng-if=\"!config.required\"\n" +
    "                        ng-click=\"onClickClearButton()\">\n" +
    "                    {{ config.clear_button_text }}\n" +
    "                </button>\n" +
    "            </div>\n" +
    "\n" +
    "            <button type=\"button\" class=\"sr-only\" ng-focus=\"onFocusTail()\"></button>\n" +
    "        </div>\n" +
    "\n" +
    "        <div class=\"cradmin-legacy-datetime-selector-page cradmin-legacy-datetime-selector-timeview\">\n" +
    "            <button type=\"button\" class=\"sr-only\" ng-focus=\"onFocusHead()\"></button>\n" +
    "            <button type=\"button\"\n" +
    "                    class=\"btn btn-link cradmin-legacy-datetime-selector-closebutton\"\n" +
    "                    aria-label=\"{{ config.close_screenreader_text }}\"\n" +
    "                    ng-click=\"hide()\">\n" +
    "                        <span class=\"{{ config.close_icon }}\" aria-hidden=\"true\"></span>\n" +
    "                    </button>\n" +
    "\n" +
    "            <button type=\"button\"\n" +
    "                    class=\"btn btn-link cradmin-legacy-datetime-selector-backbutton\"\n" +
    "                    tabindex=\"0\"\n" +
    "                    aria-label=\"{{ config.back_to_datepicker_screenreader_text }}\"\n" +
    "                    ng-click=\"showPage1()\">\n" +
    "                <span class=\"cradmin-legacy-datetime-selector-backbutton-icon-outer-wrapper\">\n" +
    "                    <span class=\"cradmin-legacy-datetime-selector-backbutton-icon-inner-wrapper\">\n" +
    "                        <span class=\"cradmin-legacy-datetime-selector-backbutton-icon {{ config.back_icon }}\"></span>\n" +
    "                    </span>\n" +
    "                </span>\n" +
    "            </button>\n" +
    "\n" +
    "            <div class=\"cradmin-legacy-datetime-selector-timeview-body-wrapper\">\n" +
    "                <div class=\"cradmin-legacy-datetime-selector-timeview-body\">\n" +
    "                    <p class=\"cradmin-legacy-datetime-selector-datepreview\">\n" +
    "                        {{ getTimeselectorDatepreview() }}\n" +
    "                    </p>\n" +
    "                    <div class=\"cradmin-legacy-datetime-selector-timeselectors\">\n" +
    "                        <form class=\"form-inline\">\n" +
    "                            <label class=\"cradmin-legacy-datetime-selector-time-label\" ng-if=\"config.time_label_text\">\n" +
    "                                {{ config.time_label_text }}\n" +
    "                            </label>\n" +
    "                            <label for=\"{{ config.destinationfieldid }}_hourselect_page2\" class=\"sr-only\">\n" +
    "                                {{ config.hour_screenreader_text }}\n" +
    "                            </label>\n" +
    "                            <select id=\"{{ config.destinationfieldid }}_hourselect_page2\"\n" +
    "                                    class=\"form-control cradmin-legacy-datetime-selector-hourselect\"\n" +
    "                                    ng-model=\"monthlyCalendarCoordinator.currentHourObject\"\n" +
    "                                    ng-options=\"hourobject.label for hourobject in monthlyCalendarCoordinator.hourselectConfig track by hourobject.value\"\n" +
    "                                    ng-change=\"onSelectHour()\">\n" +
    "                            </select>\n" +
    "                            :\n" +
    "                            <label for=\"{{ config.destinationfieldid }}_minuteselect_page2\" class=\"sr-only\">\n" +
    "                                {{ config.minute_screenreader_text }}\n" +
    "                            </label>\n" +
    "                            <select id=\"{{ config.destinationfieldid }}_minuteselect_page2\"\n" +
    "                                    class=\"form-control cradmin-legacy-datetime-selector-minuteselect\"\n" +
    "                                    ng-model=\"monthlyCalendarCoordinator.currentMinuteObject\"\n" +
    "                                    ng-options=\"minuteobject.label for minuteobject in monthlyCalendarCoordinator.minuteselectConfig track by minuteobject.value\"\n" +
    "                                    ng-change=\"onSelectMinute()\">\n" +
    "                            </select>\n" +
    "                            <button type=\"button\"\n" +
    "                                    class=\"btn btn-primary cradmin-legacy-datetime-selector-use-button\"\n" +
    "                                    ng-click=\"onClickUseTime()\"\n" +
    "                                    aria-label=\"{{ getUseButtonAriaLabel() }}\">\n" +
    "                                {{ config.usebuttonlabel }}\n" +
    "                            </button>\n" +
    "                        </form>\n" +
    "                    </div>\n" +
    "\n" +
    "                </div>\n" +
    "\n" +
    "                <div class=\"cradmin-legacy-datetime-selector-shortcuts\" ng-if=\"hasShortcuts()\">\n" +
    "                    <button type=\"button\"\n" +
    "                            class=\"btn btn-default cradmin-legacy-datetime-selector-shortcuts-nowbutton\"\n" +
    "                            ng-click=\"onClickNowButton()\"\n" +
    "                            ng-if=\"calendarCoordinator.shownDateIsTodayAndNowIsValid()\">\n" +
    "                        {{ config.now_button_text }}\n" +
    "                    </button>\n" +
    "                </div>\n" +
    "\n" +
    "            </div>\n" +
    "\n" +
    "\n" +
    "            <button type=\"button\" class=\"sr-only\" ng-focus=\"onFocusTail()\"></button>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("pagepreview/navbar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("pagepreview/navbar.tpl.html",
    "<nav cradmin-legacy-menu class=\"cradmin-legacy-menu\">\n" +
    "    <div class=\"cradmin-legacy-menu-mobileheader\">\n" +
    "        <a href=\"#\" role=\"button\"\n" +
    "           class=\"cradmin-legacy-menu-mobiletoggle\"\n" +
    "           ng-click=\"cradminMenuTogglePressed()\"\n" +
    "           ng-class=\"{'cradmin-legacy-menu-mobile-toggle-button-expanded': cradminMenuDisplay}\"\n" +
    "           aria-pressed=\"{{ getAriaPressed() }}\">\n" +
    "                {{ mobileMenuHeader }}\n" +
    "        </a>\n" +
    "    </div>\n" +
    "    <div class=\"cradmin-legacy-menu-content\"\n" +
    "             ng-class=\"{'cradmin-legacy-menu-content-display': cradminMenuDisplay}\">\n" +
    "        <ul class=\"cradmin-legacy-menu-content-main\">\n" +
    "            <li ng-repeat=\"urlConfig in previewConfig.urls\"\n" +
    "                    class=\"cradmin-legacy-menu-item {{urlConfig.css_classes}}\"\n" +
    "                    ng-class=\"{\n" +
    "                        'cradmin-legacy-menu-activeitem': $index == activeIndex\n" +
    "                    }\">\n" +
    "                <a href=\"{{ urlConfig.url }}\"\n" +
    "                        cradmin-legacy-menu-close-on-click\n" +
    "                        ng-click=\"onNavlinkClick($event, $index)\">\n" +
    "                    {{urlConfig.label}}\n" +
    "                </a>\n" +
    "            </li>\n" +
    "        </ul>\n" +
    "        <ul class=\"cradmin-legacy-menu-content-footer\">\n" +
    "            <li>\n" +
    "                <a href=\"{{ activeUrlConfig.url }}\" target=\"_blank\">\n" +
    "                    {{ activeUrlConfig.open_label }}\n" +
    "                </a>\n" +
    "            </li>\n" +
    "        </ul>\n" +
    "    </div>\n" +
    "</nav>\n" +
    "");
}]);

(function() {
  angular.module('cradminLegacy.wysihtml', []).directive('cradminLegacyWysihtml', function() {
    return {
      restrict: 'A',
      transclude: true,
      template: '<div><p>Stuff is awesome!</p><div ng-transclude></div></div>'
    };
  });

}).call(this);
