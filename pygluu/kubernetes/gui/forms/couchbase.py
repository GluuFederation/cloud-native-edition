from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, FileField, \
    IntegerField, MultipleFileField
from wtforms.widgets import PasswordInput
from wtforms.validators import DataRequired, InputRequired, \
    EqualTo, Optional, ValidationError, URL
from .helpers import password_requirement_check, RequiredIfFieldEqualTo


class CouchbaseMultiClusterForm(FlaskForm):
    """
    Couchbase Multi Cluster Form

    Fields:
        deploy_multi_cluster (string|optional, available for hybrid and couchbase backend)
    """
    deploy_multi_cluster = RadioField(
        "Is this a multi-cloud/region setup?",
        choices=[("Y", "Yes"), ("N", "No")],
        description="If you are planning for a multi-cloud/region "
                    "setup and this is the first cluster answer N "
                    "You will answer Y for the second and more cluster setup")


class CouchbaseForm(FlaskForm):
    """
    Couchbase Form

    Fields:
        install_couchbase (string|required)
        couchbase_crt (file|required_if install_couchbase is N)
        couchbase_cluster_file_override (string|required|default: N)
        couchbase_cluster_files (file|required_if couchbase_cluster_file_override is Y)
        couchbase_use_low_resource (string|optional|default: N|forced to Y for microk8s and minikube)
        couchbase_namespace (string|required|default: cbns)
        couchbase_cluster_name (string|required|default: cbgluu)
        couchbase_url (string|required|default: cbgluu.cbns.svc.cluster.local)
        couchbase_bucket_prefix (string|required|default: gluu)
        couchbase_index_num_replica string|required|default: 0)
        couchbase_user (string|required|default: admin)
        couchbase_password (string|required|default: auto generate)
        couchbase_password_confirmation (string|required|equal to couchbase_password)
        couchbase_cn (string|optional|default: Couchbase CA)

    Note:
        COUCHBASE_CN will be required when couchbase certs inside couchbase_crts-keys folder not exist
    """
    install_couchbase = RadioField(
        "Install Couchbase", choices=[("Y", "Yes"), ("N", "No")],
        description="For the following prompt if placed [N] the couchbase "
                    "is assumed to be installed or remotely provisioned",
        validators=[DataRequired()])
    package_url = StringField(
        "Couchbase Kubernetes Package URL",
        validators=[RequiredIfFieldEqualTo("install_couchbase", "Y"),
                    URL(require_tld=False, message="Url format is wrong")],
        description="Please place a downloadable link containing the couchbase linux autonomous operator kubernetes package,"
                    "go to <a target='_blank' href='https://www.couchbase.com/downloads'>https://www.couchbase.com/downloads</a>")

    couchbase_crt = FileField(
        "Couchbase certificate",
        description="Place the Couchbase certificate authority certificate in a file called couchbase.crt "
                    "This can also be found in your couchbase UI Security > Root Certificate",
        validators=[RequiredIfFieldEqualTo("install_couchbase", "N")])
    couchbase_cluster_file_override = RadioField(
        "Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml",
        choices=[("Y", "Yes"), ("N", "No")], validators=[DataRequired()])
    couchbase_cluster_files = MultipleFileField(
        "Couchbase override files",
        description="Please upload the override files under the name "
                    "couchbase-cluster.yaml, couchbase-buckets.yaml, "
                    "and couchbase-ephemeral-buckets.yaml",
        validators=[RequiredIfFieldEqualTo("couchbase_cluster_file_override", "Y")])
    couchbase_use_low_resources = RadioField(
        "Setup CB nodes using low resources for demo purposes",
        choices=[("Y", "Yes"), ("N", "No")])

    couchbase_namespace = StringField(
        "Please enter a namespace for CB objects",
        default="cbns", validators=[InputRequired()])
    couchbase_cluster_name = StringField("Please enter a cluster name",
                                         default="cbgluu",
                                         validators=[InputRequired()])
    couchbase_url = StringField(
        "Please enter  couchbase (remote or local) URL base name",
        default="cbgluu.cbns.svc.cluster.local",
        validators=[InputRequired()])

    couchbase_bucket_prefix = StringField(
        "Please enter a  prefix name for all couchbase gluu buckets",
        default="gluu",
        validators=[InputRequired()])

    couchbase_index_num_replica = StringField(
        "Please enter the number of replicas per index created.",
        description="Please note that the number of index nodes must be one greater than the number of replicas. "
                    "That means if your couchbase cluster only has 2 "
                    "index nodes you cannot place the number of replicas to be higher than 1.",
        default=0,
        validators=[InputRequired()])

    couchbase_superuser = StringField("Please enter couchbase superuser username",
                                      default="admin",
                                      validators=[InputRequired()])
    couchbase_superuser_password = StringField(
        "Couchbase superuser password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(), password_requirement_check()],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    couchbase_superuser_password_confirmation = StringField(
        "Couchbase superuser password confirm",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(), EqualTo("couchbase_superuser_password")])
    couchbase_user = StringField("Please enter gluu couchbase username",
                                 default="gluu",
                                 validators=[InputRequired()])
    couchbase_password = StringField(
        "Couchbase gluu user password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(), password_requirement_check()],
        description="Password is randomly generated with 6 characters contain "
                    "number, uppercase letter, lower case letter and symbol")
    couchbase_password_confirmation = StringField(
        "Couchbase gluu user password confirm",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired(), EqualTo("couchbase_password")])
    couchbase_cn = StringField("Enter Couchbase certificate common name.",
                               default="Couchbase CA")

    def validate_package_url(self, field):
        """
        validate field package_url, checking pattern
        """
        if "couchbase-autonomous-operator-kubernetes" not in field.data:
            raise ValidationError("The uploaded package is not the Couchbase Autonomous Operator linux package")

        if "_1." in field.data:
            raise ValidationError("The uploaded package must be version 2 or above")


