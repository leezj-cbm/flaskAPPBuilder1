from flask import render_template ,session, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi,SimpleFormView
from .forms import TweetForm
from . import appbuilder, db

"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)

    Create your Views::

    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::

    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

class SendTweet(SimpleFormView):
    form = TweetForm
    form_title = "Send a test tweet"

    message = "Tweet sent!"

    def form_get(self, form):
        provider = session["oauth_provider"]
        if not provider == "twitter":
            flash("You must login with Twitter, this will not work", "warning")
        form.message.data = "Flask-AppBuilder now supports OAuth!"

    def form_post(self, form):
        remote_app = self.appbuilder.sm.oauth_remotes["twitter"]
        resp = remote_app.post(
            "statuses/update.json",
            data={"status": form.message.data},
            token=remote_app.token,
        )
        if resp.status_code != 200:
            flash("An error occurred", "danger")
        else:
            flash(self.message, "info")
            
"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()
# -----------------------------------------------------------
# Decorator to override the OAuth provider information getter
# -----------------------------------------------------------

# https://github.com/dpgaspar/Flask-AppBuilder/blob/master/examples/oauth/app/views.py
@appbuilder.sm.oauth_user_info_getter
def get_oauth_user_info(sm, provider, response=None):
    # for keycloak
    if provider == 'keycloak':
        me = sm.oauth_remotes[provider].get('userinfo')
        data = me.json()
        return {'username': data.get('id', ''),
                'first_name': data.get('given_name', ''),
                'last_name': data.get('family_name', ''),
                'email': data.get('email', '')}
        
appbuilder.add_view(SendTweet, "Tweet", icon="fa-twitter", label="Tweet")

db.create_all()