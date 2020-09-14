from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired
from .helpers import RequiredIfFieldEqualTo
from pygluu.kubernetes.settings import SettingsHandler

settings = SettingsHandler()


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
        radius_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        radius_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        gluu_gateway_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        gluu_gateway_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
        gluu_gateway_ui_image_name (string|required_if edit_image_name_tags is Y| default from settings.json)
        gluu_gateway_ui_image_tag (string|required_if edit_image_name_tags is Y| default from settings.json)
    """
    # TODO: find a way to generate dynamic fields

    edit_image_names_tags = RadioField(
        "Would you like to manually edit the image source/name and tag",
        choices=[("Y", "Yes"), ("N", "No")],
        validators=[DataRequired()])
    casa_image_name = StringField(
        "Casa image name",
        default=settings.get("CASA_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    casa_image_tag = StringField(
        "Casa image tag",
        default=settings.get("CASA_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    config_image_name = StringField(
        "Config image name",
        default=settings.get("CONFIG_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    config_image_tag = StringField(
        "Config image tag",
        default=settings.get("CONFIG_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cache_refresh_rotate_image_name = StringField(
        "CR-rotate image name",
        default=settings.get("CACHE_REFRESH_ROTATE_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cache_refresh_rotate_image_tag = StringField(
        "CR-rotate image tag",
        default=settings.get("CACHE_REFRESH_ROTATE_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cert_manager_image_name = StringField(
        "Key rotate image name",
        default=settings.get("CERT_MANAGER_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    cert_manager_image_tag = StringField(
        "Key rotate image tag",
        default=settings.get("CERT_MANAGER_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    ldap_image_name = StringField(
        "WrenDS image name",
        default=settings.get("LDAP_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    ldap_image_tag = StringField(
        "WrenDS image tag",
        default=settings.get("LDAP_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    jackrabbit_image_name = StringField(
        "Jackrabbit image name",
        default=settings.get("JACKRABBIT_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    jackrabbit_image_tag = StringField(
        "Jackrabbit image tag",
        default=settings.get("JACKRABBIT_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxauth_image_name = StringField(
        "Oxauth image name",
        default=settings.get("OXAUTH_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxauth_image_tag = StringField(
        "Oxauth image tag",
        default=settings.get("OXAUTH_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxd_image_name = StringField(
        "Oxd Server image name",
        default=settings.get("OXD_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxd_image_tag = StringField(
        "Oxd Server image tag",
        default=settings.get("OXD_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxpassport_image_name = StringField(
        "oxPassport image name",
        default=settings.get("OXPASSPORT_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxpassport_image_tag = StringField(
        "oxPassport image tag",
        default=settings.get("OXPASSPORT_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxshibboleth_image_name = StringField(
        "oxShibboleth image name",
        default=settings.get("OXSHIBBOLETH_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxshibboleth_image_tag = StringField(
        "oxShibboleth image tag",
        default=settings.get("OXSHIBBOLETH_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxtrust_image_name = StringField(
        "oxTrust image name",
        default=settings.get("OXTRUST_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    oxtrust_image_tag = StringField(
        "oxTrust image tag",
        default=settings.get("OXTRUST_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    persistence_image_name = StringField(
        "Persistence image name",
        default=settings.get("PERSISTENCE_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    persistence_image_tag = StringField(
        "Persistence image tag",
        default=settings.get("PERSISTENCE_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    radius_image_name = StringField(
        "Radius image name",
        default=settings.get("RADIUS_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    radius_image_tag = StringField(
        "Radius image tag",
        default=settings.get("RADIUS_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_image_name = StringField(
        "Gluu-Gateway image name",
        default=settings.get("GLUU_GATEWAY_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_image_tag = StringField(
        "Gluu-Gateway image tag",
        default=settings.get("GLUU_GATEWAY_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_ui_image_name = StringField(
        "Gluu-Gateway-UI image name",
        default=settings.get("GLUU_GATEWAY_IMAGE_NAME"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
    gluu_gateway_ui_image_tag = StringField(
        "Gluu-Gateway-UI image tag",
        default=settings.get("GLUU_GATEWAY_IMAGE_TAG"),
        validators=[RequiredIfFieldEqualTo("edit_image_names_tags", "Y")])