class CouchbaseCalculatorForm(FlaskForm):
    """
    Couchbase Calculator Form.

    Fields:
        number_of_expected_users (integer|required|default: 10000000)
        using_resource_owner_password_cred_grant_flow (string|required|default: Y)
        using_code_flow (string|required|default: Y)
        using_scim_flow (string|required|default Y)
        expected_transaction_per_sec (integer|required|default:2000)
        couchbase_data_nodes (string|optional|default: "")
        couchbase_index_nodes (string|optional|default: "")
        couchbase_search_eventing_analytics_nodes (string|optional|default: "")
        couchbase_general_storage (string|optional|default: "")
        couchbase_data_storage (string|optional|default: ""|auto calculated)
        couchbase_index_storage (string|optional|default: ""|auto calculated)
        couchbase_query_storage (string|optional|default: ""|auto calculated)
        couchbase_analytics_storage (string|optional|default: ""|auto calculated)
        couchbase_volume_type (string|optional|default: see volume_types variable)
    """
    number_of_expected_users = IntegerField(
        "Please enter the number of expected users", default=1000000,
        validators=[InputRequired()])
    using_resource_owner_password_cred_grant_flow = RadioField(
        "Will you be using the resource owner password credential grant flow",
        choices=[("Y", "Yes"), ("N", "No")],
        default="Y",
        validators=[DataRequired()])
    using_code_flow = RadioField("Will you be using the code flow",
                                 choices=[("Y", "Yes"), ("N", "No")],
                                 default="Y",
                                 validators=[DataRequired()])
    using_scim_flow = RadioField("Will you be using the SCIM flow",
                                 choices=[("Y", "Yes"), ("N", "No")],
                                 default="Y",
                                 validators=[DataRequired()])
    expected_transaction_per_sec = StringField(
        "Expected transactions per second",
        default=2000,
        validators=[InputRequired()])
    couchbase_data_nodes = StringField(
        "Please enter the number of data nodes. (auto-calculated)",
        default="",
        validators=[Optional()])
    couchbase_index_nodes = StringField(
        "Please enter the number of index nodes. (auto-calculated)",
        default="")
    couchbase_query_nodes = StringField(
        "Please enter the number of query nodes. (auto-calculated)",
        default="")
    couchbase_search_eventing_analytics_nodes = StringField(
        "Please enter the number of search,eventing and analytics nodes. (auto-calculated)",
        default="")
    couchbase_general_storage = StringField(
        "Please enter the general storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_data_storage = StringField(
        "Please enter the data storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_index_storage = StringField(
        "Please enter the index node storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_query_storage = StringField(
        "Please enter the data storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_analytics_storage = StringField(
        "Please enter the analytics node storage size used for couchbase. (auto-calculated)",
        default="")
    couchbase_volume_type = RadioField("Please select the volume type.",
                                       choices=[],
                                       validators=[Optional()])
