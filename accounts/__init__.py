import logging

from flask import current_app, Flask, redirect, url_for
import accounts.mongodb as mongodb


def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    # Setup the mongodb model
    mongodb.init_app(app)

    # Register the handler blueprint.
    from .handler import handler
    app.register_blueprint(handler, url_prefix='/')

    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('handler.index'))

    # Add an error handler. This is useful for debugging the live application,
    # however, you should disable the output of the exception for production
    # applications.
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app