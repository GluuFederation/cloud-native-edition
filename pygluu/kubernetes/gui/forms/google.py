from flask_wtf import FlaskForm
from wtforms import StringField, FileField, FormField, RadioField
from wtforms.validators import InputRequired, DataRequired, Optional
from .helpers import RequiredIfFieldEqualTo


class GoogleForm(FlaskForm):
    """
    Spanner Form

    Fields:
        spanner_instance_id (string|required)
        spanner_database_id (string|required)
        google_secret_manager (string|required) : default N
        google_service_account (file|required_if persistence  is spanner and or if using google secret manager)
    """

    spanner_instance_id = StringField(
        "Please enter the google spanner instance ID",
        default="", validators=[InputRequired()])

    spanner_database_id = StringField("Please enter the google spanner database ID",
                                      default="",
                                      validators=[InputRequired()])

    google_secret_manager = RadioField(
        "Use Google Secret Manager to hold gluu configuration layer."
        " If answered with No, kubernetes secrets will be used ",
        choices=[("Y", "Yes"), ("N", "No")],
        default="N",
        validators=[DataRequired()])

    google_service_account = FileField(
        "Google service account json",
        description="Upload the google service account that has permissions to use Spanner and/or "
                    "Google Secret Manager. The service account must have "
                    "roles/secretmanager.admin to use Google secret manager and/or "
                    "roles/spanner.databaseUser to use Spanner",
        validators=[RequiredIfFieldEqualTo("google_secret_manager", "Y")])