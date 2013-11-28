module.exports = (grunt) ->
    # Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json')
        watch:
            #coffee:
                #tasks: 'coffee'
                #files: ['app/coffee/*.coffee']
            less:
                tasks: 'less'
                files: ['less/*.less']
        #coffee:
            #compile:
                #options:
                    #bare: true
                #expand: true
                #flatten: true
                #cwd: 'app/coffee'
                #src: ['*.coffee']
                #dest: 'app/js'
                #ext: '.js'
        #nggettext_extract:
            #pot:
                #files:
                    #'po/timetracker.pot': ['app/index.html', 'app/partials/*.html']
        #nggettext_compile:
            #all:
                #options:
                    #module: 'timetracker'
                #files:
                    #'app/js/translations.js': ['po/*.po']
        less:
            development:
                options:
                    paths: ["less", "bower/components"]
                files:
                    "css/styles.css": "less/styles.less"
    })

    grunt.loadNpmTasks('grunt-contrib-watch')
    #grunt.loadNpmTasks('grunt-contrib-coffee')
    #grunt.loadNpmTasks('grunt-angular-gettext')
    grunt.loadNpmTasks('grunt-contrib-less')
