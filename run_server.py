from server import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Use this for production
    # curr_server.get_app().run()  # This is for local execution
