from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired
from .helpers import RequiredIfFieldEqualTo


class ImageNameTagForm(FlaskForm):
    """
    Image Name Tag Form

    Fields :
        edit_image_names_tags (string|required)
        casa_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        casa_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        config_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        config_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        cache_refresh_rotate_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        cache_refresh_rotate_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        cert_manager_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        cert_manager_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        ldap_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        ldap_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        jackrabbit_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        jackrabbit_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxauth_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxauth_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxd_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxd_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxpassport_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxpassport_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxshibboleth_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxshibboleth_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxtrust_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        oxtrust_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        persistence_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        persistence_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
    """
    # TODO: find a way to generate dynamic fields

    edit_image_names_tags = RadioField(
        "Would you like to manually edit the image source/name and tag",
        choices=[("Y", "Yes"), ("N", "No")],
        validators=[DataRequired()])
    casa_image_name = StringField(
        "Casa image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    casa_image_tag = StringField(
        "Casa image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    config_image_name = StringField(
        "Config image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    config_image_tag = StringField(
        "Config image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cache_refresh_rotate_image_name = StringField(
        "CR-rotate image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cache_refresh_rotate_image_tag = StringField(
        "CR-rotate image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cert_manager_image_name = StringField(
        "Key rotate image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cert_manager_image_tag = StringField(
        "Key rotate image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    ldap_image_name = StringField(
        "OpenDJ image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    ldap_image_tag = StringField(
        "OpenDJ image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    jackrabbit_image_name = StringField(
        "Jackrabbit image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    jackrabbit_image_tag = StringField(
        "Jackrabbit image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxauth_image_name = StringField(
        "Oxauth image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxauth_image_tag = StringField(
        "Oxauth image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxd_image_name = StringField(
        "Oxd Server image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxd_image_tag = StringField(
        "Oxd Server image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxpassport_image_name = StringField(
        "oxPassport image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxpassport_image_tag = StringField(
        "oxPassport image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxshibboleth_image_name = StringField(
        "oxShibboleth image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxshibboleth_image_tag = StringField(
        "oxShibboleth image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxtrust_image_name = StringField(
        "oxTrust image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxtrust_image_tag = StringField(
        "oxTrust image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    persistence_image_name = StringField(
        "Persistence image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    persistence_image_tag = StringField(
        "Persistence image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    fido2_image_name = StringField(
        "FIDO2 image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    fido2_image_tag = StringField(
        "FIDO2 image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    scim_image_name = StringField(
        "SCIM image name",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    scim_image_tag = StringField(
        "SCIM image tag",
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
