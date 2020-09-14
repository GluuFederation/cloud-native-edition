from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class CouchbaseBackupForm(FlaskForm):
    """
    Couchbase Backup Form

    Fields :
        couchbase_incr_backup_schedule (string|required|default: */30 * * * *)
        couchbase_full_backup_schedule (string|required|default: 0 2 * * 6)
        couchbase_backup_rentention_time (string|required|default: 168h)
        couchbase_backup_storage_file_size (string|required|default: 20Gi)
    """
    couchbase_incr_backup_schedule = StringField(
        "Please input couchbase backup cron job schedule for incremental backups. "
        "This will run backup job every 30 mins by default.",
        default="*/30 * * * *",
        validators=[InputRequired()])
    couchbase_full_backup_schedule = StringField(
        "Please input couchbase backup cron job schedule for full backups. ",
        default="0 2 * * 6",
        validators=[InputRequired()])
    couchbase_backup_retention_time = StringField(
        "Please enter the time period in which to retain existing backups. "
        "Older backups outside this time frame are deleted",
        default="168h",
        validators=[InputRequired()])
    couchbase_backup_storage_size = StringField(
        "Size of couchbase backup volume storage",
        default="20Gi",
        validators=[InputRequired()])


class LdapBackupForm(FlaskForm):
    """
    LDAP backup Form

    Fields:
        ldap_backup_schedule (string|required|default: */30 * * * *)
    """
    ldap_backup_schedule = StringField(
        "Please input ldap backup cron job schedule. "
        "This will run backup job every 30 mins by default.",
        default="*/30 * * * *",
        validators=[InputRequired()])
