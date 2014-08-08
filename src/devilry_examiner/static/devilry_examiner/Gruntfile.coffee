module.exports = (grunt) ->
  # Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json')
    watch:
      coffee_edit_feedback:
        tasks: 'coffee:edit_feedback'
        files: ['coffee/*.coffee']
    coffee:
      edit_feedback:
        files:
          'js/edit_feedback.js': 'coffee/edit_feedback.coffee'
  })

  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-contrib-coffee')
  grunt.registerTask('default', [
    'coffee'
  ])
