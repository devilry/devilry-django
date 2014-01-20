module.exports = (grunt) ->
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json')
        watch:
            coffee_editor:
                tasks: 'coffee:editmarkdown'
                files: ['coffee/*.coffee']
        coffee:
            editmarkdown:
                files:
                    'js/editmarkdown.js': 'coffee/editmarkdown.coffee'
    })
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.registerTask('default', [
        'coffee:editmarkdown'
    ])