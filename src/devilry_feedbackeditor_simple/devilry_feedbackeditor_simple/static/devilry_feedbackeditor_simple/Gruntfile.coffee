module.exports = (grunt) ->
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json')
        watch:
            coffee_editor:
                tasks: 'coffee:editor'
                files: ['coffee/*.coffee']
        coffee:
            editor:
                files:
                    'js/editor.js': 'coffee/editor.coffee'
    })
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.registerTask('default', [
        'coffee:editor'
    ])