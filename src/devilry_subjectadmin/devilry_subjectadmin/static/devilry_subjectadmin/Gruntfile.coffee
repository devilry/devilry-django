module.exports = (grunt) ->
  # Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json')
    watch:
      #coffee_edit_feedback:
        #tasks: 'coffee:edit_feedback'
        #files: ['coffee/*.coffee']
      less:
        tasks: 'less'
        files: ['less/*.less', 'less/views/*.less']
    #coffee:
      #edit_feedback:
        #files:
          #'js/edit_feedback.js': 'coffee/edit_feedback.coffee'
    less:
      development:
        options:
          paths: ["less", "bower/components"]
        files:
          "css/styles.css": "less/styles.less"
  })

  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-contrib-coffee')
  grunt.loadNpmTasks('grunt-contrib-less')
  grunt.registerTask('default', [
    'less'
    #'coffee:editor'
  ])
