module.exports = {
    apps : [
        {
          name: 'marvin-bot',
          script: './server.js',
          watch: true,
          log_date_format: 'DD-MM-YYYY HH:mm Z',
          error_file: 'logs/error.log',
          out_file: 'logs/out.log',
          exec_mode : 'cluster'
        }
    ]
}