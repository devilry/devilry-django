module.exports = (grunt) ->
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json')
        watch:
            coffee:
                tasks: 'coffee'
                files: ['*.coffee']
        coffee:
            compile:
                files:
                    'editor.js': 'editor.coffee'
    })
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.registerTask('default', [
        'coffee:compile'
    ])