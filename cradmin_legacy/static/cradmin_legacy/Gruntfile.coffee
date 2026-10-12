module.exports = (grunt) ->

  appfiles = {
    coffeecode: ['src/**/*.coffee', '!src/**/*.spec.coffee']
    coffeetests: ['src/**/*.spec.coffee']
    templates: ['src/lib/**/*.tpl.html']
    less: ['src/less/*.less', 'src/less/**/*.less']
  }

  vendorfiles = {
    js: [
      'node_modules/jquery/dist/jquery.js'
      'node_modules/angular/angular.js'
#      'bower_components/angular-bootstrap/ui-bootstrap-tpls.js'
      'node_modules/angular-cookies/angular-cookies.js'
#      'bower_components/ng-file-upload/angular-file-upload.js'
      'thirdparty_js_libs/ng-file-upload-2.1.1/dist/angular-file-upload.js'
#      'bower_components/modernizr/modernizr.js'
      'node_modules/detectizr/dist/detectizr.js'
      'node_modules/moment/moment.js'
      'node_modules/mousetrap/mousetrap.js'
      'node_modules/angular-hotkeys/src/hotkeys.js'
      'node_modules/urijs/src/URI.js'
    ]
    ace_editor: [
      'node_modules/ace-builds/src-min-noconflict/ace.js'
      'node_modules/ace-builds/src-min-noconflict/mode-markdown.js'
      'node_modules/ace-builds/src-min-noconflict/theme-tomorrow.js'
    ]
  }

  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-contrib-less')
  grunt.loadNpmTasks('grunt-contrib-copy')
  grunt.loadNpmTasks('grunt-contrib-coffee')
  grunt.loadNpmTasks('grunt-coffeelint')
  grunt.loadNpmTasks('grunt-contrib-concat')
  grunt.loadNpmTasks('grunt-contrib-uglify')
  grunt.loadNpmTasks('grunt-karma')
  grunt.loadNpmTasks('grunt-html2js')

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json')

#    exec:
#      vitalstyles: 'custom_vitalstyles_cli.py'
    delta:
      less:
        files: appfiles.less
        tasks: [
          'less'
#          'exec:vitalstyles'
        ]
