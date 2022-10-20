from webapp import app
import os

if __name__ == '__main__':
    os.system("start cmd /c python external_server.py")
    app.run(debug=True)