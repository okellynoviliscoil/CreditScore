import connexion

# Create the application instance
app = connexion.App(__name__, specification_dir='./')

# Read the creditScore.yml file to configure the endpoints
app.add_api('creditScore.yml')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
