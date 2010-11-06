// vim: set ts=2 sts=2 et sw=2:

/*
<input type="hidden" name="form-TOTAL_FORMS" value="10" id="id_form-TOTAL_FORMS" />
<input type="hidden" name="form-INITIAL_FORMS" value="0" id="id_form-INITIAL_FORMS" />
<input type="hidden" name="form-MAX_NUM_FORMS" id="id_form-MAX_NUM_FORMS" /> 
<tr><th><label for="id_form-0-file">File:</label></th><td><input type="file" name="form-0-file" id="id_form-0-file" /></td></tr>
<tr><th><label for="id_form-1-file">File:</label></th><td><input type="file" name="form-1-file" id="id_form-1-file" /></td></tr>
<tr><th><label for="id_form-2-file">File:</label></th><td><input type="file" name="form-2-file" id="id_form-2-file" /></td></tr>
*/

(function($){

    $.fn.devilryMultiFileBoxWithFile = function(opt, filebutton) {
      var filebox = $(this);
      filebox.detach();
      filebox.appendTo(opt.withfile);
      var delbutton = $("<a></a>")
        .attr("href", "#")
        .html("delete")
        .button({
            text:false,
            icons:{primary:"ui-icon-trash"}
          });
      var label = $("<span></span>")
        .addClass("dimmed")
        .html("&nbsp;&nbsp;" + filebutton.val());
      var listitem = $("<div></div>")
        .append(delbutton)
        .append(label)
        .appendTo(opt.withfilelist);
      opt.withfilelist.show();

      delbutton.click(function() {
          listitem.remove();
          filebox.remove();
          return false;
        });
    },

    /* A single file "filebox" */
    $.fn.devilryMultiFileBox = function(opt) {
      var filebox = $(this);
      filebox.appendTo(opt.addfilebox);
      filebox.addClass("fileupload-item-without-file");
      var id = opt.idprefix + opt.max + opt.suffix;
      var name = opt.prefix + opt.max + opt.suffix;

      var filebutton = $("<input/>")
        .attr("type", "file")
        .attr("name", name)
        .attr("id", id)
        .appendTo(filebox);

      filebutton.change(function() {
          // Triggered when the users adds a file
          opt.max ++;
          opt.submitbtn.button("option", "disabled", false); // Enable submit button
          $("<div></div>").devilryMultiFileBox(opt); // Adds a new empty "file chooser"
          filebox.devilryMultiFileBoxWithFile(opt, filebutton); // Add this to the list of selected files
        });
    },

    $.fn.devilryMultiFile = function(options) {
      var opt = jQuery.extend({
          submitbtn_id: "id_submit",
          removelabel: "remove",
          currentlabel: "Current files",
          idprefix: "id_form-",
          prefix: "form-",
          suffix: "-file"
        }, options);

      opt.max = 0;
      opt.container = $(this);
      opt.container.find("tr").remove();
      opt.submitbtn = $("#"+opt.submitbtn_id).button({
          disabled: true // Disable submit until first file is added.
        });

      opt.addfilebox = $("<div></div>")
        .addClass("fileupload-without-file")
        .appendTo(opt.container);

      // Buffer of files choosen by the user as part of the delivery
      // This is always kept hidden, but the filename and a delete button is
      // kept in opt.withfilelist (below)
      opt.withfile = $("<div></div>")
        .attr("style", "display:none")
        .addClass("fileupload-with-file")
        .appendTo(opt.container);

      opt.withfilelist = $("<div></div>")
        .attr("style", "display:none")
        .addClass("fileupload-with-filelist")
        .appendTo(opt.container)
        .append($("<h2></h2>")
          .addClass("dimmed")
          .html(opt.currentlabel));

      // Create the first "file upload box"
      // It will add another box when a user adds a file to it.
      $("<div></div>").devilryMultiFileBox(opt);
    };

    $.log = function(message) {
      if(window.console) {
        console.debug(message);
      } else {
        alert(message);
      }
    };

  })(jQuery);