#      vitalstyles:
#        files: ['custom_vitalstyles_cli.py']
#        tasks: [
#            'exec:vitalstyles'
#        ]
      coffeecode:
        files: appfiles.coffeecode
        tasks: [
          'coffeelint:code', 'coffee:code', 'buildCradminDist']
      coffeetests:
        files: appfiles.coffeetests
        tasks: ['coffeelint:tests', 'coffee:tests']
      templates:
        files: appfiles.templates
        tasks: ['html2js:templates', 'buildCradminDist']
      gruntfile:
        files: 'Gruntfile.coffee'
        tasks: ['coffeelint:gruntfile']

    less:
      development:
        options:
          paths: ["less", "node_modules"]
        files:
          "dist/css/cradmin_theme_default/theme.css": "src/less/cradmin_theme_default/theme.less"
          "dist/css/cradmin_theme_topmenu/theme.css": "src/less/cradmin_theme_topmenu/theme.less"

    coffeelint:
      options:
        max_line_length:
          name: "max_line_length"
          value: 120
          level: "warn"
          limitComments: true
      code: appfiles.coffeecode
      tests: appfiles.coffeetests
      gruntfile: ['Gruntfile.coffee']

    coffee:
      code:
        expand: true
        cwd: '.'
        src: appfiles.coffeecode
        dest: '.'
        ext: '.js'
      tests:
        expand: true
        cwd: '.'
        src: appfiles.coffeetests
        dest: '.'
        ext: '.spec.js'

    concat:
      cradmin:
        src: ['src/**/*.js', '!src/**/*.spec.js']
        dest: 'dist/js/cradmin.js'

    uglify:
      options:
        mangle: false
        sourceMap: true
      cradmin:
        files:
          'dist/js/cradmin.min.js': ['dist/js/cradmin.js']
      vendor:
        files:
          'dist/vendor/cradmin-vendorjs.js': vendorfiles.js

    copy:
      vendor:
        files: [{
          expand: true
          cwd: 'node_modules/fontawesome/'
          src: ['css/*', 'fonts/*']
          dest: 'dist/vendor/fonts/fontawesome/'
        }, {
          expand: true
          cwd: 'node_modules/bootstrap/fonts/'
          src: ['glyphicons-*']
          dest: 'dist/vendor/fonts/glyphicons/'
        }, {
          expand: true
          cwd: 'node_modules/moment/locale/'
          src: ['*.js']
          dest: 'dist/vendor/momentjs-locale/'
        }, {
          expand: true
          flatten: true
          src: vendorfiles.ace_editor
          dest: 'dist/vendor/js/ace-editor/'
        }]

    karma:
      options:
        # base path that will be used to resolve all patterns
        basePath: ''

        # frameworks to use¨
        # available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['jasmine']

        # Browsers to autostart
        browsers : ['Chrome']

        # list of files / patterns to load in the browser
        files: [
          'node_modules/jquery/dist/jquery.js'
          'node_modules/angular/angular.js'
          'node_modules/angular-mocks/angular-mocks.js'
          'node_modules/angular-cookies/angular-cookies.js'
#          'bower_components/ng-file-upload/angular-file-upload.js'
          'thirdparty_js_libs/ng-file-upload-2.1.1/dist/angular-file-upload.js'
#          'node_modules/modernizr/modernizr.js'
          'node_modules/detectizr/dist/detectizr.js'
          #'bower_components/angular-ui-ace/ui-ace.min.js'
          #'bower_components/ace-builds/src-min-noconflict/ace.js'
          'src/lib/**/*.js'
        ]

        # list of files to exclude
        exclude: []

        plugins : [
          'karma-chrome-launcher'
          'karma-firefox-launcher'
          'karma-jasmine'
        ]

        # preprocess matching files before serving them to the browser
        # available preprocessors:
        # https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {}

        # test results reporter to use
        # possible values: 'dots', 'progress'
        # available reporters: https://npmjs.org/browse/keyword/karma-reporter
        reporters: ['dots'],

        # enable / disable colors in the output (reporters and logs)
        colors: true

        # level of logging
        logLevel: 'INFO'

        # enable / disable watching file and executing tests whenever any file
        # changes
        autoWatch: false

      # Runs the test server in the background. We trigger tests
      # using ``karma:watchrunner:run``
      watchrunner:
        port: 9019,
        background: true

      # Used when we just want to run the tests and exit
      singlerun:
        singleRun: true
        port: 9876

    # HTML2JS is a Grunt plugin that takes all of your template files and
    # places them into JavaScript files as strings that are added to
    # AngularJS's template cache. This means that the templates too become
    # part of the initial payload as one JavaScript file.
    html2js:
      templates:
        options:
          base: 'src/lib/'
          module: 'cradminLegacy.templates'
        src: appfiles.templates
        dest: 'src/lib/templates.js'
  })

  grunt.registerTask('buildCradminDist', [
    'concat:cradmin'
    'uglify:cradmin'
  ])

  grunt.registerTask('buildVendorDist', [
    'uglify:vendor'
    'copy:vendor'
  ])

  grunt.registerTask('build', [
    'coffeelint'
    'less'
    'coffee:tests'
    'coffee:code'
    'html2js'
    'buildCradminDist',
    'buildVendorDist',
#    'karma:singlerun'
  ])

  grunt.registerTask('dist', [
    'build'
  ])

  # Rename the watch task to delta, and make a new watch task that runs
  # build on startup
  grunt.renameTask('watch', 'delta')
  grunt.registerTask('watch', [
    'build'
    'delta'
  ])

  grunt.registerTask('default', ['build'])
