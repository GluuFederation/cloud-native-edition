from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class SpannerForm(FlaskForm):
    """
    Spanner Form

    Fields:
        spanner_instance_id (string|required)
        spanner_database_id (string|required)
    """

    spanner_instance_id = StringField(
        "Please enter the google spanner instance ID",
        default="", validators=[InputRequired()])

    spanner_database_id = StringField("Please enter the google spanner database ID",
                                      default="",
                                      validators=[InputRequired()])
